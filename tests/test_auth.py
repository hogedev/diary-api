"""認証テスト"""


def test_register(client):
    resp = client.post(
        "/api/v1/auth/register",
        json={"username": "newuser", "password": "newpass"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "newuser"
    assert data["token_type"] == "bearer"
    assert "access_token" in data


def test_register_duplicate(client):
    client.post(
        "/api/v1/auth/register",
        json={"username": "dupuser", "password": "pass1"},
    )
    resp = client.post(
        "/api/v1/auth/register",
        json={"username": "dupuser", "password": "pass2"},
    )
    assert resp.status_code == 409


def test_login(client):
    client.post(
        "/api/v1/auth/register",
        json={"username": "loginuser", "password": "loginpass"},
    )
    resp = client.post(
        "/api/v1/auth/login",
        json={"username": "loginuser", "password": "loginpass"},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client):
    client.post(
        "/api/v1/auth/register",
        json={"username": "wrongpw", "password": "correct"},
    )
    resp = client.post(
        "/api/v1/auth/login",
        json={"username": "wrongpw", "password": "wrong"},
    )
    assert resp.status_code == 401


def test_login_unknown_user(client):
    resp = client.post(
        "/api/v1/auth/login",
        json={"username": "nonexistent", "password": "any"},
    )
    assert resp.status_code == 401
