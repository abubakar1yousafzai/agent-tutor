import pytest
import pytest_asyncio


@pytest.mark.asyncio
async def test_create_user(test_client):
    resp = await test_client.post("/users", json={"email": "alice@test.com", "name": "Alice"})
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert data["email"] == "alice@test.com"
    assert data["tier"] == "free"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_user_upsert(test_client):
    payload = {"email": "bob@test.com", "name": "Bob"}
    resp1 = await test_client.post("/users", json=payload)
    resp2 = await test_client.post("/users", json=payload)
    assert resp1.status_code in (200, 201)
    assert resp2.status_code in (200, 201)
    assert resp1.json()["id"] == resp2.json()["id"]


@pytest.mark.asyncio
async def test_get_user(test_client):
    resp = await test_client.post("/users", json={"email": "carol@test.com", "name": "Carol"})
    user_id = resp.json()["id"]
    get_resp = await test_client.get(f"/users/{user_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == user_id


@pytest.mark.asyncio
async def test_get_user_not_found(test_client):
    resp = await test_client.get("/users/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404
