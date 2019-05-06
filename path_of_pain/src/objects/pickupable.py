"""Module with objects that can be picked up"""

import random

import pygame

from path_of_pain.src.framework import base, clock
from path_of_pain.src.framework import interface, const


class HeartFactory:
    def __init__(self, *groups):
        self.groups = groups
        self.flyweight = HeartFlyweight()

    def create(self, coords):
        product = Heart(self.flyweight, coords)
        for group in self.groups:
            group.add(product)
        return product


class HeartFlyweight:
    """
    Stores heart sprite
    """
    def __init__(self):
        self.LITTLE_HEART_SPRITE = pygame.image.load(const.IMG_PATH + 'little_heart.png').convert_alpha()


class Heart(base.AdvancedSprite, interface.Pickupable):
    """
    Pickupable heart that heals player on pickup
    """
    def __init__(self, flyweight, coords):
        """
        Heart init

        :param flyweight: flyweight with assets
        :param coords: coordinates of new heart
        """
        base.AdvancedSprite.__init__(self)
        interface.Pickupable.__init__(self)
        self.flyweight = flyweight
        self.rect = pygame.Rect(*coords, 30, 30)  # hitbox for collisions
        self.death_clock = clock.Clock(self.kill, 90)
        # the heart will dissaper after 3 seconds
        self.death_clock.wind_up()
        # TODO improve because it is really flat and should be under everything
        self.postponed_fetch_layer(coords[1] - 50)

    def draw(self, screen, window):
        # trivial
        return screen.blit(self.flyweight.LITTLE_HEART_SPRITE, (self.rect.x - window.x, self.rect.y - window.y))

    def update(self):
        self.death_clock.tick()


class KeyFactory:
    def __init__(self, *groups):
        self.groups = groups
        self.flyweight = KeyFlyweight()

    def create(self, coords, face):
        product = Key(self.flyweight, coords, face)
        for group in self.groups:
            group.add(product)
        return product


class KeyFlyweight:
    """
    Flyweight with key sprite
    """
    def __init__(self):
        self.KEY_SPRITE = pygame.image.load(const.IMG_PATH + 'key.png').convert_alpha()


class Key(base.AdvancedSprite, interface.Pickupable):
    """
    Pickypable key that player and enemies can pickup
    """
    def __init__(self, flyweight, coords, face=None):
        """

        :param flyweight: flyweight with assets
        :param coords: coordinates of new key
        :param face: direction the key will be pointed to
        """
        base.AdvancedSprite.__init__(self)
        interface.Pickupable.__init__(self)
        self.rect = pygame.Rect(0, 0, 25, 25)  # hitbox for collision
        self.rect.centerx, self.rect.centery = coords[0], coords[1]
        # TODO improve because it is really flat and should be under everything
        self.postponed_fetch_layer(coords[1] - 50)
        if face is None:
            self.face = const.V_LEFT.rotate(random.randint(-180, 180))  # default direction
        else:
            self.face = face
        self.image = pygame.transform.rotate(flyweight.KEY_SPRITE, self.face.angle_to(const.V_UP))
        # TODO rethink
        self.image_rect = self.image.get_rect(centerx=self.rect.centerx, centery=self.rect.centery)

    def draw(self, screen, window):
        return screen.blit(self.image, (self.image_rect.x - window.x, self.image_rect.y - window.y))
