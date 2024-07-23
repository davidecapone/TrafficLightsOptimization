import pygame 
import random
from entities.car import Car
from entities.stoplight import Stoplight
from entities.colors import TrafficLightColor
from entities.car_actions import CarActions


class Ambient():
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

        WHITE = (255, 255, 255)
        GRAY = (128, 128, 128)

        # Draw intersection
        ## Draw road
        pygame.draw.line(self.window, GRAY, (0, self.window_height//2), (self.window_width, self.window_height//2), 60)
        pygame.draw.line(self.window, GRAY, (self.window_width//2, 0), (self.window_width//2, self.window_height), 60)
        ## Draw lanes
        pygame.draw.line(self.window, WHITE, (0, self.window_height//2 - 28), (self.window_width, self.window_height//2 - 28), 1)
        pygame.draw.line(self.window, WHITE, (0, self.window_height//2 + 28), (self.window_width, self.window_height//2 + 28), 1)
        pygame.draw.line(self.window, WHITE, (self.window_width//2 - 28, 0), (self.window_width//2 - 28, self.window_height), 1)
        pygame.draw.line(self.window, WHITE, (self.window_width//2 + 28, 0), (self.window_width//2 + 28, self.window_height), 1)
        pygame.draw.line(self.window, WHITE, (0, self.window_height//2), (self.window_width, self.window_height//2), 4)
        pygame.draw.line(self.window, WHITE, (self.window_width//2, 0), (self.window_width//2, self.window_height), 4)
        ## Draw crosswalks
        pygame.draw.line(self.window, WHITE, (self.window_width//2 - 23, self.window_height//2 - 200), (self.window_width//2 - 23, self.window_height//2 - 180), 2)
        pygame.draw.line(self.window, WHITE, (self.window_width//2 - 17, self.window_height//2 -200), (self.window_width//2 - 17, self.window_height//2 - 180), 2)
        pygame.draw.line(self.window, WHITE, (self.window_width//2 - 12, self.window_height//2 - 200), (self.window_width//2 - 12, self.window_height//2 - 180), 2)
        pygame.draw.line(self.window, WHITE, (self.window_width//2 - 6, self.window_height//2 - 200), (self.window_width//2 - 6, self.window_height//2 - 180), 2)
        pygame.draw.line(self.window, WHITE, (self.window_width//2 + 6, self.window_height//2 - 200), (self.window_width//2 + 6, self.window_height//2 - 180), 2)
        pygame.draw.line(self.window, WHITE, (self.window_width//2 + 12, self.window_height//2 - 200), (self.window_width//2 + 12, self.window_height//2 - 180), 2)
        pygame.draw.line(self.window, WHITE, (self.window_width//2 + 17, self.window_height//2 - 200), (self.window_width//2 + 17, self.window_height//2 - 180), 2)
        pygame.draw.line(self.window, WHITE, (self.window_width//2 + 23, self.window_height//2 - 200), (self.window_width//2 + 23, self.window_height//2 - 180), 2)
        pygame.draw.line(self.window, WHITE, (self.window_width//2 - 200, self.window_height//2 - 23), (self.window_width//2 - 180, self.window_height//2 - 23), 2)
        pygame.draw.line(self.window, WHITE, (self.window_width//2 - 200, self.window_height//2 - 17), (self.window_width//2 - 180, self.window_height//2 - 17), 2)
        pygame.draw.line(self.window, WHITE, (self.window_width//2 - 200, self.window_height//2 - 12), (self.window_width//2 - 180, self.window_height//2 - 12), 2)
        pygame.draw.line(self.window, WHITE, (self.window_width//2 - 200, self.window_height//2 - 6), (self.window_width//2 - 180, self.window_height//2 - 6), 2)
        pygame.draw.line(self.window, WHITE, (self.window_width//2 - 200, self.window_height//2 + 6), (self.window_width//2 - 180, self.window_height//2 + 6), 2)
        pygame.draw.line(self.window, WHITE, (self.window_width//2 - 200, self.window_height//2 + 12), (self.window_width//2 - 180, self.window_height//2 + 12), 2)
        pygame.draw.line(self.window, WHITE, (self.window_width//2 - 200, self.window_height//2 + 17), (self.window_width//2 - 180, self.window_height//2 + 17), 2)
        pygame.draw.line(self.window, WHITE, (self.window_width//2 - 200, self.window_height//2 + 23), (self.window_width//2 - 180, self.window_height//2 + 23), 2)
        pygame.draw.line(self.window, WHITE, (self.window_width//2 + 180, self.window_height//2 - 23), (self.window_width//2 + 200, self.window_height//2 - 23), 2)
        pygame.draw.line(self.window, WHITE, (self.window_width//2 + 180, self.window_height//2 - 17), (self.window_width//2 + 200, self.window_height//2 - 17), 2)
        pygame.draw.line(self.window, WHITE, (self.window_width//2 + 180, self.window_height//2 - 12), (self.window_width//2 + 200, self.window_height//2 - 12), 2)
        pygame.draw.line(self.window, WHITE, (self.window_width//2 + 180, self.window_height//2 - 6), (self.window_width//2 + 200, self.window_height//2 - 6), 2)
        pygame.draw.line(self.window, WHITE, (self.window_width//2 + 180, self.window_height//2 + 6), (self.window_width//2 + 200, self.window_height//2 + 6), 2)
        pygame.draw.line(self.window, WHITE, (self.window_width//2 + 180, self.window_height//2 + 12), (self.window_width//2 + 200, self.window_height//2 + 12), 2)
        pygame.draw.line(self.window, WHITE, (self.window_width//2 + 180, self.window_height//2 + 17), (self.window_width//2 + 200, self.window_height//2 + 17), 2)
        pygame.draw.line(self.window, WHITE, (self.window_width//2 + 180, self.window_height//2 + 23), (self.window_width//2 + 200, self.window_height//2 + 23), 2)
        pygame.draw.line(self.window, WHITE, (self.window_width//2 - 23, self.window_height//2 + 200), (self.window_width//2 - 23, self.window_height//2 + 220), 2)
        pygame.draw.line(self.window, WHITE, (self.window_width//2 - 17, self.window_height//2 + 200), (self.window_width//2 - 17, self.window_height//2 + 220), 2)
        pygame.draw.line(self.window, WHITE, (self.window_width//2 - 12, self.window_height//2 + 200), (self.window_width//2 - 12, self.window_height//2 + 220), 2)
        pygame.draw.line(self.window, WHITE, (self.window_width//2 - 6, self.window_height//2 + 200), (self.window_width//2 - 6, self.window_height//2 + 220), 2)
        pygame.draw.line(self.window, WHITE, (self.window_width//2 + 6, self.window_height//2 + 200), (self.window_width//2 + 6, self.window_height//2 + 220), 2)
        pygame.draw.line(self.window, WHITE, (self.window_width//2 + 12, self.window_height//2 + 200), (self.window_width//2 + 12, self.window_height//2 + 220), 2)
        pygame.draw.line(self.window, WHITE, (self.window_width//2 + 17, self.window_height//2 + 200), (self.window_width//2 + 17, self.window_height//2 + 220), 2)
        pygame.draw.line(self.window, WHITE, (self.window_width//2 + 23, self.window_height//2 + 200), (self.window_width//2 + 23, self.window_height//2 + 220), 2)
        ## Cover intersection
        pygame.draw.rect(self.window, GRAY, (self.window_width//2 - 29, self.window_height//2 - 29, 60, 60))

    def draw_stoplight(self, stoplight:Stoplight):

        pygame.draw.line(self.window, stoplight.color_NS, (self.window_width//2 - 27, self.window_height//2 - 32), (self.window_width//2 - 2, self.window_height//2 - 32), 5)
        pygame.draw.line(self.window, stoplight.color_NS, (self.window_width//2 + 3, self.window_height//2 + 33), (self.window_width//2 + 27, self.window_height//2 + 33), 5)
        pygame.draw.line(self.window, stoplight.color_EW, (self.window_width//2 - 32, self.window_height//2 + 3), (self.window_width//2 - 32, self.window_height//2 + 27), 5)
        pygame.draw.line(self.window, stoplight.color_EW, (self.window_width//2 + 33, self.window_height//2 - 27), (self.window_width//2 + 33, self.window_height//2 - 2), 5)

    def start(self):
        # TODO: remove these lines and use the Stoplight class instead:
        RED = (255, 0, 0, 100)
        GREEN = (0, 255, 0, 100)
        YELLOW = (255, 255, 0, 100)

        stoplight = Stoplight( random.choice([GREEN, RED]) )
        prev_time = 0
        
        while True:
            
            self._blit_images()
            self._draw_lines()
            self.draw_stoplight(stoplight)

            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    pygame.quit()


            time = pygame.time.get_ticks() // 1000

            if time != prev_time:
                if time % 2 == 0:
                    car = Car(window=self.window)
                    self.cars.append(car)
                    
                prev_time = time

            if stoplight.time_green >= 300:
                stoplight.switch_yellow()

            for car in self.cars:

                if car.isStopped:
                    car.waiting_time += 1

                    if ((car.direction in [CarActions.UP, CarActions.DOWN] and stoplight.color_NS == GREEN) or 
                        (car.direction in [CarActions.LEFT, CarActions.RIGHT] and stoplight.color_EW == GREEN)):
                        car.isStopped = False
                        car.move()

                else:
                    car.waiting_time = 0

                    if ((car.direction == CarActions.UP and car.y == self.window_height//2 + 50 and (stoplight.color_NS == RED or stoplight.color_NS == YELLOW)) or
                        (car.direction == CarActions.DOWN and car.y + Car.LENGTH == self.window_height//2 - 50 and (stoplight.color_NS == RED or stoplight.color_NS == YELLOW)) or
                        (car.direction == CarActions.LEFT and car.x == self.window_width//2 + 50 and (stoplight.color_EW == RED or stoplight.color_EW == YELLOW)) or
                        (car.direction == CarActions.RIGHT and car.x + Car.LENGTH == self.window_width//2 - 50 and (stoplight.color_EW == RED or stoplight.color_EW == YELLOW))) or not car.can_move(self.cars):
                        car.stop()
                    else:
                        if ((car.direction == CarActions.UP and car.y <= self.window_height//2 + Car.SPEED and car.y >= self.window_height//2 - Car.SPEED) or
                            (car.direction == CarActions.DOWN and car.y + Car.LENGTH >= self.window_height//2 - Car.SPEED and car.y + Car.LENGTH <= self.window_height//2 + Car.SPEED) or
                            (car.direction == CarActions.LEFT and car.x <= self.window_width//2 + Car.SPEED and car.x >= self.window_width//2 - Car.SPEED) or
                            (car.direction == CarActions.RIGHT and car.x + Car.LENGTH >= self.window_width//2 - Car.SPEED and car.x + Car.LENGTH <= self.window_width//2 + Car.SPEED)):
                            car.turn_or_straight()
                        car.move()
                car.draw()

            # remove cars that have left the screen
            self.cars = [car for car in self.cars if car.x >= 0 and car.x <= self.window_width and car.y >= 0 and car.y <= self.window_height]

                
            pygame.display.update()