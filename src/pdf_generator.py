#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF生成模块
"""

from fpdf import FPDF
from typing import List, Tuple
from pathlib import Path


class PDFGenerator(FPDF):
    """PDF生成器"""

    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self.set_margins(20, 20, 20)
        self.set_auto_page_break(True, margin=20)
        self.add_page()

    def add_equations(self, equations: List[Tuple[str, str]]):
        """添加方程组到PDF"""
        # 设置字体
        self.set_font("Arial", "", 12)

        # 计算列宽
        col_width = (self.w - 2 * self.l_margin) / self.config["num_columns"]

        # 添加方程组
        for i, (equation, solution) in enumerate(equations):
            # 计算当前列
            col = i % self.config["num_columns"]
            x = self.l_margin + col * col_width

            # 计算当前行
            row = i // self.config["num_columns"]
            y = self.t_margin + row * 30

            # 添加方程组编号
            self.set_xy(x, y)
            self.cell(10, 10, f"{i+1}.", 0, 0)

            # 添加方程组
            self.set_xy(x + 10, y)
            self.multi_cell(col_width - 10, 10, equation, 0, "L")

            # 添加解
            self.set_font("Arial", "", 8)
            self.set_xy(x + 10, y + 15)
            self.cell(col_width - 10, 10, f"解：{solution}", 0, 0)
            self.set_font("Arial", "", 12)
