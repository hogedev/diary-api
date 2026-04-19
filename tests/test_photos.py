"""写真テスト"""

import io


def _get_token(auth_header: dict[str, str]) -> str:
    return auth_header["Authorization"].replace("Bearer ", "")


def test_get_photo_image(client, auth_header, sample_image, mock_storage):
    create_resp = client.post(
        "/api/v1/entries/",
        data={"text": "写真テスト", "entry_date": "2026-04-19"},
        files=[("photos", ("test.jpg", io.BytesIO(sample_image), "image/jpeg"))],
        headers=auth_header,
    )
    photo_id = create_resp.json()["photos"][0]["id"]
    token = _get_token(auth_header)
    resp = client.get(f"/api/v1/photos/{photo_id}/image", params={"token": token})
    assert resp.status_code == 200
    assert "image" in resp.headers["content-type"]
    assert resp.headers["cache-control"] == "public, max-age=31536000, immutable"


def test_get_photo_thumb(client, auth_header, sample_image, mock_storage):
    create_resp = client.post(
        "/api/v1/entries/",
        data={"text": "サムネテスト", "entry_date": "2026-04-19"},
        files=[("photos", ("test.jpg", io.BytesIO(sample_image), "image/jpeg"))],
        headers=auth_header,
    )
    photo_id = create_resp.json()["photos"][0]["id"]
    token = _get_token(auth_header)
    resp = client.get(f"/api/v1/photos/{photo_id}/image", params={"token": token, "w": 400})
    assert resp.status_code == 200


def test_delete_photo(client, auth_header, sample_image, mock_storage):
    create_resp = client.post(
        "/api/v1/entries/",
        data={"text": "削除テスト", "entry_date": "2026-04-19"},
        files=[("photos", ("test.jpg", io.BytesIO(sample_image), "image/jpeg"))],
        headers=auth_header,
    )
    photo_id = create_resp.json()["photos"][0]["id"]
    resp = client.delete(f"/api/v1/photos/{photo_id}", headers=auth_header)
    assert resp.status_code == 204


def test_get_photo_not_found(client, auth_header):
    token = _get_token(auth_header)
    resp = client.get("/api/v1/photos/9999/image", params={"token": token})
    assert resp.status_code == 404
