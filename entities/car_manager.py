from entities.car import Car
from entities.stoplight import Stoplight
from entities.car_actions import CarActions
from entities.colors import TrafficLightColor

class CarManager:
    """
    Manages the cars in the simulation.
    """
    def __init__(self, window):
            self.window = window
            self.cars = []

    def add_car(self, direction = None):
        self.cars.append(
            Car(self.window, direction=direction) if direction else Car(self.window)
        )

    def get_cars(self) -> list:
        return self.cars

    def get_stopped_cars(self, directions: list) -> list:
        """
        Get the cars that are stopped and are in the specified directions.
        
        Parameters:
        - directions: list of directions to filter the cars
        """
        return [car for car in self.cars if car.direction in directions and car.is_stopped()]

    def update_cars(self, stoplight):
        for car in self.cars:
            self.update_car(car, stoplight)

    def update_car(self, car, stoplight) -> None:
        """
        Update the car's position and state.

        Parameters:
        - car: Car object
        - stoplight: Stoplight object
        """
        if car.is_stopped():
            car.increase_waiting_time()
            car_direction = car.get_direction()

            if ((car_direction in [CarActions.UP, CarActions.DOWN] and stoplight.color_NS == TrafficLightColor.GREEN.value) or
                (car_direction in [CarActions.LEFT, CarActions.RIGHT] and stoplight.color_EW == TrafficLightColor.GREEN.value)):
                car.set_stopped(False)
                car.move()

        elif (self.is_at_intersection(car) and self.should_stop(car, stoplight)) or not car.can_move(self.cars):
            car.set_stopped(True)
        else:
            car.turn_or_straight()
            car.move()

        if car.is_out_of_window():
            self.cars.remove(car)


    def should_stop(self, car:Car, stoplight:Stoplight) -> bool:
        """
        Check the stoplight color and the car direction to determine if the car should stop.
        
        Parameters:
        - car: Car object
        - stoplight: Stoplight object
        
        Returns:
        - boolean: True if the car should stop, False otherwise
        """
        car_direction = car.get_direction()
    
        return (
            (car_direction in [CarActions.UP, CarActions.DOWN] and stoplight.color_NS in [TrafficLightColor.RED.value, TrafficLightColor.YELLOW.value]) or
            (car_direction in [CarActions.LEFT, CarActions.RIGHT] and stoplight.color_EW in [TrafficLightColor.RED.value, TrafficLightColor.YELLOW.value])
        )

    def is_at_intersection(self, car:Car) -> bool:
        """
        Check if the car is at the intersection.

        Parameters:
        - car: Car object

        Returns:
        - boolean: True if the car is at the intersection, False otherwise
        """
        car_direction = car.get_direction()
        x, y = car.get_position()
        mid_x, mid_y = self.window.get_width() // 2, self.window.get_height() // 2
        offset = 50

        return (
            (car_direction == CarActions.UP and (mid_y + offset <= y <= mid_y + offset + 3)) or
            (car_direction == CarActions.DOWN and (mid_y - offset - 3 <= y + Car.LENGTH <= mid_y - offset)) or
            (car_direction == CarActions.LEFT and (mid_x + offset <= x <= mid_x + offset + 3)) or
            (car_direction == CarActions.RIGHT and (mid_x - offset - 3 <= x + Car.LENGTH <= mid_x - offset))
        )


    