import random

import pygame

from src.framework import const


def init(game):
    for v in dir(game):
        if v.rfind('_group') != -1:
            getattr(game, v).empty()
    # TODO better switch-case
    if game.room_num == 1:
        # TODO shortcut for factory loadings
        game.enemy_factory.load()
        game.box_factory.load()
        game.hud_factory.load()
        game.sword_factory.load()
        game.key_factory.load()
        game.heart_factory.load()
        game.player_factory.load()
        game.door_factory.load()
        game.level_rect = pygame.Rect(0, 0, 3000, 2000)

        # MUSIC INITIALIZATION
        # TODO proper music controller
        if game.painful:
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
            game.box_factory.create(coords)
        enemies_coords = (500, 1300), (900, 1300), (500, 1300), (900, 1300), (500, 1600), (900, 1600), (700, 1450), \
                         (1700, 450), (2200, 450), (2850, 150), (2850, 750), (2100, 1200), (2100, 1500), (
                             1800, 1500), \
                         (2450, 1600), (2500, 1600), (2450, 1550), (2500, 1550)
        for coords in enemies_coords:
            game.enemy_factory.create(coords)
        game.door_factory.create((1450, 125), 2, 5)
        distribute_keys(game, 5)

        # TODO redo walls input because now it is DISGUSTING
        # vertical center walls
        walls_rects = (1400, 900, 200, 500), (1400, 1600, 200, 300), (
            # horizontal center walls
            100, 900, 500, 200), (900, 900, 500, 200), (1600, 900, 500, 200), (2400, 900, 500, 200), (
                          # pillars
                          900, 400, 200, 200, 90), (1400, 400, 200, 200, 120), (1900, 400, 200, 200, 150), (
                          1800, 1300, 200, 200, 30), (
                          # border walls
                          100, 0, 1300, 100), (1600, 0, 1300, 100), (1400, 0, 200, 100, 200), (0, 0, 100, 2000), (
                          0, 1900, 3000, 150), (2900, 0, 100, 2000)
        for wall in walls_rects:
            game.wall_factory.create(wall[:4], wall[-1] if len(wall) == 5 else 50)  # TODO remove this bodge

        # PLAYER INITIALIZING

        game.player = game.player_factory.create((400, 300))
        game.player.fetch_screen()
    if game.room_num == 2:
        print("yay you won now get out")
        game.to_main_menu()


def distribute_keys(game, keys):
    if len(game.enemy_group) < keys:
        raise BaseException("um there is not enough enemies to distribute so much keys")
    while keys > 0:
        en = random.choice(game.enemy_group.sprites())
        if not en.has_key:
            keys -= 1
            en.has_key = True
