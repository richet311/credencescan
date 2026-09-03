def test_login_success(client):
    response = client.post(
        "/api/auth/login", json={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_wrong_password(client):
    response = client.post(
        "/api/auth/login", json={"username": "testuser", "password": "wrong"}
    )
    assert response.status_code == 401


def test_history_requires_auth(client):
    response = client.get("/api/documents/history")
    assert response.status_code == 401


def test_history_with_valid_token(client):
    login_response = client.post(
        "/api/auth/login", json={"username": "testuser", "password": "testpass"}
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/api/documents/history", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "history" in response.json()
