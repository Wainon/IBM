from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.bot import DefaultBotProperties
from app.handlers import router
from app.config import TOKEN
from app.storage import storage
from app.middlewares import AuthMiddleware  # Импортируем мидлварь
from app.auth_handlers import register_auth_handlers
from app.callback_handlers import transfers_handlers
from app.attempt import attempt_router
import asyncio

async def main():
    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    fsm_storage = MemoryStorage()
    dp = Dispatcher(storage=fsm_storage)
    
    # Создаем экземпляр мидлвари
    auth_middleware = AuthMiddleware()

    # Регистрируем мидлварь для каждого роутера
    router.message.middleware(auth_middleware)
    router.callback_query.middleware(auth_middleware)
    
    attempt_router.message.middleware(auth_middleware)
    attempt_router.callback_query.middleware(auth_middleware)

    # Подключаем роутеры
    dp.include_router(router)
    dp.include_router(attempt_router)
    
    # Регистрируем обработчики авторизации и переходов
    register_auth_handlers(dp)
    transfers_handlers(dp)

    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")