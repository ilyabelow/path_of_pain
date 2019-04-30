import pygame

from src.framework import base, const


class HUDFlyweight:
    def __init__(self):
        # TODO remove this somewhere in a more appropriate palce I guess
        self.KEYS_COORDS = (30, 180)
        self.HEARTS_COORDS = (30, 30)
        self.STAMINA_COORDS = (30, 120)

        self.HEART_SPRITE = pygame.image.load("assets/images/heart.png").convert_alpha()
        self.HEART_EMPTY_SPRITE = pygame.image.load("assets/images/heart_empty.png").convert_alpha()
        self.STAMINA_SPRITE = pygame.image.load("assets/images/stamina_full.png").convert_alpha()
        self.STAMINA_EMPTY_SPRITE = pygame.image.load("assets/images/stamina_empty.png").convert_alpha()
        self.KEY_SPRITE = pygame.image.load("assets/images/key.png").convert_alpha()


class HUD(base.AdvancedSprite):
    def __init__(self, flyweight, owner, coords):
        base.AdvancedSprite.__init__(self)
        self.flyweight = flyweight
        self.y = const.HUD_Y
        self.image = None
        self.coords = coords
        self.owner = owner
        self.makeup()

    def draw(self, screen, window):
        return screen.blit(self.image, self.coords)

    def makeup(self):
        pass


class HealthHUD(HUD):
    def __init__(self, flyweight, owner):
        HUD.__init__(self, flyweight, owner, flyweight.HEARTS_COORDS)

    def makeup(self):
        # IMAGE COMPOSING
        self.image = pygame.Surface((self.flyweight.HEART_SPRITE.get_width() * self.owner.max_health,
                                     self.flyweight.HEART_SPRITE.get_height()), pygame.SRCALPHA, 32)
        # normal hearts
        for i in range(self.owner.max_health):
            if i < self.owner.health:
                self.image.blit(self.flyweight.HEART_SPRITE, (i * self.flyweight.HEART_SPRITE.get_width(), 0))
            else:
                self.image.blit(self.flyweight.HEART_EMPTY_SPRITE, (i * self.flyweight.HEART_SPRITE.get_width(), 0))


class KeyHUD(HUD):
    def __init__(self, flyweight, owner):
        HUD.__init__(self, flyweight, owner, flyweight.KEYS_COORDS)

    def makeup(self):
        # IMAGE COMPOSING
        self.image = pygame.Surface((self.flyweight.KEY_SPRITE.get_width() * self.owner.keys,
                                     self.flyweight.KEY_SPRITE.get_height()), pygame.SRCALPHA, 32)
        # normal hearts
        for i in range(self.owner.keys):
            self.image.blit(self.flyweight.KEY_SPRITE, (i * self.flyweight.KEY_SPRITE.get_width(), 0))


# TODO redesign those big ugly circles
class StaminaHUD(HUD):
    def __init__(self, flyweight, owner):
        HUD.__init__(self, flyweight, owner, flyweight.STAMINA_COORDS)

    def makeup(self):
        self.image = pygame.Surface((self.flyweight.STAMINA_SPRITE.get_width() * self.owner.max_stamina,
                                     self.flyweight.STAMINA_SPRITE.get_height()), pygame.SRCALPHA, 32)
        for i in range(self.owner.max_stamina):
            if i < self.owner.stamina:
                self.image.blit(self.flyweight.STAMINA_SPRITE, (i * self.flyweight.STAMINA_SPRITE.get_width(), 0))
            else:
                self.image.blit(self.flyweight.STAMINA_EMPTY_SPRITE,
                                (i * self.flyweight.STAMINA_EMPTY_SPRITE.get_width(), 0))


class HUDFactory:
    def __init__(self, *groups, load=False):
        self.groups = groups
        self.flyweight = None
        if load:
            self.load()

    def create(self, hud_type, owner):
        product = hud_type(self.flyweight, owner)
        for group in self.groups:
            group.add(product)
        return product

    def create_health(self, owner):
        return self.create(HealthHUD, owner)

    def create_keys(self, owner):
        return self.create(KeyHUD, owner)

    def create_stamina(self, owner):
        return self.create(StaminaHUD, owner)

    def load(self):
        if self.flyweight is None:
            self.flyweight = HUDFlyweight()

    def unload(self):
        self.flyweight = None
