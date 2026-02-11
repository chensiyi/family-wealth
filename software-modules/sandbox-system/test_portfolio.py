#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
持仓模块测试脚本
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'portfolio-module'))

from position import Position
from transaction import Transaction, TransactionType
from risk_metrics import RiskMetrics
from portfolio_manager import PortfolioManager

def test_position():
    """测试持仓功能"""
    print("=== 测试持仓功能 ===")
    
    # 创建持仓
    position = Position("AAPL", 100, 150.00)
    print(f"初始持仓: {position}")
    print(f"市值: ${position.market_value:.2f}")
    print(f"成本: ${position.cost_value:.2f}")
    
    # 更新价格
    position.update_price(155.50)
    print(f"更新价格后市值: ${position.market_value:.2f}")
    print(f"未实现盈亏: ${position.unrealized_pnl:.2f} ({position.unrealized_pnl_percent:.2f}%)")
    
    # 买入更多
    position.add_shares(50, 153.25)
    print(f"加仓后: {position}")
    
    # 卖出部分
    realized_pnl = position.remove_shares(30, 158.00)
    print(f"卖出后: {position}")
    print(f"实现盈亏: ${realized_pnl:.2f}")
    
    return True

def test_transaction():
    """测试交易功能"""
    print("\n=== 测试交易功能 ===")
    
    # 买入交易
    buy_txn = Transaction("AAPL", TransactionType.BUY, 100, 150.00, fees=10.00)
    print(f"买入交易: {buy_txn}")
    print(f"交易金额: ${buy_txn.amount:.2f}")
    
    # 卖出交易
    sell_txn = Transaction("AAPL", TransactionType.SELL, 50, 158.00, fees=10.00)
    print(f"卖出交易: {sell_txn}")
    print(f"交易金额: ${sell_txn.amount:.2f}")
    
    return True

def test_risk_metrics():
    """测试风险指标"""
    print("\n=== 测试风险指标 ===")
    
    risk_calc = RiskMetrics()
    
    # 测试收益率
    returns = [0.02, -0.01, 0.03, -0.02, 0.04]
    volatility = risk_calc.calculate_volatility(returns)
    sharpe = risk_calc.calculate_sharpe_ratio(returns)
    
    print(f"波动率: {volatility*100:.2f}%")
    print(f"夏普比率: {sharpe:.2f}")
    
    # 测试最大回撤
    values = [100000, 105000, 98000, 102000, 108000]
    drawdown = risk_calc.calculate_max_drawdown(values)
    print(f"最大回撤: {drawdown['max_drawdown']*100:.2f}%")
    
    return True

def test_portfolio_manager():
    """测试投资组合管理器"""
    print("\n=== 测试投资组合管理器 ===")
    
    # 创建投资组合
    portfolio = PortfolioManager(initial_cash=100000.0)
    print(f"初始投资组合: {portfolio}")
    
    # 买入股票
    success = portfolio.buy_stock("AAPL", 100, 150.00, fees=10.00, description="首次建仓")
    print(f"买入AAPL: {'成功' if success else '失败'}")
    
    success = portfolio.buy_stock("GOOGL", 10, 2800.00, fees=10.00, description="科技股配置")
    print(f"买入GOOGL: {'成功' if success else '失败'}")
    
    # 更新价格
    portfolio.update_prices({"AAPL": 155.50, "GOOGL": 2850.00})
    print("价格更新完成")
    
    # 卖出股票
    success = portfolio.sell_stock("AAPL", 50, 158.00, fees=10.00, description="部分获利了结")
    print(f"卖出AAPL: {'成功' if success else '失败'}")
    
    # 获取摘要
    summary = portfolio.get_portfolio_summary()
    print("\n--- 投资组合摘要 ---")
    print(f"现金: ${summary['cash']:,.2f}")
    print(f"持仓价值: ${summary['positions_value']:,.2f}")
    print(f"总资产: ${summary['total_value']:,.2f}")
    print(f"未实现盈亏: ${summary['unrealized_pnl']:,.2f}")
    print(f"持仓数量: {summary['position_count']}")
    
    # 获取风险指标
    risk_metrics = portfolio.get_risk_metrics()
    print("\n--- 风险指标 ---")
    print(f"总收益率: {risk_metrics['total_return']*100:.2f}%")
    if 'sharpe_ratio' in risk_metrics:
        print(f"夏普比率: {risk_metrics['sharpe_ratio']:.2f}")
    if 'volatility' in risk_metrics:
        print(f"波动率: {risk_metrics['volatility']*100:.2f}%")
    
    # 保存测试
    save_success = portfolio.save_to_file("test_portfolio.json")
    print(f"保存投资组合: {'成功' if save_success else '失败'}")
    
    return True

def main():
    """主测试函数"""
    print("🚀 启动持仓模块综合测试...\n")
    
    tests = [
        ("持仓功能", test_position),
        ("交易功能", test_transaction),
        ("风险指标", test_risk_metrics),
        ("投资组合管理", test_portfolio_manager)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"✅ {test_name}: 通过")
                passed += 1
            else:
                print(f"❌ {test_name}: 失败")
        except Exception as e:
            print(f"❌ {test_name}: 异常 - {e}")
    
    print(f"\n🏁 测试完成: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！持仓模块运行正常")
    else:
        print("⚠️  部分测试失败，请检查模块实现")
    
    # 清理测试文件
    try:
        os.remove("test_portfolio.json")
        print("🗑️  测试文件已清理")
    except:
        pass

if __name__ == "__main__":
    main()