import asyncio
from aiogram import types
from aiogram import Router, F
from aiogram.filters import Command,StateFilter
from aiogram.types import Message,Location, CallbackQuery
from src.keyboards.user_keyboards import KBClient, KBWorker 
from src.handlers.decorators import new_user_handler
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from src.methods.utils import parse_callback_data
from src.methods.database.database import DBService
# db_users = UsersManager()
# db_drivers = ActiveDriversMananger()
# db_locations = LocationsManager() 
# db_vehicles = VehiclesManager()
db = DBService()
router =  Router()
from src.misc import dp, bot,bot_id
user_location_data = {}

def get_user_locations(user_id):
    return user_location_data.get(user_id, [])

def save_user_locations(user_id, locations):
    user_location_data[user_id] = locations



@router.message(Command("start"))
@new_user_handler
async def start_handler(message: types.Message,*args, **kwargs):
    await message.answer("Добро пожаловать! Выберите действие:", reply_markup=KBClient.get_start_kb())

@router.callback_query(lambda clb: clb.data == 'start')
async def start_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    await start_handler(clb.message, is_clb=True)

@router.message(lambda msg: msg.location is not None)
async def location_handler(message: types.Message, state = FSMContext,*args, **kwargs):
    user_id = message.chat.id
    latitude = message.location.latitude
    longitude = message.location.longitude
    current_state = await state.get_state()
    # if current_state is None:
    #     return
    await message.delete_reply_markup()

    if current_state == 'LocationMethod:client' or current_state is None:
        drivers = await db.get_nearby_active_drivers(latitude, longitude)
        if not drivers:
            await message.answer("Рядом нет доступных водителей.")
        else:
            driver_id, _, _, distance = drivers[0]
            text = f"Доступный водитель: {driver_id}\nРасстояние: {distance:.2f} км"
            # Тут достаем весь контент о машине

            await message.answer_photo(photo="https://via.placeholder.com/300x150.png?text=Driver+Car", caption=text, reply_markup=KBClient.generate_driver_card(drivers,latitude,longitude))
    elif current_state == 'LocationMethod:worker':
        await db.add_driver(user_id, latitude, longitude)
        await message.answer("Вы успешно добавлены в список активных водителей. Ваш статус действителен 1 час.")
    await state.clear()


@router.callback_query(lambda clb: clb.data.startswith("drivercard"))
async def drivercard(clb: CallbackQuery,*args, **kwargs):
    user_id = clb.from_user.id
    parsed_data = parse_callback_data(clb.data)
    page = int(parsed_data.get('page')) if parsed_data.get('page') else None
    latitude = float(parsed_data.get('latitude')) if parsed_data.get('latitude') else None
    longitude = float(parsed_data.get('longitude'))if parsed_data.get('longitude') else None

    drivers = await db.get_nearby_active_drivers(latitude, longitude)
    if not drivers:
        await clb.message.answer("Рядом нет доступных водителей.")
    else:
        driver_id, _, _, distance = drivers[0]
        text = f"Всего водителей: {len(drivers)}\n\nДоступный водитель: {driver_id}\nРасстояние: {distance:.2f} км"
        # Тут достаем весь контент о машине
        
        await clb.message.answer_photo(photo="https://via.placeholder.com/300x150.png?text=Driver+Car", caption=text, reply_markup=KBClient.generate_driver_card(drivers,latitude,longitude,page))

@router.message(Command("remind_location"))
async def remind_location(message: types.Message,*args, **kwargs):
    await message.answer(
        "Пожалуйста, обновите вашу локацию:",
        reply_markup=KBClient.get_location_remind_kb()
    )


class LocationMethod(StatesGroup):
    client = State()
    worker = State()



@router.callback_query(lambda clb: clb.data.startswith("location"))
async def location_ask(clb: CallbackQuery, state : FSMContext, is_clb=True, **kwargs):
    user_id = clb.from_user.id
    parsed_data = parse_callback_data(clb.data)
    
    method = parsed_data.get('method') if parsed_data.get('method') else None

    await state.clear()
    if method == 'client':
        await state.set_state(LocationMethod.client)
    elif method == 'worker':
        await state.set_state(LocationMethod.worker)
    else:
        await clb.answer('Не пон зач локация')
    await clb.message.answer('Пожалуйста, отправьте вашу локацию:',reply_markup=KBClient.get_location_kb())
    
