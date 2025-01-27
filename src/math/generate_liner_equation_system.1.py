import logging
import random
import math
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
from datetime import datetime
from reportlab.pdfgen import canvas
from pathlib import Path
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from setlogging.logger import get_logger

logger = get_logger(log_level=logging.INFO)


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
    """计算包含动态方程数量的布局参数"""
    page_width, page_height = letter
    layout = {
        "margin": 15 * mm,
        "column_gap": 10 * mm,
        "base_y": page_height - 25 * mm,  # 顶部边距
        "line_height": 7 * mm,
        "footer_y": 15 * mm,
        "num_columns": params["num_columns"],
    }

    # 计算列宽
    layout["column_width"] = (
        page_width
        - 2 * layout["margin"]
        - (layout["num_columns"] - 1) * layout["column_gap"]
    ) / layout["num_columns"]

    # 计算每列最大方程数量
    available_height = layout["base_y"] - layout["footer_y"]
    equation_height = 2 * layout["line_height"]  # 每个方程占2行高度
    layout["equations_per_column"] = int(available_height // equation_height)

    return layout


def draw_equation(c, x, y, eq_num, equations, line_height):
    """绘制带大括号的方程组（优化版）"""
    # 设置编号
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x, y + 2 * mm, f"{eq_num}.")

    # 大括号定位参数
    brace_x = x + 8 * mm
    eq_x = brace_x + 5 * mm

    # 绘制大括号
    c.setFont("DejaVu", 14)
    c.drawString(brace_x, y, "⎧")
    c.drawString(brace_x, y - 0.5 * line_height, "⎨")
    c.drawString(brace_x, y - line_height, "⎩")

    # 绘制方程组
    c.setFont("DejaVu", 12)
    c.drawString(eq_x, y, equations[0])
    c.drawString(eq_x, y - line_height, equations[1])

    return y - 2 * line_height  # 返回下一个方程组的起始Y坐标


def create_pdf(filename, num_columns=3, equations_per_column=5, page_num=1):
    """生成PDF主函数"""
    # 注册字体
    try:
        pdfmetrics.registerFont(TTFont("DejaVu", "DejaVuSans.ttf"))
    except:
        print("Error: DejaVuSans.ttf font file not found")
        return

    # 计算布局参数
    params = {"num_columns": num_columns}
    layout = calculate_layout(params)

    # 预生成所有方程
    total_equations = num_columns * equations_per_column * page_num
    all_equations = []
    while len(all_equations) < total_equations:
        eq, sol = generate_valid_equation_system()
        all_equations.append((eq, sol))

    # 创建PDF
    c = canvas.Canvas(filename, pagesize=letter)

    for page in range(page_num):
        # 当前页的方程数据
        start_idx = page * num_columns * equations_per_column
        end_idx = start_idx + num_columns * equations_per_column
        page_data = all_equations[start_idx:end_idx]

        logger.debug(
            f"Drawing page {page+1}, start_idx: {start_idx}, end_idx: {end_idx},num_columns: {num_columns}, equations_per_column: {equations_per_column}"
        )
        # 初始化列位置
        x_positions = [
            layout["margin"] + i * (layout["column_width"] + layout["column_gap"])
            for i in range(num_columns)
        ]
        column_y = [layout["base_y"]] * num_columns

        # 存储本页答案
        solutions = []

        # 按列绘制方程
        for col in range(num_columns):
            x = x_positions[col]
            y = column_y[col]

            # 获取本列实际需要打印的方程组
            col_start = col * equations_per_column
            col_end = (col + 1) * equations_per_column
            col_data = page_data[col_start:col_end]
            actual_count = len(col_data)

            if actual_count == 0:
                continue

            # 计算留白参数
            total_available_space = y - layout["footer_y"] - 10 * mm  # 可用垂直空间
            equation_height = 2 * layout["line_height"]  # 每个方程组固定高度
            total_equations_height = actual_count * equation_height  # 方程组总高度
            remaining_space = total_available_space - total_equations_height

            # 计算间隔数量（每个方程组下方都有留白）
            spacing_count = actual_count
            spacing_height = remaining_space / spacing_count if spacing_count > 0 else 0

            # 绘制本列方程组
            for idx in range(actual_count):
                logger.debug(
                    f"Drawing equation {idx+1} in column , spacing height: {spacing_height}, col_start: {col_start}, col_end: {col_end}"
                )
                eq_index = col_start + idx
                equations, solution = col_data[idx]
                eq_num = start_idx + eq_index + 1
                solutions.append(solution)

                # 绘制方程组
                new_y = draw_equation(c, x, y, eq_num, equations, layout["line_height"])

                # 添加动态计算的留白
                y = new_y - spacing_height

                # 强制底部边界检查
                if y < layout["footer_y"] + 15 * mm:
                    break

        # 绘制页脚答案
        c.setFont("Helvetica", 6)
        footer_text = "  ".join(
            [f"{i+1}.({s[0]},{s[1]})" for i, s in enumerate(solutions)]
        )
        c.drawString(layout["margin"], layout["footer_y"], footer_text)

        c.showPage()

    c.save()


if __name__ == "__main__":
    #

    pdf_filename = f"equations_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    # print pdf location
    logger.info(
        f"Generating PDF file with linear equations and solutions at {Path.cwd()}/{pdf_filename}"
    )
    create_pdf(pdf_filename, num_columns=3, equations_per_column=4, page_num=5)
