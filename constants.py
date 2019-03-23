import pygame

# TODO separate framerate and game ticks
FRAME_RATE = 30

# GAMEPAD INPUT
B_A = 0
B_B = 1
B_X = 2
B_Y = 3
B_LB = 4
B_RB = 5
B_BACK = 6
B_START = 7
B_HOME = 8
B_LS = 9
B_RS = 10
A_LS_H = 0
A_LS_V = 1
A_LT = 2
A_RS_H = 3
A_RS_V = 4
A_RT = 5

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

# TODO type specific constants to corresponding classes. HOW?

# BOX TYPES
BOX_EMPTY = 0
BOX_HEALTH = 1
BOX_WEAK_HEALTH = 2
BOX_ENEMY = 3

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

fade_in = 10
fade_out = 10
