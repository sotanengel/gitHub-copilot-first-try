"""連結テスト: 複数のAPIエンドポイントを組み合わせたシナリオテスト"""


class TestTaskLifecycle:
    """タスクの作成から削除までの一連のフローをテストする"""

    def test_タスクの作成_更新_完了_削除フロー(self, client):
        # 1. タスクを作成
        res = client.post(
            "/tasks", json={"title": "買い物リスト作成", "description": "牛乳、卵、パンを買う"}
        )
        assert res.status_code == 201
        task_id = res.get_json()["id"]

        # 2. タスクが一覧に存在することを確認
        res = client.get("/tasks")
        assert res.status_code == 200
        tasks = res.get_json()
        assert any(t["id"] == task_id for t in tasks)

        # 3. タスクの内容を更新
        res = client.put(
            f"/tasks/{task_id}",
            json={
                "title": "買い物リスト作成（更新済）",
                "description": "牛乳、卵、パン、バターを買う",
            },
        )
        assert res.status_code == 200
        assert res.get_json()["title"] == "買い物リスト作成（更新済）"

        # 4. タスクを完了にトグル
        res = client.patch(f"/tasks/{task_id}/toggle")
        assert res.status_code == 200
        assert res.get_json()["done"] is True

        # 5. 完了状態で詳細を確認
        res = client.get(f"/tasks/{task_id}")
        assert res.status_code == 200
        assert res.get_json()["done"] is True

        # 6. タスクを削除
        res = client.delete(f"/tasks/{task_id}")
        assert res.status_code == 200

        # 7. 削除後にアクセスすると404
        res = client.get(f"/tasks/{task_id}")
        assert res.status_code == 404

    def test_複数タスクの作成と検索(self, client):
        # 複数タスクを作成
        titles = ["朝のジョギング", "報告書の作成", "朝食の準備"]
        for title in titles:
            res = client.post("/tasks", json={"title": title})
            assert res.status_code == 201

        # 一覧で全件取得
        res = client.get("/tasks")
        assert res.status_code == 200
        assert len(res.get_json()) == 3

        # 「朝」で検索すると2件ヒット
        res = client.get("/tasks/search?q=朝")
        assert res.status_code == 200
        results = res.get_json()
        assert len(results) == 2

    def test_タスク作成_即トグル_再トグル(self, client):
        # タスク作成
        res = client.post("/tasks", json={"title": "即完了タスク"})
        assert res.status_code == 201
        task_id = res.get_json()["id"]
        assert res.get_json()["done"] is False

        # 完了にトグル
        res = client.patch(f"/tasks/{task_id}/toggle")
        assert res.get_json()["done"] is True

        # 未完了に戻す
        res = client.patch(f"/tasks/{task_id}/toggle")
        assert res.get_json()["done"] is False

    def test_全タスク削除後に一覧が空(self, client):
        # 3件作成
        ids = []
        for i in range(3):
            res = client.post("/tasks", json={"title": f"タスク{i}"})
            ids.append(res.get_json()["id"])

        # 全件削除
        for task_id in ids:
            res = client.delete(f"/tasks/{task_id}")
            assert res.status_code == 200

        # 一覧が空であることを確認
        res = client.get("/tasks")
        assert res.status_code == 200
        assert res.get_json() == []
