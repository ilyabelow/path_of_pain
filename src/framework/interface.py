"""Module with different interfaces that implement extra object behaviour"""

import random

import pygame

from src.framework import clock, const


class Healthy:
    """Interface for objects with health"""

    def __init__(self,
                 max_health,
                 heal_sounds=None,
                 hit_sounds=None,
                 death_sounds=None,
                 invulnerability=-1):
        self.max_health = max_health
        self.health = max_health
        self.invulnerability_clock = clock.Clock(None, invulnerability)

        self.heal_sounds = heal_sounds
        self.hit_sounds = hit_sounds
        self.death_sounds = death_sounds

    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)
        if self.death_sounds is not None:
            random.choice(self.heal_sounds).play()
        self.after_healing()

    def after_healing(self):
        pass

    def hit(self, amount, who):
        if self.invulnerability_clock.is_not_running():
            self.invulnerability_clock.wind_up()
            self.health -= amount
            if self.hit_sounds is not None:
                random.choice(self.hit_sounds).play()
            self.on_any_health(who)

            if self.health == 1:  # TODO generalize low health
                self.on_low_health(who)
            if self.health == 0:
                if self.death_sounds is not None:
                    random.choice(self.death_sounds).play()
                self.on_zero_health(who)
            else:
                self.on_ok_health(who)

    def on_any_health(self, direction):
        pass

    def on_ok_health(self, direction):
        pass

    def on_low_health(self, direction):
        pass

    def on_zero_health(self, direction):
        pass


class Tired:
    """Interface for objects with stamina"""

    def __init__(self, max_stamina, rest_speed):
        self.rest_speed = rest_speed
        self.max_stamina = max_stamina
        self.stamina = max_stamina
        self.rest_clock = clock.Clock(self.stamina_rest, rest_speed)

    def stamina_rest(self):
        self.stamina += 1
        if self.stamina >= self.max_stamina:
            self.rest_clock.stop()
        else:
            self.rest_clock.wind_up()

    def stamina_drain(self, cost):
        self.stamina -= cost
        self.rest_clock.wind_up()

    def stamina_available(self, desired):
        return self.stamina >= desired


# TODO remove (because it is UGLY) and make similar functionality elsewhere
class Bleeding:
    """Interface for shortcut for bleeding in two modes - in one direction and in all directions"""

    def __init__(self, factory, one_dir_stats, all_dir_stats, color):
        self.all_dir_stats = all_dir_stats
        self.one_dir_stats = one_dir_stats
        self.factory = factory
        self.color = color

    def bleed_one_dir(self, pos, main_direction):
        for i in range(self.one_dir_stats['amount']):
            direction = main_direction.rotate(
                random.randint(-self.one_dir_stats['splash'], self.one_dir_stats['splash']))
            self.factory.create(pos + direction * self.one_dir_stats['offset'],
                                direction * self.one_dir_stats['speed'],
                                random.randint(self.one_dir_stats['sizes'][0], self.one_dir_stats['sizes'][1]),
                                self.one_dir_stats['fade'],
                                self.color)

    def bleed_all_dir(self, pos):
        for i in range(self.all_dir_stats['amount']):
            direction = const.V_LEFT.rotate(random.randint(-180, 180))
            self.factory.create(pos + direction * self.all_dir_stats['offset'],
                                direction * self.all_dir_stats['speed'],
                                random.randint(self.all_dir_stats['sizes'][0], self.all_dir_stats['sizes'][1]),
                                self.all_dir_stats['fade'],
                                self.color)


# TODO move some functionality here???????
class Pickupable:
    """Interface for objects that can be picked up"""

    def __init__(self):
        pass


# TODO strong connection between these two ^ v

# TODO remove may be?
class Pickuping:
    """Interface for objects that can pick up other objects"""

    def __init__(self, what_to_pickup):
        self.what_to_pickup = what_to_pickup

    def pickup(self):
        pick = pygame.sprite.spritecollide(self, self.what_to_pickup, False)
        for p in pick:
            if self.can_pickup(p):
                # TODO Pickupable.pickup() was dissolved here, mb restore?
                p.kill()
                self.do_pickup(p)

    # TODO BAD INTERFACE >:(
    def do_pickup(self, what):
        pass

    def can_pickup(self, what):
        pass


# TODO all common properties of Player and Enemy is bunched up here, needs disassembling to DIFFERENT interfaces (how?)
class Moving:
    """Interface for objects that perform complex movement"""

    def __init__(self, coords, collide_with, dash_stats, back_dash_stats):
        # TODO unpack dash stats
        self.back_dash_stats = back_dash_stats
        self.dash_stats = dash_stats
        self.rect = None
        self.collide_with = collide_with
        self.face = const.V_LEFT.rotate(random.randint(-180, 180))

        self.pos = pygame.Vector2(coords)
        self.speed = const.V_ZERO

        # TODO make up better way to state if the object is moving. This field is used in SOME cases
        self.moving = False
        self.can_be_moved = True  # object's ability to make decision about its movement!!!

        # BASE CLOCKS
        # TODO move to interfaces as well
        self.dash_clock = clock.Clock(self.unblock_movement)
        self.next_dash_clock = clock.Clock()
        self.stun_clock = clock.Clock(self.unblock_movement)
        self.throw_back_clock = clock.Clock(self.stop)

    def move_and_collide(self):
        # collision logic mostly copypasted from some example, so it works fine
        # move horizontally
        self.pos.x += self.speed.x
        self.rect.centerx = self.pos.x
        intersected = pygame.sprite.spritecollide(self, self.collide_with, False)
        for wall in intersected:
            if self.speed.x < 0:
                self.rect.left = wall.rect.right
                self.pos.x = self.rect.centerx
            else:
                self.rect.right = wall.rect.left
                self.pos.x = self.rect.centerx

        # move vertically
        self.pos.y += self.speed.y
        self.rect.centery = self.pos.y
        intersected = pygame.sprite.spritecollide(self, self.collide_with, False)
        for wall in intersected:
            if self.speed.y < 0:
                self.rect.top = wall.rect.bottom
                self.pos.y = self.rect.centery
            else:
                self.rect.bottom = wall.rect.top
                self.pos.y = self.rect.centery

    def throw_back(self, direction, speed, length, stun_duration):
        self.throw_back_clock.wind_up(length // speed)
        self.speed = direction * speed
        self.stun(stun_duration)

    def stun(self, duration):
        self.stun_clock.wind_up(duration)
        self.block_movement()

    def do_dash(self, stats, invert=False):
        self.speed = (1 - 2 * invert) * self.face * stats["speed"]
        self.dash_clock.wind_up(stats["length"] // stats["speed"])
        self.next_dash_clock.wind_up(stats["rest"])
        self.block_movement()
        stats["sound"].play()

    def dash(self):
        self.do_dash(self.dash_stats)

    def back_dash(self):
        self.do_dash(self.back_dash_stats, True)

    def unblock_movement(self):
        self.can_be_moved = True

    def block_movement(self):
        self.can_be_moved = False

    def stop(self):
        self.speed = const.V_ZERO

    def move(self):
        pass


class Interactive:
    """Interface for objects that can be interacted with"""
    def __init__(self):
        pass

    def interact(self, who):
        pass
