#!/usr/bin/env python

from enum import Enum

class TrafficLightColor(Enum):
    """
    Defines the possible colors of the traffic light.
    """
    GREEN = (0, 255, 0, 100)
    RED = (255, 0, 0, 100)
    YELLOW = (255, 255, 0, 100)