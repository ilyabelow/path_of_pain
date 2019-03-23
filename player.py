import alive
import pygame
import random
import constants
import particle
import sword
import HUD
import clock
import interface

SPRITE = None
STUNNED_SPRITE = None
SURPRISED_SPRITE = None

DASH_SOUND = None
HIT_SOUND = None
DEATH_SOUND = None
HEAL_SOUND = None
HEARTBEAT_SOUND = None
STEPS_SOUND = None  # TODO integrate!

class Player(alive.Alive, interface.Healthy):

    def __init__(self, game, coords, controller):
        alive.Alive.__init__(self, game, coords)
        interface.Healthy.__init__(
            self,
            constants.player_health if not game.painful else 1,
            [HEAL_SOUND],
            [HIT_SOUND],
            [DEATH_SOUND],
            20
        )
        self.rect = pygame.Rect(0, 0, 50, 50)
        self.rect.centerx, self.rect.centery = coords[0], coords[1]
        if not game.painful:
            self.health_hud = HUD.HealthHUD(self)
        self.controller = controller
        self.sword = sword.Sword(self)

        self.surprised_clock = clock.Clock(None, 30)

        self.clock_ticker.add_clock(*[getattr(self, attr) for attr in dir(self) if '_clock' in attr])

    def move(self):
        if self.can_be_moved:
            self.controller.check(self)
        # separate ifs because controller can stop
        if self.can_be_moved:
            # TODO rethink this legacy formula
            self.speed = self.face * self.moving * constants.player_move_speed
        if self.speed:
            self.move_and_collide_with_walls()
            self.fetch_screen()

    def draw(self, screen, window):
        if self.stun_clock.is_running():
            image = STUNNED_SPRITE
        elif self.surprised_clock.is_running():
            image = SURPRISED_SPRITE
        else:
            image = SPRITE
        rotated_image = pygame.transform.rotate(image, self.face.angle_to(constants.V_UP))
        center_rect = rotated_image.get_rect()
        screen.blit(rotated_image,
                    (self.pos.x - window.x - center_rect.w / 2, self.pos.y - window.y - center_rect.w / 2))

    # TODO union them and probably move to base class/interface
    def dash(self):
        # TODO move winding up to base class so time is set on clock init
        self.dash_clock.wind_up(constants.player_dash_duration)
        self.next_dash_clock.wind_up(constants.player_dash_wait)
        self.speed = self.face * constants.player_dash_speed
        self.can_be_moved = False
        DASH_SOUND.play()

    def back_dash(self):
        # TODO same
        self.dash_clock.wind_up(constants.player_back_dash_duration)
        self.next_dash_clock.wind_up(constants.player_back_dash_wait)
        self.speed = -self.face * constants.player_back_dash_speed
        self.can_be_moved = False
        DASH_SOUND.play()

    def on_any_health(self, who):
        self.bleed_one_dir((self.pos - who.pos).normalize())
        if not self.game.painful:
            self.health_hud.makeup()

    def on_low_health(self, who):
        HEARTBEAT_SOUND.play(-1)
        pygame.mixer.music.set_volume(0.2)

    def on_zero_health(self, who):
        HEARTBEAT_SOUND.stop()
        DEATH_SOUND.play()
        self.sword.kill()
        self.kill()
        self.bleed_all_dir()
        pygame.mixer.music.fadeout(2500)

    def on_ok_health(self, who):
        self.throw_back((self.pos - who.pos).normalize(),
                        constants.player_throwback_speed,
                        constants.player_throwback_duration,
                        constants.player_stun_duration)
        self.can_be_moved = False

    def after_healing(self):
        self.health_hud.makeup()
        HEARTBEAT_SOUND.stop()
        pygame.mixer.music.set_volume(0.5)

    def fetch_screen(self):
        self.game.window.centerx = self.rect.centerx
        self.game.window.centery = self.rect.centery
        if self.game.window.top < self.game.level_rect.top:
            self.game.window.top = self.game.level_rect.top
        if self.game.window.bottom > self.game.level_rect.bottom:
            self.game.window.bottom = self.game.level_rect.bottom
        if self.game.window.right > self.game.level_rect.right:
            self.game.window.right = self.game.level_rect.right
        if self.game.window.left < self.game.level_rect.left:
            self.game.window.left = self.game.level_rect.left

    # TODO make beautiful
    # TODO MOVE up to base class or to interface
    def bleed_one_dir(self, main_direction):
        for i in range(10):
            direction = main_direction.rotate(random.randint(-15, 15))
            self.game.particle_group.add(particle.Blood(self.pos + direction * 100,
                                                        direction * 10,
                                                        random.randint(6, 10),
                                                        0.5,
                                                        constants.C_BLACK))

    def bleed_all_dir(self):
        for i in range(20):
            direction = constants.V_RIGHT.rotate(random.randint(-180, 180))
            self.game.particle_group.add(particle.Blood(self.pos + constants.V_ZERO,
                                                        direction,
                                                        random.randint(20, 30),
                                                        0.3,
                                                        constants.C_BLACK))
