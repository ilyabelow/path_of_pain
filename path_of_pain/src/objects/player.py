"""Module with class for player with all it's logic"""
import pygame

from path_of_pain.src.framework import base
from path_of_pain.src.framework import clock
from path_of_pain.src.framework import interface, const
from path_of_pain.src.objects import pickupable


class PlayerFactory:
    def __init__(self, game, *groups):
        self.groups = groups
        self.flyweight = PlayerFlyweight()
        self.game = game

    def create(self, coords):
        product = Player(self.flyweight, self.game, coords)
        for group in self.groups:
            group.add(product)
        return product


class PlayerFlyweight:
    """
    All the player's assets and constants
    """
    def __init__(self):
        # IMAGES
        self.SPRITE = pygame.image.load(const.IMG_PATH + 'player.png').convert_alpha()
        self.STUNNED_SPRITE = pygame.image.load(const.IMG_PATH + 'player_stunned.png').convert_alpha()
        self.SURPRISED_SPRITE = pygame.image.load(const.IMG_PATH + 'player_surprised.png').convert_alpha()

        # SOUNDS
        self.DASH_SOUND = pygame.mixer.Sound(const.SND_PATH + 'hero_dash.wav')
        self.HIT_SOUND = pygame.mixer.Sound(const.SND_PATH + 'hero_damage.wav')
        self.DEATH_SOUND = pygame.mixer.Sound(const.SND_PATH + 'hero_death_extra_details.wav')
        self.HEAL_SOUND = pygame.mixer.Sound(const.SND_PATH + 'focus_health_heal.wav')
        self.HEARTBEAT_SOUND = pygame.mixer.Sound(const.SND_PATH + 'heartbeat_B_01.wav')
        self.STEPS_SOUND = pygame.mixer.Sound(const.SND_PATH + 'hero_run_footsteps_stone.wav')
        self.STEPS_SOUND.set_volume(1.5)  # TODO tune
        self.PICKUP_SOUND = pygame.mixer.Sound(const.SND_PATH + 'shiny_item_pickup.wav')

        # CONSTANTS FOR ACTIONS
        self.DASH_STATS = {'speed': 36, 'length': 180, 'rest': 5, 'cost': 1, 'sound': self.DASH_SOUND}  # TODO balance
        self.BACK_DASH_STATS = {'speed': 25, 'length': 100, 'rest': 5, 'cost': 1, 'sound': self.DASH_SOUND}
        self.BLEED_ONE_DIR_STATS = {'amount': 10, 'splash': 15, 'fade': 0.5, 'sizes': [6, 10], 'speed': 10,
                                    'offset': 100}
        self.BLEED_ALL_DIR_STATS = {'amount': 20, 'fade': 0.3, 'sizes': [20, 30], 'speed': 1, 'offset': 0}

        # MORE CONSTANTS
        self.MAX_HEALTH = 5
        self.MOVE_SPEED = 12
        self.INVULNERABILITY_DURATION = 25
        self.THROWBACK_LENGTH = 144
        self.THROWBACK_SPEED = 36
        self.STUN_DURATION = 8


class Player(base.AdvancedSprite,
             interface.Moving,
             interface.Healthy,
             interface.Pickuping,
             interface.Bleeding,
             interface.Tired):
    """
    Class that controls player
    """
    def __init__(self, flyweight, game, coords):
        """
        Init player

        :param flyweight: flyweight with all assets and constants
        :param game: game in which player is
        :param coords: initial player coordinates
        """
        base.AdvancedSprite.__init__(self)
        interface.Moving.__init__(self, coords, game.obstacle_group, flyweight.DASH_STATS, flyweight.BACK_DASH_STATS)
        interface.Healthy.__init__(
            self,
            flyweight.MAX_HEALTH if not game.painful else 1,
            [flyweight.HEAL_SOUND],
            [flyweight.HIT_SOUND],
            [flyweight.DEATH_SOUND],
            flyweight.INVULNERABILITY_DURATION
        )
        interface.Pickuping.__init__(self, game.pickupable_group)
        interface.Bleeding.__init__(
            self,
            game.blood_factory,
            flyweight.BLEED_ONE_DIR_STATS,
            flyweight.BLEED_ALL_DIR_STATS,
            const.C_BLACK
        )
        interface.Tired.__init__(self, 10, 7)  # TODO move to constants? TODO balance
        self.steps_are_stepping = False
        self.keys = 0
        self.look_away = const.V_ZERO
        self.game = game
        self.flyweight = flyweight
        self.rect = pygame.Rect(0, 0, 50, 50)  # hitbox
        self.rect.centerx, self.rect.centery = coords[0], coords[1]

        # hud inits
        self.health_hud = game.hud_factory.create_health(self)
        self.key_hud = game.hud_factory.create_keys(self)
        self.stamina_hud = game.hud_factory.create_stamina(self)

        self.sword = game.sword_factory.create(self)
        self.surprised_clock = clock.Clock(None, 30)  # How long player will be :0
        self.clock_ticker = clock.ClockTicker(self)

    def update(self):
        self.clock_ticker.tick_all()
        self.pickup()
        self.move()
        self.stamina_hud.makeup()

    # TODO bleh, redo this
    def do_pickup(self, what):
        if isinstance(what, pickupable.Key):
            self.keys += 1
            self.flyweight.PICKUP_SOUND.play()
            self.key_hud.makeup()
        if isinstance(what, pickupable.Heart):
            self.heal(1)

    def can_pickup(self, what):
        return True

    def move(self):
        if self.can_be_moved:
            self.game.input_method.check(self)
        # separate ifs because controller can stop
        if self.can_be_moved:
            if self.moving:
                self.start_stepping()
            else:
                self.stop_stepping()
            self.speed = self.face * self.moving * self.flyweight.MOVE_SPEED
        if self.speed:
            self.move_and_collide()
        self.fetch_screen()
        self.fetch_layer(self.pos.y)

    def draw(self, screen, window):
        if self.stun_clock.is_running():
            image = self.flyweight.STUNNED_SPRITE
        elif self.surprised_clock.is_running():
            image = self.flyweight.SURPRISED_SPRITE
        else:
            image = self.flyweight.SPRITE
        rotated_image = pygame.transform.rotate(image, self.face.angle_to(const.V_UP))
        center_rect = rotated_image.get_rect()
        return screen.blit(rotated_image,
                           (self.pos.x - window.x - center_rect.w / 2, self.pos.y - window.y - center_rect.w / 2))

    def on_any_health(self, who):
        self.bleed_one_dir(self.pos, (self.pos - who.pos).normalize())
        self.health_hud.makeup()

    def on_low_health(self, who):
        self.flyweight.HEARTBEAT_SOUND.play(-1)
        pygame.mixer.music.set_volume(const.MUSIC_MUTED_VOLUME)

    def on_zero_health(self, who):
        self.stop_stepping()
        self.flyweight.HEARTBEAT_SOUND.stop()
        self.flyweight.DEATH_SOUND.play()
        self.sword.kill()
        self.kill()
        self.bleed_all_dir(self.pos)
        pygame.mixer.music.fadeout(const.MUSIC_FADE_OUT_DEATH)

    def on_ok_health(self, who):
        self.throw_back((self.pos - who.pos).normalize(),
                        self.flyweight.THROWBACK_SPEED,
                        self.flyweight.THROWBACK_LENGTH,
                        self.flyweight.STUN_DURATION)
        self.can_be_moved = False

    def after_healing(self):
        self.health_hud.makeup()
        self.flyweight.HEARTBEAT_SOUND.stop()
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
            self.flyweight.STEPS_SOUND.play(-1)
            self.steps_are_stepping = True

    def stop_stepping(self):
        if self.steps_are_stepping:
            self.flyweight.STEPS_SOUND.stop()
            self.steps_are_stepping = False

    def try_to_dash(self):
        if self.dash_clock.is_not_running() and self.stamina_available(self.dash_stats['cost']):
            self.dash()
            self.stamina_drain(self.dash_stats['cost'])

    def try_to_back_dash(self):
        if self.dash_clock.is_not_running() and self.stamina_available(self.back_dash_stats['cost']):
            self.back_dash()
            self.stamina_drain(self.back_dash_stats['cost'])

    def try_to_interact(self):
        for interactive in self.game.interactive_group:
            interactive.interact(self)

    def surprise_me(self, time):
        self.surprised_clock.wind_up(time)
