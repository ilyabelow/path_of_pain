import const
import controller
import obstacle
import pygame
import enemy
import player
import particle
import random
import base
import hud
import pickupable
import sword


class State:
    def __def__(self):
        self.app = None

    def update(self):
        pass

    def draw(self):
        pass

    # TODO shared method to fade out

class Game(State):
    def __init__(self, painful=False):
        State.__init__(self)
        self.painful = painful
        self.window = pygame.display.get_surface().get_rect()
        # TODO move assets init to separate module
        # SPRITES INITIALIZATION
        player.SPRITE = pygame.image.load("assets/images/player.png").convert_alpha()
        player.STUNNED_SPRITE = pygame.image.load("assets/images/player_stunned.png").convert_alpha()
        player.SURPRISED_SPRITE = pygame.image.load("assets/images/player_surprised.png").convert_alpha()
        enemy.STUNNED_SPRITE = pygame.image.load("assets/images/enemy_stunned.png").convert_alpha()
        enemy.SURPRISED_SPRITE = pygame.image.load("assets/images/enemy_surprised.png").convert_alpha()
        enemy.SPRITE = pygame.image.load("assets/images/enemy.png").convert_alpha()
        enemy.KEY_TAKEN_SPRITE = pygame.image.load("assets/images/key_taken.png").convert_alpha()
        hud.HEART_SPRITE = pygame.image.load("assets/images/heart.png").convert_alpha()
        hud.HEART_EMPTY_SPRITE = pygame.image.load("assets/images/heart_empty.png").convert_alpha()
        hud.HEART_WEAK_SPRITE = pygame.image.load("assets/images/weak_heart.png").convert_alpha()
        hud.KEY_SPRITE = pygame.image.load("assets/images/key.png").convert_alpha()  # TODO another image
        pickupable.LITTLE_HEART_SPRITE = pygame.image.load("assets/images/little_heart.png").convert_alpha()
        pickupable.LITTLE_HEART_WEAK_SPRITE = pygame.image.load("assets/images/little_weak_heart.png").convert_alpha()
        pickupable.KEY_SPRITE = pygame.image.load("assets/images/key.png").convert_alpha()
        sword.SPRITE = pygame.image.load("assets/images/sword.png").convert_alpha()
        sword.SWANG_SPRITE = pygame.image.load("assets/images/sword_swang.png").convert_alpha()
        obstacle.BOX_SPRITE = pygame.image.load("assets/images/box.png").convert_alpha()

        # SOUND INITIALIZATION
        sword.SWING_SOUNDS = [pygame.mixer.Sound('assets/sounds/sword_{}.wav'.format(i + 1)) for i in range(5)]
        sword.CLING_SOUND = pygame.mixer.Sound('assets/sounds/sword_hit_reject.wav')

        player.DASH_SOUND = pygame.mixer.Sound('assets/sounds/hero_dash.wav')
        player.DASH_STATS["sound"] = player.DASH_SOUND
        player.BACK_DASH_STATS["sound"] = player.DASH_SOUND
        player.HIT_SOUND = pygame.mixer.Sound('assets/sounds/hero_damage.wav')
        player.DEATH_SOUND = pygame.mixer.Sound('assets/sounds/hero_death_extra_details.wav')
        player.HEAL_SOUND = pygame.mixer.Sound('assets/sounds/focus_health_heal.wav')
        player.HEARTBEAT_SOUND = pygame.mixer.Sound('assets/sounds/heartbeat_B_01.wav')
        player.STEPS_SOUND = pygame.mixer.Sound('assets/sounds/hero_run_footsteps_stone.wav')
        player.STEPS_SOUND.set_volume(1.5)  # TODO tune
        player.PICKUP_SOUND = pygame.mixer.Sound('assets/sounds/shiny_item_pickup.wav')

        enemy.DASH_SOUND = pygame.mixer.Sound('assets/sounds/ruin_fat_sentry_sword.wav')
        enemy.DASH_SOUND.set_volume(0.5)  # TODO tune
        enemy.DASH_STATS["sound"] = enemy.DASH_SOUND
        enemy.STARTLE_SOUNDS = [pygame.mixer.Sound('assets/sounds/Ruins_Sentry_Fat_startle_0{}.wav'.format(i + 1)) for i
                                in
                                range(2)]
        enemy.ATTACK_SOUNDS = [pygame.mixer.Sound('assets/sounds/Ruins_Sentry_Fat_attack_0{}.wav'.format(i + 1)) for i
                               in
                               range(3)]
        enemy.DEATH_SOUNDS = [pygame.mixer.Sound('assets/sounds/Ruins_Sentry_death_0{}.wav'.format(i + 1)) for i in
                              range(3)]
        enemy.HEAL_SOUND = pygame.mixer.Sound('assets/sounds/focus_health_heal.wav')  # TODO find another sound

        enemy.HIT_SOUND = pygame.mixer.Sound('assets/sounds/enemy_damage.wav')

        obstacle.BOX_BREAK_SOUNDS = [pygame.mixer.Sound('assets/sounds/breakable_wall_hit_{}.wav'.format(i + 1)) for i
                                     in
                                     range(2)]

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
        self.hitter_group = base.AdvancedGroup(self.render_group)
        self.level_rect = pygame.Rect(0, 0, 3000, 2000)
        self.pickupable_group = base.AdvancedGroup(self.render_group)
        self.particle_group = base.AdvancedGroup(self.render_group)
        self.box_group = base.AdvancedGroup(self.render_group,
                                            # upper room

                                            obstacle.Box(self, (200, 200)),
                                            obstacle.Box(self, (250, 200)),
                                            obstacle.Box(self, (250, 250)),
                                            obstacle.Box(self, (200, 350)),

                                            obstacle.Box(self, (1300, 700)),
                                            obstacle.Box(self, (1350, 750)),
                                            obstacle.Box(self, (1450, 750)),

                                            obstacle.Box(self, (2400, 200)),
                                            obstacle.Box(self, (2400, 400)),
                                            obstacle.Box(self, (2450, 400)),
                                            obstacle.Box(self, (2650, 350)),
                                            obstacle.Box(self, (2400, 500)),
                                            obstacle.Box(self, (2400, 700)),
                                            obstacle.Box(self, (2500, 400)),
                                            obstacle.Box(self, (2600, 300)),
                                            obstacle.Box(self, (2600, 600)),
                                            obstacle.Box(self, (2700, 400)),
                                            obstacle.Box(self, (2500, 550)),
                                            obstacle.Box(self, (2550, 500)),

                                            obstacle.Box(self, (200, 650)),
                                            obstacle.Box(self, (200, 700)),
                                            obstacle.Box(self, (250, 700)),
                                            obstacle.Box(self, (200, 750)),
                                            obstacle.Box(self, (250, 750)),
                                            obstacle.Box(self, (300, 750)),

                                            obstacle.Box(self, (650, 150)),
                                            obstacle.Box(self, (650, 200)),

                                            # bottom-left room

                                            obstacle.Box(self, (1100, 1700)),
                                            obstacle.Box(self, (1150, 1700)),
                                            obstacle.Box(self, (1200, 1700)),

                                            obstacle.Box(self, (300, 1450)),
                                            obstacle.Box(self, (250, 1500)),

                                            # bottom-right room

                                            obstacle.Box(self, (2400, 1450)),
                                            obstacle.Box(self, (2450, 1450)),
                                            obstacle.Box(self, (2500, 1450)),
                                            obstacle.Box(self, (2550, 1450)),
                                            obstacle.Box(self, (2600, 1450)),

                                            obstacle.Box(self, (2400, 1700)),
                                            obstacle.Box(self, (2450, 1700)),
                                            obstacle.Box(self, (2500, 1700)),
                                            obstacle.Box(self, (2550, 1700)),
                                            obstacle.Box(self, (2600, 1700)),

                                            obstacle.Box(self, (2350, 1500)),
                                            obstacle.Box(self, (2350, 1450)),
                                            obstacle.Box(self, (2350, 1550)),
                                            obstacle.Box(self, (2350, 1600)),
                                            obstacle.Box(self, (2350, 1650)),
                                            obstacle.Box(self, (2350, 1700)),

                                            obstacle.Box(self, (2600, 1500)),
                                            obstacle.Box(self, (2600, 1550)),
                                            obstacle.Box(self, (2600, 1600)),
                                            obstacle.Box(self, (2600, 1650)),

                                            obstacle.Box(self, (1800, 1750)),
                                            obstacle.Box(self, (2050, 1700)),

                                            )
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

        self.obstacle_group = base.AdvancedGroup(self.render_group, *self.wall_group, *self.box_group)

        self.enemy_group = base.AdvancedGroup(self.render_group,
                                              # bottom-left room
                                              enemy.Enemy(self, (500, 1300)),
                                              enemy.Enemy(self, (900, 1300)),
                                              enemy.Enemy(self, (500, 1600)),
                                              enemy.Enemy(self, (900, 1600)),
                                              enemy.Enemy(self, (700, 1450)),

                                              # upper room
                                              enemy.Enemy(self, (1700, 450)),
                                              enemy.Enemy(self, (2200, 450)),
                                              enemy.Enemy(self, (2850, 150)),
                                              enemy.Enemy(self, (2850, 750)),

                                              # bottom-right
                                              enemy.Enemy(self, (2100, 1200)),
                                              enemy.Enemy(self, (2100, 1500)),
                                              enemy.Enemy(self, (1800, 1500)),

                                              enemy.Enemy(self, (2450, 1600)),
                                              enemy.Enemy(self, (2500, 1600)),
                                              enemy.Enemy(self, (2450, 1550)),
                                              enemy.Enemy(self, (2500, 1550)),

                                              )
        self.distribute_keys()
        self.hittable_group = base.AdvancedGroup(self.render_group, *self.enemy_group, *self.box_group)

        # PLAYER INITIALIZING
        if pygame.joystick.get_count() == 0:
            ctrlr = controller.Keyboard()
        else:
            ctrlr = controller.Joystick()
        self.player = player.Player(self, (400, 300), ctrlr)
        self.player.fetch_screen()
        self.player_group = base.AdvancedGroup(self.render_group, self.player)

        self.deploy_logo(1)
        self.prev_rect = [self.window]
        self.fade = particle.Fade(const.GAME_FADE_IN, False)
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
        self.app.switch_state(Menu())

    def reset_level(self):
        # TODO reset level
        self.app.switch_state(Game(self.painful))

    def fade_out(self, action_after_faded):
        self.fade = particle.Fade(const.GAME_FADE_OUT, True, action_after_faded)
        self.render_group.add(self.fade)
        pygame.mixer.fadeout(const.GAME_FADE_OUT)
        pygame.mixer.music.fadeout(const.GAME_FADE_OUT * const.FRAME_RATE)

    def deploy_logo(self, level):
        self.particle_group.add(
            particle.Title(pygame.image.load('assets/images/{}_level{}.png'.format(level, self.painful * '_painful'))))


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
                if event.button == const.B_BACK:
                    self.fade_out(self.to_main_menu)
                if event.button == const.B_START:
                    self.fade_out(self.reset_level)
            if event.type == pygame.QUIT:  # hard quit
                pygame.quit()

        # UPDATING
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


class Menu(State):
    class Title(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            title_font = pygame.font.Font("assets/fonts/augustus.ttf", 128)
            self.image = title_font.render("Path of Pain", 10, const.C_RED)
            self.rect = self.image.get_rect(centerx=const.RESOLUTION[0] / 2, centery=200)

    class Option(pygame.sprite.Sprite):
        def __init__(self, ):
            pygame.sprite.Sprite.__init__(self)

    def __init__(self):
        State.__init__(self)
        self.option_font = pygame.font.Font("assets/fonts/augustus.ttf", 36)
        self.options = ["Play", "play painful", "exit"]
        self.option_sprite = []
        for i in self.options:
            self.option_sprite.append(self.option_font.render(i, 10, const.C_RED))

        pygame.mixer.music.load('assets/sounds/S59-55 Final Stage 3.wav')
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(1)
        self.CHANGE_SOUND = pygame.mixer.Sound('assets/sounds/ui_change_selection.wav')
        self.OK_SOUND = pygame.mixer.Sound('assets/sounds/ui_button_confirm.wav')

        self.result = const.NO
        self.option = const.OPTION_PLAY
        self.option_sprite[self.option] = self.option_font.render(self.options[self.option], 10, const.C_GOLDEN)
        self.fade = particle.Fade(const.MENU_FADE_IN, False)

        self.title_group = pygame.sprite.GroupSingle(self.Title())
        self.option_group = pygame.sprite.OrderedUpdates()

    def draw(self):
        screen = pygame.display.get_surface()
        screen.fill(const.C_BLACK)
        self.title_group.draw(screen)
        screen.blit(self.option_sprite[const.OPTION_PLAY],
                    self.option_sprite[const.OPTION_PLAY].get_rect(centerx=const.RESOLUTION[0] / 2,
                                                                   centery=const.RESOLUTION[1] / 2 - 100))
        screen.blit(self.option_sprite[const.OPTION_PLAY_PAINFUL],
                    self.option_sprite[const.OPTION_PLAY_PAINFUL].get_rect(centerx=const.RESOLUTION[0] / 2,
                                                                           centery=const.RESOLUTION[1] / 2))
        screen.blit(self.option_sprite[const.OPTION_EXIT],
                    self.option_sprite[const.OPTION_EXIT].get_rect(centerx=const.RESOLUTION[0] / 2,
                                                                   centery=const.RESOLUTION[1] / 2 + 100))
        self.fade.draw(screen, None)

        pygame.display.update()

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.change_option((self.option + 1) % const.OPTIONS)
                if event.key == pygame.K_UP:
                    self.change_option((self.option - 1) % const.OPTIONS)
                if event.key == pygame.K_SPACE:
                    self.select_option()
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == const.B_A:
                    self.select_option()
            if event.type == pygame.JOYHATMOTION:
                if event.value[1] == -1:
                    self.change_option((self.option + 1) % const.OPTIONS)
                if event.value[1] == 1:
                    self.change_option((self.option - 1) % const.OPTIONS)
        self.fade.update()

    def select_option(self):
        self.OK_SOUND.play()
        pygame.mixer.music.fadeout(const.MENU_FADE_OUT * const.FRAME_RATE)
        self.fade = particle.Fade(const.MENU_FADE_OUT, True, self.confirm_selection)

    def confirm_selection(self):
        if self.option == const.OPTION_EXIT:
            self.app.stop()
        if self.option == const.OPTION_PLAY:
            self.app.switch_state(Game())
        if self.option == const.OPTION_PLAY_PAINFUL:
            self.app.switch_state(Game(True))

    def change_option(self, option):
        self.option_sprite[self.option] = self.option_font.render(self.options[self.option], 10, const.C_RED)
        self.option_sprite[option] = self.option_font.render(self.options[option], 10, const.C_GOLDEN)
        self.option = option
        self.CHANGE_SOUND.play()


# Context for STATE PATTERN
class Application:
    def __init__(self):
        pygame.mixer.pre_init(22050, -16, 8, 64)
        pygame.init()
        pygame.mouse.set_visible(False)
        pygame.display.set_mode(const.RESOLUTION)
        pygame.display.set_caption("Path of Pain")
        pygame.display.set_icon(pygame.image.load("assets/images/enemy.png"))

        self.clock = pygame.time.Clock()
        self.state = None
        self.switched = False
        self.switch_state(Menu())
        if pygame.joystick.get_count() != 0:
            pygame.joystick.Joystick(0).init()
        self.running = True

    def switch_state(self, state):
        self.state = state
        self.state.app = self
        self.switched = True

    def run(self):
        while self.running:
            self.state.update()
            if self.switched:
                self.switched = False
                continue
            self.state.draw()
            self.clock.tick_busy_loop(const.FRAME_RATE)
        pygame.quit()

    def stop(self):
        self.running = False


def main():
    app = Application()
    app.run()


if __name__ == '__main__':
    main()
