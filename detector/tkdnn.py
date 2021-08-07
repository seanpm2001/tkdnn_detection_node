from learning_loop_node.detector.about import About
import cv2
from typing import List, Any
from typing import Union as UNION
from icecream import ic
from detection import Detection
from ctypes import *
import c_classes as c_classes
import logging
from helper import measure
import os

lib = CDLL("/usr/local/lib/libdarknetRT.so", RTLD_GLOBAL)


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

    def __init__(self, about: About):
        
        model_file = '/data/model/model.rt'
        try:
            self.net = load_network(model_file.encode("ascii"), len(about.categories), 1)
        except Exception:
            logging.exception(f'could not load {model_file}')
            raise

        logging.info(f'loaded {model_file}')

        self.image = make_image(about.resolution, about.resolution, 3)
        self.version = about.version

    def evaluate(self, image: Any) -> List[Detection]:
        resized = cv2.resize(image, (self.image.w, self.image.h), interpolation=cv2.INTER_LINEAR)
        resized_data = resized.ctypes.data_as(c_char_p)
        copy_image_from_bytes(self.image, resized_data)

        num = c_int(0)
        pnum = pointer(num)
        do_inference(self.net, self.image)
        threshold = 0.2  # TODO make this configurable thorugh REST call
        detections = get_network_boxes(self.net, threshold, pnum)
        detections = [detections[i] for i in range(pnum[0])]  # convert c to python

        (h, w, _) = image.shape
        w_ratio = w/self.image.w
        h_ratio = h/self.image.h

        detections = [Detection(
            d.name.decode("ascii"),
            int(d.bbox.x * w_ratio), int(d.bbox.y * h_ratio),
            int(d.bbox.w * w_ratio), int(d.bbox.h * h_ratio),
            self.version, round(d.prob, 2)
        ) for d in detections]

        return detections
