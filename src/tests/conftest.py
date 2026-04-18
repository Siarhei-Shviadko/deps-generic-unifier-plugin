from uuid import uuid4

import pytest
from deps_lil_chyn.infrastructure.access_management import user
from deps_unified_data import UnifiedDataFactory

from deps_generic_unifier_plugin.plugin import UnifierPlugin


@pytest.fixture
def test_user_deps_token():
    return {
        "subject": "some_user_id",
        "organisation": "deps-users",
        "roles": [],
        "groups": ["deps-users"],
        "deps_token": "token",
    }


@pytest.fixture(autouse=True)
def set_test_user_deps_token(test_user_deps_token):
    user.set(test_user_deps_token)


@pytest.fixture
def test_unified_data():
    document_id = uuid4().hex
    return UnifiedDataFactory.make_unified_data(document_id)


@pytest.fixture
def unifier_plugin():
    return UnifierPlugin()
