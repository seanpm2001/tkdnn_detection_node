from detector.tkdnn import Detector
import pytest
import os


@pytest.fixture(scope='session')
def detector():
    assert os.path.exists(
        '/data/model.rt'), "Error: Could not find model. You need to execute 'detection_node % ./download_model_for_testing.sh'"
    yield Detector()
