#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
沙盘系统主入口文件
Family Wealth Sandbox System Main Entry Point
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from analysis_engine.database_accessor import DatabaseAccessor
from dashboard.lightweight_data_generator import DataGenerator
from utils.sandbox_observer import SandboxObserver

def main():
    """主函数"""
    print("🚀 启动家族财富沙盘系统...")
    
    # 初始化数据库访问器
    db_accessor = DatabaseAccessor('storage/sandbox_data.db')
    
    # 初始化数据生成器
    data_generator = DataGenerator()
    
    # 初始化观察器
    observer = SandboxObserver()
    
    print("✅ 系统启动完成!")
    print("📊 可用功能:")
    print("  - 数据库访问: db_accessor")
    print("  - 数据生成: data_generator")
    print("  - 系统监控: observer")
    
    return {
        'db': db_accessor,
        'generator': data_generator,
        'observer': observer
    }

if __name__ == "__main__":
    system = main()