from typing import Any, Union
from learning_loop_node.detector.detector import Detector
from learning_loop_node.model_information import ModelInformation
from learning_loop_node.data_classes.category import CategoryType
import cv2
from icecream import ic
from learning_loop_node.detector.detections import Detections
from learning_loop_node.detector.box_detection import BoxDetection
from learning_loop_node.detector.point_detection import PointDetection
from ctypes import *
import c_classes as c_classes
import logging
from helper import measure
import numpy as np

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


class TkdnnDetector(Detector):
    image: Any
    category_types: Any
    net: Any
    version: Any

    def __init__(self, model_format: str) -> None:
        super().__init__(model_format)

    def init(self,  model_info: ModelInformation, model_root_path: str):
        model_file = f'{model_root_path}/model.rt'
        try:
            self.net = load_network(model_file.encode(
                "ascii"), len(model_info.categories), 1)
        except Exception:
            logging.exception(f'could not load {model_file}')
            raise

        self.image = make_image(model_info.resolution,
                                model_info.resolution, 3)
        self.version = model_info.version
        self.category_types = {c.name: c.type for c in model_info.categories}

    def evaluate(self, image: Any) -> Detections:
        detections = Detections()
        try:
            resized = cv2.resize(
                image, (self.image.w, self.image.h), interpolation=cv2.INTER_LINEAR)
            resized_data = resized.ctypes.data_as(c_char_p)
            copy_image_from_bytes(self.image, resized_data)
            num = c_int(0)
            pnum = pointer(num)
            do_inference(self.net, self.image)
            threshold = 0.01  # TODO make this configurable thorugh REST call
            boxes = get_network_boxes(self.net, threshold, pnum)
            boxes = [boxes[i] for i in range(pnum[0])]  # convert c to python
            (h, w, _) = image.shape
            w_ratio = w/self.image.w
            h_ratio = h/self.image.h

            for box in boxes:
                name = box.name.decode("ascii")
                x = int(box.bbox.x * w_ratio)
                y = int(box.bbox.y * h_ratio)
                w = int(box.bbox.w * w_ratio)
                h = int(box.bbox.h * h_ratio)
                if self.category_types[name] == CategoryType.Box:
                    detections.box_detections.append(BoxDetection(
                        name, x, y, w, h, self.version, round(box.prob, 2)
                    ))
                elif self.category_types[name] == CategoryType.Point:
                    cx, cy = (np.average([x, x + w]), np.average([y, y + h]))
                    detections.point_detections.append(PointDetection(
                        name, int(cx), int(
                            cy), self.version, round(box.prob, 2)
                    ))
        except Exception as e:
            ic(f'Exception: {str(e)}')
            logging.exception('tkdnn inference failed')

        return detections
