import constants
import controller
import obstacle
import pygame
import enemy
import player
import particle
import random


class Game:
    def __init__(self, painful=False):
        # GAME INITIALIZING
        pygame.mixer.pre_init(22050, -16, 4, 64)
        pygame.init()
        pygame.mouse.set_visible(False)
        self.clock = pygame.time.Clock()
        self.painful = painful
        # TODO separate level initialization and application initialization to allow menu and stuff

        # SCREEN INITIALIZATION
        self.screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
        pygame.display.set_caption("Path of Pain")
        # TODO support window resizing and windowed mode
        self.window = self.screen.get_rect()

        # SPRITES INITIALIZATION
        # TODO move to separate namespace
        # TODO makeup proper naming system
        self.PLAYER_SPRITE = pygame.image.load("images/player.png").convert_alpha()
        self.PLAYER_STUNNED_SPRITE = pygame.image.load("images/player_stunned.png").convert_alpha()
        self.ENEMY_STUNNED_SPRITE = pygame.image.load("images/enemy_stunned.png").convert_alpha()
        self.ENEMY_SURPRISED_SPRITE = pygame.image.load("images/enemy_surprised.png").convert_alpha()
        self.ENEMY_SPRITE = pygame.image.load("images/enemy.png").convert_alpha()
        self.HEART_SPRITE = pygame.image.load("images/heart.png").convert_alpha()
        self.HEART_EMPTY_SPRITE = pygame.image.load("images/heart_empty.png").convert_alpha()
        self.HEART_WEAK_SPRITE = pygame.image.load("images/weak_heart.png").convert_alpha()
        self.LITTLE_HEART_SPRITE = pygame.image.load("images/little_heart.png").convert_alpha()
        self.LITTLE_HEART_WEAK_SPRITE = pygame.image.load("images/little_weak_heart.png").convert_alpha()
        self.SWORD_SPRITE = pygame.image.load("images/sword.png").convert_alpha()
        self.SWORD_SWANG_SPRITE = pygame.image.load("images/sword_swang.png").convert_alpha()
        self.BOX_SPRITE = pygame.image.load("images/box.png").convert_alpha()
        pygame.display.set_icon(self.ENEMY_SPRITE)

        # SOUND INITIALIZATION
        # TODO move to separate namespace
        # TODO makeup proper naming system
        self.SWORD_SOUNDS = [pygame.mixer.Sound('sounds/sword_{}.wav'.format(i + 1)) for i in range(5)]
        self.SWORD_WALL_SOUND = pygame.mixer.Sound('sounds/sword_hit_reject.wav')
        self.DASH_SOUND = pygame.mixer.Sound('sounds/hero_dash.wav')
        self.STAB_SOUND = pygame.mixer.Sound('sounds/enemy_damage.wav')
        self.HERO_DAMAGE_SOUND = pygame.mixer.Sound('sounds/hero_damage.wav')
        self.HERO_DEATH_SOUND = pygame.mixer.Sound('sounds/hero_death_extra_details.wav')
        self.WIN_SOUND = pygame.mixer.Sound('sounds/secret_discovered_temp.wav')
        self.WIN_SOUND.set_volume(2)
        self.ENEMY_DASH_SOUND = pygame.mixer.Sound('sounds/ruin_fat_sentry_sword.wav')
        self.ENEMY_DASH_SOUND.set_volume(0.5)
        self.GASP_SOUNDS = [pygame.mixer.Sound('sounds/Ruins_Sentry_Fat_startle_0{}.wav'.format(i + 1)) for i in
                            range(2)]
        self.ATTACK_SOUNDS = [pygame.mixer.Sound('sounds/Ruins_Sentry_Fat_attack_0{}.wav'.format(i + 1)) for i in
                              range(3)]
        self.DEATH_SOUNDS = [pygame.mixer.Sound('sounds/Ruins_Sentry_death_0{}.wav'.format(i + 1)) for i in
                             range(3)]
        self.STEPS_SOUND = pygame.mixer.Sound('sounds/hero_run_footsteps_stone.wav')
        self.HEAL_SOUND = pygame.mixer.Sound('sounds/focus_health_heal.wav')

        self.HEARTBEAT_SOUND = pygame.mixer.Sound('sounds/heartbeat_B_01.wav')
        self.BOX_BREAK_SOUND = [pygame.mixer.Sound('sounds/breakable_wall_hit_{}.wav'.format(i + 1)) for i in range(2)]

        # MUSIC INITIALIZATION
        if painful:
            pygame.mixer.music.load('sounds/Furious_Gods.wav')
        else:
            pygame.mixer.music.load('sounds/Gods_and_Glory.wav')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(loops=-1)

        # LEVEL INITIALIZATION
        # TODO move to separate class and make several levels (haha)
        self.enemies_count = 0  # TODO remove this counter and move enemies in boxes in enemy_group and take len()
        self.level_rect = pygame.Rect(0, 0, 3000, 2000)
        self.box_group = pygame.sprite.Group(
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
        self.wall_group = pygame.sprite.Group(
            # vertical center walls
            obstacle.Wall(pygame.Rect(1400, 900, 200, 500), True),
            obstacle.Wall(pygame.Rect(1400, 1600, 200, 300)),

            # horizontal center walls
            obstacle.Wall(pygame.Rect(100, 900, 500, 200), True),
            obstacle.Wall(pygame.Rect(900, 900, 500, 200), True),
            obstacle.Wall(pygame.Rect(1600, 900, 500, 200), True),
            obstacle.Wall(pygame.Rect(2400, 900, 500, 200), True),
            # pillars
            obstacle.Wall(pygame.Rect(900, 400, 200, 200), True),
            obstacle.Wall(pygame.Rect(1400, 400, 200, 200), True),
            obstacle.Wall(pygame.Rect(1900, 400, 200, 200), True),
            obstacle.Wall(pygame.Rect(1800, 1300, 200, 200), True),

            # border walls
            obstacle.Wall(pygame.Rect(100, 0, 3000, 100), True),
            obstacle.Wall(pygame.Rect(0, 0, 100, 2000)),
            obstacle.Wall(pygame.Rect(0, 1900, 3000, 100)),
            obstacle.Wall(pygame.Rect(2900, 0, 100, 2000)),
            # TODO move
            *self.box_group
        )

        self.enemy_group = pygame.sprite.Group(
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
        self.hitter_group = pygame.sprite.Group()
        self.hud_group = pygame.sprite.Group()
        self.pickupable_group = pygame.sprite.Group()

        self.hittable_group = pygame.sprite.Group(*self.enemy_group, *self.box_group)

        # PLAYER INITIALIZING
        if pygame.joystick.get_count() == 0:
            ctrlr = controller.Keyboard()
        else:
            ctrlr = controller.Joystick()
        self.player = player.Player(self, (400, 300), ctrlr)
        self.player.fetch_screen()

        # GROUPS INITIALIZING
        # TODO reorganize groups (make new group types or start using advanced groups)
        self.player_group = pygame.sprite.GroupSingle(self.player)
        self.particle_group = pygame.sprite.Group()
        self.common_group = pygame.sprite.RenderPlain(*self.wall_group,
                                                      *self.enemy_group,
                                                      *self.player_group,
                                                      *self.pickupable_group)
        self.fade = None

    def win(self):
        for i in range(15):
            direction = constants.V_RIGHT.rotate(random.randint(-180, 180))
            self.particle_group.add(particle.Blood(self.player.pos + constants.V_ZERO,
                                                   direction * 5,
                                                   random.randint(10, 20),
                                                   0.5,
                                                   constants.C_GOLDEN))
        self.WIN_SOUND.play()
        self.enemies_count = -1

    def loop(self):
        self.fade = particle.Fade(constants.fade_in, False)
        running = True
        reset = False  # will the game be reseted or not
        while running:
            # TODO remove this temp solution
            # TODO better win effect
            if self.enemies_count == 0:
                self.win()
            # TODO remove this temp solution
            if self.fade.to_black and self.fade.countdown == -1:
                running = False

            # EVENT HANDLING
            for event in pygame.event.get():
                # TODO move to controller?
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.fade = particle.Fade(constants.fade_out, True)
                    if event.key == pygame.K_TAB:
                        self.fade = particle.Fade(constants.fade_out, True)
                        reset = True
                    if event.key == pygame.K_p:
                        self.fade = particle.Fade(constants.fade_out, True)
                        reset = True
                        self.painful = not self.painful
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == constants.B_BACK:
                        self.fade = particle.Fade(constants.fade_out, True)
                    if event.button == constants.B_START:
                        self.fade = particle.Fade(constants.fade_out, True)
                        reset = True
                    if event.button == constants.B_HOME:
                        self.fade = particle.Fade(constants.fade_out, True)
                        reset = True
                        self.painful = not self.painful
                if event.type == pygame.QUIT:
                    running = False

            # UPDATING
            self.player_group.update()
            self.hitter_group.update()
            self.enemy_group.update()
            self.particle_group.update()
            self.fade.update()

            # DRAWING
            # TODO optimize drawing (naaah...)
            self.screen.fill(constants.C_BACKGROUND)
            # TODO rewrite drawing (add draw to sprites and advanced draw in groups)
            for sprite in self.common_group:
                self.screen.blit(sprite.image, (sprite.rect.x - self.window.x, sprite.rect.y - self.window.y))
            for sprite in self.hitter_group:
                self.screen.blit(sprite.image, (sprite.rect.x - self.window.x, sprite.rect.y - self.window.y))
            self.hud_group.draw(self.screen)
            for sprite in self.particle_group:
                self.screen.blit(sprite.image, (sprite.rect.x - self.window.x, sprite.rect.y - self.window.y))
            self.screen.blit(self.fade.image, self.fade.rect)

            pygame.display.flip()

            # WAITING
            self.clock.tick_busy_loop(constants.FRAME_RATE)

        pygame.quit()
        return reset, self.painful


def main():
    # TODO main menu or something
    restart = True
    painful = False
    while restart:
        the_game = Game(painful)
        restart, painful = the_game.loop()


if __name__ == '__main__':
    main()
