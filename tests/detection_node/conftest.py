from logging import Logger
from typing import Generator

import socketio
from detector.tkdnn import Detector
from detector.outbox import Outbox
import pytest
import os
import asyncio
import logging
import shutil


@pytest.fixture(scope='session')
def detector():
    assert os.path.exists(
        '/data/model.rt'), "Error: Could not find model. You need to execute 'detection_node % ./download_model_for_testing.sh'"
    yield Detector()


@pytest.fixture(scope='session')
def outbox():
    outbox = Outbox()
    shutil.rmtree(outbox.path)
    os.mkdir(outbox.path)
    yield outbox


@pytest.fixture()
async def sio() -> Generator:

    sio = socketio.AsyncClient()
    try_connect = True
    while try_connect:
        try:
            await sio.connect("ws://localhost", socketio_path="/ws/socket.io")
            try_connect = False
        except:
            logging.warning('trying again')
            await asyncio.sleep(1)

    assert sio.transport() == 'websocket'
    yield sio
    await sio.disconnect()
