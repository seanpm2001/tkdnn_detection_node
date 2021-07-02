import shutil
from detector.tkdnn import Detector
from detector.outbox import Outbox
import pytest
import os


@pytest.fixture(scope='session')
def detector():
    assert os.path.exists(
        '/data/model.rt'), "Error: Could not find model. You need to execute 'detection_node % ./download_model_for_testing.sh'"
    yield Detector()


@pytest.fixture(scope='session')
def outbox():
    outbox = Outbox()
    for f in os.listdir(outbox.path):
        os.remove(os.path.join(outbox.path, f))
    yield outbox
