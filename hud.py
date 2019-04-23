import pygame
import base
import const

HEART_SPRITE = None
HEART_EMPTY_SPRITE = None
HEART_WEAK_SPRITE = None
KEY_SPRITE = None


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
        HUD.__init__(self, owner, (30, 30))

    def makeup(self):
        # IMAGE COMPOSING
        self.image = pygame.Surface((100 * (self.owner.max_health + self.owner.weak_health), 100), pygame.SRCALPHA, 32)
        # normal hearts
        for i in range(self.owner.max_health):
            if i < self.owner.health:
                self.image.blit(HEART_SPRITE, (i * 100, 0))
            else:
                self.image.blit(HEART_EMPTY_SPRITE, (i * 100, 0))
        # weak hearts
        for i in range(self.owner.weak_health):
            self.image.blit(HEART_WEAK_SPRITE, ((i + self.owner.max_health) * 100, 0))


class KeyHUD(HUD):
    def __init__(self, owner):
        HUD.__init__(self, owner, (30, 150-120*owner.game.painful))

    def makeup(self):
        # IMAGE COMPOSING
        self.image = pygame.Surface((100 * self.owner.keys, 30), pygame.SRCALPHA, 32)
        # normal hearts
        for i in range(self.owner.keys):
            self.image.blit(KEY_SPRITE, (i * 100, 0))
