import random
import math
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
from datetime import datetime
from . import pdf_generator


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
        """使用高斯分布生成服从概率分布的整数值"""
        values = list(range(-20, 21))
        mean = 0
        stddev = 7  # 标准差，越小集中度越高
        weights = [math.exp(-((x - mean) ** 2) / (2 * stddev**2)) for x in values]
        return random.choices(values, weights=weights, k=1)[0]

    def format_term(value, variable):
        """格式化单项式"""
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

    # 构建方程格式
    equations = [
        f"{{ {format_term(a1, 'x')} + {format_term(b1, 'y')} = {c1} }}",
        f"{{ {format_term(a2, 'x')} + {format_term(b2, 'y')} = {c2} }}",
    ]

    # 格式清理优化
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
        "base_y": page_height - 20 * mm,
        "line_height": 7 * mm,
        "footer_y": 15 * mm,
        "equations_per_page": params["num_columns"] * params["equations_per_column"],
        "column_width": (
            page_width
            - 2 * params["margin"]
            - (params["num_columns"] - 1) * params["column_gap"]
        )
        / params["num_columns"],
    }


def draw_equation(c, x, y, eq_num, equations, line_height):
    """绘制带编号的方程组"""
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x, y, f"{eq_num}.")
    c.setFont("Helvetica", 12)

    # 绘制方程组
    for i, eq in enumerate(equations):
        c.drawString(x + 8 * mm, y - i * line_height, eq)

    return y - (len(equations) + 1) * line_height  # 题目间间隔


def print_page(c, params, layout, equations, page_num, total_pages):
    """打印单个页面"""
    page_width, page_height = letter
    solutions = []

    # 初始化坐标
    x_positions = [
        layout["margin"] + i * (layout["column_width"] + layout["column_gap"])
        for i in range(params["num_columns"])
    ]
    y_positions = [layout["base_y"]] * params["num_columns"]

    # 绘制页眉
    c.setFont("Helvetica", 8)
    c.drawRightString(
        page_width - layout["margin"],
        page_height - 12 * mm,
        f"Page {page_num}/{total_pages}",
    )

    # 绘制方程组
    for col in range(params["num_columns"]):
        x = x_positions[col]
        y = y_positions[col]

        for idx in range(params["equations_per_column"]):
            eq_num = (
                (page_num - 1) * layout["equations_per_page"]
                + col * params["equations_per_column"]
                + idx
                + 1
            )

            # 检查是否超出方程组总数
            if eq_num - 1 >= len(equations):
                break

            eq_data = equations[eq_num - 1]
            equations_obj, solution = eq_data
            solutions.append(solution)

            # 绘制方程组
            y = draw_equation(
                c,
                x,
                y,
                eq_num,
                equations_obj,
                layout["line_height"],
            )

    # 绘制页脚解答
    c.setFont("Helvetica", 6)
    footer_text = "  ".join([f"{i+1}.({s[0]},{s[1]})" for i, s in enumerate(solutions)])
    c.drawString(layout["margin"], layout["footer_y"], footer_text)


def create_pdf(filename, num_columns=3, equations_per_column=10, page_num=1):
    """生成PDF文件"""
    # 预生成所有方程组
    total_equations = num_columns * equations_per_column * page_num
    all_equations = []
    all_solutions = []

    while len(all_equations) < total_equations:
        eq, sol = generate_valid_equation_system()
        all_equations.append(eq)
        all_solutions.append(sol)

    # 使用PDFGenerator生成PDF
    pdf = PDFGenerator(filename, num_columns, equations_per_column)
    pdf.generate_pdf(all_equations, all_solutions)


if __name__ == "__main__":
    # 生成方程组
    # pdf文件名，每列题目数量，总页数
    # 文件名带时间戳
    pdf_filename = f"./equations_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"

    create_pdf(
        pdf_filename,
        num_columns=3,
        equations_per_column=5,  # 每列题目数量
        page_num=3,  # 总页数
    )
