# Learner Tests incoming
from datetime import datetime, timedelta
import pytest
from active_learner import detection as d
from active_learner import learner as l
from icecream import ic
import time
from detection import Detection

dirt_detection = d.ActiveLearnerDetection(Detection('dirt', 0, 0, 100, 100, 'xyz', .3))
second_dirt_detection = Detection('dirt', 0, 20, 10, 10, 'xyz', .35)
conf_too_high_detection = Detection('dirt', 0, 0, 100, 100, 'xyz', .61)
conf_too_low_detection = Detection('dirt', 0, 0, 100, 100, 'xyz', .29)


def test_learner_confidence():
    learner = l.Learner()
    assert len(learner.low_conf_detections) == 0

    active_learning_cause = learner.add_detections([dirt_detection])
    assert active_learning_cause == [
        'lowConfidence'], f'Active Learning should be done due to lowConfidence'
    assert len(learner.low_conf_detections) == 1, 'Detection should be stored'

    active_learning_cause = learner.add_detections([dirt_detection])
    assert len(learner.low_conf_detections) == 1, f'Detection should already be stored'
    assert active_learning_cause == []

    active_learning_cause = learner.add_detections([conf_too_low_detection])
    assert len(learner.low_conf_detections) == 1, f'Confidence of detection too low'
    assert active_learning_cause == []

    active_learning_cause = learner.add_detections([conf_too_high_detection])
    assert len(learner.low_conf_detections) == 1, f'Confidence of detection too high'
    assert active_learning_cause == []


def test_add_second_detection_to_learner():
    learner = l.Learner()
    assert len(learner.low_conf_detections) == 0
    learner.add_detections([dirt_detection])
    assert len(learner.low_conf_detections) == 1, 'Detection should be stored'
    learner.add_detections([second_dirt_detection])
    assert len(learner.low_conf_detections) == 2, 'Second detection should be stored'


def test_update_last_seen():
    dirt_detection.last_seen = datetime.now() - timedelta(seconds=.5)
    assert dirt_detection._is_older_than(0.5) == True
    learner = l.Learner()
    learner.add_detections([dirt_detection])

    last_seen = dirt_detection.last_seen
    dirt_detection.last_seen = datetime.now() + timedelta(seconds=.5)
    learner.add_detections([dirt_detection])
    assert dirt_detection.last_seen > last_seen


def test_forget_old_detections():
    learner = l.Learner()
    assert len(learner.low_conf_detections) == 0

    active_learning_cause = learner.add_detections([dirt_detection])
    assert active_learning_cause == [
        'lowConfidence'], f'Active Learning should be done due to lowConfidence.'

    assert len(learner.low_conf_detections) == 1

    learner.low_conf_detections[0].last_seen = datetime.now() - timedelta(minutes=30)
    learner.forget_old_detections()
    assert len(learner.low_conf_detections) == 1

    learner.low_conf_detections[0].last_seen = datetime.now() - timedelta(hours=1, minutes=1)
    learner.forget_old_detections()
    assert len(learner.low_conf_detections) == 0


def test_active_learner_extracts_from_json():
    detections = [
        {"category_name": "dirt",
         "x": 1366,
         "y": 1017,
         "width": 37,
         "height": 24,
         "model_name": "some_weightfile",
         "confidence": .3},
        {"category_name": "obstacle",
         "x": 0,
         "y": 0,
         "width": 37,
         "height": 24,
         "model_name": "some_weightfile",
         "confidence": .35},
        {"category_name": "dirt",
         "x": 1479,
         "y": 862,
         "width": 14,
         "height": 11,
         "model_name": "some_weightfile",
         "confidence": .2}]

    mac = '0000'
    learners = {mac: l.Learner()}

    active_learning_cause = learners[mac].add_detections(
        [d.ActiveLearnerDetection(Detection.from_dict(_detection)) for _detection in detections])

    assert active_learning_cause == ['lowConfidence']
