from app import app


def test_homepage_loads():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"License Plate Game" in response.data


def test_login_page_loads():
    client = app.test_client()
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Login" in response.data


def test_signup_page_loads():
    client = app.test_client()
    response = client.get("/signup")
    assert response.status_code == 200
    assert b"Sign Up" in response.data