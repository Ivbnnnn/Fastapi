import pytest
from faker import Faker
from httpx import ASGITransport, AsyncClient

from main import app, db


fake = Faker()


@pytest.fixture(autouse=True)
def clear_db():
    db.clear()
    yield
    db.clear()


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest.fixture
def user_payload():
    return {
        "username": fake.user_name(),
        "age": fake.random_int(min=18, max=80),
    }


@pytest.mark.asyncio
async def test_create_user_success(client, user_payload):
    response = await client.post("/users", json=user_payload)

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert isinstance(data["id"], int)
    assert data["username"] == user_payload["username"]
    assert data["age"] == user_payload["age"]


@pytest.mark.asyncio
async def test_get_existing_user_success(client, user_payload):
    create_response = await client.post("/users", json=user_payload)
    user_id = create_response.json()["id"]

    response = await client.get(f"/users/{user_id}")

    assert response.status_code == 200
    assert response.json() == {
        "id": user_id,
        "username": user_payload["username"],
        "age": user_payload["age"],
    }


@pytest.mark.asyncio
async def test_get_not_existing_user(client):
    response = await client.get("/users/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


@pytest.mark.asyncio
async def test_delete_existing_user_success(client, user_payload):
    create_response = await client.post("/users", json=user_payload)
    user_id = create_response.json()["id"]

    response = await client.delete(f"/users/{user_id}")

    assert response.status_code == 204
    assert response.text == ""


@pytest.mark.asyncio
async def test_delete_same_user_twice(client, user_payload):
    create_response = await client.post("/users", json=user_payload)
    user_id = create_response.json()["id"]

    first_delete = await client.delete(f"/users/{user_id}")
    second_delete = await client.delete(f"/users/{user_id}")

    assert first_delete.status_code == 204
    assert second_delete.status_code == 404
    assert second_delete.json()["detail"] == "User not found"


@pytest.mark.asyncio
async def test_create_user_with_boundary_age(client):
    payload = {
        "username": fake.user_name(),
        "age": 18,
    }

    response = await client.post("/users", json=payload)

    assert response.status_code == 201
    assert response.json()["age"] == 18


@pytest.mark.asyncio
async def test_create_user_invalid_age_type(client):
    payload = {
        "username": fake.user_name(),
        "age": "not-int",
    }

    response = await client.post("/users", json=payload)

    assert response.status_code == 422