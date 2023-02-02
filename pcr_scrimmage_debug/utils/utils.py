import json
import os.path
from typing import Dict

from configs.path_config import DATA_PATH

DATA_PATH = DATA_PATH / "pcr_scrimmage"
SKILL_PATH = DATA_PATH / "skill_rate.json"
init = {}

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
    if not uid in skill_dict_all[uid].keys:
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
        return "新手"
    if 3 < data <= 6:
        return "上手"
    if 6 < data <= 12:
        return "熟练"
    if 12 < data <= 20:
        return "高手"
    if 20 < data <= 40:
        return "大师"
    if data > 40:
        return "已经无敌了!"


def get_skill_level(uid, position: str, skill_dict_all: Dict):
    uid = str(uid)
    if position == "all":
        judge = []
        for values in skill_dict_all[uid].values():
            judge.append(judge_skill_level(values))
        return judge
    else:
        return judge_skill_level(skill_dict_all[uid][position])