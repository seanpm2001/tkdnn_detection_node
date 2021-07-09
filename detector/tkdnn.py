import cv2
from typing import List, Any
from typing import Union as UNION
from icecream import ic
from detector.detection import Detection
from ctypes import *
import detector.c_classes as c_classes
import logging
from detector.helper import measure


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
            self.model_id, round(d.prob, 2)
        ) for d in detections]

        return detections