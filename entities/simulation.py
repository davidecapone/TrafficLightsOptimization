import pygame
from entities.environment import Environment
from entities.car_manager import CarManager
from entities.stoplight_manager import StoplightManager
from model import TrafficMDP
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

        # Statistics
        self.cumulative_waiting_times = {'mdp': [0], 'ft': [0]}
        self.queue_lengths = {'mdp': [], 'ft': []}
        self.n_stopped_cars = {'mdp': 0, 'ft': 0}

        self.car_spwan_policy = car_spwan_policy

        # Calculate the intervals
        self.intervals = self.calculate_intervals(
            simulation_duration, 
            self.car_spwan_policy
        )

        print(self.intervals)

    def run(self, mode:str) -> None:

        assert mode in ['mdp', 'ft'], "Mode must be either 'mdp' or 'ft'"

        if mode == 'mdp':
            mdp = TrafficMDP()

        prev_time = 0
        clock = pygame.time.Clock()

        frame = 0
        total_seconds = 0
        total_frames = 0

        start_ticks = pygame.time.get_ticks()  # Get the start ticks

        # Temporary statistics
        cumulative_waiting_time = 0

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
                    pygame.quit()
                    print("Simulation ended.")
                    return

            current_ticks = pygame.time.get_ticks()
            elapsed_ticks = current_ticks - start_ticks
            total_seconds = elapsed_ticks // 1000

            # Determine which interval we are in
            interval = self.determine_current_interval(total_seconds, self.intervals)

            if total_seconds != prev_time and total_seconds % self.car_spawn_frequency == 0:  # Add a car every 'spawn_frequency' seconds
                print(f"Time: {total_seconds}, Interval: {interval}")
                if interval == 'up_down':
                    self.car_manager.add_car(direction=[CarActions.UP, CarActions.DOWN])
                if interval == 'left_right':
                    self.car_manager.add_car(direction=[CarActions.LEFT, CarActions.RIGHT])
                elif interval == 'all_directions':
                    self.car_manager.add_car()

                #if total_seconds % 1 == 0:
                #    self.cumulative_waiting_times[test].append(cumulative_waiting_time // 30)


                if mode == 'mdp':

                    if ((self.stoplight_manager.get_ns_color() == TrafficLightColor.GREEN.value or 
                        self.stoplight_manager.get_ew_color() == TrafficLightColor.GREEN.value) and 
                        total_seconds % 7 == 0 and 
                        int(total_seconds) != int(prev_time)):

                        state = 'NS' if self.stoplight_manager.get_ns_color() == TrafficLightColor.GREEN.value else 'EW'
                        mdp.policy_iteration(self.car_manager.get_cars())
                        action = mdp.get_action(state)
                        # print(f"State {state}, Action: {action}")

                        if action == 'change':
                            self.stoplight_manager.stoplight.switch_yellow()

                elif mode == 'ft':
                    if self.stoplight_manager.stoplight.time_green >= 300:
                        self.stoplight_manager.stoplight.switch_yellow()

                prev_time = total_seconds

            # Stop the simulation after 'simulation_duration' seconds
            if total_seconds >= self.simulation_duration: 
                pygame.quit()
                print("Simulation ended.")
                return

            total_frames += 1

            self.car_manager.update_cars(self.stoplight_manager.stoplight)
            self.car_manager.draw_cars()
            pygame.display.update()

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

