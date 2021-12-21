
from typing import Generator
import socketio
from outbox import Outbox
import pytest
import os
import asyncio
import logging
import shutil


@pytest.fixture()
def outbox():
    outbox = Outbox()
    shutil.rmtree(outbox.path, ignore_errors=True)
    os.mkdir(outbox.path)

    yield outbox
    shutil.rmtree(outbox.path, ignore_errors=True)


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
