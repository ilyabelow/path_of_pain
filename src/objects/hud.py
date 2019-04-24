import pygame

from src.framework import base, const

HEART_SPRITE = None
HEART_EMPTY_SPRITE = None
HEART_WEAK_SPRITE = None
KEY_SPRITE = None
STAMINA_SPRITE = None
STAMINA_EMPTY_SPRITE = None

KEYS_POS = (30, 180)
HEARTS_POS = (30, 30)
STAMINA_POS = (30, 120)


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
        HUD.__init__(self, owner, HEARTS_POS)

    def makeup(self):
        # IMAGE COMPOSING
        self.image = pygame.Surface(
            (HEART_SPRITE.get_width() * self.owner.max_health, HEART_SPRITE.get_height()),
            pygame.SRCALPHA, 32)
        # normal hearts
        for i in range(self.owner.max_health):
            if i < self.owner.health:
                self.image.blit(HEART_SPRITE, (i * HEART_SPRITE.get_width(), 0))
            else:
                self.image.blit(HEART_EMPTY_SPRITE, (i * HEART_SPRITE.get_width(), 0))


class KeyHUD(HUD):
    def __init__(self, owner):
        HUD.__init__(self, owner, KEYS_POS)

    def makeup(self):
        # IMAGE COMPOSING
        self.image = pygame.Surface((KEY_SPRITE.get_width() * self.owner.keys, KEY_SPRITE.get_height()),
                                    pygame.SRCALPHA, 32)
        # normal hearts
        for i in range(self.owner.keys):
            self.image.blit(KEY_SPRITE, (i * KEY_SPRITE.get_width(), 0))


# TODO redesign those big ugly circles
class StaminaHUD(HUD):
    def __init__(self, owner):
        HUD.__init__(self, owner, STAMINA_POS)

    def makeup(self):
        self.image = pygame.Surface((STAMINA_SPRITE.get_width() * self.owner.max_stamina, STAMINA_SPRITE.get_height()),
                                    pygame.SRCALPHA, 32)
        for i in range(self.owner.max_stamina):
            if i < self.owner.stamina:
                self.image.blit(STAMINA_SPRITE, (i * STAMINA_SPRITE.get_width(), 0))
            else:
                self.image.blit(STAMINA_EMPTY_SPRITE, (i * STAMINA_EMPTY_SPRITE.get_width(), 0))
