from PIL import Image, ImageDraw
from PIL import ImageFont

# 设置方格的大小（像素）
grid_size = 40

# 设置白边的宽度（像素）
margin = 100

# 创建一个新的图片对象，模式为 RGB，背景色为白色，宽度和高度增加了白边的宽度
img = Image.new("RGB", (grid_size * 15 + margin * 2, grid_size * 15 + margin * 2), "white")

# 创建一个绘图对象
draw = ImageDraw.Draw(img)

# 绘制水平方向的线条，颜色为黑色，在绘制时加上白边的宽度
for y in range(margin, grid_size * 15 + margin + 1, grid_size):
    draw.line((margin, y, grid_size * 15 + margin, y), fill="black")

# 绘制垂直方向的线条，颜色为黑色，在绘制时加上白边的宽度
for x in range(margin, grid_size * 15 + margin + 1, grid_size):
    draw.line((x, margin, x, grid_size * 15 + margin), fill="black")



def show_status(player, hp, tp, side):
    # 设置文字的字体和大小
    font = ImageFont.truetype("fonts/msyh.ttf", 20)
    # 设置数值的字体和大小
    value_font = ImageFont.truetype("fonts/msyh.ttf", 13)
    # 设置文字和进度条的颜色
    text_color = "black"
    hp_color = "red"
    tp_color = "blue"
    # 设置进度条的长度和高度
    bar_length = 60
    bar_height = 10
    # 设置进度条的最大值
    max_hp = 100
    max_tp = 50
    # 根据玩家的编号和显示的位置，计算出文字和进度条的坐标
    if side == "left":
        # 如果显示在左边，就将文字和进度条靠近左边缘，并减去一个偏移量
        text_x = margin + 10 - grid_size * 2.5
        bar_x = margin + 10 - grid_size * 2.5
    elif side == "right":
        # 如果显示在右边，就将文字和进度条靠近右边缘
        text_x = grid_size * 15 + margin + 10
        bar_x = grid_size * 15 + margin + 10
    # 根据玩家的编号，计算出文字和进度条的垂直位置，使其居中对齐
    text_y = margin + (grid_size * 10 - font.getsize("Player 1")[1] * 4 - bar_height * 8) / 2 + (player - 1) * (font.getsize("Player 1")[1] * 2 + bar_height * 2)
    bar_y = text_y + font.getsize("Player 1")[1] + 5
    # 绘制玩家的编号
    draw.text((text_x, text_y), f"{player}", fill=text_color, font=font)
    # 绘制血量的背景框
    draw.rectangle((bar_x, bar_y, bar_x + bar_length - 1, bar_y + bar_height - 1), outline=text_color)
    # 绘制血量的进度条，根据血量的百分比计算长度
    hp_length = int(bar_length * hp / max_hp)
    draw.rectangle((bar_x, bar_y, bar_x + hp_length - 1, bar_y + bar_height - 1), fill=hp_color)
    # 绘制血量的数值，根据进度条的位置和长度计算坐标，并设置一个小的间隔和偏移量
    hp_text = f"{hp}"
    hp_text_x = bar_x + bar_length + 5
    hp_text_y = bar_y + (bar_height - value_font.getsize(hp_text)[1]) / 2
    draw.text((hp_text_x, hp_text_y), hp_text, fill=text_color, font=value_font)
    # 绘制 tp 值的背景框
    draw.rectangle((bar_x, bar_y + bar_height + 5, bar_x + bar_length - 1, bar_y + bar_height * 2 + 4), outline=text_color)
    # 绘制 tp 值的进度条，根据 tp 值的百分比计算长度
    tp_length = int(bar_length * tp / max_tp)
    draw.rectangle((bar_x, bar_y + bar_height + 5, bar_x + tp_length - 1, bar_y + bar_height * 2 + 4), fill=tp_color)
    # 绘制 tp 值的数值，根据进度条的位置和长度计算坐标，并设置一个小的间隔和偏移量
    tp_text = f"{tp}"
    tp_text_x = bar_x + bar_length + 5
    tp_text_y = bar_y + bar_height + 5 + (bar_height - value_font.getsize(tp_text)[1]) / 2
    draw.text((tp_text_x, tp_text_y), tp_text, fill=text_color, font=value_font)
show_status(1,80,30,"right")
show_status(2,80,30,"left")
# 保存图片到当前目录，格式为 PNG
img.save("grid.png")
