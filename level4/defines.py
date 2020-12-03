class Config:
    EMPTY, WALL, HIDER, SEEKER, OBS, ANNOUNCE, VERIFIED, IMPOSSIBLE = [0, 1, 2, 3, 4, 5, 6, 7]
    DIR = [(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)]
    LEFT_UP, UP, RIGHT_UP, RIGHT, DOWN_RIGHT, DOWN, LEFT_DOWN, LEFT = DIR
    RANGE_SEEKER = 3
    RANGE_HIDER = 2
    TIME_DELAY = 10
    CELL_SIZE = 40
    PREGAME_TURN = 10
    SIGNAL_HEURISTIC = 99999999