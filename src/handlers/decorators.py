from src.methods.database.database import DBService
from aiogram.types import Message
from src.misc import bot_id
db = DBService()
from loguru import logger

def new_user_handler(function):
    async def _new_user_handler(*args, **kwargs):
        message: Message = args[0]
        user_id = message.from_user.id
        username = message.from_user.username if message.from_user.username else None
        if (await db.get_user(user_id)) is None:
            await db.create_user(user_id,username)
            
            logger.success(f"Новый пользователь (ID: {user_id}, Username: {username})")
            if user_id == int(bot_id):

                await db.set_admin(user_id,'is_admin',1)
                #назначение бота админом для кнопок в админке(костыль, вроде пофикшен)
                logger.info(f'[Admin] {user_id} получил права админа')
            # else:
                # await message.answer(
                # "👋 Привет, вижу ты новенький. Будем знакомы, чтобы получить список моих команд напиши <code>/help</code>",
                # parse_mode="HTML")


        return await function(*args, **kwargs)

    return _new_user_handler