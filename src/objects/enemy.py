import random
import pygame
from src.framework import base, clock, interface, const
from src.objects import particle, pickupable


class EnemyFactory:
    def __init__(self, game, *groups):
        self.game = game
        self.groups = groups
        self.flyweight = EnemyFlyweight()

    def create(self, pos):
        enemy = Enemy(self.flyweight, self.game, pos)
        for group in self.groups:
            group.add(enemy)
        return enemy


class EnemyFlyweight:
    def __init__(self):
        # TEXTURES
        self.STUNNED_SPRITE = pygame.image.load("assets/images/enemy_stunned.png").convert_alpha()
        self.SURPRISED_SPRITE = pygame.image.load("assets/images/enemy_surprised.png").convert_alpha()
        self.SPRITE = pygame.image.load("assets/images/enemy.png").convert_alpha()
        self.KEY_TAKEN_SPRITE = pygame.image.load("assets/images/key_taken.png").convert_alpha()

        # SOUNDS
        self.DASH_SOUND = pygame.mixer.Sound('assets/sounds/ruin_fat_sentry_sword.wav')
        self.DASH_SOUND.set_volume(0.5)  # TODO tune?
        self.STARTLE_SOUNDS = [pygame.mixer.Sound('assets/sounds/Ruins_Sentry_Fat_startle_0{}.wav'.format(i + 1))
                               for i in range(2)]
        self.ATTACK_SOUNDS = [pygame.mixer.Sound('assets/sounds/Ruins_Sentry_Fat_attack_0{}.wav'.format(i + 1))
                              for i in range(3)]
        self.DEATH_SOUNDS = [pygame.mixer.Sound('assets/sounds/Ruins_Sentry_death_0{}.wav'.format(i + 1))
                             for i in range(3)]
        self.HIT_SOUND = pygame.mixer.Sound('assets/sounds/enemy_damage.wav')

        # TODO enums here
        self.DASH_STATS = {"speed": 20, "length": 100, "rest": 30, "sound": self.DASH_SOUND}
        self.BACK_DASH_STATS = None  # Yet?
        self.BLEED_ONE_DIR_STATS = {'amount': 7, 'splash': 15, 'fade': 0.5, 'sizes': [6, 8], 'speed': 10, 'offset': 50}
        self.BLEED_ALL_DIR_STATS = {'amount': 14, 'fade': 1, 'sizes': [15, 25], 'speed': 1, 'offset': 0}

        self.STAY_TIME = (50, 90)
        self.WANDER_TIME = (20, 40)
        self.UNITED_TIME = (30, 90)

        self.HITBOX = (50, 50)


# TODO make this class more abstract to make building more types of enemies
# TODO MORE ENEMIES MORE CONTENT
class Enemy(base.AdvancedSprite, interface.Moving, interface.Healthy, interface.Bleeding, interface.Pickuping):

    def __init__(self, flyweight, game, coords):
        base.AdvancedSprite.__init__(self)
        interface.Moving.__init__(self, coords, game.obstacle_group, flyweight.DASH_STATS, None)
        interface.Healthy.__init__(
            self,
            const.enemy_health,
            [None],
            [flyweight.HIT_SOUND],
            flyweight.DEATH_SOUNDS
        )
        interface.Bleeding.__init__(
            self,
            game.particle_group,
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
        self.spot_clock = clock.Clock(self.unblock_movement, const.enemy_spot_time)
        self.prepare_to_dash_clock = clock.Clock(self.dash, const.enemy_attack_time)
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
            self.game.pickupable_group.add(pickupable.Key(self.pos, self.face))
            self.has_key = False

    def move(self):
        if self.can_be_moved:
            if self.idle:
                self.move_when_idle()
            else:
                self.move_when_chasing()
        if self.can_be_moved:
            if self.idle:
                speed_abs = const.enemy_idle_move_speed
            elif self.next_dash_clock.is_running():
                speed_abs = const.enemy_resting_move_speed
            else:
                speed_abs = const.enemy_move_speed
            self.speed = self.moving * self.face * speed_abs

        self.move_and_collide()
        self.fetch_layer(self.pos.y)
        if self.game.player.rect.colliderect(self.rect):
            self.game.player.hit(1, self)

    def move_when_idle(self):
        dist = self.pos - self.game.player.pos
        if dist and dist.length() < const.enemy_chase_radius and self.game.player.alive():
            self.spot_clock.wind_up()
            self.speed = const.V_ZERO
            self.game.particle_group.add(
                particle.Exclamation(self.pos + const.V_RIGHT.rotate(-45) * 40, 10))  # ! will be place to upper-right
            random.choice(self.flyweight.STARTLE_SOUNDS).play()
            self.drop_key()
            self.face = -dist.normalize()
            self.can_be_moved = False
            self.moving = True
            self.idle = False
            self.idle_clock.hard_stop()

    def move_when_chasing(self):
        dist = self.pos - self.game.player.pos
        self.face = -dist.normalize()  # TODO fix problem with normalizing
        if dist.length() > const.enemy_unchase_radius or not self.game.player.alive():
            self.idle = True
            self.moving = False
            self.can_be_moved = True
            self.idle_clock.wind_up(random.randint(*self.flyweight.UNITED_TIME))
        elif dist.length() < const.enemy_dash_radius and self.next_dash_clock.is_not_running():
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

    def do_pickup(self, what):
        if isinstance(what, pickupable.Key):
            self.has_key = True

    def can_pickup(self, what):
        if isinstance(what, pickupable.Key) and not self.has_key:
            return True
        return False

    def draw(self, screen, window):
        if self.stun_clock.is_running():
            image = self.flyweight.STUNNED_SPRITE
        elif self.spot_clock.is_running():
            image =  self.flyweight.SURPRISED_SPRITE
        else:
            image =  self.flyweight.SPRITE
        if self.has_key:
            # Drawing enemy + key on a bigger surface
            ext_image = pygame.Surface((100, 100), pygame.SRCALPHA, 32)
            ext_image.blit(image, (25, 25))
            ext_image.blit( self.flyweight.KEY_TAKEN_SPRITE, (0, 25))
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
                        const.enemy_throwback_speed,
                        const.enemy_throwback_length,
                        const.enemy_stun_duration)
