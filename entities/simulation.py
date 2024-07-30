import pygame
from entities.environment import Environment
from entities.car_manager import CarManager
from entities.stoplight_manager import StoplightManager
from model.TrafficMDP import TrafficMDP
from entities.colors import TrafficLightColor
from entities.car_actions import CarActions

class Simulation:
    """
    Defines the simulation of the traffic light.

    Attributes:
    - spawning_rules: list of tuples with the duration of each interval
    - cars_per_second: float representing the number of cars that spawn per second
    - audio: bool representing if the audio is enabled
    - simulation_duration: int representing the total duration of the simulation
    - intervals: list of tuples with the duration of each interval
    """
    def __init__(self, spawning_rules:list, cars_per_second:float = 1, audio:bool = False) -> None:
        self.car_spawn_frequency = cars_per_second
        self.car_spwan_policy = spawning_rules
        self.simulation_duration = self._get_total_time(spawning_rules)
        self.intervals = spawning_rules
        self.audio = audio

        print(f"Simulation duration: {self.simulation_duration} seconds")

    def _get_total_time(self, spwan_policy: list) -> int:
        """
        Returns the simulation duration based on the intervals defined.

        Parameters:
        - spawn_policy: list of tuples with the duration of each interval

        Returns:
        - total time in seconds
        """
        return (sum(duration for _, duration in spwan_policy))
    

    def run(self, mode:str, save_stats:bool = False):
        """
        Run the simulation.

        Parameters:
        - mode: str representing the mode of the simulation (pi, vi, ft)
        - save_stats: bool representing if the stats should be saved
        """
        assert mode in ['pi', 'vi', 'ft'], "Mode must be either 'pi', 'vi or 'ft'"

        # Cumulative waiting times will measure the total waiting time of all cars that have stopped at the intersection
        self.cumulative_waiting_times = [0]
        # Stopped cars will store all the cars that have stopped at the intersection
        self.n_stopped_cars = 0

        # Initialize the environment
        self.environment = Environment(
            window_size=(1000, 1000),
            name=f'Simulation with {mode} mode',
            audio=self.audio
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
                    # Save the stats if the user wants to
                    self.save_stats(mode) if save_stats else None
                    return

            # Calculate the elapsed time
            current_ticks = pygame.time.get_ticks()
            elapsed_ticks = current_ticks - start_ticks
            total_seconds = round(elapsed_ticks / 1000, 1) # Round to 1 decimal place, so that it is possible to spawn cars every tenth of a second.

            # Determine which interval we are in
            interval = self.determine_current_interval(int(total_seconds), self.intervals)

            # Stop the simulation after 'simulation_duration' seconds
            if total_seconds >= self.simulation_duration: 
                self.environment.close()
                # Save the stats if the user wants to
                self.save_stats(mode) if save_stats else None
                return
        
            # Add a car every car_spawn_frequency seconds
            if total_seconds % self.car_spawn_frequency == 0 and total_seconds != prev_time:
                self.add_cars_based_on_interval(interval)

            # Define the mode of the simulation
            match mode:
                # Case Policy Iteration
                case 'pi':
                    # If the stoplight has been green for 5 seconds, call the policy iteration algorithm
                    if self.stoplight_manager.stoplight.time_green//30 >= 15 and int(total_seconds) != int(prev_time):
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
                    if self.stoplight_manager.stoplight.time_green//30 >= 15 and int(total_seconds) != int(prev_time):
                        # Define the state as NS if the stoplight ns is green, otherwise EW
                        state = 'NS' if self.stoplight_manager.get_ns_color() == TrafficLightColor.GREEN.value else 'EW'
                        # Get the action from the policy iteration algorithm
                        action = mdp.value_iteration(self.car_manager.get_cars(), state)
                        # Switch the stoplight to yellow if the action is 'change'
                        self.stoplight_manager.stoplight.switch_yellow() if action == 'change' else None
                # Case Fixed Time
                case 'ft':
                    # Switch the stoplight to yellow if the stoplight has been green for 7 seconds
                    self.stoplight_manager.stoplight.switch_yellow() if self.stoplight_manager.stoplight.time_green//30 >= 20 else None
                # Default case
                case _:
                    raise ValueError(f"Mode: {mode} not yet implemented")

            # Update the cars
            self.car_manager.update_cars(self.stoplight_manager.stoplight)

            # Update the cumulative waiting times every second
            if int(total_seconds) != int(prev_time):
                self.cumulative_waiting_times.append(self.car_manager.cumulative_waiting_time//30) 

            # Update the previous time (to check if a second has passed)
            prev_time = total_seconds

            # Update the stopped cars
            self.n_stopped_cars = self.car_manager.get_n_stopped_cars()   

            # Draw the cars and the info panel
            self.environment.draw_cars(self.car_manager)
            self.environment.draw_info_panel(
                int(total_seconds), 
                interval, 
                self.cumulative_waiting_times[-1],
                mode
            )
            self.environment.update()

    def calculate_intervals(self, total_time:int, proportions:list) -> list:
        """
        Calculate the intervals based on the total time and the proportions of each interval.

        Parameters:
        - total_time: int representing the total time of the simulation
        - proportions: list of tuples with the proportion of each interval

        Returns:
        - list of tuples with the name of the interval and the duration
        """
        total_proportion = sum(proportion for name, proportion in proportions)
        intervals = [(name, int((proportion / total_proportion) * total_time)) for name, proportion in proportions]
        return intervals

    def determine_current_interval(self, total_seconds:int, intervals:list):
        """
        Determine the current interval based on the total seconds and the intervals defined.

        Parameters:
        - total_seconds: int representing the total seconds of the simulation
        - intervals: list of tuples with the name of the interval and the duration

        Returns:
        - str: the name of the current interval
        - None: if the interval is not found
        """
        total_duration = sum(duration for name, duration in intervals)
        cycle_time = total_seconds % total_duration

        cumulative_time = 0
        for interval, duration in intervals:
            cumulative_time += duration
            if cycle_time < cumulative_time:
                return interval
        return None

    def add_cars_based_on_interval(self, interval:str) -> None:
        """
        Add cars based on the interval defined.

        Parameters:
        - interval: str representing the interval of the simulation

        Returns:
        - None
        """
        if interval == 'up_down':
            self.car_manager.add_car(direction=[CarActions.UP, CarActions.DOWN])
        elif interval == 'left_right':
            self.car_manager.add_car(direction=[CarActions.LEFT, CarActions.RIGHT])
        elif interval == 'all_directions':
            self.car_manager.add_car()
        else:
            return

    def to_disk(self, data, path:str):
        """
        Save the data to disk.

        Parameters:
        - data: data to save
        - path: str representing the path to save the data
        """
        with open(path, 'w') as f:
            if isinstance(data, list):
                for item in data:
                    f.write("%s,\n"%(item))
            else:
                f.write(str(data))

    def save_stats(self, mode:str):
        """
        Save the stats of the simulation to disk.

        Parameters:
        - mode: str representing the mode of the simulation
        """
        self.to_disk(self.cumulative_waiting_times, f'./data/cumulative_waiting_times_{mode}.csv')
        self.to_disk(self.n_stopped_cars, f'./data/stopped_cars_{mode}.csv')
        self.to_disk(self.car_manager.queues, f'./data/queue_lengths_{mode}.csv')
        

