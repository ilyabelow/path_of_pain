import pygame
from enum import Enum


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


# TODO remove this to classes themselves <-- !

# TODO BALANCE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# ENEMY AND PLAYER STATS
enemy_health = 3
enemy_idle_move_speed = 2
enemy_move_speed = 4
enemy_resting_move_speed = 2
enemy_chase_radius = 300
enemy_unchase_radius = 700
enemy_dash_radius = 120
enemy_spot_time = 10
enemy_attack_time = 5
enemy_throwback_length = 15
enemy_throwback_speed = 3
enemy_stun_duration = 7

player_health = 5
player_move_speed = 12
player_invulnerability_duration = 25
player_throwback_length = 144
player_throwback_speed = 36
player_stun_duration = 8

sword_swing_duration = 8, 10, 12
sword_swing_wait = 3, 4, 5  # To avoid spam?????????/
sword_combo_wait = 10, 20, 30

GAME_FADE_IN = 10
GAME_FADE_OUT = 10
MENU_FADE_IN = 30
MENU_FADE_OUT = 30

HUD_Y = 4000
FADE_Y = 5000

# TODO tune
MUSIC_NORMAL_VOLUME = 0.3
MUSIC_MUTED_VOLUME = 0.15
MUSIC_FADE_OUT = 2500


