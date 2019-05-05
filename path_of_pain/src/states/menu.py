"""Module with class for main menu of the application"""
from enum import Enum

import pygame

from path_of_pain.src.framework import base
from path_of_pain.src.framework import const
from path_of_pain.src.framework.base import State
from path_of_pain.src.framework.const import Button
from path_of_pain.src.objects import particle
from path_of_pain.src.states import game


class Option(Enum):
    """
    Menu options
    """
    PLAY = 0
    PLAY_PAINFUL = 1
    EXIT = 2


class TitleSprite(pygame.sprite.Sprite):
    """
    Class for title sprite

    It is just a static image, what else can you say about it?
    """

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        title_font = pygame.font.Font(const.FNT_PATH + 'augustus.ttf', 128)
        self.image = title_font.render('Path of Pain', 10, const.C_RED)
        self.rect = self.image.get_rect(centerx=const.RESOLUTION[0] / 2, centery=200)


class OptionSprite(pygame.sprite.Sprite):
    """
    Class for menu options
    """

    def __init__(self, menu, option):
        pygame.sprite.Sprite.__init__(self)
        self.menu = menu  # menu to which option belongs to
        self.option = option
        # Will be updated before drawing!
        self.image = None
        self.rect = None

    def update(self):
        """
        Updates option if it is chosen or unchosen

        :return: None
        """
        # Test for option update
        if self.menu.option == self.option:
            option_font = pygame.font.Font(const.FNT_PATH + 'augustus.ttf', 42)  # BIGGER
            # TODO remove bodge with '_' -> ' '
            self.image = option_font.render(self.option.name.replace('_', ' '), 10, const.C_GOLDEN)  # AND REDDER
        else:
            option_font = pygame.font.Font(const.FNT_PATH + 'augustus.ttf', 36)
            self.image = option_font.render(self.option.name.replace('_', ' '), 10, const.C_RED)
        # place in the center
        self.rect = self.image.get_rect(centerx=const.RESOLUTION[0] / 2,
                                        centery=const.RESOLUTION[1] / 2 + self.option.value * 100 - 100)


# TODO make singletone?
class Menu(State):
    """
    Class that controls main menu of the application, mainly allows user to chose one of the options
    """
    def __init__(self):
        State.__init__(self)
        # LOAD SOUND
        pygame.mixer.music.load(const.SND_PATH + 'S59-55 Final Stage 3.wav')
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(1)
        self.CHANGE_SOUND = pygame.mixer.Sound(const.SND_PATH + 'ui_change_selection.wav')
        self.OK_SOUND = pygame.mixer.Sound(const.SND_PATH + 'ui_button_confirm.wav')

        # OPTION AND TITLE INIT
        self.render_group = base.AdvancedLayeredUpdates()
        self.title_group = pygame.sprite.GroupSingle()
        self.option_group = pygame.sprite.Group()
        self.fade_group = pygame.sprite.GroupSingle()

        self.title_group.add(TitleSprite())
        for i in Option:  # adding every option from enum
            self.option_group.add(OptionSprite(self, i))
        self.option = Option.PLAY
        self.option_group.update()
        self.render_group.add(*self.title_group.sprites(), *self.option_group.sprites())
        self.blood = pygame.image.load(const.IMG_PATH + 'menu_blood.png')  # cool blood pic

        # FADE DEPLOY
        self.fade_factory = particle.FadeFactory(self.fade_group, self.render_group)
        self.fade_factory.create(const.MENU_FADE_IN, False)

    def draw(self):
        """
        Draws all options, title and background

        :return: None
        """
        # TODO optimize
        screen = pygame.display.get_surface()
        screen.fill(const.C_BLACK)
        screen.blit(self.blood, self.blood.get_rect(bottom=const.RESOLUTION[1], right=const.RESOLUTION[0]))
        self.render_group.draw_all(screen, None)
        pygame.display.update()

    def update(self):
        """
        Listen to controller, change and select option, also update fade in/out

        :return: None
        """
        # TODO move to controller? change controller?
        for event in pygame.event.get():
            if self.fade_group.__len__() != 0:
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.shift_option(+1)
                if event.key == pygame.K_UP:
                    self.shift_option(-1)
                if event.key == pygame.K_SPACE:
                    self.select_option()
                if event.key == pygame.K_ESCAPE:
                    self.set_option(Option.EXIT)
                    self.select_option()
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
        self.fade_group.update()

    def select_option(self):
        """
        Play sound and start fade after which option's action will happen

        :return: None
        """
        self.fade_factory.create(const.MENU_FADE_OUT, True, self.do_select_selection)
        pygame.mixer.music.fadeout(const.MENU_FADE_OUT * const.FRAME_RATE)
        self.OK_SOUND.play()

    def do_select_selection(self):
        """
        Actually select option

        :return: None
        """
        if self.option == Option.EXIT:
            self.app.stop()
        if self.option == Option.PLAY:
            self.app.switch_state(game.Game())
        if self.option == Option.PLAY_PAINFUL:
            self.app.switch_state(game.Game(True))

    def shift_option(self, shift):
        """
        Shortcut for shifting option up and down

        :param shift: direction of shift, might be negative
        :return: None
        """
        self.set_option(Option((self.option.value + shift) % len(Option)))

    def set_option(self, option):
        """
        Changes current selected option

        :param option: new option
        :return: None
        """
        self.option = option
        # redraw sprites
        self.option_group.update()
        self.CHANGE_SOUND.play()
