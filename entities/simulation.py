import pygame
from entities.environment import Environment
from entities.car_manager import CarManager
from entities.stoplight_manager import StoplightManager

class Simulation:
    """
    Defines the simulation of the traffic light.
    """
    def __init__(self, name: str, ambient_images_path: list, window_size: tuple = (1000, 1000), audio_effect_path: str = None):
        assert len(ambient_images_path) == 4, "Ambient must have 4 images"
        assert window_size[0] > 0 and window_size[1] > 0, "Window size must be greater than 0"

        pygame.init()
        pygame.display.set_caption(name)

        self.window = pygame.display.set_mode(window_size)
        self.environment = Environment(name, self.window, self._load_images(ambient_images_path))
        self.car_manager = CarManager(self.window)
        self.stoplight_manager = StoplightManager()

        if audio_effect_path:
            self._load_audio(audio_effect_path, volume=0.2)

        self.clock = pygame.time.Clock()

    def _load_images(self, ambient_images_path: list) -> None:
        return [pygame.image.load(image_path) for image_path in ambient_images_path]

    def _load_audio(self, audio_effect_path: str, volume: float) -> None:
        pygame.mixer.init()
        pygame.mixer.music.load(audio_effect_path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)

    def run(self) -> None:
        prev_time = 0

        while True:
            # Draw the environment
            self.environment.draw()
            self.stoplight_manager.draw_stoplight(self.window)

            self.clock.tick(60)
            self.stoplight_manager.update_stoplight()

            # Check for events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            time = pygame.time.get_ticks() // 1000
            if time != prev_time and time % 2 == 0:
                self.car_manager.add_car()
                prev_time = time

            if self.stoplight_manager.stoplight.time_green >= 300:
                self.stoplight_manager.stoplight.switch_yellow()

            self.car_manager.update_cars(self.stoplight_manager.stoplight)
            self.car_manager.draw_cars()

            pygame.display.update()