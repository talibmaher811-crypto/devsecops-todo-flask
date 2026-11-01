"""Shared pytest fixtures."""

import pytest

from app import app, todos


@pytest.fixture()
def client():
    """Provide an isolated Flask test client."""
    todos.clear()
    with app.test_client() as test_client:
        yield test_client
    todos.clear()
