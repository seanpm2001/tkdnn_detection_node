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
import shutil
import threading


class Outbox():

    def __init__(self) -> None:
        self.path = '/data/outbox'
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        base = os.environ.get('SERVER_BASE_URL')
        o = os.environ.get('ORGANIZATION')
        p = os.environ.get('PROJECT')
        self.target_uri = f'{base}/api/{o}/projects/{p}/images'
        self.upload_in_progress = False

    def save(self, cv_image, detections: List[Detection], tags: List[str]) -> None:
        id = datetime.now().isoformat(sep='_', timespec='milliseconds')
        tmp = f'../tmp/{id}'
        os.makedirs(tmp, exist_ok=True)
        with open(tmp + '/image.json', 'w') as f:
            json.dump({
                'box_detections': jsonable_encoder(detections),
                'tags': tags,
                'date': id,
            }, f)
        cv2.imwrite(tmp + '/image.jpg', cv_image)
        os.rename(tmp, self.path + '/' + id)  # NOTE rename is atomic so upload can run in parallel

    def get_data_files(self):
        return glob(f'{self.path}/*')

    def upload(self) -> None:
        if self.upload_in_progress:
            return
        self.upload_in_progress = True

        try:
            for item in self.get_data_files():
                data = [('file', open(f'{item}/image.json', 'r')),
                        ('file', open(f'{item}/image.jpg', 'rb'))]

                response = requests.post(self.target_uri, files=data)
                if response.status_code == 200:
                    shutil.rmtree(item)
                    logging.info(f'uploaded {item} successfully')
                else:
                    logging.error(f'Could not upload {item}: {response.status_code}, {response.content}')
        except:
            logging.exception('could not upload files')
        self.upload_in_progress = False
