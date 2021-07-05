import json
from glob import glob

import socketio
import detector.helper as helper
import asyncio
from detector.active_learner.learner import Learner
from detector.outbox import Outbox
from pydantic.types import Json
import requests
import json
import pytest


base_path = '/data'
image_name = 'test.jpg'
json_name = 'test.json'
image_path = f'{base_path}/{image_name}'
json_path = f'/tmp/{json_name}'


@pytest.mark.asyncio()
async def test_save_image_and_detections_if_mac_was_sent(outbox: Outbox):
    assert requests.put('http://localhost/reset').status_code == 200

    data = {('file', open('/data/test.jpg', 'rb'))}
    headers = {'mac': '0:0:0:0', 'tags':  'some_tag'}
    request = requests.post('http://localhost/detect', files=data, headers=headers)
    assert request.status_code == 200
    detections = request.json()['box_detections']

    expected_detection = {'category_name': 'marker_hinten_rechts',
                          'model_name': 'unknown model',
                          'confidence': 1.0,
                          'height': 37,
                          'width': 38,
                          'x': 724,
                          'y': 526}
    assert len(detections) == 13
    assert detections[0] == expected_detection

    # Wait for async file saving
    for retries in range(20):
        saved_files = outbox.get_data_files()
        if len(saved_files) < 2:
            await asyncio.sleep(.2)
        else:
            break

    assert len(saved_files) == 2

    json_filename = [file for file in saved_files if file.endswith('.json')][0]
    with open(json_filename, 'r') as f:
        json_content = json.load(f)

    box_detections = json_content['box_detections']
    assert len(box_detections) == 13
    assert box_detections[0] == expected_detection

    tags = json_content['tags']
    assert len(tags) == 3
    assert tags == ['0:0:0:0', 'some_tag', 'lowConfidence']


@pytest.mark.asyncio()
async def test_detect_via_socketio(sio: socketio.Client):
    with open('/data/test.jpg', 'rb') as f:
        image_bytes = f.read()

    result = await sio.call('detect', image_bytes)
    assert result == 'test'
