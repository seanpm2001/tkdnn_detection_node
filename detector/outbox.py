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


class Outbox():

    def __init__(self) -> None:
        self.path = '/data/outbox'
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        base = os.environ.get('SERVER_BASE_URL')
        o = os.environ.get('ORGANIZATION')
        p = os.environ.get('PROJECT')
        self.target_uri = f'{base}/api/{o}/projects/{p}/images'

    async def save_detections_and_image(self, detections: List[Detection], image_data: UploadFile, file_name: str, tags: List[str]) -> None:
        os.makedirs(self.path, exist_ok=True)
        file_name_without_type = file_name.rsplit('.', 1)[0]
        json_file_name = f'{file_name_without_type}.json'
        await self._write_json(json_file_name, detections, tags)
        await self.write_file(image_data, file_name)

    async def _write_json(self, json_file_name: str, detections: List[Detection], tags: List[str]) -> None:
        date = datetime.utcnow().isoformat(sep='_', timespec='milliseconds')
        json_data = json.dumps({'box_detections': jsonable_encoder(detections),
                                'tags': tags,
                                'date': date})
        with FileLock(lock_file=f'{self.path}/{json_file_name}'):
            async with aiofiles.open(f'{self.path}/{json_file_name}', 'w') as out_file:
                await out_file.write(json_data)

    async def write_file(self, file_data: Any, file_name: str):
        # Be sure to start from beginning.
        await file_data.seek(0)
        with FileLock(lock_file=f'{self.path}/{file_name}.lock'):
            async with aiofiles.open(f'{self.path}/{file_name}', 'wb') as out_file:
                while True:
                    content = await file_data.read(1024)  # async read chunk
                    if not content:
                        break
                    await out_file.write(content)  # async write chunk

        os.remove(f'{self.path}/{file_name}.lock')

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
