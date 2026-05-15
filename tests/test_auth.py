from models import User


def test_signup_creates_unapproved_user(client, app):
    response = client.post(
        "/signup",
        data={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "StrongPassword123!",
            "confirm_password": "StrongPassword123!",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():
        user = User.query.filter_by(username="testuser").first()
        assert user is not None
        assert user.email == "testuser@example.com"
        assert user.is_approved is False
        assert user.is_admin is False
        assert user.password != "StrongPassword123!"