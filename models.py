import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, DateTime, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    parent_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"))

    # Связь для работы с деревом (Self-referential relationship)
    subcategories = relationship("Category", backref="parent", remote_side=[id])


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    price = Column(Numeric(12, 2), nullable=False)
    stock_quantity = Column(Integer, default=0)


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    address = Column(String)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    # Используем datetime.datetime.now без скобок, чтобы функция вызывалась в момент создания записи
    created_at = Column(DateTime, default=datetime.datetime.now)


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False)
    price_at_order = Column(Numeric(12, 2), nullable=False)

    __table_args__ = (
        UniqueConstraint('order_id', 'product_id', name='_order_product_uc'),
    )
