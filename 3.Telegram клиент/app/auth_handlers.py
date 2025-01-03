from aiogram import types, Dispatcher
from aiogram.filters import Command
import jwt
import redis
import json  
import aiohttp
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from app.config import SECRET_KEY

# Настройка Redis
REDIS_HOST = 'localhost'
REDIS_PORT = 6380  # Убедитесь, что порт соответствует вашему серверу Redis
REDIS = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

# Функция для генерации токена
def generate_token(user_id):
    secret_key = SECRET_KEY
    token = jwt.encode({'user_id': user_id}, secret_key, algorithm='HS256')
    print(f"\ntoken: {token}")
    return token

# Функция для регистрации обработчиков авторизации
def register_auth_handlers(dp: Dispatcher):
    @dp.message(Command(commands=["login"]))
    async def login_handler(message: types.Message):
        user_id = message.from_user.id
        chat_id = message.chat.id


        keys = REDIS.keys('*')
        print(keys)

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

    @dp.callback_query(lambda c: c.data.startswith("auth_"))
    async def auth_callback(callback_query: types.CallbackQuery):
        print("Обработчик вызван, кнопка нажата")
        user_id = callback_query.from_user.id
        chat_id = callback_query.message.chat.id
        input_token = generate_token(user_id)  


        # Сохраняем статус пользователя и токен в Redis

        # Делаем запрос Redis чтобы он запомнил текущий chat_id как ключ, 
        # а в качестве значения: статус пользователя: Анонимный и токен входа;
        user_info = {'status': 'Анонимный', 'token': input_token}
        REDIS.set(chat_id, json.dumps(user_info))  # Сериализуем словарь в строку JSON

        # Получаем тип авторизации
        auth_type = callback_query.data.split("_")[1]

        # Формируем URL для авторизации
        auth_url = f"http://localhost:8080/oauth?type={auth_type}&state={input_token}"

        print(f"\nauth_url: {auth_url}")

        async with aiohttp.ClientSession() as session:
            async with session.get(auth_url) as response: # Выполняет асинхронный HTTP **GET-запрос** по адресу auth_url.
                if response.status == 200:
                    json_response = await response.json()  # Получаем JSON-объект
                    link = json_response.get("url")  # Извлекаем URL из JSON
                    if link:
                        await callback_query.answer(f"Перейдите по следующей ссылке для авторизации: {link}")
                    else:
                        await callback_query.answer("Ссылка не найдена в ответе.")
                else:
                    await callback_query.answer("Ошибка при получении данных.")

        # Отправляем сообщение с текстом
        # await callback_query.message.answer("Для авторизации нажмите кнопку ниже:")

        # # Создаем кнопку для авторизации
        # auth_button = InlineKeyboardButton(text="Авторизоваться", url=auth_url)
        # keyboard = InlineKeyboardMarkup(inline_keyboard=[[auth_button]])

        # # Отправляем кнопку с текстом
        # await callback_query.message.answer("Нажмите кнопку ниже для авторизации:", reply_markup=keyboard)

        # Отправляем кнопку для подтверждения входа
        confirm_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Подтвердить вход", callback_data="confirm_login")]
        ])
        await callback_query.message.answer("Нажмите кнопку ниже, чтобы подтвердить вход:", reply_markup=confirm_keyboard)

    @dp.callback_query(lambda c: c.data == "confirm_login")
    async def confirm_login(callback_query: types.CallbackQuery):
        # Здесь вы можете добавить логику для проверки регистрации
        # Например, отправить запрос на ваш сервер для проверки токена
        # Для примера, просто имитируем успешный вход
        access_granted = True  # Замените на реальную проверку

        if access_granted:
            await callback_query.message.answer("Вы авторизованы!")
            # Обновляем статус пользователя в Redis
            REDIS.set(callback_query.message.chat.id, json.dumps({'status': 'Authorized'}))

            chat_id = callback_query.message.chat.id
            value = REDIS.get(f"{chat_id}")
            print(value)
        else:
            await callback_query.message.answer("Доступ не получен. Начните процесс авторизации заново.")