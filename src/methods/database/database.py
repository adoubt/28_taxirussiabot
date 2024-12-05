import aiosqlite
from typing import Any,Optional,Tuple,List
from contextlib import asynccontextmanager
from src.misc import DB_PATH



class Database:
    """Асинхронный класс для работы с базой данных."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    @asynccontextmanager
    async def get_db_connection(self):
        """Асинхронный контекстный менеджер для работы с базой данных."""
        db = await aiosqlite.connect(self.db_path)
        try:
            yield db
        finally:
            await db.commit()
            await db.close()

    async def execute(self, query: str, params: tuple = ()) -> None:
        """Выполнение запроса без возврата значений."""
        async with self.get_db_connection() as db:
            await db.execute(query, params)
    async def execute_and_get_id(self, query: str, params: tuple = ()) ->  Optional[int]:
        """Выполнение запроса без возврата значений."""
        async with self.get_db_connection() as db:
            cursor = await db.execute(query, params)
            result = cursor.lastrowid
            return result if result else None

    async def fetch_one(self, query: str, params: tuple = ()) -> Optional[Tuple]:
        """Получить одну запись."""
        async with self.get_db_connection() as db:
            cursor = await db.execute(query, params)
            result =  await cursor.fetchone()
            return result if result else None

    async def fetch_all(self, query: str, params: tuple = ()) -> List[Tuple]:
        """Получить все записи."""
        async with self.get_db_connection() as db:
            cursor = await db.execute(query, params)
            result =  await cursor.fetchall()
            return result if result else None

     
    async def create_tables(self):
        await self.execute("""
            CREATE TABLE IF NOT EXISTS drivers (
                user_id INTEGER NOT NULL UNIQUE,
                location_id INTEGER NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                auto_id INTEGER DEFAULT NULL
            )""")
        await self.execute('''
            CREATE TABLE IF NOT EXISTS users(
                user_id INTEGER PRIMARY KEY,
                is_banned INTEGER DEFAULT 0,
                is_admin INTEGER DEFAULT 0,
                username TEXT DEFAULT NULL,
                subscription_type TEXT DEFAULT NULL,
                wallet_id INTEGER DEFAULT 0,
                language STRING DEFAULT NULL,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
        
        await self.execute('''
            CREATE TABLE IF NOT EXISTS locations(
                location_id INTEGER PRIMARY KEY AUTOINCREMENT,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL, 
                text TEXT DEFAUL NULL 
            )''')
        
        await self.execute('''
            CREATE TABLE IF NOT EXISTS vehicles (
                vehicle_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Уникальный идентификатор
                driver_id INTEGER NOT NULL,  -- Идентификатор водителя
                vehicle_type TEXT,  -- Тип транспорта (например, "car", "motorcycle")
                vehicle_model TEXT DEFAULT NULL,  -- Модель транспортного средства
                vehicle_color TEXT DEFAULT NULL,  -- Цвет транспортного средства
                license_plate TEXT DEFAULT NULL,  -- Номерной знак транспортного средства
                image_file_id TEXT DEFAULT NULL,  -- Ссылка на изображение транспортного средства (например, URL изображения)
                FOREIGN KEY (driver_id) REFERENCES drivers(id)  -- Связь с таблицей водителей
            )''')

            

class ActiveDriversMananger:
    """ Менеджер для работы с активными водителями"""

    def __init__(self, db: Database):
        self.db = db
       
    async def add_driver(self, user_id: int, location_id:int)-> None:
        await self.db.execute("""
                INSERT OR REPLACE INTO drivers (user_id, location_id, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (user_id, location_id))
            

    
    async def remove_driver(self, user_id: int)-> None:
        await self.db.execute("DELETE FROM drivers WHERE user_id = ?", (user_id,))
            

    
    async def update_driver_location(self, user_id: int, latitude: float, longitude: float)-> None:
        await self.add_driver(user_id, latitude, longitude)

    
    async def get_all_active_drivers(self):
        return await self.db.fetch_all("""
                SELECT *
                FROM drivers
                WHERE updated_at > DATETIME(CURRENT_TIMESTAMP, '-1 hour')
            """)
        
        



class UsersManager:
    def __init__(self, db: Database):
        self.db = db
    
    async def get_all(self):
        return await self.db.fetch_all(f'SELECT * FROM users')
                

    
    async def get_all_banned(self):
        return await self.db.fetch_all(f'SELECT * FROM users WHERE is_banned=1')
                

    
    async def get_user(self, user_id: int):
        return await self.db.fetch_one(f'SELECT * FROM users WHERE user_id = {user_id}')
                

    
    async def create_user(
        self,
        user_id:int,
        is_banned:int = 0,
        is_admin:int = 0, 
        username: str = None, 
        subscription_type: str = None,
        wallet_id :int = None,
        language: str = None,
    )-> None:
        query = '''
            INSERT INTO users(
                "user_id", "is_banned", "is_admin", "username", "subscription_type","wallet_id", "language"
            ) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
            '''
        await self.db.execute(query, (user_id, is_banned, is_admin, username, subscription_type,wallet_id,language))
            


    
    async def get_value(self, user_id: int, key: Any):
        return await self.db.fetch_one(f'SELECT {key} FROM users WHERE user_id = {user_id}')

    
    async def set_value(self, user_id: int, key: Any, new_value: Any)-> None:
        await self.db.execute(f'UPDATE users SET {key}=? WHERE user_id={user_id}',(new_value,))
            


            
    async def del_users(self)-> None:
        await self.db.execute(f'DELETE from users')
            

    
    async def is_banned(self, user_id: int):
        return await self.get_value(user_id, 'is_banned') 

    
    async def is_admin(self, user_id: int):
        return await self.get_value(user_id, 'is_admin') 
    
class VehiclesManager:
    def __init__(self, db: Database):
        self.db = db
    
    async def create_vehicle(
        self,
        driver_id:int,
        vehicle_type:str = 'car', 
        vehicle_model: str = None, 
        vehicle_color: str = None,
        license_plate:str = None,
        image_file_id: str = None,
    )-> None:
        query = '''
            INSERT INTO vehicles(
                "driver_id", "vehicle_type", "vehicle_model", "vehicle_color", "license_plate","image_file_id"
            ) 
            VALUES (?, ?, ?, ?, ?, ?)
            '''
        await self.db.execute(query, (driver_id, vehicle_type, vehicle_model, vehicle_color, license_plate,image_file_id))
            
    
    
    async def get_value(self, vehicle_id: int, key: Any):
        return await self.db.fetch_one(f'SELECT {key} FROM vehicles WHERE vehicle_id = {vehicle_id}')

    
    async def set_value(self, vehicle_id: int, key: Any, new_value: Any) -> None:
        await self.db.execute(f'UPDATE vehicles SET {key}=? WHERE vehicle_id={vehicle_id}',(new_value,))
            
     
    async def get_vehicles_by_driver(self,driver_id:int):
        return await self.db.fetch_all(f'SELECT * FROM vehicles WHERE driver_id = {driver_id}')
     
    async def get_vehicles(self):
        return await self.db.fetch_all(f'SELECT * FROM vehicles') 
            
class LocationsManager:
    
    def __init__(self, db: Database):
        self.db = db

    async def create_location(self,
                            latitude:str,
                            longitude:str, 
                            text:str = None)-> None:
        query = '''
            INSERT INTO locations(
                "latitude", "longitude", "text"
            ) 
            VALUES (?, ?, ?)
            '''
        result = await self.db.execute_and_get_id(query, (latitude, longitude, text))
        return result
    async def get_location(self,location_id:int)  :
        return await self.db.fetch_one(f'SELECT * FROM locations WHERE location_id = {location_id}')      

class DBService:
    """Сервис для работы бд."""

    def __init__(self):
        self.db = Database()
        self.active_drivers_manager = ActiveDriversMananger(self.db)
        self.users_manager = UsersManager(self.db)
        self.locations_manager = LocationsManager(self.db)
        self.vehicles_maanger = VehiclesManager(self.db)

    async def _initialize_db(self):
        """Инициализация БД."""
        await self.db.create_tables()


    async def add_driver(self,user_id:int,latitude: float, longitude: float):
        location_id = await self.locations_manager.create_location(latitude, longitude)
        await self.active_drivers_manager.add_driver( user_id, location_id)

    async def get_user(self,user_id):
        return await self.users_manager.get_user(user_id)
    
    async def create_user(self,user_id,username):
        await self.users_manager.create_user(user_id,username)

    async def set_admin(self,user_id):
        return await self.users_manager.set_value(user_id,'is_admin',1)
    
    async def unset_admin(self,user_id):
        return await self.users_manager.set_value(user_id,'is_admin',0)
    async def get_nearby_active_drivers(self,latitude, longitude, radius_km:float=5.0):
        result =  await self.active_drivers_manager.get_all_active_drivers()
        active_drivers = []
        if result:
            for row in result:
                driver_id, location_id,updated_at = row[0],row[1],row[3]
                location = await self.locations_manager.get_location(location_id)
                driver_lat,driver_lon = location[1],location[2]

                distance = ((driver_lat - latitude) ** 2 + (driver_lon - longitude) ** 2) ** 0.5 * 111  # простое приближение
                if distance <= radius_km:
                    active_drivers.append((driver_id, driver_lat, driver_lon, distance))
        return active_drivers