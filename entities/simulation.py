import pygame
from entities.environment import Environment
from entities.car_manager import CarManager
from entities.stoplight_manager import StoplightManager
from model import TrafficMDP
from entities.colors import TrafficLightColor
from entities.car_actions import CarActions

class Simulation:
    """
    Defines the simulation of the traffic light.
    """
    def __init__(self, 
                 name: str, 
                 ambient_images_path: list, 
                 window_size: tuple = (1000, 1000), 
                 audio_effect_path: str = None,
                 car_spawn_frequency: float = 1.5,
                 max_simulation_time: float = 120) -> None:
        
        assert len(ambient_images_path) == 4, "Ambient must have 4 images"
        assert window_size[0] > 0 and window_size[1] > 0, "Window size must be greater than 0"

        pygame.init()
        pygame.display.set_caption(name)

        self.window = pygame.display.set_mode(window_size)
        self.environment = Environment(self.window, self._load_images(ambient_images_path))
        self.car_manager = CarManager(self.window)
        self.stoplight_manager = StoplightManager()

        self.car_spawn_frequency = car_spawn_frequency
        self.max_simulation_time = max_simulation_time

        # Statistics
        self.cumulative_waiting_times = {'mdp': [0], 'ft': [0]}
        self.queue_lengths = {'mdp': [], 'ft': []}
        self.n_stopped_cars = {'mdp': 0, 'ft': 0}

        if audio_effect_path:
            self._load_audio(audio_effect_path, volume=0.2)


    def _load_images(self, ambient_images_path: list) -> None:
        return [pygame.image.load(image_path) for image_path in ambient_images_path]

    def _load_audio(self, audio_effect_path: str, volume: float) -> None:
        pygame.mixer.init()
        pygame.mixer.music.load(audio_effect_path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)

    def run(self, mdp, test='mdp') -> None:
        prev_time = 0
        clock = pygame.time.Clock()

        frame = 0
        seconds_passed = 0

        # Temporary statistics
        queued_cars = {'up': 0, 'down': 0, 'left': 0, 'right': 0}
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

            time = round(pygame.time.get_ticks() / 1000, 1)

            if time != prev_time and time % self.car_spawn_frequency == 0: # Add a car every 'spawn_frequency' seconds

                """
                TODO: Da decidere i times
                ciao :) ti ho aggiunto un esempio di times insieme alle statistiche, modifica i times come meglio credi!
                ricordati che entrambi i test devono avere la stessa simulazione
                al momento è così:
                Ogni test dura 5 minuti
                - primo minuto: up-down
                - secondo minuto: tutte le direzioni
                - terzo minuto: niente
                - quarto minuto: left-right
                - quinto minuto: tutte le direzioni
                """
                if time < 60 or (300 < time and time < 360):
                    # Add a car that can go up or down
                    self.car_manager.add_car(direction = [CarActions.UP, CarActions.DOWN])
                elif 180 < time and time < 240 or (480 < time and time < 540):
                    # Add a car that can go left or right
                    self.car_manager.add_car(direction = [CarActions.LEFT, CarActions.RIGHT])
                elif 60 < time and time < 120 or (240 < time and time < 300) or (360 < time and time < 420) or (540 < time and time < 600):
                    # Add a car that can go in all directions
                    self.car_manager.add_car()
                else:
                    # No cars
                    continue

                if time % 1 == 0:
                    self.cumulative_waiting_times[test].append(cumulative_waiting_time//30)

                prev_time = time

            # Stop the simulation after 'max_simulation_time' seconds
            if time >= self.max_simulation_time: 
                pygame.quit()
                print("Simulation ended.")
                return
            
            
            frame += 1
            seconds_passed = frame // 30


            if ((self.stoplight_manager.get_ns_color() == TrafficLightColor.GREEN.value or self.stoplight_manager.get_ew_color() == TrafficLightColor.GREEN.value) and seconds_passed >= 5):

                state = 'NS' if self.stoplight_manager.get_ns_color() == TrafficLightColor.GREEN.value else 'EW'
                mdp.policy_iteration(self.car_manager.get_cars())
                action = mdp.get_action(state)
                print(f"State {state}, Action: {action}")

                if action == 'change':
                    self.stoplight_manager.stoplight.switch_yellow()
                    seconds_passed = 0
                    frame = 0

            self.car_manager.update_cars(self.stoplight_manager.stoplight)
            self.car_manager.draw_cars()
            pygame.display.update()