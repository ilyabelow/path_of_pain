"""Module with main game controller"""

import pygame

from path_of_pain.src.framework import base
from path_of_pain.src.framework import const
from path_of_pain.src.framework import controller
from path_of_pain.src.framework.base import State
from path_of_pain.src.framework.const import Button
from path_of_pain.src.objects import hud, obstacle, enemy, pickupable
from path_of_pain.src.objects import player, particle, sword
from path_of_pain.src.objects import spikes
from path_of_pain.src.states import menu, level


# TODO singletone?
class Game(State):
    """
    Class that create, stores, updates, draws all actual game objects
    """

    def __init__(self):
        State.__init__(self)
        # GROUPS INITIALIZATION
        self.render_group = base.AdvancedLayeredUpdates()
        self.hittable_group = pygame.sprite.Group()
        self.hitter_group = pygame.sprite.Group()
        self.pickupable_group = pygame.sprite.Group()
        self.particle_group = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.box_group = pygame.sprite.Group()
        self.wall_group = pygame.sprite.Group()
        self.obstacle_group = pygame.sprite.Group()
        self.player_group = pygame.sprite.GroupSingle()
        self.interactive_group = pygame.sprite.Group()
        self.fade_group = pygame.sprite.GroupSingle()

        # FACTORIES INITIALIZATION
        # TODO move factories inits to level builder
        # TODO assets inside factories are loaded each level reset, NOT EFFECTIVE
        self.enemy_factory = enemy.EnemyFactory(self, self.enemy_group, self.hittable_group, self.render_group)
        self.box_factory = obstacle.BoxFactory(self, self.box_group, self.hittable_group, self.obstacle_group,
                                               self.render_group)
        self.wall_factory = obstacle.WallFactory(self.wall_group, self.obstacle_group, self.render_group)
        self.hud_factory = hud.HUDFactory(self.render_group)
        self.sword_factory = sword.SwordFactory(self.hitter_group, self.render_group)
        self.key_factory = pickupable.KeyFactory(self.pickupable_group, self.render_group)
        self.heart_factory = pickupable.HeartFactory(self.pickupable_group, self.render_group)
        self.player_factory = player.PlayerFactory(self, self.player_group, self.render_group)
        self.door_factory = obstacle.DoorFactory(self.interactive_group, self.render_group)
        self.fade_factory = particle.FadeFactory(self.fade_group, self.render_group)
        self.spikes_factory = spikes.SpikesFactory(self, self.hitter_group, self.render_group)
        self.title_factory = particle.TitleFactory(self.particle_group, self.render_group)
        # TODO move these to associated classes => do not store them in Game
        self.blood_factory = particle.BloodFactory(self.particle_group, self.render_group)
        self.exclamation_factory = particle.ExclamationFactory(self.particle_group, self.render_group)
        # CONTROLLER INITIALIZATION
        if pygame.joystick.get_count() == 0:
            self.input_method = controller.Keyboard()
        else:
            self.input_method = controller.Joystick()
        # ADDITIONAL LEVEL INITIALIZATION
        # TODO sort there out
        # these None's will be filled later
        self.painful = None
        self.level_rect = None
        self.player = None
        self.title = None
        self.room_num = None  # level number, room_num is, like, a PUN
        # DRAWING TOOLS INITIALIZATION
        self.window = pygame.display.get_surface().get_rect()  # window in which game is drawn
        self.prev_rect = [self.window]  # previously filled rects
        self.fade_factory.create(const.GAME_FADE_IN, False, self.deploy_logo)

    def to_main_menu(self):
        """
        Switches Game state to Menu state

        :return: None
        """
        self.app.switch_state(menu.Menu())

    # TODO sort out all these RESETS (may be good naming system will help)
    def reset_level(self, room_num=None):
        """
        Start fade after which the level will be reset

        :param room_num: number of level which will be set up. don't pass anything and the old level will be reset
        :return: None
        """
        self.room_num = room_num if room_num is not None else self.room_num
        self.fade_out(self.do_reset_level)

    def do_reset_level(self):
        """
        Actually reset level

        :return: None
        """
        # TODO move it somewhere
        if self.room_num == 3:
            print('yay you win now GET OUT')
            self.to_main_menu()
            return
        game_chooser = level.LevelChooser(level.LevelBuilder())
        self.app.switch_state(game_chooser.choose_level(self.room_num, self.painful))

    # TODO the same with fade in I guess
    def fade_out(self, action_after_faded):
        """
        Wrapper around creating fade out that also fade out all sounds

        :param action_after_faded: action that will be performed after fade is over
        :return: None
        """
        self.fade_factory.create(const.GAME_FADE_OUT, True, action_after_faded)
        pygame.mixer.fadeout(const.GAME_FADE_OUT)
        pygame.mixer.music.fadeout(const.GAME_FADE_OUT * const.FRAME_RATE)

    def deploy_logo(self):
        """
        Create cool logo with level name that will fade in and then fade out

        :return: None
        """
        title_font = pygame.font.Font(const.FNT_PATH + 'augustus.ttf', 100)
        # TODO not bodge-like outline drawing
        title = title_font.render(self.title, 10, const.C_BLACK)
        title.blit(title_font.render(self.title, 10, const.C_BLACK), (-1, 0))
        title.blit(title_font.render(self.title, 10, const.C_BLACK), (1, 0))
        title.blit(title_font.render(self.title, 10, const.C_BLACK), (0, -1))
        title.blit(title_font.render(self.title, 10, const.C_BLACK), (0, 1))
        title.blit(title_font.render(self.title, 10, const.C_RED), (0, 0))
        self.title_factory.create(title, (5, 20, 30, 20))

    def update(self):
        """
        Updates all the object and handles exiting

        :return: None
        """
        # EVENT HANDLING (Now it is just exiting, hmm)
        for event in pygame.event.get():
            if self.fade_group.__len__() != 0:
                break  # Do not try to exit again if fade is alredy running
            # TODO move to controller!!! and rewrite Controller to listen to events from queue
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.fade_out(self.to_main_menu)
                if event.key == pygame.K_TAB:
                    self.reset_level()
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == Button.BACK.value:
                    self.fade_out(self.to_main_menu)
                if event.button == Button.START.value:
                    self.reset_level()
            if event.type == pygame.QUIT:  # hard quit
                pygame.quit()

        # UPDATING
        # TODO think if order matters
        self.pickupable_group.update()
        self.player_group.update()
        self.hitter_group.update()
        self.enemy_group.update()
        self.particle_group.update()
        self.fade_group.update()

    def draw(self):
        """
        Draws all the objects

        :return: None
        """
        screen = pygame.display.get_surface()
        # screen.fill(const.C_BLACK, (0, 0, *const.RESOLUTION)) #  see what areas are updating
        for r in self.prev_rect:
            # fill with background not thw whole space but only dirty places: where old objects were drawn
            screen.fill(const.C_BACKGROUND, r)
        # TODO don't draw objects that are not on screen (COMPLICATED)
        rect = self.render_group.draw_all(screen, self.window)
        pygame.display.update()
        self.prev_rect.clear()
        self.prev_rect = rect
