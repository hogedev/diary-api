"""エントリCRUDテスト"""

import io


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_create_entry_text_only(client, auth_header):
    resp = client.post(
        "/api/v1/entries/",
        data={"text": "苗を植えた", "entry_date": "2026-04-19"},
        headers=auth_header,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["text"] == "苗を植えた"
    assert data["entry_date"] == "2026-04-19"
    assert data["photos"] == []


def test_create_entry_with_photo(client, auth_header, sample_image):
    resp = client.post(
        "/api/v1/entries/",
        data={"text": "収穫", "entry_date": "2026-04-19"},
        files=[("photos", ("test.jpg", io.BytesIO(sample_image), "image/jpeg"))],
        headers=auth_header,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert len(data["photos"]) == 1
    assert data["photos"][0]["original_filename"] == "test.jpg"
    assert data["photos"][0]["width"] == 100
    assert data["photos"][0]["height"] == 100


def test_create_entry_requires_auth(client):
    resp = client.post(
        "/api/v1/entries/",
        data={"text": "認証なし", "entry_date": "2026-04-19"},
    )
    assert resp.status_code in (401, 403)


def test_list_entries(client, auth_header):
    client.post(
        "/api/v1/entries/",
        data={"text": "day1", "entry_date": "2026-04-18"},
        headers=auth_header,
    )
    client.post(
        "/api/v1/entries/",
        data={"text": "day2", "entry_date": "2026-04-19"},
        headers=auth_header,
    )
    resp = client.get("/api/v1/entries/", headers=auth_header)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2
    assert data["items"][0]["entry_date"] == "2026-04-19"


def test_list_entries_date_filter(client, auth_header):
    client.post(
        "/api/v1/entries/",
        data={"text": "day1", "entry_date": "2026-04-18"},
        headers=auth_header,
    )
    client.post(
        "/api/v1/entries/",
        data={"text": "day2", "entry_date": "2026-04-19"},
        headers=auth_header,
    )
    resp = client.get("/api/v1/entries/", params={"date_from": "2026-04-19"}, headers=auth_header)
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["text"] == "day2"


def test_get_entry(client, auth_header):
    create_resp = client.post(
        "/api/v1/entries/",
        data={"text": "テスト", "entry_date": "2026-04-19"},
        headers=auth_header,
    )
    entry_id = create_resp.json()["id"]
    resp = client.get(f"/api/v1/entries/{entry_id}", headers=auth_header)
    assert resp.status_code == 200
    assert resp.json()["text"] == "テスト"


def test_get_entry_not_found(client, auth_header):
    resp = client.get("/api/v1/entries/9999", headers=auth_header)
    assert resp.status_code == 404


def test_update_entry(client, auth_header):
    create_resp = client.post(
        "/api/v1/entries/",
        data={"text": "元のテキスト", "entry_date": "2026-04-19"},
        headers=auth_header,
    )
    entry_id = create_resp.json()["id"]
    resp = client.put(
        f"/api/v1/entries/{entry_id}",
        json={"text": "更新後のテキスト"},
        headers=auth_header,
    )
    assert resp.status_code == 200
    assert resp.json()["text"] == "更新後のテキスト"


def test_delete_entry(client, auth_header):
    create_resp = client.post(
        "/api/v1/entries/",
        data={"text": "削除対象", "entry_date": "2026-04-19"},
        headers=auth_header,
    )
    entry_id = create_resp.json()["id"]
    resp = client.delete(f"/api/v1/entries/{entry_id}", headers=auth_header)
    assert resp.status_code == 204

    resp = client.get(f"/api/v1/entries/{entry_id}", headers=auth_header)
    assert resp.status_code == 404


def test_list_dates(client, auth_header):
    client.post(
        "/api/v1/entries/",
        data={"text": "a", "entry_date": "2026-04-18"},
        headers=auth_header,
    )
    client.post(
        "/api/v1/entries/",
        data={"text": "b", "entry_date": "2026-04-19"},
        headers=auth_header,
    )
    client.post(
        "/api/v1/entries/",
        data={"text": "c", "entry_date": "2026-04-19"},
        headers=auth_header,
    )
    resp = client.get("/api/v1/entries/dates", headers=auth_header)
    assert resp.status_code == 200
    dates = resp.json()
    assert len(dates) == 2


def test_add_photos_to_entry(client, auth_header, sample_image):
    create_resp = client.post(
        "/api/v1/entries/",
        data={"text": "写真追加テスト", "entry_date": "2026-04-19"},
        headers=auth_header,
    )
    entry_id = create_resp.json()["id"]
    resp = client.post(
        f"/api/v1/entries/{entry_id}/photos",
        files=[("photos", ("photo1.jpg", io.BytesIO(sample_image), "image/jpeg"))],
        headers=auth_header,
    )
    assert resp.status_code == 201
    assert len(resp.json()["photos"]) == 1


def test_user_isolation(client, auth_header):
    """別ユーザーのエントリにアクセスできないことを確認"""
    create_resp = client.post(
        "/api/v1/entries/",
        data={"text": "user1のエントリ", "entry_date": "2026-04-19"},
        headers=auth_header,
    )
    entry_id = create_resp.json()["id"]

    # 別ユーザーを作成
    resp2 = client.post(
        "/api/v1/auth/register",
        json={"username": "otheruser", "password": "otherpass"},
    )
    other_header = {"Authorization": f"Bearer {resp2.json()['access_token']}"}

    # 別ユーザーからは見えない
    resp = client.get(f"/api/v1/entries/{entry_id}", headers=other_header)
    assert resp.status_code == 404

    resp = client.get("/api/v1/entries/", headers=other_header)
    assert resp.json()["total"] == 0
