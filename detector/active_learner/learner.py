from typing import List
from active_learner.observation import Observation
from icecream import ic
from box_detection import BoxDetection
from detections import Detections


class Learner:
    def __init__(self):
        self.reset_time = 3600
        self.low_conf_box_observations: List[Observation] = []
        self.iou_threshold = 0.5

    def forget_old_detections(self):
        self.low_conf_box_observations = [detection
                                    for detection in self.low_conf_box_observations
                                    if not detection.is_older_than(self.reset_time)]

    def add_box_detections(self, box_detections: List[BoxDetection]) -> List[str]:
        return self.add_detections(Detections(box_detections=box_detections))

    def add_detections(self, detections: Detections) -> List[str]:
        active_learning_causes = set()

        for box in detections.box_detections:
            if box.confidence < .3 or box.confidence > .6:
                continue

            similar_detections = self.find_similar_observations(box)
            if(any(similar_detections)):
                [sd.update_last_seen() for sd in similar_detections]
            else:
                self.low_conf_box_observations.append(Observation(box))
                active_learning_causes.add('lowConfidence')

        return list(active_learning_causes)

    def find_similar_observations(self, new_detection: BoxDetection):
        return [
            observation
            for observation in self.low_conf_box_observations
            if observation.detection.category_name == new_detection.category_name
            and observation.detection.intersection_over_union(new_detection) >= self.iou_threshold
        ]
