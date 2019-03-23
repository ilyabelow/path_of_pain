import pygame
import clock
import constants
import particle
import random


class Healthy:
    def __init__(self,
                 max_health,
                 heal_sounds=None,
                 hit_sounds=None,
                 death_sounds=None,
                 invulnerability=-1,
                 weak_health=0):
        self.max_health = max_health
        self.health = max_health
        self.weak_health = weak_health
        self.invulnerability_clock = clock.Clock(None, invulnerability)

        self.heal_sounds = heal_sounds
        self.hit_sounds = hit_sounds
        self.death_sounds = death_sounds

    def heal(self, amount, weak):
        if not weak:
            self.health = min(self.max_health, self.health + amount)
        else:
            self.weak_health += amount
        if self.death_sounds is not None:
            random.choice(self.heal_sounds).play()
        self.after_healing()

    def after_healing(self):
        pass

    def hit(self, amount, who):
        if self.invulnerability_clock.is_not_running():
            self.invulnerability_clock.wind_up()

            if self.weak_health != 0:
                self.weak_health -= amount
            else:
                self.health -= amount
            if self.hit_sounds is not None:
                random.choice(self.hit_sounds).play()
            self.on_any_health(who)

            if self.health + self.weak_health == 1:  # TODO generalize low health
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


class Bleeding:
    def __init__(self, group, one_dir_stats, all_dir_stats, color):
        self.all_dir_stats = all_dir_stats
        self.one_dir_stats = one_dir_stats
        self.group = group
        self.color = color

    def bleed_one_dir(self, pos, main_direction):
        for i in range(self.one_dir_stats['amount']):
            direction = main_direction.rotate(
                random.randint(-self.one_dir_stats['splash'], self.one_dir_stats['splash']))
            self.group.add(particle.Blood(pos + direction * self.one_dir_stats['offset'],
                                          direction * self.one_dir_stats['speed'],
                                          random.randint(self.one_dir_stats['sizes'][0],
                                                         self.one_dir_stats['sizes'][1]),
                                          self.one_dir_stats['fade'],
                                          self.color))

    def bleed_all_dir(self, pos):
        for i in range(self.all_dir_stats['amount']):
            direction = constants.V_LEFT.rotate(random.randint(-180, 180))
            self.group.add(particle.Blood(pos + direction * self.all_dir_stats['offset'],
                                          direction * self.all_dir_stats['speed'],
                                          random.randint(self.all_dir_stats['sizes'][0],
                                                         self.all_dir_stats['sizes'][1]),
                                          self.one_dir_stats['fade'],
                                          self.color))


class Pickupable:
    def __init__(self):
        pass

    def pickup(self, who):
        pass


# TODO make pickuping for several groups
class Pickuping:
    def __init__(self, what_to_pickup):
        self.what_to_pickup = what_to_pickup

    def pickup(self):
        pick = pygame.sprite.spritecollide(self, self.what_to_pickup, False)
        for p in pick:
            p.pickup(self)


# TODO all common properties of Player and Anemy is bunched up here, needs disassembling to DIFFERENT interfaces
class Moving:
    def __init__(self, pos, collide_with, dash_stats, back_dash_stats):
        # TODO remove dull inits??? (we have to init fields in init}
        self.back_dash_stats = back_dash_stats
        self.dash_stats = dash_stats
        self.rect = None
        self.collide_with = collide_with
        self.face = constants.V_LEFT.rotate(random.randint(-180, 180))

        self.pos = pygame.Vector2(pos)
        self.speed = constants.V_ZERO

        # TODO make up better way to state if the object is moving. This field is used in SOME cases
        self.moving = False
        self.can_be_moved = True  # object's ability to make decision about its movement!!!

        # BASE CLOCKS
        # TODO move to interfaces as well
        self.dash_clock = clock.Clock(self.unblock_movement)
        self.next_dash_clock = clock.Clock(None)
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
        print()
        self.do_dash(self.back_dash_stats, True)

    def unblock_movement(self):
        self.can_be_moved = True

    def block_movement(self):
        self.can_be_moved = False

    def stop(self):
        self.speed = constants.V_ZERO

    def move(self):
        pass
