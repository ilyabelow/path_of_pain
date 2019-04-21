import pygame
import const
import game


class Application:
    def __init__(self):
        pygame.mixer.pre_init(22050, -16, 8, 64)
        pygame.init()
        pygame.mouse.set_visible(False)
        pygame.display.set_mode(const.RESOLUTION, pygame.FULLSCREEN)
        pygame.display.set_caption("Path of Pain")
        pygame.display.set_icon(pygame.image.load("images/enemy.png"))

        self.clock = pygame.time.Clock()
        self.state = game.Menu()
        if pygame.joystick.get_count() != 0:
            pygame.joystick.Joystick(0).init()
        self.running = True

    def switch_state(self):
        new_state = self.state.switch_state()
        if isinstance(self.state, game.Menu):
            if new_state == const.OPTION_EXIT:
                self.running = False
            if new_state == const.OPTION_PLAY:
                self.state = game.Game()
            if new_state == const.OPTION_PLAY_PAINFUL:
                self.state = game.Game(True)
            return
        if isinstance(self.state, game.Game):
            if new_state == const.RESTART:
                # TODO just restart level
                self.state = game.Game(self.state.painful)
            if new_state == const.TO_MAIN_MENU:
                self.state = game.Menu()

    def run(self):
        while self.running:
            self.state.update()
            self.state.draw()
            self.clock.tick_busy_loop(const.FRAME_RATE)
            self.switch_state()

        pygame.quit()


def main():
    app = Application()
    app.run()


if __name__ == '__main__':
    main()
