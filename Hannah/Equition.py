import random
import math

# 预生成高斯分布权重
_x_values = list(range(-50, 51))
_gaussian_sigma = 12
_gaussian_weights = [math.exp(-x**2/(2*_gaussian_sigma**2)) for x in _x_values]


def generate_valid_equation():
    """
    生成格式规范的一元一次方程，满足以下条件：
    1. 方程解x为整数(-30 ≤ x ≤ 30), 且服从高斯分布, 即x=0的概率最大
    2. 系数a ∈ [-20, 20]且a ≠ 0,且a=1时不显示,a=-1时显示为-x,且服从高斯分布
    3. 常数项b, c ∈ [-100, 100]
    4. 方程始终包含变量项
    5. 自动优化显示格式,不能出现--或者+-等情况
    6. 常量项分别在等式的左右两边
    7. 计算量不超过+-120
    """
    def weighted_random_x():
        """使用高斯分布生成服从概率分布的x值"""
        return random.choices(_x_values, weights=_gaussian_weights, k=1)[0]

    def format_term(value, is_variable=False):
        """格式化单项式"""
        if is_variable:
            if value == 1:
                return "x"
            if value == -1:
                return "-x"
            return f"{value}x"

        if value < 0:
            return f"- {abs(value)}"
        return f"+ {value}"

    # 生成有效参数组合
    while True:
        x = weighted_random_x()
        a = random.randint(-20, 20)
        if a == 0:
            continue

        b = random.randint(-100, 100)
        c = a * x + b

        if -120 <= c <= 120:
            break

    # 随机选择方程结构（移除会导致常量项同侧的结构）
    structures = [
        ("left_var", "right_const"),    # ax + b = c
        ("left_var", "right_const_rev"),  # b + ax = c
        ("right_var", "left_const"),    # c = ax + b
        ("neg_var", "right_const")      # -ax + c = b
    ]
    structure = random.choice(structures)

    # 构建方程两边
    left, right = [], []
    var_term = format_term(a, is_variable=True)
    const_term = format_term(b)

    if structure[0] == "left_var":
        left.append(var_term)
        if b != 0:
            left.append(const_term)
        right.append(str(c))
    elif structure[0] == "right_var":
        left.append(str(c))
        right.append(var_term)
        if b != 0:
            right.append(const_term)
    elif structure[0] == "neg_var":
        left.append(f"-{var_term.lstrip('-')}")
        left.append(f"+ {c}")
        right.append(str(b))

    # 格式清理优化
    equation = f"{' '.join(left)} = {' '.join(right)}"
    equation = equation.replace("+ -", "- ")
    equation = equation.replace("- -", "+ ")
    equation = equation.replace("= +", "= ")
    equation = equation.replace(" 1x", " x")
    equation = equation.replace("=  ", "= ")

    return equation


# 打印配置保持不变
if __name__ == "__main__":
    COLUMN_WIDTH = 25
    COLUMNS = 4
    ROWS = 10
    LINE_SPACING = 5

    for _ in range(ROWS):
        row = [f"{generate_valid_equation(): <{COLUMN_WIDTH}
                  }" for _ in range(COLUMNS)]
        print("    ".join(row))
        if LINE_SPACING > 0:
            print("\n" * (LINE_SPACING - 1), end="")
