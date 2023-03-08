<!--
 * @Author: Genisys
 * @Date: 2023-02-01 14:34:03
 * @LastEditTime: 2023-02-01 14:34:03
 * @LastEditors: Please set LastEditors
 * @Description: 模块简述
 * @FilePath: \pcr_scrimmage\README.md
-->
# pcr大乱斗
由[一个hoshino_bot插件](https://github.com/eggggi/pcr_scrimmage)修改而来的zhenxun_bot版本小游戏插件。

## 安装
首先请clone本仓库。
1. 插件本体：将仓库根目录下的 pcr_scrimmage 这个文件夹放入bot的插件文件夹中即可
2. 资源文件：由于我比较懒选择开摆，因此没有做自动下载，需要手动放置。将仓库根目录下 resources 文件夹下的 pcr_scrimmage 文件夹放入zhenxun_bot的图片资源目录下(默认为resources/image)

## 测试服
为了方便开发测试，同时不影响正常版本游玩，因此支持测试服与正式服共存。测试服使用不同的指令触发，详情请看代码。<br>
安装：将 pcr_scrimmage_debug 这个文件夹丢入插件文件夹，可与原版共存。<br>
**注：同一个群内，正式服不可与测试服一起游玩。**

## 更新日志
#### 1.8（2023/3/8）
- 新内容：
1. 源樱增强：增强其复活后的生存能力，减少复活频率并防止后期被反复秒杀；
2. 新角色：胡图图、嘉然，技能风格各异，均为特殊型角色；
- 优化与bug修复：
1. 大量bug修复；
2. 部分逻辑优化。
#### 1.7（2023/3/1）
- 新内容:
1. 被动技能系统加入，且之后可能会对部分老角色进行重做并加入被动技能；
2. 新角色源樱，此角色拥有被击倒后复活的被动技能。
- 优化与bug修复:
1. 从此版本开始正式服与测试服的熟练度数据实时同步；
2. 修复昊京吃白象方便面时只吃答辩而不回血的问题；
3. 调整了部分角色的技能效果。

#### 1.6 (2023/2/25)
- 新内容：
1. 角色定位细分：所有角色都会被分为“防御”“输出”“爆发”“特殊”四种定位中的一种，在选择角色和“大乱斗角色”命令都会显示
2. 定位熟练度：当使用某个定位的角色进行游戏时，依据战绩将能够获得该定位的熟练度。熟练度分为“新手”“上手”“熟练”“高手”“大师”“已经无敌了！”五种。高熟练度能为局内属性带来加成。
发送“查看熟练度”可查看自己的熟练度信息。
- 优化与bug修复：
1. 修复防御力为1000或更高时只能获得55%伤害减免的问题（现在可获得57%）
2. 修复管理员和群主不能强制结束游戏
3. 从此版本开始，禁止两个玩家选择相同的角色
