from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 4200, 5000
BG = "white"
LINE = (76, 74, 165)
TEXT = (110, 110, 110)
FONT_PATH = "/System/Library/Fonts/STHeiti Medium.ttc"


class Node:
    def __init__(self, label, children=None):
        self.label = label
        self.children = children or []


tree = Node(
    "国产半导体设备与光模块投资逻辑分析",
    [
        Node(
            "长鑫存储IPO利好方向",
            [
                Node("刻蚀设备", [Node("中微公司（核心龙头）"), Node("北方华创")]),
                Node("薄膜沉积设备", [Node("北方华创"), Node("拓荆科技")]),
                Node("清洗设备", [Node("盛美上海（海外第一）")]),
                Node("涂胶显影设备", [Node("芯源微（国产渗透率<5%）"), Node("北方华创为人机床（渠道定）")]),
                Node("检测设备（空间较小）", [Node("中科飞测"), Node("精测电子")]),
            ],
        ),
        Node(
            "AI产业景气逻辑",
            [
                Node("上半场：算力（GPU/HBM/TPU）"),
                Node(
                    "下半场：连接（光互联）",
                    [
                        Node("光模块封装（不可替代）", [Node("新易盛、Coherent、AAOI等")]),
                        Node(
                            "核心瓶颈环节",
                            [
                                Node("DSP芯片（仅博通、Marvell可做）", [Node("难谓为绝对龙头"), Node("国产暂无能力")]),
                                Node("标配传递的打测企业", [Node("长电科技（半导体封测，全球布局）")]),
                            ],
                        ),
                        Node(
                            "次一级核心器件（国产机会）",
                            [
                                Node("TIA/LDD/MCU/Driver/Cdr"),
                                Node("优讯股份（科创板新上市，TIA/LDD龙头）"),
                                Node("国星技术（MCU方向）"),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        Node(
            "上游材料与器件",
            [
                Node("滤化铟（InP）衬底", [Node("云南锗业（全球主产线）", [Node("2025年产能15万片，规划2028年18万片"), Node("实际扩产或达2025年25万片、2028年50万片"), Node("华为持股战略投资（持股近30%）")])]),
                Node("其他关键器件", [Node("源杰科技（EML芯片）"), Node("长光华芯、光库科技、仕佳光子、天孚通信")]),
            ],
        ),
        Node(
            "市场与政策信号",
            [
                Node("智控岸堆稳息结构（4000亿夯实新基线）"),
                Node("天联链注入赛动件（70亿美元）"),
                Node("长鑫：会释放积极信号"),
                Node("长存物价后续跟进（方向不同：企业级SSD）"),
            ],
        ),
        Node(
            "投资原则与风险提示",
            [
                Node("不追高、不加杠杆"),
                Node("拉开左侧恐慌与退潮心态"),
                Node("关注基本面与长期贴现关系"),
                Node("业绩优先于故事与题材"),
            ],
        ),
        Node(
            "其他关联机会",
            [
                Node("PCB/CCL材料", [Node("胜宏科技（业绩预告6月下旬）"), Node("生益科技、金安国纪、中材叶石")]),
                Node("ABF载板 vs 玻璃基板", [Node("ABF载板具真实产业链支撑")]),
                Node("沸基业（天银）", [Node("获英伟达关注"), Node("Q1接10亿元AI云订单"), Node("网络基础设施增长6%")]),
                Node("企业级SSD", [Node("大普微（新锐，正常标的）"), Node("佰维存（稳健联动）"), Node("阳光电源（跟踪SSD政策）")]),
            ],
        ),
    ],
)


def load_font(size):
    return ImageFont.truetype(FONT_PATH, size)


def count_leaves(node):
    if not node.children:
        return 1
    return sum(count_leaves(child) for child in node.children)


def layout(node, top, bottom, depth=0, x_step=520, pos=None):
    if pos is None:
        pos = {}
    x = 520 + depth * x_step
    y = (top + bottom) / 2
    pos[id(node)] = (x, y)
    if not node.children:
        return pos
    total = sum(count_leaves(child) for child in node.children)
    current = top
    for child in node.children:
        span = (bottom - top) * count_leaves(child) / total
        layout(child, current, current + span, depth + 1, x_step, pos)
        current += span
    return pos


def bezier_points(p0, p1, p2, p3, steps=28):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        mt = 1 - t
        x = mt ** 3 * p0[0] + 3 * mt ** 2 * t * p1[0] + 3 * mt * t ** 2 * p2[0] + t ** 3 * p3[0]
        y = mt ** 3 * p0[1] + 3 * mt ** 2 * t * p1[1] + 3 * mt * t ** 2 * p2[1] + t ** 3 * p3[1]
        pts.append((x, y))
    return pts


def draw_curve(draw, start, end, width=6):
    dx = (end[0] - start[0]) * 0.45
    points = bezier_points(
        start,
        (start[0] + dx, start[1]),
        (end[0] - dx, end[1]),
        end,
    )
    draw.line(points, fill=LINE, width=width)


def text_size(draw, text, font):
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def draw_node(draw, node, pos, parent=None):
    x, y = pos[id(node)]
    font = load_font(28 if node.children else 26)
    if parent is not None:
        px, py = pos[id(parent)]
        draw_curve(draw, (px + 24, py), (x - 24, y))
        draw.ellipse((x - 10, y - 10, x + 10, y + 10), outline=LINE, width=4, fill=BG)
    w, h = text_size(draw, node.label, font)
    draw.text((x + 22, y - h - 6), node.label, font=font, fill=TEXT)
    if not node.children and parent is not None:
        line_y = y
        draw.line((x + 18, line_y, min(x + 18 + max(260, w + 40), WIDTH - 60), line_y), fill=LINE, width=4)
    for child in node.children:
        draw_node(draw, child, pos, node)


img = Image.new("RGB", (WIDTH, HEIGHT), BG)
draw = ImageDraw.Draw(img)

positions = layout(tree, 300, HEIGHT - 300, x_step=540)

root_x, root_y = positions[id(tree)]
draw.ellipse((root_x - 12, root_y - 12, root_x + 12, root_y + 12), outline=LINE, width=5, fill=BG)
root_font = load_font(30)
root_w, root_h = text_size(draw, tree.label, root_font)
draw.line((80, root_y, root_x - 16, root_y), fill=LINE, width=5)
draw.text((90, root_y - root_h - 8), tree.label, font=root_font, fill=TEXT)

for child in tree.children:
    draw_node(draw, child, positions, tree)

out = "/Users/dds/data/ai/work/image-fix-output/mindmap-redrawn.png"
img.save(out)
print(out)
