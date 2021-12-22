import json
import asyncio
from outbox import Outbox
import requests
import json
import pytest
from icecream import ic

base_path = '/data'
image_name = 'test.jpg'
json_name = 'test.json'
image_path = f'{base_path}/{image_name}'
json_path = f'/tmp/{json_name}'


@pytest.mark.skip(reason='we need to figure out how to ensure the expected test model is loaded')
@pytest.mark.asyncio()
async def test_save_image_and_detections_if_mac_was_sent(outbox: Outbox):
    assert requests.put('http://localhost/reset').status_code == 200

    data = {('file', open('tests/test.jpg', 'rb'))}
    headers = {'mac': '0:0:0:0', 'tags':  'some_tag'}
    request = requests.post('http://localhost/detect', files=data, headers=headers)
    assert request.status_code == 200
    detections = request.json()['box_detections']

    # Wait for async file saving
    assert len(detections) > 0
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
