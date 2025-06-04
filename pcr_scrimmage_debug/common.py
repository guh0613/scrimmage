"""Common utilities and constants for pcr_scrimmage_debug."""

from typing import Dict

__all__ = [
    "uid2card",
    "GOLD_DICT",
    "SKILL_RATE_DICT",
    "hurt_defensive_calculate",
    "OFFSET_X",
    "OFFSET_Y",
    "RUNWAY_LINE_WDITH",
    "STATU_LINE_WDITH",
    "COLOR_BLACK",
    "COLOR_WRITE",
    "COLOR_RED",
    "COLOR_GREEN",
    "COLOR_BLUE",
    "COLOR_CAM_GREEN",
    "COLOR_CAM_BLUE",
    "NOW_STATU_WAIT",
    "NOW_STATU_SELECT_ROLE",
    "NOW_STATU_OPEN",
    "NOW_STATU_END",
    "NOW_STATU_WIN",
    "NOW_STAGE_WAIT",
    "NOW_STAGE_DICE",
    "NOW_STAGE_SKILL",
    "NOW_STAGE_OUT",
    "NOW_STAGE_FAKEOUT",
    "MAX_PLAYER",
    "MAX_CRIT",
    "MAX_TP",
    "MAX_DIST",
    "ONE_ROUND_TP",
    "ROUND_DISTANCE",
    "ROUND_ATTACK",
    "HIT_DOWN_TP",
    "RET_ERROR",
    "RET_NORMAL",
    "RET_SCUESS",
]

def uid2card(uid: int, user_card_dict: Dict[int, str]) -> str:
    return str(uid) if uid not in user_card_dict else user_card_dict[uid]

GOLD_DICT = {2: [200, 100], 3: [600, 400, 200], 4: [1200, 900, 600, 300]}

SKILL_RATE_DICT = {2: [1, 0], 3: [2.5, 1, 0], 4: [3.5, 2, 1.5, 1]}


def hurt_defensive_calculate(hurt: float, defensive: int) -> float:
    percent = 0.0
    if defensive <= 100:
        percent = defensive * 0.0015
    else:
        if defensive <= 500:
            percent = 100 * 0.0015 + (defensive - 100) * 0.0007
        elif 500 < defensive <= 1000:
            percent = 100 * 0.0015 + 400 * 0.0007 + (defensive - 500) * 0.0005
        else:
            percent = 100 * 0.0015 + 400 * 0.0007 + 500 * 0.0005
    return hurt - hurt * percent

OFFSET_X = 45
OFFSET_Y = 50
RUNWAY_LINE_WDITH = 4
STATU_LINE_WDITH = 2

COLOR_BLACK = (0, 0, 0)
COLOR_WRITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_CAM_GREEN = (30, 230, 100)
COLOR_CAM_BLUE = (30, 144, 255)

NOW_STATU_WAIT = 0
NOW_STATU_SELECT_ROLE = 1
NOW_STATU_OPEN = 2
NOW_STATU_END = 3
NOW_STATU_WIN = 4

NOW_STAGE_WAIT = 0
NOW_STAGE_DICE = 1
NOW_STAGE_SKILL = 2
NOW_STAGE_OUT = 3
NOW_STAGE_FAKEOUT = 4

MAX_PLAYER = 4
MAX_CRIT = 100
MAX_TP = 100
MAX_DIST = 15

ONE_ROUND_TP = 10
ROUND_DISTANCE = 2
ROUND_ATTACK = 10
HIT_DOWN_TP = 20

RET_ERROR = -1
RET_NORMAL = 0
RET_SCUESS = 1

WAIT_TIME = 3
PROCESS_WAIT_TIME = 1
STAGE_WAIT_TIME = 30
