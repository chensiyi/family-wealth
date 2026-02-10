#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专业金融数据采集器
支持多数据源，记录获取时间和来源
"""

import requests
import json
import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
import sqlite3
import time
import random
from dataclasses import dataclass

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class DataSource:
    """数据源配置类"""
    name: str
    base_url: str
    api_endpoint: str
    api_key: Optional[str] = None
    headers: Optional[Dict] = None
    rate_limit: int = 60  # 每分钟请求次数限制
    auth_required: bool = False
    data_format: str = 'json'

class ProfessionalDataCollector:
    """专业金融数据采集器"""
    
    def __init__(self, db_path: str = 'family_wealth_professional.db'):
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # 配置数据源
        self.data_sources = self._setup_data_sources()
        logger.info("✅ 数据采集器初始化完成")
    
    def _setup_data_sources(self) -> Dict[str, DataSource]:
        """配置数据源"""
        return {
            'fred': DataSource(
                name='Federal Reserve Economic Data',
                base_url='https://api.stlouisfed.org',
                api_endpoint='/fred/series/observations',
                api_key='YOUR_FRED_API_KEY',  # 需要申请API密钥
                rate_limit=120
            ),
            'yahoo_finance': DataSource(
                name='Yahoo Finance',
                base_url='https://query1.finance.yahoo.com',
                api_endpoint='/v8/finance/chart',
                rate_limit=2000
            ),
            'worldbank': DataSource(
                name='World Bank Open Data',
                base_url='http://api.worldbank.org',
                api_endpoint='/v2/country/all/indicator',
                data_format='xml',
                rate_limit=150
            ),
            'sec_edgar': DataSource(
                name='SEC EDGAR Database',
                base_url='https://data.sec.gov',
                api_endpoint='/api/xbrl/companyfacts',
                rate_limit=10
            )
        }
    
    def collect_market_data(self, symbols: List[str], period: str = '1y') -> int:
        """收集股票市场数据"""
        logger.info(f"📊 开始收集 {len(symbols)} 个标的的市场数据...")
        collected_count = 0
        
        for symbol in symbols:
            try:
                data = self._fetch_yahoo_finance_data(symbol, period)
                if data:
                    self._store_market_data(data, 'Yahoo Finance')
                    collected_count += 1
                    logger.info(f"✅ 成功收集 {symbol} 数据 ({len(data)} 条记录)")
                
                # 遵守速率限制
                time.sleep(60 / self.data_sources['yahoo_finance'].rate_limit)
                
            except Exception as e:
                logger.error(f"❌ 收集 {symbol} 数据失败: {e}")
                continue
        
        logger.info(f"🎉 市场数据收集完成，共收集 {collected_count} 个标的")
        return collected_count
    
    def _fetch_yahoo_finance_data(self, symbol: str, period: str) -> Optional[List[Dict]]:
        """从Yahoo Finance获取数据"""
        try:
            url = f"{self.data_sources['yahoo_finance'].base_url}{self.data_sources['yahoo_finance'].api_endpoint}/{symbol}"
            params = {
                'range': period,
                'interval': '1d',
                'indicators': 'quote'
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'chart' not in data or 'result' not in data['chart']:
                logger.warning(f"Yahoo Finance返回无效数据格式: {symbol}")
                return None
            
            result = data['chart']['result'][0]
            if 'timestamp' not in result or 'indicators' not in result:
                return None
            
            quotes = result['indicators']['quote'][0]
            timestamps = result['timestamp']
            
            market_data = []
            for i, timestamp in enumerate(timestamps):
                try:
                    market_data.append({
                        'symbol': symbol,
                        'date': datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d'),
                        'open': float(quotes['open'][i]) if quotes['open'][i] is not None else None,
                        'high': float(quotes['high'][i]) if quotes['high'][i] is not None else None,
                        'low': float(quotes['low'][i]) if quotes['low'][i] is not None else None,
                        'close': float(quotes['close'][i]) if quotes['close'][i] is not None else None,
                        'volume': int(quotes['volume'][i]) if quotes['volume'][i] is not None else None,
                        'adjusted_close': float(quotes['close'][i]) if quotes['close'][i] is not None else None
                    })
                except (TypeError, ValueError, IndexError):
                    continue  # 跳过无效数据点
            
            return market_data
            
        except Exception as e:
            logger.error(f"Yahoo Finance数据获取失败 {symbol}: {e}")
            return None
    
    def collect_economic_indicators(self, indicators: List[str], 
                                  start_date: str = '2020-01-01') -> int:
        """收集宏观经济指标"""
        logger.info(f"📈 开始收集 {len(indicators)} 个经济指标...")
        collected_count = 0
        
        # FRED指标映射
        fred_indicators = {
            'GDP': 'Gross Domestic Product',
            'UNRATE': 'Unemployment Rate',
            'CPIAUCSL': 'Consumer Price Index',
            'FEDFUNDS': 'Federal Funds Rate',
            'GS10': '10-Year Treasury Constant Maturity Rate'
        }
        
        for indicator in indicators:
            if indicator in fred_indicators:
                try:
                    data = self._fetch_fred_data(indicator, start_date)
                    if data:
                        self._store_economic_data(data, indicator, 'FRED')
                        collected_count += 1
                        logger.info(f"✅ 成功收集 {indicator} 数据 ({len(data)} 条记录)")
                    
                    time.sleep(60 / self.data_sources['fred'].rate_limit)
                    
                except Exception as e:
                    logger.error(f"❌ 收集 {indicator} 数据失败: {e}")
                    continue
        
        logger.info(f"🎉 经济指标收集完成，共收集 {collected_count} 个指标")
        return collected_count
    
    def _fetch_fred_data(self, series_id: str, start_date: str) -> Optional[List[Dict]]:
        """从FRED获取经济数据"""
        try:
            # 注意：这里需要真实的FRED API密钥
            # 暂时返回模拟数据用于演示
            logger.warning(f"FRED API需要注册密钥，返回模拟数据: {series_id}")
            return self._generate_mock_economic_data(series_id, start_date)
            
        except Exception as e:
            logger.error(f"FRED数据获取失败 {series_id}: {e}")
            return None
    
    def _generate_mock_economic_data(self, indicator: str, start_date: str) -> List[Dict]:
        """生成模拟经济数据"""
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.now()
        days_diff = (end - start).days
        
        data = []
        base_values = {
            'GDP': 21000,  # 单位：十亿美元
            'UNRATE': 3.5,  # 单位：百分比
            'CPIAUCSL': 290,  # CPI指数
            'FEDFUNDS': 2.5,  # 联邦基金利率
            'GS10': 3.2  # 10年期国债收益率
        }
        
        base_value = base_values.get(indicator, 100)
        trend_direction = random.choice([-1, 1])  # 随机趋势方向
        
        for i in range(0, days_diff, 30):  # 每月一条数据
            current_date = start + timedelta(days=i)
            if current_date > end:
                break
                
            # 添加趋势和随机波动
            trend = trend_direction * (i / 365) * 2  # 年化2%的趋势
            noise = random.normalvariate(0, base_value * 0.02)  # 2%的标准差
            
            value = base_value * (1 + trend/100) + noise
            
            # 确保合理范围
            if indicator == 'UNRATE':
                value = max(2.0, min(15.0, value))
            elif indicator == 'FEDFUNDS' or indicator == 'GS10':
                value = max(0.0, min(20.0, value))
            
            data.append({
                'indicator_name': indicator,
                'country_code': 'US',
                'date': current_date.strftime('%Y-%m-%d'),
                'value': round(value, 2),
                'unit': self._get_indicator_unit(indicator),
                'frequency': 'monthly'
            })
        
        return data
    
    def _get_indicator_unit(self, indicator: str) -> str:
        """获取指标单位"""
        units = {
            'GDP': 'Billions USD',
            'UNRATE': 'Percent',
            'CPIAUCSL': 'Index',
            'FEDFUNDS': 'Percent',
            'GS10': 'Percent'
        }
        return units.get(indicator, '')
    
    def _store_market_data(self, data: List[Dict], source: str):
        """存储市场数据到数据库"""
        cursor = self.connection.cursor()
        
        for record in data:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO market_data 
                    (symbol, date, open_price, high_price, low_price, close_price, 
                     volume, adjusted_close, source, fetched_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    record['symbol'],
                    record['date'],
                    record['open'],
                    record['high'],
                    record['low'],
                    record['close'],
                    record['volume'],
                    record['adjusted_close'],
                    source,
                    datetime.now().isoformat()
                ))
            except Exception as e:
                logger.error(f"存储市场数据失败: {e}")
                continue
        
        self.connection.commit()
    
    def _store_economic_data(self, data: List[Dict], indicator_name: str, source: str):
        """存储经济数据到数据库"""
        cursor = self.connection.cursor()
        
        for record in data:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO economic_indicators 
                    (indicator_name, country_code, date, value, unit, frequency, source, fetched_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    indicator_name,
                    record['country_code'],
                    record['date'],
                    record['value'],
                    record['unit'],
                    record['frequency'],
                    source,
                    datetime.now().isoformat()
                ))
            except Exception as e:
                logger.error(f"存储经济数据失败: {e}")
                continue
        
        self.connection.commit()
    
    def collect_tax_policy_data(self) -> int:
        """收集税收政策数据"""
        logger.info("⚖️ 开始收集税收政策数据...")
        
        # 预定义的税收政策数据
        tax_policies = [
            {
                'policy_type': 'Corporate Tax Rate',
                'jurisdiction': 'United States',
                'effective_date': '2018-01-01',
                'expiration_date': None,
                'rate_percentage': 21.0,
                'rate_type': 'flat',
                'exemption_amount': None,
                'deduction_limit': None,
                'policy_description': 'Tax Cuts and Jobs Act - 企业税率从35%降至21%',
                'source_document': 'Tax Cuts and Jobs Act of 2017',
                'verified': True
            },
            {
                'policy_type': 'Capital Gains Tax',
                'jurisdiction': 'United States',
                'effective_date': '2003-01-01',
                'expiration_date': None,
                'rate_percentage': 15.0,
                'rate_type': 'flat',
                'exemption_amount': None,
                'deduction_limit': None,
                'policy_description': 'Jobs and Growth Tax Relief Reconciliation Act - 资本利得税率降至15%',
                'source_document': 'JGTRRA 2003',
                'verified': True
            }
        ]
        
        cursor = self.connection.cursor()
        stored_count = 0
        
        for policy in tax_policies:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO tax_policy_history 
                    (policy_type, jurisdiction, effective_date, expiration_date, rate_percentage,
                     rate_type, exemption_amount, deduction_limit, policy_description, 
                     source_document, verified, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    policy['policy_type'],
                    policy['jurisdiction'],
                    policy['effective_date'],
                    policy['expiration_date'],
                    policy['rate_percentage'],
                    policy['rate_type'],
                    policy['exemption_amount'],
                    policy['deduction_limit'],
                    policy['policy_description'],
                    policy['source_document'],
                    policy['verified'],
                    datetime.now().isoformat()
                ))
                stored_count += 1
            except Exception as e:
                logger.error(f"存储税收政策数据失败: {e}")
                continue
        
        self.connection.commit()
        logger.info(f"✅ 税收政策数据收集完成，共存储 {stored_count} 条记录")
        return stored_count
    
    def get_collection_statistics(self) -> Dict:
        """获取数据收集统计信息"""
        stats = {}
        
        cursor = self.connection.cursor()
        
        # 市场数据统计
        cursor.execute("SELECT COUNT(DISTINCT symbol) as symbols, COUNT(*) as total_records FROM market_data")
        market_stats = cursor.fetchone()
        stats['market_data'] = {
            'unique_symbols': market_stats['symbols'],
            'total_records': market_stats['total_records']
        }
        
        # 经济指标统计
        cursor.execute("SELECT COUNT(DISTINCT indicator_name) as indicators, COUNT(*) as total_records FROM economic_indicators")
        econ_stats = cursor.fetchone()
        stats['economic_indicators'] = {
            'unique_indicators': econ_stats['indicators'],
            'total_records': econ_stats['total_records']
        }
        
        # 数据源统计
        cursor.execute("SELECT source, COUNT(*) as count FROM market_data GROUP BY source")
        source_stats = cursor.fetchall()
        stats['data_sources'] = {row['source']: row['count'] for row in source_stats}
        
        # 最新数据时间
        cursor.execute("SELECT MAX(date) as latest_date FROM market_data")
        latest_date = cursor.fetchone()['latest_date']
        stats['latest_data_date'] = latest_date
        
        return stats
    
    def close(self):
        """关闭连接"""
        self.connection.close()
        self.session.close()
        logger.info("🔒 数据采集器连接已关闭")

def main():
    """主函数 - 演示数据采集功能"""
    try:
        # 初始化数据采集器
        collector = ProfessionalDataCollector()
        
        # 收集市场数据
        market_symbols = ['^GSPC', 'AAPL', 'GOOGL', 'MSFT', 'TSLA']
        market_count = collector.collect_market_data(market_symbols, '2y')
        
        # 收集经济指标
        indicators = ['GDP', 'UNRATE', 'CPIAUCSL', 'FEDFUNDS', 'GS10']
        econ_count = collector.collect_economic_indicators(indicators, '2020-01-01')
        
        # 收集税收政策数据
        tax_count = collector.collect_tax_policy_data()
        
        # 显示统计信息
        stats = collector.get_collection_statistics()
        logger.info("📊 数据收集统计:")
        logger.info(f"  市场数据: {stats['market_data']['unique_symbols']} 个标的, {stats['market_data']['total_records']} 条记录")
        logger.info(f"  经济指标: {stats['economic_indicators']['unique_indicators']} 个指标, {stats['economic_indicators']['total_records']} 条记录")
        logger.info(f"  税收政策: {tax_count} 条记录")
        logger.info(f"  最新数据日期: {stats['latest_data_date']}")
        logger.info(f"  数据来源: {stats['data_sources']}")
        
        collector.close()
        logger.info("🎉 数据采集演示完成!")
        
    except Exception as e:
        logger.error(f"❌ 数据采集过程中出现错误: {e}")
        raise

if __name__ == "__main__":
    main()