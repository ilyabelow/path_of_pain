from enum import Enum

import pygame

from src.framework import const
from src.framework.base import State
from src.framework.const import Button
from src.objects import particle
from src.states import game


class Option(Enum):
    PLAY = 0
    PLAY_PAINFUL = 1
    EXIT = 2


class TitleSprite(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        title_font = pygame.font.Font("assets/fonts/augustus.ttf", 128)
        self.image = title_font.render("Path of Pain", 10, const.C_RED)
        self.rect = self.image.get_rect(centerx=const.RESOLUTION[0] / 2, centery=200)


class OptionSprite(pygame.sprite.Sprite):
    def __init__(self, menu, option):
        pygame.sprite.Sprite.__init__(self)
        self.menu = menu
        self.option = option
        self.image = None
        self.rect = None

    def update(self):
        if self.menu.option == self.option:
            option_font = pygame.font.Font("assets/fonts/augustus.ttf", 42)
            # Bodge with '_' -> ' '
            self.image = option_font.render(self.option.name.replace('_', ' '), 10, const.C_GOLDEN)
        else:
            option_font = pygame.font.Font("assets/fonts/augustus.ttf", 36)
            self.image = option_font.render(self.option.name.replace('_', ' '), 10, const.C_RED)
        self.rect = self.image.get_rect(centerx=const.RESOLUTION[0] / 2,
                                        centery=const.RESOLUTION[1] / 2 + self.option.value * 100 - 100)


class Menu(State):
    def __init__(self):
        State.__init__(self)
        # LOAD SOUND
        pygame.mixer.music.load('assets/sounds/S59-55 Final Stage 3.wav')
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(1)
        self.CHANGE_SOUND = pygame.mixer.Sound('assets/sounds/ui_change_selection.wav')
        self.OK_SOUND = pygame.mixer.Sound('assets/sounds/ui_button_confirm.wav')

        # OPTION AND TITLE INIT
        self.title_group = pygame.sprite.GroupSingle(TitleSprite())
        self.option_group = pygame.sprite.OrderedUpdates()
        for i in Option:
            self.option_group.add(OptionSprite(self, i))
        self.blood = pygame.image.load('assets/images/menu_blood.png')
        # STATE INIT
        self.option = Option.PLAY
        self.option_group.update()
        self.fade = particle.Fade(const.MENU_FADE_IN, False)

    def draw(self):
        screen = pygame.display.get_surface()
        screen.fill(const.C_BLACK)
        screen.blit(self.blood, self.blood.get_rect(bottom=const.RESOLUTION[1], right=const.RESOLUTION[0]))
        self.title_group.draw(screen)
        self.option_group.draw(screen)
        self.fade.draw(screen, None)
        pygame.display.update()

    def update(self):
        # TODO move to controller? change controller?
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.shift_option(+1)
                if event.key == pygame.K_UP:
                    self.shift_option(-1)
                if event.key == pygame.K_SPACE:
                    self.select_option()
                if event.key == pygame.K_ESCAPE:
                    self.app.stop()
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == Button.A.value:
                    self.select_option()
                if event.button == Button.BACK.value:
                    self.set_option(Option.EXIT)
                    self.select_option()
            if event.type == pygame.JOYHATMOTION:
                if event.value[1] == -1:
                    self.shift_option(1)
                if event.value[1] == 1:
                    self.shift_option(-1)
        self.fade.update()

    def select_option(self):
        self.fade = particle.Fade(const.MENU_FADE_OUT, True, self.confirm_selection)
        pygame.mixer.music.fadeout(const.MENU_FADE_OUT * const.FRAME_RATE)
        self.OK_SOUND.play()

    def confirm_selection(self):
        if self.option == Option.EXIT:
            self.app.stop()
        if self.option == Option.PLAY:
            self.app.switch_state(game.Game())
        if self.option == Option.PLAY_PAINFUL:
            self.app.switch_state(game.Game(True))

    def shift_option(self, shift):
        self.set_option(Option((self.option.value + shift) % len(Option)))

    def set_option(self, option):
        self.option = option
        self.option_group.update()
        self.CHANGE_SOUND.play()
