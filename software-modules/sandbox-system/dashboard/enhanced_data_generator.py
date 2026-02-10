#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改进版金融数据分析工具
生成更真实、更有价值的时间序列数据
"""

import sqlite3
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import math
import numpy as np

class EnhancedFinancialDataGenerator:
    """增强版金融数据生成器"""
    
    def __init__(self):
        self.start_date = datetime(2000, 1, 1)
        self.end_date = datetime(2024, 12, 31)
        self.days_count = (self.end_date - self.start_date).days
        
    def generate_enhanced_interest_rates(self) -> List[Dict]:
        """生成增强版利率数据 - 更贴近真实市场行为"""
        rates = []
        current_rate = 6.5  # 2000年初基准利率
        
        # 定义关键历史时期的真实利率变化
        historical_periods = {
            # 网络泡沫破裂期 (2000-2001)
            (datetime(2000, 1, 1), datetime(2001, 12, 31)): lambda x: 6.5 - 2.5 * (x/730),
            # 911后降息周期 (2001-2003)
            (datetime(2001, 1, 1), datetime(2003, 6, 30)): lambda x: 4.0 - 3.5 * (x/880),
            # 房地产繁荣期 (2003-2006)
            (datetime(2003, 1, 1), datetime(2006, 6, 30)): lambda x: 1.0 + 3.0 * (x/1278),
            # 次贷危机前 (2006-2007)
            (datetime(2006, 1, 1), datetime(2007, 8, 31)): lambda x: 5.25 - 1.5 * (x/608),
            # 金融危机降息 (2007-2009)
            (datetime(2007, 1, 1), datetime(2009, 3, 31)): lambda x: 5.25 - 5.15 * (x/789),
            # QE时代低利率 (2009-2015)
            (datetime(2009, 1, 1), datetime(2015, 12, 31)): lambda x: 0.1 + 0.5 * math.sin(x * 0.002),
            # 加息周期 (2015-2018)
            (datetime(2015, 1, 1), datetime(2018, 12, 31)): lambda x: 0.25 + 2.5 * (x/1460),
            # 疫情降息 (2019-2020)
            (datetime(2019, 1, 1), datetime(2020, 12, 31)): lambda x: 2.5 - 2.4 * (x/1095) if x < 365 else 0.1,
            # 疫情后复苏 (2021-2024)
            (datetime(2021, 1, 1), datetime(2024, 12, 31)): lambda x: 0.1 + 0.25 * (x/1460) + 2.0 * math.sin(x * 0.01)
        }
        
        for i in range(self.days_count):
            date = self.start_date + timedelta(days=i)
            
            # 找到对应的周期函数
            rate_func = None
            for (start, end), func in historical_periods.items():
                if start <= date <= end:
                    # 计算在这个周期内的相对位置
                    period_start = (date - start).days
                    rate_func = func
                    break
            
            if rate_func:
                # 应用周期函数并添加噪声
                base_rate = max(0.0, rate_func(period_start))
                noise = random.normalvariate(0, 0.15)  # 正态分布噪声
                seasonal = 0.2 * math.sin(2 * math.pi * i / 365)  # 年度季节性
                current_rate = base_rate + noise + seasonal
            else:
                # 默认情况下缓慢回归均值
                target_rate = 2.5
                adjustment = (target_rate - current_rate) * 0.001
                noise = random.normalvariate(0, 0.1)
                current_rate += adjustment + noise
            
            # 确保利率在合理范围内
            current_rate = max(0.0, min(10.0, current_rate))
            
            rates.append({
                'date': date.strftime('%Y-%m-%d'),
                'rate': round(current_rate, 3),
                'fed_funds_rate': round(current_rate, 3),
                'real_rate': round(current_rate - 2.5, 3),  # 假设2.5%长期通胀目标
                'policy_regime': self._get_policy_regime(date, current_rate)
            })
        
        return rates
    
    def _get_policy_regime(self, date: datetime, rate: float) -> str:
        """判断货币政策立场"""
        if rate < 1.0:
            return "极度宽松"
        elif rate < 3.0:
            return "宽松"
        elif rate < 5.0:
            return "中性"
        else:
            return "紧缩"
    
    def generate_realistic_tax_data(self) -> List[Dict]:
        """生成更真实的税收数据"""
        tax_data = []
        
        # 历史上重要的税改节点
        tax_changes = {
            2001: {'corporate': 35.0, 'capital_gains': 20.0},  # 布什减税
            2003: {'corporate': 35.0, 'capital_gains': 15.0},  # 资本利得税降低
            2017: {'corporate': 21.0, 'capital_gains': 20.0},  # 特朗普税改
        }
        
        current_corp_tax = 35.0
        current_cg_tax = 20.0
        
        for i in range(self.days_count):
            date = self.start_date + timedelta(days=i)
            year = date.year
            
            # 检查是否有税改
            if year in tax_changes:
                current_corp_tax = tax_changes[year]['corporate']
                current_cg_tax = tax_changes[year]['capital_gains']
            
            # 添加年度微调和州税影响
            corp_adjustment = random.normalvariate(0, 0.3)
            cg_adjustment = random.normalvariate(0, 0.2)
            
            # 考虑经济周期影响
            economic_cycle = math.sin(2 * math.pi * i / (365 * 8))  # 8年周期
            cyclical_adjustment = economic_cycle * 0.5
            
            corporate_tax = max(15, min(40, current_corp_tax + corp_adjustment + cyclical_adjustment))
            capital_gains_tax = max(10, min(30, current_cg_tax + cg_adjustment))
            
            tax_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'corporate_tax': round(corporate_tax, 2),
                'capital_gains_tax': round(capital_gains_tax, 2),
                'payroll_tax': round(7.65 + random.normalvariate(0, 0.1), 2),  # 社保税
                'estate_tax_exemption': self._calculate_estate_exemption(year),
                'tax_burden_index': round((corporate_tax + capital_gains_tax) / 2, 2)
            })
        
        return tax_data
    
    def _calculate_estate_exemption(self, year: int) -> float:
        """计算遗产税豁免额"""
        if year < 2002:
            return 1000000  # 100万美元
        elif year < 2009:
            return 3500000  # 逐步提高到350万
        elif year < 2011:
            return 1000000  # 短暂回到100万
        elif year < 2018:
            return 5490000  # 逐步提高
        elif year < 2026:
            return 11700000  # 2018-2025年1170万
        else:
            return 5000000  # 预计回到约500万
    
    def generate_advanced_portfolio_data(self) -> List[Dict]:
        """生成高级投资组合数据 - 包含更多资产类别"""
        holdings = []
        
        # 初始配置 (2000年)
        allocation = {
            'us_equity': 50.0,
            'intl_equity': 15.0,
            'us_bonds': 25.0,
            'commodities': 5.0,
            'reits': 3.0,
            'cash': 2.0
        }
        
        portfolio_value = 1000000  # 初始100万美元
        
        # 历史重大事件对配置的影响
        events = {
            2000: {'us_equity': -15, 'cash': 10},  # 网络泡沫破裂
            2003: {'us_equity': 10, 'intl_equity': 5},  # 房地产繁荣
            2008: {'us_equity': -20, 'us_bonds': 15, 'cash': 5},  # 金融危机
            2010: {'intl_equity': 8, 'commodities': 3},  # 复苏期多元化
            2015: {'us_equity': 5, 'reits': 2},  # 低利率环境
            2020: {'us_equity': -10, 'us_bonds': 8, 'cash': 2},  # 疫情初期
            2021: {'us_equity': 12, 'commodities': 3},  # 疫情后反弹
        }
        
        for i in range(self.days_count):
            date = self.start_date + timedelta(days=i)
            year = date.year
            
            # 处理重大事件
            if year in events:
                for asset_class, change in events[year].items():
                    if asset_class in allocation:
                        allocation[asset_class] += change
            
            # 市场驱动的自然调整
            days_passed = i
            market_phase = math.sin(2 * math.pi * days_passed / (365 * 7))  # 7年周期
            
            # 牛市时增加股票配置
            if market_phase > 0:
                allocation['us_equity'] += 0.002
                allocation['cash'] -= 0.002
            else:
                allocation['us_equity'] -= 0.001
                allocation['cash'] += 0.001
            
            # 添加随机扰动
            for asset_class in allocation:
                noise = random.normalvariate(0, 0.2)
                allocation[asset_class] += noise
            
            # 确保配置合理性
            total = sum(allocation.values())
            for key in allocation:
                allocation[key] = max(0, allocation[key])
            # 重新归一化
            if total > 0:
                for key in allocation:
                    allocation[key] = (allocation[key] / total) * 100
            
            # 计算组合价值变化
            daily_return = self._calculate_daily_portfolio_return(date, allocation)
            portfolio_value *= (1 + daily_return)
            
            # 添加通胀影响
            inflation_rate = 0.025 + 0.01 * math.sin(2 * math.pi * days_passed / (365 * 5))
            portfolio_value *= (1 + inflation_rate / 365)
            
            holdings.append({
                'date': date.strftime('%Y-%m-%d'),
                'allocation': {k: round(v, 2) for k, v in allocation.items()},
                'total_value': round(portfolio_value, 2),
                'daily_return': round(daily_return * 100, 3),
                'sharpe_ratio': self._calculate_sharpe_ratio(holdings[-30:] if len(holdings) >= 30 else holdings),
                'drawdown': self._calculate_current_drawdown(holdings)
            })
        
        return holdings
    
    def _calculate_daily_portfolio_return(self, date: datetime, allocation: Dict) -> float:
        """计算每日组合收益"""
        # 简化的资产收益模型
        us_equity_return = random.normalvariate(0.0004, 0.015)  # 年化约10%波动率
        intl_equity_return = random.normalvariate(0.0003, 0.018)  # 稍高波动率
        bonds_return = random.normalvariate(0.0002, 0.005)  # 较低波动率
        commodities_return = random.normalvariate(0.0001, 0.02)  # 高波动率
        reits_return = random.normalvariate(0.0003, 0.012)  # 中等波动率
        cash_return = 0.0001  # 现金收益很低
        
        # 考虑市场联动
        if date.year in [2000, 2008, 2020]:  # 危机年份
            crisis_factor = -0.001
            us_equity_return += crisis_factor
            intl_equity_return += crisis_factor * 1.2  # 国际股市跌幅更大
        
        weighted_return = (
            allocation['us_equity'] * us_equity_return +
            allocation['intl_equity'] * intl_equity_return +
            allocation['us_bonds'] * bonds_return +
            allocation['commodities'] * commodities_return +
            allocation['reits'] * reits_return +
            allocation['cash'] * cash_return
        ) / 100
        
        return weighted_return
    
    def _calculate_sharpe_ratio(self, recent_data: List[Dict]) -> float:
        """计算夏普比率"""
        if len(recent_data) < 2:
            return 0
        
        returns = [d['daily_return']/100 for d in recent_data]
        if len(set(returns)) <= 1:  # 所有收益相同
            return 0
            
        avg_return = np.mean(returns)
        std_dev = np.std(returns)
        
        # 年化夏普比率 (假设无风险利率为2%)
        annualized_return = (1 + avg_return) ** 252 - 1
        annualized_std = std_dev * math.sqrt(252)
        risk_free_rate = 0.02
        
        if annualized_std > 0:
            sharpe = (annualized_return - risk_free_rate) / annualized_std
            return round(sharpe, 2)
        return 0
    
    def _calculate_current_drawdown(self, holdings: List[Dict]) -> float:
        """计算当前回撤"""
        if not holdings:
            return 0
        
        current_value = holdings[-1]['total_value']
        peak_value = max(h['total_value'] for h in holdings)
        
        if peak_value > 0:
            drawdown = (peak_value - current_value) / peak_value
            return round(drawdown * 100, 2)
        return 0
    
    def generate_enhanced_inflation_data(self) -> List[Dict]:
        """生成增强版通胀数据"""
        inflation_data = []
        
        # 历史通胀模式
        base_inflation = 2.5
        oil_shock_years = [2008, 2022]  # 石油冲击年份
        pandemic_years = [2020, 2021]   # 疫情年份
        
        for i in range(self.days_count):
            date = self.start_date + timedelta(days=i)
            year = date.year
            
            # 基础通胀趋势
            long_term_trend = base_inflation + 0.5 * math.sin(2 * math.pi * i / (365 * 15))  # 15年长周期
            
            # 短期波动
            short_term_cycle = 1.0 * math.sin(2 * math.pi * i / (365 * 3))  # 3年周期
            seasonal = 0.3 * math.sin(2 * math.pi * i / 365)  # 年度季节性
            
            # 特殊事件冲击
            shock_effect = 0
            if year in oil_shock_years:
                shock_effect = 3.0 * math.exp(-(i % 365) / 100)  # 指数衰减
            elif year in pandemic_years:
                shock_effect = (-1.0 if year == 2020 else 2.5) * math.exp(-(i % 365) / 150)
            
            # 随机噪声
            noise = random.normalvariate(0, 0.3)
            
            inflation_rate = long_term_trend + short_term_cycle + seasonal + shock_effect + noise
            inflation_rate = max(-2.0, min(15.0, inflation_rate))  # 限制在合理范围
            
            # 计算CPI (基于通胀率累积)
            cpi_base = 100
            cumulative_inflation = sum(
                inf_rate for inf_rate in 
                [float(d.get('inflation_rate', 0)) for d in inflation_data[-365:] if d]
            ) / 100 if len(inflation_data) >= 365 else 0
            
            cpi = cpi_base * (1 + cumulative_inflation/100)
            
            inflation_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'inflation_rate': round(inflation_rate, 2),
                'cpi': round(cpi, 2),
                'core_inflation': round(max(0, inflation_rate - 0.5), 2),  # 扣除食品能源
                'breakeven_inflation': round(inflation_rate + 0.5, 2),  # TIPS盈亏平衡通胀率
                'inflation_regime': self._classify_inflation_regime(inflation_rate)
            })
        
        return inflation_data
    
    def _classify_inflation_regime(self, rate: float) -> str:
        """通胀区间分类"""
        if rate < 0:
            return "通缩"
        elif rate < 2:
            return "低通胀"
        elif rate < 4:
            return "温和通胀"
        elif rate < 7:
            return "中度通胀"
        else:
            return "高通胀"

class DataQualityAssurance:
    """数据质量保证工具"""
    
    @staticmethod
    def validate_data_consistency(data_list: List[Dict], date_field: str = 'date') -> Dict:
        """验证数据一致性"""
        validation_results = {
            'total_records': len(data_list),
            'date_range': None,
            'missing_values': 0,
            'outliers': [],
            'consistency_issues': []
        }
        
        if not data_list:
            return validation_results
        
        # 检查日期范围
        dates = [datetime.strptime(record[date_field], '%Y-%m-%d') for record in data_list]
        validation_results['date_range'] = {
            'start': min(dates).strftime('%Y-%m-%d'),
            'end': max(dates).strftime('%Y-%m-%d')
        }
        
        # 检查缺失值
        for record in data_list:
            for key, value in record.items():
                if value is None or (isinstance(value, float) and math.isnan(value)):
                    validation_results['missing_values'] += 1
        
        # 检查异常值（简单统计方法）
        numeric_fields = [key for key in data_list[0].keys() 
                         if isinstance(data_list[0][key], (int, float)) and key != date_field]
        
        for field in numeric_fields:
            values = [record[field] for record in data_list if isinstance(record[field], (int, float))]
            if values:
                mean_val = np.mean(values)
                std_val = np.std(values)
                threshold = 3 * std_val
                
                outliers = [(i, val) for i, val in enumerate(values) 
                           if abs(val - mean_val) > threshold]
                if outliers:
                    validation_results['outliers'].append({
                        'field': field,
                        'count': len(outliers),
                        'examples': outliers[:5]  # 最多显示5个例子
                    })
        
        return validation_results

def main():
    """主函数 - 生成改进版分析数据"""
    generator = EnhancedFinancialDataGenerator()
    qa = DataQualityAssurance()
    
    print("🚀 正在生成增强版金融时间序列数据...")
    print("=" * 50)
    
    # 生成各类数据序列
    print("📊 生成利率数据...")
    interest_rates = generator.generate_enhanced_interest_rates()
    
    print("💰 生成税收数据...")
    tax_rates = generator.generate_realistic_tax_data()
    
    print("📈 生成投资组合数据...")
    portfolio_data = generator.generate_advanced_portfolio_data()
    
    print("🔥 生成通胀数据...")
    inflation_data = generator.generate_enhanced_inflation_data()
    
    # 数据质量检查
    print("\n🔍 进行数据质量检查...")
    quality_reports = {
        'interest_rates': qa.validate_data_consistency(interest_rates),
        'tax_rates': qa.validate_data_consistency(tax_rates),
        'portfolio_data': qa.validate_data_consistency(portfolio_data),
        'inflation_data': qa.validate_data_consistency(inflation_data)
    }
    
    # 输出统计信息
    print("\n📋 数据生成统计:")
    for data_name, data in [('利率数据', interest_rates), ('税收数据', tax_rates), 
                           ('投资组合数据', portfolio_data), ('通胀数据', inflation_data)]:
        print(f"  {data_name}: {len(data)} 条记录")
    
    print("\n✅ 质量检查结果:")
    for name, report in quality_reports.items():
        print(f"  {name}: {report['total_records']} 条记录, "
              f"{report['missing_values']} 个缺失值")
    
    # 定义危机时期分析
    crisis_periods = [
        ("2000年网络泡沫破裂", "2000-03-01", "2001-11-30"),
        ("2008年金融危机", "2008-09-01", "2009-06-30"),
        ("2020年疫情危机", "2020-02-01", "2020-12-31")
    ]
    
    # 生成危机分析报告
    crisis_analysis = {}
    for period_name, start_date, end_date in crisis_periods:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        # 筛选危机期间数据
        crisis_interest = [r for r in interest_rates 
                          if start_date <= r['date'] <= end_date]
        crisis_portfolio = [p for p in portfolio_data 
                           if start_date <= p['date'] <= end_date]
        
        if crisis_interest and crisis_portfolio:
            crisis_analysis[period_name] = {
                'duration_days': len(crisis_interest),
                'rate_change': {
                    'start': crisis_interest[0]['rate'],
                    'end': crisis_interest[-1]['rate'],
                    'change': round(crisis_interest[-1]['rate'] - crisis_interest[0]['rate'], 3)
                },
                'portfolio_response': {
                    'start_value': crisis_portfolio[0]['total_value'],
                    'end_value': crisis_portfolio[-1]['total_value'],
                    'drawdown': crisis_portfolio[-1]['drawdown']
                }
            }
    
    # 计算整体绩效指标
    performance_metrics = {
        'total_return': round(((portfolio_data[-1]['total_value'] / portfolio_data[0]['total_value']) - 1) * 100, 2),
        'annualized_return': round((((portfolio_data[-1]['total_value'] / portfolio_data[0]['total_value']) ** 
                                   (1/(len(portfolio_data)/365.25))) - 1) * 100, 2),
        'max_drawdown': max(p['drawdown'] for p in portfolio_data),
        'final_portfolio_value': portfolio_data[-1]['total_value'],
        'current_sharpe_ratio': portfolio_data[-1]['sharpe_ratio'] if portfolio_data else 0
    }
    
    # 准备输出数据
    analysis_data = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'data_period': {
                'start': generator.start_date.strftime('%Y-%m-%d'),
                'end': generator.end_date.strftime('%Y-%m-%d')
            },
            'generator_version': '2.0'
        },
        'interest_rates': interest_rates[-1500:],  # 取最近约4年数据
        'tax_rates': tax_rates[-1500:],
        'portfolio_holdings': portfolio_data[-1500:],
        'inflation_data': inflation_data[-1500:],
        'quality_reports': quality_reports,
        'crisis_analysis': crisis_analysis,
        'performance_metrics': performance_metrics
    }
    
    # 保存数据
    output_file = 'enhanced_financial_analysis_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 增强版分析数据已保存到: {output_file}")
    print(f"📁 文件大小: {open(output_file, 'rb').read().__len__()/1024:.1f} KB")
    
    # 生成简要报告
    print("\n📋 执行摘要:")
    print(f"  • 时间跨度: {generator.start_date.strftime('%Y')} - {generator.end_date.strftime('%Y')}")
    print(f"  • 数据质量: 优秀 ({sum(r['missing_values'] for r in quality_reports.values())} 个缺失值)")
    print(f"  • 总体收益: {performance_metrics['total_return']}%")
    print(f"  • 年化收益: {performance_metrics['annualized_return']}%")
    print(f"  • 最大回撤: {performance_metrics['max_drawdown']}%")
    print(f"  • 当前夏普比率: {performance_metrics['current_sharpe_ratio']}")

if __name__ == "__main__":
    main()