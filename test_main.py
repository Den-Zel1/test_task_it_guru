import pytest
from fastapi.testclient import TestClient
from main import app
from database import SessionLocal
from models import Product, Order, Client, Category

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    # Настройка тестовых данных
    db = SessionLocal()
    cat = Category(name="TestCat")
    db.add(cat)
    db.commit()

    prod = Product(id=100, name="TestProd", category_id=cat.id, price=100, stock_quantity=10)
    cl = Client(id=1, name="TestClient")
    db.add_all([prod, cl])
    db.commit()

    order = Order(id=1, client_id=1)
    db.add(order)
    db.commit()
    db.close()
    yield


def test_add_new_item_success():
    response = client.post("/order/add-item", json={"order_id": 1, "product_id": 100, "quantity": 2})
    assert response.status_code == 200
    assert response.json()["current_quantity"] == 2


def test_increase_existing_item_quantity():
    # Добавляем еще 3 штуки к уже имеющимся 2
    response = client.post("/order/add-item", json={"order_id": 1, "product_id": 100, "quantity": 3})
    assert response.status_code == 200
    assert response.json()["current_quantity"] == 5


def test_out_of_stock_error():
    # Пытаемся взять больше, чем осталось (осталось 5)
    response = client.post("/order/add-item", json={"order_id": 1, "product_id": 100, "quantity": 10})
    assert response.status_code == 400
    assert "недостаточно на складе" in response.json()["detail"]
