#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强数据源测试脚本
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../data-hub/data-sources/enhanced'))

from news_collector import NewsCollector
from financial_analyzer import FinancialAnalyzer

def test_news_collector():
    """测试新闻收集器"""
    print("=== 测试新闻收集器 ===")
    
    collector = NewsCollector()
    print(f"支持的行业: {list(collector.supported_sectors.keys())}")
    print(f"支持的地区: {list(collector.regions.keys())}")
    
    # 测试科技行业新闻收集
    tech_news = collector.collect_sector_news('technology', 'us', 7)
    print(f"收集到 {len(tech_news)} 条美国科技新闻")
    
    if tech_news:
        print("最新3条新闻:")
        for i, news in enumerate(tech_news[:3]):
            print(f"{i+1}. [{news['publish_date'][:10]}] {news['title']}")
            print(f"   来源: {news['source']}, 影响力: {news['impact_score']}")
    
    # 测试行业摘要
    summary = collector.get_sector_summary('energy', 'global', 30)
    print(f"\n能源行业摘要:")
    print(f"新闻总数: {summary['news_count']}")
    print(f"情绪分布: {summary['sentiment_distribution']}")
    print(f"热门关键词: {list(summary['top_keywords'].keys())[:5]}")
    
    return True

def test_financial_analyzer():
    """测试金融分析器"""
    print("\n=== 测试金融分析器 ===")
    
    analyzer = FinancialAnalyzer()
    print(f"支持的筛选标准: {list(analyzer.screening_criteria.keys())}")
    
    # 测试股票筛选
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
        }
    ]
    
    # 价值筛选
    value_stocks = analyzer.screen_stocks(sample_stocks, 'value')
    print(f"\n价值型股票筛选结果 ({len(value_stocks)}只):")
    for stock in value_stocks:
        print(f"{stock['symbol']} - 得分: {stock['screening_score']:.2f}")
    
    # 成长筛选
    growth_stocks = analyzer.screen_stocks(sample_stocks, 'growth')
    print(f"\n成长型股票筛选结果 ({len(growth_stocks)}只):")
    for stock in growth_stocks:
        print(f"{stock['symbol']} - 得分: {stock['screening_score']:.2f}")
    
    # 质量筛选
    quality_stocks = analyzer.screen_stocks(sample_stocks, 'quality')
    print(f"\n质量型股票筛选结果 ({len(quality_stocks)}只):")
    for stock in quality_stocks:
        print(f"{stock['symbol']} - 得分: {stock['screening_score']:.2f}")
    
    # 测试技术指标计算
    price_data = [
        {'date': '2024-02-10', 'open': 850.0, 'high': 880.0, 'low': 845.0, 'close': 875.28, 'volume': 52000000},
        {'date': '2024-02-09', 'open': 840.0, 'high': 855.0, 'low': 835.0, 'close': 850.0, 'volume': 48000000},
        {'date': '2024-02-08', 'open': 830.0, 'high': 845.0, 'low': 825.0, 'close': 840.0, 'volume': 51000000},
        # 添加更多数据点以满足技术指标计算需求
        {'date': '2024-02-07', 'open': 825.0, 'high': 835.0, 'low': 820.0, 'close': 830.0, 'volume': 49000000},
        {'date': '2024-02-06', 'open': 820.0, 'high': 830.0, 'low': 815.0, 'close': 825.0, 'volume': 47000000},
        {'date': '2024-02-05', 'open': 815.0, 'high': 825.0, 'low': 810.0, 'close': 820.0, 'volume': 46000000},
        {'date': '2024-02-04', 'open': 810.0, 'high': 820.0, 'low': 805.0, 'close': 815.0, 'volume': 45000000},
        {'date': '2024-02-03', 'open': 805.0, 'high': 815.0, 'low': 800.0, 'close': 810.0, 'volume': 44000000},
        {'date': '2024-02-02', 'open': 800.0, 'high': 810.0, 'low': 795.0, 'close': 805.0, 'volume': 43000000},
        {'date': '2024-02-01', 'open': 795.0, 'high': 805.0, 'low': 790.0, 'close': 800.0, 'volume': 42000000},
        {'date': '2024-01-31', 'open': 790.0, 'high': 800.0, 'low': 785.0, 'close': 795.0, 'volume': 41000000},
        {'date': '2024-01-30', 'open': 785.0, 'high': 795.0, 'low': 780.0, 'close': 790.0, 'volume': 40000000},
        {'date': '2024-01-29', 'open': 780.0, 'high': 790.0, 'low': 775.0, 'close': 785.0, 'volume': 39000000},
        {'date': '2024-01-28', 'open': 775.0, 'high': 785.0, 'low': 770.0, 'close': 780.0, 'volume': 38000000},
        {'date': '2024-01-27', 'open': 770.0, 'high': 780.0, 'low': 765.0, 'close': 775.0, 'volume': 37000000},
        {'date': '2024-01-26', 'open': 765.0, 'high': 775.0, 'low': 760.0, 'close': 770.0, 'volume': 36000000},
        {'date': '2024-01-25', 'open': 760.0, 'high': 770.0, 'low': 755.0, 'close': 765.0, 'volume': 35000000},
        {'date': '2024-01-24', 'open': 755.0, 'high': 765.0, 'low': 750.0, 'close': 760.0, 'volume': 34000000},
        {'date': '2024-01-23', 'open': 750.0, 'high': 760.0, 'low': 745.0, 'close': 755.0, 'volume': 33000000},
        {'date': '2024-01-22', 'open': 745.0, 'high': 755.0, 'low': 740.0, 'close': 750.0, 'volume': 32000000},
    ]
    
    tech_indicators = analyzer.calculate_technical_indicators(price_data)
    print(f"\n技术指标计算结果:")
    print(f"5日均线: ${tech_indicators['ma_5']:.2f}")
    print(f"20日均线: ${tech_indicators['ma_20']:.2f}")
    print(f"RSI(14): {tech_indicators['rsi_14']:.2f}")
    print(f"MACD: {tech_indicators['macd']:.4f}")
    print(f"布林带上轨: ${tech_indicators['bb_upper']:.2f}")
    print(f"布林带中轨: ${tech_indicators['bb_middle']:.2f}")
    print(f"布林带下轨: ${tech_indicators['bb_lower']:.2f}")
    
    # 投资评级
    stock_data = sample_stocks[0]
    rating = analyzer.generate_investment_rating(stock_data, tech_indicators)
    print(f"\n投资评级:")
    print(f"综合评级: {rating['overall_rating']}")
    print(f"价值评级: {rating['value_rating']}")
    print(f"技术评级: {rating['technical_rating']}")
    
    return True

def main():
    """主测试函数"""
    print("🚀 启动增强数据源综合测试...\n")
    
    tests = [
        ("新闻收集器", test_news_collector),
        ("金融分析器", test_financial_analyzer)
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
            import traceback
            traceback.print_exc()
    
    print(f"\n🏁 测试完成: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！增强数据源模块运行正常")
    else:
        print("⚠️  部分测试失败，请检查模块实现")

if __name__ == "__main__":
    main()