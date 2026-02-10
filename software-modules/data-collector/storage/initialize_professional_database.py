#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专业金融数据库初始化脚本
基于炒股软件数据模型设计
"""

import sqlite3
import json
import logging
from datetime import datetime, date
from typing import List, Dict, Optional
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('database_init.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProfessionalFinanceDatabase:
    """专业金融数据库管理器"""
    
    def __init__(self, db_path: str = 'professional_finance.db'):
        self.db_path = db_path
        self.connection = None
        self._connect()
        self._initialize_schema()
    
    def _connect(self):
        """建立数据库连接"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # 使结果可以通过列名访问
            logger.info(f"✅ 成功连接到数据库: {self.db_path}")
        except Exception as e:
            logger.error(f"❌ 数据库连接失败: {e}")
            raise
    
    def _initialize_schema(self):
        """初始化数据库表结构"""
        logger.info("🚀 开始初始化数据库表结构...")
        
        # 1. 市场数据表
        self._create_market_data_table()
        
        # 2. 宏观经济指标表
        self._create_economic_indicators_table()
        
        # 3. 资产配置历史表
        self._create_asset_allocation_table()
        
        # 4. 税收政策历史表
        self._create_tax_policy_table()
        
        # 5. 危机事件分析表
        self._create_crisis_analysis_table()
        
        # 6. 投资者行为追踪表
        self._create_investor_behavior_table()
        
        # 7. 数据源元信息表
        self._create_data_source_table()
        
        # 8. 创建索引
        self._create_indexes()
        
        # 9. 创建视图
        self._create_views()
        
        # 10. 创建触发器
        self._create_triggers()
        
        logger.info("✅ 数据库表结构初始化完成")
    
    def _create_market_data_table(self):
        """创建市场数据表"""
        sql = """
        CREATE TABLE IF NOT EXISTS market_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            date DATE NOT NULL,
            open_price REAL,
            high_price REAL,
            low_price REAL,
            close_price REAL NOT NULL,
            volume INTEGER,
            adjusted_close REAL,
            dividend REAL DEFAULT 0,
            split_coefficient REAL DEFAULT 1,
            source TEXT NOT NULL,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_quality_score REAL DEFAULT 1.0,
            UNIQUE(symbol, date)
        )
        """
        self.connection.execute(sql)
        logger.info("✅ 市场数据表创建完成")
    
    def _create_economic_indicators_table(self):
        """创建宏观经济指标表"""
        sql = """
        CREATE TABLE IF NOT EXISTS economic_indicators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            indicator_name TEXT NOT NULL,
            country_code TEXT DEFAULT 'US',
            date DATE NOT NULL,
            value REAL NOT NULL,
            previous_value REAL,
            forecast_value REAL,
            unit TEXT,
            frequency TEXT CHECK(frequency IN ('daily', 'weekly', 'monthly', 'quarterly', 'yearly')),
            source TEXT NOT NULL,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reliability_score REAL DEFAULT 1.0,
            UNIQUE(indicator_name, country_code, date)
        )
        """
        self.connection.execute(sql)
        logger.info("✅ 宏观经济指标表创建完成")
    
    def _create_asset_allocation_table(self):
        """创建资产配置历史表"""
        sql = """
        CREATE TABLE IF NOT EXISTS asset_allocation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            portfolio_id TEXT NOT NULL,
            date DATE NOT NULL,
            asset_class TEXT NOT NULL,
            allocation_percentage REAL NOT NULL,
            market_value REAL NOT NULL,
            cost_basis REAL,
            unrealized_gain_loss REAL,
            currency TEXT DEFAULT 'USD',
            rebalance_reason TEXT,
            strategy_reference TEXT,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(portfolio_id, asset_class, date)
        )
        """
        self.connection.execute(sql)
        logger.info("✅ 资产配置历史表创建完成")
    
    def _create_tax_policy_table(self):
        """创建税收政策历史表"""
        sql = """
        CREATE TABLE IF NOT EXISTS tax_policy_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            policy_type TEXT NOT NULL,
            jurisdiction TEXT NOT NULL,
            effective_date DATE NOT NULL,
            expiration_date DATE,
            rate_percentage REAL,
            rate_type TEXT CHECK(rate_type IN ('flat', 'progressive', 'regressive')),
            exemption_amount REAL,
            deduction_limit REAL,
            policy_description TEXT,
            source_document TEXT,
            verified BOOLEAN DEFAULT FALSE,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(policy_type, jurisdiction, effective_date)
        )
        """
        self.connection.execute(sql)
        logger.info("✅ 税收政策历史表创建完成")
    
    def _create_crisis_analysis_table(self):
        """创建危机事件分析表"""
        sql = """
        CREATE TABLE IF NOT EXISTS crisis_event_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT NOT NULL UNIQUE,
            event_name TEXT NOT NULL,
            event_date DATE NOT NULL,
            event_category TEXT CHECK(event_category IN ('financial', 'political', 'natural_disaster', 'pandemic', 'geopolitical')),
            severity_level INTEGER CHECK(severity_level BETWEEN 1 AND 10),
            affected_markets TEXT,
            trigger_symbols TEXT,
            market_reaction_data TEXT,
            duration_days INTEGER,
            recovery_period_days INTEGER,
            economic_impact_estimate REAL,
            data_sources TEXT,
            analysis_notes TEXT,
            verified BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.connection.execute(sql)
        logger.info("✅ 危机事件分析表创建完成")
    
    def _create_investor_behavior_table(self):
        """创建投资者行为追踪表"""
        sql = """
        CREATE TABLE IF NOT EXISTS investor_behavior_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            participant_id TEXT NOT NULL,
            decision_date DATE NOT NULL,
            action_type TEXT CHECK(action_type IN ('buy', 'sell', 'hold', 'hedge', 'diversify')),
            asset_symbol TEXT,
            quantity REAL,
            price_per_unit REAL,
            total_amount REAL,
            portfolio_percentage REAL,
            decision_rationale TEXT,
            market_conditions TEXT,
            risk_assessment TEXT,
            confidence_level INTEGER CHECK(confidence_level BETWEEN 1 AND 10),
            outcome_measured BOOLEAN DEFAULT FALSE,
            actual_return REAL,
            benchmark_comparison REAL,
            measured_at DATE,
            performance_notes TEXT,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.connection.execute(sql)
        logger.info("✅ 投资者行为追踪表创建完成")
    
    def _create_data_source_table(self):
        """创建数据源元信息表"""
        sql = """
        CREATE TABLE IF NOT EXISTS data_source_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_name TEXT NOT NULL UNIQUE,
            source_type TEXT CHECK(source_type IN ('official', 'financial', 'alternative', 'news')),
            base_url TEXT,
            api_endpoint TEXT,
            authentication_required BOOLEAN DEFAULT FALSE,
            auth_method TEXT,
            rate_limit INTEGER,
            data_format TEXT CHECK(data_format IN ('json', 'csv', 'xml', 'api')),
            last_accessed TIMESTAMP,
            success_rate REAL DEFAULT 1.0,
            average_response_time REAL,
            reliability_score REAL DEFAULT 1.0,
            supported_indicators TEXT,
            contact_info TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.connection.execute(sql)
        logger.info("✅ 数据源元信息表创建完成")
    
    def _create_indexes(self):
        """创建索引优化查询性能"""
        indexes = [
            # 市场数据索引
            "CREATE INDEX IF NOT EXISTS idx_market_symbol_date ON market_data(symbol, date)",
            "CREATE INDEX IF NOT EXISTS idx_market_date ON market_data(date)",
            "CREATE INDEX IF NOT EXISTS idx_market_source ON market_data(source)",
            
            # 宏观经济指标索引
            "CREATE INDEX IF NOT EXISTS idx_econ_indicator_date ON economic_indicators(indicator_name, date)",
            "CREATE INDEX IF NOT EXISTS idx_econ_country_date ON economic_indicators(country_code, date)",
            
            # 资产配置索引
            "CREATE INDEX IF NOT EXISTS idx_allocation_portfolio_date ON asset_allocation_history(portfolio_id, date)",
            "CREATE INDEX IF NOT EXISTS idx_allocation_asset_date ON asset_allocation_history(asset_class, date)",
            
            # 税收政策索引
            "CREATE INDEX IF NOT EXISTS idx_tax_jurisdiction_date ON tax_policy_history(jurisdiction, effective_date)",
            "CREATE INDEX IF NOT EXISTS idx_tax_type_date ON tax_policy_history(policy_type, effective_date)",
            
            # 危机事件索引
            "CREATE INDEX IF NOT EXISTS idx_crisis_date_severity ON crisis_event_analysis(event_date, severity_level)",
            "CREATE INDEX IF NOT EXISTS idx_crisis_category ON crisis_event_analysis(event_category)",
            
            # 投资者行为索引
            "CREATE INDEX IF NOT EXISTS idx_behavior_participant_date ON investor_behavior_tracking(participant_id, decision_date)",
            "CREATE INDEX IF NOT EXISTS idx_behavior_action_date ON investor_behavior_tracking(action_type, decision_date)",
            "CREATE INDEX IF NOT EXISTS idx_behavior_symbol_date ON investor_behavior_tracking(asset_symbol, decision_date)"
        ]
        
        for index_sql in indexes:
            self.connection.execute(index_sql)
        
        logger.info("✅ 数据库索引创建完成")
    
    def _create_views(self):
        """创建常用查询视图"""
        views = [
            # 综合行情视图
            """
            CREATE VIEW IF NOT EXISTS market_overview_view AS
            SELECT 
                md.symbol,
                md.date,
                md.close_price,
                md.volume,
                md.adjusted_close,
                ei.indicator_name,
                ei.value as indicator_value,
                ROW_NUMBER() OVER (PARTITION BY md.symbol ORDER BY md.date DESC) as rn
            FROM market_data md
            LEFT JOIN economic_indicators ei ON md.date = ei.date
            WHERE md.date >= date('now', '-30 days')
            ORDER BY md.symbol, md.date DESC
            """,
            
            # 资产配置分析视图
            """
            CREATE VIEW IF NOT EXISTS asset_allocation_analysis AS
            SELECT 
                aah.portfolio_id,
                aah.asset_class,
                aah.date,
                aah.allocation_percentage,
                aah.market_value,
                LAG(aah.allocation_percentage) OVER (
                    PARTITION BY aah.portfolio_id, aah.asset_class 
                    ORDER BY aah.date
                ) as previous_allocation,
                aah.allocation_percentage - LAG(aah.allocation_percentage) OVER (
                    PARTITION BY aah.portfolio_id, aah.asset_class 
                    ORDER BY aah.date
                ) as allocation_change,
                aah.rebalance_reason
            FROM asset_allocation_history aah
            WHERE aah.date >= date('now', '-1 year')
            """,
            
            # 危机影响分析视图
            """
            CREATE VIEW IF NOT EXISTS crisis_impact_analysis AS
            SELECT 
                cea.event_name,
                cea.event_date,
                cea.severity_level,
                cea.duration_days,
                cea.economic_impact_estimate,
                md.symbol,
                md.date,
                md.close_price,
                LAG(md.close_price, 5) OVER (
                    PARTITION BY md.symbol 
                    ORDER BY md.date
                ) as pre_crisis_price,
                ((md.close_price - LAG(md.close_price, 5) OVER (
                    PARTITION BY md.symbol 
                    ORDER BY md.date
                )) / LAG(md.close_price, 5) OVER (
                    PARTITION BY md.symbol 
                    ORDER BY md.date
                )) * 100 as price_change_percent
            FROM crisis_event_analysis cea
            JOIN market_data md ON md.date BETWEEN 
                date(cea.event_date) AND 
                date(cea.event_date, '+5 days')
            ORDER BY cea.event_date DESC, md.symbol
            """
        ]
        
        for view_sql in views:
            self.connection.execute(view_sql)
        
        logger.info("✅ 数据库视图创建完成")
    
    def _create_triggers(self):
        """创建触发器维护数据一致性"""
        triggers = [
            # 自动更新时间戳
            """
            CREATE TRIGGER IF NOT EXISTS update_market_data_timestamp 
            AFTER UPDATE ON market_data
            BEGIN
                UPDATE market_data SET fetched_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END
            """,
            
            # 数据质量评分自动计算
            """
            CREATE TRIGGER IF NOT EXISTS calculate_data_quality
            AFTER INSERT ON market_data
            BEGIN
                UPDATE market_data 
                SET data_quality_score = CASE 
                    WHEN NEW.source IN ('FRED', 'Yahoo Finance', 'SEC') THEN 0.95
                    WHEN NEW.source LIKE '%official%' THEN 0.9
                    ELSE 0.7
                END
                WHERE id = NEW.id;
            END
            """,
            
            # 自动更新数据源访问时间
            """
            CREATE TRIGGER IF NOT EXISTS update_source_access_time
            AFTER INSERT ON market_data
            BEGIN
                UPDATE data_source_metadata 
                SET last_accessed = CURRENT_TIMESTAMP,
                    success_rate = (success_rate * 0.9 + 1.0 * 0.1)
                WHERE source_name = NEW.source;
            END
            """
        ]
        
        for trigger_sql in triggers:
            self.connection.execute(trigger_sql)
        
        logger.info("✅ 数据库触发器创建完成")
    
    def insert_sample_data(self):
        """插入示例数据用于测试"""
        logger.info("📊 开始插入示例数据...")
        
        # 1. 插入数据源信息
        data_sources = [
            ('FRED', 'official', 'https://fred.stlouisfed.org', '/api', False, 'api', 120, 'api', 0.98, 0.2, 'GDP,UNRATE,CPI'),
            ('Yahoo Finance', 'financial', 'https://finance.yahoo.com', '/v8/finance/chart', False, 'api', 2000, 'json', 0.95, 0.1, '^GSPC,AAPL,GOOGL'),
            ('SEC EDGAR', 'official', 'https://www.sec.gov', '/api', True, 'api_key', 10, 'json', 0.99, 0.5, '10-K,10-Q,13F')
        ]
        
        for source in data_sources:
            self.connection.execute("""
                INSERT OR IGNORE INTO data_source_metadata 
                (source_name, source_type, base_url, api_endpoint, authentication_required, 
                 auth_method, rate_limit, data_format, reliability_score, average_response_time, supported_indicators)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, source)
        
        # 2. 插入宏观经济指标示例数据
        economic_data = [
            ('GDP', 'US', '2023-12-01', 22000.0, 21800.0, 22200.0, 'Billions USD', 'quarterly', 'FRED'),
            ('UNRATE', 'US', '2023-12-01', 3.7, 3.8, 3.6, 'Percent', 'monthly', 'FRED'),
            ('CPI', 'US', '2023-12-01', 315.0, 312.0, 318.0, 'Index', 'monthly', 'FRED')
        ]
        
        for data in economic_data:
            self.connection.execute("""
                INSERT OR IGNORE INTO economic_indicators 
                (indicator_name, country_code, date, value, previous_value, forecast_value, unit, frequency, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, data)
        
        # 3. 插入市场数据示例
        market_data_samples = [
            ('^GSPC', '2024-01-15', 4800.0, 4850.0, 4780.0, 4820.0, 3500000000, 4820.0, 0, 1, 'Yahoo Finance'),
            ('AAPL', '2024-01-15', 185.5, 187.2, 184.8, 186.3, 45000000, 186.3, 0, 1, 'Yahoo Finance'),
            ('GOOGL', '2024-01-15', 142.8, 144.5, 141.2, 143.7, 28000000, 143.7, 0, 1, 'Yahoo Finance')
        ]
        
        for data in market_data_samples:
            self.connection.execute("""
                INSERT OR IGNORE INTO market_data 
                (symbol, date, open_price, high_price, low_price, close_price, volume, adjusted_close, dividend, split_coefficient, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, data)
        
        # 4. 插入危机事件示例数据
        crisis_events = [
            ('2008_subprime_crisis', '2008年次贷危机', '2008-09-15', 'financial', 9, 
             '["US","EU","Global"]', '["^GSPC","BKLN","XLF"]', 
             '{"price_drop": -50, "volatility_spike": 80}', 365, 730, -2000.0,
             '["SEC filings","Fed records","News reports"]', '雷曼兄弟破产引发的全球金融危机')
        ]
        
        for event in crisis_events:
            self.connection.execute("""
                INSERT OR IGNORE INTO crisis_event_analysis 
                (event_id, event_name, event_date, event_category, severity_level, 
                 affected_markets, trigger_symbols, market_reaction_data, duration_days, 
                 recovery_period_days, economic_impact_estimate, data_sources, analysis_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, event)
        
        self.connection.commit()
        logger.info("✅ 示例数据插入完成")
    
    def get_database_stats(self) -> Dict:
        """获取数据库统计信息"""
        stats = {}
        
        # 获取各表记录数
        tables = ['market_data', 'economic_indicators', 'asset_allocation_history', 
                 'tax_policy_history', 'crisis_event_analysis', 'investor_behavior_tracking', 
                 'data_source_metadata']
        
        for table in tables:
            try:
                cursor = self.connection.execute(f"SELECT COUNT(*) as count FROM {table}")
                count = cursor.fetchone()['count']
                stats[table] = count
            except:
                stats[table] = 0
        
        # 获取数据库大小
        if os.path.exists(self.db_path):
            stats['database_size_mb'] = round(os.path.getsize(self.db_path) / (1024 * 1024), 2)
        
        return stats
    
    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            logger.info("🔒 数据库连接已关闭")

def main():
    """主函数"""
    try:
        # 初始化数据库
        db = ProfessionalFinanceDatabase('family_wealth_professional.db')
        
        # 插入示例数据
        db.insert_sample_data()
        
        # 显示数据库统计信息
        stats = db.get_database_stats()
        logger.info("📊 数据库统计信息:")
        for table, count in stats.items():
            if table != 'database_size_mb':
                logger.info(f"  {table}: {count} 条记录")
        logger.info(f"  数据库大小: {stats.get('database_size_mb', 0)} MB")
        
        # 测试查询
        logger.info("🔍 测试查询功能...")
        
        # 测试市场数据查询
        cursor = db.connection.execute("""
            SELECT symbol, date, close_price, volume 
            FROM market_data 
            ORDER BY date DESC, symbol 
            LIMIT 5
        """)
        results = cursor.fetchall()
        logger.info("📈 最新市场数据:")
        for row in results:
            logger.info(f"  {row['symbol']} | {row['date']} | ${row['close_price']} | {row['volume']:,}")
        
        # 测试视图查询
        cursor = db.connection.execute("SELECT * FROM market_overview_view LIMIT 3")
        view_results = cursor.fetchall()
        logger.info("👁️ 市场概览视图测试:")
        for row in view_results:
            logger.info(f"  {row['symbol']} | {row['date']} | ${row['close_price']}")
        
        db.close()
        logger.info("🎉 数据库初始化和测试完成!")
        
    except Exception as e:
        logger.error(f"❌ 数据库初始化过程中出现错误: {e}")
        raise

if __name__ == "__main__":
    main()