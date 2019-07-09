"""Module with several HUDs for player"""
import pygame

from path_of_pain.src.framework import base
from path_of_pain.src.framework import const


class HUDFactory:
    def __init__(self, *groups):
        self.groups = groups
        self.flyweight = HUDFlyweight()

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


class HUDFlyweight:
    """
    All assets are stored in one place
    """

    def __init__(self):
        # TODO remove this somewhere in a more appropriate palce I guess
        self.KEYS_COORDS = (30, 180)
        self.HEARTS_COORDS = (30, 30)
        self.STAMINA_COORDS = (30, 120)

        self.HEART_SPRITE = pygame.image.load(const.IMG_PATH + 'heart.png').convert_alpha()
        self.HEART_EMPTY_SPRITE = pygame.image.load(const.IMG_PATH + 'heart_empty.png').convert_alpha()
        self.STAMINA_SPRITE = pygame.image.load(const.IMG_PATH + 'stamina_full.png').convert_alpha()
        self.STAMINA_EMPTY_SPRITE = pygame.image.load(const.IMG_PATH + 'stamina_empty.png').convert_alpha()
        self.KEY_SPRITE = pygame.image.load(const.IMG_PATH + 'key.png').convert_alpha()


# TODO move to framework.base?
class HUD(base.AdvancedSprite):
    """
    Base class for all HUDs
    """

    def __init__(self, flyweight, owner, coords):
        """
        Init base HUD

        :param flyweight: flyweight with assets
        :param owner: HUD's owner = player
        :param coords: coordinates where upper left corner will be
        """
        base.AdvancedSprite.__init__(self)
        self.flyweight = flyweight
        self.postponed_fetch_layer(const.HUD_Y)
        self.image = None
        self.coords = coords
        self.owner = owner
        self.makeup()

    def draw(self, screen, window):
        return screen.blit(self.image, self.coords)

    def makeup(self):
        """
        Redraw HUD image

        :return: None
        """
        pass


class HealthHUD(HUD):
    """
    HUD for health which is made of hearts
    """

    def __init__(self, flyweight, owner):
        HUD.__init__(self, flyweight, owner, flyweight.HEARTS_COORDS)

    def makeup(self):
        # whole image
        self.image = pygame.Surface((self.flyweight.HEART_SPRITE.get_width() * self.owner.max_health,
                                     self.flyweight.HEART_SPRITE.get_height()), pygame.SRCALPHA, 32)
        # placing hearts
        for i in range(self.owner.max_health):
            if i < self.owner.health:
                self.image.blit(self.flyweight.HEART_SPRITE, (i * self.flyweight.HEART_SPRITE.get_width(), 0))
            else:
                self.image.blit(self.flyweight.HEART_EMPTY_SPRITE, (i * self.flyweight.HEART_SPRITE.get_width(), 0))


class KeyHUD(HUD):
    """
    HUD for keys
    """

    def __init__(self, flyweight, owner):
        HUD.__init__(self, flyweight, owner, flyweight.KEYS_COORDS)

    def makeup(self):
        # whole image
        self.image = pygame.Surface((self.flyweight.KEY_SPRITE.get_width() * self.owner.keys,
                                     self.flyweight.KEY_SPRITE.get_height()), pygame.SRCALPHA, 32)
        # placing keys
        for i in range(self.owner.keys):
            self.image.blit(self.flyweight.KEY_SPRITE, (i * self.flyweight.KEY_SPRITE.get_width(), 0))


# TODO redesign those big ugly circles
class StaminaHUD(HUD):
    def __init__(self, flyweight, owner):
        HUD.__init__(self, flyweight, owner, flyweight.STAMINA_COORDS)

    # TODO this is a copypaste of HealthHUD, maybe unite?
    def makeup(self):
        self.image = pygame.Surface((self.flyweight.STAMINA_SPRITE.get_width() * self.owner.max_stamina,
                                     self.flyweight.STAMINA_SPRITE.get_height()), pygame.SRCALPHA, 32)
        for i in range(self.owner.max_stamina):
            if i < self.owner.stamina:
                self.image.blit(self.flyweight.STAMINA_SPRITE, (i * self.flyweight.STAMINA_SPRITE.get_width(), 0))
            else:
                self.image.blit(self.flyweight.STAMINA_EMPTY_SPRITE,
                                (i * self.flyweight.STAMINA_EMPTY_SPRITE.get_width(), 0))
