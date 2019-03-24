import pygame
import base
import const

HEART_SPRITE = None
HEART_EMPTY_SPRITE = None
HEART_WEAK_SPRITE = None
KEY_SPRITE = None


# TODO base class for hud?
class HealthHUD(base.AdvancedSprite):
    def __init__(self, obj):
        base.AdvancedSprite.__init__(self)
        self.obj = obj
        # TODO move adding to group?
        self.y = const.HUD_Y
        self.obj.game.common_group.add(self)
        self.image = None
        self.makeup()

    def makeup(self):
        # IMAGE COMPOSING
        self.image = pygame.Surface((100 * (self.obj.max_health + self.obj.weak_health), 100), pygame.SRCALPHA, 32)
        # normal hearts
        for i in range(self.obj.max_health):
            if i < self.obj.health:
                self.image.blit(HEART_SPRITE, (i * 100, 0))
            else:
                self.image.blit(HEART_EMPTY_SPRITE, (i * 100, 0))
        # weak hearts
        for i in range(self.obj.weak_health):
            self.image.blit(HEART_WEAK_SPRITE, ((i + self.obj.max_health) * 100, 0))

    def draw(self, screen, window):
        return screen.blit(self.image, (30, 30))


# TODO copypasted from heart hud => make base class
class KeyHUD(base.AdvancedSprite):
    def __init__(self, obj):
        base.AdvancedSprite.__init__(self)
        self.obj = obj
        # TODO move adding to group?
        self.y = const.HUD_Y
        self.obj.game.common_group.add(self)
        self.image = None
        self.makeup()

    def makeup(self):
        # IMAGE COMPOSING
        self.image = pygame.Surface((100 * (self.obj.max_health + self.obj.weak_health), 30), pygame.SRCALPHA, 32)
        # normal hearts
        for i in range(self.obj.keys):
            self.image.blit(KEY_SPRITE, (i * 100, 0))

    def draw(self, screen, window):
        return screen.blit(self.image, (30, 150))
