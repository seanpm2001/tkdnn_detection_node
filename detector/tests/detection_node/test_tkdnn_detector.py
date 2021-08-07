from icecream import ic
import cv2
from ctypes import *


def test_initialization(detector):
    assert detector.image.w == 800
    assert detector.image.h == 800
    assert detector.image.c == 3


def test_detection(detector):
    image = cv2.imread('tests/test.jpg')
    detections = detector.evaluate(image)
    for d in detections:
        image = cv2.rectangle(image, (d.x, d.y), (d.x + d.width, d.y + d.height), (0, 0, 0), 2)
    cv2.imwrite('/data/test-result.jpg', image)
    assert len(detections) > 0
