import typing as tp

import pydantic

from common.database.models import OrderStatus

class RestaurantSchema(pydantic.BaseModel):
    name: str = pydantic.Field(max_length=255)
    description: tp.Optional[str] = pydantic.Field(max_length=500)
    address: tp.Optional[str] = pydantic.Field(max_length=255)


class MenuItemSchema(pydantic.BaseModel):
    name: str = pydantic.Field(max_length=255)
    description: tp.Optional[str] = pydantic.Field(max_length=500)
    price: int = pydantic.Field(default=0, ge=0)
    is_available: bool = pydantic.Field(default=True)
    category: str = pydantic.Field(max_length=255)


class MenuItemOutSchema(MenuItemSchema):
    id: tp.Optional[int] = pydantic.Field(default=None)


class RestaurantOutSchema(RestaurantSchema):
    id: tp.Optional[int] = pydantic.Field(default=None)


class OrderItemInSchema(pydantic.BaseModel):
    menu_item_id: int
    quantity: int = pydantic.Field(default=1, ge=1)

class OrderItemOutSchema(pydantic.BaseModel):
    menu_item_name: str
    quantity: int = pydantic.Field(default=1, ge=1)
    price: int = pydantic.Field(ge=0)


class OrderOutSchema(pydantic.BaseModel):
    id: tp.Optional[int] = pydantic.Field(default=None)
    customer_name: tp.Optional[str] = pydantic.Field(max_length=100)
    customer_phone: str = pydantic.Field(max_length=100)
    delivery_address: str = pydantic.Field(max_length=255)
    items: tp.List[OrderItemOutSchema]
    status: OrderStatus


class OrderInSchema(pydantic.BaseModel):
    customer_name: tp.Optional[str] = pydantic.Field(max_length=100, default=None)
    customer_phone: str = pydantic.Field(max_length=100)
    delivery_address: str = pydantic.Field(max_length=255)
    restaurant_id: int
    items: tp.List[OrderItemInSchema]
