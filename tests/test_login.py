from werkzeug.security import generate_password_hash

from extensions import db
from models import User


def test_login_success(client, app):
    with app.app_context():
        user = User(
            username="loginuser",
            email="login@example.com",
            password=generate_password_hash("Password123!"),
            is_approved=True,
            is_admin=False,
        )

        db.session.add(user)
        db.session.commit()

    response = client.post(
        "/login",
        data={
            "username": "loginuser",
            "password": "Password123!",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    # Adjust this assertion if your post-login page differs
    assert b"Logout" in response.data or b"Leaderboard" in response.data