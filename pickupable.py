import random

import pygame

import base
import clock
import const
import interface

LITTLE_HEART_SPRITE = None
LITTLE_HEART_WEAK_SPRITE = None

KEY_SPRITE = None

BLEED_ALL_DIR_STATS = {'amount': 15, 'fade': 0.5, 'sizes': [10, 15],
                       'speed': 0.7, 'offset': 5}


class Heart(base.AdvancedSprite, interface.Pickupable, interface.Bleeding):
    def __init__(self, part_group, coords, weak=False):
        base.AdvancedSprite.__init__(self)
        interface.Pickupable.__init__(self)
        interface.Bleeding.__init__(self, part_group, None,
                                    BLEED_ALL_DIR_STATS,
                                    const.C_RED)  # TODO pink for weak
        self.weak = weak
        self.rect = pygame.Rect(coords.x, coords.y, 30, 30)
        self.image = None
        if not weak:
            self.image = LITTLE_HEART_SPRITE
        else:
            self.image = LITTLE_HEART_WEAK_SPRITE
        # TODO improve because it is really flat and should be under everything
        self.y = coords.y - 50
        self.death_clock = clock.Clock(self.expire, )
        self.death_clock.wind_up(90 - 60 * self.weak)

    def draw(self, screen, window):
        return screen.blit(self.image,
                           (self.rect.x - window.x, self.rect.y - window.y))

    def update(self):
        self.death_clock.tick()

    def expire(self):
        self.bleed_all_dir(pygame.Vector2(self.rect.x, self.rect.y))
        self.kill()


class Key(base.AdvancedSprite, interface.Pickupable):
    def __init__(self, coords, face=None):
        base.AdvancedSprite.__init__(self)
        interface.Pickupable.__init__(self)
        self.rect = pygame.Rect(0, 0, 25, 25)
        self.rect.centerx, self.rect.centery = coords.x, coords.y
        # TODO improve because it is really flat and should be under everything
        self.y = coords.y - 100
        if face is None:
            self.face = const.V_LEFT.rotate(random.randint(-180, 180))
        else:
            self.face = face
        self.image = pygame.transform.rotate(KEY_SPRITE,
                                             self.face.angle_to(const.V_UP))
        # TODO rethink
        self.im_rect = self.image.get_rect(centerx=self.rect.centerx,
                                           centery=self.rect.centery)

    def draw(self, screen, window):
        return screen.blit(self.image, (self.im_rect.x - window.x,
                                        self.im_rect.y - window.y))
