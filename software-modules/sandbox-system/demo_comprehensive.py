#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
家族财富管理系统综合演示
Family Wealth Management System Comprehensive Demo
"""

import sys
import os

# 添加模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'portfolio-module'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../data-hub/data-sources/enhanced'))

from portfolio_manager import PortfolioManager
from news_collector import NewsCollector
from financial_analyzer import FinancialAnalyzer

def demo_portfolio_management():
    """演示投资组合管理功能"""
    print("=" * 60)
    print("🎯 投资组合管理演示")
    print("=" * 60)
    
    # 创建投资组合
    portfolio = PortfolioManager(initial_cash=1000000.0)
    print(f"💼 初始投资组合: {portfolio}")
    
    # 模拟交易
    print("\n📈 执行交易操作:")
    transactions = [
        ("NVDA", 100, 850.00, "AI芯片龙头建仓"),
        ("JNJ", 200, 150.00, "防御性医疗股配置"),
        ("MSFT", 150, 380.00, "软件巨头投资"),
        ("TSLA", 50, 220.00, "电动车概念布局")
    ]
    
    for symbol, qty, price, desc in transactions:
        success = portfolio.buy_stock(symbol, qty, price, fees=10.00, description=desc)
        if success:
            print(f"   ✅ 买入 {symbol}: {qty}股 @ ${price:.2f} - {desc}")
        else:
            print(f"   ❌ 买入 {symbol} 失败")
    
    # 更新价格
    print("\n📊 更新市场价格:")
    price_updates = {
        "NVDA": 875.28,
        "JNJ": 152.40,
        "MSFT": 395.50,
        "TSLA": 235.80
    }
    portfolio.update_prices(price_updates)
    for symbol, price in price_updates.items():
        print(f"   📈 {symbol}: ${price:.2f}")
    
    # 查看投资组合状态
    summary = portfolio.get_portfolio_summary()
    print(f"\n💰 投资组合摘要:")
    print(f"   现金余额: ${summary['cash']:,.2f}")
    print(f"   持仓价值: ${summary['positions_value']:,.2f}")
    print(f"   总资产: ${summary['total_value']:,.2f}")
    print(f"   未实现盈亏: ${summary['unrealized_pnl']:,.2f}")
    print(f"   持仓数量: {summary['position_count']}只股票")
    
    # 风险分析
    risk_metrics = portfolio.get_risk_metrics()
    print(f"\n🛡️ 风险指标:")
    print(f"   总收益率: {risk_metrics['total_return']*100:.2f}%")
    if 'sharpe_ratio' in risk_metrics:
        print(f"   夏普比率: {risk_metrics['sharpe_ratio']:.2f}")
    if 'volatility' in risk_metrics:
        print(f"   波动率: {risk_metrics['volatility']*100:.2f}%")
    if 'max_drawdown' in risk_metrics:
        print(f"   最大回撤: {risk_metrics['max_drawdown']['max_drawdown']*100:.2f}%")

def demo_news_collection():
    """演示新闻收集功能"""
    print("\n" + "=" * 60)
    print("📰 全球行业新闻收集演示")
    print("=" * 60)
    
    collector = NewsCollector()
    
    # 收集不同行业的新闻
    sectors_to_check = ['technology', 'energy', 'finance']
    regions_to_check = ['us', 'cn', 'global']
    
    for sector in sectors_to_check:
        print(f"\n🔍 {collector._get_sector_chinese(sector)}行业新闻:")
        for region in regions_to_check[:2]:  # 只显示前两个地区
            news = collector.collect_sector_news(sector, region, 3)
            if news:
                print(f"   🌍 {collector.regions.get(region, region)}地区 ({len(news)}条):")
                for item in news[:2]:  # 只显示前2条
                    print(f"     • [{item['publish_date'][:10]}] {item['title']}")
                    print(f"       来源: {item['source']}, 影响力: {item['impact_score']:.2f}")
            else:
                print(f"   🌍 {collector.regions.get(region, region)}地区: 暂无新闻")

def demo_financial_analysis():
    """演示金融分析功能"""
    print("\n" + "=" * 60)
    print("📊 金融数据分析演示")
    print("=" * 60)
    
    analyzer = FinancialAnalyzer()
    
    # 模拟股票数据
    sample_stocks = [
        {
            'symbol': 'NVDA',
            'company': '英伟达',
            'current_price': 875.28,
            'pe_ratio': 65.2,
            'pb_ratio': 25.8,
            'dividend_yield': 0.02,
            'revenue_growth': 120.5,
            'earnings_growth': 145.3,
            'debt_equity_ratio': 0.25,
            'current_ratio': 8.2,
            'roa': 28.5,
            'roe': 52.1
        },
        {
            'symbol': 'JNJ',
            'company': '强生',
            'current_price': 152.40,
            'pe_ratio': 24.8,
            'pb_ratio': 3.2,
            'dividend_yield': 2.8,
            'revenue_growth': 3.2,
            'earnings_growth': 2.1,
            'debt_equity_ratio': 0.45,
            'current_ratio': 1.8,
            'roa': 12.3,
            'roe': 24.7
        },
        {
            'symbol': 'MSFT',
            'company': '微软',
            'current_price': 395.50,
            'pe_ratio': 32.5,
            'pb_ratio': 12.8,
            'dividend_yield': 0.8,
            'revenue_growth': 18.3,
            'earnings_growth': 22.1,
            'debt_equity_ratio': 0.65,
            'current_ratio': 2.5,
            'roa': 18.7,
            'roe': 35.2
        }
    ]
    
    # 多维度筛选
    screening_types = ['value', 'growth', 'quality']
    screening_names = {'value': '价值投资', 'growth': '成长投资', 'quality': '质量投资'}
    
    for stype in screening_types:
        screened = analyzer.screen_stocks(sample_stocks, stype)
        print(f"\n🎯 {screening_names[stype]}筛选结果:")
        for stock in screened:
            print(f"   📈 {stock['symbol']} ({stock['company']}) - 得分: {stock['screening_score']:.2f}")
            print(f"      当前价格: ${stock['current_price']:.2f}")
    
    # 技术指标计算示例
    print(f"\n📈 技术分析示例 (NVDA):")
    price_data = [
        {'date': '2024-02-10', 'open': 850.0, 'high': 880.0, 'low': 845.0, 'close': 875.28, 'volume': 52000000},
        {'date': '2024-02-09', 'open': 840.0, 'high': 855.0, 'low': 835.0, 'close': 850.0, 'volume': 48000000},
        # ... 更多数据点
    ] + [{'date': f'2024-02-{i:02d}', 'open': 800+i, 'high': 810+i, 'low': 790+i, 'close': 800+i, 'volume': 40000000-i*100000} for i in range(8, 0, -1)]
    
    tech_indicators = analyzer.calculate_technical_indicators(price_data)
    print(f"   5日均线: ${tech_indicators['ma_5']:.2f}")
    print(f"   RSI(14): {tech_indicators['rsi_14']:.2f}")
    print(f"   MACD: {tech_indicators['macd']:.4f}")
    print(f"   布林带宽度: {tech_indicators['bb_width']:.4f}")

def main():
    """主演示函数"""
    print("🚀 家族财富管理系统综合功能演示")
    print("Welcome to Family Wealth Management System Demo")
    print()
    
    try:
        demo_portfolio_management()
        demo_news_collection()
        demo_financial_analysis()
        
        print("\n" + "=" * 60)
        print("🎉 演示完成！所有功能模块运行正常")
        print("=" * 60)
        print("📋 系统功能总结:")
        print("   ✅ 投资组合管理 - 完整的股票交易模拟")
        print("   ✅ 风险指标计算 - 夏普比率、最大回撤等")
        print("   ✅ 全球新闻收集 - 7大行业×5大地区覆盖")
        print("   ✅ 金融数据分析 - 价值、成长、质量三维度筛选")
        print("   ✅ 技术指标计算 - RSI、MACD、布林带等")
        print()
        print("💡 系统已准备好为您提供专业的财富管理支持！")
        
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()