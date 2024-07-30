from entities.car import Car
from entities.stoplight import Stoplight
from entities.car_actions import CarActions
from entities.colors import TrafficLightColor

class CarManager:
    """
    Manages the cars in the simulation.

    Attributes:
    - window: pygame window
    - cars: list of Car objects
    - cumulative_waiting_time: int representing the total waiting time of all cars that have stopped at the intersection
    - n_stopped_cars: int representing the number of cars that have stopped at the intersection
    - queue_lenghts: dict with the number of cars stopped in each direction
    - queues: list of the queue lengths for each direction
    """
    def __init__(self, window):
            self.window = window

            self.cars = []
            
            self.cumulative_waiting_time = 0
            self.n_stopped_cars = 0
            self.queue_lenghts = {
                CarActions.UP:0, 
                CarActions.DOWN:0, 
                CarActions.LEFT:0, 
                CarActions.RIGHT:0
            }

            self.queues = []

    def add_car(self, direction:list = None) -> None:
        """
        Add a car to the simulation.

        Parameters:
        - direction: list of directions that the car can take
        """
        self.cars.append(
            Car(self.window, direction=direction) if direction else Car(self.window)
        )

    def get_cars(self) -> list:
        return self.cars

    def get_n_stopped_cars(self) -> int:
        return self.n_stopped_cars

    def get_stopped_cars(self, directions:list) -> list:
        """
        Get the cars that are stopped and are in the specified directions.
        
        Parameters:
        - directions: list of directions to filter the cars

        Returns:
        - list: list of Car objects that are stopped and are in the specified directions
        """
        return [car for car in self.cars if car.direction in directions and car.is_stopped()]

    def update_cars(self, stoplight:Stoplight) -> None:
        """
        Update the cars' positions and states.

        Parameters:
        - stoplight: Stoplight object
        """
        for car in self.cars:
            self.update_car(car, stoplight) 


    def update_car(self, car, stoplight:Stoplight) -> None:
        """
        Update the car's position and state.

        Parameters:
        - car: Car object
        - stoplight: Stoplight object
        """
        # Check if the car is stopped
        if car.is_stopped():
            # Increase the waiting time of the car
            car.increase_waiting_time()
            self.cumulative_waiting_time += 1

            car_direction = car.get_direction()

            # Check if the stoplight is green and the car can move
            if ((car_direction in [CarActions.UP, CarActions.DOWN] and stoplight.color_NS == TrafficLightColor.GREEN.value) or
                (car_direction in [CarActions.LEFT, CarActions.RIGHT] and stoplight.color_EW == TrafficLightColor.GREEN.value)):
                
                car.set_stopped(False)
                
                if self.queue_lenghts[car.get_direction()] != 0:
                    self.queues.append(self.queue_lenghts[car.get_direction()])
                    self.queue_lenghts[car.get_direction()] = 0

                car.move()

        # Check if the car is at the intersection and should stop or if the car cannot move
        elif (self.is_at_intersection(car) and self.should_stop(car, stoplight)) or not car.can_move(self.cars):
            car.set_stopped(True)
            # Increase the counters for the stopped cars and the queue lengths
            self.n_stopped_cars += 1
            self.queue_lenghts[car.get_direction()] += 1

        # Move the car
        else:
            car.turn_or_straight()
            car.move()

        # Remove the car if it is out of the window
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


    