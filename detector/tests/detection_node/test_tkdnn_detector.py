from icecream import ic
import cv2
from ctypes import *
from learning_loop_node.globals import GLOBALS
import time


def test_initialization(configured_detector):
    assert configured_detector.image.w == 800
    assert configured_detector.image.h == 800
    assert configured_detector.image.c == 3


def test_tkdnn_detector(configured_detector):
    image = cv2.imread('tests/test.jpg')
    detections = configured_detector.evaluate(image)
    for d in detections.box_detections:
        image = cv2.rectangle(
            image, (d.x, d.y), (d.x + d.width, d.y + d.height), (0, 0, 0), 2)
    cv2.imwrite(f'{GLOBALS.data_folder}/test-result_box.jpg', image)
    assert len(detections.box_detections) == 4


def test_performance(configured_detector):
    sum = 0
    measurements = 10
    for i in range(measurements):
        start_time = time.time()
        image = cv2.imread('tests/test.jpg')
        detections = configured_detector.evaluate(image)
        dt = (time.time() - start_time) * 1000
        if i > 0:  # first detection may be slow
            sum += dt
        assert len(detections.box_detections) > 0

    average = int(sum / (measurements-1))
    print(f'~{average} ms ', end='')
    assert average < 200, f'avereage detection time should be low, but was {average}'
    # TODO discuss with @Rodja why the it has to be 185ms, bzw. why it is way slower now.
