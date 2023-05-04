##可用角色

"""
##可用角色可自定义增加，详细看下面的示例

基础属性：
	name			名字		string
	health			生命值		number
	distance		攻击距离	number
	attack			攻击力		number
	defensive		防御力		number
	tp				能量值		number
	crit			暴击		float	暴击概率百分比，1为100%
	active_skills	主动技能	list[dict]
	passive_skills	被动技能	list[dict] 依赖主动技能
		被动技能的主要作用，是为了让一个主动技能可以同时选择不同的触发对象
		例如：yly，砍别人一刀自己掉血
		被动技能优先级比主动高，可以先对自身增加攻击力后再进行攻击
		（其实，把这个 “被动技能” 说成是 “附带效果” 也可以，单纯为了区分不同的触发对象而已）

技能：
	name			技能名称	string
	text			技能描述	string
	tp_cost			消耗tp		number
	effect			技能效果	list[dict]
	trigger			触发对象	string
	passive			被动		list[number] 数字对应基础属性的passive_skill

	################（技能效果可增加，增加后在 skillEffect() 里做处理）################
	效果effect：(可选单个或多个) (被动技能：对自己和对目标的效果要分开)
		attr				属性改变，如果要同时改变多个属性值，每个属性都需要单独添加一条被动

		move				移动，正数为前进负数为后退	number
		move_goal			向目标移动（一个技能有多个效果且包括向目标移动，向目标移动效果必须最先触发）
							这个效果必须放在被动
		ignore_dist			无视距离，参数填啥都行，不会用到

		make_it_out_tp		令目标出局时tp变动
		make_it_out_turn	令目标出局时锁定回合

	################触发对象可继续增加，添加后在 skillTrigger() 里做处理################
	触发对象trigger：
		select				选择目标

		all					对所有人有效(包括自己)
		all_except_me		对所有人有效(除了自己)
		me					只对自己有效

		near				离自己最近

"""

EFFECT_HURT = "hurt"  # 造成伤害	tuple元组 (数值，加成类型，加成的数值对象，加成比例，是否为真实伤害)
# 加成类型：attr.py , 为0时无加成; 加成的数值对象：0自己 1目标

# 需要EFFECT_HURT作为前置	↓
EFFECT_ELIMINATE = "eliminate"  # 斩杀效果，目标生命值越低造成的伤害越高		tuple元组 (目标生命值降低比例, 伤害数值)
EFFECT_STAND = "stand"  # 背水效果，自身生命值越低造成的伤害越高		tuple元组 (自身生命值降低比例, 伤害数值)
EFFECT_LIFESTEAL = "life_steal"  # 生命偷取	float 伤害-生命值之间的转换比例
EFFECT_SKIP_TRUEDAMAGE = "skip_truedamage" # 使用技能前跳过特定回合数，则变为真实伤害       number 需要跳过的回合数
EFFECT_SKIP_CRIT = "skip_crit" # 使用技能前每跳过一个回合，此次暴击率增加     number 暴击率增加的数值
# 需要EFFECT_HURT作为前置	↑

EFFECT_BUFF = "buff"  # buff效果		list[tuple,tuple] [(BuffType.xx, 数值, 可触发次数), (...)]
EFFECT_BUFF_BY_BT = "buff_by_bt"  # buff效果触发(通过buff类型)	list[BuffType]		立即触发指定buff类型的buff效果
# EFFECT_BUFF_BY_BT需要EFFECT_BUFF作为前置
EFFECT_ATTR_CHANGE = "attr"  # 属性改变，正数为增加，负数为减少	list[tuple,tuple] [(属性类型，数值，加成类型，加成比例), (...)]
# 属性类型/加成类型：attr.py , 为0时无加成
EFFECT_DEL_BUFF = "del_buff"

EFFECT_MOVE = "move"  # 移动，正数为前进负数为后退（触发跑道事件）	number
EFFECT_MOVE_GOAL = "move_goal"  # 向目标移动（一个技能有多个效果且包括向目标移动，向目标移动效果必须最先触发） tuple元组(移动距离，是否无视攻击范围)
# 这个效果必须放在被动（不触发跑道事件）
EFFECT_IGNORE_DIST = "ignore_dist"  # 无视距离效果，参数随便填，不会用到
# 这个效果必须放在被动
EFFECT_AOE = "aoe"  # 范围效果			tuple	(半径范围, 是否对自己生效)
EFFECT_HIT_BACK = "hit_back"  # 击退				number	填正数为击退x格子，负数为拉近
EFFECT_LOCKTURN = "lock_turn"  # 锁定回合			number	不会切换到下一个玩家，当前玩家继续丢色子和放技能
EFFECT_SKILL_CHANGE = "skill_change"  # 更改技能			tuple	(BuffType.xx, [被动技能编号1, 被动技能编号2])
# 当自身存在某个特定buff时，技能效果替换为特定被动效果，原效果不触发
EFFECT_JUMP = "jump"  # 选择目标的移动效果，移动到目标身边，参数随便填，不会用到
# 效果相对比较特殊，最好放在被动且搭配TRIGGER_SELECT_EXCEPT_ME使用

EFFECT_REVENGE = "revenge"
EFFECT_KILL_REBORN = "kill_reborn"
EFFECT_REBORN = "reborn"
EFFECT_TP_LOCKTURN = "tp_lockturn"
EFFECT_OUT_TP = "make_it_out_tp"  # 令目标出局时tp变动		number
EFFECT_OUT_LOCKTURN = "make_it_out_turn"  # 令目标出局时锁定回合	number	锁定回合：不会切换到下一个玩家，当前玩家继续丢色子和放技能
EFFECT_TP_REQUEST = "tp_request"
EFFECT_COST_TP = "cost_tp"
EFFECT_RANDOM = "random"
EFFECT_SWEETBUFF = "sweetbuff"
EFFECT_GET_SWEETIE = "get_sweetie"
EFFECT_CAT_POISION = "cat_poision"
EFFECT_SWEET_LOCKTURN = "sweet_lockturn"
EFFECT_DOUBLESPEED = "doublespeed"
EFFECT_ATTACK_BURST = "attack_burst"
EFFECT_HEALTH_DOWN = "health_down"
EFFECT_SKIP_JUDGE = "skip_judge" # 刀酱特有技能效果，不作为其他技能的效果使用
EFFECT_UNKNOWN = "unknown" # 刀酱特有技能效果，不作为其他技能的效果使用



EFFECT_DIZZINESS = "dizziness"  # 眩晕效果，跳过特定玩家一回合 number

TRIGGER_SELECT = "select"  # 选择目标(包括自己)
TRIGGER_SELECT_EXCEPT_ME = "select_except_me"  # 选择目标(除了自己)
TRIGGER_ALL = "all"  # 对所有人有效(包括自己)
TRIGGER_ALL_EXCEPT_ME = "all_except_me"  # 对所有人有效(除了自己)
TRIGGER_ME = "me"  # 只对自己有效
TRIGGER_NEAR = "near"  # 离自己最近的目标

# 角色定位
POSITION_DEFEND = "防御型" # 防御，以高防御高血量进行持续战斗的定位
POSITION_ATTACK = "输出型" # 输出，持续输出兼顾发育的定位
POSITION_BURST = "爆发型" # 爆发，以高爆发输出秒人的定位
POSITION_SPECIAL = "特殊型" # 特殊，拥有独特技能效果的定位

# 被动技能列表
PASSIVE_REBORN = "reborn"
PASSIVE_HEALTHTP = "healthtp"
PASSIVE_SWEETIE = "sweetie"
PASSIVE_ATTACKSPEED = "attackspeed"
PASSIVE_SKIP = "skip"

from .attr import Attr
from .buff import BuffType

# 角色字典
ROLE = {
    # 注意：id要和_pcr_data.py里对应角色一样

    1701: {
        "name": "环奈",
        "position": POSITION_ATTACK,

        "health": 1000,
        "distance": 9,
        "attack": 110,
        "defensive": 80,
        "crit": 10,
        "tp": 0,

        "active_skills": [
            {
                "name": "普通攻击",
                "text": "对目标造成0(+1.0自身攻击力)伤害",
                "tp_cost": 0,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (0, Attr.ATTACK, 0, 1, False)
                }
            },
            {
                "name": "冲击之刃",
                "text": "对目标造成及其半径3范围内所有玩家造成90(+1.2自身攻击力)伤害，并降低20护甲",
                "tp_cost": 20,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (90, Attr.ATTACK, 0, 1.2, False),
                    EFFECT_ATTR_CHANGE: [(Attr.DEFENSIVE, -20, 0, 0)],
                    EFFECT_AOE: (3, False)
                }
            },
            {
                "name": "天赐之物",
                "text": "所有玩家增加50点攻击力和10%暴击率，自身持续永久，其他玩家持续1个自我回合",
                "tp_cost": 30,
                "trigger": TRIGGER_ALL_EXCEPT_ME,
                "passive": [0],

                "effect": {
                    EFFECT_BUFF: [
                        (BuffType.NormalSelfAttrAtkUp, 50, 1),
                        (BuffType.NormalSelfAttrCritUp, 10, 1),
                    ],
                }
            },
            {
                "name": "闪耀之刃",
                "text": "对目标造成及其半径4范围内所有玩家造成120(+1.2自身攻击力)伤害，并将所造成伤害的20%转为生命值。自身增加10%暴击率和0.1倍爆伤",
                "tp_cost": 40,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [1],

                "effect": {
                    EFFECT_HURT: (120, Attr.ATTACK, 0, 1.2, False),
                    EFFECT_LIFESTEAL: 0.2,
                    EFFECT_AOE: (4, False),
                }
            },
        ],
        "passive_skills": [
            {
                "trigger": TRIGGER_ME,
                "effect": {
                    EFFECT_ATTR_CHANGE: [
                        (Attr.CRIT, 10, 0, 0),
                        (Attr.ATTACK, 50, 0, 0)
                    ],
                }
            },
            {
                "trigger": TRIGGER_ME,
                "effect": {
                    EFFECT_ATTR_CHANGE: [
                        (Attr.CRIT, 10, 0, 0),
                        (Attr.CRIT_HURT, 0.1, 0, 0)
                    ],
                }
            },
        ]
    },
    1068: {
        "name": "晶",
        "position": POSITION_ATTACK,

        "health": 1300,
        "distance": 9,
        "attack": 50,
        "defensive": 100,
        "crit": 5,
        "tp": 0,

        "active_skills": [
            {
                "name": "普通攻击",
                "text": "对目标造成0(+1.0自身攻击力)伤害,并回复10点TP",
                "tp_cost": 0,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [2],

                "effect": {
                    EFFECT_HURT: (0, Attr.ATTACK, 0, 1, False)
                }
            },
            {
                "name": "热身!/加速！",
                "text": "热身！:增加自己80攻击力、15%的暴击率持续4回合。\n " +
                        "\t加速！:永久增加自己100点攻击、20%的暴击率，并展开+10TP上升领域3回合。",
                "tp_cost": 20,
                "trigger": TRIGGER_ME,
                "passive": [],
                "effect": {
                    EFFECT_BUFF: [
                        (BuffType.NormalAttrAtkUp, 80, 4),
                        (BuffType.NormalAttrCritUp, 15, 4),
                    ],
                    EFFECT_SKILL_CHANGE: (BuffType.Akriasworld, [0]),
                }
            },
            {
                "name": "岩石穿刺",
                "text": "岩石穿刺！:降低目标20点防御力，并造成100(+0.8自身攻击力)，并将所造成伤害的10%转为生命值；\n" +
                        "\t如果已释放万物改造，则该技能将额外永久降低玩家20点攻击力，且附加自身损失生命值的额外真实伤害，并附带20%生命偷取。",
                "tp_cost": 30,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],
                "effect": {
                    EFFECT_ATTR_CHANGE: [(Attr.DEFENSIVE, 20, 0, 0)],
                    EFFECT_HURT: (100, Attr.ATTACK, 0, 0.8, False),
                    EFFECT_LIFESTEAL: 0.10,
                    EFFECT_SKILL_CHANGE: (BuffType.Akriasworld, [3])
                }
            },
            {
                "name": "万物改造/万物归灵",
                "text": "使用七冠权力，大幅提升自身属性，回复30tp，并将其他所有玩家防御力降为0，且继续下一回合。\n" +
                        "\t万物归灵:晶将所贮存的能量一并释放，并造成0(+3.0自身攻击力)的真实伤害，并回复自身大量的生命值。",
                "tp_cost": 100,
                "trigger": TRIGGER_ME,
                "passive": [1],
                "effect": {
                    EFFECT_ATTR_CHANGE: [(Attr.NOW_TP, 30, 0, 0)],
                    EFFECT_BUFF: [
                        (BuffType.Akriasworld, 0, 99999),
                        (BuffType.NormalAttrAtkUp, 200, 99999),
                        (BuffType.NormalAttrCritUp, 25, 99999),
                        (BuffType.NormalAttrDefUp, 30, 99999),
                    ],
                    EFFECT_LOCKTURN: 1,
                    EFFECT_SKILL_CHANGE: (BuffType.Akriasworld, [4])
                }
            }
        ],
        "passive_skills": [
            {
                "trigger": TRIGGER_ME,
                "effect": {
                    EFFECT_BUFF: [(BuffType.TurnAttrTPUp, 10, 3)],
                    EFFECT_ATTR_CHANGE: [
                        (Attr.ATTACK, 100, 0, 0),
                        (Attr.CRIT, 20, 0, 0)
                    ],
                }
            },
            {
                "trigger": TRIGGER_ALL_EXCEPT_ME,
                "effect": {
                    EFFECT_ATTR_CHANGE: [(Attr.DEFENSIVE, 0, Attr.DEFENSIVE, 1)],
                }
            },
            {
                "trigger": TRIGGER_ME,
                "effect": {
                    EFFECT_ATTR_CHANGE: [(Attr.NOW_TP, 10, 0, 0)],
                }
            },
            {
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "effect": {
                    EFFECT_HURT: (100, Attr.ATTACK, 0, 0.8, True),
                    EFFECT_STAND: (1, 1.5),
                    EFFECT_LIFESTEAL: 0.2,
                    EFFECT_ATTR_CHANGE: [
                        (Attr.DEFENSIVE, -20, 0, 0),
                        (Attr.ATTACK, -20, 0, 0)
                    ],
                }
            },
            {
                "trigger": TRIGGER_ALL_EXCEPT_ME,
                "effect": {
                    EFFECT_HURT: (0, Attr.ATTACK, 0, 3.0, True),
                    EFFECT_LIFESTEAL: 5,
                }
            },
        ]
    },
    1061: {
        "name": "矛依未",
        "position": POSITION_BURST,

        "health": 1200,
        "distance": 5,
        "attack": 130,
        "defensive": 60,
        "crit": 10,
        "tp": 0,

        "active_skills": [
            {
                "name": "普通攻击",
                "text": "对目标造成0(+1.0自身攻击力)伤害,并回复5点TP",
                "tp_cost": 0,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [3],

                "effect": {
                    EFFECT_HURT: (0, Attr.ATTACK, 0, 1, False)
                }
            },
            {
                "name": "吓到你发抖！/ 天楼回刃斩",
                "text": ("吓到你发抖！:对目标造成50(+0.8自身攻击力)伤害，并降低30点攻击力持续3玩家回合，且将其击退5步 \n" +
                         "\t天楼回刃斩：对目标造成120(+1.5自身攻击力)伤害，并将造成伤害的12%转化为生命值"),
                "tp_cost": 20,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],
                "effect": {
                    EFFECT_HURT: (50, Attr.ATTACK, 0, 0.8, False),
                    EFFECT_BUFF: [(BuffType.NormalAttrAtkDown, -30, 3)],
                    EFFECT_HIT_BACK: 5,
                    EFFECT_SKILL_CHANGE: (BuffType.TenRouHaDanKen, [0]),
                }
            },
            {
                "name": "这边啦这边！/ 天楼闪薙斩",
                "text": ("这边啦这边！:降低目标及其半径范围2以内所有玩家45点防御力，持续8个玩家回合，并减少30TP \n" +
                         "\t天楼闪薙斩：对目标及其半径范围3以内所有玩家造成100(+1.1自身攻击力)伤害，并将造成伤害的5%转化为生命值"),
                "tp_cost": 20,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],
                "effect": {
                    EFFECT_ATTR_CHANGE: [(Attr.NOW_TP, -30, 0, 0)],
                    EFFECT_BUFF: [(BuffType.NormalAttrDefDown, -45, 8)],
                    EFFECT_AOE: (2, False),
                    EFFECT_SKILL_CHANGE: (BuffType.TenRouHaDanKen, [1]),
                }
            },
            {
                "name": "天楼霸断剑",
                "text": "对目标造成50(+1.0自身攻击力)伤害，并巨幅增加自身所有属性，持续全场！",
                "tp_cost": 100,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [2],
                "effect": {
                    EFFECT_HURT: (50, Attr.ATTACK, 0, 1, False),
                }
            }
        ],
        "passive_skills": [
            {
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "effect": {
                    EFFECT_HURT: (120, Attr.ATTACK, 0, 1.5, False),
                    EFFECT_LIFESTEAL: 0.12,
                }
            },
            {
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "effect": {
                    EFFECT_HURT: (100, Attr.ATTACK, 0, 1.1, False),
                    EFFECT_AOE: (3, False),
                    EFFECT_LIFESTEAL: 0.05,
                }
            },
            {
                "trigger": TRIGGER_ME,
                "effect": {
                    EFFECT_ATTR_CHANGE: [(Attr.NOW_TP, 100, 0, 0)],
                    EFFECT_BUFF: [(BuffType.TenRouHaDanKen, 5, 99999),
                                  (BuffType.NormalAttrAtkUp, 120, 99999),
                                  (BuffType.NormalAttrCritUp, 30, 99999),
                                  (BuffType.NormalAttrMaxHelUp, 300, 99999)],
                    EFFECT_BUFF_BY_BT: [BuffType.NormalAttrAtkUp,
                                        BuffType.NormalAttrCritUp,
                                        BuffType.NormalAttrMaxHelUp],
                }
            },
            {
                "trigger": TRIGGER_ME,
                "effect": {
                    EFFECT_ATTR_CHANGE: [(Attr.NOW_TP, 5, 0, 0)],
                }
            }
        ]
    },
    1060: {
        "name": "凯露",
        "position": POSITION_ATTACK,

        "health": 1050,
        "distance": 10,
        "attack": 125,
        "defensive": 60,
        "crit": 20,
        "tp": 0,

        "active_skills": [
            {
                "name": "普通攻击",
                "text": "对目标造成0(+1.0自身攻击力)伤害",
                "tp_cost": 10,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (0, Attr.ATTACK, 0, 1, False)
                }
            },
            {
                "name": "闪电球",
                "text": "对目标及其范围1内的敌人造成70(+0.7自身攻击力)伤害并减少50防御(持续4回合)，并增加自身20点攻击力",
                "tp_cost": 20,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [0],
                "effect": {
                    EFFECT_HURT: (70, Attr.ATTACK, 0, 0.7, False),
                    EFFECT_BUFF: [(BuffType.NormalAttrDefDown, -50, 4)],
                    EFFECT_AOE: (1, False),
                }
            },
            {
                "name": "能量吸附",
                "text": "对目标造成50(+1.5自身攻击力)伤害，并将造成伤害的30%转换为自身生命值，并回复自身40点TP",
                "tp_cost": 30,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [1],
                "effect": {
                    EFFECT_HURT: (40, Attr.ATTACK, 0, 1.5, False),
                    EFFECT_LIFESTEAL: 0.3,
                }
            },
            {
                "name": "格林爆裂",
                "text": "对所有人造成100(+2.00自身攻击力)真实伤害",
                "tp_cost": 60,
                "trigger": TRIGGER_ALL_EXCEPT_ME,
                "passive": [],
                "effect": {
                    EFFECT_HURT: (100, Attr.ATTACK, 0, 2.00, True),
                }
            }
        ],
        "passive_skills": [
            {
                "trigger": TRIGGER_ME,
                "effect": {
                    EFFECT_ATTR_CHANGE: [(Attr.ATTACK, 20, 0, 0)],
                }
            },
            {
                "trigger": TRIGGER_ME,
                "effect": {
                    EFFECT_ATTR_CHANGE: [(Attr.NOW_TP, 20, 0, 0)],
                }
            }
        ],

    },

    1059: {
        "name": "可可萝",
        "position": POSITION_DEFEND,

        "health": 1000,
        "distance": 6,
        "attack": 50,
        "defensive": 70,
        "crit": 5,
        "tp": 0,

        "active_skills": [
            {
                "name": "普通攻击",
                "text": "对目标造成0(+1.0自身攻击力)伤害",
                "tp_cost": 0,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (0, Attr.ATTACK, 0, 1, False)
                }
            },
            {
                "name": "三连击",
                "text": "向目标移动3格，并对目标造成100(+1.5自身攻击力)伤害",
                "tp_cost": 20,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [0],
                "effect": {
                    EFFECT_HURT: (100, Attr.ATTACK, 0, 1.5, False)
                }
            },
            {
                "name": "极光守护",
                "text": "增加1000点防御力，持续4个玩家回合",
                "tp_cost": 20,
                "trigger": TRIGGER_ME,
                "passive": [],
                "effect": {
                    EFFECT_BUFF: [(BuffType.NormalAttrDefUp, 1000, 4)],
                }
            },
            {
                "name": "光之加护",
                "text": "自身回复300点生命值，并增加50点攻击力",
                "tp_cost": 50,
                "trigger": TRIGGER_ME,
                "passive": [],
                "effect": {
                    EFFECT_ATTR_CHANGE: [
                        (Attr.NOW_HEALTH, 250, 0, 0),
                        (Attr.ATTACK, 50, 0, 0)],
                }
            }
        ],
        "passive_skills": [
            {
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "effect": {
                    EFFECT_MOVE_GOAL: (3, False),
                }
            }
        ]
    },
    1058: {
        "name": "佩可",
        "position": POSITION_DEFEND,

        "health": 1800,
        "distance": 5,
        "attack": 55,
        "defensive": 82,
        "crit": 5,
        "tp": 0,

        "active_skills": [
            {
                "name": "普通攻击",
                "text": "对目标造成0(+1.8自身攻击力)伤害",
                "tp_cost": 0,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (0, Attr.ATTACK, 0, 1.8, False)
                }
            },
            {
                "name": "跳砍",
                "text": "对目标造成50(+1.5自身防御力)伤害",
                "tp_cost": 20,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (50, Attr.DEFENSIVE, 0, 1.5, False)
                }
            },
            {
                "name": "超大饭团",
                "text": "回复自身100(+0.8自身防御力)生命值，并增加30点防御力",
                "tp_cost": 25,
                "trigger": TRIGGER_ME,
                "passive": [],

                "effect": {
                    EFFECT_ATTR_CHANGE: [
                        (Attr.NOW_HEALTH, 100, Attr.DEFENSIVE, 0.8),
                        (Attr.DEFENSIVE, 30, 0, 0)],
                }
            },
            {
                "name": "公主突袭",
                "text": "向目标移动5格，对目标造成350真实伤害，并增加自身45点防御力",
                "tp_cost": 50,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [0, 1],

                "effect": {
                    EFFECT_HURT: (350, Attr.ATTACK, 0, 0, True),
                }
            }
        ],
        "passive_skills": [
            {
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "effect": {
                    EFFECT_MOVE_GOAL: (5, False),
                }
            },
            {
                "trigger": TRIGGER_ME,
                "effect": {
                    EFFECT_ATTR_CHANGE: [(Attr.DEFENSIVE, 45, 0, 0)],
                }
            }
        ]
    },
    1057: {
        "name": "姬塔",
        "position": POSITION_BURST,

        "health": 900,
        "distance": 5,
        "attack": 90,
        "defensive": 60,
        "crit": 15,
        "tp": 0,

        "active_skills": [
            {
                "name": "普通攻击",
                "text": "对目标造成0(+1.0攻击力)点伤害",
                "tp_cost": 0,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (0, Attr.ATTACK, 0, 1, False)
                }
            },
            {
                "name": "广域斩击",
                "text": "对目标造80(+1.0攻击力)伤害，恢复自身40TP",
                "tp_cost": 20,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [1],
                "effect": {
                    EFFECT_HURT: (80, Attr.ATTACK, 0, 1.0, False),
                }
            },
            {
                "name": "剑意迸发",
                "text": "恢复自身50TP，并提升20点TP上限和10%暴击率",
                "tp_cost": 30,
                "trigger": TRIGGER_ME,
                "passive": [],
                "effect": {
                    EFFECT_ATTR_CHANGE: [
                        (Attr.NOW_TP, 50, 0, 0),
                        (Attr.MAX_TP, 20, 0, 0),
                        (Attr.CRIT, 10, 0, 0)
                    ],
                }
            },
            {
                "name": "星河一天",
                "text": "对离自己最近的目标造成150(+1.5攻击力)伤害，并回复30点TP和提升0.2倍暴击伤害。所造成伤害的20%将转为生命值。",
                "tp_cost": 80,
                "trigger": TRIGGER_NEAR,
                "passive": [0],
                "effect": {
                    EFFECT_HURT: (150, Attr.ATTACK, 0, 1.5, False),
                    EFFECT_LIFESTEAL: 0.3,
                }
            },
        ],

        "passive_skills": [
            {
                "trigger": TRIGGER_ME,
                "effect": {
                    EFFECT_ATTR_CHANGE: [
                        (Attr.NOW_TP, 30, 0, 0),
                        (Attr.CRIT_HURT, 0.2, 0, 0),
                    ],
                }
            },
            {
                "trigger": TRIGGER_ME,
                "effect": {
                    EFFECT_ATTR_CHANGE: [(Attr.NOW_TP, 40, 0, 0)],
                }
            }
        ]
    },
    1052: {
        "name": "莉玛",
        "position": POSITION_DEFEND,

        "health": 1700,
        "distance": 5,
        "attack": 0,
        "defensive": 160,
        "crit": 0,
        "tp": 0,

        "active_skills": [
            {
                "name": "普通攻击",
                "text": "对目标造成75点真实伤害",
                "tp_cost": 0,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (75, Attr.ATTACK, 0, 0, True)
                }
            },
            {
                "name": "护盾",
                "text": "为自己增加一个200点生命值的护盾（只可触发1次），并增加10点防御力",
                "tp_cost": 30,
                "trigger": TRIGGER_ME,
                "passive": [],

                "effect": {
                    EFFECT_BUFF: [(BuffType.Shield, 200, 1)],
                    EFFECT_ATTR_CHANGE: [(Attr.DEFENSIVE, 10, 0, 0)],
                }
            },
            {
                "name": "毛茸茸突袭",
                "text": "向目标移动3格，对目标造成60(+0.3自身防御力)伤害，并增加自身32点防御",
                "tp_cost": 24,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [0, 1],

                "effect": {
                    EFFECT_HURT: (60, Attr.DEFENSIVE, 0, 0.3, False),
                }
            },
            {
                "name": "毛茸茸挥击",
                "text": "向目标移动4格，对目标造成140(+0.8自身防御力)伤害，并增加自身75点防御",
                "tp_cost": 66,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [2, 3],

                "effect": {
                    EFFECT_HURT: (140, Attr.DEFENSIVE, 0, 0.8, False),
                },
            }
        ],
        "passive_skills": [
            {
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "effect": {
                    EFFECT_MOVE_GOAL: (3, False),
                }
            },
            {
                "trigger": TRIGGER_ME,
                "effect": {
                    EFFECT_ATTR_CHANGE: [(Attr.DEFENSIVE, 32, 0, 0)],
                }
            },
            {
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "effect": {
                    EFFECT_MOVE_GOAL: (4, False),
                }
            },
            {
                "trigger": TRIGGER_ME,
                "effect": {
                    EFFECT_ATTR_CHANGE: [(Attr.DEFENSIVE, 75, 0, 0)],
                }
            },
        ]
    },
    1049: {
        "name": "静流",
        "position": POSITION_DEFEND,

        "health": 1200,
        "distance": 5,
        "attack": 70,
        "defensive": 120,
        "crit": 5,
        "tp": 0,

        "active_skills": [
            {
                "name": "普通攻击",
                "text": "对目标造成0(+1.0自身攻击力)真实伤害",
                "tp_cost": 0,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (0, Attr.ATTACK, 0, 1.0, True),
                }
            },
            {
                "name": "爱的头槌",
                "text": "为自己和目标恢复100(+1.0自身防御力)的生命值，并眩晕目标1回合",
                "tp_cost": 30,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [0],

                "effect": {
                    EFFECT_ATTR_CHANGE: [(Attr.NOW_HEALTH, 100, Attr.DEFENSIVE, 1.0)],
                    EFFECT_DIZZINESS: 1,
                }
            },
            {
                "name": "守护",
                "text": "为自己增添一个可抵御200点伤害的护盾（可触发1次），并提升40防御力",
                "tp_cost": 30,
                "trigger": TRIGGER_ME,
                "passive": [],

                "effect": {
                    EFFECT_BUFF: [(BuffType.Shield, 200, 1)],
                    EFFECT_ATTR_CHANGE: [(Attr.DEFENSIVE, 40, 0, 0), ]
                }
            },
            {
                "name": "神圣惩击",
                "text": "对目标造成其最大生命值30%的真实伤害，并为自己增添一个可抵御200点伤害的护盾(可触发1次)",
                "tp_cost": 60,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [1],

                "effect": {
                    EFFECT_HURT: (1, Attr.MAX_HEALTH, 1, 0.3, True),
                }
            },
        ],
        "passive_skills": [
            {
                "trigger": TRIGGER_ME,
                "effect": {
                    EFFECT_ATTR_CHANGE: [(Attr.NOW_HEALTH, 100, Attr.DEFENSIVE, 1.5)],
                },
            },
            {
                "trigger": TRIGGER_ME,
                "effect": {
                    EFFECT_BUFF: [(BuffType.Shield, 200, 1)],
                },
            }
        ]
    },
    1044: {
        "name": "伊莉亚",
        "position": POSITION_ATTACK,

        "health": 1280,
        "distance": 6,
        "attack": 180,
        "defensive": 40,
        "crit": 25,
        "tp": 0,

        "active_skills": [
            {
                "name": "普通攻击",
                "text": "对目标造成0(+0.8自身攻击力)真实伤害，并回复所造成伤害50%生命值",
                "tp_cost": 0,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (0, Attr.ATTACK, 0, 0.8, True),
                    EFFECT_LIFESTEAL: 0.5
                }
            },
            {
                "name": "血腥爆破",
                "text": "对目标造成120(+0.8自身攻击力)的真实伤害,并提升自身25攻击力、回复所造成伤害40%生命值,且对自身造成60(+0.6攻击力)伤害",
                "tp_cost": 25,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [0, 1],

                "effect": {
                    EFFECT_HURT: (120, Attr.ATTACK, 0, 0.8, True),
                    EFFECT_LIFESTEAL: 0.4
                }
            },
            {
                "name": "血腥之矛",
                "text": "对目标及其半径3范围内的所有玩家造成120(+0.5自身攻击力)的真实伤害,并回复所造成伤害25%生命值,且对自身造成45(+0.8攻击力)伤害",
                "tp_cost": 20,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [2],

                "effect": {
                    EFFECT_AOE: (3, False),
                    EFFECT_HURT: (120, Attr.ATTACK, 0, 0.5, True),
                    EFFECT_LIFESTEAL: 0.25
                }
            },
            {
                "name": "朱色之噬",
                "text": "对目标及其半径3范围内所有玩家造成120(+1.0自身攻击力)的真实伤害,并回复所造成伤害75%生命值",
                "tp_cost": 60,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_AOE: (3, False),
                    EFFECT_HURT: (120, Attr.ATTACK, 0, 1.0, True),
                    EFFECT_LIFESTEAL: 0.75,
                }
            }
        ],
        "passive_skills": [
            {
                "trigger": TRIGGER_ME,
                "effect": {
                    EFFECT_ATTR_CHANGE: [(Attr.ATTACK, 25, 0, 0)],
                }
            },
            {
                "trigger": TRIGGER_ME,
                "effect": {
                    EFFECT_HURT: (60, Attr.ATTACK, 0, 0.6, False),
                }
            },
            {
                "trigger": TRIGGER_ME,
                "effect": {
                    EFFECT_HURT: (45, Attr.ATTACK, 0, 0.8, False),
                }
            }
        ]
    },
    1040: {
        "name": "碧",
        "position": POSITION_SPECIAL,

        "health": 1000,
        "distance": 15,
        "attack": 100,
        "defensive": 50,
        "crit": 10,
        "tp": 10,

        "active_skills": [
            {
                "name": "普通攻击",
                "text": "对目标造成0(+1.0自身攻击力)伤害",
                "tp_cost": 10,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (0, Attr.ATTACK, 0, 1, False)
                }
            },
            {
                "name": "光合作用",
                "text": "自身每回合回复125生命值，持续3个玩家回合",
                "tp_cost": 30,
                "trigger": TRIGGER_ME,
                "passive": [0],

                "effect": {
                    EFFECT_BUFF: [(BuffType.TurnAttrHelUp, 125, 3)],
                },
            },
            {
                "name": "酸性藤曼",
                "text": "使目标每回合降低10防御力,持续4回合。并附加每回合减少60生命值的中毒效果，持续3个玩家回合",
                "tp_cost": 30,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_BUFF: [(BuffType.TurnAttrDefDown, -10, 4)],
                    EFFECT_BUFF: [(BuffType.TurnAttrHelDown, -60, 3)],
                }
            },
            {
                "name": "剧毒绽放",
                "text": "无视距离，对目标及其半径4范围内的玩家造成130(+1.0自身攻击力)的伤害，并降低目标3点攻击距离。附加每回合减少100生命值的中毒效果，持续3个玩家回合",
                "tp_cost": 60,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [0],

                "effect": {
                    EFFECT_AOE: (4, False),
                    EFFECT_HURT: (130, Attr.ATTACK, 0, 1.0, False),
                    EFFECT_BUFF: [(BuffType.TurnAttrHelDown, -100, 3)],
                    EFFECT_ATTR_CHANGE: [(Attr.DISTANCE, -3, 0, 0)],
                },
            },
        ],
        "passive_skills": [
            {
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "effect": {
                    EFFECT_IGNORE_DIST: 0,
                }
            },
        ]
    },
    1038: {
        "name": "栞",
        "position": POSITION_ATTACK,

        "health": 875,
        "distance": 12,
        "attack": 80,
        "defensive": 60,
        "crit": 5,
        "tp": 0,

        "active_skills": [
            {
                "name": "普通攻击",
                "text": "对目标造成0(+0.5自身攻击力)伤害",
                "tp_cost": 0,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (0, Attr.ATTACK, 0, 0.5, False)
                }
            },
            {
                "name": "风之箭",
                "text": "对目标造成80(+1.45自身攻击力)伤害,并自身回复40tp",
                "tp_cost": 20,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [2],

                "effect": {
                    EFFECT_HURT: (80, Attr.ATTACK, 0, 1.45, False)
                }
            },
            {
                "name": "三重箭矢",
                "text": "对除自己外所有玩家造成70(+0.8自身攻击力)伤害,并自身回复50tp",
                "tp_cost": 20,
                "trigger": TRIGGER_ALL_EXCEPT_ME,
                "passive": [0],

                "effect": {
                    EFFECT_HURT: (70, Attr.ATTACK, 0, 0.8, False)
                }
            },
            {
                "name": "附魔之箭",
                "text": "对目标造成100(+1.5自身攻击力)伤害,并提升自身100攻击力和回复50tp，并将所造成伤害的20%转为生命值。",
                "tp_cost": 100,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [0, 1],

                "effect": {
                    EFFECT_HURT: (100, Attr.ATTACK, 0, 1.5, False),
                    EFFECT_LIFESTEAL: 0.2,
                }
            }
        ],
        "passive_skills": [
            {
                "trigger": TRIGGER_ME,
                "effect": {
                    EFFECT_ATTR_CHANGE: [(Attr.NOW_TP, 50, 0, 0)]
                }
            },
            {
                "trigger": TRIGGER_ME,
                "effect": {
                    EFFECT_ATTR_CHANGE: [(Attr.ATTACK, 100, 0, 0)]
                }
            },
            {
                "trigger": TRIGGER_ME,
                "effect": {
                    EFFECT_ATTR_CHANGE: [(Attr.NOW_TP, 40, 0, 0)]
                }
            },
        ]
    },
    1036: {
        "name": "镜华",
        "position": POSITION_BURST,

        "health": 800,
        "distance": 15,
        "attack": 150,
        "defensive": 60,
        "crit": 0,
        "tp": 0,

        "active_skills": [
            {
                "name": "普通攻击",
                "text": "对目标造成0(+1.0自身攻击力)伤害",
                "tp_cost": 10,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (0, Attr.ATTACK, 0, 1, False)
                }
            },
            {
                "name": "魔法增幅",
                "text": "自身增加50点攻击力, 且下次攻击增加70%暴击概率",
                "tp_cost": 20,
                "trigger": TRIGGER_ME,
                "passive": [],

                "effect": {
                    EFFECT_ATTR_CHANGE: [(Attr.ATTACK, 50, 0, 0)],
                    EFFECT_BUFF: [(BuffType.AttackAttrCritUp, 70, 1)],
                }
            },
            {
                "name": "冰枪术",
                "text": "对目标造成20(+1.5自身攻击力)伤害",
                "tp_cost": 30,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (20, Attr.ATTACK, 0, 1.5, False),
                }
            },
            {
                "name": "宇宙苍蓝闪",
                "text": "无视距离，对目标造成70(+2.2自身攻击力)伤害，并将所造成伤害的20%转为生命值",
                "tp_cost": 60,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [0],

                "effect": {
                    EFFECT_HURT: (70, Attr.ATTACK, 0, 2.2, False),
                    EFFECT_LIFESTEAL: 0.2,
                }
            }
        ],
        "passive_skills": [
            {
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "effect": {
                    EFFECT_IGNORE_DIST: 0,
                }
            },
        ]
    },
    1034: {
        "name": "优花梨",
        "position": POSITION_DEFEND,

        "health": 1200,
        "distance": 7,
        "attack": 0,
        "defensive": 100,
        "crit": 5,
        "tp": 20,

        "active_skills": [
            {
                "name": "肉蛋葱鸡",
                "text": "无视距离，向离自己最近的目标移动5步，并对目标造成0(+1.0自身防御力)真实伤害",
                "tp_cost": 10,
                "trigger": TRIGGER_NEAR,
                "passive": [0],

                "effect": {
                    EFFECT_HURT: (0, Attr.DEFENSIVE, 0, 1, True)
                }
            },
            {
                "name": "护盾",
                "text": "为自己增加一个200点生命值的护盾（只可触发1次），并增加10点防御力",
                "tp_cost": 20,
                "trigger": TRIGGER_ME,
                "passive": [],

                "effect": {
                    EFFECT_BUFF: [(BuffType.Shield, 200, 1)],
                    EFFECT_ATTR_CHANGE: [(Attr.DEFENSIVE, 10, 0, 0)],
                }
            },
            {
                "name": "月下独酌",
                "text": "自身增加20TP, 并恢复自身防御力50%的生命值",
                "tp_cost": 20,
                "trigger": TRIGGER_ME,
                "passive": [],

                "effect": {
                    EFFECT_ATTR_CHANGE: [
                        (Attr.NOW_HEALTH, 0, Attr.DEFENSIVE, 0.50),
                        (Attr.NOW_TP, 40, 0, 0)],
                },
            },
            {
                "name": "第七天堂",
                "text": "提升全体50防御,回复全体根据自身防御50%生命值,自身额外提升30防御和100生命值",
                "tp_cost": 80,
                "trigger": TRIGGER_ALL,
                "passive": [1],

                "effect": {
                    EFFECT_ATTR_CHANGE: [
                        (Attr.NOW_HEALTH, 0, Attr.DEFENSIVE, 0.5),
                        (Attr.DEFENSIVE, 50, 0, 0)],
                },
            }
        ],
        "passive_skills": [
            {
                "trigger": TRIGGER_NEAR,
                "effect": {
                    EFFECT_MOVE_GOAL: (5, False),
                }
            },
            {
                "trigger": TRIGGER_ME,
                "effect": {
                    EFFECT_ATTR_CHANGE: [
                        (Attr.DEFENSIVE, 30, 0, 0),
                        (Attr.NOW_HEALTH, 100, 0, 0)],
                },
            }
        ]
    },
    1029: {
        "name": "望",
        "position": POSITION_DEFEND,

        "health": 1200,
        "distance": 7,
        "attack": 100,
        "defensive": 140,
        "crit": 5,
        "tp": 0,

        "active_skills": [
            {
                "name": "普通攻击",
                "text": "对目标造成0(+1.35自身攻击力)真实伤害",
                "tp_cost": 10,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (0, Attr.ATTACK, 0, 1.35, True)
                }
            },
            {
                "name": "悦音斩击",
                "text": "对目标造成30(+0.8自身攻击力)伤害并眩晕1个自我回合，且降低目标30攻击力持续2个玩家回合",
                "tp_cost": 35,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (30, Attr.ATTACK, 0, 0.8, False),
                    EFFECT_BUFF: [(BuffType.NormalAttrAtkDown, -30, 2)],
                    EFFECT_DIZZINESS: 1
                }
            },
            {
                "name": "偶像声援",
                "text": "对自身回复100(+1.0自身防御力)的生命值，对其他玩家回复50(+0.5自身防御力)的生命值",
                "tp_cost": 30,
                "trigger": TRIGGER_ALL_EXCEPT_ME,
                "passive": [0],

                "effect": {
                    EFFECT_ATTR_CHANGE: [(Attr.NOW_HEALTH, 50, Attr.DEFENSIVE, 0.5)]
                }
            },
            {
                "name": "Live On Stage!",
                "text": "为自己增加一个1000生命值的护盾（只可触发1次）并提升70点防御力，赋予全体玩家50点攻击力，且下次攻击必爆并增加50%爆伤",
                "tp_cost": 60,
                "trigger": TRIGGER_ME,
                "passive": [1],

                "effect": {
                    EFFECT_BUFF: [(BuffType.Shield, 1000, 1)],
                    EFFECT_ATTR_CHANGE: [(Attr.DEFENSIVE, 70, 0, 0)],
                }
            },
        ],
        "passive_skills": [
            {
                "trigger": TRIGGER_ME,
                "effect": {
                    EFFECT_ATTR_CHANGE: [(Attr.NOW_HEALTH, 100, Attr.DEFENSIVE, 1.0)]
                },
            },
            {
                "trigger": TRIGGER_ALL,
                "effect": {
                    EFFECT_ATTR_CHANGE: [(Attr.ATTACK, 50, 0, 0)],
                    EFFECT_BUFF: [
                        (BuffType.AttackAttrCritUp, 100, 1),
                        (BuffType.AttackAttrCritHurtUp, 0.5, 1)
                    ],
                }
            },
        ]
    },
    1028: {
        "name": "咲恋",
        "position": POSITION_ATTACK,

        "health": 1100,
        "distance": 7,
        "attack": 90,
        "defensive": 70,
        "crit": 10,
        "tp": 0,

        "active_skills": [
            {
                "name": "普通攻击",
                "text": "对目标造成0(+1.0自身攻击力)伤害",
                "tp_cost": 0,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (0, Attr.ATTACK, 0, 1, False)
                }
            },
            {
                "name": "优雅声援",
                "text": "自身恢复30TP，并提升50攻击力",
                "tp_cost": 20,
                "trigger": TRIGGER_ME,
                "passive": [],

                "effect": {
                    EFFECT_ATTR_CHANGE: [
                        (Attr.NOW_TP, 30, 0, 0),
                        (Attr.ATTACK, 50, 0, 0)
                    ],
                }
            },
            {
                "name": "烈焰斩击",
                "text": "对目标及其半径2范围内的其他玩家造成80(+1.0自身攻击力)的伤害,自身每损失1%生命值额外造成3点伤害",
                "tp_cost": 30,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_AOE: (2, False),
                    EFFECT_HURT: (80, Attr.ATTACK, 0, 1.0, False),
                    EFFECT_STAND: (1, 3),
                }
            },
            {
                "name": "凤凰之终结",
                "text": "对目标及其半径5范围内的玩家造成100(+1.2自身攻击力)的伤害,自身每损失1%生命值额外造成8点伤害，并将所造成伤害的20%转为生命值。",
                "tp_cost": 70,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_AOE: (5, False),
                    EFFECT_HURT: (100, Attr.ATTACK, 0, 1.2, False),
                    EFFECT_STAND: (1, 8),
                    EFFECT_LIFESTEAL: 0.3,
                }
            },
        ],
        "passive_skills": []
    },
    1022: {
        "name": "依里",
        "position": POSITION_BURST,

        "health": 900,
        "distance": 10,
        "attack": 120,
        "defensive": 50,
        "crit": 5,
        "tp": 0,

        "active_skills": [
            {
                "name": "普通攻击",
                "text": "对目标造成0(+1.0自身攻击力)伤害",
                "tp_cost": 10,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (0, Attr.ATTACK, 0, 1, False)
                }
            },
            {
                "name": "极限充能",
                "text": "消耗自身150HP提高70攻击力，并自身回复30TP",
                "tp_cost": 0,
                "trigger": TRIGGER_ME,
                "passive": [],

                "effect": {
                    EFFECT_ATTR_CHANGE: [
                        (Attr.ATTACK, 70, 0, 0),
                        (Attr.NOW_TP, 30, 0, 0),
                        (Attr.NOW_HEALTH, -150, 0, 0,)],
                }
            },
            {
                "name": "暗影吮吸",
                "text": "对目标及其半径3内的敌人造成60(+0.7自身攻击力)真实伤害，并将所造成伤害的30%转换为生命值",
                "tp_cost": 20,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (60, Attr.ATTACK, 0, 0.7, True),
                    EFFECT_AOE: (3, False),
                    EFFECT_LIFESTEAL: 0.30,
                }
            },
            {
                "name": "闪电之枪",
                "text": "对目标及其半径4范围内自己以外的玩家造成70(+2.0自身攻击力)真实伤害，并将所造成伤害的20%转换为生命值",
                "tp_cost": 50,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_AOE: (4, False),
                    EFFECT_HURT: (70, Attr.ATTACK, 0, 2.0, True),
                    EFFECT_LIFESTEAL: 0.2,
                }
            }
        ],
        "passive_skills": []
    },
    1020: {
        "name": "美美",
        "position": POSITION_ATTACK,

        "health": 1000,
        "distance": 5,
        "attack": 110,
        "defensive": 80,
        "crit": 5,
        "tp": 0,

        "active_skills": [
            {
                "name": "普通攻击",
                "text": "对目标造成0(+1.0自身攻击力)伤害",
                "tp_cost": 0,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (0, Attr.ATTACK, 0, 1, False)
                }
            },
            {
                "name": "蹦蹦跳跳",
                "text": "自身增加40点攻击力和40点防御力",
                "tp_cost": 20,
                "trigger": TRIGGER_ME,
                "passive": [],

                "effect": {
                    EFFECT_ATTR_CHANGE: [
                        (Attr.ATTACK, 40, 0, 0),
                        (Attr.DEFENSIVE, 40, 0, 0)],
                }
            },
            {
                "name": "崩山击",
                "text": "向目标移动3格，并对目标及其半径4范围内的所有玩家造成100(+1.5自身攻击力)伤害",
                "tp_cost": 30,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [0],

                "effect": {
                    EFFECT_HURT: (100, Attr.ATTACK, 0, 1.5, False),
                    EFFECT_AOE: (4, False)
                }
            },
            {
                "name": "兰德索尔正义",
                "text": "对目标造成120(+0.5自身攻击力)点真实伤害，目标生命值每降低1%则额外造成7点真实伤害，并将所造成伤害的30%转为生命值。",
                # 斩杀效果
                "tp_cost": 60,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (120, Attr.ATTACK, 0, 0.5, True),
                    EFFECT_ELIMINATE: (1, 7),
                    EFFECT_LIFESTEAL: 0.3,
                }
            },
        ],
        "passive_skills": [
            {
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "effect": {
                    EFFECT_MOVE_GOAL: (3, False),
                }
            }
        ]
    },
    1017: {
        "name": "香织",
        "position": POSITION_BURST,

        "health": 900,
        "distance": 5,
        "attack": 120,
        "defensive": 60,
        "crit": 15,
        "tp": 0,

        "active_skills": [
            {
                "name": "普通攻击",
                "text": "对目标造成0(+1.0自身攻击力)的伤害",
                "tp_cost": 0,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (0, Attr.ATTACK, 0, 1, False)
                }
            },
            {
                "name": "正中突破",
                "text": "对目标造成80(+1.0自身攻击力)的伤害，并降低其20点防御力",
                "tp_cost": 20,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (80, Attr.ATTACK, 0, 1.0, False),
                    EFFECT_ATTR_CHANGE: [(Attr.DEFENSIVE, -20, 0, 0)],
                },
            },
            {
                "name": "精神统一",
                "text": "每自我回合永久提升自身40点攻击,持续3回合",
                "tp_cost": 35,
                "trigger": TRIGGER_ME,
                "passive": [],

                "effect": {
                    EFFECT_BUFF: [(BuffType.TurnSelfAttrAtkUp, 40, 3)],
                }
            },
            {
                "name": "琉球犬重拳出击",
                "text": "对目标造成200(+2.0自身攻击力)真实伤害，并将所造成伤害的30%转为生命值。使用后会降低自身250攻击力持续1个自我回合",
                "tp_cost": 70,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [0],

                "effect": {
                    EFFECT_HURT: (200, Attr.ATTACK, 0, 2.0, True),
                    EFFECT_LIFESTEAL: 0.3,
                }
            }
        ],
        "passive_skills": [
            {
                "trigger": TRIGGER_ME,
                "effect": {
                    EFFECT_BUFF: [(BuffType.NormalSelfAttrAtkDown, -250, 1)],
                },
            }
        ]
    },
    1016: {
        "name": "铃奈",
        "position": POSITION_BURST,

        "health": 900,
        "distance": 12,
        "attack": 100,
        "defensive": 50,
        "crit": 15,
        "tp": 0,

        "active_skills": [
            {
                "name": "普通攻击",
                "text": "对目标造成0(+1.0自身攻击力)伤害",
                "tp_cost": 10,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (0, Attr.ATTACK, 0, 1, False)
                }
            },
            {
                "name": "魅力全开",
                "text": "每自我回合增加15%暴击率，持续全局",
                "tp_cost": 0,
                "trigger": TRIGGER_ME,
                "passive": [],

                "effect": {
                    EFFECT_BUFF: [(BuffType.TurnSelfAttrCritUp, 15, 9999)],
                }
            },
            {
                "name": "会心飞镖",
                "text": "对目标造成100(+1.25自身攻击力)伤害",
                "tp_cost": 20,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (100, Attr.ATTACK, 0, 1.25, False)
                }
            },
            {
                "name": "一箭穿心",
                "text": "对目标造成200(+2.5自身攻击力)伤害，并将所造成伤害的30%转为生命值。",
                "tp_cost": 70,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (200, Attr.ATTACK, 0, 2.5, False),
                    EFFECT_LIFESTEAL: 0.3,
                }
            },
        ],
        "passive_skills": []
    },
    1008: {
        "name": "雪",
        "position": POSITION_BURST,

        "health": 800,
        "distance": 10,
        "attack": 110,
        "defensive": 50,
        "crit": 5,
        "tp": 10,

        "active_skills": [
            {
                "name": "普通攻击",
                "text": "对目标造成0(+1.5自身最大TP)伤害",
                "tp_cost": 0,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (0, Attr.MAX_TP, 0, 1, False)
                }
            },
            {
                "name": "我那令人目眩的美貌♪",
                "text": "对目标造成50(+1.0自身攻击力)伤害，并使其致盲，下次攻击不会造成伤害",
                "tp_cost": 30,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (50, Attr.ATTACK, 0, 1, False),
                    EFFECT_BUFF: [(BuffType.Blind, 0, 1)],
                }
            },
            {
                "name": "可爱的我会为你加油的♪",
                "text": "全体回复10TP，自身额外回复20%最大TP和20TP最大值",
                "tp_cost": 30,
                "trigger": TRIGGER_ALL,
                "passive": [0],

                "effect": {
                    EFFECT_ATTR_CHANGE: [(Attr.NOW_TP, 10, 0, 0)],
                }
            },
            {
                "name": "拜倒在我的美貌之下吧！",
                "text": "自身增加50TP和50TP最大值，对自己外所有玩家造成100(+2.0自身当前TP)伤害，并降低10TP。所造成伤害的20%将转换为生命值",
                "tp_cost": 100,
                "trigger": TRIGGER_ALL_EXCEPT_ME,
                "passive": [1],

                "effect": {
                    EFFECT_HURT: (100, Attr.NOW_TP, 0, 2.0, False),
                    EFFECT_ATTR_CHANGE: [(Attr.NOW_TP, -10, 0, 0)],
                    EFFECT_LIFESTEAL: 0.2,
                }
            },
        ],
        "passive_skills": [
            {
                "trigger": TRIGGER_ME,
                "effect": {
                    EFFECT_ATTR_CHANGE: [
                        (Attr.MAX_TP, 20, 0, 0),
                        (Attr.NOW_TP, 0, Attr.MAX_TP, 0.2),
                    ],
                },
            },
            {
                "trigger": TRIGGER_ME,
                "effect": {
                    EFFECT_ATTR_CHANGE: [
                        (Attr.MAX_TP, 50, 0, 0),
                        (Attr.NOW_TP, 50, 0, 0),
                    ],
                },
            }
        ]
    },
    1007: {
        "name": "宫子",
        "position": POSITION_DEFEND,

        "health": 1200,
        "distance": 5,
        "attack": 80,
        "defensive": 200,
        "crit": 5,
        "tp": 0,

        "active_skills": [
            {
                "name": "普通攻击",
                "text": "对目标造成10(+0.25自身最大生命值)伤害",
                "tp_cost": 10,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (10, Attr.MAX_HEALTH, 0, 0.25, False)
                }
            },
            {
                "name": "我~好~恨~啊~",
                "text": "免疫下次受到的伤害，且降低自身8%最大生命值",
                "tp_cost": 20,
                "trigger": TRIGGER_ME,
                "passive": [],

                "effect": {
                    EFFECT_BUFF: [(BuffType.Ghost, 9999, 1)],  # 其实就是一个超高生命值的护盾
                    EFFECT_ATTR_CHANGE: [(Attr.MAX_HEALTH, -1, Attr.MAX_HEALTH, 0.08)],
                }
            },
            {
                "name": "点心时间到了~",
                "text": "回复50(+0.3已损失生命值)生命值",
                "tp_cost": 20,
                "trigger": TRIGGER_ME,
                "passive": [],

                "effect": {
                    EFFECT_ATTR_CHANGE: [(Attr.NOW_HEALTH, 50, Attr.COST_HEALTH, 0.3)],
                }
            },
            {
                "name": "把你变成布丁",
                "text": "对目标造成100(+0.8自身攻击力)点真实伤害，目标生命值每降低1%则额外造成5点真实伤害，且自身增加10%生命值上限",
                "tp_cost": 60,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [0],

                "effect": {
                    EFFECT_HURT: (100, Attr.ATTACK, 0, 0.8, True),
                    EFFECT_ELIMINATE: (1, 5)
                }
            },
        ],
        "passive_skills": [
            {
                "trigger": TRIGGER_ME,
                "effect": {
                    EFFECT_ATTR_CHANGE: [(Attr.MAX_HEALTH, 0, Attr.MAX_HEALTH, 0.1)],
                },
            }
        ]
    },
    1006: {
        "name": "茜里",
        "position": POSITION_ATTACK,

        "health": 1000,
        "distance": 10,
        "attack": 90,
        "defensive": 80,
        "crit": 5,
        "tp": 0,

        "active_skills": [
            {
                "name": "普通攻击",
                "text": "对目标造成0(+1.0自身攻击力)伤害",
                "tp_cost": 10,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (0, Attr.ATTACK, 0, 1, False)
                }
            },
            {
                "name": "小恶魔之吻",
                "text": "对目标造成100(+1.0自身攻击力)伤害，并将所造成伤害的50%转换为生命值",
                "tp_cost": 20,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (100, Attr.ATTACK, 0, 1.0, False),
                    EFFECT_LIFESTEAL: 0.5,
                }
            },
            {
                "name": "暗影打击",
                "text": "对目标造成100(+1.0自身攻击力)伤害，并降低目标35点护甲",
                "tp_cost": 20,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (100, Attr.ATTACK, 0, 1.0, False),
                    EFFECT_ATTR_CHANGE: [(Attr.DEFENSIVE, -35, 0, 0)],
                }
            },
            {
                "name": "甜蜜恶魔声援",
                "text": "自身增加260点攻击力，持续1回合，并继续下一回合",
                "tp_cost": 50,
                "trigger": TRIGGER_ME,
                "passive": [],

                "effect": {
                    EFFECT_BUFF: [(BuffType.NormalAttrAtkUp, 260, 1)],
                    EFFECT_LOCKTURN: 1,
                }
            }
        ],
        "passive_skills": []
    },
    1005: {
        "name": "茉莉",
        "position": POSITION_ATTACK,

        "health": 1100,
        "distance": 5,
        "attack": 90,
        "defensive": 100,
        "crit": 10,
        "tp": 0,

        "active_skills": [
            {
                "name": "普通攻击",
                "text": "对目标造成0(+1.0自身攻击力)伤害",
                "tp_cost": 0,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (0, Attr.ATTACK, 0, 1, False)
                }
            },
            {
                "name": "大杀四方",
                "text": "以自身为中心对半径5以内所有玩家造成150(+0.5自身攻击力)伤害，并将所造成伤害的75%转换为生命值",
                "tp_cost": 20,
                "trigger": TRIGGER_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (150, Attr.ATTACK, 0, 0.5, False),
                    EFFECT_LIFESTEAL: 0.75,
                    EFFECT_AOE: (5, False),
                }
            },
            {
                "name": "猛虎冲击",
                "text": "向目标移动3步，对其造成50(+1.0自身攻击力)伤害，并将其眩晕1回合",
                "tp_cost": 35,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [2],

                "effect": {
                    EFFECT_HURT: (50, Attr.ATTACK, 0, 1, False),
                    EFFECT_DIZZINESS: 1,
                }
            },
            {
                "name": "虎之英雄轰炸",
                "text": "跳到目标身边，以自身为中心对半径7以内所有玩家造成150(+1.5自身攻击力)真实伤害，并为自己增加一个200生命值的护盾（可触发1次）",
                "tp_cost": 40,
                "trigger": TRIGGER_ME,
                "passive": [0, 1],

                "effect": {
                    EFFECT_HURT: (150, Attr.ATTACK, 0, 1.5, True),
                    EFFECT_AOE: (7, False)
                }
            },
        ],
        "passive_skills": [
            {
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "effect": {
                    EFFECT_JUMP: 0,
                    EFFECT_IGNORE_DIST: 0,
                }
            },
            {
                "trigger": TRIGGER_ME,
                "effect": {
                    EFFECT_BUFF: [(BuffType.Shield, 200, 1)],
                }
            },
            {
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "effect": {
                    EFFECT_MOVE_GOAL: (3, False),
                }
            }
        ]
    },
    1004: {
        "name": "未奏希",
        "position": POSITION_ATTACK,

        "health": 1200,
        "distance": 10,
        "attack": 100,
        "defensive": 250,
        "crit": 10,
        "tp": 0,

        "active_skills": [
            {
                "name": "普通攻击",
                "text": "对目标造成0(+1.0自身攻击力)伤害",
                "tp_cost": 10,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (0, Attr.ATTACK, 0, 1, False)
                }
            },
            {
                "name": "小炸弹",
                "text": "对目标及其半径4范围内的所有玩家造成100(+1.0自身攻击力)伤害（不包括自己）",
                "tp_cost": 20,
                "trigger": TRIGGER_SELECT,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (100, Attr.ATTACK, 0, 1.0, False),
                    EFFECT_AOE: (4, False)
                }
            },
            {
                "name": "中炸弹",
                "text": "对目标及其半径8范围内的所有玩家造成150(+1.5自身攻击力)伤害（包括自己）",
                "tp_cost": 40,
                "trigger": TRIGGER_SELECT,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (150, Attr.ATTACK, 0, 1.5, False),
                    EFFECT_AOE: (8, True)
                }
            },
            {
                "name": "大炸弹",
                "text": "对场上所有玩家造成200(+2.0自身攻击力)伤害（包括自己），并赋予自己外所有人每回合降低70生命值的灼烧状态",
                "tp_cost": 70,
                "trigger": TRIGGER_ALL,
                "passive": [0],

                "effect": {
                    EFFECT_HURT: (200, Attr.ATTACK, 0, 2.0, False)
                }
            }
        ],
        "passive_skills": [
            {
                "trigger": TRIGGER_ALL_EXCEPT_ME,
                "effect": {
                    EFFECT_BUFF: [(BuffType.TurnAttrHelDown2, -70, 3)],
                }
            }
        ]
    },
    1003: {
        "name": "怜",
        "position": POSITION_ATTACK,

        "health": 900,
        "distance": 5,
        "attack": 100,
        "defensive": 70,
        "crit": 5,
        "tp": 0,

        "active_skills": [
            {
                "name": "普通攻击",
                "text": "对目标造成0(+1.0自身攻击力)真实伤害",
                "tp_cost": 0,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (0, Attr.ATTACK, 0, 1.0, True)
                }
            },
            {
                "name": "破甲突刺",
                "text": "无视距离，对离自己最近的目标造成50(+20%目标最大生命值)伤害，并降低目标50%防御力",
                "tp_cost": 20,
                "trigger": TRIGGER_NEAR,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (50, Attr.MAX_HEALTH, 1, 0.20, False),
                    EFFECT_ATTR_CHANGE: [(Attr.DEFENSIVE, -1, Attr.DEFENSIVE, 0.5)],
                }
            },
            {
                "name": "极东骑术",
                "text": "为自己增加一个250的护盾（只可触发1次），并增加15%攻击力，且继续下一回合",
                "tp_cost": 40,
                "trigger": TRIGGER_ME,
                "passive": [],

                "effect": {
                    EFFECT_BUFF: [(BuffType.Shield, 250, 1)],
                    EFFECT_ATTR_CHANGE: [(Attr.ATTACK, 0, Attr.ATTACK, 0.15)],
                    EFFECT_LOCKTURN: 1,
                }
            },
            {
                "name": "极光风暴",
                "text": "对自己以外的所有人造成135(+1.0自身攻击力)真实伤害，并展开攻击力上升、暴击率上升的领域4回合。",
                "tp_cost": 60,
                "trigger": TRIGGER_ALL_EXCEPT_ME,
                "passive": [0],

                "effect": {
                    EFFECT_HURT: (135, Attr.ATTACK, 0, 1.0, True)
                }
            }
        ],
        "passive_skills": [
            {
                "trigger": TRIGGER_ME,
                "effect": {
                    EFFECT_BUFF: [
                        (BuffType.NormalAttrAtkUp, 100, 4),
                        (BuffType.NormalAttrCritUp, 20, 4),
                    ],
                }
            },
        ]
    },
    1002: {
        "name": "优衣",
        "position": POSITION_SPECIAL,

        "health": 1000,
        "distance": 8,
        "attack": 80,
        "defensive": 60,
        "crit": 0,
        "tp": 10,

        "active_skills": [
            {
                "name": "普通攻击",
                "text": "对目标造成0(+1.0自身攻击力)伤害",
                "tp_cost": 0,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (0, Attr.ATTACK, 0, 1, False)
                }
            },
            {
                "name": "花瓣射击",
                "text": "对目标造成75(+2.0自身攻击力)伤害，并降低目标70点攻击力，持续3个自我回合，且降低其10点TP",
                "tp_cost": 20,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (75, Attr.ATTACK, 0, 2.0, False),
                    EFFECT_BUFF: [(BuffType.NormalSelfAttrAtkDown, -70, 3)],
                    EFFECT_ATTR_CHANGE: [(Attr.NOW_TP, -10, 0, 0)],
                }
            },
            {
                "name": "全体治愈",
                "text": "全体回复100生命值，自己额外回复300生命值，除自己外减少3点攻击距离",
                "tp_cost": 60,
                "trigger": TRIGGER_ALL,
                "passive": [0, 1],

                "effect": {
                    EFFECT_ATTR_CHANGE: [(Attr.NOW_HEALTH, 100, 0, 0)]
                }
            }
        ],
        "passive_skills": [
            {
                "trigger": TRIGGER_ALL_EXCEPT_ME,
                "effect": {
                    EFFECT_ATTR_CHANGE: [(Attr.DISTANCE, -3, 0, 0)],
                }
            },
            {
                "trigger": TRIGGER_ME,
                "effect": {
                    EFFECT_ATTR_CHANGE: [(Attr.NOW_HEALTH, 300, 0, 0)]
                }
            }
        ],
    },
    1001: {
        "name": "日和莉",
        "position": POSITION_BURST,

        "health": 1000,
        "distance": 5,
        "attack": 100,
        "defensive": 60,
        "crit": 10,
        "tp": 0,

        "active_skills": [
            {
                "name": "普通攻击",
                "text": "对目标造成0(+1.0自身攻击力)伤害",
                "tp_cost": 0,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (0, Attr.ATTACK, 0, 1, False)
                }
            },
            {
                "name": "勇气冲拳",
                "text": "无视距离，对离自己最近的目标造成0(+0.75自身攻击力伤害)，并将所造成伤害的30%转换为生命值，且增加自身50点攻击力和1点攻击距离",
                "tp_cost": 20,
                "trigger": TRIGGER_NEAR,
                "passive": [0],

                "effect": {
                    EFFECT_HURT: (0, Attr.ATTACK, 0, 0.75, False),
                    EFFECT_LIFESTEAL: 0.3,
                }
            },
            {
                "name": "日和莉烈焰冲击",
                "text": "对目标造成200(+2.5自身攻击力)伤害，并将造成伤害的30%转化为生命值。若目标被击倒，自身回复70点tp并继续下一回合",
                "tp_cost": 100,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (200, Attr.ATTACK, 0, 2.5, False),
                    EFFECT_LIFESTEAL: 0.3,
                    EFFECT_OUT_TP: 70,
                    EFFECT_OUT_LOCKTURN: 1
                }
            }
        ],
        "passive_skills": [
            {
                "trigger": TRIGGER_ME,
                "effect": {
                    EFFECT_ATTR_CHANGE: [
                        (Attr.ATTACK, 50, 0, 0),
                        (Attr.DISTANCE, 1, 0, 0)],
                }
            },
        ]
    },
    5101: {
        "name": "phelia",
        "position": POSITION_BURST,

        "health": 1200,
        "distance": 8,
        "attack": 100,
        "defensive": 70,
        "crit": 10,
        "tp": 0,

        "active_skills": [
            {
                "name": "攻击!",
                "text": "对目标造成0(+1.5自身攻击力)伤害,并将造成伤害的30%转化为生命值。若令目标出局则获得20tp",
                "tp_cost": 10,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (0, Attr.ATTACK, 0, 1.5, False),
                    EFFECT_LIFESTEAL: 0.3,
                    EFFECT_OUT_TP: 20,
                }
            },
            {
                "name": "躁动起来!",
                "text": "向前移动3格并触发跑道事件，强化下一次普通攻击，使其暴击率与暴击伤害提升50%与0.2倍",
                "tp_cost": 20,
                "trigger": TRIGGER_ME,
                "passive": [],

                "effect": {
                    EFFECT_MOVE: 3,
                    EFFECT_BUFF: [
                        (BuffType.AttackAttrCritUp, 50, 1),
                        (BuffType.AttackAttrCritHurtUp, 0.2, 1)
                    ],
                    EFFECT_SKILL_CHANGE: (BuffType.Imangry, [0]),
                }
            },
            {
                "name": "开溜!",
                "text": "向后移动5格并触发跑道事件，强化下一次普通攻击，使其暴击率与暴击伤害提升50%与0.2倍",
                "tp_cost": 25,
                "trigger": TRIGGER_ME,
                "passive": [],

                "effect": {
                    EFFECT_MOVE: -5,
                    EFFECT_BUFF: [
                        (BuffType.AttackAttrCritUp, 50, 1),
                        (BuffType.AttackAttrCritHurtUp, 0.2, 1)
                    ],
                    EFFECT_SKILL_CHANGE: (BuffType.Imangry, [1]),
                }
            },
            {
                "name": "我要生气了!",
                "text": "立即触发当前所处位置的跑道事件，回复20tp，攻击力增加100，本局大乱斗剩余的时间内，暴击率提升10%(每局只提升一次)，每次使用技能2或3时将获得一个额外回合",
                "tp_cost": 70,
                "trigger": TRIGGER_ME,
                "passive": [],

                "effect": {
                    EFFECT_MOVE: 0,
                    EFFECT_ATTR_CHANGE: [
                        (Attr.NOW_TP, 20, 0, 0),
                        (Attr.ATTACK, 100, 0, 0)
                    ],
                    EFFECT_BUFF: [(BuffType.Imangry, 10, 99999)],
                }
            },
        ],
        "passive_skills": [
            {
                "trigger": TRIGGER_ME,
                "effect": {
                    EFFECT_MOVE: 3,
                    EFFECT_BUFF: [
                        (BuffType.AttackAttrCritUp, 50, 1),
                        (BuffType.AttackAttrCritHurtUp, 0.2, 1)
                    ],
                    EFFECT_LOCKTURN: 1,
                }
            },
            {
                "trigger": TRIGGER_ME,
                "effect": {
                    EFFECT_MOVE: -5,
                    EFFECT_BUFF: [
                        (BuffType.AttackAttrCritUp, 50, 1),
                        (BuffType.AttackAttrCritHurtUp, 0.2, 1)
                    ],
                    EFFECT_LOCKTURN: 1,
                }
            },
        ]
    },
    5102: {
        "name": "昊京",
        "position": POSITION_SPECIAL,

        "health": 1200,
        "distance": 5,
        "attack": 50,
        "defensive": 85,
        "crit": 10,
        "tp": 0,

        "active_skills": [
            {
                "name": "喝哎！",
                "text": "在初始形态与答辩形态之间切换，普通形态具有更强的生存能力，答辩形态则擅长绳之以法，使用此技能时若tp已达到40则获得一个额外回合",
                "tp_cost": 10,
                "trigger": TRIGGER_ME,
                "passive": [],

                "effect": {
                    EFFECT_ATTR_CHANGE: [
                        (Attr.MAX_HEALTH, -200, 0, 0),
                        (Attr.ATTACK, 80, 0, 0),
                        (Attr.DEFENSIVE, -35, 0, 0)
                    ],
                    EFFECT_BUFF: [(BuffType.heai, 4, 99999)],
                    EFFECT_SKILL_CHANGE: (BuffType.heai, [0]),
                    EFFECT_TP_LOCKTURN: 30,
                }
            },
            {
                "name": "隐忍 / 强迫",
                "text": "隐忍：基于已损失生命值的12%获得防御力加成，并为自己增加一个200点生命值的护盾(只可触发一次);\n" +
                        "\t强迫：基于已损失生命值的15%获得攻击力加成",
                "tp_cost": 20,
                "trigger": TRIGGER_ME,
                "passive": [],

                "effect": {
                    EFFECT_ATTR_CHANGE: [(Attr.DEFENSIVE, 0, Attr.COST_HEALTH, 0.12)],
                    EFFECT_BUFF: [(BuffType.Shield, 200, 1)],
                    EFFECT_SKILL_CHANGE: (BuffType.heai, [1]),
                }
            },
            {
                "name": "答辩方便面 / 特种兵战斗技巧",
                "text": "答辩方便面：恢复800点生命值，并在接下来的两个回合开始时受到220点伤害\n" +
                        "\t特种兵战斗技巧：对目标造成伤害，目标每损失1%生命值，便造成15点伤害",
                "tp_cost": 30,
                "trigger": TRIGGER_ME,
                "passive": [],

                "effect": {
                    EFFECT_BUFF: [(BuffType.TurnAttrHelDown3, -220, 2)],
                    EFFECT_ATTR_CHANGE: [(Attr.NOW_HEALTH, 800, 0, 0)],
                    EFFECT_SKILL_CHANGE: (BuffType.heai, [2]),
                }
            },
            {
                "name": "任何邪恶终将绳之以法",
                "text": "初始形态下：自身防御力降低至0，并将所有防御力转化为攻击力，恢复等同于消耗防御力30%的tp\n" +
                        "\t答辩形态下：自身攻击力降低至0，并对目标造成相当于所消耗攻击力3倍的伤害并击退10格，恢复等同于消耗攻击力30%的tp",
                "tp_cost": 70,
                "trigger": TRIGGER_ME,
                "passive": [],

                "effect": {
                    EFFECT_ATTR_CHANGE: [(Attr.ATTACK, 0, Attr.DEFENSIVE, 1),
                                         (Attr.NOW_TP, 0, Attr.DEFENSIVE, 0.3),
                                         (Attr.DEFENSIVE, -1000, 0, 0)],
                    EFFECT_SKILL_CHANGE: (BuffType.heai, [3,4]),
                }
            },
        ],
        "passive_skills": [
            {
                "trigger": TRIGGER_ME,
                "effect": {
                    EFFECT_ATTR_CHANGE: [
                        (Attr.MAX_HEALTH, 200, 0, 0),
                        (Attr.ATTACK, -80, 0, 0),
                        (Attr.DEFENSIVE, 35, 0, 0)
                    ],
                    EFFECT_DEL_BUFF: [BuffType.heai],
                    EFFECT_TP_LOCKTURN: 40,
                }
            },
            {
                "trigger": TRIGGER_ME,
                "effect": {
                    EFFECT_ATTR_CHANGE: [(Attr.ATTACK, 0, Attr.COST_HEALTH, 0.15)],
                }
            },
            {
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "effect": {
                    EFFECT_HURT: (0, 0, 0, 0, False),
                    EFFECT_ELIMINATE: (1, 15)
                }
            },
            {
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "effect": {
                    EFFECT_HURT: (0, Attr.ATTACK, 0, 3, False),
                    EFFECT_HIT_BACK: 10
                }
            },
            {
                "trigger": TRIGGER_ME,
                "effect": {
                    EFFECT_ATTR_CHANGE: [(Attr.NOW_TP, 0, Attr.ATTACK, 0.3),
                                         (Attr.ATTACK, -1000, 0, 0)],
                }
            },
        ]
    },
    5103: {
        "name": "源樱",
        "position": POSITION_SPECIAL,
        "passive": PASSIVE_REBORN,
        "passive_text": "被击倒时只会暂时出局，并在3自我回合后复活，每次复活时,血量上限增加350点，防御力增加50点，获得80点攻击力与15%暴击率",

        "health": 500,
        "distance": 6,
        "attack": 80,
        "defensive": 50,
        "crit": 10,
        "tp": 0,

        "active_skills": [
            {
                "name": "普通攻击",
                "text": "对目标造成50(+1.0自身攻击力)伤害(可以攻击自己)",
                "tp_cost": 0,
                "trigger": TRIGGER_SELECT,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (50, Attr.ATTACK, 0, 1.0, False)
                }
            },
            {
                "name": "复仇",
                "text": "对目标造成150(+1.5自身攻击力)伤害，若目标为自己的'杀人凶手'，则必定暴击；若复仇成功，则复活所需的回合数缩短1",
                "tp_cost": 25,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (150, Attr.ATTACK, 0, 1.5, False),
                    EFFECT_REVENGE: 1,
                    EFFECT_KILL_REBORN: 1
                }
            },
            {
                "name": "坚强意志",
                "text": "在本局大乱斗中，复活所需的回合数缩短为2",
                "tp_cost": 50,
                "trigger": TRIGGER_ME,
                "passive": [],

                "effect": {
                    EFFECT_REBORN: 2
                }
            },
        ],
        "passive_skills": [
        ]
    },
    5104: {
        "name": "胡图图",
        "position": POSITION_SPECIAL,
        "passive": PASSIVE_HEALTHTP,
        "passive_text": "图图的技能不消耗tp，而是改为消耗等量的生命值",

        "health": 2500,
        "distance": 6,
        "attack": 0,
        "defensive": 150,
        "crit": 20,
        "tp": 0,

        "active_skills": [
            {
                "name": "普通攻击",
                "text": "对目标造成50(+1.0自身防御力)伤害，并将伤害的30%转化为生命值",
                "tp_cost": 50,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (0, Attr.DEFENSIVE, 0, 1.0, False),
                    EFFECT_LIFESTEAL: 0.3
                }
            },
            {
                "name": "翻斗花园小霸王",
                "text": "从以下六种效果中随机选择一种：恢复500点生命值；暴击率提升15%；tp值增加10点；防御力提升50点；生命值降低150点；防御力降低30点。如果已经使用过技能3，则改为随机选择两次",
                "tp_cost": 250,
                "trigger": TRIGGER_ME,
                "passive": [],

                "effect": {
                    EFFECT_RANDOM: 1,
                }
            },
            {
                "name": "俺滴图图啊！",
                "text": "(该技能需要tp值为100时才能使用)最大生命值降低1000，在本局大乱斗中，图图受到攻击时不再扣除生命值，而改为扣除伤害0.075倍的等量tp值；当tp值归0时，图图出局",
                "tp_cost": 1000,
                "trigger": TRIGGER_ME,
                "passive": [],

                "effect": {
                    EFFECT_TP_REQUEST: 100,
                    EFFECT_ATTR_CHANGE: [(Attr.MAX_HEALTH, -1000, 0, 0)],
                    EFFECT_COST_TP: 1
                }
            },
        ],
        "passive_skills": [
        ]
    },
    5105: {
        "name": "嘉然",
        "position": POSITION_SPECIAL,
        "passive": PASSIVE_SWEETIE,
        "passive_text": "嘉然拥有嘉心糖的支持(最多10个)，游戏开始时获得3个；每一个嘉心糖可以为嘉然提供150点生命值上限，30点攻击力，30点防御力，以及10%的暴击率。嘉然的嘉心糖数量与生命值上限相关，嘉然每失去150点生命值，就会失去一个嘉心糖",

        "health": 500,
        "distance": 6,
        "attack": 10,
        "defensive": 10,
        "crit": 0,
        "tp": 0,

        "active_skills": [
            {
                "name": "普通攻击",
                "text": "对目标造成0(+1.0自身攻击力)伤害，每有一名嘉心糖，此伤害提升8%；并将伤害的15%转化为生命值",
                "tp_cost": 10,
                "trigger": TRIGGER_SELECT,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (0, Attr.ATTACK, 0, 1.0, False),
                    EFFECT_LIFESTEAL: 0.15,
                    EFFECT_SWEETBUFF: 1.08,
                }
            },
            {
                "name": "开播",
                "text": "嘉然立即获得1个嘉心糖，并在接下来的2个自我回合内每回合获得2个嘉心糖",
                "tp_cost": 25,
                "trigger": TRIGGER_ME,
                "passive": [],

                "effect": {
                    EFFECT_GET_SWEETIE: 1,
                    EFFECT_BUFF:[(BuffType.Sweetie, 2, 2)]
                }
            },
            {
                "name": "顿顿解馋",
                "text": "嘉然攻击某个目标，对其造成100(+1.5自身攻击力)伤害，并使其获得猫中毒状态，持续3个自我回合(不可叠加)；在猫中毒状态下的角色每当受到攻击伤害时，嘉然都将获得3个嘉心糖并从该玩家处抢夺10点tp",
                "tp_cost": 30,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (100, Attr.ATTACK, 0, 1.5, False),
                    EFFECT_CAT_POISION: 3
                }
            },
            {
                "name": "番茄炒蛋拳！",
                "text": "嘉然用尽全身力气挥出著名的番茄炒蛋拳，对目标造成200(+1.0自身攻击力)伤害，并消耗全部的嘉心糖，每消耗1个，此伤害提升20%(嘉然的面板按消耗前结算)；如果消耗了3个或更多嘉心糖，则嘉然锁定1个回合并获得2个嘉心糖",
                "tp_cost": 75,
                "trigger": TRIGGER_ME,
                "passive": [0],

                "effect": {
                    EFFECT_SWEET_LOCKTURN: 3

                }
            },
        ],
        "passive_skills": [
            {
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "effect": {
                    EFFECT_HURT: (200, Attr.ATTACK, 0, 1.0, False),
                    EFFECT_SWEETBUFF: 1.2
                }
            }
        ]
    },
    5106: {
        "name": "程小姐",
        "position": POSITION_DEFEND,
        "passive": PASSIVE_ATTACKSPEED,
        "passive_text": "程小姐拥有独有的属性'攻击速度'，当程小姐进行攻击或反击时，每有100点攻击速度，程小姐会额外攻击一次；程小姐受到攻击伤害时会发动防御反击，造成等同于防御力100%的伤害，每进行一次反击，程小姐获得15点防御力与25点攻击速度",

        "health": 1200,
        "distance": 6,
        "attack": 0,
        "defensive": 90,
        "crit": 15,
        "tp": 0,

        "active_skills": [
            {
                "name": "你不行",
                "text": "对目标造成0(+0.7自身防御力)伤害，并增加25点防御力和攻击速度",
                "tp_cost": 15,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (0, Attr.DEFENSIVE, 0, 0.7, False),
                    EFFECT_ATTR_CHANGE: [(Attr.DEFENSIVE, 25, 0, 0),
                                         (Attr.ATTACK_SPEED, 25, 0, 0)],
                }
            },
            {
                "name": "白月光",
                "text": "增加50点防御力与50点攻击速度，持续2个自我回合",
                "tp_cost": 25,
                "trigger": TRIGGER_ME,
                "passive": [],

                "effect": {
                    EFFECT_BUFF:[(BuffType.NormalSelfAttrDefUp, 50, 2),
                                 (BuffType.NormalSelfAttrSpeedUp, 50, 2)]
                }
            },
            {
                "name": "行不行啊细狗",
                "text": "使用此技能时，攻击速度视为原来的两倍；对目标造成70(+1.0自身防御力)伤害，技能期间每攻击一次，目标防御力降低20%，下一次攻击的伤害增加20%；若将目标击倒，恢复500点生命值",
                "tp_cost": 70,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (70, Attr.DEFENSIVE, 0, 1.0, False),
                    EFFECT_DOUBLESPEED: 1,
                    EFFECT_ATTACK_BURST: 1,
                    EFFECT_HEALTH_DOWN: 500
                }
            }
        ],
        "passive_skills": [

        ]
    },
    5107: {
        "name": "刀酱",
        "position": POSITION_ATTACK,
        "passive": PASSIVE_SKIP,
        "passive_text": "刀酱每跳过一次技能发动阶段，都能获得15%的暴击率与0.3倍的暴击伤害，直到使用技能后，清空此加成；刀酱的每一个已跳过回合，都将使其丢色子时获得额外的5tp",

        "health": 1000,
        "distance": 5,
        "attack": 100,
        "defensive": 70,
        "crit": 15,
        "tp": 0,

        "active_skills": [
            {
                "name": "普通攻击",
                "text": "对目标造成0(+0.9自身攻击力)伤害，并将所造成伤害的15%转化为生命值；使用此技能前每跳过一个回合，此技能的暴击率提升10%",
                "tp_cost": 10,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (0, Attr.ATTACK, 0, 0.9, False),
                    EFFECT_LIFESTEAL: 0.15,
                    EFFECT_SKIP_CRIT: 10,
                }
            },
            {
                "name": "好果汁",
                "text": "对目标造成80(+1.5自身攻击力)伤害，并将所造成伤害的30%转化为生命值；使用此技能前若已经跳过2个或更多回合，此伤害改为真实伤害",
                "tp_cost": 30,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_HURT: (80, Attr.ATTACK, 0, 1.5, False),
                    EFFECT_LIFESTEAL: 0.3,
                    EFFECT_SKIP_TRUEDAMAGE: 2,
                }
            },
            {
                "name": "你比泰深都牛批",
                "text": "比较自身与目标已经跳过的回合数，若自身跳过回合数更低，则对目标造成100(+1.8自身攻击力)伤害；否则降低目标60%防御力",
                "tp_cost": 30,
                "trigger": TRIGGER_SELECT_EXCEPT_ME,
                "passive": [],

                "effect": {
                    EFFECT_SKIP_JUDGE: 1,
                }
            },
            {
                "name": "我...我不到啊",
                "text": "(此技能需要70tp才可以使用)攻击力提升50点，进入迷糊状态，期间可以无限次发动任意技能(此技能除外)，直到发送“跳过”为止(此回合仍然视为已跳过)；迷糊状态期间每使用一次技能，已跳过回合数-1",
                "tp_cost": 0,
                "trigger": TRIGGER_ME,
                "passive": [],

                "effect": {
                    EFFECT_TP_REQUEST: 70,
                    EFFECT_ATTR_CHANGE: [(Attr.ATTACK, 50, 0, 0)],
                    EFFECT_UNKNOWN: 1,
                }
            }
        ],
        "passive_skills": [

        ]
    },
}
