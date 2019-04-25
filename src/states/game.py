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

        # WIN SOUND
        self.WIN_SOUND = pygame.mixer.Sound('assets/sounds/secret_discovered_temp.wav')
        self.WIN_SOUND.set_volume(2)

        # GROUPS INITIALIZATION
        # TODO move level generation to separate entity
        self.render_group = base.AdvancedLayeredUpdates()
        self.hittable_group = base.AdvancedGroup(self.render_group)
        self.hitter_group = base.AdvancedGroup(self.render_group)
        self.pickupable_group = base.AdvancedGroup(self.render_group)
        self.particle_group = base.AdvancedGroup(self.render_group)
        self.enemy_group = base.AdvancedGroup(self.render_group)
        self.box_group = base.AdvancedGroup(self.render_group)
        self.wall_group = base.AdvancedGroup(self.render_group)
        self.obstacle_group = base.AdvancedGroup(self.render_group)
        self.player_group = base.AdvancedGroup(self.render_group)

        # FACTORIES INITIALIZATION
        self.enemy_factory = enemy.EnemyFactory(self, self.enemy_group, self.hittable_group)
        self.box_factory = obstacle.BoxFactory(self, self.box_group, self.hittable_group, self.obstacle_group)
        self.wall_factory = obstacle.WallFactory(self.wall_group, self.obstacle_group)
        self.hud_factory = hud.HUDFactory(self.render_group)
        self.sword_factory = sword.SwordFactory(self.hitter_group)
        self.key_factory = pickupable.KeyFactory(self.pickupable_group)
        self.heart_factory = pickupable.HeartFactory(self.pickupable_group)
        self.player_factory = player.PlayerFactory(self, self.player_group)

        # LEVEL INITIALIZATION
        self.level_rect = None
        self.max_keys = 0
        self.player = None

        self.room_num = 1
        self.reset_level()

    def init_room(self):
        self.enemy_factory.load()
        self.box_factory.load()
        self.hud_factory.load()
        self.sword_factory.load()
        self.key_factory.load()
        self.heart_factory.load()
        self.player_factory.load()
        for v in dir(self):
            if v.rfind('_group') != -1:
                getattr(self, v).empty()
        # TODO better switch-case
        if self.room_num == 1:
            self.level_rect = pygame.Rect(0, 0, 3000, 2000)

            # MUSIC INITIALIZATION
            # TODO proper music controller
            if self.painful:
                pygame.mixer.music.load('assets/sounds/Furious_Gods.wav')
            else:
                pygame.mixer.music.load('assets/sounds/Gods_and_Glory.wav')
            pygame.mixer.music.set_volume(const.MUSIC_NORMAL_VOLUME)
            pygame.mixer.music.play(loops=-1)

            boxes_coords = (200, 200), (250, 200), (250, 250), (200, 350), (1300, 700), (1350, 750), (1450, 750), (
                2400, 200), (2400, 400), (2450, 400), (2650, 350), (2400, 500), (2400, 700), (2500, 400), (
                               2600, 300), (2600, 600), (2700, 400), (2500, 550), (2550, 500), (200, 650), (200, 700), (
                               250, 700), (200, 750), (250, 750), (300, 750), (650, 150), (650, 200), (1100, 1700), (
                               1150, 1700), (1200, 1700), (300, 1450), (250, 1500), (2400, 1450), (2450, 1450), (
                               2500, 1450), (2550, 1450), (2600, 1450), (2400, 1700), (2450, 1700), (2500, 1700), (
                               2550, 1700), (2600, 1700), (2350, 1500), (2350, 1450), (2350, 1550), (2350, 1600), (
                               2350, 1650), (2350, 1700), (2600, 1500), (2600, 1550), (2600, 1600), (2600, 1650), (
                               1800, 1750), (2050, 1700)
            for coords in boxes_coords:
                self.box_factory.create(coords)
            enemies_coords = (500, 1300), (900, 1300), (500, 1300), (900, 1300), (500, 1600), (900, 1600), (700, 1450), \
                             (1700, 450), (2200, 450), (2850, 150), (2850, 750), (2100, 1200), (2100, 1500), (
                                 1800, 1500), \
                             (2450, 1600), (2500, 1600), (2450, 1550), (2500, 1550)
            for coords in enemies_coords:
                self.enemy_factory.create(coords)
            self.max_keys = 5
            self.distribute_keys()

            # TODO redo walls input because now it is DISGUSTING
            # vertical center walls
            walls_rects = (1400, 900, 200, 500), (1400, 1600, 200, 300), (
                # horizontal center walls
                100, 900, 500, 200), (900, 900, 500, 200), (1600, 900, 500, 200), (2400, 900, 500, 200), (
                              # pillars
                              900, 400, 200, 200, 90), (1400, 400, 200, 200, 120), (1900, 400, 200, 200, 150), (
                              1800, 1300, 200, 200, 30), (
                              # border walls
                              100, 0, 2800, 100), (0, 0, 100, 2000), (0, 1900, 3000, 150), (
                              2900, 0, 100, 2000)
            for wall in walls_rects:
                self.wall_factory.create(wall[:4], wall[-1] if len(wall) == 5 else 50)  # TODO remove this bodge

            # PLAYER INITIALIZING
            if pygame.joystick.get_count() == 0:
                ctrlr = controller.Keyboard()
            else:
                ctrlr = controller.Joystick()
            self.player = self.player_factory.create((400, 300), ctrlr)
            self.player.fetch_screen()

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
        self.init_room()
        self.prev_rect = [self.window]
        # TODO particle factory
        self.fade = particle.Fade(const.GAME_FADE_IN, False, self.deploy_logo)
        self.render_group.add(self.fade)
        self.update()  # TODO remove

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

        # UPDATING (order matters?)
        self.pickupable_group.update()
        self.player_group.update()
        self.hitter_group.update()
        self.enemy_group.update()
        self.particle_group.update()
        self.fade.update()

    def draw(self):
        # DRAWING
        screen = pygame.display.get_surface()
        # see what areas are updating
        # screen.fill(const.C_BLACK, (0, 0, *const.RESOLUTION))
        for r in self.prev_rect:
            screen.fill(const.C_BACKGROUND, r)
        rect = self.render_group.draw_all(screen, self.window)
        pygame.display.update()
        self.prev_rect.clear()
        self.prev_rect = rect
