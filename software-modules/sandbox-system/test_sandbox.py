#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
沙盘系统功能测试脚本
用于验证核心组件的基本功能
"""

import sys
import os
from pathlib import Path

# 添加必要的路径
current_dir = Path(__file__).parent
sys.path.extend([
    str(current_dir / 'analysis-engine'),
    str(current_dir / 'dashboard'),
    str(current_dir / 'utils')
])

def test_data_generation():
    """测试数据生成功能"""
    print("🧪 测试数据生成功能...")
    try:
        from lightweight_data_generator import generate_lightweight_data
        data = generate_lightweight_data()
        print(f"✅ 数据生成成功!")
        print(f"   - 利率数据点: {len(data['interest_rates'])}")
        print(f"   - 税率数据点: {len(data['tax_rates'])}")
        print(f"   - 投资组合数据点: {len(data['portfolio_holdings'])}")
        return True
    except Exception as e:
        print(f"❌ 数据生成测试失败: {e}")
        return False

def test_sandbox_observer():
    """测试沙盘观察器功能"""
    print("\n🧪 测试沙盘观察器功能...")
    try:
        from sandbox_observer import SandboxObserver
        # 使用相对路径连接到数据收集器的数据库
        db_path = '../data-collector/storage/family_wealth_professional.db'
        observer = SandboxObserver(db_path)
        overview = observer.get_ecosystem_overview()
        print(f"✅ 观察器初始化成功!")
        print(f"   - 参与者总数: {overview['overview']['total_participants']}")
        print(f"   - 历史事件数: {overview['overview']['total_events']}")
        return True
    except Exception as e:
        print(f"❌ 观察器测试失败: {e}")
        return False

def test_simple_dashboard():
    """测试简化仪表板功能"""
    print("\n🧪 测试简化仪表板功能...")
    try:
        # 直接读取已有的数据文件
        import json
        dashboard_file = current_dir / 'dashboard' / 'financial_analysis_data.json'
        if dashboard_file.exists():
            with open(dashboard_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ 仪表板数据加载成功!")
            print(f"   - 数据点数量: {len(data.get('interest_rates', []))}")
            return True
        else:
            print("❌ 仪表板数据文件不存在")
            return False
    except Exception as e:
        print(f"❌ 仪表板测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始沙盘系统功能测试\n")
    
    results = []
    
    # 运行各项测试
    results.append(("数据生成", test_data_generation()))
    results.append(("沙盘观察", test_sandbox_observer()))
    results.append(("仪表板显示", test_simple_dashboard()))
    
    # 输出测试总结
    print("\n" + "="*50)
    print("📊 测试结果总结:")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:12}: {status}")
        if result:
            passed += 1
    
    print(f"\n总体结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有核心功能测试通过！")
        return True
    else:
        print("⚠️  部分功能需要修复")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)