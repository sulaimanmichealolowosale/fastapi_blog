from fastapi.testclient import TestClient
from app.database import get_db, Base
from app.main import app
from app.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest


# SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:sulaiman@localhost:5432/test_fastblog'
SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test'


engine = create_engine(SQLALCHEMY_DATABASE_URL)
testingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = testingSessionLocal()
    try:
        yield db
    finally:
        db.close()



@pytest.fixture
def client(session):
    def override_get_db():
        
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

