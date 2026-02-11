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

# 添加数据中台模块路径
sys.path.append(str(Path(__file__).parent.parent / 'data-hub'))

# 临时修复导入问题
sys.path.append(os.path.join(os.path.dirname(__file__), 'analysis-engine'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'dashboard'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

# 导入数据中台适配器
from utils.data_hub_adapter import create_sandbox_data_adapter, create_legacy_adapter

# 导入原有组件（逐步迁移）
try:
    from database_accessor import DatabaseAccessor
    from lightweight_data_generator import DataGenerator
    from sandbox_observer import SandboxObserver
except ImportError as e:
    print(f"⚠️  部分原有组件导入失败: {e}")
    DatabaseAccessor = None
    DataGenerator = None
    SandboxObserver = None

def main():
    """主函数"""
    print("🚀 启动家族财富沙盘系统...")
    
    # 初始化数据中台适配器（新架构）
    data_hub_adapter = create_sandbox_data_adapter()
    legacy_adapter = create_legacy_adapter()
    
    # 初始化原有组件（逐步淘汰）
    components = {}
    
    if DatabaseAccessor:
        try:
            db_accessor = DatabaseAccessor('storage/sandbox_data.db')
            components['db'] = db_accessor
        except Exception as e:
            print(f"⚠️  数据库访问器初始化失败: {e}")
    
    if DataGenerator:
        try:
            data_generator = DataGenerator()
            components['generator'] = data_generator
        except Exception as e:
            print(f"⚠️  数据生成器初始化失败: {e}")
    
    if SandboxObserver:
        try:
            observer = SandboxObserver()
            components['observer'] = observer
        except Exception as e:
            print(f"⚠️  观察器初始化失败: {e}")
    
    # 系统健康检查
    health_status = data_hub_adapter.health_check()
    
    print("✅ 系统启动完成!")
    print(f"📊 数据中台状态: {health_status['status']}")
    print("🔧 可用功能:")
    print("  - 新数据中台适配器: data_hub_adapter")
    print("  - 遗留接口适配器: legacy_adapter")
    
    if components:
        print("  - 原有组件（逐步迁移中）:")
        for name in components.keys():
            print(f"    - {name}")
    
    return {
        'data_hub_adapter': data_hub_adapter,
        'legacy_adapter': legacy_adapter,
        'components': components,
        'health_status': health_status
    }

if __name__ == "__main__":
    system = main()