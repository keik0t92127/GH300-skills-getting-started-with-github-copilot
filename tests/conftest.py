import copy
import pytest

import src.app as app_module


@pytest.fixture(autouse=True)
def backup_activities():
    """Backup and restore the in-memory activities dict to isolate tests."""
    original = copy.deepcopy(app_module.activities)
    try:
        yield
    finally:
        app_module.activities.clear()
        app_module.activities.update(original)
