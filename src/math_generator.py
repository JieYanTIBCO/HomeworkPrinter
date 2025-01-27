#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数学作业生成模块
"""

import random
from typing import List, Tuple

class MathGenerator:
    """数学作业生成器"""
    
    def __init__(self, config: dict):
        self.config = config
        self.equation_count = 0
        
    def generate_equation(self) -> Tuple[str, str]:
        """生成一个方程组及其解"""
        # 生成两个随机系数
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        c = random.randint(1, 10)
        d = random.randint(1, 10)
        
        # 生成方程组
        equation1 = f"{a}x + {b}y = {a + b}"
        equation2 = f"{c}x + {d}y = {c + d}"
        
        # 计算解
        x = 1
        y = 1
        
        # 返回方程组和解
        return (
            f"\\begin{{cases}}\n"
            f"  {equation1} \\\\\n"
            f"  {equation2}\n"
            f"\\end{{cases}}",
            f"(x={x}, y={y})"
        )
        
    def generate_page(self) -> List[Tuple[str, str]]:
        """生成一页方程组"""
        equations = []
        for _ in range(self.config['equations_per_page']):
            equations.append(self.generate_equation())
        return equations
