import enum
import typing as tp

import sqlalchemy
import sqlmodel


class Restaurant(sqlmodel.SQLModel, table=True):
    __tablename__ = "restaurants"

    id: tp.Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    name: str = sqlmodel.Field(index=True, nullable=False, max_length=255)
    description: tp.Optional[str] = sqlmodel.Field(max_length=500)
    address: tp.Optional[str] = sqlmodel.Field(max_length=255)

    menu_items: tp.List["MenuItem"] = sqlmodel.Relationship(back_populates="restaurant", cascade_delete=True)
    orders: tp.List["Order"] = sqlmodel.Relationship(back_populates="restaurant", cascade_delete=True)


class MenuItem(sqlmodel.SQLModel, table=True):
    __tablename__ = "menu_items"

    id: tp.Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    restaurant_id: tp.Optional[int] = sqlmodel.Field(default=None, foreign_key="restaurants.id")
    name: str = sqlmodel.Field(index=True, nullable=False, max_length=255)
    description: tp.Optional[str] = sqlmodel.Field(max_length=500)
    price: int = sqlmodel.Field(nullable=False, default=0, ge=0)
    is_available: bool = sqlmodel.Field(nullable=False, default=True)
    category: str = sqlmodel.Field(nullable=False, max_length=255)

    restaurant: tp.Optional["Restaurant"] = sqlmodel.Relationship(back_populates="menu_items")


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PREPARING = "preparing"
    DELIVERING = "delivering"
    DELIVERED = "delivered"
    CANCELED = "canceled"


class Order(sqlmodel.SQLModel, table=True):
    __tablename__ = "orders"

    id: tp.Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    customer_name: tp.Optional[str] = sqlmodel.Field(max_length=100)
    customer_phone: str = sqlmodel.Field(nullable=False, max_length=100)
    delivery_address: str = sqlmodel.Field(nullable=False, max_length=255)
    restaurant_id: tp.Optional[int] = sqlmodel.Field(default=None, foreign_key="restaurants.id")
    status: OrderStatus = sqlmodel.Field(
        sa_column=sqlalchemy.Column(
            sqlalchemy.Enum(OrderStatus, name="orderstatus", create_type=False),
            nullable=False,
            default=OrderStatus.PENDING
        )
    )

    items: tp.List["OrderItem"] = sqlmodel.Relationship(back_populates="order", cascade_delete=True)
    restaurant: "Restaurant" = sqlmodel.Relationship(back_populates="orders")


class OrderItem(sqlmodel.SQLModel, table=True):
    __tablename__ = "order_items"

    id: tp.Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    order_id: tp.Optional[int] = sqlmodel.Field(default=None, foreign_key="orders.id")
    menu_item_id: int = sqlmodel.Field(foreign_key="menu_items.id")
    menu_item_name: str = sqlmodel.Field(nullable=False, max_length=255)
    price: int = sqlmodel.Field(nullable=False, default=0, ge=0)
    quantity: int = sqlmodel.Field(nullable=False, default=1, ge=1)

    order: "Order" = sqlmodel.Relationship(back_populates="items")
