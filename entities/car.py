import random
import pygame

# Constants
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 1000
CAR_SPEED = 2
CAR_WIDTH = 20
CAR_LENGTH = 40
TURN_SIGNAL_BLINK_INTERVAL = 1000
WAITING_TIME_FONT_SIZE = 20
TURN_SIGNAL_COLOR = (255, 85, 0)

class Car:
    def __init__(self, x, y, direction, window_width=WINDOW_WIDTH, window_height=WINDOW_HEIGHT):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = CAR_SPEED
        self.width = CAR_WIDTH
        self.length = CAR_LENGTH
        self.stopped = False
        self.color = self._generate_random_color()
        self.turn_right = random.choice([False, True])
        self.waiting_time = 0

        self.window_width = window_width
        self.window_height = window_height

    def _generate_random_color(self):
        return (random.randint(1, 255), random.randint(1, 255), random.randint(1, 255))

    def move(self):
        if not self.stopped:
            if self.direction == 'up':
                self.y -= self.speed
            elif self.direction == 'down':
                self.y += self.speed
            elif self.direction == 'left':
                self.x -= self.speed
            elif self.direction == 'right':
                self.x += self.speed

    def draw(self, win):
        self._draw_car_body(win)
        self._draw_turn_signal(win)
        self._draw_waiting_time(win)

    def _draw_car_body(self, win):
        rect = pygame.Rect(self.x, self.y, self.width if self.direction in ['up', 'down'] else self.length, self.length if self.direction in ['up', 'down'] else self.width)
        pygame.draw.rect(win, self.color, rect)

    def _draw_turn_signal(self, win):
        if self.turn_right and pygame.time.get_ticks() // TURN_SIGNAL_BLINK_INTERVAL % 2 == 0:
            points = self._calculate_turn_signal_points()
            pygame.draw.polygon(win, TURN_SIGNAL_COLOR, points)

    def _calculate_turn_signal_points(self):
        if self.direction == 'up':
            return [(self.x + self.width, self.y), (self.x + self.width, self.y + 10), (self.x + self.width + 5, self.y - 5), (self.x + self.width + 5, self.y + 15)]
        elif self.direction == 'down':
            return [(self.x, self.y + self.length), (self.x, self.y + self.length - 10), (self.x - 5, self.y + self.length + 5), (self.x - 5, self.y + self.length - 15)]
        elif self.direction == 'left':
            return [(self.x, self.y), (self.x + 10, self.y), (self.x - 5, self.y - 5), (self.x + 15, self.y - 5)]
        else:  # self.direction == 'right'
            return [(self.x + self.length, self.y + self.width // 2), (self.x + self.length - 10, self.y + self.width // 2), (self.x + self.length + 5, self.y + self.width // 2 - 5), (self.x + self.length + 5, self.y + self.width // 2 + 5)]

    def _draw_waiting_time(self, win):
        font = pygame.font.Font(None, WAITING_TIME_FONT_SIZE)
        text = font.render(str(self.waiting_time // 30), True, (255, 255, 255))
        text = pygame.transform.rotate(text, 90)
        win.blit(text, (self.x + 5, self.y + 5))

    def stop(self):
        self.stopped = True

    def can_move(self, other_cars):
        for other_car in other_cars:
            if other_car.stopped:
                if self.direction == other_car.direction == 'up' and other_car.y + other_car.length + 4 <= self.y <= other_car.y + other_car.length + 6:
                    return False
                elif self.direction == other_car.direction == 'down' and other_car.y - self.length - 6 <= self.y <= other_car.y - self.length - 4:
                    return False
                elif self.direction == other_car.direction == 'left' and other_car.x + other_car.length + 4 <= self.x <= other_car.x + other_car.length + 6:
                    return False
                elif self.direction == other_car.direction == 'right' and other_car.x - self.length - 6 <= self.x <= other_car.x - self.length - 4:
                    return False
        return True

    def turn_or_straight(self):
        if self.turn_right:
            if self.direction == 'up' and self.y <= self.window_height // 2:
                self.direction = 'right'
                self.x += self.length // 2
                self.y = self.window_height // 2 + 5
                self.turn_right = False
            elif self.direction == 'down' and self.y + self.length >= self.window_height // 2:
                self.direction = 'left'
                self.x -= self.length // 2
                self.y = self.window_height // 2 - 20 - 4
                self.turn_right = False
            elif self.direction == 'left' and self.x <= self.window_width // 2:
                self.direction = 'up'
                self.x = self.window_width // 2 + 5
                self.y -= self.length // 2
                self.turn_right = False
            elif self.direction == 'right' and self.x + self.length >= self.window_width // 2:
                self.direction = 'down'
                self.x = self.window_width // 2 - 20 - 4
                self.y += self.length // 2
                self.turn_right = False