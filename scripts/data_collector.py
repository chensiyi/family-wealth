#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
家族财富管理沙盘系统 - 数据采集和处理工具
"""

import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sqlite3
import logging
from dataclasses import dataclass

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DataSourceConfig:
    """数据源配置"""
    name: str
    url: str
    api_key: Optional[str] = None
    headers: Optional[Dict] = None
    frequency: str = "daily"  # daily, weekly, monthly

class FinancialDataCollector:
    """金融数据采集器"""
    
    def __init__(self):
        self.data_sources = self._configure_data_sources()
        self.db_connection = self._initialize_database()
    
    def _configure_data_sources(self) -> Dict[str, DataSourceConfig]:
        """配置数据源"""
        sources = {
            'fred': DataSourceConfig(
                name='Federal Reserve Economic Data',
                url='https://api.stlouisfed.org/fred/series/observations',
                api_key='YOUR_FRED_API_KEY'
            ),
            'worldbank': DataSourceConfig(
                name='World Bank Open Data',
                url='http://api.worldbank.org/v2/country/all/indicator'
            ),
            'yahoo_finance': DataSourceConfig(
                name='Yahoo Finance API',
                url='https://query1.finance.yahoo.com/v8/finance/chart'
            )
        }
        return sources
    
    def _initialize_database(self) -> sqlite3.Connection:
        """初始化SQLite数据库"""
        conn = sqlite3.connect('sandbox_data.db')
        
        # 创建参与者档案表
        conn.execute('''
            CREATE TABLE IF NOT EXISTS participants_profile (
                participant_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                role TEXT NOT NULL,
                tier_level INTEGER,
                jurisdiction TEXT,
                assets_under_management REAL,
                market_influence_score REAL,
                risk_profile TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建历史事件表
        conn.execute('''
            CREATE TABLE IF NOT EXISTS historical_events (
                event_id TEXT PRIMARY KEY,
                event_date DATE NOT NULL,
                event_type TEXT NOT NULL,
                description TEXT,
                impact_score REAL,
                affected_participants TEXT,
                data_sources TEXT,
                verified BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建决策行为表
        conn.execute('''
            CREATE TABLE IF NOT EXISTS decision_actions (
                action_id TEXT PRIMARY KEY,
                participant_id TEXT,
                event_id TEXT,
                decision_timestamp TIMESTAMP,
                action_type TEXT NOT NULL,
                asset_class TEXT,
                amount REAL,
                rationale TEXT,
                actual_outcome TEXT,
                FOREIGN KEY (participant_id) REFERENCES participants_profile(participant_id),
                FOREIGN KEY (event_id) REFERENCES historical_events(event_id)
            )
        ''')
        
        conn.commit()
        return conn
    
    def collect_fred_data(self, series_id: str, start_date: str, end_date: str) -> pd.DataFrame:
        """收集FRED经济数据"""
        try:
            params = {
                'series_id': series_id,
                'api_key': self.data_sources['fred'].api_key,
                'file_type': 'json',
                'observation_start': start_date,
                'observation_end': end_date
            }
            
            response = requests.get(self.data_sources['fred'].url, params=params)
            response.raise_for_status()
            
            data = response.json()
            observations = data['observations']
            
            df = pd.DataFrame(observations)
            df['date'] = pd.to_datetime(df['date'])
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            
            logger.info(f"成功收集 {series_id} 数据，共 {len(df)} 条记录")
            return df
            
        except Exception as e:
            logger.error(f"收集FRED数据失败: {e}")
            return pd.DataFrame()
    
    def collect_market_data(self, symbol: str, period: str = '1y') -> pd.DataFrame:
        """收集市场数据"""
        try:
            url = f"{self.data_sources['yahoo_finance'].url}/{symbol}"
            params = {
                'range': period,
                'interval': '1d',
                'indicators': 'quote'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            quotes = data['chart']['result'][0]['indicators']['quote'][0]
            timestamps = data['chart']['result'][0]['timestamp']
            
            df = pd.DataFrame({
                'timestamp': timestamps,
                'open': quotes['open'],
                'high': quotes['high'],
                'low': quotes['low'],
                'close': quotes['close'],
                'volume': quotes['volume']
            })
            
            df['date'] = pd.to_datetime(df['timestamp'], unit='s')
            df = df.drop('timestamp', axis=1)
            
            logger.info(f"成功收集 {symbol} 市场数据")
            return df
            
        except Exception as e:
            logger.error(f"收集市场数据失败: {e}")
            return pd.DataFrame()
    
    def store_participant_data(self, participant_data: Dict):
        """存储参与者数据"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO participants_profile 
                (participant_id, name, type, role, tier_level, jurisdiction, 
                 assets_under_management, market_influence_score, risk_profile)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                participant_data['participant_id'],
                participant_data['name'],
                participant_data['type'],
                participant_data['role'],
                participant_data.get('tier_level'),
                participant_data.get('jurisdiction'),
                participant_data.get('assets_under_management'),
                participant_data.get('market_influence_score'),
                json.dumps(participant_data.get('risk_profile', {}))
            ))
            
            self.db_connection.commit()
            logger.info(f"成功存储参与者数据: {participant_data['name']}")
            
        except Exception as e:
            logger.error(f"存储参与者数据失败: {e}")
    
    def store_event_data(self, event_data: Dict):
        """存储历史事件数据"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO historical_events 
                (event_id, event_date, event_type, description, impact_score, 
                 affected_participants, data_sources, verified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event_data['event_id'],
                event_data['event_date'],
                event_data['event_type'],
                event_data['description'],
                event_data.get('impact_score', 0),
                json.dumps(event_data.get('affected_participants', [])),
                json.dumps(event_data.get('data_sources', [])),
                event_data.get('verified', False)
            ))
            
            self.db_connection.commit()
            logger.info(f"成功存储事件数据: {event_data['event_id']}")
            
        except Exception as e:
            logger.error(f"存储事件数据失败: {e}")

class CrisisEventAnalyzer:
    """危机事件分析器"""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def analyze_2008_crisis(self):
        """分析2008年金融危机"""
        crisis_events = [
            {
                'event_id': '2008_lehman_bankruptcy',
                'event_date': '2008-09-15',
                'event_type': 'corporate',
                'description': '雷曼兄弟申请破产保护，引发全球金融危机',
                'impact_score': 9.5,
                'affected_participants': ['Lehman Brothers', 'Goldman Sachs', 'JP Morgan', 'Bear Stearns'],
                'data_sources': ['SEC filings', 'Fed records', 'News reports'],
                'verified': True
            },
            {
                'event_id': '2008_tarp_approval',
                'event_date': '2008-10-03',
                'event_type': 'policy',
                'description': '美国国会批准7000亿美元问题资产救助计划(TARP)',
                'impact_score': 8.0,
                'affected_participants': ['US Treasury', 'Major Banks', 'Insurance Companies'],
                'data_sources': ['Congressional records', 'Treasury documents'],
                'verified': True
            }
        ]
        
        # 存储危机事件数据
        collector = FinancialDataCollector()
        for event in crisis_events:
            collector.store_event_data(event)
        
        # 分析参与者行为
        self._analyze_participant_responses(crisis_events)
    
    def _analyze_participant_responses(self, events: List[Dict]):
        """分析参与者应对行为"""
        behaviors = [
            {
                'action_id': 'gs_2008_short_covering',
                'participant_id': 'Goldman_Sachs',
                'event_id': '2008_lehman_bankruptcy',
                'decision_timestamp': '2008-09-16 09:30:00',
                'action_type': 'liquidity',
                'asset_class': 'cash',
                'amount': 50000000000,  # 500亿美元
                'rationale': '应对市场流动性危机，保护客户资产',
                'actual_outcome': {
                    'short_term_impact': '维持了市场信心',
                    'long_term_benefit': '获得了竞争优势'
                }
            },
            {
                'action_id': 'jpm_2008_washington_mutual_acquisition',
                'participant_id': 'JP_Morgan',
                'event_id': '2008_lehman_bankruptcy',
                'decision_timestamp': '2008-09-25 18:00:00',
                'action_type': 'investment',
                'asset_class': 'banking_assets',
                'amount': 19000000000,  # 190亿美元
                'rationale': '以极低价格收购优质资产，扩大市场份额',
                'actual_outcome': {
                    'short_term_cost': '承担了整合风险',
                    'long_term_gain': '成为美国最大银行'
                }
            }
        ]
        
        # 存储行为数据
        cursor = self.db.cursor()
        for behavior in behaviors:
            cursor.execute('''
                INSERT OR REPLACE INTO decision_actions 
                (action_id, participant_id, event_id, decision_timestamp, action_type,
                 asset_class, amount, rationale, actual_outcome)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                behavior['action_id'],
                behavior['participant_id'],
                behavior['event_id'],
                behavior['decision_timestamp'],
                behavior['action_type'],
                behavior['asset_class'],
                behavior['amount'],
                behavior['rationale'],
                json.dumps(behavior['actual_outcome'])
            ))
        
        self.db.commit()
        logger.info("参与者行为分析完成")

def main():
    """主函数"""
    # 初始化数据采集器
    collector = FinancialDataCollector()
    
    # 收集宏观经济数据示例
    gdp_data = collector.collect_fred_data('GDP', '2000-01-01', '2023-12-31')
    unemployment_data = collector.collect_fred_data('UNRATE', '2000-01-01', '2023-12-31')
    
    # 收集市场数据示例
    sp500_data = collector.collect_market_data('^GSPC', '5y')
    gold_data = collector.collect_market_data('GC=F', '5y')
    
    # 分析危机事件
    analyzer = CrisisEventAnalyzer(collector.db_connection)
    analyzer.analyze_2008_crisis()
    
    logger.info("数据采集和分析完成")

if __name__ == "__main__":
    main()