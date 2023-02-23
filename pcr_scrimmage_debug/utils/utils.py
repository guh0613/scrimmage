import json
import os.path
from typing import Dict

from configs.path_config import DATA_PATH

DATA_PATH = DATA_PATH / "pcr_scrimmage"
SKILL_PATH = DATA_PATH / "skill_rate.json"
init = {}

# 熟练度字段
SKILL_RATE_NEW = "新手"
SKILL_RATE_ONHAND = "上手"
SKILL_RATE_SKILFUL = "熟练"
SKILL_RATE_ADVANCED = "高手"
SKILL_RATE_MASTER = "大师"
SKILL_RATE_LEGEND = "已经无敌了！"

#
def init_data():
    if not os.path.exists(DATA_PATH):
        os.mkdir(DATA_PATH)
    if not os.path.exists(SKILL_PATH):
        with open(SKILL_PATH, 'x', encoding='utf-8') as f:
            json.dump(init, f, ensure_ascii=False, indent=4)
    pass

def save_skill_data(skill_dict_all):
    with open(SKILL_PATH, 'w', encoding='utf-8') as f:
        json.dump(skill_dict_all, f, ensure_ascii=False, indent=4)

def load_skill_data():
    with open(SKILL_PATH, 'r', encoding='utf-8') as f:
       return json.load(f)

def create_skill_data(uid, skill_dict_all):
    uid = str(uid)
    skill_dict_all[uid] = {"defend" : 0, "attack" : 0, "burst" : 0, "special" : 0}
    return skill_dict_all

def update_skill_data(uid, position: str, skill_dict_all: Dict, num):
    uid = str(uid)
    if not uid in skill_dict_all.keys():
        skill_dict_all[uid] = {"defend": 0, "attack": 0, "burst": 0, "special": 0}
    if position == "all":
        for k,v in skill_dict_all[uid].items():
            skill_dict_all[uid][k] = v+num
    if position == "防御型":
        skill_dict_all[uid]["defend"] = skill_dict_all[uid]["defend"] + num
    if position == "输出型":
        skill_dict_all[uid]["attack"] = skill_dict_all[uid]["attack"] + num
    if position == "爆发型":
        skill_dict_all[uid]["burst"] = skill_dict_all[uid]["burst"] + num
    if position == "特殊型":
        skill_dict_all[uid]["special"] = skill_dict_all[uid]["special"] + num
    return skill_dict_all

def judge_skill_level(data):
    if data <= 3:
        return SKILL_RATE_NEW
    if 3 < data <= 6:
        return SKILL_RATE_ONHAND
    if 6 < data <= 12:
        return SKILL_RATE_SKILFUL
    if 12 < data <= 20:
        return SKILL_RATE_ADVANCED
    if 20 < data <= 40:
        return SKILL_RATE_MASTER
    if data > 40:
        return SKILL_RATE_LEGEND


def get_skill_level(uid, position: str, skill_dict_all: Dict):
    uid = str(uid)
    if position == "all":
        judge = []
        for values in skill_dict_all[uid].values():
            judge.append(judge_skill_level(values))
        return judge
    else:
        return judge_skill_level(skill_dict_all[uid][position])

def get_skill_bonus(uid, position: str, skill_dict_all: Dict):
    uid = str(uid)
    bonus_dict = {}
    if not uid in skill_dict_all.keys():
        skill_dict_all[uid] = {"defend": 0, "attack": 0, "burst": 0, "special": 0}
        return 0
    skilllevel = get_skill_level(uid, position, skill_dict_all)
    if position == "防御型":
        if skilllevel == SKILL_RATE_ONHAND:
            bonus_dict["health"] = 80
            bonus_dict["defend"] = 10
        elif skilllevel == SKILL_RATE_SKILFUL:
            bonus_dict["health"] = 120
            bonus_dict["defend"] = 20
        elif skilllevel == SKILL_RATE_ADVANCED:
            bonus_dict["health"] = 200
            bonus_dict["defend"] = 30
        elif skilllevel == SKILL_RATE_MASTER:
            bonus_dict["health"] = 300
            bonus_dict["defend"] = 40
        elif skilllevel == SKILL_RATE_LEGEND:
            bonus_dict["health"] = 450
            bonus_dict["defend"] = 50
        else:
            return {}
        return bonus_dict

    if position == "输出型":
        if skilllevel == SKILL_RATE_ONHAND:
            bonus_dict["health"] = 50
            bonus_dict["attack"] = 15
        elif skilllevel == SKILL_RATE_SKILFUL:
            bonus_dict["health"] = 100
            bonus_dict["attack"] = 25
        elif skilllevel == SKILL_RATE_ADVANCED:
            bonus_dict["health"] = 150
            bonus_dict["attack"] = 35
        elif skilllevel == SKILL_RATE_MASTER:
            bonus_dict["health"] = 200
            bonus_dict["attack"] = 45
        elif skilllevel == SKILL_RATE_LEGEND:
            bonus_dict["health"] = 300
            bonus_dict["attack"] = 60
            bonus_dict["distance"] = 1
        else:
            return {}
        return bonus_dict

    if position == "爆发型":
        if skilllevel == SKILL_RATE_ONHAND:
            bonus_dict["attack"] = 25
        elif skilllevel == SKILL_RATE_SKILFUL:
            bonus_dict["attack"] = 35
        elif skilllevel == SKILL_RATE_ADVANCED:
            bonus_dict["attack"] = 50
        elif skilllevel == SKILL_RATE_MASTER:
            bonus_dict["attack"] = 60
        elif skilllevel == SKILL_RATE_LEGEND:
            bonus_dict["attack"] = 80
        else:
            return {}
        return bonus_dict

    if position == "特殊型":
        if skilllevel == SKILL_RATE_ONHAND:
            bonus_dict["tp"] = 10
        elif skilllevel == SKILL_RATE_SKILFUL:
            bonus_dict["tp"] = 15
        elif skilllevel == SKILL_RATE_ADVANCED:
            bonus_dict["tp"] = 20
        elif skilllevel == SKILL_RATE_MASTER:
            bonus_dict["tp"] = 30
        elif skilllevel == SKILL_RATE_LEGEND:
            bonus_dict["tp"] = 40
        else:
            return {}
        return bonus_dict


