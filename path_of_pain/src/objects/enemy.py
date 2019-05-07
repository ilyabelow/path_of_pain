import random
from typing import Tuple

import pygame

from path_of_pain.src.framework import base, clock, const
from path_of_pain.src.framework import interface
from path_of_pain.src.objects import pickupable


class EnemyFactory:
    # TODO type validation for game cannot be done because it requires importing game
    def __init__(self, game, *groups: pygame.sprite.AbstractGroup):
        self.groups = groups
        self.game = game
        self.flyweight = EnemyFlyweight()

    def create(self, coords: Tuple[int, int]):
        product = Enemy(self.flyweight, self.game, coords)
        for group in self.groups:
            group.add(product)
        return product


class EnemyFlyweight:
    def __init__(self):
        # TEXTURES
        self.STUNNED_SPRITE = pygame.image.load(const.IMG_PATH + 'enemy_stunned.png').convert_alpha()
        self.SURPRISED_SPRITE = pygame.image.load(const.IMG_PATH + 'enemy_surprised.png').convert_alpha()
        self.SPRITE = pygame.image.load(const.IMG_PATH + 'enemy.png').convert_alpha()
        self.KEY_TAKEN_SPRITE = pygame.image.load(const.IMG_PATH + 'key_taken.png').convert_alpha()

        # SOUNDS
        self.DASH_SOUND = pygame.mixer.Sound(const.SND_PATH + 'ruin_fat_sentry_sword.wav')
        self.DASH_SOUND.set_volume(0.5)  # TODO tune?
        self.STARTLE_SOUNDS = [pygame.mixer.Sound(const.SND_PATH + 'Ruins_Sentry_Fat_startle_0{}.wav'.format(i + 1))
                               for i in range(2)]
        self.ATTACK_SOUNDS = [pygame.mixer.Sound(const.SND_PATH + 'Ruins_Sentry_Fat_attack_0{}.wav'.format(i + 1))
                              for i in range(3)]
        self.DEATH_SOUNDS = [pygame.mixer.Sound(const.SND_PATH + 'Ruins_Sentry_death_0{}.wav'.format(i + 1))
                             for i in range(3)]
        self.HIT_SOUND = pygame.mixer.Sound(const.SND_PATH + 'enemy_damage.wav')

        # TODO enums here
        self.DASH_STATS = {'speed': 20, 'length': 100, 'rest': 30, 'sound': self.DASH_SOUND}
        self.BACK_DASH_STATS = None  # Yet?
        self.BLEED_ONE_DIR_STATS = {'amount': 7, 'splash': 15, 'fade': 0.5, 'sizes': [6, 8], 'speed': 10, 'offset': 50}
        self.BLEED_ALL_DIR_STATS = {'amount': 14, 'fade': 1, 'sizes': [15, 25], 'speed': 1, 'offset': 0}

        self.STAY_TIME = (50, 90)
        self.WANDER_TIME = (20, 40)
        self.UNITED_TIME = (30, 90)

        self.HITBOX = (50, 50)
        # STATS
        self.health = 3
        self.idle_move_speed = 2
        self.move_speed = 4
        self.resting_move_speed = 2
        self.chase_radius = 300
        self.unchase_radius = 700
        self.dash_radius = 120
        self.spot_time = 10
        self.attack_time = 5
        self.throwback_length = 15
        self.throwback_speed = 3
        self.stun_duration = 7


# TODO make this class more abstract to make building more types of enemies
# TODO MORE ENEMIES MORE CONTENT
class Enemy(base.AdvancedSprite, interface.Moving, interface.Healthy, interface.Bleeding, interface.Pickuping):

    def __init__(self, flyweight: EnemyFlyweight, game, coords: Tuple[int, int]):
        base.AdvancedSprite.__init__(self)
        interface.Moving.__init__(self, coords, game.obstacle_group, flyweight.DASH_STATS, None)
        interface.Healthy.__init__(
            self,
            flyweight.health,
            [None],
            [flyweight.HIT_SOUND],
            flyweight.DEATH_SOUNDS
        )
        interface.Bleeding.__init__(
            self,
            game.blood_factory,
            flyweight.BLEED_ONE_DIR_STATS,
            flyweight.BLEED_ALL_DIR_STATS,
            const.C_RED
        )
        interface.Pickuping.__init__(
            self,
            game.pickupable_group
        )
        self.flyweight = flyweight
        self.game = game
        # TODO make it in one line?
        self.rect = pygame.Rect(0, 0, flyweight.HITBOX[0], flyweight.HITBOX[1])
        self.rect.centerx, self.rect.centery = coords[0], coords[1]
        # CLOCKS
        self.spot_clock = clock.Clock(self.unblock_movement, flyweight.spot_time)
        self.prepare_to_dash_clock = clock.Clock(self.dash, flyweight.attack_time)
        self.idle_clock = clock.Clock(self.move_in_idle)

        # INITIAL IDLE
        # TODO move to strategy
        self.idle_clock.wind_up(random.randint(*flyweight.UNITED_TIME))
        self.idle = True
        self.moving = bool(random.randint(0, 2))
        self.has_key = False

        self.clock_ticker = clock.ClockTicker(self)

    def update(self):
        self.clock_ticker.tick_all()
        if self.spot_clock.is_not_running():
            self.pickup()
        self.move()

    def drop_key(self):
        if self.has_key:
            self.game.key_factory.create((self.pos.x, self.pos.y), self.face)
            self.has_key = False

    def move(self):
        if self.can_be_moved:
            if self.idle:
                self.move_when_idle()
            else:
                self.move_when_chasing()
        if self.can_be_moved:
            if self.idle:
                speed_abs = self.flyweight.idle_move_speed
            elif self.next_dash_clock.is_running():
                speed_abs = self.flyweight.resting_move_speed
            else:
                speed_abs = self.flyweight.move_speed
            self.speed = self.moving * self.face * speed_abs

        self.move_and_collide()
        self.fetch_layer(self.pos.y)
        if self.game.player.rect.colliderect(self.rect):
            self.game.player.hit(1, self)

    def move_when_idle(self):
        dist = self.pos - self.game.player.pos
        if dist and dist.length() < self.flyweight.chase_radius and self.game.player.alive():
            self.spot_clock.wind_up()
            self.speed = const.V_ZERO
            # ! will be place to upper-right
            self.game.exclamation_factory.create(self.pos + const.V_RIGHT.rotate(-45) * 40, 10)
            random.choice(self.flyweight.STARTLE_SOUNDS).play()
            self.drop_key()
            self.face = -dist.normalize()
            self.can_be_moved = False
            self.moving = True
            self.idle = False
            self.idle_clock.stop()

    def move_when_chasing(self):
        dist = self.pos - self.game.player.pos
        self.face = -dist.normalize()  # TODO fix problem with normalizing 0 vector
        if dist.length() > self.flyweight.unchase_radius or not self.game.player.alive():
            self.idle = True
            self.moving = False
            self.can_be_moved = True
            self.idle_clock.wind_up(random.randint(*self.flyweight.UNITED_TIME))
        elif dist.length() < self.flyweight.dash_radius and self.next_dash_clock.is_not_running():
            self.prepare_to_dash_clock.wind_up()
            random.choice(self.flyweight.ATTACK_SOUNDS).play()
            self.speed = const.V_ZERO
            self.can_be_moved = False

    def move_in_idle(self):
        if self.moving:
            self.moving = False
            self.idle_clock.wind_up(random.randint(*self.flyweight.STAY_TIME))
        else:
            self.moving = True
            self.face.rotate_ip(random.randint(-180, 180))  # 360 degrees
            self.idle_clock.wind_up(random.randint(*self.flyweight.WANDER_TIME))

    def do_pickup(self, what: interface.Pickupable):
        if isinstance(what, pickupable.Key):
            self.has_key = True

    def can_pickup(self, what: interface.Pickupable) -> bool:
        return isinstance(what, pickupable.Key) and not self.has_key

    def draw(self, screen: pygame.Surface, window: pygame.Rect) -> pygame.Rect:
        if self.stun_clock.is_running():
            image = self.flyweight.STUNNED_SPRITE
        elif self.spot_clock.is_running():
            image = self.flyweight.SURPRISED_SPRITE
        else:
            image = self.flyweight.SPRITE
        if self.has_key:
            # Drawing enemy + key on a bigger surface
            ext_image = pygame.Surface((100, 100), pygame.SRCALPHA, 32)
            ext_image.blit(image, (25, 25))
            ext_image.blit(self.flyweight.KEY_TAKEN_SPRITE, (0, 25))
            image = ext_image
        rotated_image = pygame.transform.rotate(image, self.face.angle_to(const.V_UP))
        # tl;dr image is padded when rotated, this method allows to center image back
        center_rect = rotated_image.get_rect(centerx=image.get_width() / 2, centery=image.get_width() / 2)
        return screen.blit(rotated_image,
                           (self.pos.x - window.x - center_rect.w / 2, self.pos.y - window.y - center_rect.w / 2))

    def on_any_health(self, who):
        self.bleed_one_dir(self.pos, (self.pos - who.pos).normalize())

    def on_zero_health(self, who):
        self.bleed_all_dir(self.pos)
        self.drop_key()
        self.kill()

    def on_ok_health(self, who):
        self.throw_back((self.pos - who.pos).normalize(),
                        self.flyweight.throwback_speed,
                        self.flyweight.throwback_length,
                        self.flyweight.stun_duration)
