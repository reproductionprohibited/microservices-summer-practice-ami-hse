import http
import typing as tp

import httpx
from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import select

from common.database.dbsetup import init_db, SessionDep
from common.database.models import Order, OrderItem, OrderStatus
from common.database.schemas import OrderInSchema, OrderItemOutSchema, OrderOutSchema
from common.settings import RESTAURANT_SERVICE_URL

app = FastAPI(title="Order Service API")


@app.on_event("startup")
async def on_startup():
    await init_db()


@app.get("/ping")
async def ping():
    return {"status": "ok"}


@app.get("/orders", response_model=tp.List[OrderOutSchema])
async def get_orders(session: SessionDep):
    orders = (await session.exec(select(Order).options(selectinload(Order.items)))).all()
    return orders


@app.get("/orders/{order_id}", response_model=OrderOutSchema)
async def get_order_by_id(order_id: int, session: SessionDep):
    order = (
        await session.exec(select(Order).where(Order.id == order_id).options(selectinload(Order.items)))).one_or_none()
    if order is None:
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail="Order not found")
    return order


@app.post("/orders")
async def create_order(order_schema: OrderInSchema, session: SessionDep):
    order_items = []
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{RESTAURANT_SERVICE_URL}/restaurants/{order_schema.restaurant_id}")
        if resp.status_code == http.HTTPStatus.NOT_FOUND:
            raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail="Restaurant not found")
        elif resp.status_code >= 500:
            raise HTTPException(status_code=http.HTTPStatus.SERVICE_UNAVAILABLE,
                                detail="Restaurant service unavailable")

        for item in order_schema.items:
            resp = await client.get(f"{RESTAURANT_SERVICE_URL}/menu-items/{item.menu_item_id}")
            if resp.status_code == http.HTTPStatus.NOT_FOUND:
                raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail=f"Menu item not found")
            elif resp.status_code >= 500:
                raise HTTPException(status_code=http.HTTPStatus.SERVICE_UNAVAILABLE,
                                    detail="Restaurant service unavailable")

            data = resp.json()
            if data['is_available'] is False:
                raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND,
                                    detail="Menu item is not available for order")

            item = OrderItem(
                menu_item_id=item.menu_item_id,
                menu_item_name=data["name"],
                price=data["price"],
                quantity=item.quantity,
            )
            order_items.append(item)

    order = Order(
        customer_name=order_schema.customer_name,
        customer_phone=order_schema.customer_phone,
        delivery_address=order_schema.delivery_address,
        restaurant_id=order_schema.restaurant_id,
    )

    session.add(order)
    await session.commit()
    await session.refresh(order)

    for order_item in order_items:
        order_item.order_id = order.id
        session.add(order_item)

    await session.commit()
    await session.refresh(order)

    return OrderOutSchema(
        customer_name=order.customer_name,
        customer_phone=order.customer_phone,
        delivery_address=order.delivery_address,
        items=[
            OrderItemOutSchema(
                menu_item_name=item.menu_item_name,
                quantity=item.quantity,
                price=item.price,
            )
            for item in order_items
        ]
    )


@app.post("/orders/{order_id}/change-status", response_model=OrderOutSchema)
async def change_order_status(order_id: int, status: OrderStatus, session: SessionDep):
    order = (
        await session.exec(select(Order).where(Order.id == order_id).options(selectinload(Order.items)))).one_or_none()
    if order is None:
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail="Order not found")
    order.status = status
    session.add(order)
    await session.commit()
    await session.refresh(order)

    return order


@app.delete("/orders/{order_id}")
async def delete_order(order_id: int, session: SessionDep) -> tp.Dict[str, str]:
    order = (await session.exec(select(Order).where(Order.id == order_id))).one_or_none()
    if order is None:
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail="Order not found")
    await session.delete(order)
    await session.commit()
    return {"status": f"Order [{order_id}] deleted"}
