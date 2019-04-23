import pygame
import base
import const
from enum import Enum

HEART_SPRITE = None
HEART_EMPTY_SPRITE = None
HEART_WEAK_SPRITE = None
KEY_SPRITE = None


class HUDPos(Enum):
    KEYS = (30, 150)
    HEARTS = (30, 30)
    STAMINA = (0, 0)


class HUD(base.AdvancedSprite):
    def __init__(self, owner, pos):
        base.AdvancedSprite.__init__(self)
        self.y = const.HUD_Y
        self.image = None
        self.pos = pos
        self.owner = owner
        self.owner.game.render_group.add(self)
        self.makeup()

    def draw(self, screen, window):
        return screen.blit(self.image, self.pos)

    def makeup(self):
        pass


class HealthHUD(HUD):
    def __init__(self, owner):
        HUD.__init__(self, owner, HUDPos.HEARTS.value)

    def makeup(self):
        # IMAGE COMPOSING
        self.image = pygame.Surface(
            (HEART_SPRITE.get_width() * (self.owner.max_health + self.owner.weak_health), HEART_SPRITE.get_height()),
            pygame.SRCALPHA, 32)
        # normal hearts
        for i in range(self.owner.max_health):
            if i < self.owner.health:
                self.image.blit(HEART_SPRITE, (i * HEART_SPRITE.get_width(), 0))
            else:
                self.image.blit(HEART_EMPTY_SPRITE, (i * HEART_SPRITE.get_width(), 0))
        # weak hearts
        for i in range(self.owner.weak_health):
            self.image.blit(HEART_WEAK_SPRITE, ((i + self.owner.max_health) * HEART_SPRITE.get_width(), 0))


class KeyHUD(HUD):
    def __init__(self, owner):
        HUD.__init__(self, owner, HUDPos.KEYS.value)

    def makeup(self):
        # IMAGE COMPOSING
        self.image = pygame.Surface((KEY_SPRITE.get_width() * self.owner.keys, KEY_SPRITE.get_height()),
                                    pygame.SRCALPHA, 32)
        # normal hearts
        for i in range(self.owner.keys):
            self.image.blit(KEY_SPRITE, (i * KEY_SPRITE.get_width(), 0))


# TODO add stamina!!! heheheheh