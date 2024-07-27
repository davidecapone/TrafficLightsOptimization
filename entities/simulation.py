import pygame
from entities.environment import Environment
from entities.car_manager import CarManager
from entities.stoplight_manager import StoplightManager
from model.TrafficMDP import TrafficMDP
from entities.colors import TrafficLightColor
from entities.car_actions import CarActions
import time

class Simulation:
    """
    Defines the simulation of the traffic light.
    """
    def __init__(self, 
                 name: str, 
                 car_spwan_policy: list,
                 car_spawn_frequency: float = 1.5,
                 simulation_duration: float = 120) -> None:
        
        # Initialize the environment, car manager and stoplight manager
        self.environment = Environment(
            window_size=(1000, 1000),
            name=name,
            audio=False
        )

        self.window = self.environment.get_window()

        self.car_manager = CarManager(self.window)
        self.stoplight_manager = StoplightManager()

        # Simulation parameters
        self.car_spawn_frequency = car_spawn_frequency
        self.simulation_duration = simulation_duration
        self.car_spwan_policy = car_spwan_policy

        # Cumulative waiting times will measure the total waiting time of all cars that have stopped at the intersection
        self.cumulative_waiting_times = dict()

        # Calculate the intervals
        self.intervals = self.calculate_intervals(simulation_duration, self.car_spwan_policy)


    def run(self, mode:str) -> None:

        assert mode in ['mdp', 'ft'], "Mode must be either 'mdp' or 'ft'"

        if mode == 'mdp':
            mdp = TrafficMDP()

        prev_time = 0
        clock = pygame.time.Clock()
        total_seconds = 0
        start_ticks = pygame.time.get_ticks()  # Get the start ticks

        while True:
            clock.tick(30)

            # Draw the environment:
            self.environment.draw()
            self.stoplight_manager.draw_stoplight(self.window)

            # Update the stoplight:
            self.stoplight_manager.update_stoplight()

            # Check if the user wants to quit the game:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.environment.close()
                    return

            # Calculate the elapsed time
            current_ticks = pygame.time.get_ticks()
            elapsed_ticks = current_ticks - start_ticks
            total_seconds = elapsed_ticks // 1000

            # Determine which interval we are in
            interval = self.determine_current_interval(total_seconds, self.intervals)

            # Stop the simulation after 'simulation_duration' seconds
            if total_seconds >= self.simulation_duration: 
                self.environment.close()
                return
 
            if ((total_seconds != prev_time) and (total_seconds % self.car_spawn_frequency == 0)):
                self.add_cars_based_on_interval(interval)
                prev_time = total_seconds

            match mode:
                case 'mdp':
                    is_ns_stoplight_green = True if self.stoplight_manager.get_ns_color() == TrafficLightColor.GREEN.value else False
                    is_ew_stoplight_green = True if self.stoplight_manager.get_ew_color() == TrafficLightColor.GREEN.value else False

                    if ((is_ns_stoplight_green or is_ew_stoplight_green) and 
                        total_seconds % 7 == 0 and int(total_seconds) != int(prev_time)):

                        # Define the state as NS if the stoplight ns is green, otherwise EW
                        state = 'NS' if self.stoplight_manager.get_ns_color() == TrafficLightColor.GREEN.value else 'EW'
                        mdp.policy_iteration(self.car_manager.get_cars())
                        action = mdp.get_action(state)

                        self.stoplight_manager.stoplight.switch_yellow() if action == 'change' else None

                case 'ft':
                    self.stoplight_manager.stoplight.switch_yellow() if self.stoplight_manager.stoplight.time_green >= 300 else None

                case _:
                    raise ValueError(f"Mode: {mode} not yet implemented")


            self.car_manager.update_cars(self.stoplight_manager.stoplight)

            self.cumulative_waiting_times[total_seconds] = self.car_manager.cumulative_waiting_time//30        

            self.environment.draw_cars(self.car_manager)
            self.environment.draw_info_panel(
                self.car_manager, 
                total_seconds, 
                interval, 
                self.cumulative_waiting_times[total_seconds],
                mode
            )
            self.environment.update()

            self.to_disk(self.cumulative_waiting_times, f'./data/cumulative_waitingtimes_{mode}.csv')


    def to_disk(self, data: dict, filename: str) -> None:
        with open(filename, 'w') as f:
            for key in data.keys():
                f.write("%s,%s\n"%(key,data[key]))

    def calculate_intervals(self, total_time, proportions):
        total_proportion = sum(proportion for name, proportion in proportions)
        intervals = [(name, int((proportion / total_proportion) * total_time)) for name, proportion in proportions]
        return intervals

    def determine_current_interval(self, total_seconds, intervals):
        total_duration = sum(duration for name, duration in intervals)
        cycle_time = total_seconds % total_duration

        cumulative_time = 0
        for interval, duration in intervals:
            cumulative_time += duration
            if cycle_time < cumulative_time:
                return interval
        return None

    def add_cars_based_on_interval(self, interval):
        if interval == 'up_down':
            self.car_manager.add_car(direction=[CarActions.UP, CarActions.DOWN])
        elif interval == 'left_right':
            self.car_manager.add_car(direction=[CarActions.LEFT, CarActions.RIGHT])
        elif interval == 'all_directions':
            self.car_manager.add_car()
        else:
            return

