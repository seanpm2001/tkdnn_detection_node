import cv2
from typing import List, Any
from typing import Union as UNION
from icecream import ic
from detector.detection import Detection
from ctypes import *
import detector.c_classes as c_classes
import logging


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


class Detector():

    def __init__(self):

        with open('/data/names.txt', 'r') as f:
            self.classes = f.read().rstrip('\n').split('\n')

        try:
            self.net = load_network('/data/model.rt'.encode("ascii"), len(self.classes), 1)
        except Exception:
            logging.exception(f'could not load model')
            raise

        with open('/data/training.cfg', 'r') as f:
            for l in f.readlines():
                if l.startswith('width='):
                    width = int(l.split('=')[1])
                if l.startswith('height='):
                    height = int(l.split('=')[1])

            self.image = make_image(width, height, 3)

        self.model_id = 'unknown model'  # TODO see https://trello.com/c/C2HJ0g01/174-tensorrt-file-f%C3%BCr-tkdnn-detector-deployen

    def evaluate(self, image: Any) -> List[Detection]:
        resized = cv2.resize(image, (self.image.w, self.image.h), interpolation=cv2.INTER_LINEAR)
        frame_data = resized.ctypes.data_as(c_char_p)
        copy_image_from_bytes(self.image, frame_data)

        num = c_int(0)
        pnum = pointer(num)
        do_inference(self.net, self.image)
        theshold = 0.2  # TODO make this configurable thorugh REST call
        dets = get_network_boxes(self.net, theshold, pnum)
        detections = []
        for i in range(pnum[0]):
            bbox = dets[i].bbox
            detections.append((dets[i].name.decode("ascii"), dets[i].prob,
                              bbox.x, bbox.y, bbox.w, bbox.h))

        parsed_detections = []

        (w, h, _) = image.shape
        w_ratio = w/self.image.w
        h_ratio = h/self.image.h
        for detection in detections:
            category_name = detection[0]
            confidence = round(detection[1], 3) * 100
            left = int(detection[2] * w_ratio)
            top = int(detection[3] * h_ratio)
            width = int(detection[4] * w_ratio)
            height = int(detection[5] * h_ratio)
            detection = Detection(category_name, left, top, width, height, self.model_id, confidence)
            parsed_detections.append(detection)

        return parsed_detections
