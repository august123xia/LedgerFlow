from app_sqlite import app
import sqlite3


def test_home():
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert response.get_data(as_text=True) == "Hello Flask + SQLite"


def test_create_invoice(tmp_path, monkeypatch):
    # 1. 创建临时数据库路径
    test_db = tmp_path / "ledgerflow_test.db"

    # 2. 创建数据库和表
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT,
            amount REAL,
            status TEXT
        )
        """
    )

    conn.commit()
    cursor.close()
    conn.close()

    # 3. 临时替换 Flask 的数据库路径
    monkeypatch.setattr("app_sqlite.DB_PATH", test_db)

    # 4. 创建测试客户端
    client = app.test_client()

    # 5. 模拟 POST 请求
    response = client.post("/invoices", json={
        "customer": "Qantas",
        "amount": 2500,
        "status": "unpaid"
    })
    assert response.status_code == 201

    get_response = client.get("/invoices")
    invoices = get_response.get_json()

    assert invoices[0]["customer"] == "Qantas"
    assert invoices[0]["amount"] == 2500
    assert invoices[0]["status"] == "unpaid"

    patch_response = client.patch("/invoices/1", json={
      "status": "paid"
    })

    assert patch_response.status_code == 200

    get_response = client.get("/invoices")
    invoices = get_response.get_json()
   

    # 6. 检查结果
    assert invoices[0]["status"] == "paid"

    delete_response = client.delete("/invoices/1")

    assert delete_response.status_code == 200

    # 重新 GET 查询数据库
    get_response = client.get("/invoices")
    invoices = get_response.get_json()

    # 验证数据库已经没有发票
    assert invoices == []


import pytest
import sqlite3
from app_sqlite import app

@pytest.fixture
def client(tmp_path, monkeypatch):

    # 创建临时数据库
    test_db = tmp_path / "ledgerflow_test.db"

    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()

    # 创建 invoices 表
    cursor.execute("""
        CREATE TABLE invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT,
            amount REAL,
            status TEXT
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()

    # 让 Flask 使用临时数据库
    monkeypatch.setattr("app_sqlite.DB_PATH", test_db)

    # 返回 Flask Test Client
    return app.test_client()


# 独立的 POST 测试
def test_create_invoice(client):

    response = client.post("/invoices", json={
        "customer": "Qantas",
        "amount": 2500,
        "status": "unpaid"
    })

    assert response.status_code == 201


def test_update_invoice(client):

    # 第一步：创建发票
    response = client.post("/invoices", json={
        "customer": "Qantas",
        "amount": 2500,
        "status": "unpaid"
    })

    assert response.status_code == 201

    # 第二步：更新发票
    patch_response = client.patch(
        "/invoices/1",
        json={"status": "paid"}
    )

    assert patch_response.status_code == 200

        # 第三步：GET 验证更新结果
    get_response = client.get("/invoices")
    invoices = get_response.get_json()

    assert invoices[0]["status"] == "paid"


def test_delete_invoice(client):

    # 第一步：创建发票
    response = client.post("/invoices", json={
        "customer": "Qantas",
        "amount": 2500,
        "status": "unpaid"
    })

    assert response.status_code == 201

    # 第二步：删除发票
    delete_response = client.delete("/invoices/1")

    # 验证删除成功
    assert delete_response.status_code == 200

    # 第三步：GET 查询所有发票
    get_response = client.get("/invoices")

    # 获取 JSON 数据
    invoices = get_response.get_json()

    # 验证发票列表为空
    assert invoices == []

def test_delete_nonexistent_invoice(client):
    response = client.delete("/invoices/999")
    assert response.status_code == 404

def test_create_invoice_invalid_amount(client):

    response = client.post("/invoices", json={
        "customer": "Qantas",
        "amount": -100,
        "status": "unpaid"
    })

    assert response.status_code == 400