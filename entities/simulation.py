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

        # Simulation parameters
        self.name = name
        self.car_spawn_frequency = car_spawn_frequency
        self.simulation_duration = simulation_duration
        self.car_spwan_policy = car_spwan_policy

        # Calculate the intervals
        self.intervals = self.calculate_intervals(simulation_duration, self.car_spwan_policy)


    def run(self, mode:str):

        assert mode in ['pi', 'vi', 'ft'], "Mode must be either 'pi', 'vi or 'ft'"

        # Cumulative waiting times will measure the total waiting time of all cars that have stopped at the intersection
        self.cumulative_waiting_times = dict()
        # Stopped cars will store all the cars that have stopped at the intersection
        self.n_stopped_cars = dict()

        # Initialize the environment
        self.environment = Environment(
            window_size=(1000, 1000),
            name=self.name,
            audio=False
        )

        self.window = self.environment.get_window()

        self.car_manager = CarManager(self.window)
        self.stoplight_manager = StoplightManager()

        if mode == 'pi' or mode == 'vi':
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
                    self.save_stats(mode)
                    return

            # Calculate the elapsed time
            current_ticks = pygame.time.get_ticks()
            elapsed_ticks = current_ticks - start_ticks
            total_seconds = round(elapsed_ticks / 1000, 1)

            # Determine which interval we are in
            interval = self.determine_current_interval(int(total_seconds), self.intervals)

            # Stop the simulation after 'simulation_duration' seconds
            if total_seconds >= self.simulation_duration: 
                self.environment.close()
                self.save_stats(mode)
                return
        
            # Add a car every car_spawn_frequency seconds
            if total_seconds % self.car_spawn_frequency == 0 and total_seconds != prev_time:
                self.add_cars_based_on_interval(interval)

            # Define the mode of the simulation
            match mode:
                # Case Policy Iteration
                case 'pi':
                    # If the stoplight has been green for 5 seconds, call the policy iteration algorithm
                    if self.stoplight_manager.stoplight.time_green//30 >= 5 and int(total_seconds) != int(prev_time):
                        # Define the state as NS if the stoplight ns is green, otherwise EW
                        state = 'NS' if self.stoplight_manager.get_ns_color() == TrafficLightColor.GREEN.value else 'EW'
                        # Get the action from the policy iteration algorithm
                        mdp.policy_iteration(self.car_manager.get_cars())
                        action = mdp.get_action(state)
                        # Switch the stoplight to yellow if the action is 'change'
                        self.stoplight_manager.stoplight.switch_yellow() if action == 'change' else None
                # Case Value Iteration
                case 'vi':
                    # If the stoplight has been green for 5 seconds, call the value iteration algorithm
                    if self.stoplight_manager.stoplight.time_green//30 >= 5 and int(total_seconds) != int(prev_time):
                        # Define the state as NS if the stoplight ns is green, otherwise EW
                        state = 'NS' if self.stoplight_manager.get_ns_color() == TrafficLightColor.GREEN.value else 'EW'
                        # Get the action from the policy iteration algorithm
                        action = mdp.value_iteration(self.car_manager.get_cars(), state)
                        # Switch the stoplight to yellow if the action is 'change'
                        self.stoplight_manager.stoplight.switch_yellow() if action == 'change' else None
                # Case Fixed Time
                case 'ft':
                    # Switch the stoplight to yellow if the stoplight has been green for 5 seconds
                    self.stoplight_manager.stoplight.switch_yellow() if self.stoplight_manager.stoplight.time_green//30 >= 5 else None
                # Default case
                case _:
                    raise ValueError(f"Mode: {mode} not yet implemented")
            
            # Update the previous time to avoid adding cars every frame
            prev_time = total_seconds

            # Update the cars
            self.car_manager.update_cars(self.stoplight_manager.stoplight)

            # Update the cumulative waiting times
            self.cumulative_waiting_times[total_seconds] = self.car_manager.cumulative_waiting_time//30  

            # Update the stopped cars
            self.n_stopped_cars['stopped_cars'] = self.car_manager.get_n_stopped_cars()      

            # Draw the cars and the info panel
            self.environment.draw_cars(self.car_manager)
            self.environment.draw_info_panel(
                self.car_manager, 
                total_seconds, 
                interval, 
                self.cumulative_waiting_times[total_seconds],
                mode
            )
            self.environment.update()

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

    def to_disk(self, data, path):
        with open(path, 'w') as f:
            for key in data.keys():
                f.write("%s,%s\n"%(key,data[key]))

    def save_list(self, data, path):
        with open(path, 'w') as f:
            for item in data:
                f.write("%s\n"%item)

    def save_stats(self, mode:str):
        #self.to_disk(self.cumulative_waiting_times, f'./data/cumulative_waitingtimes_{mode}.csv')
        #self.to_disk(self.n_stopped_cars, f'./data/stopped_cars_{mode}.csv')
        #self.save_list(self.car_manager.queues, f'./data/queue_lengths_{mode}.csv')
        pass

