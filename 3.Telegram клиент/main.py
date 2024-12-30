from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from app.handlers import router  # Подключаем router напрямую
from app.config import TOKEN, POSTGRESQL_DSN  # Убедитесь, что вы импортируете DSN для PostgreSQL
from app.storage import storage  # Импортируем класс Storage
import asyncio
from aiogram.client.bot import DefaultBotProperties

async def main():
    # Создаем объект бота с использованием DefaultBotProperties
    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)  # Указываем parse_mode через default
    )
    
    
    # Хранилище для FSM
    fsm_storage = MemoryStorage()
    
    # Создаем диспетчер
    dp = Dispatcher(storage=fsm_storage)
    
    # Подключаем маршрутизатор
    dp.include_router(router)
    
    
    # Запускаем бота
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")