from icecream import ic
import cv2
from ctypes import *

from tkdnn import Tkdnn


def test_initialization(detector):
    assert detector.image.w == 800
    assert detector.image.h == 800
    assert detector.image.c == 3


def test_box_detection(detector: Tkdnn):
    image = cv2.imread('tests/test.jpg')
    detections = detector.evaluate(image)
    for d in detections.box_detections:
        image = cv2.rectangle(image, (d.x, d.y), (d.x + d.width, d.y + d.height), (0, 0, 0), 2)
    cv2.imwrite('/data/test-result.jpg', image)
    assert len(detections.box_detections) > 0

def test_point_detection(detector: Tkdnn):
    image = cv2.imread('tests/test2.jpg')
    detections = detector.evaluate(image)
    for d in detections.point_detections:
        image = cv2.rectangle(image, (d.x, d.y), (d.x + 20, d.y + 20), (0, 0, 0), 2)
    cv2.imwrite('/data/test2-result.jpg', image)
    assert len(detections.point_detections) > 0
