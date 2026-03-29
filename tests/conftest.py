import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, DATABASE, init_db


@pytest.fixture
def client(tmp_path, monkeypatch):
    """テスト用のFlaskクライアントを生成し、一時DBを使用する"""
    db_path = str(tmp_path / "test.db")
    monkeypatch.setattr("app.DATABASE", db_path)
    app.config["TESTING"] = True

    # 一時DBでテーブルを初期化
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.execute('''CREATE TABLE IF NOT EXISTS tasks
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         title TEXT NOT NULL,
         description TEXT DEFAULT '',
         done INTEGER DEFAULT 0,
         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_task(client):
    """テスト用のサンプルタスクを作成する"""
    response = client.post("/tasks", json={
        "title": "テストタスク",
        "description": "テスト用の説明"
    })
    return response.get_json()
