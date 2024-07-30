import random
import pygame
from entities.car_actions import CarActions

class Car:
    """
    Implements the car object.

    Attributes:
    - window: pygame window
    - window_width: int representing the width of the window
    - window_height: int representing the height of the window
    - direction: CarActions representing the direction the car is facing
    - x: int representing the x coordinate of the car
    - y: int representing the y coordinate of the car
    - isStopped: bool representing if the car is stopped
    - turn_right: bool representing if the car is turning right
    - waiting_time: int representing the time the car has been waiting
    - color: tuple representing the color of the car

    Constants:
    - SPEED: int representing the speed of the car
    - WIDTH: int representing the width of the car
    - LENGTH: int representing the length of the car
    """
    SPEED = 4
    WIDTH = 20
    LENGTH = 40

    def __init__(self, window, direction:list = None):
        self.window = window
        self.window_width = self.window.get_width()
        self.window_height = self.window.get_height()

        if direction:
            self.direction = random.choice(direction)
        else:
            self.direction = random.choice([CarActions.UP, CarActions.DOWN, CarActions.LEFT, CarActions.RIGHT])

        self.x, self.y = self._set_veichle_coordinates(self.direction)

        self.isStopped = False

        self.turn_right = random.choice([False, True])

        self.waiting_time = 0
        
        self.color = (random.randint(1, 255), random.randint(1, 255), random.randint(1, 255))


    def get_direction(self) -> CarActions:
        return self.direction

    def get_position(self) -> tuple:
        return self.x, self.y

    def increase_waiting_time(self): 
        self.waiting_time += 1

    def set_waiting_time(self, time:int):
        self.waiting_time = time

    def get_waiting_time(self) -> int:
        return self.waiting_time

    def set_stopped(self, isStopped:bool):
        self.isStopped = isStopped

    def is_stopped(self) -> bool:
        return self.isStopped
    
    def is_out_of_window(self) -> bool:
        return self.x < 0 or self.x > self.window_width or self.y < 0 or self.y > self.window_height

    def _set_veichle_coordinates(self, direction:CarActions) -> tuple:
        """
        Set the initial coordinates of the vehicle based on the direction it is facing.

        Parameters:
            direction (CarActions): The direction the vehicle is facing.

        Returns:
            tuple: The x and y coordinates of the vehicle.
        """
        if direction == CarActions.UP:
            return self.window_width // 2 + 5, self.window_height
        elif direction == CarActions.DOWN:
            return self.window_width // 2 - 20 - 4, 0
        elif direction == CarActions.LEFT:
            return self.window_width, self.window_height // 2 - 20 - 4
        elif direction == CarActions.RIGHT:
            return 0, self.window_height // 2 + 5

    def move(self):
        """
        Move the car based on the direction it is facing.

        Raises:
            AssertionError: If the car is stopped, it cannot move.
        """
        assert not self.is_stopped(), "Car is stopped, cannot move"
        #self.set_waiting_time(0)
        if self.direction == CarActions.UP:
            self.y -= Car.SPEED
        elif self.direction == CarActions.DOWN:
            self.y += Car.SPEED
        elif self.direction == CarActions.LEFT:
            self.x -= Car.SPEED
        elif self.direction == CarActions.RIGHT:
            self.x += Car.SPEED

    def draw(self):
        """
        Draw the car on the window.
        """
        pygame.draw.rect(self.window, self.color, self._generate_car_rect())

        self._draw_turn_signal()
        self._draw_waiting_time()

    def _generate_car_rect(self):
        """
        Generate the rectangle representing the car.
        """
        rect = pygame.Rect(
            self.x, 
            self.y,
            Car.WIDTH if self.direction in [CarActions.UP, CarActions.DOWN] else Car.LENGTH, 
            Car.LENGTH if self.direction in [CarActions.UP, CarActions.DOWN] else Car.WIDTH
        )
        return rect

    def _draw_turn_signal(self):
        """
        Draws the turn signal blinker of the car.
        """
        TURN_SIGNAL_BLINK_INTERVAL = 1000
        TURN_SIGNAL_COLOR = (255, 85, 0)

        if self.turn_right and pygame.time.get_ticks() // TURN_SIGNAL_BLINK_INTERVAL % 2 == 0:
            points = self._calculate_turn_signal_points()
            pygame.draw.polygon(self.window, TURN_SIGNAL_COLOR, points) 

    def _calculate_turn_signal_points(self):
        """
        Calculate the coordinates of the turn signal blinker.

        Returns:
            list: The list of coordinates of the turn signal blinker.
        """
        if self.direction == CarActions.UP:
            return [(self.x + Car.WIDTH, self.y), (self.x + Car.WIDTH, self.y + 10), (self.x + Car.WIDTH + 5, self.y - 5), (self.x + Car.WIDTH + 5, self.y + 15)]
        elif self.direction == CarActions.DOWN:
            return [(self.x, self.y + Car.LENGTH), (self.x, self.y + Car.LENGTH - 10), (self.x - 5, self.y + Car.LENGTH + 5), (self.x - 5, self.y + Car.LENGTH - 15)]
        elif self.direction == CarActions.LEFT:
            return [(self.x, self.y), (self.x + 10, self.y), (self.x - 5, self.y - 5), (self.x + 15, self.y - 5)]
        else:  # self.direction == 'right'
            return [(self.x + Car.LENGTH, self.y + Car.WIDTH), (self.x + Car.LENGTH - 10, self.y + Car.WIDTH ), (self.x + Car.LENGTH + 5, self.y + Car.WIDTH + 5), (self.x + Car.LENGTH - 15, self.y + Car.WIDTH + 5)]

    def _draw_waiting_time(self):
        """
        Draws the waiting time of the car, displayed in the top-left corner of the car.
        """
        font = pygame.font.Font(None, 20)   # font size for waiting time
        text = font.render(str(self.get_waiting_time() // 30), True, (255, 255, 255))
        text = pygame.transform.rotate(text, 90)
        self.window.blit(text, (self.x + 5, self.y + 5))

    def can_move(self, other_cars: list) -> bool:
        """
        Check if the car can move based on the other cars on the road.

        Parameters:
            other_cars (list): A list of other cars on the road.

        Returns:
            bool: True if the car can move, False otherwise.
        """
        for other_car in other_cars:
            if other_car.isStopped:
                if self.direction == other_car.direction == CarActions.UP and other_car.y + Car.LENGTH + 4 <= self.y <= other_car.y + Car.LENGTH + 6:
                    return False
                elif self.direction == other_car.direction == CarActions.DOWN and other_car.y - Car.LENGTH - 6 <= self.y <= other_car.y - Car.LENGTH - 4:
                    return False
                elif self.direction == other_car.direction == CarActions.LEFT and other_car.x + Car.LENGTH + 4 <= self.x <= other_car.x + Car.LENGTH + 6:
                    return False
                elif self.direction == other_car.direction == CarActions.RIGHT and other_car.x - Car.LENGTH - 6 <= self.x <= other_car.x - Car.LENGTH - 4:
                    return False
        return True

    def turn_or_straight(self):
        """
        Turn the car right if the turn_right attribute is True, otherwise move straight.
        """
        if self.turn_right:
            if self.direction == CarActions.UP and self.y <= self.window_height // 2:
                self.direction = CarActions.RIGHT
                self.x += Car.LENGTH // 2
                self.y = self.window_height // 2 + 5
                self.turn_right = False

            elif self.direction == CarActions.DOWN and self.y + Car.LENGTH >= self.window_height // 2:
                self.direction = CarActions.LEFT
                self.x -= Car.LENGTH // 2
                self.y = self.window_height // 2 - 20 - 4
                self.turn_right = False

            elif self.direction == CarActions.LEFT and self.x <= self.window_width // 2:
                self.direction = CarActions.UP
                self.x = self.window_width // 2 + 5
                self.y -= Car.LENGTH // 2
                self.turn_right = False

            elif self.direction == CarActions.RIGHT and self.x + Car.LENGTH >= self.window_width // 2:
                self.direction = CarActions.DOWN
                self.x = self.window_width // 2 - 20 - 4
                self.y += Car.LENGTH // 2
                self.turn_right = False