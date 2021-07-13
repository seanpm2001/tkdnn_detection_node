import os
from glob import glob
from fastapi.encoders import jsonable_encoder
import aiofiles
import os
from filelock import FileLock
from icecream import ic
from fastapi.datastructures import UploadFile
from detector.detection import Detection
from typing import List, Any
import json
from datetime import datetime
import requests
import logging
import cv2


class Outbox():

    def __init__(self) -> None:
        self.path = '/data/outbox'
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        base = os.environ.get('SERVER_BASE_URL')
        o = os.environ.get('ORGANIZATION')
        p = os.environ.get('PROJECT')
        self.target_uri = f'{base}/api/{o}/projects/{p}/images'

    def save(self, cv_image, detections: List[Detection], tags: List[str]) -> None:
        location = self.path + '/' + datetime.now().isoformat(sep='_', timespec='milliseconds') + '/'
        os.makedirs(location, exist_ok=True)
        with open(location + 'metadata.json', 'w') as f:
            json.dump({
                'box_detections': jsonable_encoder(detections),
                'tags': tags,
                'date': datetime.now().isoformat(sep='_', timespec='milliseconds')
            }, f)
        cv2.imwrite(location + 'image.jpg', cv_image)

    def get_data_files(self):
        return glob(f'{self.path}/*[!.lock]', recursive=True)

    def submit(self) -> None:
        all_files = self.get_data_files()
        image_files = [file for file in all_files if '.json' not in file]
        for file in image_files:
            file_name = os.path.splitext(file)[0]
            if not os.path.exists(f'{file_name}.json.lock') or not os.path.exists(f'{file}.lock'):
                data = [('file', open(f'{file_name}.json', 'r')),
                        ('file', open(file, 'rb'))]

                response = requests.post(self.target_uri, files=data)
                if response.status_code == 200:
                    os.remove(f'{file_name}.json')
                    os.remove(file)
                    logging.info(f'submitted {file} successfully')
                else:
                    logging.error(f'Could not submit {file}: {response.status_code}, {response.content}')
