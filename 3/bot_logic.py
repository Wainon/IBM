#!/usr/bin/env python3
from flask import Flask, request, jsonify

import threading
import queue
import redis
import json
import aiohttp
import logging
import jwt
import datetime

app = Flask(__name__)
REDIS_HOST = 'localhost'
REDIS_PORT = 6379 
REDIS = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("my_logger")
def redischek(id,tupe,log="-"):
    keys = REDIS.keys('*')
    print(f"Ключ {keys}")
    user_data = REDIS.get(id)
    print(f"данные соответсвующие ключу {keys} = {user_data}")
    if not user_data:
        return False
    
    if log=="-":   
        return True 
    user_data = json.loads(user_data)
    
    status = user_data.get(tupe, "")
    print(status)
    if status==log:
        return True
    return False

def redisget(id,tupe):
    print("id ",id)
    keys = REDIS.keys('*')
    print(f"Ключ {keys}")

    user_data = REDIS.get(id)
    print("tupe ",tupe)
    if not user_data:
        return ""
    user_data = json.loads(user_data)
    print("user_data ",user_data)
    status = user_data.get(tupe, "")
    print("status ",status)
    return status
async def gethttp(lhttp):
    async with aiohttp.ClientSession() as session:
        print(f"lhttp: {lhttp}")
        try:
            async with session.get(lhttp) as response:
                if response.status == 200:
                    try:
                        json_data = await response.json()
                        print(f"response json: {json_data}")
                        return json_data
                    except ValueError:
                        logging.error("Ошибка: ответ не является корректным JSON.")
                else:
                    logging.error(f"Ошибка при получении данных. Статус: {response.status}")
        except aiohttp.ClientError as e:
            logging.error(f"Ошибка при выполнении запроса: {str(e)}")
    return ""
# Функция для генерации токена
def generate_token(chat_id):
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    payload = {
        'chat_id': chat_id,
        'exp': expiration_time
    }
    token = jwt.encode(payload, "SECRET_KEY", algorithm='HS256')
    return token
async def updateAccessToken(chat_id):
    U = redisget(chat_id,'tokenU') 
    print(f"AccessToken: {U}")
    AccessToken = await getServerM(f"http://localhost:8080/func/updateAccessToken?state={U}")
    AccessToken = AccessToken.get("AccessToken")
    a={'status': 'Authtorizovanni', 'tokenD': AccessToken, 'tokenU': U}
    REDIS.set(chat_id, json.dumps(a))
    return True

async def login(chat_id):
    print("login")
    if not redischek(chat_id, "status", "-"):
        print("- False")
        return False
    if redischek(chat_id, "status", "Authtorizovanni"):
        print("Authtorizovanni True")
        # Await the asynchronous function call
        f = await updateAccessToken(chat_id)
        print(f"f: {f}")
        if not f:
            return False
        return True
    print("login2")
    async with aiohttp.ClientSession() as session:
        try:
            # Bot Logic достаёт из ответа от Redis токен входа и делает запрос 
            # модулю Авторизации отправляя токен входа для проверки;
            r = redisget(chat_id, 'inputToken')
            print(f"input token: {r}")
            # Модуль Авторизации проверяет есть ли у него запись
            #  для указанного токена входа и отвечает
            lhttp = f"http://localhost:8080/func/valedtocen?state={r}"
            print(f"lhttp: {lhttp}")
            async with session.get(lhttp) as response:
                if response.status == 200:
                    json_response = await response.json()
                    errorAuth = json_response.get("error")
                    state = json_response.get("state")
                    if state == "доступ получен":
                        tokenD = json_response.get("TokenD")  # Get tokenD from the response
                        tokenU = json_response.get("TokenU")  # Get tokenU from the response
                        REDIS.delete(chat_id)  # Use chat_id instead of chat_id
                        REDIS.set(chat_id, json.dumps({'status': 'Authtorizovanni', 'tokenD': tokenD, 'tokenU': tokenU}))
                        return True
                    elif errorAuth == "не опознанный токен":
                        REDIS.delete(chat_id)
                        return False
                    else:
                        return False
                elif response.status == 401:
                    logging.error("Ошибка авторизации: 401 Unauthorized")
                    REDIS.delete(chat_id)
                else:
                    logging.error(f"Ошибка при получении данных. Статус: {response.status}")
        except aiohttp.ClientError as e:
            logging.error(f"Ошибка при выполнении запроса: {str(e)}")
    return False  


async def getServerM(lhttp):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(lhttp) as response:
                if response.status == 200:
                    return  await response.json()
                else:
                    logging.error(f"Ошибка при получении данных. Статус: {response.status}")
        except aiohttp.ClientError as e:
            logging.error(f"Ошибка при выполнении запроса: {str(e)}")
    return {"errer":"lox"}   

@app.route('/botTelegramLogic/login', methods=['GET'])
async def process_login_message():
    try:
        type = request.args.get('type')
        chat_id = request.args.get('chat_id')
        if redischek(chat_id,"status","Authtorizovanni"):
            response={"status":"Authtorizovanni"}
        else:
            if not type:    
                if await login(chat_id):
                    response={"status":"Authtorizovanni"}
                    return jsonify(response), 200
                response={"status":"login"}
            else:
                inputToken = generate_token(chat_id)
                REDIS.set(chat_id, json.dumps({'status':"Anonym","inputToken":inputToken}))
                log = await gethttp(f"http://localhost:8080/oauth?type={type}&state={inputToken}")
                if log.get("state") == "доступ получен":  # Предполагается, что это состояние успешной авторизации
                    tokenD = log.get("TokenD")
                    tokenU = log.get("TokenU")
                    REDIS.set(chat_id, json.dumps({'status': 'Authtorizovanni', 'tokenD': tokenD, 'tokenU': tokenU}))
                    response = {"status": "Authtorizovanni"}
                else:
                    response = log
        print(f"response: {response}")
        return jsonify(response), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        print("base")


@app.route('/botTelegramLogic/codeinput', methods=['GET'])
async def codeinput():
    chat_id = request.args.get('chat_id')
    code = request.args.get('code')
    U = redisget(chat_id,'tokenU')
    
    status_auth = f"http://localhost:8080/oauth/code?code={code}&TokenU={U}"
    print(f"status_auth   {status_auth}")
    access_granted = False
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(status_auth) as response:
                if response.status == 200:
                    try:
                        response = {"auth" : "success"}
                        return jsonify(response), 200
                    except ValueError:
                        print("Ошибка: ответ не является корректным JSON.")     
                        response = {"auth" : "failed"}                                                                                 
                else:
                    response = {"auth" : "failed"} 
                    print(f"Ошибка при получении данных. Статус: {response.status}")  
        except aiohttp.ClientError as e:
            await callback_query.message.reply(f"Ошибка при выполнении запроса: {str(e)}")
            response = {"auth" : "failed"} 
    return jsonify(response), 200
    
@app.route('/botTelegramLogic/logout', methods=['GET'])
async def logout():
    try:
        chat_id = request.args.get('chat_id')
        if not chat_id:
            return jsonify({'error': 'chat_id is required'}), 400

        # Проверяем, авторизован ли пользователь
        if redischek(chat_id, "status", "Authtorizovanni"):
            REDIS.delete(chat_id)  # Удаляем все данные для chat_id
            response = {"status": "delete"}
        else:
            response = {"status": "not_authorized"}
        return jsonify(response), 200
    except Exception as e:
        logger.error(f"Ошибка при выходе из аккаунта: {e}")
        return jsonify({'error': str(e)}), 500

    finally:
        logger.info("Завершение обработки запроса на выход из аккаунта")

@app.route('/botTelegramLogic/profile', methods=['GET'])
async def profile():
    chat_id = request.args.get('chat_id')
    print("chat id: ", chat_id)
    if not await login(chat_id):
        response={"status":"not login"}
        return jsonify(response), 401
    D = redisget(chat_id,'tokenD') 
    print(f"tokenD: {D}")
    lhttp = f"http://localhost:8000/req?type=UserDats&AccessToken={D}"
    print(lhttp)
    return jsonify(await getServerM(lhttp)), 200

@app.route('/botTelegramLogic/update_name', methods=['GET'])
async def update_name():
    try:
        chat_id = request.args.get('chat_id')
        new_name = request.args.get('name')
        if not chat_id or not new_name:
            return jsonify({'error': 'chat_id and name are required'}), 400

        # Получаем текущие данные пользователя
        user_data = REDIS.get(chat_id)
        if not user_data:
            return jsonify({'error': 'User not found'}), 404

        user_data = json.loads(user_data)
        tokenD = user_data.get('tokenD')

        # Отправляем запрос на сервер для обновления имени
        update_url = f"http://localhost:8000/req?type=updateName&AccessToken=${tokenD}&newName=${newName}"
        response = await getServerM(update_url)

        if response.get("status") == "success":
            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"status": "error", "message": "Failed to update name"}), 500

    except Exception as e:
        logger.error(f"Ошибка при обновлении имени: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/botTelegramLogic/check_anonymous_users', methods=['GET'])
async def check_anonymous_users():
    try:
        # Получаем всех пользователей в статусе "Анонимный"
        anonymous_users = []
        for key in REDIS.keys():
            user_data = REDIS.get(key)
            if user_data:
                user_data = json.loads(user_data)
                if user_data.get("status") == "Anonym":
                    anonymous_users.append(key.decode())  # Декодируем ключ

        # Если анонимных пользователей нет, возвращаем пустой массив
        if not anonymous_users:
            return jsonify({"users": []}), 200

        # Обработка каждого анонимного пользователя
        results = []
        for chat_id in anonymous_users:
            # Запрос к модулю авторизации для проверки токена
            input_token = json.loads(REDIS.get(chat_id)).get("inputToken")
            auth_url = f"http://localhost:8080/func/valedtocen?state={input_token}"
            async with aiohttp.ClientSession() as session:
                async with session.get(auth_url) as response:
                    if response.status == 200:
                        json_response = await response.json()
                        state = json_response.get("state")
                        if state == "доступ получен":
                            # Обновляем статус пользователя в Redis
                            tokenD = json_response.get("TokenD")
                            tokenU = json_response.get("TokenU")
                            REDIS.set(chat_id, json.dumps({'status': 'Authtorizovanni', 'tokenD': tokenD, 'tokenU': tokenU}))
                            results.append({"chat_id": chat_id, "status": "success"})
                        else:
                            # Удаляем пользователя из Redis
                            REDIS.delete(chat_id)
                            results.append({"chat_id": chat_id, "status": "failed"})
                    elif response.status == 401:
                        # Ошибка 401: неопознанный токен или истекшее время
                        REDIS.delete(chat_id)
                        results.append({"chat_id": chat_id, "status": "failed"})
                    else:
                        # Другие ошибки (например, 500)
                        REDIS.delete(chat_id)
                        results.append({"chat_id": chat_id, "status": "failed"})

        # Возвращаем результаты в формате JSON
        return jsonify({"users": results}), 200

    except Exception as e:
        # Логируем ошибку и возвращаем сообщение об ошибке
        logging.error(f"Ошибка в check_anonymous_users: {e}")
        return jsonify({"error": "Internal Server Error"}), 500


if __name__ == '__main__':
    app.run(port=8001)
