from .db import database
from .models.item import ItemModel


async def create_init_data():
    products_data = [
        {"name": "t-shirt", "price": 80},
        {"name": "cup", "price": 20},
        {"name": "book", "price": 50},
        {"name": "pen", "price": 10},
        {"name": "powerbank", "price": 200},
        {"name": "hoody", "price": 300},
        {"name": "umbrella", "price": 200},
        {"name": "socks", "price": 10},
        {"name": "wallet", "price": 50},
        {"name": "pink-hoody", "price": 500},
        {"name": "expensive", "price": 100000},
    ]

    async with database.async_session() as session:
        for product_data in products_data:
            session.add(ItemModel(**product_data))
        await session.commit()
