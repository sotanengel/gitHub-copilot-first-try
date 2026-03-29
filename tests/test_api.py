"""結合テスト: タスクAPIの各エンドポイントをテストする"""


class TestGetTasks:
    """GET /tasks のテスト"""

    def test_空のタスク一覧を取得(self, client):
        response = client.get("/tasks")
        assert response.status_code == 200
        assert response.get_json() == []

    def test_タスク作成後に一覧取得(self, client, sample_task):
        response = client.get("/tasks")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]["title"] == "テストタスク"


class TestGetTask:
    """GET /tasks/<id> のテスト"""

    def test_存在するタスクを取得(self, client, sample_task):
        task_id = sample_task["id"]
        response = client.get(f"/tasks/{task_id}")
        assert response.status_code == 200
        data = response.get_json()
        assert data["title"] == "テストタスク"
        assert data["description"] == "テスト用の説明"

    def test_存在しないタスクを取得すると404(self, client):
        response = client.get("/tasks/9999")
        assert response.status_code == 404
        assert "error" in response.get_json()


class TestCreateTask:
    """POST /tasks のテスト"""

    def test_タスクを正常に作成(self, client):
        response = client.post("/tasks", json={"title": "新しいタスク", "description": "説明文"})
        assert response.status_code == 201
        data = response.get_json()
        assert data["title"] == "新しいタスク"
        assert data["description"] == "説明文"
        assert data["done"] is False
        assert "id" in data

    def test_タイトルなしでタスク作成すると400(self, client):
        response = client.post("/tasks", json={"description": "説明のみ"})
        assert response.status_code == 400

    def test_説明なしでタスク作成(self, client):
        response = client.post("/tasks", json={"title": "タイトルのみ"})
        assert response.status_code == 201
        data = response.get_json()
        assert data["description"] == ""

    def test_JSONなしでタスク作成するとエラー(self, client):
        response = client.post("/tasks", data="not json", content_type="text/plain")
        assert response.status_code in (400, 415)


class TestUpdateTask:
    """PUT /tasks/<id> のテスト"""

    def test_タスクのタイトルを更新(self, client, sample_task):
        task_id = sample_task["id"]
        response = client.put(f"/tasks/{task_id}", json={"title": "更新されたタスク"})
        assert response.status_code == 200
        data = response.get_json()
        assert data["title"] == "更新されたタスク"

    def test_タスクの完了状態を更新(self, client, sample_task):
        task_id = sample_task["id"]
        response = client.put(f"/tasks/{task_id}", json={"done": True})
        assert response.status_code == 200
        data = response.get_json()
        assert data["done"] is True

    def test_存在しないタスクを更新すると404(self, client):
        response = client.put("/tasks/9999", json={"title": "更新"})
        assert response.status_code == 404


class TestDeleteTask:
    """DELETE /tasks/<id> のテスト"""

    def test_タスクを正常に削除(self, client, sample_task):
        task_id = sample_task["id"]
        response = client.delete(f"/tasks/{task_id}")
        assert response.status_code == 200
        # 削除後に再取得すると404
        response = client.get(f"/tasks/{task_id}")
        assert response.status_code == 404

    def test_存在しないタスクを削除すると404(self, client):
        response = client.delete("/tasks/9999")
        assert response.status_code == 404


class TestSearchTasks:
    """GET /tasks/search のテスト"""

    def test_タスクを検索(self, client, sample_task):
        response = client.get("/tasks/search?q=テスト")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) >= 1
        assert data[0]["title"] == "テストタスク"

    def test_存在しないキーワードで検索(self, client, sample_task):
        response = client.get("/tasks/search?q=存在しない")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 0

    def test_検索クエリなしだと400(self, client):
        response = client.get("/tasks/search")
        assert response.status_code == 400


class TestToggleTask:
    """PATCH /tasks/<id>/toggle のテスト"""

    def test_タスクの完了状態をトグル(self, client, sample_task):
        task_id = sample_task["id"]
        # 未完了 → 完了
        response = client.patch(f"/tasks/{task_id}/toggle")
        assert response.status_code == 200
        data = response.get_json()
        assert data["done"] is True
        # 完了 → 未完了
        response = client.patch(f"/tasks/{task_id}/toggle")
        assert response.status_code == 200
        data = response.get_json()
        assert data["done"] is False

    def test_存在しないタスクをトグルすると404(self, client):
        response = client.patch("/tasks/9999/toggle")
        assert response.status_code == 404
