from typing import List
from dataclasses import dataclass, field

from box_detection import BoxDetection
from point_detection import PointDetection


@dataclass
class Detections:
    box_detections: List[BoxDetection] = field(default_factory=list)
    point_detections: List[PointDetection] = field(default_factory=list)