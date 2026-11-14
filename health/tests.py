from unittest.mock import patch

import pytest
from django.test import Client


@pytest.mark.django_db
def test_liveness_returns_200():
    client = Client()

    response = client.get("/health/live/")

    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


@pytest.mark.django_db
def test_readiness_returns_200_when_database_is_available():
    client = Client()

    response = client.get("/health/ready/")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "database": "connected",
    }


@pytest.mark.django_db
def test_readiness_returns_503_when_database_fails():
    client = Client()

    with patch(
        "health.views.connection.cursor", side_effect=Exception("Database unavailable")
    ):
        response = client.get("/health/ready/")

    assert response.status_code == 503
    assert response.json() == {
        "status": "not_ready",
        "database": "unavailable",
    }
