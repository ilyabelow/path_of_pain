"""Module with objects that can be picked up"""

import random

import pygame

from path_of_pain.src.framework import base, clock
from path_of_pain.src.framework import interface, const


class HeartFactory:
    """
    Creates new heart and places it in according groups
    """

    def __init__(self, *groups):
        """
        Factory init

        :param groups: groups that new products will be added to
        """
        self.groups = groups
        self.flyweight = None

    def create(self, coords):
        product = Heart(self.flyweight, coords)
        for group in self.groups:
            group.add(product)
        return product

    def load(self):
        if self.flyweight is None:
            self.flyweight = HeartFlyweight()

    def unload(self):
        self.flyweight = None


class HeartFlyweight:
    def __init__(self):
        self.LITTLE_HEART_SPRITE = pygame.image.load(const.IMG_PATH + 'little_heart.png').convert_alpha()


class Heart(base.AdvancedSprite, interface.Pickupable):
    def __init__(self, flyweight, coords):
        base.AdvancedSprite.__init__(self)
        interface.Pickupable.__init__(self)
        self.rect = pygame.Rect(*coords, 30, 30)
        self.image = None
        self.image = flyweight.LITTLE_HEART_SPRITE
        self.y = coords[1] - 50  # TODO improve because it is really flat and should me under everything
        self.death_clock = clock.Clock(self.kill, 90)
        self.death_clock.wind_up()

    def draw(self, screen, window):
        return screen.blit(self.image, (self.rect.x - window.x, self.rect.y - window.y))

    def update(self):
        self.death_clock.tick()


class KeyFactory:
    def __init__(self, *groups, load=False):
        self.groups = groups
        self.flyweight = None
        if load:
            self.load()

    def create(self, coords, face):
        product = Key(self.flyweight, coords, face)
        for group in self.groups:
            group.add(product)
        return product

    def load(self):
        if self.flyweight is None:
            self.flyweight = KeyFlyweight()

    def unload(self):
        self.flyweight = None


class KeyFlyweight:
    def __init__(self):
        self.KEY_SPRITE = pygame.image.load(const.IMG_PATH + 'key.png').convert_alpha()


class Key(base.AdvancedSprite, interface.Pickupable):
    def __init__(self, flyweight, coords, face=None):
        base.AdvancedSprite.__init__(self)
        interface.Pickupable.__init__(self)
        self.rect = pygame.Rect(0, 0, 25, 25)
        self.rect.centerx, self.rect.centery = coords[0], coords[1]
        self.y = coords[1] - 100  # TODO improve because it is really flat and should me under everything
        if face is None:
            self.face = const.V_LEFT.rotate(random.randint(-180, 180))
        else:
            self.face = face
        self.image = pygame.transform.rotate(flyweight.KEY_SPRITE, self.face.angle_to(const.V_UP))
        # TODO rethink
        self.im_rect = self.image.get_rect(centerx=self.rect.centerx, centery=self.rect.centery)

    def draw(self, screen, window):
        return screen.blit(self.image, (self.im_rect.x - window.x, self.im_rect.y - window.y))
