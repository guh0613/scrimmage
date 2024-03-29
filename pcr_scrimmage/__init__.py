'''
<A little game base on hoshino_bot, gameplay like RichMan>
Copyright (C) <2021/06/11>  <eggggi>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

from typing import Dict, List
import os
import asyncio
import math
import random
import re

from nonebot.params import CommandArg

from configs.path_config import IMAGE_PATH
from nonebot.adapters.onebot.v11 import Message

from utils import message_builder
from utils.image_utils import pic2b64
from PIL import Image, ImageFont, ImageDraw
from nonebot import on_fullmatch, on_message, logger, on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, GROUP_ADMIN, GROUP_OWNER
from nonebot.matcher import Matcher
from models.bag_user import BagUser

from . import chara
from .utils.utils import (init_data, load_skill_data, create_skill_data, get_skill_level, save_skill_data, update_skill_data, get_skill_bonus
                            , SKILL_RATE_LEGEND, SKILL_RATE_MASTER, SKILL_RATE_ADVANCED, SKILL_RATE_SKILFUL, SKILL_RATE_ONHAND, SKILL_RATE_NEW
                          , getkey)
from .attr import Attr, AttrTextChange
from .buff import BuffEffectType, BuffTriggerType, Buff, BuffType
from .runway_case import (CASE_NONE, CASE_ATTACK, CASE_DEFENSIVE, CASE_HEALTH,
                          CASE_MOVE, CASE_TP, RUNWAY_CASE)
from .role import (EFFECT_BUFF, EFFECT_BUFF_BY_BT, EFFECT_DIZZINESS, EFFECT_HIT_BACK, EFFECT_JUMP, EFFECT_SKILL_CHANGE,
                   EFFECT_STAND, ROLE, EFFECT_LOCKTURN,
                   EFFECT_HURT, EFFECT_ATTR_CHANGE, EFFECT_MOVE, EFFECT_MOVE_GOAL, EFFECT_LIFESTEAL,
                   EFFECT_OUT_TP, EFFECT_OUT_LOCKTURN, EFFECT_IGNORE_DIST, EFFECT_AOE, EFFECT_ELIMINATE,
                   TRIGGER_ME, TRIGGER_ALL_EXCEPT_ME, TRIGGER_ALL, TRIGGER_SELECT, TRIGGER_SELECT_EXCEPT_ME,
                   TRIGGER_NEAR, EFFECT_DEL_BUFF, EFFECT_TP_LOCKTURN, POSITION_DEFEND, POSITION_SPECIAL, POSITION_BURST,
                   POSITION_ATTACK
, PASSIVE_REBORN, EFFECT_REBORN, EFFECT_REVENGE, EFFECT_KILL_REBORN, PASSIVE_HEALTHTP, EFFECT_TP_REQUEST,
                   EFFECT_COST_TP, EFFECT_RANDOM, PASSIVE_SWEETIE, EFFECT_SWEETBUFF, EFFECT_GET_SWEETIE,
                   EFFECT_CAT_POISION, EFFECT_SWEET_LOCKTURN, PASSIVE_ATTACKSPEED)

__zx_plugin_name__ = "大乱斗"
__plugin_usage__ = """
usage：
    基础命令：
	1、大乱斗规则
	可查看大乱斗相关规则
	2、大乱斗角色
	可查看所有可用角色
	3、角色详情 （角色名）
	如：角色详情 黑猫
	可查看角色的基础属性和技能
	4、结束大乱斗
	可以强制结束正在进行的大乱斗游戏
	（该命令只有管理员和房主可用）
一、创建阶段：
	1、创建大乱斗
	2、加入大乱斗
	3、开始大乱斗
二、选择角色阶段：
	1、（角色名）
	如：凯露 / 黑猫
	（名字和外号都行）
三、对战阶段：
	1、丢色子
	2、（技能编号） @xxx
	如：1 @xxx
	发送技能编号并@目标，如果这个技能不需要指定目标，直接发送技能编号即可
	3、查看属性
	可查看自己当前角色详细属性
	4、投降 / 认输
""".strip()
__plugin_des__ = "进行一场激动人心的大乱斗"
__plugin_cmd__ = ["大乱斗规则/创建大乱斗"]
__plugin_type__ = ("群内小游戏",)
__plugin_version__ = 1.0
__plugin_author__ = "egggi"
__plugin_settings__ = {
    "level": 5,  # 群权限等级，请不要设置为1或999，若无特殊情况请设置为5
    "default_status": True,  # 进群时的默认开关状态
    "limit_superuser": False,  # 开关插件的限制是否限制超级用户
    "cmd": ['大乱斗'],  # 命令别名，主要用于帮助和开关
}

info = on_command("角色详情", priority=5, block=True)
prop = on_fullmatch("查看属性", priority=5, block=True)
finish = on_fullmatch("结束大乱斗", priority=5, block=True)
rule = on_fullmatch("大乱斗规则", priority=4, block=True)
character = on_fullmatch("大乱斗角色", priority=5, block=True)
surrend = on_fullmatch("认输", priority=5, block=True)
skill = on_message(priority=999, block=True)
dice = on_command('丢色子', aliases={"丢"}, priority=5, block=True)
selectcha = on_message(priority=999, block=True)
start = on_fullmatch("开始大乱斗", priority=5, block=True)
join = on_fullmatch("加入大乱斗", priority=5, block=True)
create = on_fullmatch("创建大乱斗", priority=5, block=True)
skillbonus = on_fullmatch("熟练度奖励", priority=5, block=True)

FILE_PATH = os.path.dirname(__file__)

IMAGE_PATH = IMAGE_PATH / "pcr_scrimmage"

if not os.path.exists(IMAGE_PATH):
    os.mkdir(IMAGE_PATH)
    logger.info('create folder succeed')


init_data()

async def get_user_card_dict(bot, group_id):
    mlist = await bot.get_group_member_list(group_id=group_id)
    d = {}
    for m in mlist:
        d[m['user_id']] = m['card'] if m['card'] != '' else m['nickname']
    return d


def uid2card(uid, user_card_dict):
    return str(uid) if uid not in user_card_dict.keys() else user_card_dict[uid]

##结算时可以获得的金币
GOLD_DICT = {
    2:[200, 100],
    3:[600, 400, 200],
    4:[1200, 900, 600, 300]
}

SKILL_RATE_DICT = {
    2:[1, 0],
    3:[2.5, 1, 0],
    4:[3.5, 2, 1.5, 1]
}

# 防御力计算机制。
# 100点防御力内，每1点防御力增加0.15%伤害减免；
# 到达100点防御力后，每一点防御力只可获得0.12%伤害减免；
# 100点防御力后，每1点防御力增加0.05%伤害减免；
# 最高有效防御力为1000
# （防御力可无限提升，但最高只能获得57%伤害减免）
def hurt_defensive_calculate(hurt, defensive):
    percent = 0.0
    if defensive <= 100:
        percent = defensive * 0.0015
    else:
        if defensive <= 1000:
            percent = 100 * 0.0015 + (defensive - 100) * 0.0005
        else:
            percent = 100 * 0.0012 + 900 * 0.0005
    return hurt - hurt * percent


###显示偏移###	（可以改）
OFFSET_X = 45  # 整体右移
OFFSET_Y = 50  # 整体下移

###线宽###		（别改）
RUNWAY_LINE_WDITH = 4  # 跑道线宽
STATU_LINE_WDITH = 2  # 状态条线宽 血条tp条

###常用颜色###
COLOR_BLACK = (0, 0, 0)
COLOR_WRITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_CAM_GREEN = (30, 230, 100)  # 血条填充色
COLOR_CAM_BLUE = (30, 144, 255)  # tp条填充色

###当前房间状态###
NOW_STATU_WAIT = 0
NOW_STATU_SELECT_ROLE = 1
NOW_STATU_OPEN = 2
NOW_STATU_END = 3
NOW_STATU_WIN = 4

###当前玩家处于什么阶段###
NOW_STAGE_WAIT = 0  # 等待
NOW_STAGE_DICE = 1  # 丢色子
NOW_STAGE_SKILL = 2  # 释放技能
NOW_STAGE_OUT = 3  # 出局
NOW_STAGE_FAKEOUT = 4 # 假死

MAX_PLAYER = 4  # 最大玩家数量
MAX_CRIT = 100  # 最大暴击
MAX_TP = 100  # tp值上限
MAX_DIST = 15  # 最大攻击距离

ONE_ROUND_TP = 10  # 单回合获得tp量
ROUND_DISTANCE = 2  # 每隔x回合增加的攻击距离(x为当前存活人数)
ROUND_ATTACK = 10  # 每隔x回合增加的攻击力
HIT_DOWN_TP = 20  # 击倒获得的tp

RET_ERROR = -1  # 错误
RET_NORMAL = 0
RET_SCUESS = 1  # 成功


# 角色
class Role:
    def __init__(self, user_id) -> None:
        self.user_id = user_id  # 玩家的qq号

        self.role_id = 0  # 角色编号
        self.name = ''  # 角色名
        self.role_icon = None  # 角色头像
        self.player_num = 0  # 玩家在这个房间的编号
        self.room_obj = None  # 房间对象
        self.position = '' # 角色定位

        self.attr = {}  # 角色属性列表
        '''
		{
			Attr.xx = 数值,
			Attr.xx = 数值,
		}
		'''

        self.buff = {}  # 角色buff列表
        '''
		NomalBuffFlag: 用来标记是否是普通buff，该类buff在结束后会返还扣除的属性值或扣除增加的属性值
		NomalBuffChangeNum: 用来记录普通buff改变的数值，用来处理有上限的属性
		{
			BuffType1 = [数值, 次数, NomalBuffFlag, NomalBuffChangeNum],
			BuffType2 = [数值, 次数, NomalBuffFlag, NomalBuffChangeNum],
		}
		'''

        self.now_location = 0  # 当前位置
        self.now_stage = NOW_STAGE_WAIT  # 当前处于什么阶段
        self.skip_turn = 0  # 跳过x回合
        self.reborn_turn = 3 # 复活所需回合数
        self.revenge = 0 # 复仇对象
        self.costtp = 0
        self.sweetie = 0 # 嘉心糖数量
        self.lastsweetie = -1
        self.catpoison = 0

        self.passive = ''
        self.active_skills = []  # 技能列表
        self.passive_skills = []  # 被动列表

    # 选择角色后对数据的初始化
    def initData(self, role_id, room_obj):
        image = IMAGE_PATH / "chara" / f"{role_id}31.png"
        role_data = ROLE[role_id]


        if role_data:
            self.role_id = role_id

            self.name = role_data['name']
            self.role_icon = Image.open(image)
            self.room_obj: PCRScrimmage = room_obj
            self.position = role_data['position']

            self.attr[Attr.MAX_HEALTH] = role_data['health']
            self.attr[Attr.NOW_HEALTH] = self.attr[Attr.MAX_HEALTH]
            self.attr[Attr.DISTANCE] = role_data['distance']
            self.attr[Attr.ATTACK] = role_data['attack']
            self.attr[Attr.DEFENSIVE] = role_data['defensive']
            self.attr[Attr.CRIT] = role_data['crit']
            self.attr[Attr.CRIT_HURT] = 2
            self.attr[Attr.NOW_TP] = role_data['tp']
            self.attr[Attr.MAX_TP] = MAX_TP

            self.attr[Attr.COST_HEALTH] = 0

            self.passive = role_data['passive'] if role_data.get('passive', -1) != -1 else ''
            # 游戏开始时先计算一次嘉然的属性
            if self.passive == PASSIVE_SWEETIE:
                self.sweetie = 3
                self.sweetiecalculate(True)
            self.active_skills = role_data['active_skills']
            self.passive_skills = role_data['passive_skills']

        bonus_dict = get_skill_bonus(self.user_id, self.position, load_skill_data())
        for k,v in bonus_dict.items():
            if k == "defend":
                self.attr[Attr.DEFENSIVE] += v
            if k == "health":
                self.attr[Attr.MAX_HEALTH] += v
                self.attr[Attr.NOW_HEALTH] += v
            if k == "attack":
                self.attr[Attr.ATTACK] += v
            if k == "distance":
                self.attr[Attr.DISTANCE] += v
            if k == "tp":
                self.attr[Attr.NOW_TP] += v

    # 属性数值改变的统一处理
    def attrChange(self, attr_type, num):
        if self.now_stage in (NOW_STAGE_OUT, NOW_STAGE_FAKEOUT): return

        # 属性数值改变前的处理
        if attr_type == Attr.NOW_HEALTH and num < 0:
            # 如果生命值减少，则按百分比回复tp
            hurt_tp = math.floor(abs(num) / self.attr[Attr.MAX_HEALTH] * 100 / 2)
            self.attrChange(Attr.NOW_TP, hurt_tp)

        self.attr[attr_type] += num

        # 属性数值改变后的处理
        if attr_type == Attr.NOW_HEALTH and num < 0 and self.passive == PASSIVE_SWEETIE:
            # 重新计算嘉然的属性
            self.sweetiecalculate()
        if attr_type == Attr.MAX_HEALTH and num > 0:
            # 如果增加的是生命最大值，则当前生命也增加同等数值
            self.attr[Attr.NOW_HEALTH] += num
        if attr_type == Attr.MAX_TP and num > 0:
            # 如果增加的是tp最大值，则当前tp也增加同等数值
            self.attr[Attr.NOW_TP] += num
        if ((attr_type == Attr.NOW_HEALTH or attr_type == Attr.MAX_HEALTH) and
                self.attr[Attr.NOW_HEALTH] > self.attr[Attr.MAX_HEALTH]):
            # 当前生命值不能超过最大生命值
            self.attr[Attr.NOW_HEALTH] = self.attr[Attr.MAX_HEALTH]
        if ((attr_type == Attr.NOW_TP or attr_type == Attr.MAX_TP) and
                self.attr[Attr.NOW_TP] > self.attr[Attr.MAX_TP]):
            # 不能超过最大tp
            self.attr[Attr.NOW_TP] = self.attr[Attr.MAX_TP]
        if attr_type == Attr.DISTANCE and self.attr[Attr.DISTANCE] > MAX_DIST:
            # 不能超过最大攻击距离
            self.attr[Attr.DISTANCE] = MAX_DIST
        if attr_type == Attr.CRIT and self.attr[Attr.CRIT] > MAX_CRIT:
            # 不能超过最大暴击
            self.attr[Attr.CRIT] = MAX_CRIT

        # 已消耗生命值特殊处理
        if attr_type == Attr.NOW_HEALTH:
            self.attr[Attr.COST_HEALTH] = self.attr[Attr.MAX_HEALTH] - self.attr[Attr.NOW_HEALTH]



        if self.attr[attr_type] <= 0:
            self.attr[attr_type] = 0
            if self.costtp == 1:
                if attr_type == Attr.NOW_TP:
                    self.room_obj.outDispose(self)
                elif attr_type == Attr.NOW_HEALTH:
                    self.room_obj.outDispose(self)
            else:
                if attr_type == Attr.NOW_HEALTH:
                    if self.passive == PASSIVE_REBORN:
                        self.room_obj.outDispose(self, True, self.reborn_turn)
                    else:
                        # 如果是生命值降为0，则调用出局接口
                        self.room_obj.outDispose(self)
        return self.attr[attr_type]

    # 位置改变	flag:如果为真，则直接设置固定位置；如果为假，根据原位置改变
    def locationChange(self, num, runway, flag=False):
        if self.now_stage in (NOW_STAGE_OUT, NOW_STAGE_FAKEOUT): return
        runway[self.now_location]["players"].remove(self.user_id)
        if flag:
            self.now_location = num
        else:
            self.now_location += num
        while (self.now_location >= len(runway) or self.now_location < 0):
            if self.now_location >= len(runway):
                self.now_location -= len(runway)
            elif self.now_location < 0:
                self.now_location += len(runway)
        runway[self.now_location]["players"].append(self.user_id)

    # 状态改变
    def stageChange(self, stage):
        self.now_stage = stage

    # 眩晕x回合
    def dizziness(self, turn):
        self.skip_turn = turn

    # 被攻击
    def beHurt(self, num):
        if self.costtp == 1:
            num = self.buffTriggerByTriggerType(BuffTriggerType.Hurt, num)
            num = math.floor(num * 0.1)
            self.attrChange(Attr.NOW_TP, num)
        else:
            num = self.buffTriggerByTriggerType(BuffTriggerType.Hurt, num)
            self.attrChange(Attr.NOW_HEALTH, num)
        return num

    # 添加buff
    def addBuff(self, buff_info):
        self.buff[buff_info[0]] = [buff_info[1], buff_info[2], 0, 0]

    # 删除buff（不要在迭代self.buff时调用）
    def deleteBuff(self, buff_type):
        if buff_type in self.buff:
            trigger_type = Buff[buff_type]['trigger_type']
            if (trigger_type == BuffTriggerType.Normal or
                trigger_type == BuffTriggerType.NormalSelf or
                trigger_type == BuffTriggerType.Attack) and 'attr_type' in Buff[buff_type]:
                self.attrChange(Buff[buff_type]['attr_type'], -self.buff[buff_type][3])
            del self.buff[buff_type]

    # 删除失效buff
    def deleteInvalidBuff(self):
        buff_keys = []
        for keys in self.buff.keys():
            buff_keys.append(keys)
        for buff_type in buff_keys:
            if self.buff[buff_type][1] <= 0:
                self.deleteBuff(buff_type)

    # 通过触发类型触发buff
    def buffTriggerByTriggerType(self, trigger_type, num=0):
        for buff_type in self.buff.keys():
            need_trigger_type = Buff[buff_type]['trigger_type']
            if need_trigger_type == trigger_type:
                effect_type = Buff[buff_type]['effect_type']
                num = self.buffEffect(trigger_type, effect_type, buff_type, num)
            if len(self.buff) == 0: break
        return num

    # 通过buff类型触发buff
    def buffTriggerByBuffType(self, buff_type, num=0):
        trigger_type = Buff[buff_type]['trigger_type']
        effect_type = Buff[buff_type]['effect_type']
        if buff_type in self.buff:
            num = self.buffEffect(trigger_type, effect_type, buff_type, num)
        return num

    # buff效果生效
    def buffEffect(self, trigger_type, effect_type, buff_type, num):
        if effect_type == BuffEffectType.Attr:
            attr_type = Buff[buff_type]['attr_type']
            if (trigger_type == BuffTriggerType.Normal or
                    trigger_type == BuffTriggerType.NormalSelf or
                    trigger_type == BuffTriggerType.Attack):
                if self.buff[buff_type][2] == 0:
                    old_num = self.attr[attr_type]
                    new_num = self.attrChange(attr_type, self.buff[buff_type][0])
                    self.buff[buff_type][2] = 1
                    self.buff[buff_type][3] = new_num - old_num
            else:
                self.attrChange(attr_type, self.buff[buff_type][0])
        elif effect_type == BuffEffectType.Shield:
            num += self.buff[buff_type][0]
            self.buff[buff_type][0] += num - self.buff[buff_type][0]
            if num > 0: num = 0
        elif effect_type == BuffEffectType.Blind:
            num = 0
        elif effect_type == BuffEffectType.Prop:
            self.sweetie += self.buff[buff_type][0]
            self.sweetiecalculate(True)

        self.buff[buff_type][1] -= 1

        return num

    # 检查当前状态
    def checkStatu(self, scrimmage):
        msg = [
            f"玩家：{uid2card(self.user_id, scrimmage.user_card_dict)}",
            f"角色：{self.name}",
            f"生命值：{self.attr[Attr.NOW_HEALTH]}/{self.attr[Attr.MAX_HEALTH]}",
            f"TP：{self.attr[Attr.NOW_TP]}",
            f"攻击距离：{self.attr[Attr.DISTANCE]}",
            f"攻击力：{self.attr[Attr.ATTACK]}",
            f"防御力：{self.attr[Attr.DEFENSIVE]}",
            f"暴击率：{self.attr[Attr.CRIT]}%",
            f"暴击伤害：{self.attr[Attr.CRIT_HURT]}倍",
            f'位置：{self.now_location}'
        ]
        if self.passive == PASSIVE_SWEETIE:
            msg.append(f'嘉心糖数量：{self.sweetie}')
        if self.passive == PASSIVE_ATTACKSPEED:
            msg.append(f'攻击速度：{self.attr[Attr.ATTACK_SPEED]}')
        if len(self.buff) != 0:
            msg.append('\nbuff效果列表:')
            for buff_type, buff_info in self.buff.items():
                buff_text: str = Buff[buff_type]['text']
                buff_text = buff_text.format(abs(buff_info[0]), buff_info[1] == 0 and 1 or (
                        buff_info[1] > 10000 and "无限" or buff_info[1]))
                msg.append(f'{Buff[buff_type]["name"]}:{buff_text}')
        return msg

    # 计算嘉然的属性
    def sweetiecalculate(self, isnothurt=False):
        role_data = ROLE[self.role_id]
        if isnothurt:
            pass
        else:
            sweetienum = math.ceil((self.attr[Attr.NOW_HEALTH] - role_data['health']) / 150)
            self.sweetie = sweetienum if sweetienum >= 0 else 0
        if self.sweetie > 10:
            self.sweetie = 10
        maxhealth = role_data['health'] + (150 * self.sweetie)
        num = maxhealth - self.attr[Attr.MAX_HEALTH]
        # 如果是正收益，则生命值一起增加
        if num > 0:
            self.attr[Attr.MAX_HEALTH] = maxhealth
            self.attr[Attr.NOW_HEALTH] += num
        else:
            self.attr[Attr.MAX_HEALTH] = maxhealth
        if self.lastsweetie == -1:
            attack = (30 * self.sweetie)
            self.attr[Attr.ATTACK] = role_data['attack'] + attack
            self.attr[Attr.DEFENSIVE] = role_data['defensive'] + (30 * self.sweetie)
            self.attr[Attr.CRIT] = role_data['crit'] + (5 * self.sweetie)
            if self.attr[Attr.CRIT] > MAX_CRIT:
                self.attr[Attr.CRIT] = MAX_CRIT
            self.lastsweetie = self.sweetie
        else:
            num = self.sweetie - self.lastsweetie
            if num != 0:
                self.attrChange(Attr.ATTACK, (30*num))
                self.attrChange(Attr.DEFENSIVE, (30*num))
                self.attrChange(Attr.CRIT, (5*num))
                self.lastsweetie = self.sweetie




# 公主连结大乱斗
class PCRScrimmage:
    # 初始化
    def __init__(self, gid, manager, room_master, is_debug, across_range=10, vertical_range=10, grid_size=50) -> None:
        ##核心数据
        self.gid = gid  # 群号
        self.mgr = manager  # 管理器
        self.room_master = room_master  # 房主
        self.player_list = {}  # 玩家列表  ####这个东西不能迭代values，不懂原理
        self.now_statu = NOW_STATU_WAIT  # 当前游戏状态
        self.now_turn = 0  # 现在是玩家x的回合
        self.dice_num = 0  # 已丢色子次数的总数
        self.lock_turn = 0  # 回合锁定，x回合内都是同个玩家
        self.now_playing_players = []  # 当前正在游玩的玩家id	[xxx, xxx]
        self.rank = {}  # 结算排行	{1:xxx,2:xxx}
        self.player_satge_timer = 0  # 玩家阶段计时器。回合切换时重置
        self.is_debug = is_debug # 是否是测试服(已弃用)
        self.is_selected = [] # 是否已经被选

        self.user_card_dict = {}  # 群内所有成员信息

        # 初始化跑道，总共36个格子
        self.runway = [{"players": [], "case": 0} for i in range((across_range - 1) * 4)]
        for runway_case in self.runway:
            runway_case["case"] = random.choice(range(len(RUNWAY_CASE)))

        ##显示数据	注意：显示数据别乱改
        self.grid_size = grid_size  ##本来想做自定义跑道数量的，但显示适配太麻烦了，躺平
        self.vertical_range_x = vertical_range
        self.across_range_y = across_range
        width = (self.vertical_range_x + 2) * self.grid_size
        hight = (self.across_range_y + 2) * self.grid_size

        # 基础图片，初始化完成后不会再改变
        self.base_image = Image.new('RGB', (width, hight), COLOR_WRITE)
        self.draw = ImageDraw.Draw(self.base_image)

        # 当前状态图片，会随着游戏进度一直改变
        self.now_image = Image.new('RGB', (width, hight), COLOR_WRITE)
        self.now_draw = ImageDraw.Draw(self.now_image)

        FONTS_PATH = os.path.join(FILE_PATH, 'fonts')
        FONTS = os.path.join(FONTS_PATH, 'msyh.ttf')
        self.runwayTextFont = ImageFont.truetype(FONTS, 30)
        self.font = ImageFont.truetype(FONTS, 15)
        pass

    def __enter__(self):
        self.mgr.playing[self.gid] = self
        self.displayInit()
        self.ready(self.room_master)
        return self

    def __exit__(self, type_, value, trace):
        del self.mgr.playing[self.gid]

    # 加入房间准备
    def ready(self, user_id):
        if self.getPlayerNum() < MAX_PLAYER:
            self.player_list[user_id] = Role(user_id)
        pass

    # 检查是否全部玩家都选择了角色
    def checkAllPlayerSelectRole(self):
        num = 0
        for player_id in self.player_list:
            if self.getPlayerObj(player_id).role_id != 0:
                num += 1
        if num >= len(self.player_list):
            return True
        else:
            return False

    # 游戏正式开始需要做的处理
    def gameOpen(self):
        num = 0
        for player_id in self.player_list:
            offset_x, offset_y = 0, 0
            if num == 1:
                offset_x = 1
            elif num == 2:
                offset_y = 1
            elif num == 3:
                offset_x, offset_y = 1, 1

            self.now_playing_players.append(player_id)
            player = self.getPlayerObj(player_id)
            player.now_location = num * 9  # 玩家保存的位置
            self.runway[num * 9]["players"].append(player_id)  # 跑道保存的位置
            player.player_num = num  # 玩家编号
            head = player.role_icon  # 玩家头像

            after_head = head.resize((95, 97))

            # 放置玩家头像
            self.base_image.paste(after_head,
                                  (OFFSET_X + self.grid_size * 2 + offset_x * 200 + 3,
                                   OFFSET_Y + math.floor(self.grid_size * 1.5) + offset_y * 190 + 2))
            # 显示玩家名字
            self.playerInfoText(offset_x, offset_y, 12, text=f'name：{uid2card(player.user_id, self.user_card_dict)}')
            # 攻击距离
            self.playerInfoText(offset_x, offset_y, 28, text=f'dist   ：{player.attr[Attr.DISTANCE]}')

            num += 1

        # 房主的状态改为丢色子状态
        self.getPlayerObj(self.room_master).stageChange(NOW_STAGE_DICE)

        # 更新当前显示状态
        self.refreshNowImageStatu()

    # 玩家阶段计时器，超过一定时间不操作直接判负
    async def PlayerStageTimer(self, gid, bot, ev):
        self.player_satge_timer += 1
        if self.player_satge_timer > STAGE_WAIT_TIME:
            now_turn_player = self.getNowTurnPlayerObj()
            self.outDispose(now_turn_player)
            await bot.send(ev, message_builder.at(now_turn_player.user_id) + '已超时，出局')
            self.turnChange()  # 回合切换
            self.refreshNowImageStatu()  # 刷新当前显示状态
            image = IMAGE_PATH / f"{gid}.png"
            img = self.getNowImage()
            img.save(image)
            imgcode = message_builder.image(b64=pic2b64(Image.open(image)))
            await bot.send(ev, imgcode)
            await asyncio.sleep(PROCESS_WAIT_TIME)
            await self.stageRemind(bot, ev)

    # 回合改变，到下一个玩家
    def turnChange(self):
        readytoreborn = 0
        now_turn_player: Role = self.getNowTurnPlayerObj()
        if now_turn_player.now_stage != NOW_STAGE_OUT:  # 如果当前玩家已经出局，则不改变状态
            now_turn_player.stageChange(NOW_STAGE_WAIT)  # 已结束的玩家
        else:
            self.lock_turn = 0  # 如果玩家已出局，则取消回合锁定

        self.player_satge_timer = 0  # 重置玩家阶段计时器

        # 游戏胜利或结束则直接退出
        if (self.now_statu == NOW_STATU_WIN or
                self.now_statu == NOW_STATU_END):
            return readytoreborn

        skip_flag = False
        i = 0
        # 寻找下一回合的玩家
        while (i < len(self.player_list)):
            self.now_turn += 1
            if self.now_turn >= len(self.player_list):
                self.now_turn = 0
            next_turn_player = self.getNowTurnPlayerObj()  # 下一个玩家

            if next_turn_player.skip_turn > 0:  # 跳过被眩晕的玩家
                next_turn_player.skip_turn -= 1
                if next_turn_player.skip_turn == 0 and next_turn_player.now_stage == NOW_STAGE_FAKEOUT:
                    next_turn_player.stageChange(NOW_STAGE_WAIT)
                    next_turn_player.attr[Attr.MAX_HEALTH] += 350
                    next_turn_player.attr[Attr.DEFENSIVE] += 50
                    next_turn_player.attr[Attr.NOW_HEALTH] = next_turn_player.attr[Attr.MAX_HEALTH]
                    next_turn_player.attr[Attr.ATTACK] += 80
                    next_turn_player.attrChange(Attr.CRIT, 15)
                    key = getkey(self.rank, next_turn_player.user_id)
                    self.rank.pop(key)
                    temp = {}
                    for k in self.rank.keys():
                        if k < key:
                            temp[k+1] = self.rank[k]
                    self.rank.update(temp)
                    self.now_playing_players.append(next_turn_player.user_id)
                    readytoreborn = next_turn_player.user_id
                skip_flag = True
                continue
            if next_turn_player.now_stage != NOW_STAGE_OUT:  # 跳过已出局的玩家
                if self.lock_turn > 0:  # 检查是否锁定了当前回合
                    now_turn_player.stageChange(NOW_STAGE_DICE)
                    self.now_turn = now_turn_player.player_num
                    self.lock_turn -= 1
                    return readytoreborn
                next_turn_player.stageChange(NOW_STAGE_DICE)
                return readytoreborn
            if skip_flag:  # 如果检测到有跳过眩晕玩家，则重新循环
                i = 0
                skip_flag = False
            i += 1

        # 找不到直接结束游戏
        self.now_statu = NOW_STATU_END

    # 玩家出局处理
    def outDispose(self, player: Role, isfake=False, rebornturn=0):
        if isfake:
            player.stageChange(NOW_STAGE_FAKEOUT)
            player.skip_turn = rebornturn
        else:
            player.stageChange(NOW_STAGE_OUT)
        self.rank[len(self.now_playing_players)] = player.user_id
        if player.user_id in self.now_playing_players:
            self.now_playing_players.remove(player.user_id)
        if len(self.now_playing_players) == 1:
            self.rank[1] = self.now_playing_players[0]
            self.now_statu = NOW_STATU_WIN

    # 丢色子
    async def throwDice(self, player_id, step, bot, ev):
        player = self.getPlayerObj(player_id)

        player.locationChange(step, self.runway)

        for iter_player_id in self.now_playing_players:  # 每丢1次色子为一个回合
            iter_player = self.getPlayerObj(iter_player_id)
            iter_player.deleteInvalidBuff()
            iter_player.attrChange(Attr.NOW_TP, ONE_ROUND_TP)
            iter_player.buffTriggerByTriggerType(BuffTriggerType.Normal)
            iter_player.buffTriggerByTriggerType(BuffTriggerType.Turn)
            if iter_player_id == player_id:
                if player.catpoison > 0:
                    player.catpoison -= 1
                player.buffTriggerByTriggerType(BuffTriggerType.NormalSelf)
                player.buffTriggerByTriggerType(BuffTriggerType.TurnSelf)

        self.dice_num += 1
        # 每丢(场上玩家数量)次色子，所有玩家增加攻击距离和攻击力
        if self.dice_num % (len(self.now_playing_players) + 1) == 0:
            for iter_player_id in self.now_playing_players:
                self.getPlayerObj(iter_player_id).attrChange(Attr.DISTANCE, ROUND_DISTANCE)
                self.getPlayerObj(iter_player_id).attrChange(Attr.ATTACK, ROUND_ATTACK)
            self.dice_num = 1

        if player.now_stage == NOW_STAGE_FAKEOUT:
            await bot.send(ev, message_builder.at(player.user_id) + f'暂时出局并将在{player.reborn_turn}回合后复活！')
            self.turnChange()  # 回合切换
            self.refreshNowImageStatu()  # 刷新当前显示状态

        if player.now_stage == NOW_STAGE_OUT:
            await bot.send(ev, message_builder.at(player.user_id) + '出局')
            self.turnChange()  # 回合切换
            self.refreshNowImageStatu()  # 刷新当前显示状态
            return

        await self.caseTrigger(player, bot, ev)

    # 技能触发跑道事件
    def skillcaseTrigger(self, player: Role, back_msg):
        case_num = self.runway[player.now_location]["case"]
        str1, num = "", 0
        if case_num == CASE_NONE:
            pass
        elif case_num == CASE_HEALTH:
            numRange = RUNWAY_CASE[CASE_HEALTH]["range"]
            num = random.choice(range(numRange[0], numRange[1]))
            player.attrChange(Attr.NOW_HEALTH, num)
        elif case_num == CASE_DEFENSIVE:
            numRange = RUNWAY_CASE[CASE_DEFENSIVE]["range"]
            num = random.choice(range(numRange[0], numRange[1]))
            player.attrChange(Attr.DEFENSIVE, num)
        elif case_num == CASE_ATTACK:
            numRange = RUNWAY_CASE[CASE_ATTACK]["range"]
            num = random.choice(range(numRange[0], numRange[1]))
            player.attrChange(Attr.ATTACK, num)
        elif case_num == CASE_TP:
            numRange = RUNWAY_CASE[CASE_TP]["range"]
            num = random.choice(range(numRange[0], numRange[1]))
            player.attrChange(Attr.NOW_TP, num)
        elif case_num == CASE_MOVE:
            numRange = RUNWAY_CASE[CASE_MOVE]["range"]
            num = random.choice(range(numRange[0], numRange[1]))
            if num == 0: num += 1
            player.locationChange(num, self.runway)

        if num > 0:
            if case_num == CASE_MOVE:
                str1 = "前"
            else:
                str1 = "增加"
        else:
            if case_num == CASE_MOVE:
                str1 = "后"
            else:
                str1 = "减少"
        text = "触发事件，"
        text += RUNWAY_CASE[case_num]["text"].format(str1, abs(num))
        if case_num != CASE_NONE and num == 0:
            text += "，所以什么都不会发生"
        elif case_num == CASE_NONE:
            text = "什么也没发生"
        back_msg.append(text)
        return back_msg

    # 触发跑道事件
    async def caseTrigger(self, player: Role, bot, ev: GroupMessageEvent):
        case_num = self.runway[player.now_location]["case"]
        str1, num = "", 0
        if case_num == CASE_NONE:
            pass
        elif case_num == CASE_HEALTH:
            numRange = RUNWAY_CASE[CASE_HEALTH]["range"]
            num = random.choice(range(numRange[0], numRange[1]))
            player.attrChange(Attr.NOW_HEALTH, num)
        elif case_num == CASE_DEFENSIVE:
            numRange = RUNWAY_CASE[CASE_DEFENSIVE]["range"]
            num = random.choice(range(numRange[0], numRange[1]))
            player.attrChange(Attr.DEFENSIVE, num)
        elif case_num == CASE_ATTACK:
            numRange = RUNWAY_CASE[CASE_ATTACK]["range"]
            num = random.choice(range(numRange[0], numRange[1]))
            player.attrChange(Attr.ATTACK, num)
        elif case_num == CASE_TP:
            numRange = RUNWAY_CASE[CASE_TP]["range"]
            num = random.choice(range(numRange[0], numRange[1]))
            player.attrChange(Attr.NOW_TP, num)
        elif case_num == CASE_MOVE:
            numRange = RUNWAY_CASE[CASE_MOVE]["range"]
            num = random.choice(range(numRange[0], numRange[1]))
            if num == 0: num += 1
            player.locationChange(num, self.runway)

        if num > 0:
            if case_num == CASE_MOVE:
                str1 = "前"
            else:
                str1 = "增加"
        else:
            if case_num == CASE_MOVE:
                str1 = "后"
            else:
                str1 = "减少"
        text = "触发事件，"
        text += RUNWAY_CASE[case_num]["text"].format(str1, abs(num))
        if case_num != CASE_NONE and num == 0:
            text += "，所以什么都不会发生"
        elif case_num == CASE_NONE:
            text = "什么也没发生"
        await bot.send(ev, text)

        if case_num == CASE_MOVE and num != 0:
            self.refreshNowImageStatu()
            image = IMAGE_PATH / f'{ev.group_id}.png'
            img = self.getNowImage()
            img.save(image)
            imgcode = message_builder.image(b64=pic2b64(Image.open(image)))
            await bot.send(ev, imgcode)
            await asyncio.sleep(1)
            await self.caseTrigger(player, bot, ev)
        if player.now_stage == NOW_STAGE_FAKEOUT:
            await bot.send(ev, message_builder.at(player.user_id) + f'暂时出局并将在{player.reborn_turn}回合后复活！')
            self.turnChange()  # 回合切换
            self.refreshNowImageStatu()  # 刷新当前显示状态
        if player.now_stage == NOW_STAGE_OUT:
            await bot.send(ev, message_builder.at(player.user_id) + '出局')
            self.turnChange()  # 回合切换
            self.refreshNowImageStatu()  # 刷新当前显示状态
        else:
            player.stageChange(NOW_STAGE_SKILL)

    # 使用技能
    async def useSkill(self, skill_id, use_player_id, goal_player_id, bot, ev):
        if skill_id != 0:
            use_player_obj = self.getPlayerObj(use_player_id)
            if skill_id > len(use_player_obj.active_skills) or skill_id <= 0:
                await bot.send(ev, '技能编号不正确')
                return RET_ERROR

            real_skill_id = skill_id - 1  # 实际技能id
            skill = use_player_obj.active_skills[real_skill_id]
            skill_tp_cost = skill["tp_cost"]  # tp消耗
            if skill_tp_cost > use_player_obj.attr[Attr.NOW_TP if use_player_obj.passive!=PASSIVE_HEALTHTP else Attr.NOW_HEALTH]:  # 检查tp是否足够
                await bot.send(ev, 'tp不足，无法使用这个技能' if use_player_obj.passive!=PASSIVE_HEALTHTP else '生命值不足，无法使用这个技能')
                return RET_ERROR

            # 先扣除tp
            use_player_obj.attrChange(Attr.NOW_TP if use_player_obj.passive!=PASSIVE_HEALTHTP else Attr.NOW_HEALTH, -skill_tp_cost)

            use_player_name = uid2card(use_player_obj.user_id, self.user_card_dict)
            use_skill_nale = use_player_obj.active_skills[real_skill_id]["name"]
            await bot.send(ev, f'{use_player_name}尝试使用{use_skill_nale}')

            back_msg = []
            ret, msg = self.skillTrigger(use_player_obj, goal_player_id, real_skill_id, False, back_msg)
            if ret == RET_ERROR:
                await bot.send(ev, Message(msg))
                # 技能释放失败，返还tp
                use_player_obj.attrChange(Attr.NOW_TP if use_player_obj.passive!=PASSIVE_HEALTHTP else Attr.NOW_HEALTH, skill_tp_cost)
                return ret
            await bot.send(ev, Message('\n'.join(back_msg)))

        return RET_SCUESS

    # 技能释放对象选择
    def skillTrigger(self, use_skill_player: Role, goal_player_id, skill_id, is_passive, back_msg):

        if is_passive:
            skill = use_skill_player.passive_skills[skill_id]  # 被动技能详细数据
        else:
            skill = use_skill_player.active_skills[skill_id]  # 主动技能详细数据
        skill_trigger = skill["trigger"]  # 技能的触发对象
        skill_effect = skill["effect"]  # 技能效果

        # 这个技能有两套技能组
        if EFFECT_SKILL_CHANGE in skill_effect:
            buff_type = skill_effect[EFFECT_SKILL_CHANGE][0]
            new_skill_goal = skill_effect[EFFECT_SKILL_CHANGE][1]
            if buff_type in use_skill_player.buff:
                for skill_id in new_skill_goal:
                    ret, msg = self.skillTrigger(use_skill_player, goal_player_id, skill_id, True, back_msg)
                    if ret == RET_ERROR: return ret, msg
                return RET_SCUESS, ''

        # 选择触发对象
        if skill_trigger == TRIGGER_SELECT or skill_trigger == TRIGGER_SELECT_EXCEPT_ME:
            if goal_player_id > 0:
                goal_player_obj = self.getPlayerObj(goal_player_id)
                if not goal_player_obj:
                    return RET_ERROR, '目标不在房间里'
                if goal_player_obj.now_stage in (NOW_STAGE_OUT, NOW_STAGE_FAKEOUT):
                    return RET_ERROR, '目标已出局'
                if skill_trigger == TRIGGER_SELECT_EXCEPT_ME and goal_player_obj == use_skill_player:
                    return RET_ERROR, '不能选择自己'

                # 检查被动技能里是否带有无视距离的技能效果
                disregard_dist = False
                if "passive" in skill and len(skill["passive"]) != 0:
                    for passive_skill_id in skill["passive"]:
                        passive_skill_effect = use_skill_player.passive_skills[passive_skill_id]["effect"]
                        if (EFFECT_MOVE_GOAL in passive_skill_effect or
                                EFFECT_IGNORE_DIST in passive_skill_effect):
                            disregard_dist = True
                            break

                # 计算攻击距离
                dist = self.getTwoPlayerDist(use_skill_player, goal_player_obj)
                if (dist > use_skill_player.attr[Attr.DISTANCE] and not disregard_dist and not is_passive):
                    return RET_ERROR, '攻击距离不够'

                # 先触发被动技能
                if "passive" in skill and len(skill["passive"]) != 0:
                    for passive_skill_id in skill["passive"]:
                        ret, msg = self.skillTrigger(use_skill_player, goal_player_id, passive_skill_id, True, back_msg)
                        if ret == RET_ERROR: return ret, msg
                # 后触发主动技能
                return self.skillEffect(use_skill_player, goal_player_obj, skill_effect, back_msg)
            else:
                return RET_ERROR, '该技能需要选择一个目标'

        # 先触发被动技能
        if "passive" in skill and len(skill["passive"]) != 0:
            for passive_skill_id in skill["passive"]:
                ret, msg = self.skillTrigger(use_skill_player, goal_player_id, passive_skill_id, True, back_msg)
                if ret == RET_ERROR: return ret, msg

        if skill_trigger == TRIGGER_ME:  # 自己
            ret, msg = self.skillEffect(use_skill_player, use_skill_player, skill_effect, back_msg)
            if ret == RET_ERROR: return ret, msg
        elif skill_trigger == TRIGGER_ALL:  # 所有人
            for player_id in self.player_list:
                goal_player = self.getPlayerObj(player_id)
                ret, msg = self.skillEffect(use_skill_player, goal_player, skill_effect, back_msg)
                if ret == RET_ERROR: return ret, msg
        elif skill_trigger == TRIGGER_ALL_EXCEPT_ME:  # 除了自己的其它人
            for player_id in self.player_list:
                if player_id == use_skill_player.user_id: continue
                goal_player = self.getPlayerObj(player_id)
                ret, msg = self.skillEffect(use_skill_player, goal_player, skill_effect, back_msg)
                if ret == RET_ERROR: return ret, msg
        elif skill_trigger == TRIGGER_NEAR:  # 离自己最近的目标
            goal_player = self.getNearPlayer(use_skill_player)
            ret, msg = self.skillEffect(use_skill_player, goal_player, skill_effect, back_msg)
            if ret == RET_ERROR: return ret, msg
        else:
            return RET_ERROR, '技能配置出错'

        return RET_SCUESS, msg

    # 技能效果生效
    def skillEffect(self, use_skill_player: Role, goal_player: Role, skill_effect_base, back_msg: List):
        if goal_player.now_stage in (NOW_STAGE_OUT, NOW_STAGE_FAKEOUT): return RET_NORMAL, ''

        skill_effect: Dict = skill_effect_base.copy()  # 拷贝一份，避免修改保存在角色信息的技能效果
        use_player_name = uid2card(use_skill_player.user_id, self.user_card_dict)
        goal_player_name = uid2card(goal_player.user_id, self.user_card_dict)

        if EFFECT_TP_REQUEST in skill_effect:
            if use_skill_player.attr[Attr.NOW_TP] < skill_effect[EFFECT_TP_REQUEST]:
                return RET_ERROR, '未满足技能释放要求'

        # aoe效果
        if EFFECT_AOE in skill_effect:
            aoe_dist = skill_effect[EFFECT_AOE][0]  # aoe范围
            to_self = skill_effect[EFFECT_AOE][1]  # 是否对自己生效
            del skill_effect[EFFECT_AOE]  # 删掉aoe效果，避免无限递归
            for i in range(goal_player.now_location - aoe_dist, goal_player.now_location + aoe_dist):
                location = i  # 处理后的位置，避免下标不在跑道上的数组里
                if location >= len(self.runway):
                    location -= len(self.runway)
                elif location < 0:
                    location = len(self.runway) + location
                if len(self.runway[location]["players"]) > 0:
                    for runway_player_id in self.runway[location]["players"]:
                        if runway_player_id == use_skill_player.user_id and not to_self: continue
                        runway_player_obj = self.getPlayerObj(runway_player_id)
                        self.skillEffect(use_skill_player, runway_player_obj, skill_effect, back_msg)
            skill_effect.clear()  # 递归完成清空所有效果，不需要再次触发

        # 向目标移动
        if EFFECT_MOVE_GOAL in skill_effect:
            num = skill_effect[EFFECT_MOVE_GOAL][0]
            ignore_dist = skill_effect[EFFECT_MOVE_GOAL][1]

            # 向目标移动的效果，在触发时才计算攻击距离
            distance = use_skill_player.now_location - goal_player.now_location
            half_circle = len(self.runway) / 2
            dist = self.getTwoPlayerDist(use_skill_player, goal_player)
            if not ignore_dist and dist > use_skill_player.attr[Attr.DISTANCE] + num: return RET_ERROR, '攻击距离不够'

            if distance > 0:
                if distance > half_circle:
                    use_skill_player.locationChange(num, self.runway)
                else:
                    use_skill_player.locationChange(-num, self.runway)
            else:
                if abs(distance) < half_circle:
                    use_skill_player.locationChange(num, self.runway)
                else:
                    use_skill_player.locationChange(-num, self.runway)
            back_msg.append(f'{use_player_name}往离{goal_player_name}较近的方向移动了{num}步')

        # 选择目标的移动效果
        if EFFECT_JUMP in skill_effect:
            use_skill_player.locationChange(goal_player.now_location + random.choice([-1, 1]), self.runway, True)
            back_msg.append(f'{use_player_name}移动到了{goal_player_name}的身边')

        # 击退/拉近
        if EFFECT_HIT_BACK in skill_effect:
            num = skill_effect[EFFECT_HIT_BACK]
            distance = use_skill_player.now_location - goal_player.now_location
            half_circle = len(self.runway) / 2
            if distance > 0:
                if distance > half_circle:
                    goal_player.locationChange(num, self.runway)
                else:
                    goal_player.locationChange(-num, self.runway)
            else:
                if abs(distance) < half_circle:
                    goal_player.locationChange(num, self.runway)
                else:
                    goal_player.locationChange(-num, self.runway)
            if num > 0:
                back_msg.append(f'{use_player_name}将{goal_player_name}击退了{num}步')
            else:
                back_msg.append(f'{use_player_name}将{goal_player_name}拉近了{abs(num)}步')

        # 位置改变
        if EFFECT_MOVE in skill_effect:
            num = skill_effect[EFFECT_MOVE]
            goal_player.locationChange(num, self.runway)

            if num < 0:
                back_msg.append(f'{goal_player_name}后退了{abs(num)}步')
                back_msg = self.skillcaseTrigger(goal_player, back_msg)
            else:
                back_msg.append(f'{goal_player_name}前进了{num}步')
                back_msg = self.skillcaseTrigger(goal_player, back_msg)

        # 获得嘉心糖效果
        if EFFECT_GET_SWEETIE in skill_effect:
            num = skill_effect[EFFECT_GET_SWEETIE]
            use_skill_player.sweetie += num
            use_skill_player.sweetiecalculate(True)
            back_msg.append(f'{use_player_name}获得了{num}个嘉心糖')


        # buff效果
        if EFFECT_BUFF in skill_effect:
            for buff_info in skill_effect[EFFECT_BUFF]:
                buff_name = Buff[buff_info[0]]['name']
                buff_text: str = Buff[buff_info[0]]['text']
                buff_text = buff_text.format(abs(buff_info[1]), buff_info[2] > 1000 and "无限" or buff_info[2])
                goal_player.addBuff(buff_info)
                back_msg.append(f'{goal_player_name}获得buff《{buff_name}》，{buff_text}')

        # 清除buff效果
        if EFFECT_DEL_BUFF in skill_effect:
            for bufftype in skill_effect[EFFECT_DEL_BUFF]:
                goal_player.deleteBuff(bufftype)
                back_msg.append(f'{goal_player_name}切换回初始形态了')


        # 立即触发特定buff
        if EFFECT_BUFF_BY_BT in skill_effect:
            for buffType in skill_effect[EFFECT_BUFF_BY_BT]:
                self.getPlayerObj(goal_player.user_id).buffTriggerByBuffType(buffType)

        # 属性改变
        if EFFECT_ATTR_CHANGE in skill_effect:
            for effect in skill_effect[EFFECT_ATTR_CHANGE]:
                attr_type = effect[0]  # 属性类型
                num = effect[1]  # 基础数值
                addition_type = effect[2]  # 加成类型
                addition_prop = effect[3]  # 加成比例
                text = AttrTextChange(attr_type)

                if addition_type != 0 and addition_prop != 0:
                    add = goal_player.attr[addition_type] * addition_prop
                    num = math.floor(num + (num < 0 and -add or add))  # 计算加成后的数值
                goal_player.attrChange(attr_type, num)

                if num < 0:
                    back_msg.append(f'{goal_player_name}降低了{abs(num)}点{text}')
                    if goal_player.now_stage == NOW_STAGE_OUT:
                        back_msg.append(f'{message_builder.at(goal_player.user_id)}出局')
                    if goal_player.now_stage == NOW_STAGE_FAKEOUT:
                        back_msg.append(f'{message_builder.at(goal_player.user_id)}暂时出局并将在{goal_player.reborn_turn}回合后复活！')
                else:
                    back_msg.append(f'{goal_player_name}增加了{num}点{text}')

        # 造成伤害
        if EFFECT_HURT in skill_effect:
            num, crit_flag = self.hurtCalculate(skill_effect, use_skill_player, goal_player, back_msg)
            num = goal_player.beHurt(num)
            if goal_player.costtp == 1:
                back_msg.append(f'{crit_flag and "暴击！" or ""}{goal_player_name}的tp值降低了{abs(num)}点')
            else:
                back_msg.append(f'{crit_flag and "暴击！" or ""}{goal_player_name}受到了{abs(num)}点伤害')

            if num < 0 < goal_player.catpoison:
                diana_player = self.getDianaObj()
                diana_player.sweetie += 1
                diana_player.sweetiecalculate(True)
                goal_player.attrChange(Attr.NOW_TP, -10)
                diana_player.attrChange(Attr.NOW_TP, 10)
                diana_player_name = uid2card(diana_player.user_id, self.user_card_dict)
                back_msg.append(f'由于{goal_player_name}正处于猫中毒状态，{diana_player_name}获得了1个嘉心糖并从该玩家处抢夺了10点tp')

            if goal_player.now_stage == NOW_STAGE_OUT:
                use_skill_player.attrChange(Attr.NOW_TP, HIT_DOWN_TP)  # 击倒回复tp
                back_msg.append(f'{message_builder.at(goal_player.user_id)}出局')
            if goal_player.now_stage == NOW_STAGE_FAKEOUT:
                use_skill_player.attrChange(Attr.NOW_TP, HIT_DOWN_TP)  # 击倒回复tp
                goal_player.revenge = use_skill_player.user_id
                back_msg.append(f'{message_builder.at(goal_player.user_id)}暂时出局并将在{goal_player.reborn_turn}回合后复活！')

        # 猫中毒效果
        if EFFECT_CAT_POISION in skill_effect:
            num = skill_effect[EFFECT_CAT_POISION]
            goal_player.catpoison = num
            back_msg.append(f'{goal_player_name}进入了猫中毒状态，持续{num}个自我回合')

        # 消耗嘉心糖锁定回合效果
        if EFFECT_SWEET_LOCKTURN in skill_effect:
            num = use_skill_player.sweetie
            use_skill_player.sweetie = 0
            use_skill_player.sweetiecalculate(True)
            back_msg.append(f'{use_player_name}消耗了{num}个嘉心糖')
            lockrequirement = skill_effect[EFFECT_SWEET_LOCKTURN]
            if num >= lockrequirement:
                self.lock_turn = 1
                back_msg.append(f'由于消耗数量达到了{lockrequirement}个或更多，{use_player_name}锁定了一回合')


        # tp达到指定值时锁定回合
        if EFFECT_TP_LOCKTURN in skill_effect:
            num1 = skill_effect[EFFECT_TP_LOCKTURN]
            if use_skill_player.attr[Attr.NOW_TP] >= num1:
                self.lock_turn = 1
                back_msg.append(f'{use_player_name}锁定了1回合')

        if EFFECT_COST_TP in skill_effect:
            use_skill_player.costtp = 1
            back_msg.append(f'{use_player_name}接下来受到攻击时改为降低tp值！')

        if EFFECT_RANDOM in skill_effect:
            if use_skill_player.costtp != 1:
                choice = [random.choice(range(1,7))]
            else:
                choice = [random.choice(range(1,7)),random.choice(range(1,7))]
            for choose in choice:
                if choose == 1:
                    use_skill_player.attrChange(Attr.NOW_HEALTH, 500)
                    back_msg.append(f'{use_player_name}增加了500点生命值')
                if choose == 2:
                    use_skill_player.attrChange(Attr.CRIT, 15)
                    back_msg.append(f'{use_player_name}增加了15%暴击率')
                if choose == 3:
                    use_skill_player.attrChange(Attr.NOW_TP, 10)
                    back_msg.append(f'{use_player_name}增加了10点tp')
                if choose == 4:
                    use_skill_player.attrChange(Attr.DEFENSIVE, 50)
                    back_msg.append(f'{use_player_name}增加了50点防御力')
                if choose == 5:
                    use_skill_player.attrChange(Attr.NOW_HEALTH, -150)
                    back_msg.append(f'{use_player_name}减少了150点生命值')
                if choose == 6:
                    use_skill_player.attrChange(Attr.DEFENSIVE, -50)
                    back_msg.append(f'{use_player_name}减少了50点防御力')

        # 效果击倒tp
        if EFFECT_OUT_TP in skill_effect:
            if goal_player.now_stage in (NOW_STAGE_OUT, NOW_STAGE_FAKEOUT):
                num = skill_effect[EFFECT_OUT_TP]
                use_skill_player.attrChange(Attr.NOW_TP, num)
                extra_msg = '暂时' if goal_player.now_stage == NOW_STAGE_FAKEOUT else ''
                if num < 0:
                    back_msg.append(f'{goal_player_name}{extra_msg}被击倒，{use_player_name}降低了{abs(num)}点TP')
                else:
                    back_msg.append(f'{goal_player_name}{extra_msg}被击倒，{use_player_name}增加了{num}点TP')

        # 复仇成功缩短复活时间
        if EFFECT_KILL_REBORN in skill_effect:
            if goal_player.user_id == use_skill_player.revenge and goal_player.now_stage in (NOW_STAGE_OUT, NOW_STAGE_FAKEOUT):
                num = skill_effect[EFFECT_KILL_REBORN]
                if use_skill_player.reborn_turn > 1:
                    use_skill_player.reborn_turn -= num
                    back_msg.append(f'{use_player_name}完成了复仇，复活所需的回合数缩短了{num}！')
                else:
                    back_msg.append(f'{use_player_name}完成了复仇，但复活所需的回合数已经不能再缩短了！')

        # 回合锁定效果
        if EFFECT_LOCKTURN in skill_effect:
            num = skill_effect[EFFECT_LOCKTURN]
            self.lock_turn = num
            back_msg.append(f'{use_player_name}锁定了{num}回合')

        # 击退回合锁定效果
        if EFFECT_OUT_LOCKTURN in skill_effect:
            if goal_player.now_stage in (NOW_STAGE_OUT, NOW_STAGE_FAKEOUT):
                num = skill_effect[EFFECT_OUT_LOCKTURN]
                self.lock_turn = num
                back_msg.append(f'{use_player_name}锁定了{num}回合')

        # 缩短复活回合数效果
        if EFFECT_REBORN in skill_effect:
            num = skill_effect[EFFECT_REBORN]
            if goal_player.reborn_turn <= num:
                return RET_ERROR, '使用此技能不会有任何效果！请选择其他技能'
            goal_player.reborn_turn = num
            back_msg.append(f'{use_player_name}的复活所需回合数缩短为了{num}！')

        # 眩晕效果
        if EFFECT_DIZZINESS in skill_effect:
            num = skill_effect[EFFECT_DIZZINESS]
            goal_player.dizziness(num)
            back_msg.append(f'{goal_player_name}被眩晕{num}回合')

        if len(back_msg) == 0:
            back_msg.append('什么都没发生')
        return RET_SCUESS, ''

    # 伤害计算独立出来处理
    def hurtCalculate(self, skill_effect, use_skill_player: Role, goal_player: Role, back_msg: List):
        num = abs(skill_effect[EFFECT_HURT][0])  # 基础数值
        addition_type = skill_effect[EFFECT_HURT][1]  # 加成类型
        addition_goal = (skill_effect[EFFECT_HURT][2] == 0  # （三目）
                         and use_skill_player or goal_player)  # 加成的数值对象：0自己 1目标
        addition_prop = skill_effect[EFFECT_HURT][3]  # 加成比例
        is_real = skill_effect[EFFECT_HURT][4]  # 是否是真实伤害

        use_skill_player.buffTriggerByTriggerType(BuffTriggerType.Attack)
        crit_flag = random.choice(range(0, MAX_CRIT)) < use_skill_player.attr[Attr.CRIT]

        # 复仇
        if EFFECT_REVENGE in skill_effect:
            if use_skill_player.revenge != 0 and use_skill_player.revenge == goal_player.user_id:
                crit_flag = True

        if addition_type != 0 and addition_prop != 0:  # 计算加成后的数值
            num = num + addition_goal.attr[addition_type] * addition_prop
        if use_skill_player.attr[Attr.CRIT] != 0 and crit_flag:  # 计算暴击
            num *= use_skill_player.attr[Attr.CRIT_HURT]
        if not is_real:  # 如果是真实伤害则不计算目标的防御
            goal_player_def = goal_player.attr[Attr.DEFENSIVE]  # 目标防御力
            num = hurt_defensive_calculate(num, goal_player_def)  # 计算目标防御力后的数值

        # 嘉心糖增伤效果
        if EFFECT_SWEETBUFF in skill_effect:
            sweet_prop = skill_effect[EFFECT_SWEETBUFF]
            num = num * (sweet_prop ** use_skill_player.sweetie) # 每有一个嘉心糖增伤

        # 斩杀效果
        if EFFECT_ELIMINATE in skill_effect:
            # cons_prop：目标已消耗的生命值比例; real_prop：真正的伤害比例
            cons_prop = 1 - goal_player.attr[Attr.NOW_HEALTH] / goal_player.attr[Attr.MAX_HEALTH]
            real_prop = cons_prop / skill_effect[EFFECT_ELIMINATE][0]
            num += real_prop * 100 * skill_effect[EFFECT_ELIMINATE][1]
        # 背水效果
        if EFFECT_STAND in skill_effect:
            cons_prop = 1 - use_skill_player.attr[Attr.NOW_HEALTH] / use_skill_player.attr[Attr.MAX_HEALTH]
            real_prop = cons_prop / skill_effect[EFFECT_STAND][0]
            num += real_prop * 100 * skill_effect[EFFECT_STAND][1]
        # 生命偷取
        if EFFECT_LIFESTEAL in skill_effect:
            steal_prop = skill_effect[EFFECT_LIFESTEAL]
            add = math.floor(num * steal_prop)
            use_skill_player.attrChange(Attr.NOW_HEALTH, add)
            back_msg.append(f'{uid2card(use_skill_player.user_id, self.user_card_dict)}增加了{add}点生命值')


        # 判断一下是否有致盲buff
        num = use_skill_player.buffTriggerByBuffType(BuffType.Blind, num)

        num = math.floor(num)  # 小数数值向下取整
        num = 0 - num  # 变回负数，代表扣血
        return num, crit_flag

    # 阶段提醒，丢色子/放技能阶段
    async def stageRemind(self, bot, ev: GroupMessageEvent):
        player = self.getNowTurnPlayerObj()
        stage = player.now_stage
        msg = [f'回合剩余{WAIT_TIME * (STAGE_WAIT_TIME - self.player_satge_timer)}秒']
        if stage == NOW_STAGE_DICE:
            msg.append(f'{message_builder.at(player.user_id)}的丢色子阶段(发送 丢 或 丢色子)')
            await bot.send(ev, Message("\n".join(msg)))
        elif stage == NOW_STAGE_SKILL:
            msg.append(f'{message_builder.at(player.user_id)}的放技能阶段：\n(发送技能编号，如需选择目标则@目标)')
            skill_list = player.active_skills
            skill_num = 0
            if player.passive == PASSIVE_HEALTHTP:
                for skill in skill_list:
                    tp_cost = skill["tp_cost"]
                    msg.append(f'  技能{skill_num + 1}:{skill["name"]}({tp_cost}生命值):\n   {skill["text"]}\n')
                    skill_num += 1
            else:
                for skill in skill_list:
                    tp_cost = skill["tp_cost"]
                    msg.append(f'  技能{skill_num + 1}:{skill["name"]}({tp_cost}TP):\n   {skill["text"]}\n')
                    skill_num += 1
            msg.append('(发送"跳过"跳过出技能阶段)')
            await bot.send(ev, Message("\n".join(msg)))

    # 获取基础图片
    def getBaseImage(self):
        return self.base_image

    # 获取当前状态图片
    def getNowImage(self):
        return self.now_image

    # 获取当前玩家数量
    def getPlayerNum(self):
        return len(self.player_list)

    # 获取玩家对象
    def getPlayerObj(self, player_id):
        player: Role = self.player_list[player_id]
        return player

    # 找到嘉然玩家
    def getDianaObj(self):
        for player_id in self.player_list:
            player = self.getPlayerObj(player_id)
            if player.passive == PASSIVE_SWEETIE:
                return player
            else:
                return None

    # 获取当前回合的玩家对象
    def getNowTurnPlayerObj(self):
        for player_id in self.player_list:
            player = self.getPlayerObj(player_id)
            if player.player_num == self.now_turn:
                return player

    # 获取两个玩家之间的距离
    def getTwoPlayerDist(self, p1: Role, p2: Role):
        dist = abs(p1.now_location - p2.now_location)
        half_circle = len(self.runway) / 2
        if abs(dist) > half_circle: dist = half_circle - abs(half_circle - dist)
        return dist

    # 获取离玩家最近的一个目标玩家id
    def getNearPlayer(self, own_player: Role):
        dist_list = []  # 距离列表 [[玩家id,距离],[]]
        for player_id in self.player_list:
            player = self.getPlayerObj(player_id)
            if player == own_player: continue
            if player.now_stage in (NOW_STAGE_OUT, NOW_STAGE_FAKEOUT): continue
            dist_list.append([player.user_id, self.getTwoPlayerDist(own_player, player)])
        # 极其低效的排序算法，时间复杂度为O(n^2)，数据量小，懒得改了_(:3)∠)_
        for i in range(len(dist_list)):  # 类似插入排序，从小到大
            save_info = dist_list[i]
            save_location = -1
            del dist_list[i]
            for j in range(len(dist_list)):
                comp_info = dist_list[j]
                if save_info[1] > comp_info[1]:
                    save_location = j
            dist_list.insert(save_location + 1, save_info)
        return self.getPlayerObj(dist_list[0][0])

    # 刷新当前状态图片
    def refreshNowImageStatu(self):
        self.now_image = self.base_image.copy()
        self.now_draw = ImageDraw.Draw(self.now_image)

        # 遍历玩家列表，刷新玩家当前状态
        num = 0
        for player_id in self.player_list:
            offset_x, offset_y = 0, 0
            if num == 1:
                offset_x = 1
            elif num == 2:
                offset_y = 1
            elif num == 3:
                offset_x, offset_y = 1, 1

            player = self.getPlayerObj(player_id)
            health_line_length = 96 * (player.attr[Attr.NOW_HEALTH] / player.attr[Attr.MAX_HEALTH])
            tp_line_length = 96 * (player.attr[Attr.NOW_TP] / player.attr[Attr.MAX_TP])

            self.statuLineFill(health_line_length, offset_x, offset_y, -16, COLOR_CAM_GREEN)  # 血条填充
            self.statuLineFill(tp_line_length, offset_x, offset_y, 1, COLOR_CAM_BLUE)  # tp条填充
            self.roleStatuText(offset_x, offset_y, -23, text=str(player.attr[Attr.NOW_HEALTH]))  # 血条数值
            self.roleStatuText(offset_x, offset_y, -5, text=str(player.attr[Attr.NOW_TP]))  # tp条数值
            self.playerInfoText(offset_x, offset_y, 28, text=f'dist   ：{player.attr[Attr.DISTANCE]}')  # 攻击距离
            self.playerInfoText(offset_x, offset_y, 12,
                                text=f'name：{uid2card(player.user_id, self.user_card_dict)}')  # 玩家名字

            if self.now_turn == player.player_num:  # 当前回合的玩家，头像框为绿色
                self.drawBox(100, 100, self.grid_size * 2 + offset_x * 200, self.grid_size * 1.5 + offset_y * 190,
                             COLOR_GREEN, is_now=True)
            if player.now_stage == NOW_STAGE_OUT:  # 已出局的玩家，头像框为黑色，且跑道旁不显示头像
                self.drawBox(100, 100, self.grid_size * 2 + offset_x * 200, self.grid_size * 1.5 + offset_y * 190,
                             COLOR_BLACK, is_now=True)
            else:
                self.roleIconLocation(player.role_icon, player.now_location)  # 显示玩家角色位置
            num += 1

    # 显示初始化
    def displayInit(self):
        j = 0
        for i in range(self.across_range_y + 1):  # 画横线
            self.draw.line((0 + OFFSET_X, j + OFFSET_Y) +
                           (self.grid_size * self.vertical_range_x + OFFSET_X, j + OFFSET_Y),
                           fill=COLOR_BLACK, width=RUNWAY_LINE_WDITH)
            j += self.grid_size
        j = 0
        for i in range(self.vertical_range_x + 1):  # 画竖线
            self.draw.line((j + OFFSET_X, 0 + OFFSET_Y) +
                           (j + OFFSET_X, self.grid_size * self.across_range_y + OFFSET_Y),
                           fill=COLOR_BLACK, width=RUNWAY_LINE_WDITH)
            j += self.grid_size
        # 中间遮掩
        self.draw.rectangle(
            (RUNWAY_LINE_WDITH + self.grid_size + OFFSET_X - 1, RUNWAY_LINE_WDITH + self.grid_size + OFFSET_Y - 1,
             self.grid_size - (RUNWAY_LINE_WDITH / 2) + (self.vertical_range_x - 2) * self.grid_size + OFFSET_X,
             self.grid_size - (RUNWAY_LINE_WDITH / 2) + (self.across_range_y - 2) * self.grid_size + OFFSET_Y),
            fill=COLOR_WRITE)
        # 画框
        for i in range(2):
            for j in range(2):
                self.drawBox(100, 100, self.grid_size * 2 + i * 200, self.grid_size * 1.5 + j * 190, COLOR_RED)  # 头像框
                self.drawBox(100, 10, self.grid_size * 2 + i * 200, self.grid_size * 4 + j * 190 - 17, COLOR_BLACK,
                             STATU_LINE_WDITH)  # 血条框
                self.drawBox(100, 10, self.grid_size * 2 + i * 200, self.grid_size * 4 + j * 190, COLOR_BLACK,
                             STATU_LINE_WDITH)  # TP框
        # 填充跑道事件文字
        self.fillCaseText()

    # 画盒子（画框）
    def drawBox(self, length, width, offset_x, offset_y, color=COLOR_BLACK, line_width=RUNWAY_LINE_WDITH, is_now=False):
        draw = self.draw
        if is_now: draw = self.now_draw
        draw.line(((OFFSET_X + offset_x, OFFSET_Y + offset_y),
                   (OFFSET_X + offset_x, OFFSET_Y + width + offset_y),
                   (OFFSET_X + length + offset_x, OFFSET_Y + width + offset_y),
                   (OFFSET_X + length + offset_x, OFFSET_Y + offset_y),
                   (OFFSET_X + offset_x, OFFSET_Y + offset_y)),
                  fill=color, width=line_width)

    # 填充跑道事件文字
    def fillCaseText(self):
        i = 0
        for runway in self.runway:
            runway_case = RUNWAY_CASE[runway["case"]]
            name = runway_case["name"]
            color = runway_case["color"]
            if i <= 9:
                self.fillText(i, 0, color, name)
            elif i <= 18:
                self.fillText(9, i - 9, color, name)
            elif i <= 27:
                self.fillText(9 - (i - 9 * 2), 9, color, name)
            else:
                self.fillText(0, 9 - (i - 9 * 3), color, name)
            i += 1

    # 同上，封装一下
    def fillText(self, grid_x, grid_y, textColeor=COLOR_BLACK, text=''):
        self.draw.text((grid_x * self.grid_size + OFFSET_X + 10, grid_y * self.grid_size + OFFSET_Y + 5),
                       text, font=self.runwayTextFont, fill=textColeor)

    # 状态条填充   最大长度96  血条offset填-16，tp条填1
    def statuLineFill(self, length, offset_x, offset_y, offset, color=COLOR_BLACK, width=8):
        self.now_draw.rectangle((OFFSET_X + self.grid_size * 2 + offset_x * 200 + 2,
                                 OFFSET_Y + self.grid_size * 4 + offset_y * 190 + offset,
                                 OFFSET_X + length + self.grid_size * 2 + offset_x * 200 + 2,
                                 OFFSET_Y + width + self.grid_size * 4 + offset_y * 190 + offset),
                                fill=color)

    # 角色当前状态数字（血量/tp）
    def roleStatuText(self, offset_x, offset_y, offset, textColeor=COLOR_BLACK, text=''):
        self.now_draw.text((OFFSET_X + 100 + self.grid_size * 2 + offset_x * 200 + 2,
                            OFFSET_Y + self.grid_size * 4 + offset_y * 190 + offset),
                           text, font=self.font, fill=textColeor)

    # 玩家信息文字
    def playerInfoText(self, offset_x, offset_y, offset, textColeor=COLOR_BLACK, text=''):
        self.now_draw.text((OFFSET_X + self.grid_size * 2 + offset_x * 200 + 2,
                            OFFSET_Y + self.grid_size * 4 + offset_y * 190 + offset),
                           text, font=self.font, fill=textColeor)

    # 角色头像位置
    def roleIconLocation(self, icon, location):
        small_icon = icon.resize((25, 25))
        if location <= 9:
            self.now_image.paste(small_icon, (OFFSET_X + 14 + self.grid_size * location,
                                              OFFSET_Y - 30))
        elif location <= 18:
            self.now_image.paste(small_icon, (OFFSET_X + 10 + self.grid_size * 10,
                                              OFFSET_Y + 14 + self.grid_size * (location - 9)))
        elif location <= 27:
            self.now_image.paste(small_icon, (OFFSET_X + 14 + self.grid_size * (9 - (location - 9 * 2)),
                                              OFFSET_Y + 10 + self.grid_size * 10))
        else:
            self.now_image.paste(small_icon, (OFFSET_X - 30,
                                              OFFSET_Y + 14 + self.grid_size * (9 - (location - 9 * 3))))


# 管理器
class manager:
    def __init__(self):
        self.playing: List[PCRScrimmage] = {}

    def is_playing(self, gid):
        return gid in self.playing

    def start(self, gid, uid, is_debug):
        return PCRScrimmage(gid, self, uid, is_debug)

    def get_game(self, gid):
        return self.playing[gid] if gid in self.playing else None

mgr = manager()
WAIT_TIME = 3  # 每x秒检查一次房间状态
PROCESS_WAIT_TIME = 1  # 避免发送太快增加的缓冲时间

STAGE_WAIT_TIME = 30  # 玩家阶段等待时间，超过这个时间判负。


# 实际时间是 STAGE_WAIT_TIME * WAIT_TIME

@create.handle()
async def game_create(bot, ev: GroupMessageEvent):
    gid, uid = ev.group_id, ev.user_id
    if mgr.is_playing(gid):
        await create.finish('有另一局游戏仍在进行中…')
    image = IMAGE_PATH / f'{gid}.png'
    if os.path.exists(image):
        os.remove(image)
    from extensive_plugin import pcr_scrimmage_debug
    if pcr_scrimmage_debug.mgr.is_playing(gid):
        await create.finish('有测试服游戏正在进行中...')

    with mgr.start(gid, uid, is_debug=True) as scrimmage:
        msg = ['大乱斗房间已创建，等待加入中。。。',
               f'{WAIT_TIME}分钟后不开始会自动结束',
               f'当前人数({scrimmage.getPlayerNum()}/{MAX_PLAYER})',
               f'（发送“加入大乱斗”加入）']
        await bot.send(ev, '\n'.join(msg))
        scrimmage.user_card_dict = await get_user_card_dict(bot, gid)

        for i in range(60):  # 从等待到正式开始的循环等待
            await asyncio.sleep(WAIT_TIME)
            if scrimmage.now_statu == NOW_STATU_OPEN:
                scrimmage.gameOpen()
                img = scrimmage.getNowImage()
                img.save(image)
                imgcode = message_builder.image(b64=pic2b64(Image.open(image)))
                await bot.send(ev, imgcode)
                await asyncio.sleep(PROCESS_WAIT_TIME)
                await scrimmage.stageRemind(bot, ev)
                break
            elif scrimmage.now_statu == NOW_STATU_END:
                break

        if scrimmage.now_statu == NOW_STATU_OPEN:
            while True:  # 开始后的循环等待
                await asyncio.sleep(WAIT_TIME)
                await scrimmage.PlayerStageTimer(gid, bot, ev)  # 玩家阶段计时器
                if (scrimmage.now_statu == NOW_STATU_END or
                        scrimmage.now_statu == NOW_STATU_WIN): break
        if scrimmage.now_statu == NOW_STATU_WIN:
            msg = ['大乱斗已结束，排名如下：']
            for i in range(len(scrimmage.rank)):
                user_card = uid2card(scrimmage.rank[i + 1], scrimmage.user_card_dict)
                puid = scrimmage.rank[i+1]
                player = scrimmage.getPlayerObj(puid)
                skill_rate = SKILL_RATE_DICT[len(scrimmage.rank)][i]
                skill_dict = load_skill_data()
                skill_dict = update_skill_data(puid, player.position, skill_dict, skill_rate)
                save_skill_data(skill_dict)
                if skill_rate > 0:
                    skill_msg = f',且对 {player.position} 角色的熟练度提高了！'
                else:
                    skill_msg = ''
                gold = GOLD_DICT[len(scrimmage.rank)][i]
                await BagUser.add_gold(puid,gid,gold)
                gold_msg = f',获得{gold}金币'
                msg.append(f'第{i + 1}名：{user_card}{gold_msg}{skill_msg}')
            await bot.send(ev, '\n'.join(msg))
        else:
            await bot.send(ev, f'游戏结束')


@join.handle()
async def game_join(bot, ev: GroupMessageEvent):
    gid, uid = ev.group_id, ev.user_id

    scrimmage = mgr.get_game(gid)
    if not scrimmage or scrimmage.now_statu != NOW_STATU_WAIT:
        return
    if uid in scrimmage.player_list:
        await join.finish('您已经在准备房间里了', at_sender=True)
    if scrimmage.getPlayerNum() >= MAX_PLAYER:
        await join.finish('人数已满，无法继续加入', at_sender=True)

    scrimmage.ready(uid)

    msg = []
    for user_id in scrimmage.player_list:
        user_card = uid2card(user_id, scrimmage.user_card_dict)
        msg.append(user_card)
    await bot.send(ev, f'已加入\n当前人数({scrimmage.getPlayerNum()}/{MAX_PLAYER})\n{" ".join(msg)}')
    if scrimmage.getPlayerNum() == MAX_PLAYER:
        await bot.send(ev,
                       f'人数已满，可开始游戏。\n' + message_builder.at(scrimmage.room_master) + '（发送“开始大乱斗”开始）')


@start.handle()
async def game_start(bot, ev: GroupMessageEvent):
    gid, uid = ev.group_id, ev.user_id

    scrimmage = mgr.get_game(gid)
    if not scrimmage or scrimmage.now_statu != NOW_STATU_WAIT:
        return
    if not uid == scrimmage.room_master:
        await start.finish('只有房主才能开始', at_sender=True)
    if scrimmage.getPlayerNum() < 2:
        await start.finish('要两个人以上才能开始', at_sender=True)

    scrimmage.now_statu = NOW_STATU_SELECT_ROLE

    role_list = '游戏开始，请选择角色，当前可选角色：\n'
    msgd = ''
    msga = ''
    msgb = ''
    msgs = ''
    for role in ROLE.values():
        if role["position"] == POSITION_DEFEND:
            msgd += f'{role["name"]} '
        if role["position"] == POSITION_ATTACK:
            msga += f'{role["name"]} '
        if role["position"] == POSITION_BURST:
            msgb += f'{role["name"]} '
        if role["position"] == POSITION_SPECIAL:
            msgs += f'{role["name"]} '
    role_list += '————————————————————\n'
    role_list += '防御：\n'
    role_list += msgd
    role_list += '\n——————————————————\n输出：\n'
    role_list += msga
    role_list += '\n——————————————————\n爆发：\n'
    role_list += msgb
    role_list += '\n——————————————————\n特殊：\n'
    role_list += msgs
    role_list += '\n——————————————————'
    role_list += '\n输入“角色详情 角色名” 可查看角色属性和技能\n输入"查看熟练度"可查看你的熟练度\n（所有人都选择角色后自动开始）\n'
    for player_id in scrimmage.player_list:
        role_list += message_builder.at(player_id)
    await bot.send(ev, role_list)


@selectcha.handle()
async def select_role(bot, ev: GroupMessageEvent):
    gid, uid = ev.group_id, ev.user_id
    scrimmage = mgr.get_game(gid)
    if not scrimmage or scrimmage.now_statu != NOW_STATU_SELECT_ROLE:
        return
    # 已加入房间的玩家才能选择角色
    if uid not in scrimmage.player_list:
        return

    image = IMAGE_PATH / f'{gid}.png'

    characterid = chara.name2id(ev.message.extract_plain_text())
    if characterid != chara.UNKNOWN and characterid in ROLE:
        if characterid in scrimmage.is_selected:
            await selectcha.finish('这个角色已经被其他玩家选择了', at_sender=True)

        scrimmage.is_selected.append(characterid)
        player = scrimmage.getPlayerObj(uid)
        player.initData(characterid, scrimmage)
        skill_dict = load_skill_data()
        skilllevel = get_skill_level(uid, player.position, skill_dict)
        if skilllevel == SKILL_RATE_NEW:
            await selectcha.send(f'你在当前定位的熟练度为：{skilllevel},没有获得任何熟练度奖励。继续努力吧！',
                                 at_sender=True)
        else:
            await selectcha.send(f'你在当前定位的熟练度为：{skilllevel},发送"熟练度奖励"来查询你获得的熟练度奖励',
                                 at_sender=True)

        img = player.role_icon
        img.save(image)
        imgcode = message_builder.image(b64=pic2b64(Image.open(image)))
        await selectcha.send(f"你选择的角色是：{player.name}", at_sender=True)

        if scrimmage.checkAllPlayerSelectRole():
            await asyncio.sleep(PROCESS_WAIT_TIME)
            await bot.send(ev, "所有人都选择了角色，大乱斗即将开始！\n碾碎他们")
            await asyncio.sleep(PROCESS_WAIT_TIME)
            scrimmage.now_statu = NOW_STATU_OPEN

@skillbonus.handle()
async def bonus(bot, ev: GroupMessageEvent):
    gid, uid = ev.group_id, ev.user_id
    scrimmage = mgr.get_game(gid)

    if not scrimmage or not scrimmage.now_statu in (NOW_STATU_OPEN,NOW_STATU_SELECT_ROLE):
        return
    if uid not in scrimmage.player_list:
        await skillbonus.finish('你还没有选择任何角色', at_sender=True)

    player = scrimmage.getPlayerObj(uid)
    skill_dict = load_skill_data()
    skilllevel = get_skill_level(uid, player.position, skill_dict)
    if skilllevel == SKILL_RATE_NEW:
        await skillbonus.finish('你当前没有获得任何熟练度奖励。继续努力吧！')
    bonus_dict = get_skill_bonus(uid, player.position, skill_dict)
    msg = '你的熟练度奖励如下：'
    for k, v in bonus_dict.items():
        if k == "defend":
            msg += f'\n防御力+{v}'
        if k == "health":
            msg += f'\n生命值+{v}'
        if k == "attack":
            msg += f'\n攻击力+{v}'
        if k == "distance":
            msg += f'\n攻击距离+{v}'
        if k == "tp":
            msg += f'\n初始tp值+{v}'
    await skillbonus.finish(msg, at_sender=True)


@dice.handle()
async def throw_dice(bot, ev: GroupMessageEvent):
    gid, uid = ev.group_id, ev.user_id

    scrimmage = mgr.get_game(gid)
    if not scrimmage or scrimmage.now_statu != NOW_STATU_OPEN:
        return
    # 已加入房间的玩家才能丢色子
    if uid not in scrimmage.player_list:
        return
    # 不是当前回合的玩家无法丢色子
    if scrimmage.getNowTurnPlayerObj().user_id != uid:
        return
    # 当前回合不是丢色子状态无法丢色子
    if scrimmage.getPlayerObj(uid).now_stage != NOW_STAGE_DICE:
        return

    step = random.choice(range(1, 9))
    await bot.send(ev, '色子结果为：' + str(step))
    await scrimmage.throwDice(uid, step, bot, ev)
    scrimmage.refreshNowImageStatu()

    image = IMAGE_PATH / f'{gid}.png'

    img = scrimmage.getNowImage()
    img.save(image)
    imgcode = message_builder.image(b64=pic2b64(Image.open(image)))
    await bot.send(ev, imgcode)
    await asyncio.sleep(PROCESS_WAIT_TIME)
    await scrimmage.stageRemind(bot, ev)


@skill.handle()
async def use_skill(bot, ev: GroupMessageEvent):
    gid, uid = ev.group_id, ev.user_id

    msg_text = ev.raw_message
    match = re.match(r'^(\d+)( |) *(?:\[CQ:at,qq=(\d+)\])?', msg_text)
    if not match and msg_text != '跳过':
        return
    scrimmage = mgr.get_game(gid)
    if not scrimmage or scrimmage.now_statu != NOW_STATU_OPEN:
        return
    # 已加入房间的玩家才能释放技能
    if uid not in scrimmage.player_list:
        return
    # 不是当前回合的玩家无法释放技能
    if scrimmage.getNowTurnPlayerObj().user_id != uid:
        return
    # 当前回合不是放技能状态无法放技能
    if scrimmage.getPlayerObj(uid).now_stage != NOW_STAGE_SKILL:
        return

    skill_id = ''
    goal_player_id = ''
    if match:
        skill_id = match.group(1)
        goal_player_id = match.group(3) or '0'
    else:
        skill_id = '0'
        goal_player_id = '0'

    goal_player_id = int(goal_player_id)
    skill_id = int(skill_id)

    if goal_player_id != 0 and goal_player_id not in scrimmage.player_list:
        await bot.send(ev, "不能选择场外玩家")
        return

    ret = await scrimmage.useSkill(skill_id, uid, goal_player_id, bot, ev)
    if ret == RET_ERROR:
        return

    # 回合切换
    result = scrimmage.turnChange()
    if result != 0:
        await skill.send(message_builder.at(result) + "已经复活！")

    scrimmage.refreshNowImageStatu()  # 刷新当前显示状态

    image = IMAGE_PATH / f'{gid}.png'

    img = scrimmage.getNowImage()
    img.save(image)
    imgcode = message_builder.image(b64=pic2b64(Image.open(image)))
    await bot.send(ev, imgcode)
    await asyncio.sleep(PROCESS_WAIT_TIME)
    await scrimmage.stageRemind(bot, ev)


@surrend.handle()
async def throw_dice(bot, ev: GroupMessageEvent):
    gid, uid = ev.group_id, ev.user_id

    scrimmage = mgr.get_game(gid)
    if not scrimmage or scrimmage.now_statu != NOW_STATU_OPEN:
        return
    # 已加入房间的玩家才能投降
    if uid not in scrimmage.player_list:
        return
    # 不是当前回合的玩家无法投降
    if scrimmage.getNowTurnPlayerObj().user_id != uid:
        return

    player = scrimmage.getPlayerObj(uid)
    scrimmage.outDispose(player)
    await bot.send(ev, f'{uid2card(uid, scrimmage.user_card_dict)}已投降')
    if scrimmage.now_statu == NOW_STATU_OPEN:
        scrimmage.turnChange()
        scrimmage.refreshNowImageStatu()
        image = IMAGE_PATH / f'{gid}.png'

        img = scrimmage.getNowImage()
        img.save(image)
        imgcode = message_builder.image(b64=pic2b64(Image.open(image)))
        await bot.send(ev, imgcode)
        await asyncio.sleep(PROCESS_WAIT_TIME)
        await scrimmage.stageRemind(bot, ev)


@prop.handle()
async def check_property(bot, ev: GroupMessageEvent):
    gid, uid = ev.group_id, ev.user_id
    scrimmage = mgr.get_game(gid)
    if not scrimmage or scrimmage.now_statu != NOW_STATU_OPEN:
        return
    if uid not in scrimmage.player_list:
        return
    player = scrimmage.getPlayerObj(uid)
    msg = player.checkStatu(scrimmage)
    await bot.send(ev, "\n".join(msg))


@info.handle()
async def check_role(bot, ev: GroupMessageEvent, arg: Message = CommandArg()):
    role_name = arg.extract_plain_text().strip()
    characterid = chara.name2id(role_name)
    if characterid != chara.UNKNOWN and characterid in ROLE:
        role_info = ROLE[characterid]
        msg = [
            f"名字：{role_info['name']}",
            f"角色定位：{role_info['position']}",
            f"生命值：{role_info['health']}",
            f"TP：{role_info['tp']}",
            f"攻击距离：{role_info['distance']}",
            f"攻击力：{role_info['attack']}",
            f"防御力：{role_info['defensive']}",
            f"暴击率：{role_info['crit'] > MAX_CRIT and MAX_CRIT or role_info['crit']}%",
            f"被动技能：{role_info['passive_text'] if role_info.get('passive_text', -1) != -1 else '无'}",
            f"技能：(若有双技能组则以斜线分隔)",
        ]
        skill_num = 1
        if role_info.get('passive', -1) == PASSIVE_HEALTHTP:
            for skill in role_info['active_skills']:
                msg.append(f"  技能{skill_num}：{skill['name']}({skill['tp_cost']}生命值)：{skill['text']}")
                skill_num += 1
        else:
            for skill in role_info['active_skills']:
                msg.append(f"  技能{skill_num}：{skill['name']}({skill['tp_cost']}tp)：{skill['text']}")
                skill_num += 1
        return await bot.send(ev, "\n".join(msg))

    await bot.send(ev, '不存在的角色')


@finish.handle()
async def game_end(bot, ev: GroupMessageEvent):
    gid, uid = ev.group_id, ev.user_id

    scrimmage = mgr.get_game(gid)
    if not scrimmage or scrimmage.now_statu == NOW_STATU_END:
        return
    if not await GROUP_ADMIN(bot, ev) and not await GROUP_OWNER(bot, ev) and not uid == scrimmage.room_master:
        await finish.finish('只有群管理或房主才能强制结束', at_sender=True)

    scrimmage.now_statu = NOW_STATU_END
    await bot.send(ev, f"您已强制结束大乱斗，请等待结算")


@rule.handle()
async def game_help_all_role(bot, ev: GroupMessageEvent):
    msg = '''大乱斗规则
1、和大富翁类似，一个正方形环形跑道，跑道上有多个事件，通过丢色子走到特定的位置触发事件
2、可多个玩家同时玩，最多4个，最少2个。每个玩家可选择一个角色列表里的角色，不同的角色有不同的属性、技能
3、角色有tp值，可用来释放技能。每次投掷色子，所有玩家都会增加tp值，受到伤害也会增加tp值
4、需要选择目标的技能释放范围可能有距离限制，以角色属性的攻击距离为准
5、避免游戏时长过长，每(场上玩家数量)个玩家回合增加一次攻击力和攻击距离
6、可投降
7、活到最后获胜（吃鸡？）

--回合机制：
玩家回合：当前默认的回合机制，每个玩家丢一次色子为经过一回合
自我回合：另一种回合机制，每次轮到自己后才为经过一回合
'''
    await bot.send(ev, msg)


@character.handle()
async def game_help_rule(bot, ev: GroupMessageEvent):
    msgd = ''
    msga = ''
    msgb = ''
    msgs = ''
    for role in ROLE.values():
        if role["position"] == POSITION_DEFEND:
            msgd += f'{role["name"]} '
        if role["position"] == POSITION_ATTACK:
            msga += f'{role["name"]} '
        if role["position"] == POSITION_BURST:
            msgb += f'{role["name"]} '
        if role["position"] == POSITION_SPECIAL:
            msgs += f'{role["name"]} '
    msg = '当前可选角色有：\n'
    msg += '————————————————————\n'
    msg += '防御：\n'
    msg += msgd
    msg += '\n——————————————————\n输出：\n'
    msg += msga
    msg += '\n——————————————————\n爆发：\n'
    msg += msgb
    msg += '\n——————————————————\n特殊：\n'
    msg += msgs
    msg += '\n——————————————————'
    msg += f'\n共{len(ROLE)}位角色'
    await bot.send(ev, msg)
