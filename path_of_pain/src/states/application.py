import pygame

from path_of_pain.src.framework import const
from path_of_pain.src.states.menu import Menu


# Context for STATE PATTERN
class Application:
    def __init__(self):
        pygame.mixer.pre_init(22050, -16, 8, 64)
        pygame.init()
        pygame.mouse.set_visible(False)
        pygame.display.set_mode(const.RESOLUTION, pygame.FULLSCREEN)
        pygame.display.set_caption("Path of Pain")
        pygame.display.set_icon(pygame.image.load(const.IMG_PATH + "enemy.png"))

        self.clock = pygame.time.Clock()
        self.state = None
        self.switched = False
        self.switch_state(Menu())
        if pygame.joystick.get_count() != 0:
            pygame.joystick.Joystick(0).init()
        self.running = True

    def switch_state(self, state):
        self.state = state
        self.state.app = self
        self.switched = True

    def run(self):
        while self.running:
            self.state.update()
            if self.switched:
                self.switched = False
                continue
            self.state.draw()
            self.clock.tick_busy_loop(const.FRAME_RATE)
            # print(self.clock.get_fps())
        pygame.quit()

    def stop(self):
        self.running = False
        self.switched = True  # It will not be redrawn right after stopping
