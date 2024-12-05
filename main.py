import asyncio
from loguru import logger
from src.handlers import user_handler
from src.misc import bot, dp
from src.methods.database.init_db import init_databases

# Запуск бота

# Инициализация баз данных
async def on_startup():
    await init_databases()  # Инициализация всех баз данных

def register_handlers():
    dp.include_routers(user_handler.router)

async def main():
    await on_startup()  # Вызов инициализации баз данных
    register_handlers() # Регистрация обработчиков
    # aaio_polling_task = asyncio.create_task(payment_polling())  # Отключено, если не нужно
    
    # Запускаем все задачи параллельно
    await asyncio.gather(
        dp.start_polling(bot),  # Telegram-бот
    )
if __name__ == "__main__":
    logger.add('src/logs/logs.log', format="{time} {level} {message}", level='DEBUG')
    asyncio.run(main())