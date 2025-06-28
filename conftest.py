import os

import pytest

from config.constants import BASE_DATA_DIR


@pytest.fixture
def data_direcries_and_children():
    required_dirs = [
        BASE_DATA_DIR,
        os.path.join(BASE_DATA_DIR, "raw"),
        os.path.join(BASE_DATA_DIR, "flattened"),
        os.path.join(BASE_DATA_DIR, "errors")
    ]

