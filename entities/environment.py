import pygame
import os

# Colors
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

AMBIENT_IMAGES_PATH = './assets/img/'
AUDIO_PATH = './assets/audio/street_sound_effect.mp3'

class Environment:
    """
    Defines the environment of the simulation, which includes the images and the drawing of the environment.
    """
    def __init__(self, window_size, name, audio):
        
        assert window_size[0] > 0 and window_size[1] > 0, "Window size must be greater than 0"
        assert name, "Name for the simulation must be a valid string"

        self.window = None
        self._pygame_init(window_size, name, audio=audio)

        self.ambient_images = self._resize_images(
            self._load_pygame_images(
                [os.path.join(AMBIENT_IMAGES_PATH, image) for image in os.listdir(AMBIENT_IMAGES_PATH)]
            )
        )

        self.window_width = self.window.get_width()
        self.window_height = self.window.get_height()

    def get_window(self):
        return self.window

    def _pygame_init(self, window_size:tuple, name:str, audio:bool) -> None:
        pygame.init()
        pygame.display.set_caption(name)
        self.window = pygame.display.set_mode(window_size)

        if audio:
            pygame.mixer.init()
            pygame.mixer.music.load(audio)
            pygame.mixer.music.set_volume(0.2)
            pygame.mixer.music.play(-1)

    def _load_pygame_images(self, ambient_images_path: list) -> None:
        return [pygame.image.load(image_path) for image_path in ambient_images_path]

    def _resize_images(self, ambient_images):
        window_width = self.window.get_width()
        window_height = self.window.get_height()
        return [pygame.transform.scale(image, (window_width // 2 - 30, window_height // 2 - 30)) for image in ambient_images]

    def draw(self):
        self._blit_images()
        self._draw_lines()

    def _blit_images(self):
        self.window.blit(self.ambient_images[0], (0, 0))
        self.window.blit(self.ambient_images[1], (self.window_width // 2 + 30, 0))
        self.window.blit(self.ambient_images[2], (self.window_width // 2 + 30, self.window_height // 2 + 30))
        self.window.blit(self.ambient_images[3], (0, self.window_height // 2 + 30))

    def _draw_lines(self):
        # Draw intersection
        pygame.draw.line(self.window, GRAY, (0, self.window_height // 2), (self.window_width, self.window_height // 2), 60)
        pygame.draw.line(self.window, GRAY, (self.window_width // 2, 0), (self.window_width // 2, self.window_height), 60)
        # Draw lanes
        for offset in [-28, 28]:
            pygame.draw.line(self.window, WHITE, (0, self.window_height // 2 + offset), (self.window_width, self.window_height // 2 + offset), 1)
            pygame.draw.line(self.window, WHITE, (self.window_width // 2 + offset, 0), (self.window_width // 2 + offset, self.window_height), 1)
        pygame.draw.line(self.window, WHITE, (0, self.window_height // 2), (self.window_width, self.window_height // 2), 4)
        pygame.draw.line(self.window, WHITE, (self.window_width // 2, 0), (self.window_width // 2, self.window_height), 4)
        # Draw crosswalks
        crosswalk_offsets = [-23, -17, -12, -6, 6, 12, 17, 23]
        for offset in crosswalk_offsets:
            pygame.draw.line(self.window, WHITE, (self.window_width // 2 + offset, self.window_height // 2 - 200), (self.window_width // 2 + offset, self.window_height // 2 - 180), 2)
            pygame.draw.line(self.window, WHITE, (self.window_width // 2 + offset, self.window_height // 2 + 200), (self.window_width // 2 + offset, self.window_height // 2 + 220), 2)
            pygame.draw.line(self.window, WHITE, (self.window_width // 2 - 200, self.window_height // 2 + offset), (self.window_width // 2 - 180, self.window_height // 2 + offset), 2)
            pygame.draw.line(self.window, WHITE, (self.window_width // 2 + 180, self.window_height // 2 + offset), (self.window_width // 2 + 200, self.window_height // 2 + offset), 2)
        # Cover intersection
        pygame.draw.rect(self.window, GRAY, (self.window_width // 2 - 29, self.window_height // 2 - 29, 60, 60))

