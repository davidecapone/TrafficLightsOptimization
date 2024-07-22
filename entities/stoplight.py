#!/usr/bin/env python

from entities.colors import TrafficLightColor

class Stoplight:
    GREEN_DURATION = 300  # ticks
    YELLOW_DURATION = 90  # ticks

    def __init__(self, color):
        
        self.color_NS = color

        if self.color_NS == TrafficLightColor.GREEN.value:
            self.color_EW = TrafficLightColor.RED.value
        else:
            self.color_EW = TrafficLightColor.GREEN.value

        self.time_yellow = 0
        self.time_green = 0


    def switch_yellow(self):

        if self.color_NS == TrafficLightColor.GREEN.value:
            self.color_NS = TrafficLightColor.YELLOW.value
        elif self.color_EW == TrafficLightColor.GREEN.value:
            self.color_EW = TrafficLightColor.YELLOW.value

    def update_stoplight(self):

        if self.color_NS == TrafficLightColor.GREEN.value or self.color_EW == TrafficLightColor.GREEN.value:
            self.time_green += 1
        if self.color_NS == TrafficLightColor.YELLOW.value or self.color_EW == TrafficLightColor.YELLOW.value:
            self.time_yellow += 1

        if self.time_yellow >= Stoplight.YELLOW_DURATION:
            if self.color_NS == TrafficLightColor.YELLOW.value:
                self.color_NS = TrafficLightColor.RED.value
                self.color_EW = TrafficLightColor.GREEN.value
                self.time_green = 0
            elif self.color_EW == TrafficLightColor.YELLOW.value:
                self.color_EW = TrafficLightColor.RED.value
                self.color_NS = TrafficLightColor.GREEN.value
                self.time_green = 0
            self.time_yellow = 0