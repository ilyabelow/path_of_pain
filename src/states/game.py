import random

import pygame

from src.framework import base, controller, const
from src.framework.base import State
from src.framework.const import Button
from src.objects import enemy, obstacle, player, particle, pickupable, sword, hud
from src.states import menu


class Game(State):
    def __init__(self, painful=False):
        State.__init__(self)
        self.painful = painful
        self.window = pygame.display.get_surface().get_rect()
        # TODO move assets init to separate module
        hud.HEART_SPRITE = pygame.image.load("assets/images/heart.png").convert_alpha()
        hud.HEART_EMPTY_SPRITE = pygame.image.load("assets/images/heart_empty.png").convert_alpha()
        hud.STAMINA_SPRITE = pygame.image.load("assets/images/stamina_full.png").convert_alpha()
        hud.STAMINA_EMPTY_SPRITE = pygame.image.load("assets/images/stamina_empty.png").convert_alpha()
        hud.KEY_SPRITE = pygame.image.load("assets/images/key.png").convert_alpha()

        self.WIN_SOUND = pygame.mixer.Sound('assets/sounds/secret_discovered_temp.wav')
        self.WIN_SOUND.set_volume(2)  # TODO tune

        # MUSIC INITIALIZATION
        # TODO proper music controller
        # TODO custom music!
        if self.painful:
            pygame.mixer.music.load('assets/sounds/Furious_Gods.wav')
        else:
            pygame.mixer.music.load('assets/sounds/Gods_and_Glory.wav')
        pygame.mixer.music.set_volume(const.MUSIC_NORMAL_VOLUME)
        pygame.mixer.music.play(loops=-1)

        # GROUPS INITIALIZATION
        self.render_group = base.AdvancedLayeredUpdates()
        # TODO move level generation to separate entity

        self.max_keys = 5
        self.hittable_group = base.AdvancedGroup(self.render_group)
        self.hitter_group = base.AdvancedGroup(self.render_group)
        self.level_rect = pygame.Rect(0, 0, 3000, 2000)
        self.pickupable_group = base.AdvancedGroup(self.render_group)
        self.particle_group = base.AdvancedGroup(self.render_group)
        self.enemy_group = base.AdvancedGroup(self.render_group)
        self.enemy_factory = enemy.EnemyFactory(self, self.enemy_group, self.hittable_group)
        self.box_group = base.AdvancedGroup(self.render_group)
        self.obstacle_group = base.AdvancedGroup(self.render_group)
        self.box_factory = obstacle.BoxFactory(self, self.box_group, self.hittable_group, self.obstacle_group)
        boxes_coords = (200, 200), (250, 200), (250, 250), (200, 350), (1300, 700), (1350, 750), (1450, 750), (
            2400, 200), (2400, 400), (2450, 400), (2650, 350), (2400, 500), (2400, 700), (2500, 400), (
                           2600, 300), (2600, 600), (2700, 400), (2500, 550), (2550, 500), (200, 650), (200, 700), (
                           250, 700), (200, 750), (250, 750), (300, 750), (650, 150), (650, 200), (1100, 1700), (
                           1150, 1700), (1200, 1700), (300, 1450), (250, 1500), (2400, 1450), (2450, 1450), (
                           2500, 1450), (2550, 1450), (2600, 1450), (2400, 1700), (2450, 1700), (2500, 1700), (
                           2550, 1700), (2600, 1700), (2350, 1500), (2350, 1450), (2350, 1550), (2350, 1600), (
                           2350, 1650), (2350, 1700), (2600, 1500), (2600, 1550), (2600, 1600), (2600, 1650), (
                           1800, 1750), (2050, 1700)
        for box in boxes_coords:
            self.box_factory.create(box)
        enemies_coords = (500, 1300), (900, 1300), (500, 1300), (900, 1300), (500, 1600), (900, 1600), (700, 1450), \
                         (1700, 450), (2200, 450), (2850, 150), (2850, 750), (2100, 1200), (2100, 1500), (1800, 1500), \
                         (2450, 1600), (2500, 1600), (2450, 1550), (2500, 1550)
        for coord in enemies_coords:
            self.enemy_factory.create(coord)
        self.sword_factory = sword.SwordFactory(self.hitter_group)  # TODO redundant?
        self.key_factory = pickupable.KeyFactory(self.pickupable_group)
        self.heart_factory = pickupable.HeartFactory(self.pickupable_group)
        self.wall_group = base.AdvancedGroup(self.render_group,
                                             # vertical center walls
                                             obstacle.Wall(pygame.Rect(1400, 900, 200, 500)),
                                             obstacle.Wall(pygame.Rect(1400, 1600, 200, 300)),

                                             # horizontal center walls
                                             obstacle.Wall(pygame.Rect(100, 900, 500, 200)),
                                             obstacle.Wall(pygame.Rect(900, 900, 500, 200)),
                                             obstacle.Wall(pygame.Rect(1600, 900, 500, 200)),
                                             obstacle.Wall(pygame.Rect(2400, 900, 500, 200)),
                                             # pillars
                                             obstacle.Wall(pygame.Rect(900, 400, 200, 200), 90),
                                             obstacle.Wall(pygame.Rect(1400, 400, 200, 200), 120),
                                             obstacle.Wall(pygame.Rect(1900, 400, 200, 200), 150),
                                             obstacle.Wall(pygame.Rect(1800, 1300, 200, 200), 30),

                                             # border walls
                                             obstacle.Wall(pygame.Rect(100, 0, 2800, 100)),
                                             obstacle.Wall(pygame.Rect(0, 0, 100, 2000)),
                                             obstacle.Wall(pygame.Rect(0, 1900, 3000, 150)),
                                             obstacle.Wall(pygame.Rect(2900, 0, 100, 2000)),
                                             )

        self.obstacle_group.add(*self.wall_group)

        self.distribute_keys()
        # PLAYER INITIALIZING
        self.player_group = base.AdvancedGroup(self.render_group)
        if pygame.joystick.get_count() == 0:
            ctrlr = controller.Keyboard()
        else:
            ctrlr = controller.Joystick()
        self.player_factory = player.PlayerFactory(self, self.player_group)
        self.player = self.player_factory.create((400, 300), ctrlr)
        self.player.fetch_screen()

        self.prev_rect = [self.window]
        self.fade = particle.Fade(const.GAME_FADE_IN, False, self.deploy_logo)
        self.render_group.add(self.fade)

    def distribute_keys(self):
        if len(self.enemy_group) < self.max_keys:
            raise BaseException("um there is not enough enemies to distribute so much keys")
        key_amount = self.max_keys
        while key_amount > 0:
            en = random.choice(self.enemy_group.sprites())
            if not en.has_key:
                key_amount -= 1
                en.has_key = True

    def win(self):
        self.player.surprised_clock.wind_up()
        for i in range(15):
            direction = const.V_RIGHT.rotate(random.randint(-180, 180))
            self.particle_group.add(particle.Blood(self.player.pos + const.V_ZERO,
                                                   direction * 5,
                                                   random.randint(10, 20),
                                                   0.5,
                                                   const.C_GOLDEN))
        self.WIN_SOUND.play()

    def to_main_menu(self):
        self.app.switch_state(menu.Menu())

    def reset_level(self):
        # TODO reset level
        self.app.switch_state(Game(self.painful))

    def fade_out(self, action_after_faded):
        self.fade = particle.Fade(const.GAME_FADE_OUT, True, action_after_faded)
        self.render_group.add(self.fade)
        pygame.mixer.fadeout(const.GAME_FADE_OUT)
        pygame.mixer.music.fadeout(const.GAME_FADE_OUT * const.FRAME_RATE)

    def deploy_logo(self):
        self.particle_group.add(
            particle.Title(pygame.image.load('assets/images/{}_level{}.png'.format(1, self.painful * '_painful')),
                           (5, 20, 30, 20)))  # ok stage duration

    def update(self):
        # EVENT HANDLING (Now it is just exiting, hmm)
        for event in pygame.event.get():
            # TODO move to controller!!! and rewrite Controller to listen to events from queue
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.fade_out(self.to_main_menu)
                if event.key == pygame.K_TAB:
                    self.fade_out(self.reset_level)
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == Button.BACK.value:
                    self.fade_out(self.to_main_menu)
                if event.button == Button.START.value:
                    self.fade_out(self.reset_level)
            if event.type == pygame.QUIT:  # hard quit
                pygame.quit()

        # UPDATING
        self.pickupable_group.update()
        self.player_group.update()
        self.hitter_group.update()
        self.enemy_group.update()
        self.particle_group.update()
        self.fade.update()

    def draw(self):
        # DRAWING
        # see what areas are updating
        # self.screen.fill(const.C_BLACK, (0, 0, *const.RESOLUTION))
        screen = pygame.display.get_surface()
        for r in self.prev_rect:
            screen.fill(const.C_BACKGROUND, r)
        rect = self.render_group.draw_all(screen, self.window)
        pygame.display.update()
        self.prev_rect.clear()
        self.prev_rect = rect
