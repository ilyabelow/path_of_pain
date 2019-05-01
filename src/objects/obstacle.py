import random
from enum import Enum

import pygame

from src.framework import base, interface, const


class DoorFactory:
    def __init__(self, *groups, load=False):
        self.groups = groups
        self.flyweight = None
        if load:
            self.load()

    def create(self, coords, next_level, locks):
        product = Door(self.flyweight, coords, next_level, locks)
        for group in self.groups:
            group.add(product)
        return product

    def load(self):
        if self.flyweight is None:
            self.flyweight = DoorFlyweight()

    def unload(self):
        self.flyweight = None


class DoorFlyweight:
    def __init__(self):
        self.DOOR_OPENED_SPRITE = pygame.image.load("assets/images/door_opened.png").convert_alpha()
        self.DOOR_LOCKED_SPRITE = pygame.image.load("assets/images/door_locked.png").convert_alpha()
        self.LOCK_SPRITE = pygame.image.load("assets/images/lock.png").convert_alpha()
        self.KEY_TURN_SOUND = pygame.mixer.Sound('assets/sounds/shiny_item_pickup.wav')
        self.OPENED_SOUND = pygame.mixer.Sound('assets/sounds/gate_open.wav')


class Door(base.AdvancedSprite, interface.Interactive):
    def __init__(self, flyweight, coords, next_level, locks):
        base.AdvancedSprite.__init__(self)
        interface.Interactive.__init__(self)
        self.flyweight = flyweight
        self.max_locks = locks
        self.locks = locks
        self.next_level = next_level
        self.locked = True
        self.coords = coords
        self.rect = pygame.Rect(coords[0], coords[1] - 100, 100, 100)
        self.y = self.rect.bottom

    def draw(self, screen, window):
        if self.locked:
            rect = screen.blit(self.flyweight.DOOR_LOCKED_SPRITE, (self.rect.x - window.x, self.rect.y - window.y))
            for i in range(self.locks):
                screen.blit(self.flyweight.LOCK_SPRITE,
                            (self.rect.x - window.x + i * self.flyweight.LOCK_SPRITE.get_width(),
                             self.rect.y - window.y + 60))
            return rect
        return screen.blit(self.flyweight.DOOR_OPENED_SPRITE, (self.rect.x - window.x, self.rect.y - window.y))

    def interact(self, who):
        if abs(const.V_UP.angle_to(who.face)) < 90 and \
                (who.rect.right > self.rect.left or
                 who.rect.left < self.rect.right) and \
                who.rect.top < self.rect.bottom:
            if self.locked:
                if self.locks == 0:
                    self.locked = False
                    self.flyweight.OPENED_SOUND.play()
                elif who.keys >= 1:
                    who.keys -= 1
                    self.locks -= 1
                    if self.locks == 0:
                        who.surprise_me(10)
                    self.flyweight.KEY_TURN_SOUND.play()
                    who.key_hud.makeup()

            else:
                who.game.reset_level(self.next_level)


class WallFactory:
    def __init__(self, *groups):
        self.groups = groups

    def create(self, dimentions, height=50):
        product = Wall(pygame.Rect(*dimentions), height)
        for group in self.groups:
            group.add(product)
        return product


class Wall(base.AdvancedSprite):
    def __init__(self, rect, height):
        base.AdvancedSprite.__init__(self)
        self.WALL_MAX_BASE_HEIGHT = 25  # dunno how to call it, it's actually 1/2 of player
        base_height = min(self.WALL_MAX_BASE_HEIGHT, height // 2)
        self.image = pygame.Surface((rect.w, rect.h + height + base_height))
        self.image.fill((137, 107, 77))
        self.rect = rect
        pygame.draw.rect(self.image, (117, 90, 63), (0, rect.h + base_height, rect.w, height))
        self.y = rect.centery  # TODO workout a better solution
        self.height = height

    def draw(self, screen, window):
        return screen.blit(self.image, (self.rect.x - window.x, self.rect.y - window.y - self.height))


class BoxType(Enum):
    EMPTY = 0
    HEALTH = 1
    ENEMY = 2


class BoxFactory:
    def __init__(self, game, *groups, load=False):
        self.groups = groups
        self.flyweight = None
        if load:
            self.load()
        self.game = game

    def create(self, coords):
        product = Box(self.flyweight, self.game, coords)
        for group in self.groups:
            group.add(product)
        return product

    def load(self):
        if self.flyweight is None:
            self.flyweight = BoxFlyweight()

    def unload(self):
        self.flyweight = None


class BoxFlyweight:
    def __init__(self):
        self.BOX_SPRITE = pygame.image.load("assets/images/box.png").convert_alpha()

        self.BOX_BREAK_SOUNDS = [pygame.mixer.Sound('assets/sounds/breakable_wall_hit_{}.wav'.format(i + 1))
                                 for i in range(2)]
        self.BLEED_ONE_DIR_STATS = {'amount': 5, 'splash': 45, 'fade': 2, 'sizes': [10, 15], 'speed': 6, 'offset': 10}
        self.BLEED_ALL_DIR_STATS = {'amount': 15, 'fade': 2, 'sizes': [15, 20], 'speed': 6, 'offset': 0}


# TODO make this class more general to allow different boxes: jars, skulls, etc
class Box(base.AdvancedSprite, interface.Healthy, interface.Bleeding):
    def __init__(self, flyweight, game, coords):
        base.AdvancedSprite.__init__(self)
        interface.Healthy.__init__(self, random.randint(1, 3), None, flyweight.BOX_BREAK_SOUNDS, None)
        interface.Bleeding.__init__(
            self,
            game.blood_factory,
            flyweight.BLEED_ONE_DIR_STATS,
            flyweight.BLEED_ALL_DIR_STATS,
            const.C_BOX
        )  # TODO square blood
        self.rect = pygame.Rect(*coords, 50, 35)
        self.game = game
        self.flyweight = flyweight
        self.enemy_factory = game.enemy_factory
        self.offsets = [[0, 0]] + [[random.randint(-5, 5), random.randint(-5, 5)] for i in range(self.max_health - 1)]
        # TODO better randomizer?
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
            self.game.heart_factory.create(self.rect.move(10, 10)[:2])
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
