import os

# These must be set BEFORE importing app.
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["MAIL_USERNAME"] = "test@example.com"
os.environ["MAIL_PASSWORD"] = "test-password"
os.environ["MAIL_DEFAULT_SENDER"] = "test@example.com"

import pytest

from app import app as flask_app
from extensions import db


@pytest.fixture
def app():
    flask_app.config["TESTING"] = True

    db_uri = flask_app.config["SQLALCHEMY_DATABASE_URI"]
    if db_uri != "sqlite:///:memory:":
        raise RuntimeError(f"Refusing to run tests against non-test database: {db_uri}")

    with flask_app.app_context():
        db.create_all()

        yield flask_app

        db.session.remove()
        db.drop_all()