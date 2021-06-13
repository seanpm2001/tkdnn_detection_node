from detector.tkdnn import Detector
import pytest
import os
import shutil
from detector.helper import data_dir


@pytest.fixture(scope='session')
def detector():
    yield Detector()


@pytest.fixture(autouse=True, scope='session')
def check_for_model_data():
    assert os.path.exists(
        '/data/model.rt'), "Error: Could not find model. You need to execute 'detection_node % ./download_model_for_testing.sh'"
