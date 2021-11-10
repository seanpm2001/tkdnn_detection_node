import uvicorn
from fastapi import APIRouter, Request, File, UploadFile, Header
from fastapi.encoders import jsonable_encoder
from typing import Optional, List, Any
import cv2
import numpy as np
from fastapi.responses import JSONResponse
from icecream import ic
from fastapi_utils.tasks import repeat_every
from fastapi_socketio import SocketManager
import data  # import before DetectorNode
from tkdnn import Tkdnn
from outbox import Outbox
from detections import Detections
from active_learner import learner as l
from learning_loop_node import DetectorNode
import helper
import asyncio
from datetime import datetime
from threading import Thread
import logging
import icecream
icecream.install()

logging.getLogger().setLevel(logging.INFO)

about = data.ensure_model()
node = DetectorNode(uuid='12d7750b-4f0c-4d8d-86c6-c5ad04e19d57', name='detector node')
sio = SocketManager(app=node)
outbox = Outbox()
router = APIRouter()
learners = {}


@router.put("/reset")
def reset_test_learner(request: Request):
    global learners
    learners = {}


@router.post("/upload")
async def upload_image(files: List[UploadFile] = File(...)):
    loop = asyncio.get_event_loop()
    for file_data in files:
        await loop.run_in_executor(None, lambda: outbox.save(file_data, [], ['picked_by_system']))

    return 200, "OK"

@node.sio.event
async def info(sid):
    return jsonable_encoder(about.dict())

@node.sio.event
async def upload(sid, data):
    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(None, lambda: outbox.save(data['image'], Detections(), ['picked_by_system']))
    except Exception as e:
        logging.exception('could not upload via socketio')
        return {'error': str(e)}


@node.sio.event
async def detect(sid, data):
    try:
        np_image = np.frombuffer(data['image'], np.uint8)
        return await get_detections(np_image, data.get('mac', None), data.get('tags', []), data.get('active_learning', True))
    except Exception as e:
        logging.exception('could not detect via socketio')
        with open('/tmp/bad_img_from_socket_io.jpg', 'wb') as f:
            f.write(data['image'])
        return {'error': str(e)}


@router.post("/detect")
async def http_detect(request: Request, file: UploadFile = File(...), mac: str = Header(...), tags: Optional[str] = Header(None)):
    """
    Example Usage

        curl --request POST -H 'mac: FF:FF' -F 'file=@test.jpg' localhost:8004/detect

        for i in `seq 1 10`; do time curl --request POST -H 'mac: FF:FF' -F 'file=@test.jpg' localhost:8004/detect; done
    """
    try:
        np_image = np.fromfile(file.file, np.uint8)
    except:
        raise Exception(f'Uploaded file {file.filename} is no image file.')

    return JSONResponse(await get_detections(np_image, mac, tags.split(',') if tags else []))


async def get_detections(np_image, mac: str, tags: str, active_learning=True):
    loop = asyncio.get_event_loop()
    image = await loop.run_in_executor(None, lambda: cv2.imdecode(np_image, cv2.IMREAD_COLOR))
    detections = await loop.run_in_executor(None, lambda: tkdnn.evaluate(image))
    info = "\n    ".join([str(d) for d in detections.box_detections])
    logging.debug('detected:\n    ' + info)
    if active_learning:
        thread = Thread(target=learn, args=(detections, mac, tags, image))
        thread.start()
    return jsonable_encoder(detections)


def learn(detections: Detections, mac: str, tags: Optional[str], cv_image) -> None:
    active_learning_causes = check_detections_for_active_learning(detections, mac)

    if any(active_learning_causes):
        tags.append(mac)
        tags.append(*active_learning_causes)

        outbox.save(cv_image, detections, tags)


def check_detections_for_active_learning(detections: Detections, mac: str) -> List[str]:
    global learners
    {learner.forget_old_detections() for (mac, learner) in learners.items()}
    if mac not in learners:
        learners[mac] = l.Learner()

    active_learning_causes = learners[mac].add_detections(detections)
    return active_learning_causes


@node.on_event("startup")
def load_model():
    global tkdnn
    tkdnn = Tkdnn(about)


@node.on_event("startup")
@repeat_every(seconds=30, raise_exceptions=False, wait_first=False)
def submit() -> None:
    thread = Thread(target=outbox.upload)
    thread.start()


sids = []


@node.sio.event
def connect(sid, environ, auth):
    global sids
    sids.append(sid)


@node.on_event("shutdown")
async def shutdown():
    for sid in sids:
        await node.sio.disconnect(sid)

node.include_router(router, prefix="")

if __name__ == "__main__":
    uvicorn.run("main:node", host="0.0.0.0", port=80, lifespan='on', reload=True)
