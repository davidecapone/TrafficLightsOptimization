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
                 traffic_mdp: TrafficMDP = None):
        
        assert len(ambient_images_path) == 4, "Ambient must have 4 images"
        assert window_size[0] > 0 and window_size[1] > 0, "Window size must be greater than 0"

        pygame.init()
        pygame.display.set_caption(name)

        self.window = pygame.display.set_mode(window_size)
        self.environment = Environment(self.window, self._load_images(ambient_images_path))
        self.car_manager = CarManager(self.window)
        self.stoplight_manager = StoplightManager()

        if audio_effect_path:
            self._load_audio(audio_effect_path, volume=0.2)

        if traffic_mdp:
            self.traffic_mdp = traffic_mdp

    def _load_images(self, ambient_images_path: list) -> None:
        return [pygame.image.load(image_path) for image_path in ambient_images_path]

    def _load_audio(self, audio_effect_path: str, volume: float) -> None:
        pygame.mixer.init()
        pygame.mixer.music.load(audio_effect_path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)

    def run(self) -> None:
        prev_time = 0
        clock = pygame.time.Clock()

        car_frequency = 1.5 # Add a car every 1.5 seconds
        max_time = 120 # Stop the simulation after 120 seconds
        frame = 0
        seconds_passed = 0

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
                    return

            time = round(pygame.time.get_ticks() // 1000, 1)

            if time != prev_time and time % car_frequency == 0: # Add a car every 1.5 seconds

                """
                ???
                """
                if time < 30:
                    self.car_manager.add_car(direction = [CarActions.UP, CarActions.DOWN])
                elif 60 < time < 90:
                    self.car_manager.add_car(direction = [CarActions.LEFT, CarActions.RIGHT])
                else:
                    self.car_manager.add_car()
                    
                prev_time = time

            if time >= max_time: # Stop the simulation after 120 seconds
                pygame.quit()
                return
            
            frame += 1
            seconds_passed = frame // 30


            if ((self.stoplight_manager.get_ns_color() == TrafficLightColor.GREEN.value or self.stoplight_manager.get_ew_color() == TrafficLightColor.GREEN.value) and seconds_passed >= 5):

                state = 'NS' if self.stoplight_manager.get_ns_color() == TrafficLightColor.GREEN.value else 'EW'
                self.traffic_mdp.policy_iteration(self.car_manager.get_cars())
                action = self.traffic_mdp.get_action(state)
                print(action)

                if action == 'change':
                    self.stoplight_manager.stoplight.switch_yellow()
                    seconds_passed = 0
                    frame = 0

            self.car_manager.update_cars(self.stoplight_manager.stoplight)
            self.car_manager.draw_cars()
            pygame.display.update()