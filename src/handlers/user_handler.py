import asyncio
from aiogram import types
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from src.keyboards import user_keyboards


router =  Router()
from src.misc import bot,bot_id

help_msg = '''/ava {n} Available
/una {n} Unavailable
/tak {n} Taken
n = 10 by default
/db  Download Base
/del {username}
/del all
/start
/help
'''

@router.message(Command("start"))
@new_user_handler
async def start_handler(message: Message, state: FSMContext,is_clb=False,**kwargs):
    await message.answer(help_msg)