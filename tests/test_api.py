from app import create_app


def test_home_route():
    client = create_app().test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert response.is_json


def test_health_route():
    client = create_app().test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_recommend_route_success():
    client = create_app().test_client()
    response = client.get("/recommend?movie=Avatar")
    assert response.status_code == 200
    data = response.get_json()
    assert data["movie"] == "Avatar"
    assert isinstance(data["recommendations"], list)
    assert len(data["recommendations"]) > 0


def test_missing_movie_parameter():
    client = create_app().test_client()
    response = client.get("/recommend")
    assert response.status_code == 400
    assert "movie query parameter is required" in response.get_json()["error"]


def test_invalid_movie_name():
    client = create_app().test_client()
    response = client.get("/recommend?movie=NotAMovie")
    assert response.status_code == 404
    assert "Movie not found" in response.get_json()["error"]
