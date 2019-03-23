import alive
import pygame
import random
import constants
import particle
import clock
import interface

SPRITE = None
STUNNED_SPRITE = None
SURPRISED_SPRITE = None

DASH_SOUND = None
ATTACK_SOUNDS = None
HIT_SOUND = None
DEATH_SOUNDS = None
STARTLE_SOUNDS = None
HEAL_SOUND = None
# TODO make this class more abstract to make building more types of enemies
# TODO MORE ENEMIES MORE CONTENT
class Enemy(alive.Alive, interface.Healthy):

    def __init__(self, game, coords):
        alive.Alive.__init__(self, game, coords)
        interface.Healthy.__init__(
            self,
            constants.enemy_health,
            [HEAL_SOUND],
            [HIT_SOUND],
            DEATH_SOUNDS
        )
        game.enemies_count += 1
        self.rect = pygame.Rect(0, 0, 50, 50)
        self.rect.centerx, self.rect.centery = coords[0], coords[1]
        # CLOCKS
        self.spot_clock = clock.Clock(self.unblock_movement, constants.enemy_spot_time)
        self.prepare_to_dash_clock = clock.Clock(self.dash, constants.enemy_dash_time)
        self.idle_clock = clock.Clock(self.move_in_idle)

        # INITIAL IDLE
        self.idle_clock.wind_up(random.randint(30, 90))
        self.idle = True
        self.moving = random.randint(0, 2)

        self.clock_ticker.add_clock(*[getattr(self, attr) for attr in dir(self) if '_clock' in attr])

    def move(self):
        # TODO remove reference to main player to add compatibility of several players
        # TODO refactor this a bit
        if self.can_be_moved:  # can decide how to move
            # TODO fix problem with normalizing
            dist = self.pos - self.game.player.pos
            if self.idle:
                # start chasing?
                if dist and dist.length() < constants.enemy_chase_radius and self.game.player.alive():
                    self.spot_clock.wind_up()
                    self.speed = constants.V_ZERO
                    self.game.particle_group.add(
                        particle.Exclamation(self.pos + constants.V_RIGHT.rotate(-45) * 40, 10))
                    random.choice(STARTLE_SOUNDS).play()
                    self.face = -dist.normalize()
                    self.can_be_moved = False
                    self.moving = True
                    self.idle = False
                    self.idle_clock.stop()
            else:  # already chasing
                self.face = -dist.normalize()
                # stop chasing?
                if dist.length() > constants.enemy_unchase_radius or not self.game.player.alive():
                    self.idle = True
                    self.moving = False
                    self.can_be_moved = True
                    self.idle_clock.wind_up(random.randint(30, 90))
                # ATTACK???
                elif dist.length() < constants.enemy_dash_radius and self.next_dash_clock.is_not_running():
                    self.prepare_to_dash_clock.wind_up()
                    random.choice(ATTACK_SOUNDS).play()
                    self.speed = constants.V_ZERO
                    self.can_be_moved = False

        if self.can_be_moved:
            # SMART SPEED CALC
            if self.idle:
                speed_abs = constants.enemy_idle_move_speed
            elif self.next_dash_clock.is_running():
                speed_abs = constants.enemy_resting_move_speed
            else:
                speed_abs = constants.enemy_move_speed
            self.speed = self.moving * self.face * speed_abs

        self.move_and_collide_with_walls()
        if self.game.player.rect.colliderect(self.rect):
            self.game.player.hit(1, self)

    def move_in_idle(self):
        if self.moving:
            self.moving = False
            self.idle_clock.wind_up(random.randint(50, 90))
        else:
            self.moving = True
            self.face.rotate_ip(random.randint(-180, 180))
            self.idle_clock.wind_up(random.randint(20, 40))

    def draw(self, screen, window):
        if self.stun_clock.is_running():
            image = STUNNED_SPRITE
        elif self.spot_clock.is_running():
            image = SURPRISED_SPRITE
        else:
            image = SPRITE
        rotated_image = pygame.transform.rotate(image, self.face.angle_to(constants.V_UP))
        center_rect = rotated_image.get_rect(centerx=25, centery=25)
        screen.blit(rotated_image,
                    (self.pos.x - window.x - center_rect.w / 2, self.pos.y - window.y - center_rect.w / 2))

    def on_any_health(self, who):
        self.bleed_one_dir((self.pos - who.pos).normalize())

    def on_zero_health(self, who):
        self.bleed_all_dir()
        self.game.enemies_count -= 1
        self.kill()

    def on_ok_health(self, who):
        self.throw_back((self.pos - who.pos).normalize(),
                        constants.enemy_throwback_speed,
                        constants.enemy_throwback_duration,
                        constants.enemy_stun_duration)

    # TODO this is so similar to player's dash! merge???
    def dash(self):
        self.dash_clock.wind_up(constants.enemy_dash_duration)
        self.next_dash_clock.wind_up(constants.enemy_next_dash_wait)
        self.speed = self.face * constants.enemy_dash_speed
        self.can_be_moved = False
        DASH_SOUND.play()

    # TODO MOVE up to base class or to interface
    def bleed_one_dir(self, main_direction):
        for i in range(7):
            direction = main_direction.rotate(random.randint(-15, 15))
            self.game.particle_group.add(particle.Blood(self.pos + direction * 50,
                                                        direction * 10,
                                                        random.randint(6, 8),
                                                        0.5,
                                                        constants.C_RED))

    def bleed_all_dir(self):
        for i in range(14):
            direction = constants.V_LEFT.rotate(random.randint(-180, 180))
            self.game.particle_group.add(particle.Blood(self.pos + constants.V_ZERO,
                                                        direction,
                                                        random.randint(15, 25),
                                                        1,
                                                        constants.C_RED))
