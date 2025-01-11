from aiogram import Bot  # Импортируем класс Bot
import aiohttp
import json

async def check_auth_status(bot: Bot):
    url = "http://localhost/botTelegramLogic/check_anonymous_users"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    # Обработка ответа от Bot Logic
                    for user in data.get("users", []):
                        chat_id = user.get("chat_id")
                        status = user.get("status")

                        # Отправляем сообщение каждые 60 секунд
                        if status == "success":
                            await bot.send_message(chat_id, "Вы успешно авторизованы! Теперь вы можете пользоваться всеми функциями бота.")
                        elif status == "failed":
                            await bot.send_message(chat_id, "Авторизация не удалась. Пожалуйста, попробуйте снова.")
                else:
                    print(f"Ошибка при запросе к Bot Logic: {response.status}")
        except aiohttp.ClientError as e:
            print(f"Ошибка сети: {e}")