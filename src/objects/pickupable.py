import random

import pygame

from src.framework import base, clock, interface, const


class HeartFlyweight:
    def __init__(self):
        self.LITTLE_HEART_SPRITE = pygame.image.load("assets/images/little_heart.png").convert_alpha()


class Heart(base.AdvancedSprite, interface.Pickupable):
    def __init__(self, flyweight, coords):
        base.AdvancedSprite.__init__(self)
        interface.Pickupable.__init__(self)
        self.rect = pygame.Rect(coords.x, coords.y, 30, 30)
        self.image = None
        self.image = flyweight.LITTLE_HEART_SPRITE
        self.y = coords.y - 50  # TODO improve because it is really flat and should me under everything
        self.death_clock = clock.Clock(self.kill, 90)
        self.death_clock.wind_up()

    def draw(self, screen, window):
        return screen.blit(self.image, (self.rect.x - window.x, self.rect.y - window.y))

    def update(self):
        self.death_clock.tick()


HeartFactory = base.get_factory(Heart, HeartFlyweight)


class KeyFlyweight:
    def __init__(self):
        self.KEY_SPRITE = pygame.image.load("assets/images/key.png").convert_alpha()


class Key(base.AdvancedSprite, interface.Pickupable):
    def __init__(self, flyweight, coords, face=None):
        base.AdvancedSprite.__init__(self)
        interface.Pickupable.__init__(self)
        self.rect = pygame.Rect(0, 0, 25, 25)
        self.rect.centerx, self.rect.centery = coords.x, coords.y
        self.y = coords.y - 100  # TODO improve because it is really flat and should me under everything
        if face is None:
            self.face = const.V_LEFT.rotate(random.randint(-180, 180))
        else:
            self.face = face
        self.image = pygame.transform.rotate(flyweight.KEY_SPRITE, self.face.angle_to(const.V_UP))
        # TODO rethink
        self.im_rect = self.image.get_rect(centerx=self.rect.centerx, centery=self.rect.centery)

    def draw(self, screen, window):
        return screen.blit(self.image, (self.im_rect.x - window.x, self.im_rect.y - window.y))


KeyFactory = base.get_factory(Key, KeyFlyweight)
