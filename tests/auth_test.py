import pytest

from fastapi_common.auth import MockBearer
from fastapi_common.auth.models.standard_claims import StandardClaims


# todo: test auth package
def test_placeholder():
    assert True


# Test the fake user injection
def test_mock_user_call():
    bearer = MockBearer()
    user = bearer._mock_get_user_info()
    assert isinstance(user, StandardClaims)
    assert user.email == "fake@example.com"
