"""Module with player's sword"""

import random

import pygame

from path_of_pain.src.framework import base, clock
from path_of_pain.src.framework import const


class SwordFactory:
    """
    Creates new assosiated product and places it in according groups
    """

    def __init__(self, *groups):
        """
        Factory init

        :param groups: groups that new products will be added to
        """
        self.groups = groups
        self.flyweight = None

    def create(self, owner):
        """
        Create new product and place it in game groups

        :param owner: sword's owner
        :return: newly created product
        """
        product = Sword(self.flyweight, owner)
        for group in self.groups:
            group.add(product)
        return product

    def load(self):
        """
        Load flyweight if necessary

        :return: None
        """
        if self.flyweight is None:
            self.flyweight = SwordFlyweight()

    def unload(self):
        """
        Unload flyweight if it is not needed

        :return: None
        """
        self.flyweight = None


class SwordFlyweight:
    """
    Stores assets and constants
    """
    def __init__(self):
        self.SPRITE = pygame.image.load(const.IMG_PATH + 'sword.png').convert_alpha()
        self.SWANG_SPRITE = pygame.image.load(const.IMG_PATH + 'sword_swang.png').convert_alpha()

        self.SWING_SOUNDS = [pygame.mixer.Sound(const.SND_PATH + 'sword_{}.wav'.format(i + 1)) for i in range(5)]
        self.CLING_SOUND = pygame.mixer.Sound(const.SND_PATH + 'sword_hit_reject.wav')

        self.SWING_WAIT = 3
        self.SWING_DURATION = 9

        self.STAMINA_COST = 2


# TODO projectiles!
# TODO base class with better name then 'hitter'
class Sword(base.AdvancedSprite):
    def __init__(self, flyweight, owner):
        super(Sword, self).__init__()
        self.game = owner.game
        self.owner = owner
        self.game.hitter_group.add(self)  # redundant?
        self.pos = None
        self.rect = None
        self.flyweight = flyweight
        # SWING STATS
        self.right_hand = True

        # CLOCKS
        self.current_swing_clock = clock.Clock()  # runs while the sword is swang
        self.next_swing_clock = clock.Clock()  # avoid swing spamming
        self.clock_ticker = clock.ClockTicker(self)

        self.move()

    def swing(self):
        """
        Perform attack on enemies

        :return: None
        """
        # check if you can swing at all
        if self.next_swing_clock.is_not_running and self.owner.stamina_available(self.flyweight.STAMINA_COST):
            self.next_swing_clock.wind_up(self.flyweight.SWING_WAIT)
            self.current_swing_clock.wind_up(self.flyweight.SWING_DURATION)
            self.right_hand = not self.right_hand  # switch hand, just for aesthetics
            self.owner.stamina_drain(self.flyweight.STAMINA_COST)

            # ACTUAL HITTING
            self.move()
            # TODO good hitbox for sword
            self.rect = pygame.Rect(0, 0, 50, 50)
            self.rect.centerx = self.pos.x
            self.rect.centery = self.pos.y
            # finding enemies that are hit
            got_hit = pygame.sprite.spritecollide(self, self.game.hittable_group, False)
            for entity in got_hit:
                entity.hit(1, self)

            # SOUND EFFECTS
            random.choice(self.flyweight.SWING_SOUNDS).play()
            # make cling noise if sword hit wall
            wall = pygame.sprite.spritecollideany(self, self.game.wall_group)
            if wall is not None:
                self.flyweight.CLING_SOUND.play()

    def move(self):
        """
        Sync position with player

        :return: None
        """
        if self.current_swing_clock.is_not_running():
            self.pos = self.owner.pos + self.owner.face.rotate(90) * (80 * self.right_hand - 40)
        else:
            self.pos = self.owner.pos + self.owner.face * 70

    def update(self):
        self.clock_ticker.tick_all()
        self.move()
        self.fetch_layer(self.owner.pos.y)  # TODO make better layer calculation

    def draw(self, screen, window):
        if self.current_swing_clock.is_not_running():
            image = pygame.transform.rotate(self.flyweight.SPRITE, self.owner.face.angle_to(const.V_UP))
        else:
            if self.right_hand:
                image = pygame.transform.rotate(pygame.transform.flip(self.flyweight.SWANG_SPRITE, True, False),
                                                self.owner.face.angle_to(const.V_UP) - 45)
            else:
                image = pygame.transform.rotate(self.flyweight.SWANG_SPRITE, self.owner.face.angle_to(const.V_UP) + 45)
        rect = image.get_rect(centerx=self.pos.x, centery=self.pos.y)
        return screen.blit(image, (rect.x - window.x, rect.y - window.y))
