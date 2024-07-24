import pygame 
import random
from entities.car import Car
from entities.stoplight import Stoplight
from entities.colors import TrafficLightColor
from entities.car_actions import CarActions

# Colors
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

class Simulation():
    def __init__(self, name:str, ambient_images_path:list, window_size:tuple = (1000, 1000), audio_effect_path:str = None):

        assert len(ambient_images_path) == 4, "Ambient must have 4 images"
        assert window_size[0] > 0 and window_size[1] > 0, "Window size must be greater than 0"

        pygame.init()

        self.window = pygame.display.set_mode(window_size)
        self.window_width = self.window.get_width()
        self.window_height = self.window.get_height()

        self.ambient_images = self._load_images(ambient_images_path)
        self.ambient_images = self._resize_images(self.ambient_images)
        self._blit_images()

        if audio_effect_path:
            self._load_audio(audio_effect_path, volume = 0.2)

        self._draw_lines()

        self.clock = pygame.time.Clock()
        self.cars = []

        pygame.display.set_caption(name)


    def _load_images(self, ambient_images_path:list) -> None:
            
            ambient_images = []
    
            for image_path in ambient_images_path:
                ambient_images.append(pygame.image.load(image_path))
    
            return ambient_images

            # using list com
    
    def _resize_images(self, ambient_images:list) -> None:
         
        for i in range(len(ambient_images)):
            ambient_images[i] = pygame.transform.scale(
                 ambient_images[i], (self.window_width//2 - 30, self.window_height//2 - 30))
    
        return ambient_images
    
    def _blit_images(self) -> None:
    
        self.window.blit(self.ambient_images[0], (0, 0))
        self.window.blit(self.ambient_images[1], (self.window_width//2 + 30, 0))
        self.window.blit(self.ambient_images[2], (self.window_width//2 + 30, self.window_height//2 + 30))
        self.window.blit(self.ambient_images[3], (0, self.window_height//2 + 30))
    
    def _load_audio(self, audio_effect_path:str, volume:float) -> None:

            pygame.mixer.init()
            pygame.mixer.music.load(audio_effect_path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1)

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

    def draw_stoplight(self, stoplight:Stoplight):

        pygame.draw.line(self.window, stoplight.color_NS, (self.window_width//2 - 27, self.window_height//2 - 32), (self.window_width//2 - 2, self.window_height//2 - 32), 5)
        pygame.draw.line(self.window, stoplight.color_NS, (self.window_width//2 + 3, self.window_height//2 + 33), (self.window_width//2 + 27, self.window_height//2 + 33), 5)
        pygame.draw.line(self.window, stoplight.color_EW, (self.window_width//2 - 32, self.window_height//2 + 3), (self.window_width//2 - 32, self.window_height//2 + 27), 5)
        pygame.draw.line(self.window, stoplight.color_EW, (self.window_width//2 + 33, self.window_height//2 - 27), (self.window_width//2 + 33, self.window_height//2 - 2), 5)

    def run(self):

        stoplight = Stoplight()
        prev_time = 0
        
        while True:
            
            # Draw the ambient
            self._blit_images()
            self._draw_lines()
            self.draw_stoplight(stoplight)

            self.clock.tick(30)
            stoplight.update_stoplight()

            # Check for events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
            

            time = pygame.time.get_ticks() // 1000
            if time != prev_time and time % 2 == 0:
                car = Car(window=self.window)
                self.cars.append(car)
                prev_time = time

            if stoplight.time_green >= 300:
                stoplight.switch_yellow()

            for car in self.cars:

                car_direction = car.get_direction()

                if car.is_stopped():
                    car.increase_waiting_time() # Then we increase the waiting time

                    if ((car_direction in [CarActions.UP, CarActions.DOWN] and stoplight.color_NS == TrafficLightColor.GREEN.value) or 
                        (car_direction in [CarActions.LEFT, CarActions.RIGHT] and stoplight.color_EW == TrafficLightColor.GREEN.value)):
                        car.set_stopped(False)
                        car.move()

                else:   # Car is moving
                    car_x, car_y = car.get_position()

                    if ((car_direction == CarActions.UP and car_y == self.window_height//2 + 50 and (stoplight.color_NS in [TrafficLightColor.RED.value, TrafficLightColor.YELLOW.value])) or
                        (car_direction == CarActions.DOWN and car_y + Car.LENGTH == self.window_height//2 - 50 and (stoplight.color_NS in [TrafficLightColor.RED.value, TrafficLightColor.YELLOW.value])) or
                        (car_direction == CarActions.LEFT and car_x == self.window_width//2 + 50 and (stoplight.color_EW in [TrafficLightColor.RED.value, TrafficLightColor.YELLOW.value])) or
                        (car_direction == CarActions.RIGHT and car_x + Car.LENGTH == self.window_width//2 - 50 and (stoplight.color_EW in [TrafficLightColor.RED.value, TrafficLightColor.YELLOW.value]))) or not car.can_move(self.cars):
                        car.set_stopped(True)
                    else:
                        if ((car_direction == CarActions.UP and car_y <= self.window_height//2 + Car.SPEED and car_y >= self.window_height//2 - Car.SPEED) or
                            (car_direction == CarActions.DOWN and car_y + Car.LENGTH >= self.window_height//2 - Car.SPEED and car_y + Car.LENGTH <= self.window_height//2 + Car.SPEED) or
                            (car_direction == CarActions.LEFT and car_x <= self.window_width//2 + Car.SPEED and car_x >= self.window_width//2 - Car.SPEED) or
                            (car_direction == CarActions.RIGHT and car_x + Car.LENGTH >= self.window_width//2 - Car.SPEED and car_x + Car.LENGTH <= self.window_width//2 + Car.SPEED)):
                            car.turn_or_straight()
                        car.move()

                # Remove cars that have left the screen
                if car.is_out_of_window():
                    self.cars.remove(car)

                car.draw()
                
            pygame.display.update()
