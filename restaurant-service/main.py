import http
import typing as tp

from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import select

from common.database.dbsetup import init_db, SessionDep
from common.database.models import MenuItem, Restaurant
from common.database.schemas import (
    MenuItemOutSchema,
    MenuItemSchema,
    RestaurantOutSchema,
    RestaurantSchema,
)

app = FastAPI(title="Restaurant Service API")


@app.on_event("startup")
async def on_startup():
    await init_db()


@app.get("/ping")
async def ping() -> tp.Dict[str, str]:
    return {"status": "ok"}


@app.get("/restaurants", response_model=tp.List[RestaurantOutSchema])
async def get_all_restaurants(session: SessionDep):
    restaurants = (await session.exec(select(Restaurant))).all()
    return restaurants


@app.post("/restaurants", response_model=RestaurantOutSchema)
async def create_restaurant(restaurant_schema: RestaurantSchema, session: SessionDep):
    restaurant = Restaurant(
        name=restaurant_schema.name,
        description=restaurant_schema.description,
        address=restaurant_schema.address,
    )
    session.add(restaurant)
    await session.commit()
    await session.refresh(restaurant)
    return restaurant


@app.get("/restaurants/{restaurant_id}", response_model=RestaurantOutSchema)
async def get_restaurant_by_id(restaurant_id: int, session: SessionDep):
    restaurant = (await session.exec(select(Restaurant).where(Restaurant.id == restaurant_id))).one_or_none()
    if restaurant is None:
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail="Restaurant not found")
    return restaurant


@app.get("/restaurants/by-name/{restaurant_name}", response_model=RestaurantOutSchema)
async def get_restaurant_by_name(restaurant_name: str, session: SessionDep):
    restaurant = (await session.exec(select(Restaurant).where(Restaurant.name == restaurant_name))).one_or_none()
    if restaurant is None:
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail="Restaurant not found")
    return restaurant


@app.put("/restaurants/{restaurant_id}", response_model=RestaurantOutSchema)
async def update_restaurant(restaurant_id: int, restaurant_schema: RestaurantSchema, session: SessionDep):
    restaurant = (await session.exec(select(Restaurant).where(Restaurant.id == restaurant_id))).one_or_none()
    if restaurant is None:
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail="Restaurant not found")
    restaurant.name = restaurant_schema.name
    restaurant.description = restaurant_schema.description
    restaurant.address = restaurant_schema.address
    session.add(restaurant)
    await session.commit()
    await session.refresh(restaurant)
    return restaurant


@app.delete("/restaurants/{restaurant_id}")
async def delete_restaurant(restaurant_id: int, session: SessionDep) -> tp.Dict[str, str]:
    restaurant = (await session.exec(select(Restaurant).where(Restaurant.id == restaurant_id))).one_or_none()
    if restaurant is None:
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail="Restaurant not found")
    await session.delete(restaurant)
    await session.commit()
    return {"message": f"Restaurant [{restaurant_id}] deleted"}


@app.post("/restaurants/{restaurant_id}/menu-items", response_model=MenuItemOutSchema)
async def add_menu_item_to_restaurant(restaurant_id: int, menu_item_schema: MenuItemSchema, session: SessionDep):
    restaurant = (await session.exec(select(Restaurant).where(Restaurant.id == restaurant_id))).one_or_none()
    if restaurant is None:
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail="Restaurant not found")
    menu_item = MenuItem(
        name=menu_item_schema.name,
        description=menu_item_schema.description,
        price=menu_item_schema.price,
        is_available=menu_item_schema.is_available,
        category=menu_item_schema.category,
        restaurant_id=restaurant_id,
    )
    session.add(menu_item)
    session.add(restaurant)
    await session.commit()
    await session.refresh(menu_item)
    await session.refresh(restaurant)

    return menu_item


@app.get("/restaurants/{restaurant_id}/menu-items", response_model=tp.List[MenuItemOutSchema])
async def get_restaurant_menu_items(restaurant_id: int, session: SessionDep, only_available: bool = False):
    query = select(Restaurant).where(Restaurant.id == restaurant_id).options(selectinload(Restaurant.menu_items))
    restaurant = (await session.exec(query)).one_or_none()
    if restaurant is None:
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail="Restaurant not found")

    menu_items = restaurant.menu_items
    if only_available:
        return [menu_item for menu_item in menu_items if menu_item.is_available]
    return menu_items


@app.get("/menu-items/{menu_item_id}", response_model=MenuItemOutSchema)
async def get_menu_item_by_id(menu_item_id: int, session: SessionDep):
    menu_item = (await session.exec(select(MenuItem).where(MenuItem.id == menu_item_id))).one_or_none()
    if menu_item is None:
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail="Menu item not found")
    return menu_item


@app.put("/menu-items/{menu_item_id}", response_model=MenuItemOutSchema)
async def update_menu_item(menu_item_id: int, menu_item_schema: MenuItemSchema, session: SessionDep):
    menu_item = (await session.exec(select(MenuItem).where(MenuItem.id == menu_item_id))).one_or_none()
    if menu_item is None:
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail="Menu item not found")
    menu_item.name = menu_item_schema.name
    menu_item.description = menu_item_schema.description
    menu_item.price = menu_item_schema.price
    menu_item.is_available = menu_item_schema.is_available
    menu_item.category = menu_item_schema.category

    session.add(menu_item)
    await session.commit()
    await session.refresh(menu_item)
    return menu_item


@app.delete("/menu-items/{menu_item_id}", response_model=MenuItemOutSchema)
async def delete_menu_item(menu_item_id: int, session: SessionDep):
    menu_item = (await session.exec(select(MenuItem).where(MenuItem.id == menu_item_id))).one_or_none()
    if menu_item is None:
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail="Menu item not found")
    await session.delete(menu_item)
    await session.commit()
    return menu_item
