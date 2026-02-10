#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
参与者数据库初始化脚本
填充重要的金融机构和参与者档案
"""

import sqlite3
import json
from datetime import datetime

def initialize_participants_database():
    """初始化参与者数据库"""
    
    # 连接数据库
    conn = sqlite3.connect('sandbox_data.db')
    cursor = conn.cursor()
    
    # 重要金融机构档案数据
    major_participants = [
        # 中央银行
        {
            'participant_id': 'FEDERAL_RESERVE',
            'name': 'Federal Reserve System',
            'type': 'government',
            'role': 'regulator',
            'tier_level': 1,
            'jurisdiction': 'United States',
            'assets_under_management': 8000000000000,  # 8万亿美元
            'market_influence_score': 10.0,
            'risk_profile': {
                'risk_tolerance': 'high',
                'decision_horizon': 'long_term',
                'information_advantage': 'extreme',
                'regulatory_power': 'supreme'
            }
        },
        
        # 顶级投行
        {
            'participant_id': 'GOLDMAN_SACHS',
            'name': 'Goldman Sachs Group Inc.',
            'type': 'institution',
            'role': 'intermediary',
            'tier_level': 2,
            'jurisdiction': 'United States',
            'assets_under_management': 4500000000000,  # 4.5万亿美元
            'market_influence_score': 9.2,
            'risk_profile': {
                'risk_tolerance': 'medium_high',
                'decision_horizon': 'medium_term',
                'information_advantage': 'strong',
                'client_base': 'institutional'
            }
        },
        
        {
            'participant_id': 'JP_MORGAN',
            'name': 'JPMorgan Chase & Co.',
            'type': 'institution',
            'role': 'intermediary',
            'tier_level': 2,
            'jurisdiction': 'United States',
            'assets_under_management': 3900000000000,  # 3.9万亿美元
            'market_influence_score': 9.0,
            'risk_profile': {
                'risk_tolerance': 'medium',
                'decision_horizon': 'long_term',
                'information_advantage': 'strong',
                'business_segments': ['commercial_banking', 'investment_banking', 'asset_management']
            }
        },
        
        # 资产管理公司
        {
            'participant_id': 'BLACKROCK',
            'name': 'BlackRock Inc.',
            'type': 'institution',
            'role': 'intermediary',
            'tier_level': 2,
            'jurisdiction': 'United States',
            'assets_under_management': 10000000000000,  # 10万亿美元
            'market_influence_score': 9.5,
            'risk_profile': {
                'risk_tolerance': 'low_medium',
                'decision_horizon': 'long_term',
                'technology_advantage': 'leading',
                'product_range': 'comprehensive'
            }
        },
        
        {
            'participant_id': 'VANGUARD',
            'name': 'The Vanguard Group',
            'type': 'institution',
            'role': 'intermediary',
            'tier_level': 3,
            'jurisdiction': 'United States',
            'assets_under_management': 7500000000000,  # 7.5万亿美元
            'market_influence_score': 8.8,
            'risk_profile': {
                'risk_tolerance': 'low',
                'decision_horizon': 'very_long_term',
                'cost_advantage': 'significant',
                'client_focus': 'retail_investors'
            }
        },
        
        # 对冲基金
        {
            'participant_id': 'BRIDGEWATER',
            'name': 'Bridgewater Associates',
            'type': 'institution',
            'role': 'intermediary',
            'tier_level': 3,
            'jurisdiction': 'United States',
            'assets_under_management': 231000000000,  # 2310亿美元
            'market_influence_score': 8.5,
            'risk_profile': {
                'risk_tolerance': 'high',
                'decision_horizon': 'medium_term',
                'research_capability': 'world_class',
                'strategy_focus': 'macro_hedge_fund'
            }
        },
        
        # 主权财富基金
        {
            'participant_id': 'SAUDI_PIF',
            'name': 'Public Investment Fund of Saudi Arabia',
            'type': 'government',
            'role': 'investor',
            'tier_level': 2,
            'jurisdiction': 'Saudi Arabia',
            'assets_under_management': 620000000000,  # 6200亿美元
            'market_influence_score': 8.0,
            'risk_profile': {
                'risk_tolerance': 'medium',
                'decision_horizon': 'very_long_term',
                'strategic_focus': 'economic_diversification',
                'geographic_diversity': 'global'
            }
        },
        
        # 科技巨头
        {
            'participant_id': 'APPLE_INC',
            'name': 'Apple Inc.',
            'type': 'institution',
            'role': 'producer',
            'tier_level': 2,
            'jurisdiction': 'United States',
            'assets_under_management': 351000000000,  # 3510亿美元现金储备
            'market_influence_score': 9.3,
            'risk_profile': {
                'risk_tolerance': 'low_medium',
                'decision_horizon': 'long_term',
                'innovation_capacity': 'leading',
                'market_position': 'dominant'
            }
        },
        
        {
            'participant_id': 'MICROSOFT',
            'name': 'Microsoft Corporation',
            'type': 'institution',
            'role': 'producer',
            'tier_level': 3,
            'jurisdiction': 'United States',
            'assets_under_management': 166000000000,  # 1660亿美元现金储备
            'market_influence_score': 8.7,
            'risk_profile': {
                'risk_tolerance': 'medium',
                'decision_horizon': 'long_term',
                'cloud_computing_lead': True,
                'enterprise_focus': 'strong'
            }
        },
        
        # 能源公司
        {
            'participant_id': 'ARAMCO',
            'name': 'Saudi Aramco',
            'type': 'institution',
            'role': 'producer',
            'tier_level': 2,
            'jurisdiction': 'Saudi Arabia',
            'assets_under_management': 350000000000,  # 3500亿美元市值
            'market_influence_score': 8.2,
            'risk_profile': {
                'risk_tolerance': 'medium',
                'decision_horizon': 'long_term',
                'resource_control': 'monopoly',
                'geopolitical_exposure': 'high'
            }
        }
    ]
    
    # 插入数据
    for participant in major_participants:
        cursor.execute('''
            INSERT OR REPLACE INTO participants_profile 
            (participant_id, name, type, role, tier_level, jurisdiction, 
             assets_under_management, market_influence_score, risk_profile)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            participant['participant_id'],
            participant['name'],
            participant['type'],
            participant['role'],
            participant['tier_level'],
            participant['jurisdiction'],
            participant['assets_under_management'],
            participant['market_influence_score'],
            json.dumps(participant['risk_profile'])
        ))
    
    # 提交更改
    conn.commit()
    
    # 验证插入结果
    cursor.execute('SELECT COUNT(*) FROM participants_profile')
    count = cursor.fetchone()[0]
    print(f"成功初始化 {count} 个参与者档案")
    
    # 显示样本数据
    cursor.execute('''
        SELECT participant_id, name, type, role, tier_level, 
               assets_under_management, market_influence_score 
        FROM participants_profile 
        ORDER BY market_influence_score DESC 
        LIMIT 5
    ''')
    
    print("\n影响力排名前5的参与者:")
    print("-" * 80)
    for row in cursor.fetchall():
        print(f"ID: {row[0]:<20} 名称: {row[1]:<25} 影响力得分: {row[6]:.1f}")
    
    # 关闭连接
    conn.close()

def create_sample_events():
    """创建样本历史事件"""
    
    conn = sqlite3.connect('sandbox_data.db')
    cursor = conn.cursor()
    
    sample_events = [
        {
            'event_id': 'dotcom_bubble_2000',
            'event_date': '2000-03-10',
            'event_type': 'market',
            'description': '互联网泡沫破裂，纳斯达克指数从高点下跌78%',
            'impact_score': 8.5,
            'affected_participants': ['Tech_Companies', 'Venture_Capital', 'Retail_Investors'],
            'data_sources': ['NASDAQ_records', 'SEC_filings', 'Academic_studies'],
            'verified': True
        },
        {
            'event_id': 'subprime_crisis_2007',
            'event_date': '2007-02-01',
            'event_type': 'crisis',
            'description': '次贷危机开始显现，房价下跌引发连锁反应',
            'impact_score': 9.0,
            'affected_participants': ['Banks', 'Insurance_Companies', 'Real_Estate'],
            'data_sources': ['Fed_reports', 'FHFA_data', 'News_analysis'],
            'verified': True
        },
        {
            'event_id': 'quantitative_easing_2008',
            'event_date': '2008-11-25',
            'event_type': 'policy',
            'description': '美联储宣布第一轮量化宽松政策，购买MBS和长期国债',
            'impact_score': 8.8,
            'affected_participants': ['Federal_Reserve', 'Major_Banks', 'Bond_Market'],
            'data_sources': ['FOMC_statements', 'Fed_balance_sheet', 'Market_data'],
            'verified': True
        },
        {
            'event_id': 'oil_price_crash_2014',
            'event_date': '2014-06-01',
            'event_type': 'commodity',
            'description': '国际油价从115美元暴跌至40美元以下',
            'impact_score': 7.5,
            'affected_participants': ['Oil_Companies', 'Energy_Sector', 'Exporting_Countries'],
            'data_sources': ['EIA_data', 'IMF_commodity_prices', 'Industry_reports'],
            'verified': True
        },
        {
            'event_id': 'covid_pandemic_2020',
            'event_date': '2020-03-11',
            'event_type': 'crisis',
            'description': '新冠疫情全球大流行，金融市场剧烈震荡',
            'impact_score': 9.2,
            'affected_participants': ['Global_Economy', 'Healthcare', 'Travel_Industry'],
            'data_sources': ['WHO_reports', 'Government_data', 'Market_indices'],
            'verified': True
        }
    ]
    
    for event in sample_events:
        cursor.execute('''
            INSERT OR REPLACE INTO historical_events 
            (event_id, event_date, event_type, description, impact_score, 
             affected_participants, data_sources, verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event['event_id'],
            event['event_date'],
            event['event_type'],
            event['description'],
            event['impact_score'],
            json.dumps(event['affected_participants']),
            json.dumps(event['data_sources']),
            event['verified']
        ))
    
    conn.commit()
    print(f"\n成功创建 {len(sample_events)} 个样本历史事件")
    conn.close()

if __name__ == "__main__":
    print("开始初始化沙盘系统数据库...")
    initialize_participants_database()
    create_sample_events()
    print("数据库初始化完成！")