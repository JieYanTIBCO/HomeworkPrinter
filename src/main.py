#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
作业打印系统主程序
"""

import sys
import yaml
from pathlib import Path

# 加载配置
CONFIG_PATH = Path(__file__).parent.parent / 'config' / 'settings.yaml'

def load_config():
    """加载配置文件"""
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        sys.exit(1)

def main():
    """主程序入口"""
    config = load_config()
    print("作业打印系统启动...")
    print(f"当前配置: {config}")

if __name__ == '__main__':
    main()
