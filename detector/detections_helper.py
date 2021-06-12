import cv2
from typing import List, Any
from typing import Union as UNION
from icecream import ic
import helper
import os
import detection as d
import subprocess
from ctypes import *
import c_classes


lib = CDLL("/tkDNN/build/libdarknetRT.so", RTLD_GLOBAL)


load_network = lib.load_network
load_network.argtypes = [c_char_p, c_int, c_int]
load_network.restype = c_void_p

copy_image_from_bytes = lib.copy_image_from_bytes
copy_image_from_bytes.argtypes = [c_classes.IMAGE, c_char_p]

make_image = lib.make_image
make_image.argtypes = [c_int, c_int, c_int]
make_image.restype = c_classes.IMAGE

do_inference = lib.do_inference
do_inference.argtypes = [c_void_p, c_classes.IMAGE]

get_network_boxes = lib.get_network_boxes
get_network_boxes.argtypes = [c_void_p, c_float, POINTER(c_int)]
get_network_boxes.restype = POINTER(c_classes.DETECTION)


def class_count(names_txt: str) -> int:
    with open(names_txt, 'r') as f:
        names = f.read().rstrip('\n').split('\n')
    return len(names)


def create_darknet_image(image: Any) -> None:
    try:
        height, width, channels = image.shape
        darknet_image = make_image(width, height, channels)
        frame_data = image.ctypes.data_as(c_char_p)
        copy_image_from_bytes(darknet_image, frame_data)
    except Exception as e:
        print(e)

    return darknet_image


def get_detections(image: Any, net: bytes) -> List[d.Detection]:
    darknet_image = create_darknet_image(image)
    model_id = 'unknown model'  # TODO see https://trello.com/c/C2HJ0g01/174-tensorrt-file-f%C3%BCr-tkdnn-detector-deployen
    detections = detect_image(net, darknet_image, model_id)
    parsed_detections = parse_detections(detections)
    return parsed_detections


def detect_image(net, darknet_image, net_id, thresh=.2):
    num = c_int(0)

    pnum = pointer(num)
    do_inference(net, darknet_image)
    dets = get_network_boxes(net, thresh, pnum)
    detections = []
    for i in range(pnum[0]):
        bbox = dets[i].bbox
        detections.append((dets[i].name.decode("ascii"), dets[i].prob, bbox.x, bbox.y, bbox.w, bbox.h, net_id))

    return detections


def parse_detections(detections: List[UNION[int, str]]) -> List[d.Detection]:
    parsed_detections = []
    for detection in detections:
        category_name = detection[0]
        confidence = round(detection[1], 3) * 100
        left = int(detection[2])
        top = int(detection[3])
        width = int(detection[4])
        height = int(detection[5])
        net_id = detection[6]
        detection = d.Detection(category_name, left, top, width, height, net_id, confidence)
        parsed_detections.append(detection)

    return parsed_detections
