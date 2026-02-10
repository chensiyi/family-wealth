#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
轻量级金融数据生成器
专为快速测试和演示设计
"""

import json
import random
from datetime import datetime, timedelta
import math

def generate_lightweight_data():
    """生成轻量级金融数据用于测试"""
    
    # 时间范围：最近4年
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2024, 12, 31)
    days_count = (end_date - start_date).days
    
    print("🚀 生成轻量级测试数据...")
    
    # 1. 利率数据
    interest_rates = []
    base_rate = 0.25  # 2020年初的低利率
    
    for i in range(days_count):
        date = start_date + timedelta(days=i)
        
        # 疫情初期急速降息，然后缓慢加息
        if date.year == 2020:
            rate = max(0.1, base_rate - 0.15 * (i/365))
        elif date.year == 2021:
            rate = 0.1 + 0.2 * (i/365)
        elif date.year == 2022:
            rate = 0.25 + 1.0 * (i/365)
        elif date.year == 2023:
            rate = 1.5 + 1.0 * (i/365)
        else:  # 2024
            rate = 2.5 + 0.5 * math.sin(i * 0.01)
        
        # 添加随机波动
        rate += random.normalvariate(0, 0.05)
        rate = max(0.0, min(5.0, rate))
        
        interest_rates.append({
            'date': date.strftime('%Y-%m-%d'),
            'rate': round(rate, 3)
        })
    
    # 2. 税收数据
    tax_rates = []
    corporate_tax = 21.0  # 2017年后的企业税率
    
    for i in range(days_count):
        date = start_date + timedelta(days=i)
        
        # 添加小幅波动
        corp_tax = corporate_tax + random.normalvariate(0, 0.5)
        cg_tax = 20.0 + random.normalvariate(0, 0.3)
        
        tax_rates.append({
            'date': date.strftime('%Y-%m-%d'),
            'corporate_tax': round(max(15, min(30, corp_tax)), 2),
            'capital_gains_tax': round(max(10, min(25, cg_tax)), 2)
        })
    
    # 3. 投资组合数据
    portfolio_data = []
    equity_pct = 60.0
    bond_pct = 30.0
    cash_pct = 10.0
    portfolio_value = 1000000
    
    major_events = {
        '2020-03-15': {'equity_drop': -25, 'cash_increase': 10},  # 疫情初期
        '2020-11-01': {'equity_recovery': 15, 'bond_decrease': 5},  # 疫苗消息
        '2022-01-15': {'equity_volatility': -10, 'commodity_increase': 5}  # 通胀担忧
    }
    
    for i in range(days_count):
        date = start_date + timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        
        # 处理重大事件
        if date_str in major_events:
            event = major_events[date_str]
            if 'equity_drop' in event:
                equity_pct += event['equity_drop']
                cash_pct -= event['equity_drop']
            if 'equity_recovery' in event:
                equity_pct += event['equity_recovery']
                bond_pct -= event['equity_recovery'] * 0.5
                cash_pct -= event['equity_recovery'] * 0.5
            if 'cash_increase' in event:
                cash_pct += event['cash_increase']
                equity_pct -= event['cash_increase'] * 0.7
                bond_pct -= event['cash_increase'] * 0.3
        
        # 日常调整
        market_mood = math.sin(2 * math.pi * i / 200)  # 短期市场情绪
        if market_mood > 0:
            equity_pct += 0.05
            cash_pct -= 0.05
        else:
            equity_pct -= 0.03
            cash_pct += 0.03
        
        # 添加随机扰动
        noise = random.normalvariate(0, 0.5)
        equity_pct += noise
        bond_pct -= noise * 0.3
        cash_pct -= noise * 0.7
        
        # 确保总和为100%
        total = equity_pct + bond_pct + cash_pct
        equity_pct = (equity_pct / total) * 100
        bond_pct = (bond_pct / total) * 100
        cash_pct = (cash_pct / total) * 100
        
        # 计算组合价值变化
        daily_return = (random.normalvariate(0.0003, 0.01) * equity_pct/100 + 
                       random.normalvariate(0.0001, 0.003) * bond_pct/100 +
                       0.00005 * cash_pct/100)
        portfolio_value *= (1 + daily_return)
        
        portfolio_data.append({
            'date': date_str,
            'equity_percentage': round(equity_pct, 2),
            'bond_percentage': round(bond_pct, 2),
            'cash_percentage': round(cash_pct, 2),
            'total_value': round(portfolio_value, 2)
        })
    
    # 4. 通胀数据
    inflation_data = []
    base_inflation = 2.0
    
    for i in range(days_count):
        date = start_date + timedelta(days=i)
        
        # 疫情初期通缩，2021-2022高通胀，之后回落
        if date.year == 2020:
            inflation = -0.5 + 1.0 * (i/365)
        elif date.year in [2021, 2022]:
            inflation = 5.0 - 2.0 * ((i-365*1)/730) if date.year == 2021 else 3.0 - 1.0 * ((i-365*2)/365)
        else:
            inflation = 2.5 + 0.5 * math.sin(i * 0.02)
        
        # 添加噪声
        inflation += random.normalvariate(0, 0.3)
        inflation = max(-1.0, min(10.0, inflation))
        
        inflation_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'inflation_rate': round(inflation, 2)
        })
    
    # 5. 危机分析数据
    crisis_analysis = {
        "2020年疫情危机": {
            "duration_days": 274,
            "start_value": 3.0,
            "end_value": 0.1,
            "absolute_change": -2.9,
            "percentage_change": -96.67,
            "volatility": 68.7
        },
        "2022年通胀冲击": {
            "duration_days": 180,
            "start_value": 0.25,
            "end_value": 3.0,
            "absolute_change": 2.75,
            "percentage_change": 1100.0,
            "volatility": 45.2
        }
    }
    
    # 6. 绩效指标
    performance_metrics = {
        "total_return": round(((portfolio_value / 1000000) - 1) * 100, 2),
        "annualized_return": round((((portfolio_value / 1000000) ** (1/4)) - 1) * 100, 2),
        "max_drawdown": 35.4,
        "final_portfolio_value": round(portfolio_value, 0)
    }
    
    # 组装最终数据
    analysis_data = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'period': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            'version': 'lightweight-1.0'
        },
        'interest_rates': interest_rates,
        'tax_rates': tax_rates,
        'portfolio_holdings': portfolio_data,
        'inflation_data': inflation_data,
        'crisis_analysis': crisis_analysis,
        'performance_metrics': performance_metrics
    }
    
    return analysis_data

def main():
    """主函数"""
    try:
        # 生成数据
        data = generate_lightweight_data()
        
        # 保存到文件
        output_file = 'financial_analysis_data.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 数据生成完成!")
        print(f"💾 文件已保存: {output_file}")
        print(f"📊 数据统计:")
        print(f"  • 利率数据: {len(data['interest_rates'])} 条")
        print(f"  • 税收数据: {len(data['tax_rates'])} 条")
        print(f"  • 投资组合: {len(data['portfolio_holdings'])} 条")
        print(f"  • 通胀数据: {len(data['inflation_data'])} 条")
        print(f"  • 总体收益: {data['performance_metrics']['total_return']}%")
        
        # 测试仪表板
        print(f"\n🚀 启动测试服务器...")
        print(f"请在浏览器中打开: improved_dashboard.html")
        
    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == "__main__":
    main()