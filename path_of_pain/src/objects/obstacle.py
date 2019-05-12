"""
Module with miscellaneous static objects
"""

import random
from enum import Enum

import pygame

from path_of_pain.src.framework import base
from path_of_pain.src.framework import interface, const
from path_of_pain.src.objects import particle


class DoorFactory:
    """
    Creates doors and pots them into corresponding containers
    """

    def __init__(self, *groups):
        self.groups = groups
        self.flyweight = DoorFlyweight()

    def create(self, coords, next_level, locks):
        product = Door(self.flyweight, coords, next_level, locks)
        for group in self.groups:
            group.add(product)
        return product


class DoorFlyweight:
    """
    Door image and sound assets
    """

    def __init__(self):
        self.DOOR_OPENED_SPRITE = pygame.image.load(const.IMG_PATH + 'door_opened.png').convert_alpha()
        self.DOOR_LOCKED_SPRITE = pygame.image.load(const.IMG_PATH + 'door_locked.png').convert_alpha()
        self.LOCK_SPRITE = pygame.image.load(const.IMG_PATH + 'lock.png').convert_alpha()
        self.KEY_TURN_SOUND = pygame.mixer.Sound(const.SND_PATH + 'shiny_item_pickup.wav')
        self.OPENED_SOUND = pygame.mixer.Sound(const.SND_PATH + 'gate_open.wav')


class Door(base.AdvancedSprite, interface.Interactive):
    """
    A door is a way to go to the next level
    """

    def __init__(self, flyweight, coords, next_level, locks):
        """
        Door init

        :param flyweight: flyweight with assets
        :param coords: coordinate of bottom left corner
        :param next_level: level to which the door will lead
        :param locks: amount of locks on the door
        """
        base.AdvancedSprite.__init__(self)
        interface.Interactive.__init__(self)
        self.flyweight = flyweight
        self.max_locks = locks
        self.locks = locks
        self.next_level = next_level
        self.locked = True
        self.coords = coords
        # TODO move defining point to middle of the bottom
        self.rect = pygame.Rect(coords[0], coords[1] - 100, 100, 100)
        self.postponed_fetch_layer(self.rect.bottom)

    def draw(self, screen, window):
        if self.locked:
            # draw DOOR_LOCKED_SPRITE + locks
            rect = screen.blit(self.flyweight.DOOR_LOCKED_SPRITE, (self.rect.x - window.x, self.rect.y - window.y))
            for i in range(self.locks):
                screen.blit(self.flyweight.LOCK_SPRITE,
                            (self.rect.x - window.x + i * self.flyweight.LOCK_SPRITE.get_width(),
                             self.rect.y - window.y + 60))
            return rect
        return screen.blit(self.flyweight.DOOR_OPENED_SPRITE, (self.rect.x - window.x, self.rect.y - window.y))

    def interact(self, who):
        # checking if player is in correct position to interact with the door
        if abs(const.V_UP.angle_to(who.face)) < 90 and (  # facing in right direction
                who.rect.right > self.rect.left or who.rect.left < self.rect.right  # player is within door horizontally
        ) and who.rect.top < self.rect.bottom:  # player touches the door from below
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
    """
    Creates walls and pots them into corresponding containers
    """

    def __init__(self, *groups):
        self.groups = groups

    def create(self, dimensions, height=50):
        product = Wall(pygame.Rect(*dimensions), height)
        for group in self.groups:
            group.add(product)
        return product


class Wall(base.AdvancedSprite):
    """
    Walls make up level structure
    """

    def __init__(self, rect, height):
        """
        Wall init

        :param rect: Rectangle of wall hitbox
        :param height: wall height
        """
        base.AdvancedSprite.__init__(self)
        # TODO move it
        self.WALL_MAX_BASE_HEIGHT = 25  # dunno how to call it, it's actually 1/2 of player
        base_height = min(self.WALL_MAX_BASE_HEIGHT, height // 2)  # height of bottom "shadow"
        self.rect = rect
        self.height = height

        # IMAGE COMPOSING
        self.image = pygame.Surface((rect.w, rect.h + height + base_height))
        self.image.fill((137, 107, 77))
        # bottom "shadow"
        pygame.draw.rect(self.image, (117, 90, 63), (0, rect.h + base_height, rect.w, height))

        self.postponed_fetch_layer(rect.centery)

    def draw(self, screen, window):
        # trivial
        return screen.blit(self.image, (self.rect.x - window.x, self.rect.y - window.y - self.height))


class BoxType(Enum):
    """
    List of action that box can perform after destruction
    """
    EMPTY = 0
    HEALTH = 1
    ENEMY = 2


class BoxFactory:
    """
    Creates boxes and pots them into corresponding containers
    """

    def __init__(self, game, *groups):
        self.groups = groups
        self.flyweight = BoxFlyweight()
        self.game = game

    def create(self, coords):
        product = Box(self.flyweight, self.game, coords)
        for group in self.groups:
            group.add(product)
        return product


class BoxFlyweight:
    """
    Box image and sound assets + some constants
    """

    def __init__(self):
        self.BOX_SPRITE = pygame.image.load(const.IMG_PATH + 'box.png').convert_alpha()

        self.BOX_BREAK_SOUNDS = [pygame.mixer.Sound(const.SND_PATH + 'breakable_wall_hit_{}.wav'.format(i + 1))
                                 for i in range(2)]
        self.BLEED_ONE_DIR_STATS = {'amount': 5, 'splash': 45, 'fade': 2, 'sizes': [10, 15], 'speed': 6, 'offset': 10,
                                    'color': const.C_BOX}
        self.BLEED_ALL_DIR_STATS = {'amount': 15, 'fade': 2, 'sizes': [15, 20], 'speed': 6, 'offset': 0,
                                    'color': const.C_BOX}


# TODO make this class more general to allow different boxes: jars, skulls, etc
class Box(base.AdvancedSprite, interface.Healthy, interface.Bleeding):
    """
    Boxes are static objects which you can destroy Zelda-style
    """

    def __init__(self, flyweight, game, coords):
        """
        Box init

        :param flyweight: flyweight with asets and constants
        :param game: game in which box is stores
        :param coords: coordinates of upper left corner
        """
        base.AdvancedSprite.__init__(self)
        interface.Healthy.__init__(self, random.randint(1, 3), None, flyweight.BOX_BREAK_SOUNDS, None)
        interface.Bleeding.__init__(
            self,
            game.blood_factory_factory.create(particle.BoxBlood()),
            flyweight.BLEED_ONE_DIR_STATS,
            flyweight.BLEED_ALL_DIR_STATS,
        )
        self.rect = pygame.Rect(*coords, 50, 35)  # hitbox
        self.flyweight = flyweight
        self.heart_factory = game.heart_factory
        self.enemy_factory = game.enemy_factory
        # offsets of boxes in the stack, just for decoration
        self.offsets = [[0, 0]] + [[random.randint(-5, 5), random.randint(-5, 5)] for i in range(self.max_health - 1)]

        # RANDOMIZE POST-DESTRUCTION BOX ACTION
        if random.randint(0, 6) == 0 and not game.painful:
            self.mode = BoxType.HEALTH
        elif random.randint(0, 15) == 0:
            self.mode = BoxType.ENEMY
        else:
            self.mode = BoxType.EMPTY

        self.postponed_fetch_layer(self.rect.y)

    def on_ok_health(self, who):
        # just some bleeding
        pos = pygame.Vector2((self.rect.centerx, self.rect.centery - (self.health - 1) * 15))
        self.bleed_one_dir(pos, (pos - who.pos).normalize())
        # move all upper boxes one level down (well, sort of)
        self.offsets.pop(0)

    def on_zero_health(self, who):
        pos = pygame.Vector2((self.rect.centerx, self.rect.centery))
        self.bleed_all_dir(pos)

        # BOX ACTION
        if self.mode == BoxType.HEALTH:
            self.heart_factory.create(self.rect.move(10, 10)[:2])  # move(10, 10) to center out the heart
        if self.mode == BoxType.ENEMY:
            newborn_enemy = self.enemy_factory.create_enemy(self.rect[:2])
            newborn_enemy.stun(15)

        self.kill()

    def draw(self, screen, window):
        rects = []
        for i in range(self.health):
            # drawing boxes in a stack from the bottom one to the top one
            # some magical numbers here and there, but it works fine
            rects.append(screen.blit(self.flyweight.BOX_SPRITE, (
                self.rect.x - window.x + self.offsets[i][0],
                self.rect.y - window.y - i * 15 + self.offsets[i][1] - 8)))  # TODO height = 8, generalize
        return rects[0].unionall(rects[1:])  # updated screen part consist of several rects, one for each box
