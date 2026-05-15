from werkzeug.security import generate_password_hash

from app import populate_data
from extensions import db
from models import StateProvince, User, UserTracking


def test_authenticated_user_can_save_seen_plate(client, app):
    with app.app_context():
        populate_data()

        user = User(
            username="tracker",
            email="tracker@example.com",
            password=generate_password_hash("Password123!"),
            is_approved=True,
            is_admin=False,
        )
        db.session.add(user)
        db.session.commit()

        colorado = StateProvince.query.filter_by(name="Colorado", category="US").first()
        assert colorado is not None

        user_id = user.id
        colorado_id = colorado.id

    client.post(
        "/login",
        data={
            "username": "tracker",
            "password": "Password123!",
        },
        follow_redirects=True,
    )

    response = client.post(
        "/user",
        data={
            "us_states": [str(colorado_id)],
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():
        tracking = UserTracking.query.filter_by(
            user_id=user_id,
            state_province_id=colorado_id,
        ).first()

        assert tracking is not None