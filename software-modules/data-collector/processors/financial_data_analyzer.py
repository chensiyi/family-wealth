#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
金融数据时间序列分析工具
生成税费、利率、持仓等关键指标的历史数据和趋势分析
"""

import sqlite3
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import math

class FinancialTimeSeriesGenerator:
    """金融时间序列数据生成器"""
    
    def __init__(self):
        self.start_date = datetime(2000, 1, 1)
        self.end_date = datetime(2023, 12, 31)
        self.days_count = (self.end_date - self.start_date).days
    
    def generate_interest_rate_series(self) -> List[Dict]:
        """生成利率时间序列数据"""
        rates = []
        base_rate = 5.0  # 基准利率5%
        current_rate = base_rate
        
        for i in range(self.days_count):
            date = self.start_date + timedelta(days=i)
            
            # 模拟2008年金融危机期间的利率大幅下调
            if date.year == 2008 and date.month >= 9:
                target_rate = 0.5
                adjustment = (target_rate - current_rate) * 0.02
                current_rate += adjustment
            # 2015年后的低利率环境
            elif date.year >= 2015:
                target_rate = 1.5 + math.sin(i * 0.001) * 0.5
                adjustment = (target_rate - current_rate) * 0.01
                current_rate += adjustment
            # 正常周期波动
            else:
                seasonal_factor = math.sin(i * 0.01) * 0.3
                trend_factor = math.sin(i * 0.0005) * 1.0
                noise = random.uniform(-0.1, 0.1)
                current_rate += seasonal_factor + trend_factor + noise
                current_rate = max(0.1, min(10.0, current_rate))
            
            rates.append({
                'date': date.strftime('%Y-%m-%d'),
                'rate': round(current_rate, 3),
                'type': '联邦基金利率'
            })
        
        return rates
    
    def generate_tax_rate_series(self) -> List[Dict]:
        """生成税率时间序列数据"""
        tax_rates = []
        base_corporate_tax = 35.0  # 2000年企业税率
        base_capital_gains = 20.0  # 资本利得税率
        
        for i in range(self.days_count):
            date = self.start_date + timedelta(days=i)
            year = date.year
            
            # 2017年特朗普税改
            if year >= 2018:
                corporate_tax = 21.0
                capital_gains = 20.0
            # 2003年布什税改
            elif year >= 2003:
                corporate_tax = 35.0
                capital_gains = 15.0
            else:
                corporate_tax = base_corporate_tax
                capital_gains = base_capital_gains
            
            # 添加年度小幅调整
            corporate_tax += random.uniform(-0.5, 0.5)
            capital_gains += random.uniform(-0.3, 0.3)
            
            tax_rates.append({
                'date': date.strftime('%Y-%m-%d'),
                'corporate_tax': round(max(15, min(40, corporate_tax)), 2),
                'capital_gains_tax': round(max(10, min(30, capital_gains)), 2),
                'year': year
            })
        
        return tax_rates
    
    def generate_portfolio_holdings_series(self) -> List[Dict]:
        """生成投资组合持仓时间序列"""
        holdings = []
        # 初始配置比例
        equity_pct = 60.0
        bond_pct = 30.0
        cash_pct = 10.0
        
        for i in range(self.days_count):
            date = self.start_date + timedelta(days=i)
            year = date.year
            
            # 2008年金融危机期间的避险行为
            if 2008 <= year <= 2009:
                equity_target = 40.0
                bond_target = 45.0
                cash_target = 15.0
            # 2020年疫情期间的配置调整
            elif year == 2020:
                equity_target = 55.0
                bond_target = 35.0
                cash_target = 10.0
            # 正常时期的均衡配置
            else:
                equity_target = 60.0
                bond_target = 30.0
                cash_target = 10.0
            
            # 渐进式调整
            adjustment_speed = 0.005
            equity_pct += (equity_target - equity_pct) * adjustment_speed
            bond_pct += (bond_target - bond_pct) * adjustment_speed
            cash_pct += (cash_target - cash_pct) * adjustment_speed
            
            # 添加随机波动
            noise = random.uniform(-1, 1)
            equity_pct += noise
            bond_pct -= noise * 0.5
            cash_pct -= noise * 0.5
            
            # 确保总和为100%
            total = equity_pct + bond_pct + cash_pct
            equity_pct = (equity_pct / total) * 100
            bond_pct = (bond_pct / total) * 100
            cash_pct = (cash_pct / total) * 100
            
            holdings.append({
                'date': date.strftime('%Y-%m-%d'),
                'equity_percentage': round(equity_pct, 2),
                'bond_percentage': round(bond_pct, 2),
                'cash_percentage': round(cash_pct, 2),
                'total_value': round(1000000 * (1 + i * 0.0002), 0)  # 假设初始100万美元
            })
        
        return holdings
    
    def generate_inflation_series(self) -> List[Dict]:
        """生成通胀率时间序列"""
        inflation = []
        base_inflation = 2.5
        
        for i in range(self.days_count):
            date = self.start_date + timedelta(days=i)
            
            # 2008年通缩风险
            if date.year == 2009:
                current_inflation = -1.0
            # 2021-2022年高通胀
            elif 2021 <= date.year <= 2022:
                current_inflation = 8.0
            # 正常通胀水平
            else:
                cycle_factor = math.sin(i * 0.001) * 1.5
                current_inflation = base_inflation + cycle_factor + random.uniform(-0.5, 0.5)
                current_inflation = max(-2, min(15, current_inflation))
            
            inflation.append({
                'date': date.strftime('%Y-%m-%d'),
                'inflation_rate': round(current_inflation, 2),
                'cpi': round(100 * math.exp(i * 0.0001 * current_inflation), 2)
            })
        
        return inflation

class DataAnalysisEngine:
    """数据分析引擎"""
    
    def __init__(self):
        self.generator = FinancialTimeSeriesGenerator()
    
    def perform_crisis_analysis(self, data_series: List[Dict], crisis_periods: List[Tuple]) -> Dict:
        """危机期间数据分析"""
        analysis_results = {}
        
        for period_name, start_date, end_date in crisis_periods:
            # 筛选危机期间数据
            crisis_data = [
                record for record in data_series 
                if start_date <= record['date'] <= end_date
            ]
            
            if crisis_data:
                # 计算关键指标变化
                start_value = crisis_data[0]['rate'] if 'rate' in crisis_data[0] else crisis_data[0].get('equity_percentage', 0)
                end_value = crisis_data[-1]['rate'] if 'rate' in crisis_data[-1] else crisis_data[-1].get('equity_percentage', 0)
                change = end_value - start_value
                
                analysis_results[period_name] = {
                    'duration_days': len(crisis_data),
                    'start_value': round(start_value, 3),
                    'end_value': round(end_value, 3),
                    'absolute_change': round(change, 3),
                    'percentage_change': round((change / start_value) * 100, 2) if start_value != 0 else 0,
                    'volatility': self.calculate_volatility([d.get('rate', d.get('equity_percentage', 0)) for d in crisis_data])
                }
        
        return analysis_results
    
    def calculate_volatility(self, values: List[float]) -> float:
        """计算波动率"""
        if len(values) < 2:
            return 0
        
        returns = []
        for i in range(1, len(values)):
            if values[i-1] != 0:
                ret = (values[i] - values[i-1]) / values[i-1]
                returns.append(ret)
        
        if not returns:
            return 0
            
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        return round(math.sqrt(variance) * math.sqrt(252) * 100, 2)  # 年化波动率
    
    def generate_performance_metrics(self, portfolio_data: List[Dict]) -> Dict:
        """生成投资组合绩效指标"""
        if not portfolio_data:
            return {}
        
        # 计算年化收益率
        initial_value = portfolio_data[0]['total_value']
        final_value = portfolio_data[-1]['total_value']
        years = len(portfolio_data) / 365.25
        
        total_return = (final_value - initial_value) / initial_value
        annualized_return = (1 + total_return) ** (1/years) - 1 if years > 0 else 0
        
        # 计算最大回撤
        peak = initial_value
        max_drawdown = 0
        
        for record in portfolio_data:
            current_value = record['total_value']
            if current_value > peak:
                peak = current_value
            
            drawdown = (peak - current_value) / peak
            max_drawdown = max(max_drawdown, drawdown)
        
        return {
            'total_return': round(total_return * 100, 2),
            'annualized_return': round(annualized_return * 100, 2),
            'max_drawdown': round(max_drawdown * 100, 2),
            'final_portfolio_value': final_value
        }

def main():
    """主函数 - 生成分析数据"""
    engine = DataAnalysisEngine()
    
    print("正在生成金融时间序列数据...")
    
    # 生成各类数据序列
    interest_rates = engine.generator.generate_interest_rate_series()
    tax_rates = engine.generator.generate_tax_rate_series()
    portfolio_holdings = engine.generator.generate_portfolio_holdings_series()
    inflation_data = engine.generator.generate_inflation_series()
    
    print(f"✓ 利率数据: {len(interest_rates)} 条记录")
    print(f"✓ 税率数据: {len(tax_rates)} 条记录") 
    print(f"✓ 持仓数据: {len(portfolio_holdings)} 条记录")
    print(f"✓ 通胀数据: {len(inflation_data)} 条记录")
    
    # 定义危机时期
    crisis_periods = [
        ("2008年金融危机", "2008-09-01", "2009-06-30"),
        ("2020年疫情危机", "2020-03-01", "2020-12-31")
    ]
    
    # 进行危机分析
    rate_analysis = engine.perform_crisis_analysis(interest_rates, crisis_periods)
    portfolio_analysis = engine.perform_crisis_analysis(portfolio_holdings, crisis_periods)
    
    print("\n=== 危机期间利率变化分析 ===")
    for crisis, metrics in rate_analysis.items():
        print(f"{crisis}:")
        print(f"  持续时间: {metrics['duration_days']}天")
        print(f"  利率变化: {metrics['start_value']}% → {metrics['end_value']}%")
        print(f"  变化幅度: {metrics['absolute_change']}个百分点 ({metrics['percentage_change']}%)")
        print(f"  期间波动率: {metrics['volatility']}%")
        print()
    
    print("=== 投资组合危机响应分析 ===")
    for crisis, metrics in portfolio_analysis.items():
        print(f"{crisis}:")
        print(f"  股票配置变化: {metrics['start_value']}% → {metrics['end_value']}%")
        print(f"  调整幅度: {metrics['absolute_change']}个百分点")
        print()
    
    # 计算投资组合绩效
    performance = engine.generate_performance_metrics(portfolio_holdings)
    print("=== 投资组合绩效指标 ===")
    print(f"总收益率: {performance['total_return']}%")
    print(f"年化收益率: {performance['annualized_return']}%")
    print(f"最大回撤: {performance['max_drawdown']}%")
    print(f"最终组合价值: ${performance['final_portfolio_value']:,.0f}")
    
    # 保存数据到JSON文件供图表使用
    import json
    analysis_data = {
        'interest_rates': interest_rates[-1000:],  # 取最近1000天数据
        'tax_rates': tax_rates[-1000:],
        'portfolio_holdings': portfolio_holdings[-1000:],
        'inflation_data': inflation_data[-1000:],
        'crisis_analysis': {
            'rate_analysis': rate_analysis,
            'portfolio_analysis': portfolio_analysis
        },
        'performance_metrics': performance
    }
    
    with open('financial_analysis_data.json', 'w', encoding='utf-8') as f:
        json.dump(analysis_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ 分析数据已保存到 financial_analysis_data.json")

if __name__ == "__main__":
    main()