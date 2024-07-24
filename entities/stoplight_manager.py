import pygame
from entities.stoplight import Stoplight
from entities.colors import TrafficLightColor

class StoplightManager:
    """
    Manages the stoplight in the simulation.
    """
    def __init__(self):
        self.stoplight = Stoplight()

    def update_stoplight(self):
        self.stoplight.update_stoplight()

    def draw_stoplight(self, window):
        pygame.draw.line(window, self.stoplight.color_NS, (window.get_width() // 2 - 27, window.get_height() // 2 - 32), (window.get_width() // 2 - 2, window.get_height() // 2 - 32), 5)
        pygame.draw.line(window, self.stoplight.color_NS, (window.get_width() // 2 + 3, window.get_height() // 2 + 33), (window.get_width() // 2 + 27, window.get_height() // 2 + 33), 5)
        pygame.draw.line(window, self.stoplight.color_EW, (window.get_width() // 2 - 32, window.get_height() // 2 + 3), (window.get_width() // 2 - 32, window.get_height() // 2 + 27), 5)
        pygame.draw.line(window, self.stoplight.color_EW, (window.get_width() // 2 + 33, window.get_height() // 2 - 27), (window.get_width() // 2 + 33, window.get_height() // 2 - 2), 5)

    def get_ns_color(self):
        return self.stoplight.get_ns_color()

    def get_ew_color(self) -> TrafficLightColor:
        return self.stoplight.get_ew_color()

    
