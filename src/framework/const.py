"""Module with some application-wide constants"""
from enum import Enum

import pygame

# TODO separate framerate and game ticks
FRAME_RATE = 30
RESOLUTION = (1920, 1080)


# GAMEPAD INPUT
class Button(Enum):
    A = 0
    B = 1
    X = 2
    Y = 3
    LB = 4
    RB = 5
    BACK = 6
    START = 7
    HOME = 8
    LS = 9
    RS = 10


class Axis(Enum):
    LS_H = 0
    LS_V = 1
    LT = 2
    RS_H = 3
    RS_V = 4
    RT = 5


# VECTORS
# TODO make functions that return copy of a vector?
V_UP = pygame.Vector2(0, -1)
V_DOWN = pygame.Vector2(0, 1)
V_RIGHT = pygame.Vector2(1, 0)
V_LEFT = pygame.Vector2(-1, 0)
V_ZERO = pygame.Vector2(0, 0)

# COLOuRS
C_BACKGROUND = (196, 164, 127)
C_RED = (255, 0, 0)
C_BOX = (118, 87, 50)
C_BLACK = (0, 0, 0)
C_WHITE = (255, 255, 255)
C_GOLDEN = (255, 215, 0)

# FADE
GAME_FADE_IN = 5
GAME_FADE_OUT = 10
MENU_FADE_IN = 10
MENU_FADE_OUT = 20

# SPECIAL LAYERS
IMP_PARTICLE_Y = 3000
HUD_Y = 4000
FADE_Y = 5000

# TODO tune
# TODO make proper music box
# MUSIC STATS
MUSIC_NORMAL_VOLUME = 0.3
MUSIC_MUTED_VOLUME = 0.15
MUSIC_FADE_OUT_DEATH = 2500
MUSIC_FADE_OUT_WIN = 1000
