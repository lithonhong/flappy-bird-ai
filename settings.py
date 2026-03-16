import pygame

# window
SCREEN = (500 * 16 / 9, 500)
GAME_SCREEN = (280, SCREEN[1])
FPS = 1200

# controls metadata
BIRD_NUM = 200
GAME_LENGTH = 200
GAME_MAX_Y = GAME_SCREEN[1]
SET_SEED = True
SEED = 805603

# generation
GEN_BAD_RATIO = 0.7
GEN_TWO_PARENT_REPR = 0.8
GEN_ONE_PARENT_REPR = 0
GEN_TOP_SURVIVOR_RATIO = (1 - GEN_ONE_PARENT_REPR - GEN_TWO_PARENT_REPR)
GEN_MUTATION_RATIO = 0.05
GEN_MODIFY_RATIO = 0.2
COLLISION_PENALTY = 50

POPS = [
      0,
      int(GEN_TWO_PARENT_REPR * BIRD_NUM),
      int(GEN_ONE_PARENT_REPR * BIRD_NUM)
]
POPS[0] = BIRD_NUM - sum(POPS)

_good_bird_count = int(BIRD_NUM * (1 - GEN_BAD_RATIO))
BREED_CHANCE = [BIRD_NUM * 2 - i for i in range(_good_bird_count)]
BREED_CHANCE.extend([0 for i in range(BIRD_NUM - _good_bird_count)])
_curr_sum = sum(BREED_CHANCE)
BREED_CHANCE = [i/_curr_sum for i in BREED_CHANCE]

# neurons
NUM_INPUT = 6
NUM_HIDDEN = 7
NUM_OUTPUT = 1

# pipe
PIPE_MIN_Y = 40
PIPE_MAX_Y = 320
PIPE_MIN_WIDTH = 100
PIPE_FIRST_X = 240
PIPE_DISTANCE = 144
GAME_MAX_X = PIPE_DISTANCE * GAME_LENGTH + PIPE_FIRST_X

# world metadata
GRAVITY = 1.5
X_VEL = 3

# bird
BIRD_INIT_X = 60
BIRD_INIT_Y = 240
BIRD_JUMP_VEL = -12
BIRD_JUMP_COOLDOWN = 3
BIRD_TERMINAL_VEL = 16
BIRD_UP_ANGLE = 30
BIRD_DOWN_ANGLE = -60
BIRD_COLOURS = ["red", "yellow", "blue"]
BIRD_CATEGORIES = ["one_parent", "old_bird", "two_parent", "random"]

# text
START_X = 320
START_Y = 20
HEADING_INDENT = 20
FONT_SIZE = 15
GAP = FONT_SIZE + 5
SECTIONS = (180, 160, 160)
DASHBOARD_BG_COLOUR = (120, 150, 180)

# graphs
PERCENTILES = (0.1, 0.25, 0.4, 0.5, 0.6, 0.75, 0.9)
GRAPH_BG_COLOUR = (240, 240, 240)
GRAPH_TEXT_COLOUR = (40, 40, 40)

# images
IMG = {
    "background_day": pygame.image.load("assets/sprites/background-day.png"),
    "base": pygame.image.load("assets/sprites/base.png"),
    "pipe_btm": pygame.image.load("assets/sprites/pipe-green.png")
}

IMG["pipe_top"] = pygame.transform.flip(IMG["pipe_btm"], False, True)

for i in ("red", "blue", "yellow"):
    IMG[f"{i}_bird"] = [
        pygame.image.load(f"assets/sprites/{i}bird-{j}flap.png") for j in ("down", "mid", "up")
    ]
