import random

import pygame

from src.framework import base, clock, const


class SwordFactory:
    def __init__(self, *groups, load=False):
        self.groups = groups
        self.flyweight = None
        if load:
            self.load()

    def create(self, owner):
        product = Sword(self.flyweight, owner)
        for group in self.groups:
            group.add(product)
        return product

    def load(self):
        if self.flyweight is None:
            self.flyweight = SwordFlyweight()

    def unload(self):
        self.flyweight = None


class SwordFlyweight:
    def __init__(self):
        self.SPRITE = pygame.image.load("assets/images/sword.png").convert_alpha()
        self.SWANG_SPRITE = pygame.image.load("assets/images/sword_swang.png").convert_alpha()

        self.SWING_SOUNDS = [pygame.mixer.Sound('assets/sounds/sword_{}.wav'.format(i + 1)) for i in range(5)]
        self.CLING_SOUND = pygame.mixer.Sound('assets/sounds/sword_hit_reject.wav')

        self.SWING_WAIT = 3
        self.SWING_DURATION = 9

        self.STAMINA_COST = 2


# TODO projectiles!
# TODO base class with better name then "hitter"
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
        self.current_swing_clock = clock.Clock()
        self.next_swing_clock = clock.Clock()
        self.clock_ticker = clock.ClockTicker(self)

        self.move()

    def swing(self):
        if self.next_swing_clock.is_not_running and self.owner.stamina_available(self.flyweight.STAMINA_COST):
            self.next_swing_clock.wind_up(self.flyweight.SWING_WAIT)
            self.current_swing_clock.wind_up(self.flyweight.SWING_DURATION)
            self.right_hand = not self.right_hand  # switch hand, just for aesthetics

            self.owner.stamina_drain(self.flyweight.STAMINA_COST)
            # HITTING
            self.pos = self.owner.pos + self.owner.face * 70
            # TODO good hitbox for sword
            self.rect = pygame.Rect(0, 0, 50, 50)
            self.rect.centerx = self.pos.x
            self.rect.centery = self.pos.y
            got_hit = pygame.sprite.spritecollide(self, self.game.hittable_group, False)
            for entity in got_hit:
                entity.hit(1, self)

            # SOUND EFFECTS
            random.choice(self.flyweight.SWING_SOUNDS).play()
            wall = pygame.sprite.spritecollideany(self, self.game.wall_group)
            if wall is not None:
                self.flyweight.CLING_SOUND.play()

    def move(self):
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
