from icecream import ic
import cv2
from ctypes import *


def test_initialization(detector):
    assert len(detector.classes) == 9
    assert detector.image.w == 800
    assert detector.image.h == 800
    assert detector.image.c == 3


def test_detection(detector):
    image = cv2.imread('/data/test.jpg')
    detections = detector.evaluate(image)
    for d in detections:
        image = cv2.rectangle(image, (d.x, d.y), (d.x + d.width, d.y + d.height), (0, 0, 0), 2)
    cv2.imwrite('/data/test-result.jpg', image)
    assert len(detections) == 13
    d = detections[0]
    assert d.category_name == 'marker_hinten_rechts'
    assert d.confidence == 99.9
    assert d.x == 724
    assert d.y == 526
    assert d.width == 38
    assert d.height == 37
    assert d.model_name == 'unknown model'
