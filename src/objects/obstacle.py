import random
from enum import Enum

import pygame

from src.framework import base, interface, const
from src.objects import pickupable


class Wall(base.AdvancedSprite):
    def __init__(self, rect, height=50):
        base.AdvancedSprite.__init__(self)
        self.WALL_MAX_BASE_HEIGHT = 25  # dunno how to call it, it's actually 1/2 of player
        base_height = min(self.WALL_MAX_BASE_HEIGHT, height // 2)
        self.image = pygame.Surface((rect.w, rect.h + height + base_height))
        self.image.fill((137, 107, 77))
        self.rect = rect
        pygame.draw.rect(self.image, (117, 90, 63), (0, rect.h + base_height, rect.w, height))
        self.y = rect.y
        self.height = height

    def draw(self, screen, window):
        return screen.blit(self.image, (self.rect.x - window.x, self.rect.y - window.y - self.height))


class BoxType(Enum):
    EMPTY = 0
    HEALTH = 1
    ENEMY = 2


class BoxFlyweight:
    def __init__(self):
        self.BOX_SPRITE = pygame.image.load("assets/images/box.png").convert_alpha()

        self.BOX_BREAK_SOUNDS = [pygame.mixer.Sound('assets/sounds/breakable_wall_hit_{}.wav'.format(i + 1))
                                 for i in range(2)]
        self.BLEED_ONE_DIR_STATS = {'amount': 5, 'splash': 45, 'fade': 2, 'sizes': [10, 15], 'speed': 6, 'offset': 10}
        self.BLEED_ALL_DIR_STATS = {'amount': 15, 'fade': 2, 'sizes': [15, 20], 'speed': 6, 'offset': 0}


# TODO make this class more general to allow different boxes: jars, skulls, etc
class Box(base.AdvancedSprite, interface.Healthy, interface.Bleeding):
    def __init__(self, flyweight, game, pos):
        base.AdvancedSprite.__init__(self)
        interface.Healthy.__init__(self, random.randint(1, 3), None, flyweight.BOX_BREAK_SOUNDS, None)
        interface.Bleeding.__init__(
            self,
            game.particle_group,
            flyweight.BLEED_ONE_DIR_STATS,
            flyweight.BLEED_ALL_DIR_STATS,
            const.C_BOX
        )  # TODO square blood
        self.rect = pygame.Rect(*pos, 50, 35)
        self.game = game
        self.flyweight = flyweight
        self.enemy_factory = game.enemy_factory
        self.offsets = [[0, 0]] + [[random.randint(-5, 5), random.randint(-5, 5)] for i in range(self.max_health - 1)]
        # TODO better randomizer
        # TODO store not mode but objects itself?
        if random.randint(0, 6) == 0 and not game.painful:
            self.mode = BoxType.HEALTH
        elif random.randint(0, 15) == 0:
            self.mode = BoxType.ENEMY
        else:
            self.mode = BoxType.EMPTY
        self.y = self.rect.y

    def on_ok_health(self, who):
        pos = pygame.Vector2((self.rect.centerx, self.rect.centery - (self.health - 1) * 15))
        self.bleed_one_dir(pos, (pos - who.pos).normalize())
        self.offsets.pop(0)

    def on_zero_health(self, who):
        pos = pygame.Vector2((self.rect.centerx, self.rect.centery))
        self.bleed_all_dir(pos)

        # BOX ACTION
        if self.mode == BoxType.HEALTH:
            # move(10, 10) to center out the heart
            heal = pickupable.Heart(self.game.particle_group, self.rect.move(10, 10))
            self.game.pickupable_group.add(heal)
        if self.mode == BoxType.ENEMY:
            newborn_enemy = self.enemy_factory.create(self.rect[:2])
            newborn_enemy.stun(15)

        self.kill()

    def draw(self, screen, window):
        rects = []
        for i in range(self.health):
            rects.append(screen.blit(self.flyweight.BOX_SPRITE, (
                self.rect.x - window.x + self.offsets[i][0],
                self.rect.y - window.y - i * 15 + self.offsets[i][1] - 8)))  # TODO height = 8, generalize
        return rects[0].unionall(rects[1:])


BoxFactory = base.get_factory_with_game(Box, BoxFlyweight)
