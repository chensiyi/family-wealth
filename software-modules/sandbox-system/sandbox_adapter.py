#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
沙盘系统数据库适配器
将数据收集器的数据库结构转换为沙盘系统期待的格式
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional

class SandboxDataAdapter:
    """沙盘数据适配器"""
    
    def __init__(self, db_path: str = '../data-collector/storage/family_wealth_professional.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
    
    def get_participants_profile(self) -> List[Dict]:
        """获取参与者档案数据（从现有数据转换）"""
        # 由于原始数据库没有participants_profile表，我们需要从其他表推断参与者信息
        participants = []
        
        # 从investor_behavior_tracking表提取参与者信息
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT DISTINCT participant_id,
                   COUNT(*) as total_actions,
                   SUM(total_amount) as total_investment,
                   AVG(confidence_level) as avg_confidence
            FROM investor_behavior_tracking
            GROUP BY participant_id
        ''')
        
        rows = cursor.fetchall()
        
        for i, row in enumerate(rows):
            participants.append({
                'participant_id': row['participant_id'],
                'name': f"Investor_{row['participant_id']}",
                'type': 'institutional' if row['total_investment'] > 1000000 else 'individual',
                'role': 'investor',
                'tier_level': 1,
                'jurisdiction': 'US',
                'assets_under_management': float(row['total_investment'] or 0),
                'market_influence_score': min(100, float(row['total_actions'] or 0) * 2),
                'risk_profile': 'moderate',
                'created_at': datetime.now().isoformat()
            })
        
        # 如果没有参与者数据，创建一些示例数据
        if not participants:
            sample_participants = [
                {
                    'participant_id': 'FED',
                    'name': 'Federal Reserve',
                    'type': 'central_bank',
                    'role': 'monetary_authority',
                    'tier_level': 1,
                    'jurisdiction': 'US',
                    'assets_under_management': 8000000000000,  # 8万亿美元
                    'market_influence_score': 100,
                    'risk_profile': 'systemic',
                    'created_at': datetime.now().isoformat()
                },
                {
                    'participant_id': 'JPM',
                    'name': 'JPMorgan Chase',
                    'type': 'commercial_bank',
                    'role': 'financial_intermediary',
                    'tier_level': 2,
                    'jurisdiction': 'US',
                    'assets_under_management': 3700000000000,  # 3.7万亿美元
                    'market_influence_score': 95,
                    'risk_profile': 'conservative',
                    'created_at': datetime.now().isoformat()
                }
            ]
            participants.extend(sample_participants)
        
        return participants
    
    def get_historical_events(self) -> List[Dict]:
        """获取历史事件数据"""
        cursor = self.conn.cursor()
        
        # 从crisis_event_analysis表获取危机事件
        cursor.execute('''
            SELECT event_id, event_name, event_date, event_category,
                   severity_level, affected_markets, trigger_symbols,
                   market_reaction_data, duration_days, recovery_period_days
            FROM crisis_event_analysis
            WHERE verified = TRUE
            ORDER BY event_date DESC
        ''')
        
        events = []
        rows = cursor.fetchall()
        
        for row in rows:
            events.append({
                'event_id': row['event_id'],
                'event_date': row['event_date'],
                'event_type': row['event_category'],
                'description': row['event_name'],
                'impact_score': float(row['severity_level'] or 5),
                'affected_participants': row['affected_markets'] or '[]',
                'trigger_symbols': row['trigger_symbols'] or '[]',
                'market_reaction': row['market_reaction_data'] or '{}',
                'duration_days': row['duration_days'] or 0,
                'recovery_days': row['recovery_period_days'] or 0
            })
        
        # 如果没有事件数据，创建一些示例事件
        if not events:
            sample_events = [
                {
                    'event_id': 'COVID-19',
                    'event_date': '2020-03-15',
                    'event_type': 'pandemic',
                    'description': '新冠疫情全球爆发',
                    'impact_score': 9,
                    'affected_participants': json.dumps(['FED', 'JPM', 'BlackRock']),
                    'trigger_symbols': json.dumps(['SPY', 'TLT', 'GLD']),
                    'market_reaction': json.dumps({'SPY': -30, 'TLT': 15, 'GLD': 25}),
                    'duration_days': 274,
                    'recovery_days': 180
                },
                {
                    'event_id': 'INFLATION-2022',
                    'event_date': '2022-01-15',
                    'event_type': 'financial',
                    'description': '通胀担忧加剧',
                    'impact_score': 7,
                    'affected_participants': json.dumps(['FED', 'Vanguard']),
                    'trigger_symbols': json.dumps(['SPY', 'TIP', 'DBC']),
                    'market_reaction': json.dumps({'SPY': -15, 'TIP': 12, 'DBC': 20}),
                    'duration_days': 180,
                    'recovery_days': 90
                }
            ]
            events.extend(sample_events)
        
        return events
    
    def get_decision_actions(self) -> List[Dict]:
        """获取决策行为数据"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT participant_id, decision_date, action_type, asset_symbol,
                   total_amount, portfolio_percentage, decision_rationale,
                   confidence_level, actual_return
            FROM investor_behavior_tracking
            ORDER BY decision_date DESC
        ''')
        
        actions = []
        rows = cursor.fetchall()
        
        for row in rows:
            actions.append({
                'action_id': f"{row['participant_id']}_{row['decision_date']}_{row['asset_symbol']}",
                'participant_id': row['participant_id'],
                'event_id': 'MANUAL_ENTRY',  # 手动录入标识
                'decision_timestamp': row['decision_date'],
                'action_type': row['action_type'],
                'asset_symbol': row['asset_symbol'],
                'amount': float(row['total_amount'] or 0),
                'portfolio_percentage': float(row['portfolio_percentage'] or 0),
                'confidence_level': row['confidence_level'] or 5,
                'rationale': row['decision_rationale'] or '',
                'actual_performance': row['actual_return'] or 0,
                'benchmark_return': 0.0  # 默认基准回报
            })
        
        return actions
    
    def create_sandbox_views(self):
        """创建沙盘系统所需的视图"""
        cursor = self.conn.cursor()
        
        # 创建参与者档案表（如果不存在）
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
                created_at TEXT
            )
        ''')
        
        # 插入参与者数据
        participants = self.get_participants_profile()
        for p in participants:
            cursor.execute('''
                INSERT OR REPLACE INTO participants_profile 
                (participant_id, name, type, role, tier_level, jurisdiction,
                 assets_under_management, market_influence_score, risk_profile, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                p['participant_id'], p['name'], p['type'], p['role'], p['tier_level'],
                p['jurisdiction'], p['assets_under_management'], p['market_influence_score'],
                p['risk_profile'], p['created_at']
            ))
        
        # 创建历史事件表（如果不存在）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historical_events (
                event_id TEXT PRIMARY KEY,
                event_date TEXT NOT NULL,
                event_type TEXT NOT NULL,
                description TEXT NOT NULL,
                impact_score REAL,
                affected_participants TEXT,
                trigger_symbols TEXT,
                market_reaction TEXT,
                duration_days INTEGER,
                recovery_days INTEGER
            )
        ''')
        
        # 插入事件数据
        events = self.get_historical_events()
        for e in events:
            cursor.execute('''
                INSERT OR REPLACE INTO historical_events
                (event_id, event_date, event_type, description, impact_score,
                 affected_participants, trigger_symbols, market_reaction, duration_days, recovery_days)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                e['event_id'], e['event_date'], e['event_type'], e['description'],
                e['impact_score'], e['affected_participants'], e['trigger_symbols'],
                e['market_reaction'], e['duration_days'], e['recovery_days']
            ))
        
        # 创建决策行为表（如果不存在）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS decision_actions (
                action_id TEXT PRIMARY KEY,
                participant_id TEXT NOT NULL,
                event_id TEXT,
                decision_timestamp TEXT NOT NULL,
                action_type TEXT NOT NULL,
                asset_symbol TEXT,
                amount REAL,
                portfolio_percentage REAL,
                confidence_level INTEGER,
                rationale TEXT,
                actual_performance REAL,
                benchmark_return REAL
            )
        ''')
        
        # 插入行为数据
        actions = self.get_decision_actions()
        for a in actions:
            cursor.execute('''
                INSERT OR REPLACE INTO decision_actions
                (action_id, participant_id, event_id, decision_timestamp, action_type,
                 asset_symbol, amount, portfolio_percentage, confidence_level,
                 rationale, actual_performance, benchmark_return)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                a['action_id'], a['participant_id'], a['event_id'], a['decision_timestamp'],
                a['action_type'], a['asset_symbol'], a['amount'], a['portfolio_percentage'],
                a['confidence_level'], a['rationale'], a['actual_performance'], a['benchmark_return']
            ))
        
        self.conn.commit()
        print("✅ 沙盘系统视图创建完成")

# 测试适配器
if __name__ == "__main__":
    adapter = SandboxDataAdapter()
    adapter.create_sandbox_views()
    print("✅ 数据库适配器测试完成")