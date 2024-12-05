from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')  # Замените на ваш токен от бота
DB_PATH = 'src/databases/database.db'
bot_id = BOT_TOKEN.split(":",1)[0]

bot = Bot(BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())