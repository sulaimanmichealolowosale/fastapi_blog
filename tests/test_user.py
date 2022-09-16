from app import schemas
from .database import client, session


def test_root(client):
    res = client.get("/")
    print(res.json().get("message"))
    assert res.status_code == 200


def test_create_user(client):
    res = client.post(
        "/users/", json={"email": "just@just.com", "password": "sulaiman", "username": "just"})

    new_user = schemas.GetUser(**res.json())

    assert new_user.username == "just"
    assert res.status_code == 201
