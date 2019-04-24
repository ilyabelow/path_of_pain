import pygame
import random
import const
import particle
import clock
import interface
import base
import pickupable

# TODO move all of these somewhere...
SPRITE = None
STUNNED_SPRITE = None
SURPRISED_SPRITE = None
KEY_TAKEN_SPRITE = None

DASH_SOUND = None
ATTACK_SOUNDS = None
HIT_SOUND = None
DEATH_SOUNDS = None
STARTLE_SOUNDS = None
HEAL_SOUND = None

# TODO enums here?
DASH_STATS = {"speed": 20, "length": 100, "rest": 30, "sound": DASH_SOUND}
BACK_DASH_STATS = None  # Yet
BLEED_ONE_DIR_STATS = {'amount': 7, 'splash': 15, 'fade': 0.5, 'sizes': [6, 8], 'speed': 10, 'offset': 50}
BLEED_ALL_DIR_STATS = {'amount': 14, 'fade': 1, 'sizes': [15, 25], 'speed': 1, 'offset': 0}


# TODO make this class more abstract to make building more types of enemies
# TODO MORE ENEMIES MORE CONTENT
class Enemy(base.AdvancedSprite, interface.Moving, interface.Healthy, interface.Bleeding, interface.Pickuping):
    STAY_TIME = (50, 90)
    WANDER_TIME = (20, 40)
    UNITED_TIME = (30, 90)

    def __init__(self, game, coords):
        base.AdvancedSprite.__init__(self)
        interface.Moving.__init__(self, coords, game.obstacle_group, DASH_STATS, None)
        interface.Healthy.__init__(
            self,
            const.enemy_health,
            [HEAL_SOUND],
            [HIT_SOUND],
            DEATH_SOUNDS
        )
        interface.Bleeding.__init__(
            self,
            game.particle_group,
            BLEED_ONE_DIR_STATS,
            BLEED_ALL_DIR_STATS,
            const.C_RED
        )
        interface.Pickuping.__init__(
            self,
            game.pickupable_group
        )
        self.game = game
        self.rect = pygame.Rect(0, 0, 50, 50)  # hitbox
        self.rect.centerx, self.rect.centery = coords[0], coords[1]
        # CLOCKS
        self.spot_clock = clock.Clock(self.unblock_movement, const.enemy_spot_time)
        self.prepare_to_dash_clock = clock.Clock(self.dash, const.enemy_attack_time)
        self.idle_clock = clock.Clock(self.move_in_idle)

        # INITIAL IDLE
        self.idle_clock.wind_up(random.randint(*self.UNITED_TIME))
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
            # TODO make better key positioning
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
            random.choice(STARTLE_SOUNDS).play()
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
            self.idle_clock.wind_up(random.randint(*self.UNITED_TIME))
        elif dist.length() < const.enemy_dash_radius and self.next_dash_clock.is_not_running():
            self.prepare_to_dash_clock.wind_up()
            random.choice(ATTACK_SOUNDS).play()
            self.speed = const.V_ZERO
            self.can_be_moved = False

    def move_in_idle(self):
        if self.moving:
            self.moving = False
            self.idle_clock.wind_up(random.randint(*self.STAY_TIME))
        else:
            self.moving = True
            self.face.rotate_ip(random.randint(-180, 180))  # 360 degrees
            self.idle_clock.wind_up(random.randint(*self.WANDER_TIME))

    def do_pickup(self, what):
        if isinstance(what, pickupable.Key):
            self.has_key = True

    def can_pickup(self, what):
        if isinstance(what, pickupable.Key) and not self.has_key:
            return True
        return False

    def draw(self, screen, window):
        if self.stun_clock.is_running():
            image = STUNNED_SPRITE
        elif self.spot_clock.is_running():
            image = SURPRISED_SPRITE
        else:
            image = SPRITE
        if self.has_key:
            # Drawing enemy + key on a bigger surface
            ext_image = pygame.Surface((100, 100), pygame.SRCALPHA, 32)
            ext_image.blit(image, (25, 25))
            ext_image.blit(KEY_TAKEN_SPRITE, (0, 25))
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
