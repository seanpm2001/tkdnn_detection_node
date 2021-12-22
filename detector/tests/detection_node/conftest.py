
from typing import Generator
import socketio
from outbox import Outbox
import pytest
import os
import asyncio
import logging
import shutil
from learning_loop_node.globals import GLOBALS
from learning_loop_node import gdrive_downloader
from tkdnn_detector import TkdnnDetector
import zipfile


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


def download_model() -> str:
    file_id = '1jNgQDqQeaZhIWFCxV1eKeuLzXHYhXAQv'
    zip_file_path = '/tmp/model.zip'
    try:
        os.remove(zip_file_path)
    except:
        pass
    gdrive_downloader.download(file_id, zip_file_path)
    # unzip and place downloaded model
    tmp_path = f'/tmp/model_folder'
    shutil.rmtree(tmp_path, ignore_errors=True)

    with zipfile.ZipFile(file=zip_file_path, mode='r') as zip:
        zip.extractall(tmp_path)

    return tmp_path


@pytest.fixture(scope='session')
def configured_detector(data_folder):
    model_folder = download_model()
    os.symlink(model_folder, f'{GLOBALS.data_folder}/model')
    detector = TkdnnDetector(model_format='tensorrt')
    detector.load_model()
    yield detector


@pytest.fixture(autouse=True, scope='session')
def data_folder():
    GLOBALS.data_folder = '/tmp/learning_loop_lib_data'
    shutil.rmtree(GLOBALS.data_folder, ignore_errors=True)
    os.makedirs(GLOBALS.data_folder)
    yield
    shutil.rmtree(GLOBALS.data_folder, ignore_errors=True)
