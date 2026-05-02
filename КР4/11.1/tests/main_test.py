from fastapi.testclient import TestClient

from main import app, users

client = TestClient(app)


def setup_function():
    users.clear()


def test_create_user_success():
    response = client.post(
        "/users",
        json={
            "username": "ivan",
            "email": "ivan@example.com",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] == 1
    assert data["username"] == "ivan"
    assert data["email"] == "ivan@example.com"


def test_create_user_invalid_email():
    response = client.post(
        "/users",
        json={
            "username": "ivan",
            "email": "wrong-email",
        },
    )

    assert response.status_code == 422


def test_get_user_success():
    users[1] = {
        "id": 1,
        "username": "ivan",
        "email": "ivan@example.com",
    }

    response = client.get("/users/1")

    assert response.status_code == 200
    assert response.json() == users[1]


def test_get_user_not_found():
    response = client.get("/users/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_delete_user_success():
    users[1] = {
        "id": 1,
        "username": "ivan",
        "email": "ivan@example.com",
    }

    response = client.delete("/users/1")

    assert response.status_code == 200
    assert response.json()["message"] == "User deleted"
    assert 1 not in users


def test_delete_user_not_found():
    response = client.delete("/users/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"