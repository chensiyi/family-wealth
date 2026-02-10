#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动创建沙盘数据库表结构
"""

import sqlite3
import json

def create_database_tables():
    """手动创建数据库表"""
    conn = sqlite3.connect('sandbox_data.db')
    cursor = conn.cursor()
    
    # 创建参与者档案表
    cursor.execute('''
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
    cursor.execute('''
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
    cursor.execute('''
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
    
    # 插入样本参与者数据
    participants_data = [
        ('FEDERAL_RESERVE', 'Federal Reserve System', 'government', 'regulator', 1, 'United States', 8000000000000, 10.0, 
         '{"risk_tolerance": "high", "decision_horizon": "long_term", "information_advantage": "extreme"}'),
        ('GOLDMAN_SACHS', 'Goldman Sachs Group Inc.', 'institution', 'intermediary', 2, 'United States', 4500000000000, 9.2,
         '{"risk_tolerance": "medium_high", "decision_horizon": "medium_term", "information_advantage": "strong"}'),
        ('JP_MORGAN', 'JPMorgan Chase & Co.', 'institution', 'intermediary', 2, 'United States', 3900000000000, 9.0,
         '{"risk_tolerance": "medium", "decision_horizon": "long_term", "business_segments": ["commercial_banking", "investment_banking"]}')
    ]
    
    cursor.executemany('''
        INSERT OR REPLACE INTO participants_profile 
        (participant_id, name, type, role, tier_level, jurisdiction, 
         assets_under_management, market_influence_score, risk_profile)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', participants_data)
    
    # 插入样本事件数据
    events_data = [
        ('2008_lehman_bankruptcy', '2008-09-15', 'corporate', 
         '雷曼兄弟申请破产保护，引发全球金融危机', 9.5,
         '["Lehman Brothers", "Goldman Sachs", "JP Morgan"]',
         '["SEC filings", "Fed records"]', True),
        ('2008_tarp_approval', '2008-10-03', 'policy',
         '美国国会批准7000亿美元问题资产救助计划(TARP)', 8.0,
         '["US Treasury", "Major Banks"]',
         '["Congressional records"]', True)
    ]
    
    cursor.executemany('''
        INSERT OR REPLACE INTO historical_events 
        (event_id, event_date, event_type, description, impact_score, 
         affected_participants, data_sources, verified)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', events_data)
    
    # 插入样本行为数据
    actions_data = [
        ('gs_2008_short_covering', 'GOLDMAN_SACHS', '2008_lehman_bankruptcy', 
         '2008-09-16 09:30:00', 'liquidity', 'cash', 50000000000,
         '应对市场流动性危机，保护客户资产',
         '{"short_term_impact": "维持了市场信心", "long_term_benefit": "获得了竞争优势"}'),
        ('jpm_2008_washington_mutual_acquisition', 'JP_MORGAN', '2008_lehman_bankruptcy',
         '2008-09-25 18:00:00', 'investment', 'banking_assets', 19000000000,
         '以极低价格收购优质资产，扩大市场份额',
         '{"short_term_cost": "承担了整合风险", "long_term_gain": "成为美国最大银行"}')
    ]
    
    cursor.executemany('''
        INSERT OR REPLACE INTO decision_actions 
        (action_id, participant_id, event_id, decision_timestamp, action_type,
         asset_class, amount, rationale, actual_outcome)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', actions_data)
    
    conn.commit()
    conn.close()
    print("数据库表创建完成并填充样本数据")

if __name__ == "__main__":
    create_database_tables()