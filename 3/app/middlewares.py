from aiogram import types
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from app.storage import storage

class AuthMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        # Проверяем, является ли событие сообщением или callback-запросом
        if isinstance(event, types.Message):
            user_id = event.from_user.id
            # Исключаем команды /start, /help и /login из проверки авторизации
            if event.text and (event.text.startswith("/start") or event.text.startswith("/help") or event.text.startswith("/login")):
                return await handler(event, data)
            
            # Проверяем, авторизован ли пользователь
            if not storage.is_user_authorized(user_id):
                await event.answer("Вы не авторизованы. Пожалуйста, авторизуйтесь с помощью команды /login.")
                return  # Прекращаем выполнение обработчика

        elif isinstance(event, types.CallbackQuery):
            user_id = event.from_user.id
            # Проверяем, авторизован ли пользователь
            if not storage.is_user_authorized(user_id):
                await event.answer("Вы не авторизованы. Пожалуйста, авторизуйтесь с помощью команды /login.", show_alert=True)
                return  # Прекращаем выполнение обработчика

        # Если пользователь авторизован, продолжаем обработку
        return await handler(event, data)