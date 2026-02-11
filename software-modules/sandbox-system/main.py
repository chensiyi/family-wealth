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

# 导入数据中台适配器
from utils.data_hub_adapter import create_sandbox_data_adapter, create_legacy_adapter

def main():
    """主函数"""
    print("🚀 启动家族财富沙盘系统...")
    
    # 初始化数据中台适配器（现代架构）
    data_hub_adapter = create_sandbox_data_adapter()
    legacy_adapter = create_legacy_adapter()
    
    # 系统健康检查
    health_status = data_hub_adapter.health_check()
    
    print("✅ 系统启动完成!")
    print(f"📊 数据中台状态: {health_status['status']}")
    print("🔧 可用功能:")
    print("  - 数据中台适配器: data_hub_adapter")
    print("  - 兼容接口适配器: legacy_adapter")
    
    return {
        'data_hub_adapter': data_hub_adapter,
        'legacy_adapter': legacy_adapter,
        'health_status': health_status
    }

if __name__ == "__main__":
    system = main()