#!/usr/bin/env python

GREEN = (0, 255, 0, 100)
RED = (255, 0, 0, 100)
YELLOW = (255, 255, 0, 100)

class Stoplight:
    GREEN_DURATION = 300  # ticks
    YELLOW_DURATION = 90  # ticks

    def __init__(self, color):
        self.color_NS = color
        if self.color_NS == GREEN:
            self.color_EW = RED
        else:
            self.color_EW = GREEN
        self.time_yellow = 0
        self.time_green = 0

    def switch_yellow(self):
        if self.color_NS == GREEN:
            self.color_NS = YELLOW
        elif self.color_EW == GREEN:
            self.color_EW = YELLOW

    def update_stoplight(self):
        if self.color_NS == GREEN or self.color_EW == GREEN:
            self.time_green += 1
        if self.color_NS == YELLOW or self.color_EW == YELLOW:
            self.time_yellow += 1

        if self.time_yellow >= 90:
            if self.color_NS == YELLOW:
                self.color_NS = RED
                self.color_EW = GREEN
                self.time_green = 0
            elif self.color_EW == YELLOW:
                self.color_EW = RED
                self.color_NS = GREEN
                self.time_green = 0
            self.time_yellow = 0