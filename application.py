import pygame
from src.states.menu import Menu
from src.framework import const


# Context for STATE PATTERN
class Application:
    def __init__(self):
        pygame.mixer.pre_init(22050, -16, 8, 64)
        pygame.init()
        pygame.mouse.set_visible(False)
        pygame.display.set_mode(const.RESOLUTION, pygame.FULLSCREEN)
        pygame.display.set_caption("Path of Pain")
        pygame.display.set_icon(pygame.image.load("assets/images/enemy.png"))

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
        pygame.quit()

    def stop(self):
        self.running = False


def main():
    app = Application()
    app.run()


if __name__ == '__main__':
    main()
