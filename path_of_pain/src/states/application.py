"""Module with class that controls pygame directly"""
import pygame

from path_of_pain.src.framework import const
from path_of_pain.src.states.menu import Menu


# Context for STATE PATTERN
class Application:
    """
    Class for creating pygame window, updating and drawing in it
    """
    def __init__(self):
        # Pygame config
        pygame.mixer.pre_init(22050, -16, 8, 64)
        pygame.init()
        pygame.mouse.set_visible(False)
        pygame.display.set_mode(const.RESOLUTION, pygame.FULLSCREEN)
        pygame.display.set_caption("Path of Pain")
        pygame.display.set_icon(pygame.image.load(const.IMG_PATH + "enemy.png"))

        self.state = None
        self.switched = False
        self.switch_state(Menu())
        # Joystick init
        if pygame.joystick.get_count() != 0:
            pygame.joystick.Joystick(0).init()
        self.clock = pygame.time.Clock()
        self.running = True

    def switch_state(self, state):
        """
        Switches current state to state passed in arguments

        Also remembers if state was changed in this iteration of main loop

        :param state: new state
        :return: None
        """
        self.state = state
        self.state.app = self
        self.switched = True

    def run(self):
        """
        Runs the application: updates it every frame

        :return: None
        """
        while self.running:
            self.state.update()
            # If state was switched after updating it will not be drawn not updated
            if self.switched:
                self.switched = False
                continue
            self.state.draw()
            self.clock.tick_busy_loop(const.FRAME_RATE)
            # print(self.clock.get_fps())
        pygame.quit()

    def stop(self):
        """
        Stors the application by breaking main loop

        :return: None
        """
        self.running = False
        self.switched = True  # It will not be redrawn right after stopping
