from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

class KBClient:
    def generate_driver_card(drivers:list,latitude:float,longitude:float,page:int=0) -> InlineKeyboardMarkup:
        if page <0:
            driver = drivers[-1] 
            page = len(drivers)-1
        else:
            driver = drivers[page % len(drivers)] 
            page = page % len(drivers)
        url = f"https://t.me/user?id={driver[0]}"
        chat_btn = [
            InlineKeyboardButton(text="Чат с водителем", url=url)
        ]
        pages_btns = [
            [InlineKeyboardButton(text="‹", callback_data=f'drivercard:page={page+1}&latitude={latitude}&longitude={longitude}'),
            InlineKeyboardButton(text="›", callback_data=f"drivercard:page={page-1}&latitude={latitude}&longitude={longitude}")]
            
        ]
        back_btn = [InlineKeyboardButton(text="Назад", callback_data="start")]
        ikb = [chat_btn] +pages_btns + [back_btn]
      
        return InlineKeyboardMarkup(inline_keyboard=ikb)
    


    def get_start_kb()-> InlineKeyboardMarkup:
        ikb =[
            [InlineKeyboardButton(text="Найти машину",callback_data="location:method=client"),
             InlineKeyboardButton(text="Работать",callback_data="location:method=worker"),
             ]
            ]
        return InlineKeyboardMarkup(inline_keyboard=ikb)
    
    def get_location_kb() -> ReplyKeyboardMarkup:
        rkb = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="Отправить локацию", request_location=True)]
            ],resize_keyboard=True, one_time_keyboard=True)
        return rkb
    def get_location_remind_kb() -> ReplyKeyboardMarkup:
        rkb = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="Отправить локацию", request_location=True)]
            ],resize_keyboard=True, one_time_keyboard=True)
        return rkb

class KBWorker:

    def generate_driver_card() -> InlineKeyboardMarkup:
        
        ikb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="callback",callback_data="callback")]
            ]) 
        return ikb
    
