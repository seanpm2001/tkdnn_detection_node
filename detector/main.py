import uvicorn
from fastapi import APIRouter, Request, File, UploadFile, Header
from fastapi.encoders import jsonable_encoder
from learning_loop_node import DetectorNode
from typing import Optional, List, Any
import cv2
import numpy as np
from fastapi.responses import JSONResponse
from icecream import ic
from fastapi_utils.tasks import repeat_every
from detector.tkdnn import Detector
import detector.helper as helper
from detector.detection import Detection
from detector.active_learner import learner as l
from detector.active_learner import detection as d
import requests
import os
import PIL.Image
import asyncio
from detector.helper import measure

node = DetectorNode(uuid='12d7750b-4f0c-4d8d-86c6-c5ad04e19d57', name='detector node')
detector = Detector()
router = APIRouter()
learners = {}


@router.put("/reset")
def reset_test_learner(request: Request):
    global learners
    learners = {}


@router.post("/upload")
async def upload_image(request: Request, files: List[UploadFile] = File(...)):
    for file_data in files:
        await helper.write_file(file_data, file_data.filename)

    return 200, "OK"


@router.post("/detect")
async def compute_detections(request: Request, file: UploadFile = File(...), mac: str = Header(...), tags: Optional[str] = Header(None)):
    """
    Example Usage

        curl --request POST -H 'mac: FF:FF' -F 'file=@test.jpg' localhost:8004/detect

        for i in `seq 1 10`; do time curl --request POST -H 'mac: FF:FF' -F 'file=@test.jpg' localhost:8004/detect; done
    """

    measure(reset=True)

    try:
        np_image = np.fromfile(file.file, np.uint8)
    except:
        raise Exception(f'Uploaded file {file.filename} is no image file.')

    measure()
    image = cv2.imdecode(np_image, cv2.IMREAD_COLOR)
    measure()
    detections = detector.evaluate(image)
    measure()

    loop = asyncio.get_event_loop()
    loop.create_task(learn(detections, mac, tags, file, str(file.filename)))
    measure()

    return JSONResponse({'box_detections': jsonable_encoder(detections)})


async def learn(detections: List[Detection], mac: str, tags: Optional[str], image_data: Any, filename: str) -> None:
    active_learning_causes = check_detections_for_active_learning(detections, mac)

    if any(active_learning_causes):
        tags_list = [mac]
        if tags:
            tags_list += tags.split(',') if tags else []
        tags_list += active_learning_causes

        await helper.save_detections_and_image(helper.data_dir, detections, image_data, filename,
                                               tags_list)


def check_detections_for_active_learning(detections: List[Detection], mac: str) -> List[str]:
    global learners
    {learner.forget_old_detections() for (mac, learner) in learners.items()}
    if mac not in learners:
        learners[mac] = l.Learner()

    active_learning_causes = learners[mac].add_detections(detections)
    return active_learning_causes


# @node.on_event("startup")
# @repeat_every(seconds=30, raise_exceptions=False, wait_first=False)
# def handle_detections() -> None:
#     _handle_detections()


def _handle_detections() -> None:  # TODO move
    all_files = helper.get_data_files()
    image_files = [file for file in all_files if '.json' not in file]

    for file in image_files:
        file_name = os.path.splitext(file)[0]
        if not os.path.exists(f'{data_dir}/{file_name}.json.lock') or not os.path.exists(f'{data_dir}/{file}.lock'):
            data = [('file', open(f'{file_name}.json', 'r')),
                    ('file', open(file, 'rb'))]

            request = requests.post(f'{node.url}/api/{node.organization}/projects/{node.project}/images', files=data)
            if request.status_code == 200:
                os.remove(f'{file_name}.json')
                os.remove(file)


node.include_router(router, prefix="")

if __name__ == "__main__":
    uvicorn.run("main:node", host="0.0.0.0", port=80, lifespan='on', reload=True)
