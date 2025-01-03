from aiogram import types, Dispatcher
from aiogram.filters import Command
import jwt
import redis
import json  
import aiohttp
import datetime
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from app.config import SECRET_KEY

# Настройка Redis
REDIS_HOST = 'localhost'
REDIS_PORT = 6379  # Убедитесь, что порт соответствует вашему серверу Redis
REDIS = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

# Функция для генерации токена
def generate_token(user_id):
    secret_key = SECRET_KEY
    # Устанавливаем время истечения токена на 5 минут
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    # Создаем полезную нагрузку с user_id и временем истечения
    payload = {
        'user_id': user_id,
        'exp': expiration_time
    }
    
    token = jwt.encode(payload, secret_key, algorithm='HS256')

    print(f"\ntoken: {token}")
    return token

# Функция для регистрации обработчиков авторизации
def register_auth_handlers(dp: Dispatcher):
    @dp.message(Command(commands=["login"]))
    async def login_handler(message: types.Message):
        user_id = message.from_user.id
        chat_id = message.chat.id

        input_token = generate_token(user_id)  

        keys = REDIS.keys('*')
        print(f"Ключ {keys}")

        # Проверяем, есть ли у пользователя токен в Redis
        user_data = REDIS.get(chat_id)
        # Redis сообщает, что такого ключа нет если выполняется следующее условие
        if not user_data:
            print("Пользователь не авторизован , авторизуем")
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="Авторизация через GitHub", callback_data="auth_git"),
                    InlineKeyboardButton(text="Авторизация через Яндекс ID", callback_data="auth_yndex"),
                ],
                [
                    InlineKeyboardButton(text="Авторизация через код (JWT)", callback_data="auth_code")
                ]
            ])
            await message.answer("Вы не авторизованы. Пожалуйста, выберите метод авторизации:", reply_markup=keyboard)
        #тут прописывать следующие условия из сценария (как я понимаю)
        else:
            await message.answer("Вы уже авторизованы.")

        async def fetch_auth_url(auth_type, input_token, callback_query):
            auth_url = f"http://localhost:8080/oauth?type={auth_type}&state={input_token}"
            print(f"\nauth_url: {auth_url}")

            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(auth_url) as response:
                        print(f"response status: {response.status}")
                        
                        if response.status == 200:
                            try:
                                json_response = await response.json()  # Получаем JSON-объект
                                print(f"\njson response: {json_response}")

                                link = json_response.get("URL")  # Извлекаем URL из JSON
                                print(f"\nlink: {link}")
                                code = json_response.get("code") 
                                print(f"\ncode: {code}")
                                if link:
                                    # Используем bot.send_message для отправки длинного сообщения
                                    await callback_query.message.reply(f"Перейдите по следующей ссылке для авторизации: {link}")
                                elif code:
                                    await callback_query.message.reply(f"Ваш для выполнения авторизации {code}")
                                    
                                else:
                                    await callback_query.message.reply("Ссылка не найдена в ответе.")
                            except ValueError:
                                await callback_query.message.reply("Ошибка: ответ не является корректным JSON.")
                        else:
                            await callback_query.message.reply(f"Ошибка при получении данных. Статус: {response.status}")
                except aiohttp.ClientError as e:
                    await callback_query.message.reply(f"Ошибка при выполнении запроса: {str(e)}")

        @dp.callback_query(lambda c: c.data.startswith("auth_"))
        async def auth_callback(callback_query: types.CallbackQuery):
            print("Обработчик вызван, кнопка нажата")
            user_id = callback_query.from_user.id
            chat_id = callback_query.message.chat.id

            # Сохраняем статус пользователя и токен в Redis
            user_info = {'status': 'Анонимный', 'token': input_token}

            REDIS.set(chat_id, json.dumps(user_info))  # Сериализуем словарь в строку JSON

            data = REDIS.get(chat_id)
            print(f"redis data: {data}")

            # Получаем тип авторизации
            auth_type = callback_query.data.split("_")[1]

            # Вызываем функцию для получения URL авторизации
            await fetch_auth_url(auth_type, input_token, callback_query)

            # Отправляем кнопку для подтверждения входа
            confirm_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Подтвердить вход", callback_data="confirm_login")]
            ])
            await callback_query.message.answer("Нажмите кнопку ниже, чтобы подтвердить вход:", reply_markup=confirm_keyboard)

        @dp.callback_query(lambda c: c.data == "confirm_login")
        async def confirm_login(callback_query: types.CallbackQuery):
            # Обновляем статус пользователя в Redis
            chat_id = callback_query.message.chat.id
            data = REDIS.get(chat_id)
            data_str = data.decode('utf-8')  # Декодируем байты в строку
            # Десериализация JSON-строки в Python-объект
            data = json.loads(data_str)
            # Теперь вы можете получить доступ к полям
            token = data.get('token')
            print(f"redis data: {token}")

            new_auth_url = f"http://localhost:8080/func/valedtocen?state={token}"
            

            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(new_auth_url) as response:
                            if response.status == 200: # если 200 тогда смотрю что находится в статусе(state)
                                try:
                                    
                                    json_response = await response.json() 
                                    state = json_response.get("state") # беру статус из адреса
                                    if state == "доступ получен": # if state == "доступ получен"
                                        tokenD = json_response.get("TokenD")  # беру tokenD из адреса
                                        tokenU = json_response.get("TokenU") # беру tokenU из адреса
                                        REDIS.set(callback_query.message.chat.id, 
                                                json.dumps({'status': 'Authorized','tokenD': tokenD, 'tokenU': tokenU })) # перезаписываю редис
                                        access_granted = True  
                                    else:
                                        access_granted = False  
                                except ValueError:
                                    access_granted = False
                                    print("Ошибка: ответ не является корректным JSON.")                                                              
                            else:
                                access_granted = False
                                print(f"Ошибка при получении данных. Статус: {response.status}")
                
                except aiohttp.ClientError as e:
                    await callback_query.message.reply(f"Ошибка при выполнении запроса: {str(e)}")
            if access_granted:
                await callback_query.message.answer("Вы авторизованы!")

                value = REDIS.get(f"{chat_id}")
                print(f"По ключу {chat_id} лежит {value}")
            else:
                await callback_query.message.answer("Доступ не получен. Начните процесс авторизации заново.")