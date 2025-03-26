import pytest
from app import create_app
from app.extensions import mongo


@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "MONGO_URI": "mongodb://localhost:27017/test_db"
    })

    with app.app_context():
        yield app
        mongo.db.client.drop_database("test_db")


@pytest.fixture
def client(app):
    return app.test_client()


def test_create_session(client):
    """
    Test session creation route.
    """
    # response = client.post("/session/create", json={"user_id": 1})
    response = client.post("/session/create")
    assert response.status_code == 201
    assert "session_id" in response.json

    session_id = response.json['session_id']

    # Verify data was inserted into the test database
    session = mongo.db.session.find_one(
        {"session_id": session_id})
    assert session is not None
    assert "session_id" in session


def test_handle_join_session(client):
    """
    """
    response = client.post("/session/create")
    assert response.status_code == 201
    assert "session_id" in response.json

    session_id = response.json['session_id']

    request_json = {'countryName': 'United States'}
    response = client.post(f"/session/join/{session_id}", json=request_json)
    assert response.status_code == 201
    assert "session_id" in response.json
    assert "player" in response.json

    response = client.get(f"/session/{session_id}")

    assert response.status_code == 200
    assert "session_id" in response.json
    assert len(response.json['session']['players']) == 1
