"""Module with a collection of particles"""
from enum import Enum
from typing import Tuple
from typing import Union

import pygame

from path_of_pain.src.framework import base, clock
from path_of_pain.src.framework import const


# Abstract class for implementations for bridge pattern
class Speck:
    def draw_shape(self, screen: pygame.Surface, centerx: Union[float, int], centery: Union[float, int],
                   radius: Union[float, int]) -> pygame.Rect:
        """
        Abstract method with blood type

        :param screen: surface to draw on
        :param centerx: x coordinate of the center of the particle
        :param centery: y coordinate of the center of the particle
        :param radius: particle "radius", but not really
        :return: rectangle that was drawn
        """
        pass

    def get_color(self) -> Tuple[int, int, int]:
        """
        Shortcut for choosing color

        :return: Color tuple
        """
        pass


# Note: we don't need specks with EVERY shape and EVERY color
class Round(Speck):
    """
    Round specks
    """

    def draw_shape(self, screen: pygame.Surface, centerx: Union[float, int], centery: Union[float, int],
                   radius: Union[float, int]) -> pygame.Rect:
        image = pygame.Surface((int(radius * 2), int(radius * 2)), pygame.SRCALPHA, 32)
        pygame.draw.circle(image, self.get_color(), [i // 2 for i in image.get_size()], int(radius))
        return screen.blit(image, (int(centerx - radius), int(centery - radius)))


class PlayerBlood(Round):
    """
    Player blood is round and black
    """

    def get_color(self) -> Tuple:
        return const.C_BLACK


class EnemyBlood(Round):
    """
    Enemy color is round and red
    """

    def get_color(self):
        return const.C_RED


class BossBlood(Round):
    """
    Boss color is round and dark red
    """

    def get_color(self):
        return (160, 0, 0)


class Square(Speck):
    """
    Square specks
    """

    def draw_shape(self, screen, centerx, centery, radius):
        image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA, 32)
        image.fill(self.get_color())
        return screen.blit(image, (centerx - radius, centery - radius))


class BoxBlood(Square):
    """
    Box "blood" is square and brown
    """

    def get_color(self):
        return const.C_BOX


class BloodFactoryFactory:
    """
    Abstract factory that produces factories of different blood (but all these factories have identical groups!)
    """

    def __init__(self, *groups: pygame.sprite.AbstractGroup):
        self.groups = groups

    def create(self, speck: Speck):
        return BloodFactory(speck, *self.groups)


class BloodFactory:
    def __init__(self, speck: Speck, *groups: pygame.sprite.AbstractGroup):
        self.groups = groups
        self.speck = speck

    def create(self, pos, speed, size, fadeout):
        product = Blood(self.speck, pos, speed, size, fadeout)
        for group in self.groups:
            group.add(product)
        return product


# TODO make blood that rise up and that falls on parabola
# Abstraction for bridge pattern
class Blood(base.AdvancedSprite):
    """
    Class for circular particle which moves ant const speed and fades out with time
    """

    def __init__(self, shape: Speck, pos: pygame.Vector2, speed: pygame.Vector2, size: int, fadeout: int):
        """
        Blood init

        :type shape: blood shape
        :param pos: initial position
        :param speed: moving speed
        :param size: initial size
        """
        base.AdvancedSprite.__init__(self)
        # TODO more customisable blood
        self.shape = shape
        self.speed = speed
        self.fadeout = fadeout
        self.pos = pos
        self.size = size

    def update(self, *args):
        # Move and fade
        self.pos.x += self.speed.x
        self.pos.y += self.speed.y
        self.fetch_layer(self.pos.y)
        # Fade
        self.size -= self.fadeout
        if self.size < 0:
            self.kill()
            return

    def draw(self, screen, window):
        # Delegate to implementation
        return self.shape.draw_shape(screen, self.pos.x - window.x, self.pos.y - window.y, self.size)


class ExclamationFactory:
    def __init__(self, *groups):
        self.groups = groups

    def create(self, pos, lifetime):
        product = Exclamation(pos, lifetime)
        for group in self.groups:
            group.add(product)
        return product


class Exclamation(base.AdvancedSprite):
    """
    Class for ! that appear when an enemy spots you
    """

    def __init__(self, pos, lifetime):
        """
        ! init

        :param pos: position
        :param lifetime: ticks to dissapear
        """
        base.AdvancedSprite.__init__(self)
        font = pygame.font.Font(None, 80)
        self.image = font.render("!", 3, const.C_BLACK)
        self.rect = self.image.get_rect(centerx=pos.x, centery=pos.y)
        self.postponed_fetch_layer(const.IMP_PARTICLE_Y)

        self.clock = clock.Clock(self.kill, lifetime)
        self.clock.wind_up()

    def update(self):
        self.clock.tick()

    def draw(self, screen, window):
        # Trivial
        return screen.blit(self.image, (self.rect.x - window.x, self.rect.y - window.y))


class FadeFactory:
    def __init__(self, *groups):
        self.groups = groups

    def create(self, duration, to_black, when_stops=None):
        product = Fade(duration, to_black, when_stops)
        for group in self.groups:
            group.add(product)
        return product


class Fade(base.AdvancedSprite):
    """
    Particle that covers the whole screen and makes it fade in/out
    """

    def __init__(self, duration, to_black, when_stops=None):
        """
        Init

        :param duration: duration of fade
        :param to_black: True if fade to black, False if fade from black
        :param when_stops: action to perform when fade is over
        """
        base.AdvancedSprite.__init__(self)
        if when_stops is None:
            when_stops = self.kill
        self.to_black = to_black
        self.duration = duration
        self.postponed_fetch_layer(const.FADE_Y)
        self.clock = clock.Clock(when_stops, duration)
        self.clock.wind_up()

    def update(self):
        self.clock.tick()
        # TODO temp solution
        if self.clock.is_not_running():
            self.kill()

    def draw(self, screen, window):
        image = pygame.Surface(const.RESOLUTION).convert_alpha()
        if self.to_black:
            # TODO remove bodge with abs()
            image.fill((0, 0, 0, 255 * (abs(self.duration - self.clock.how_much_is_left()) / self.duration)))
        else:
            image.fill((0, 0, 0, 255 * (abs(self.clock.how_much_is_left()) / self.duration)))
        return screen.blit(image, (0, 0))


class TitleState(Enum):
    """
    States that title can have
    """
    WAIT = 0
    FADE_IN = 1
    STAY = 2
    FADE_OUT = 3


class TitleFactory:
    def __init__(self, *groups):
        self.groups = groups

    def create(self, image, state_durations):
        product = Title(image, state_durations)
        for group in self.groups:
            group.add(product)
        return product


# TODO make customizable positioning?
class Title(base.AdvancedSprite):
    """
    Cool letters that fade in at the bottom of the screen and then fade out
    """

    def __init__(self, image, state_durations):
        """
        Init

        :param image: what image to operate on
        :param state_durations: tuple of 4 duration of each of 4 states
        """
        base.AdvancedSprite.__init__(self)
        self.image = image
        self.stage = TitleState.WAIT
        self.state_durations = state_durations
        self.clock = clock.Clock(self.next_stage)
        self.clock.wind_up(self.state_durations[self.stage.value])
        self.postponed_fetch_layer(const.IMP_PARTICLE_Y)

    def update(self):
        self.clock.tick()

    def draw(self, screen, offset):
        if self.stage != TitleState.WAIT:
            temp = self.image.copy()
            alpha = 255
            if self.stage == TitleState.FADE_IN:
                alpha = 255 * (self.state_durations[1] - self.clock.how_much_is_left()) / self.state_durations[1]
            if self.stage == TitleState.FADE_OUT:
                alpha = 255 * self.clock.how_much_is_left() / self.state_durations[3]

            temp.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)
            return screen.blit(temp,
                               self.image.get_rect(centerx=const.RESOLUTION[0] / 2, bottom=const.RESOLUTION[1] - 25))
        return pygame.Rect(0, 0, 0, 0)  # Nothing is drawn

    def next_stage(self):
        """
        Move to the next stage, kill self if this is the last stage

        :return: None
        """
        if self.stage == TitleState.FADE_OUT:
            self.kill()
        else:
            self.stage = TitleState(self.stage.value + 1)
            self.clock.wind_up(self.state_durations[self.stage.value])
