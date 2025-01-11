from aiogram import types, Dispatcher
from aiogram.filters import Command
import jwt
import redis
import json  
import aiohttp
import datetime
import logging
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from app.config import SECRET_KEY
from bot_logic import gethttp
from app.keyboards import auth_keyboard
from app.storage import storage
from aiogram import F
from app.keyboards import get_personal_account_keyboard
# Настройка Redis
REDIS_HOST = 'localhost'
REDIS_PORT = 6379  # Убедитесь, что порт соответствует вашему серверу Redis
REDIS = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

# Функция для генерации токена
def generate_token(user_id):
    secret_key = SECRET_KEY
    # Устанавливаем время истечения токена на 5 минут
    # Создаем полезную нагрузку с user_id и временем истечения
    payload = {
        'user_id': user_id,
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

        # Проверяем, есть ли у пользователя токен в Redis
        user_data = REDIS.get(chat_id)

        if user_data is None:
            print("Данные для chat_id не найдены в Redis")
        else:
            try:
                # Декодируем JSON
                data = json.loads(user_data)
    
                # Извлекаем token и status
                token = data.get('token')
                status = data.get('status')
                
                # Проверяем, что token и status существуют
                if token is None or status is None:
                    print("data не содержит token или status")
            
            except json.JSONDecodeError:
                print("Ошибка: Данные в Redis не являются валидным JSON")
            except Exception as e:
                print(f"Произошла ошибка: {e}")
        # Redis сообщает, что такого ключа нет если выполняется следующее условие
        if not user_data:
            keyboard = auth_keyboard()
            print("Пользователь не авторизован , авторизуем")
            await message.answer("Вы не авторизованы. Пожалуйста, выберите метод авторизации:", reply_markup=keyboard)
        elif status == "Anonym":
            keyboard = auth_keyboard()
            status_auth = f"http://localhost/botTelegramLogic/login?chat_id={chat_id}"
            real_anonim = False
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(status_auth) as response:
                        if response.status == 200: # если 200 тогда смотрю что находится в статусе(state)
                            try:
                                
                                json_response = await response.json() 
                                status = json_response.get("status") 
                                if status == "login": 
                                    real_anonim = True 
                                else:
                                    real_anonim = False
                            except ValueError:
                                print("Ошибка: ответ не является корректным JSON.")                                                              
                        else:
                            print(f"Ошибка при получении данных. Статус: {response.status}")
                
                except aiohttp.ClientError as e:
                    await callback_query.message.reply(f"Ошибка при выполнении запроса: {str(e)}")
            if real_anonim:
                print("Пользователь в статусе анонима, предлагаем повторно авторизоваться")
            
                await message.answer("Вы не авторизованы. Пожалуйста, выберите метод авторизации:", reply_markup=keyboard)
            else:
                print("компонент bot_logic.py не был запущен")
            
        else:
            status_auth = f"http://localhost/botTelegramLogic/login?chat_id={chat_id}"
            auth = False
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(status_auth) as response:
                        if response.status == 200: 
                            try:
                                
                                json_response = await response.json() 
                                status = json_response.get("status") 
                                if status == "Authtorizovanni": 
                                    auth = True 
                                else:
                                    auth = False
                            except ValueError:
                                print("Ошибка: ответ не является корректным JSON.")                                                              
                        else:
                            print(f"Ошибка при получении данных. Статус: {response.status}")
                
                except aiohttp.ClientError as e:
                    await callback_query.message.reply(f"Ошибка при выполнении запроса: {str(e)}")
            if auth:
                await message.answer("Вы уже авторизованы.")
                personal_account = f'http://localhost/botTelegramLogic/profile?chat_id={chat_id}'

                async with aiohttp.ClientSession() as session:
                    try:
                        async with session.get(personal_account) as response:
                            if response.status == 200:
                                try:
                                    json_response = await response.json()
                                    user_data = json_response.get("user")
                                    if user_data:
                                        email = user_data.get("email")
                                        name = user_data.get("name")
                                        if email and name:
                                            # Используем клавиатуру из keyboards.py
                                            await message.answer(
                                                f"Ваш личный кабинет\nВаше имя: {name}\nВаш email: {email}",
                                                reply_markup=get_personal_account_keyboard()
                                            )
                                            
                                        else:
                                            await message.answer("Данные пользователя неполные.")
                                    else:
                                        await message.answer("Ключ 'user' отсутствует в JSON.")
                                except ValueError as e:
                                    logging.error(f"Ошибка: ответ не является корректным JSON. {e}")
                                    await message.answer("Ошибка при обработке данных.")
                            else:
                                logging.error(f"Ошибка при получении данных. Статус: {response.status}")
                                await message.answer("Ошибка при получении данных.")
                    except aiohttp.ClientError as e:
                        logging.error(f"Ошибка при выполнении запроса: {e}")
                        await message.answer("Ошибка сети.")
                    except Exception as e:
                        logging.error(f"Неожиданная ошибка: {e}")
                        await message.answer("Произошла неожиданная ошибка.")
                print("мегапроверка пройдена")
            else:
                print("компонент bot_logic.py не был запущен")

        

        @dp.callback_query(lambda c: c.data.startswith("auth_"))
        async def auth_callback(callback_query: types.CallbackQuery):
            print("Обработчик вызван, кнопка нажата")
            chat_id = callback_query.message.chat.id
            type_auth = callback_query.data.split("_")[1]
            access_granted = False  

            link_for_auth = f"http://localhost/botTelegramLogic/login?type={type_auth}&chat_id={chat_id}"

            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(link_for_auth) as response:
                            if response.status == 200: # если 200 тогда смотрю что находится в статусе(state)
                                try:           
                                    json_response = await response.json() 
                                    url_for_auth = json_response.get("URL")
                                    code = json_response.get("code")
                                    if url_for_auth:
                                        print(f"URL for auth for user: {url_for_auth}") 
                                    elif code:
                                        print(f"code for auth user: {code}")
                                    else:
                                        print("не удалось обработать link_for_auth")
                                    if url_for_auth:
                                        await callback_query.message.reply(f"Перейдите по следующей ссылке для авторизации: {url_for_auth}")
                                        # Отправляем кнопку для подтверждения входа
                                        confirm_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                                            [InlineKeyboardButton(text="Подтвердить вход", callback_data="confirm_login")]
                                        ])
                                        await callback_query.message.answer("Нажмите кнопку ниже, чтобы подтвердить вход:", reply_markup=confirm_keyboard)
                                    elif code:
                                        await callback_query.message.reply(f"Код для авторизации на web клиенте: {code}")

                                        confirm_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                                            [InlineKeyboardButton(text="Подтвердить вход", callback_data="confirm_login")]
                                        ])
                                        await callback_query.message.answer("Нажмите кнопку ниже, чтобы подтвердить вход:", reply_markup=confirm_keyboard)
                                    else:
                                        print("мы не получили url из ссылки")
                                except ValueError:
                                    print("Ошибка: ответ не является корректным JSON.")                                                              
                            else:
                                print(f"Ошибка при получении данных. Статус: {response.status}")
                
                except aiohttp.ClientError as e:
                    await callback_query.message.reply(f"Ошибка при выполнении запроса: {str(e)}")




        @dp.callback_query(lambda c: c.data == "confirm_login")
        async def confirm_login(callback_query: types.CallbackQuery):
            print("Нажата кнопка подтверждения входа")
            chat_id = callback_query.message.chat.id

            status_auth = f"http://localhost/botTelegramLogic/login?chat_id={chat_id}"
            
            access_granted = False
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(status_auth) as response:
                        if response.status == 200: # если 200 тогда смотрю что находится в статусе(state)
                            try:
                                json_response = await response.json() 
                                status = json_response.get("status") 
                                if status == "Authtorizovanni": 
                                    access_granted = True  
                                    # В обработчике успешной авторизации
                                    storage.set_user_authorized(user_id, authorized=True)
                                else:
                                    access_granted = False
                            except ValueError:
                                print("Ошибка: ответ не является корректным JSON.")                                                              
                        else:
                            print(f"Ошибка при получении данных. Статус: {response.status}")
                
                except aiohttp.ClientError as e:
                    await callback_query.message.reply(f"Ошибка при выполнении запроса: {str(e)}")
            if access_granted:
                await callback_query.message.answer("Вы авторизованы!")

                personal_account = f'http://localhost/botTelegramLogic/profile?chat_id={chat_id}'

                async with aiohttp.ClientSession() as session:
                    try:
                        async with session.get(personal_account) as response:
                            if response.status == 200:
                                try:
                                    json_response = await response.json()
                                    user_data = json_response.get("user")
                                    if user_data:
                                        email = user_data.get("email")
                                        name = user_data.get("name")
                                        if email and name:

                                            # Используем клавиатуру из keyboards.py
                                            await callback_query.message.answer(
                                                f"Ваш личный кабинет\nВаше имя: {name}\nВаш email: {email}",
                                                reply_markup=get_personal_account_keyboard()
                                            )
                                        else:
                                            await callback_query.message.answer("Данные пользователя неполные.")
                                    else:
                                        await callback_query.message.answer("Ключ 'user' отсутствует в JSON.")
                                except ValueError as e:
                                    logging.error(f"Ошибка: ответ не является корректным JSON. {e}")
                                    await callback_query.message.answer("Ошибка при обработке данных.")
                            else:
                                logging.error(f"Ошибка при получении данных. Статус: {response.status}")
                                await callback_query.message.answer("Ошибка при получении данных.")
                    except aiohttp.ClientError as e:
                        logging.error(f"Ошибка при выполнении запроса: {e}")
                        await callback_query.message.answer("Ошибка сети.")
                    except Exception as e:
                        logging.error(f"Неожиданная ошибка: {e}")
                        await callback_query.message.answer("Произошла неожиданная ошибка.")
            else:
                await callback_query.message.answer("Доступ не получен. Начните процесс авторизации заново.")


        @dp.callback_query(lambda c: c.data == "exit_status")
        async def exit_account(callback_query: types.CallbackQuery):
            chat_id = callback_query.message.chat.id

            logout_url = f"http://localhost/botTelegramLogic/logout?chat_id={chat_id}"
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(logout_url) as response:
                        print(response.status)
                        if response.status == 200:
                            storage.set_user_authorized(user_id, authorized=False)
                            await callback_query.message.answer("Вы успешно вышли из аккаунта, сеанс завершён. Можете снова авторизоваться командой /login")
                        else:
                            await callback_query.message.answer("Ошибка при выходе из аккаунта.")
                except aiohttp.ClientError as e:
                    logging.error(f"Ошибка сети: {e}")
                    await callback_query.message.answer("Ошибка сети при выходе из аккаунта.")

            await callback_query.answer()  # Подтверждаем обработку callback 

        @dp.callback_query(lambda c: c.data == "change_name")
        async def change_name_handler(callback_query: types.CallbackQuery):
            chat_id = callback_query.message.chat.id
            await callback_query.message.answer("Введите новое имя:")
            # Здесь можно сохранить состояние, что пользователь ожидает ввода нового имени
            # Например, использовать Redis для хранения состояния "ожидание ввода имени"
            REDIS.set(f"{chat_id}_waiting_for_name", "true")
        
        @dp.message(lambda message: REDIS.get(f"{message.chat.id}_waiting_for_name") == b"true")
        async def process_new_name(message: types.Message):
            chat_id = message.chat.id
            new_name = message.text
            REDIS.delete(f"{chat_id}_waiting_for_name")  # Удаляем состояние ожидания

            # Отправляем запрос на сервер для обновления имени
            update_name_url = f"http://localhost/botTelegramLogic/update_name?chat_id={chat_id}&name={new_name}"
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(update_name_url) as response:
                        if response.status == 200:
                            await message.answer(f"Имя успешно изменено на {new_name}!")
                        else:
                            await message.answer("Ошибка при изменении имени.")
                except aiohttp.ClientError as e:
                    await message.answer(f"Ошибка сети: {str(e)}")

        
