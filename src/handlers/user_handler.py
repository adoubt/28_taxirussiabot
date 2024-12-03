import asyncio
from aiogram import types
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message,Location




router =  Router()
from src.misc import dp, bot,bot_id
user_location_data = {}

def get_user_locations(user_id):
    return user_location_data.get(user_id, [])

def save_user_locations(user_id, locations):
    user_location_data[user_id] = locations


@router.message(Command("start"))

async def start_handler(message: Message,is_clb=False,**kwargs):
    await message.answer("erwtr")

@router.message(F.content_type.in_({'location'}))
async def handle_route(message: types.Message):
    if message.location:
        # Сохранение геолокации отправленной пользователем
        user_id = message.from_user.id
        user_locations = get_user_locations(user_id)  # Получаем текущие геолокации пользователя из памяти или базы данных
        
        if not user_locations:
            user_locations = []
        
        user_locations.append((message.location.latitude, message.location.longitude))
        save_user_locations(user_id, user_locations)  # Сохраняем обновленный список геолокаций
        
        if len(user_locations) == 2:
            point_a = user_locations[0]
            point_b = user_locations[1]
            await message.answer(f"Маршрут получен: A -> {point_a}, B -> {point_b}")
            # Очистить список геолокаций после получения маршрута
            save_user_locations(user_id, [])
        else:
            await message.answer("Отправьте геолокацию точки B для завершения маршрута.")
