from sqlmodel import Session

from passlib.hash import pbkdf2_sha256
import fastapi
from fastapi.testclient import TestClient

from sqlmodel import select

from mocks import (
    create_user_data,
    create_db_and_tables,
    engine,
    UserCreate,
    UserPublic,
    User,
)

app = fastapi.FastAPI()


def hash_password(password: str) -> str:
    return pbkdf2_sha256.hash(password)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    return TestClient(app)


@app.post("/users/", response_model=UserPublic)
def create_user(user: UserCreate):
    hashed_password = hash_password(user.password)
    with Session(engine) as session:
        extra_data = {"hashed_password": hashed_password}
        db_user = User.model_validate(user, update=extra_data)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user


@app.get("/users/", response_model=list[UserPublic])
def list_users(
    offset: int = 0, limit: int = fastapi.Query(default=100, le=100)
) -> list[UserPublic]:
    with Session(engine) as session:
        users = session.exec(select(User).offset(offset).limit(limit)).all()
        return users


def generate_user_obj():
    user_data = create_user_data.copy()
    user_data["hashed_password"] = hash_password(user_data["password"])
    with Session(engine) as session:
        user = User(**user_data)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def test_create_user():
    test_client = on_startup()
    response = test_client.post("/users/", json=create_user_data)
    assert response.status_code == 200


def test_list_users():
    test_client = on_startup()
    generate_user_obj()
    response = test_client.get("/users/")

    assert response.status_code == 200
    assert len(response.json())

    generated_user_dict = response.json().pop()
    keys_that_are_consistent = [
        "name",
        "email",
        "username",
    ]

    for key in keys_that_are_consistent:
        assert key in generated_user_dict.keys()
        assert generated_user_dict[key] == create_user_data[key]


if __name__ == "__main__":
    test_create_user()
    test_list_users()
