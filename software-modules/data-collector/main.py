#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
信息收集器主入口文件
Family Wealth Data Collector Main Entry Point
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from storage.initialize_professional_database import ProfessionalFinanceDatabase
from data_sources.professional_data_collector import ProfessionalDataCollector
from processors.financial_data_analyzer import FinancialDataAnalyzer

def main():
    """主函数"""
    print("📡 启动家族财富信息收集器...")
    
    # 初始化专业数据库
    database = ProfessionalFinanceDatabase('storage/family_wealth_professional.db')
    
    # 初始化数据收集器
    collector = ProfessionalDataCollector('storage/family_wealth_professional.db')
    
    # 初始化数据分析器
    analyzer = FinancialDataAnalyzer('storage/family_wealth_professional.db')
    
    print("✅ 收集器启动完成!")
    print("📊 可用功能:")
    print("  - 数据库管理: database")
    print("  - 数据采集: collector")
    print("  - 数据分析: analyzer")
    
    return {
        'database': database,
        'collector': collector,
        'analyzer': analyzer
    }

if __name__ == "__main__":
    collector_system = main()