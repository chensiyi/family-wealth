#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
沙盘系统观察界面 - 复盘分析工具
提供多维度的观察视角和复盘功能
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import os

class SandboxObserver:
    """沙盘观察器 - 提供多种观察视角
    
    注意：此版本已集成数据中台模块，优先使用数据中台获取数据
    """
    
    def __init__(self, db_path: str = None, use_data_hub: bool = True):
        self.use_data_hub = use_data_hub
        
        if use_data_hub:
            # 使用数据中台适配器
            from utils.data_hub_adapter import create_sandbox_data_adapter
            self.data_adapter = create_sandbox_data_adapter()
            self.db_conn = None
        else:
            # 使用传统数据库连接
            import sqlite3
            self.db_path = db_path or 'sandbox_data.db'
            self.db_conn = sqlite3.connect(self.db_path)
            self.setup_views()
    
    def setup_views(self):
        """创建观察视图（传统模式）"""
        if not self.db_conn:
            return
            
        cursor = self.db_conn.cursor()
        
        # 创建参与者影响力排行榜视图
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS participant_rankings AS
            SELECT 
                participant_id,
                name,
                type,
                role,
                tier_level,
                assets_under_management,
                market_influence_score,
                RANK() OVER (ORDER BY market_influence_score DESC) as influence_rank,
                RANK() OVER (ORDER BY assets_under_management DESC) as asset_rank
            FROM participants_profile
        ''')
        
        # 创建事件影响分析视图
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS event_impact_analysis AS
            SELECT 
                he.event_id,
                he.event_date,
                he.event_type,
                he.description,
                he.impact_score,
                json_extract(he.affected_participants, '$') as affected_count,
                COUNT(da.action_id) as recorded_actions,
                AVG(da.amount) as avg_action_amount
            FROM historical_events he
            LEFT JOIN decision_actions da ON he.event_id = da.event_id
            GROUP BY he.event_id
        ''')
        
        # 创建参与者行为模式视图
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS participant_behavior_patterns AS
            SELECT 
                p.participant_id,
                p.name,
                p.role,
                COUNT(da.action_id) as total_actions,
                SUM(CASE WHEN da.action_type = 'investment' THEN 1 ELSE 0 END) as investment_count,
                SUM(CASE WHEN da.action_type = 'liquidity' THEN 1 ELSE 0 END) as liquidity_count,
                AVG(da.amount) as avg_action_size,
                MIN(da.decision_timestamp) as first_action,
                MAX(da.decision_timestamp) as last_action
            FROM participants_profile p
            LEFT JOIN decision_actions da ON p.participant_id = da.participant_id
            GROUP BY p.participant_id
        ''')
        
        self.db_conn.commit()
    
    def get_ecosystem_overview(self) -> Dict:
        """生态系统概览 - 鸟瞰视角"""
        if self.use_data_hub:
            # 使用数据中台获取数据
            return self._get_ecosystem_overview_from_data_hub()
        else:
            # 使用传统数据库
            return self._get_ecosystem_overview_from_db()
    
    def _get_ecosystem_overview_from_data_hub(self) -> Dict:
        """从数据中台获取生态系统概览"""
        try:
            # 获取市场数据作为基础
            market_data = self.data_adapter.get_financial_data(
                symbol='SPY',  # 使用标普500ETF作为市场代理
                data_type='prices',
                start_date='2020-01-01',
                end_date='2024-12-31'
            )
            
            # 获取经济指标
            economic_data = self.data_adapter.get_economic_indicators(
                indicators=['GDP', 'UNRATE', 'CPIAUCSL']
            )
            
            # 模拟参与者统计数据（实际应用中应从数据中台获取）
            total_participants = 50  # 模拟数据
            total_events = 25       # 模拟数据
            total_actions = 200     # 模拟数据
            
            return {
                'overview': {
                    'total_participants': total_participants,
                    'total_events': total_events,
                    'total_actions': total_actions,
                    'data_source': 'data_hub'
                },
                'market_data': market_data if market_data['success'] else None,
                'economic_indicators': economic_data if economic_data['success'] else None,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': f'数据中台获取失败: {str(e)}',
                'data_source': 'data_hub'
            }
    
    def _get_ecosystem_overview_from_db(self) -> Dict:
        """从传统数据库获取生态系统概览"""
        cursor = self.db_conn.cursor()
        
        # 参与者统计
        cursor.execute('SELECT COUNT(*) FROM participants_profile')
        total_participants = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM historical_events')
        total_events = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM decision_actions')
        total_actions = cursor.fetchone()[0]
        
        # 资产规模分布
        cursor.execute('''
            SELECT 
                role,
                COUNT(*) as count,
                SUM(assets_under_management) as total_assets
            FROM participants_profile
            GROUP BY role
            ORDER BY total_assets DESC
        ''')
        role_distribution = cursor.fetchall()
        
        # 影响力排名前5
        cursor.execute('''
            SELECT name, market_influence_score, assets_under_management
            FROM participant_rankings
            WHERE influence_rank <= 5
            ORDER BY influence_rank
        ''')
        top_influencers = cursor.fetchall()
        
        return {
            'overview': {
                'total_participants': total_participants,
                'total_events': total_events,
                'total_actions': total_actions,
                'data_source': 'local_db'
            },
            'role_distribution': [
                {
                    'role': row[0],
                    'count': row[1],
                    'total_assets': row[2]
                } for row in role_distribution
            ],
            'top_influencers': [
                {
                    'name': row[0],
                    'influence_score': row[1],
                    'assets': row[2]
                } for row in top_influencers
            ]
        }
    
    def get_timeline_view(self, start_date: str = None, end_date: str = None) -> List[Dict]:
        """时间线视角 - 按时间顺序观察事件发展"""
        cursor = self.conn.cursor()
        
        where_clause = ""
        params = []
        
        if start_date:
            where_clause += " AND event_date >= ?"
            params.append(start_date)
        
        if end_date:
            where_clause += " AND event_date <= ?"
            params.append(end_date)
        
        query = f'''
            SELECT 
                event_id,
                event_date,
                event_type,
                description,
                impact_score,
                affected_participants,
                (SELECT COUNT(*) FROM decision_actions WHERE event_id = he.event_id) as recorded_actions
            FROM historical_events he
            WHERE 1=1 {where_clause}
            ORDER BY event_date DESC
        '''
        
        cursor.execute(query, params)
        events = cursor.fetchall()
        
        return [
            {
                'event_id': row[0],
                'date': row[1],
                'type': row[2],
                'description': row[3],
                'impact_score': row[4],
                'affected_participants': json.loads(row[5]) if row[5] else [],
                'recorded_actions': row[6] or 0
            } for row in events
        ]
    
    def get_participant_drilldown(self, participant_id: str) -> Dict:
        """参与者钻取视角 - 深入分析单个参与者"""
        cursor = self.conn.cursor()
        
        # 基本信息
        cursor.execute('''
            SELECT participant_id, name, type, role, tier_level, jurisdiction,
                   assets_under_management, market_influence_score, risk_profile
            FROM participants_profile
            WHERE participant_id = ?
        ''', (participant_id,))
        
        basic_info = cursor.fetchone()
        if not basic_info:
            return {'error': 'Participant not found'}
        
        # 行为模式
        cursor.execute('''
            SELECT total_actions, investment_count, liquidity_count, 
                   avg_action_size, first_action, last_action
            FROM participant_behavior_patterns
            WHERE participant_id = ?
        ''', (participant_id,))
        
        behavior = cursor.fetchone()
        
        # 相关事件
        cursor.execute('''
            SELECT he.event_id, he.event_date, he.description, he.impact_score
            FROM historical_events he
            JOIN decision_actions da ON he.event_id = da.event_id
            WHERE da.participant_id = ?
            ORDER BY he.event_date DESC
        ''', (participant_id,))
        
        related_events = cursor.fetchall()
        
        # 风险画像
        risk_profile = json.loads(basic_info[8]) if basic_info[8] else {}
        
        return {
            'basic_info': {
                'id': basic_info[0],
                'name': basic_info[1],
                'type': basic_info[2],
                'role': basic_info[3],
                'tier': basic_info[4],
                'jurisdiction': basic_info[5],
                'assets': basic_info[6],
                'influence_score': basic_info[7]
            },
            'behavior_patterns': {
                'total_actions': behavior[0] if behavior else 0,
                'investment_actions': behavior[1] if behavior else 0,
                'liquidity_actions': behavior[2] if behavior else 0,
                'avg_action_size': behavior[3] if behavior else 0,
                'first_action': behavior[4] if behavior else None,
                'last_action': behavior[5] if behavior else None
            },
            'related_events': [
                {
                    'event_id': row[0],
                    'date': row[1],
                    'description': row[2],
                    'impact_score': row[3]
                } for row in related_events
            ],
            'risk_profile': risk_profile
        }
    
    def get_crisis_response_analysis(self, crisis_event_id: str) -> Dict:
        """危机响应分析视角 - 观察危机中的群体行为"""
        cursor = self.conn.cursor()
        
        # 危机基本信息
        cursor.execute('''
            SELECT event_id, event_date, description, impact_score
            FROM historical_events
            WHERE event_id = ?
        ''', (crisis_event_id,))
        
        crisis_info = cursor.fetchone()
        if not crisis_info:
            return {'error': 'Crisis event not found'}
        
        # 各参与者响应行为
        cursor.execute('''
            SELECT 
                p.name,
                p.role,
                p.market_influence_score,
                da.action_type,
                da.asset_class,
                da.amount,
                da.rationale,
                da.actual_outcome
            FROM decision_actions da
            JOIN participants_profile p ON da.participant_id = p.participant_id
            WHERE da.event_id = ?
            ORDER BY p.market_influence_score DESC
        ''', (crisis_event_id,))
        
        responses = cursor.fetchall()
        
        # 响应统计
        cursor.execute('''
            SELECT 
                action_type,
                COUNT(*) as count,
                AVG(amount) as avg_amount,
                SUM(amount) as total_amount
            FROM decision_actions
            WHERE event_id = ?
            GROUP BY action_type
        ''', (crisis_event_id,))
        
        action_stats = cursor.fetchall()
        
        return {
            'crisis_info': {
                'event_id': crisis_info[0],
                'date': crisis_info[1],
                'description': crisis_info[2],
                'impact_score': crisis_info[3]
            },
            'responses': [
                {
                    'participant': row[0],
                    'role': row[1],
                    'influence_score': row[2],
                    'action_type': row[3],
                    'asset_class': row[4],
                    'amount': row[5],
                    'rationale': row[6],
                    'outcome': json.loads(row[7]) if row[7] else None
                } for row in responses
            ],
            'action_statistics': [
                {
                    'action_type': row[0],
                    'count': row[1],
                    'avg_amount': row[2],
                    'total_amount': row[3]
                } for row in action_stats
            ]
        }
    
    def generate_crisis_narrative(self, crisis_event_id: str) -> str:
        """生成危机叙事报告"""
        analysis = self.get_crisis_response_analysis(crisis_event_id)
        
        if 'error' in analysis:
            return f"无法生成报告: {analysis['error']}"
        
        narrative = f"# {analysis['crisis_info']['description']} 复盘报告\n\n"
        narrative += f"**发生时间**: {analysis['crisis_info']['date']}\n"
        narrative += f"**影响程度**: {analysis['crisis_info']['impact_score']}/10\n\n"
        
        narrative += "## 参与者响应分析\n\n"
        
        for response in analysis['responses']:
            narrative += f"### {response['participant']} ({response['role']})\n"
            narrative += f"- **行动类型**: {response['action_type']}\n"
            narrative += f"- **涉及资产**: {response['asset_class']}\n"
            narrative += f"- **金额规模**: ${response['amount']:,.0f}\n"
            narrative += f"- **决策理由**: {response['rationale']}\n"
            
            if response['outcome']:
                narrative += f"- **实际结果**: {response['outcome'].get('short_term_impact', 'N/A')}\n"
                narrative += f"- **长期影响**: {response['outcome'].get('long_term_benefit', 'N/A')}\n"
            narrative += "\n"
        
        narrative += "## 行动统计汇总\n\n"
        for stat in analysis['action_statistics']:
            narrative += f"- **{stat['action_type']}**: {stat['count']}次行动，平均金额${stat['avg_amount']:,.0f}，总计${stat['total_amount']:,.0f}\n"
        
        return narrative

def main():
    """主函数 - 演示观察功能"""
    
    # 确保数据库存在
    if not os.path.exists('sandbox_data.db'):
        print("正在初始化数据库...")
        os.system('python scripts/initialize_database.py')
    
    observer = SandboxObserver()
    
    print("=== 家族财富管理沙盘观察系统 ===\n")
    
    # 1. 生态系统概览
    print("1. 🌍 生态系统概览")
    overview = observer.get_ecosystem_overview()
    print(f"   参与者总数: {overview['overview']['total_participants']}")
    print(f"   历史事件数: {overview['overview']['total_events']}")
    print(f"   记录行为数: {overview['overview']['total_actions']}")
    print("\n   角色分布:")
    for role in overview['role_distribution']:
        print(f"   - {role['role']}: {role['count']}个参与者，总资产${role['total_assets']/1e12:.1f}万亿美元")
    
    print("\n   影响力排名前5:")
    for influencer in overview['top_influencers']:
        print(f"   - {influencer['name']}: 影响力得分{influencer['influence_score']}, 资产${influencer['assets']/1e12:.1f}万亿美元")
    
    print("\n" + "="*50 + "\n")
    
    # 2. 时间线观察
    print("2. 📅 近期重大事件时间线")
    timeline = observer.get_timeline_view()
    for i, event in enumerate(timeline[:3]):  # 显示最近3个事件
        print(f"   {i+1}. {event['date']}: {event['description']}")
        print(f"      类型: {event['type']}, 影响得分: {event['impact_score']}")
        print(f"      涉及参与者: {len(event['affected_participants'])}个, 记录行为: {event['recorded_actions']}个")
        print()
    
    print("="*50 + "\n")
    
    # 3. 参与者深度分析
    print("3. 🔍 高盛集团深度分析")
    gs_analysis = observer.get_participant_drilldown('GOLDMAN_SACHS')
    if 'error' not in gs_analysis:
        info = gs_analysis['basic_info']
        behavior = gs_analysis['behavior_patterns']
        print(f"   基本信息: {info['name']} ({info['role']})")
        print(f"   资产规模: ${info['assets']/1e12:.1f}万亿美元")
        print(f"   影响力得分: {info['influence_score']}/10")
        print(f"   行为统计: 总计{behavior['total_actions']}个决策行为")
        print(f"   投资行为: {behavior['investment_actions']}次，流动性管理: {behavior['liquidity_actions']}次")
    
    print("\n" + "="*50 + "\n")
    
    # 4. 危机复盘分析
    print("4. 📊 2008年金融危机复盘")
    crisis_report = observer.generate_crisis_narrative('2008_lehman_bankruptcy')
    print(crisis_report)

if __name__ == "__main__":
    main()