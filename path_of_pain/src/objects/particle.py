from enum import Enum

import pygame

from path_of_pain.src.framework import base, clock
from path_of_pain.src.framework import const


# TODO make template factories for different blood (abstract factory may be? bridge? WHO KNOWS???)

class BloodFactory:
    def __init__(self, *groups):
        self.groups = groups

    def create(self, pos, speed, size, fadeout, color):
        product = Blood(pos, speed, size, fadeout, color)
        for group in self.groups:
            group.add(product)
        return product


# TODO rename and make more general?
class Blood(base.AdvancedSprite):
    def __init__(self, pos, speed, size, fadeout, color):
        base.AdvancedSprite.__init__(self)
        # TODO more customisable blood
        self.color = color
        self.speed = speed
        self.fadeout = fadeout
        self.pos = pos
        self.size = size

    def update(self, *args):
        self.pos.x += self.speed.x
        self.pos.y += self.speed.y
        self.size -= self.fadeout
        if self.size < 0:
            self.kill()
            return
        self.fetch_layer(self.pos.y)

    def draw(self, screen, window):
        image = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA, 32)
        pygame.draw.circle(image, self.color, [i // 2 for i in image.get_size()], int(self.size))
        return screen.blit(image, (self.pos.x - window.x, self.pos.y - window.y))


class ExclamationFactory:
    def __init__(self, *groups):
        self.groups = groups

    def create(self, pos, lifetime):
        product = Exclamation(pos, lifetime)
        for group in self.groups:
            group.add(product)
        return product


class Exclamation(base.AdvancedSprite):
    def __init__(self, pos, lifetime):
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
    def __init__(self, duration, to_black, when_stops=None):
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
    def __init__(self, image, state_durations):
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
        if self.stage == TitleState.FADE_OUT:
            self.kill()
        else:
            self.stage = TitleState(self.stage.value + 1)
            self.clock.wind_up(self.state_durations[self.stage.value])
