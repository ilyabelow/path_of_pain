import pygame
import const
import sword
import hud
import clock
import interface
import base
import pickupable

SPRITE = None
STUNNED_SPRITE = None
SURPRISED_SPRITE = None

DASH_SOUND = None
HIT_SOUND = None
DEATH_SOUND = None
HEAL_SOUND = None
HEARTBEAT_SOUND = None
STEPS_SOUND = None
PICKUP_SOUND = None

DASH_STATS = {"speed": 36, "length": 180, "rest": 15, "sound": DASH_SOUND}
BACK_DASH_STATS = {"speed": 25, "length": 100, "rest": 10, "sound": DASH_SOUND}
BLEED_ONE_DIR_STATS = {'amount': 10, 'splash': 15, 'fade': 0.5, 'sizes': [6, 10], 'speed': 10, 'offset': 100}
BLEED_ALL_DIR_STATS = {'amount': 20, 'fade': 0.3, 'sizes': [20, 30], 'speed': 1, 'offset': 0}


class Player(base.AdvancedSprite, interface.Moving, interface.Healthy, interface.Pickuping, interface.Bleeding):

    def __init__(self, game, coords, controller):
        base.AdvancedSprite.__init__(self)
        interface.Moving.__init__(self, coords, game.obstacle_group, DASH_STATS, BACK_DASH_STATS)
        interface.Healthy.__init__(
            self,
            const.player_health if not game.painful else 1,
            [HEAL_SOUND],
            [HIT_SOUND],
            [DEATH_SOUND],
            20
        )
        interface.Pickuping.__init__(self, game.pickupable_group)
        interface.Bleeding.__init__(
            self,
            game.particle_group,
            BLEED_ONE_DIR_STATS,
            BLEED_ALL_DIR_STATS,
            const.C_BLACK
        )
        self.steps_are_stepping = False
        self.keys = 0
        self.look_away = const.V_ZERO
        self.game = game
        self.rect = pygame.Rect(0, 0, 50, 50)
        self.rect.centerx, self.rect.centery = coords[0], coords[1]
        if not game.painful:
            self.health_hud = hud.HealthHUD(self)
        self.key_hud = hud.KeyHUD(self)
        self.controller = controller
        self.sword = sword.Sword(self)

        self.surprised_clock = clock.Clock(None, 30)

        self.clock_ticker = clock.ClockTicker(self)

    def update(self):
        self.clock_ticker.tick_all()
        self.pickup()
        self.move()

    def do_pickup(self, what):
        if isinstance(what, pickupable.Key):
            self.keys += 1
            PICKUP_SOUND.play()
            self.key_hud.makeup()
            if self.keys == self.game.max_keys:
                self.game.win()
        if isinstance(what, pickupable.Heart):
            self.heal(1, what.weak)

    def can_pickup(self, what):
        return True

    def move(self):
        if self.can_be_moved:
            self.controller.check(self)
        # separate ifs because controller can stop
        if self.can_be_moved:
            if self.moving:
                self.start_stepping()
            else:
                self.stop_stepping()
            self.speed = self.face * self.moving * const.player_move_speed
        if self.speed:
            self.move_and_collide()
        self.fetch_screen()
        self.fetch_layer(self.pos.y)

    def draw(self, screen, window):
        if self.stun_clock.is_running():
            image = STUNNED_SPRITE
        elif self.surprised_clock.is_running():
            image = SURPRISED_SPRITE
        else:
            image = SPRITE
        rotated_image = pygame.transform.rotate(image, self.face.angle_to(const.V_UP))
        center_rect = rotated_image.get_rect()
        return screen.blit(rotated_image,
                           (self.pos.x - window.x - center_rect.w / 2, self.pos.y - window.y - center_rect.w / 2))

    def on_any_health(self, who):
        self.bleed_one_dir(self.pos, (self.pos - who.pos).normalize())
        if not self.game.painful:
            self.health_hud.makeup()

    def on_low_health(self, who):
        HEARTBEAT_SOUND.play(-1)
        pygame.mixer.music.set_volume(const.MUSIC_MUTED_VOLUME)

    def on_zero_health(self, who):
        self.stop_stepping()
        HEARTBEAT_SOUND.stop()
        DEATH_SOUND.play()
        self.sword.kill()
        self.kill()
        self.bleed_all_dir(self.pos)
        pygame.mixer.music.fadeout(const.MUSIC_FADE_OUT)

    def on_ok_health(self, who):
        self.throw_back((self.pos - who.pos).normalize(),
                        const.player_throwback_speed,
                        const.player_throwback_length,
                        const.player_stun_duration)
        self.can_be_moved = False

    def after_healing(self):
        self.health_hud.makeup()
        HEARTBEAT_SOUND.stop()
        pygame.mixer.music.set_volume(const.MUSIC_NORMAL_VOLUME)

    def fetch_screen(self):
        self.game.window.centerx = self.rect.centerx + int(self.look_away.x)
        self.game.window.centery = self.rect.centery + int(self.look_away.y)
        if self.game.window.top < self.game.level_rect.top:
            self.game.window.top = self.game.level_rect.top
        if self.game.window.bottom > self.game.level_rect.bottom:
            self.game.window.bottom = self.game.level_rect.bottom
        if self.game.window.right > self.game.level_rect.right:
            self.game.window.right = self.game.level_rect.right
        if self.game.window.left < self.game.level_rect.left:
            self.game.window.left = self.game.level_rect.left

    def start_stepping(self):
        if not self.steps_are_stepping:
            STEPS_SOUND.play(-1)
            self.steps_are_stepping = True

    def stop_stepping(self):
        if self.steps_are_stepping:
            STEPS_SOUND.stop()
            self.steps_are_stepping = False
