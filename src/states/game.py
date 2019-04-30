import pygame

from src.framework import base, const
from src.framework import controller
from src.framework.base import State
from src.framework.const import Button
from src.objects import enemy, obstacle, player, particle, pickupable, sword, hud
from src.states import menu, level


class Game(State):
    def __init__(self, painful=False):
        State.__init__(self)
        self.painful = painful
        self.window = pygame.display.get_surface().get_rect()

        # TODO move level storage into another entity? or is it a little bit on an overstretch?
        # GROUPS INITIALIZATION
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
        self.interactive_group = base.AdvancedGroup(self.render_group)

        # FACTORIES INITIALIZATION
        self.enemy_factory = enemy.EnemyFactory(self, self.enemy_group, self.hittable_group)
        self.box_factory = obstacle.BoxFactory(self, self.box_group, self.hittable_group, self.obstacle_group)
        self.wall_factory = obstacle.WallFactory(self.wall_group, self.obstacle_group)
        self.hud_factory = hud.HUDFactory(self.render_group)
        self.sword_factory = sword.SwordFactory(self.hitter_group)
        self.key_factory = pickupable.KeyFactory(self.pickupable_group)
        self.heart_factory = pickupable.HeartFactory(self.pickupable_group)
        self.player_factory = player.PlayerFactory(self, self.player_group)
        self.door_factory = obstacle.DoorFactory(self.interactive_group)
        self.fade_factory = particle.FadeFactory(self.particle_group)
        self.title_factory = particle.TitleFactory(self.particle_group)
        # LEVEL INITIALIZATION
        self.level_rect = None
        self.player = None

        if pygame.joystick.get_count() == 0:
            self.input_method = controller.Keyboard()
        else:
            self.input_method = controller.Joystick()
        self.title = None
        self.room_num = 1  # tee hee
        self.prev_rect = None

        self.do_reset_level()

    def to_main_menu(self):
        self.app.switch_state(menu.Menu())

    def reset_level(self, room_num=None):
        self.room_num = room_num if room_num is not None else self.room_num
        self.fade_out(self.do_reset_level)

    def do_reset_level(self):
        level.init(self)
        self.prev_rect = [self.window]
        self.fade_factory.create(const.GAME_FADE_IN, False, self.deploy_logo)

    def fade_out(self, action_after_faded):
        self.fade_factory.create(const.GAME_FADE_OUT, True, action_after_faded)
        pygame.mixer.fadeout(const.GAME_FADE_OUT)
        pygame.mixer.music.fadeout(const.GAME_FADE_OUT * const.FRAME_RATE)

    def deploy_logo(self):
        # TODO remove naming plug
        title_font = pygame.font.Font("assets/fonts/augustus.ttf", 100)
        title = title_font.render(self.title, 10, const.C_BLACK)
        title.blit(title_font.render(self.title, 10, const.C_BLACK), (-1, 0))
        title.blit(title_font.render(self.title, 10, const.C_BLACK), (1, 0))
        title.blit(title_font.render(self.title, 10, const.C_BLACK), (0, -1))
        title.blit(title_font.render(self.title, 10, const.C_BLACK), (0, 1))
        title.blit(title_font.render(self.title, 10, const.C_RED), (0, 0))
        self.title_factory.create(title, (5, 20, 30, 20))

    def update(self):
        # EVENT HANDLING (Now it is just exiting, hmm)
        for event in pygame.event.get():
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

        # UPDATING (order matters?)
        # TODO it should be guaranteed that in one of these updates level will not be reset
        self.pickupable_group.update()
        self.player_group.update()
        self.hitter_group.update()
        self.enemy_group.update()
        self.particle_group.update()  # <------ here goes level reset => fall

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
