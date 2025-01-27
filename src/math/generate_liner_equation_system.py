import random
import math
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph


def generate_valid_equation_system():
    """
    生成格式规范的二元一次方程组，满足以下条件：
    方程格式：
        a1x + b1y = c1
        a2x + b2y = c2

    条件：
    1. 方程解x, y为整数(-20 ≤ x ≤ 20), 且服从高斯分布, 即x，y=0的概率最大。
    2. 系数a1, a2, b1, b2 ∈ [-20, 20]且均为非零整数。
    3. 常数项c1, c2满足：
        a1x + b1y <= 120
        a2x + b2y <= 120
    4. 系数a1, b1, a2, b2服从高斯分布，且满足：
        a = 1时不显示，a = -1时显示为-x或-y。
    5. 方程始终包含变量项，且自动优化显示格式，避免出现--或者+-等情况。
    6. 常量项c1, c2分别位于等式的右侧。
    """

    def weighted_random():
        values = list(range(-20, 21))
        mean = 0
        stddev = 7
        weights = [math.exp(-((x - mean) ** 2) / (2 * stddev**2)) for x in values]
        return random.choices(values, weights=weights, k=1)[0]

    def format_term(value, variable):
        if value == 0:
            return ""
        if value == 1:
            return variable
        if value == -1:
            return f"-{variable}"
        return f"{value}{variable}"

    while True:
        x = weighted_random()
        y = weighted_random()

        a1 = weighted_random()
        b1 = weighted_random()
        a2 = weighted_random()
        b2 = weighted_random()

        if a1 == 0 or b1 == 0 or a2 == 0 or b2 == 0:
            continue

        c1 = a1 * x + b1 * y
        c2 = a2 * x + b2 * y

        if abs(c1) > 120 or abs(c2) > 120:
            continue

        break

    equations = [
        f"{format_term(a1, 'x')} + {format_term(b1, 'y')} = {c1}",
        f"{format_term(a2, 'x')} + {format_term(b2, 'y')} = {c2}",
    ]

    for i in range(len(equations)):
        equations[i] = equations[i].replace("+ -", "- ")
        equations[i] = equations[i].replace("- -", "+ ")
        equations[i] = equations[i].replace(" 1x", " x")
        equations[i] = equations[i].replace(" 1y", " y")

    return equations, (x, y)


def calculate_layout(params):
    """计算页面布局参数"""
    page_width, page_height = letter
    return {
        "margin": 15 * mm,
        "column_gap": 10 * mm,
        "base_y": page_height - 25 * mm,  # 调整顶部边距
        "line_height": 7 * mm,
        "footer_y": 15 * mm,
        "column_width": (
            page_width
            - 2 * params["margin"]
            - (params["num_columns"] - 1) * params["column_gap"]
        )
        / params["num_columns"],
    }


def draw_equation(c, x, y, eq_num, equations, line_height):
    """绘制带大括号的方程组"""
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x, y, f"{eq_num}.")

    # 设置大括号位置
    brace_x = x + 8 * mm
    eq_x = brace_x + 5 * mm

    # 绘制大括号
    c.setFont("DejaVu", 14)
    c.drawString(brace_x, y, "⎧")
    c.drawString(brace_x, y - 0.5 * line_height, "⎨")
    c.drawString(brace_x, y - line_height, "⎩")

    # 绘制方程
    c.setFont("DejaVu", 12)
    c.drawString(eq_x, y, equations[0])
    c.drawString(eq_x, y - 1 * line_height, equations[1])

    return y - 3.5 * line_height  # 返回下一个方程组的y坐标


def create_pdf(filename, num_columns=3, equations_per_column=10, page_num=1):
    """生成PDF文件"""
    # 预生成所有方程组
    total_equations = num_columns * equations_per_column * page_num
    all_equations = []
    while len(all_equations) < total_equations:
        eq, sol = generate_valid_equation_system()
        all_equations.append((eq, sol))

    # 注册字体
    try:
        pdfmetrics.registerFont(TTFont("DejaVu", "DejaVuSans.ttf"))
    except:
        print("Error: DejaVuSans.ttf font file not found")
        return

    # 创建画布
    c = canvas.Canvas(filename, pagesize=letter)
    params = {
        "num_columns": num_columns,
        "equations_per_column": equations_per_column,
        "margin": 15 * mm,
        "column_gap": 10 * mm,
    }
    layout = calculate_layout(params)

    for page in range(page_num):
        # 当前页的方程组
        start_idx = page * num_columns * equations_per_column
        end_idx = start_idx + num_columns * equations_per_column
        page_equations = all_equations[start_idx:end_idx]

        # 绘制页眉
        c.setFont("Helvetica", 8)
        c.drawRightString(
            letter[0] - layout["margin"],
            letter[1] - 15 * mm,
            f"Page {page+1}/{page_num}",
        )

        # 初始化列位置
        x_positions = [
            layout["margin"] + i * (layout["column_width"] + layout["column_gap"])
            for i in range(num_columns)
        ]
        y_positions = [layout["base_y"]] * num_columns

        solutions = []
        for col in range(num_columns):
            x = x_positions[col]
            y = y_positions[col]
            for idx in range(equations_per_column):
                eq_index = col * equations_per_column + idx
                if eq_index >= len(page_equations):
                    break

                eq_num = start_idx + col * equations_per_column + idx + 1
                equations, solution = page_equations[eq_index]
                solutions.append(solution)

                # 绘制方程组
                new_y = draw_equation(c, x, y, eq_num, equations, layout["line_height"])
                if new_y < layout["footer_y"] + 30 * mm:  # 预留页脚空间
                    break
                y = new_y

        # 绘制页脚答案
        c.setFont("Helvetica", 6)
        footer_text = "  ".join(
            [f"{i+1}.({s[0]},{s[1]})" for i, s in enumerate(solutions)]
        )
        c.drawString(layout["margin"], layout["footer_y"], footer_text)

        c.showPage()

    c.save()


if __name__ == "__main__":
    pdf_filename = f"equations_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    create_pdf(
        pdf_filename,
        num_columns=3,
        equations_per_column=3,
        page_num=2,
    )
