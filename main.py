import logging
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Импорты из твоих файлов
from database import SessionLocal, engine
from models import Base, Product, OrderItem, Order

# Настройка логирования, чтобы видеть события в консоли Docker
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Создание таблиц (TODO: в продакшене лучше использовать Alembic для миграций)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Inventory Service")


# Dependency для работы с сессией БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class AddItemSchema(BaseModel):
    order_id: int
    product_id: int
    quantity: int


@app.post("/order/add-item")
def add_item_to_order(data: AddItemSchema, db: Session = Depends(get_db)):
    logger.info(f"Запрос на добавление: заказ={data.order_id}, товар={data.product_id}, кол-во={data.quantity}")

    # 1. Проверка существования заказа (обязательно для корректности бизнес-логики)
    order = db.query(Order).filter(Order.id == data.order_id).first()
    if not order:
        logger.warning(f"Заказ {data.order_id} не найден в базе")
        raise HTTPException(status_code=404, detail=f"Заказ с ID {data.order_id} не существует")

    # 2. Проверка наличия товара
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        logger.warning(f"Товар {data.product_id} не найден")
        raise HTTPException(status_code=404, detail="Товар не найден")

    # 3. Проверка остатков
    if product.stock_quantity < data.quantity:
        logger.error(
            f"Недостаточно товара {data.product_id}. Требуется: {data.quantity}, в наличии: {product.stock_quantity}")
        raise HTTPException(status_code=400, detail="Товара недостаточно на складе")

    try:
        # 4. Поиск товара в текущем заказе
        item = db.query(OrderItem).filter(
            OrderItem.order_id == data.order_id,
            OrderItem.product_id == data.product_id
        ).first()

        if item:
            logger.info(f"Товар {data.product_id} уже есть в заказе {data.order_id}. Увеличиваем количество.")
            item.quantity += data.quantity
        else:
            logger.info(f"Добавляем новую позицию товара {data.product_id} в заказ {data.order_id}")
            item = OrderItem(
                order_id=data.order_id,
                product_id=data.product_id,
                quantity=data.quantity,
                price_at_order=product.price  # Фиксируем цену на момент покупки
            )
            db.add(item)

        # 5. Списание остатка (FIXME: возможно возникновение Race Condition при высокой нагрузке)
        product.stock_quantity -= data.quantity

        db.commit()
        db.refresh(item)

        logger.info(f"Успешно: товар {data.product_id} добавлен. Новый остаток: {product.stock_quantity}")
        return {"status": "success", "current_quantity": item.quantity}

    except Exception as e:
        db.rollback()
        logger.error(f"Критическая ошибка при обновлении заказа: {str(e)}")
        raise HTTPException(status_code=500, detail="Ошибка при обработке заказа")
