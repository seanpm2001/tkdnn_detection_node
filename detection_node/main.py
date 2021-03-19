import sys
import asyncio
import threading
from fastapi import APIRouter, FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse
from threading import Thread
from fastapi_utils.tasks import repeat_every
import simplejson as json
import requests
import io
from learning_loop_node.node import Node, State
from typing import List
import cv2
from glob import glob
import inferences_helper
import PIL.Image
import numpy as np
from fastapi.responses import JSONResponse

hostname = 'backend'
node = Node(hostname, uuid='12d7750b-4f0c-4d8d-86c6-c5ad04e19d57', name='detection node')
node.path = '/data/yolo4_tiny_3lspp_12_76844'
node.net = inferences_helper.load_network(
    f'{node.path}/training.cfg', f'{node.path}/training_final.weights')


@node.get_model_files
def get_model_files(ogranization: str, project: str, model_id: str) -> List[str]:
    return _get_model_files


def _get_model_files() -> List[str]:
    files = glob('/data/**/*')
    return files


router = APIRouter()


@router.post("/images/")
async def compute_detections(request: Request, file: UploadFile = File(...)):
    try:
        image = PIL.Image.open(file.file)
    except:
        raise Exception(f'Uploaded file {file.filename} is no image file.')

    image = np.asarray(image)
    image = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB)
    net_input_image_width, net_input_image_height = inferences_helper._get_network_input_image_size(node.path)
    outs = inferences_helper.get_inferences(node.net, image, net_input_image_width, net_input_image_height)
    net_id = inferences_helper._get_model_id(node.path)
    inferences = inferences_helper.parse_inferences(
        outs, node.net, image.shape[0], image.shape[1], net_id)

    return JSONResponse({'box_detections': inferences})

# setting up backdoor_controls
node.include_router(router, prefix="")
