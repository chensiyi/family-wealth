#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专业金融数据库访问层
提供统一的数据访问接口，支持查询、分析和报表功能
"""

import sqlite3
import json
import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseAccessor:
    """数据库访问器"""
    
    def __init__(self, db_path: str = 'family_wealth_professional.db'):
        self.db_path = db_path
        self.connection = None
        self._connect()
    
    def _connect(self):
        """建立数据库连接"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            logger.info(f"✅ 数据库连接成功: {self.db_path}")
        except Exception as e:
            logger.error(f"❌ 数据库连接失败: {e}")
            raise
    
    def get_market_data(self, symbol: str, start_date: str = None, 
                       end_date: str = None, limit: int = None) -> List[Dict]:
        """获取指定标的的市场数据"""
        try:
            query = """
                SELECT symbol, date, open_price, high_price, low_price, 
                       close_price, volume, adjusted_close, source, fetched_at
                FROM market_data 
                WHERE symbol = ?
            """
            params = [symbol]
            
            if start_date:
                query += " AND date >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND date <= ?"
                params.append(end_date)
            
            query += " ORDER BY date DESC"
            
            if limit:
                query += " LIMIT ?"
                params.append(limit)
            
            cursor = self.connection.execute(query, params)
            results = cursor.fetchall()
            
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"获取市场数据失败 {symbol}: {e}")
            return []
    
    def get_economic_indicators(self, indicator_name: str = None, 
                              country_code: str = 'US',
                              start_date: str = None, end_date: str = None) -> List[Dict]:
        """获取经济指标数据"""
        try:
            query = """
                SELECT indicator_name, country_code, date, value, unit, 
                       frequency, source, fetched_at
                FROM economic_indicators 
                WHERE country_code = ?
            """
            params = [country_code]
            
            if indicator_name:
                query += " AND indicator_name = ?"
                params.append(indicator_name)
            
            if start_date:
                query += " AND date >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND date <= ?"
                params.append(end_date)
            
            query += " ORDER BY date DESC"
            
            cursor = self.connection.execute(query, params)
            results = cursor.fetchall()
            
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"获取经济指标数据失败: {e}")
            return []
    
    def get_asset_allocation_history(self, portfolio_id: str, 
                                   start_date: str = None, end_date: str = None) -> List[Dict]:
        """获取资产配置历史"""
        try:
            query = """
                SELECT portfolio_id, date, asset_class, allocation_percentage, 
                       market_value, cost_basis, unrealized_gain_loss, currency,
                       rebalance_reason, strategy_reference
                FROM asset_allocation_history 
                WHERE portfolio_id = ?
            """
            params = [portfolio_id]
            
            if start_date:
                query += " AND date >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND date <= ?"
                params.append(end_date)
            
            query += " ORDER BY date DESC"
            
            cursor = self.connection.execute(query, params)
            results = cursor.fetchall()
            
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"获取资产配置历史失败 {portfolio_id}: {e}")
            return []
    
    def get_crisis_events(self, category: str = None, 
                         start_date: str = None, end_date: str = None) -> List[Dict]:
        """获取危机事件数据"""
        try:
            query = """
                SELECT event_id, event_name, event_date, event_category, 
                       severity_level, affected_markets, trigger_symbols,
                       market_reaction_data, duration_days, recovery_period_days,
                       economic_impact_estimate, data_sources, analysis_notes
                FROM crisis_event_analysis 
                WHERE verified = TRUE
            """
            params = []
            
            if category:
                query += " AND event_category = ?"
                params.append(category)
            
            if start_date:
                query += " AND event_date >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND event_date <= ?"
                params.append(end_date)
            
            query += " ORDER BY event_date DESC"
            
            cursor = self.connection.execute(query, params)
            results = cursor.fetchall()
            
            # 解析JSON字段
            parsed_results = []
            for row in results:
                row_dict = dict(row)
                try:
                    row_dict['affected_markets'] = json.loads(row_dict['affected_markets'])
                    row_dict['trigger_symbols'] = json.loads(row_dict['trigger_symbols'])
                    row_dict['market_reaction_data'] = json.loads(row_dict['market_reaction_data'])
                    row_dict['data_sources'] = json.loads(row_dict['data_sources'])
                except:
                    pass
                parsed_results.append(row_dict)
            
            return parsed_results
            
        except Exception as e:
            logger.error(f"获取危机事件数据失败: {e}")
            return []
    
    def get_data_source_stats(self) -> Dict:
        """获取数据源统计信息"""
        try:
            stats = {}
            
            # 市场数据来源统计
            cursor = self.connection.execute("""
                SELECT source, COUNT(*) as count, 
                       MIN(date) as first_date, MAX(date) as last_date
                FROM market_data 
                GROUP BY source
            """)
            stats['market_data_sources'] = [dict(row) for row in cursor.fetchall()]
            
            # 经济指标来源统计
            cursor = self.connection.execute("""
                SELECT source, COUNT(*) as count,
                       MIN(date) as first_date, MAX(date) as last_date
                FROM economic_indicators 
                GROUP BY source
            """)
            stats['economic_indicator_sources'] = [dict(row) for row in cursor.fetchall()]
            
            # 数据质量统计
            cursor = self.connection.execute("""
                SELECT AVG(data_quality_score) as avg_quality,
                       COUNT(*) as total_records
                FROM market_data
            """)
            quality_stats = cursor.fetchone()
            stats['data_quality'] = dict(quality_stats) if quality_stats else {}
            
            return stats
            
        except Exception as e:
            logger.error(f"获取数据源统计失败: {e}")
            return {}
    
    def get_time_series_analysis(self, symbol: str, start_date: str, 
                               end_date: str) -> Dict:
        """获取时间序列分析数据"""
        try:
            # 获取基础数据
            market_data = self.get_market_data(symbol, start_date, end_date)
            if not market_data:
                return {}
            
            df = pd.DataFrame(market_data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # 计算技术指标
            volatility_data = self._calculate_volatility(df)
                    
            analysis = {
                'symbol': symbol,
                'date_range': {
                    'start': df['date'].min().strftime('%Y-%m-%d'),
                    'end': df['date'].max().strftime('%Y-%m-%d'),
                    'total_days': len(df)
                },
                'price_stats': {
                    'open': float(df['open_price'].iloc[-1]) if not df['open_price'].empty else 0,
                    'high': float(df['high_price'].max()) if not df['high_price'].empty else 0,
                    'low': float(df['low_price'].min()) if not df['low_price'].empty else 0,
                    'close': float(df['close_price'].iloc[-1]) if not df['close_price'].empty else 0,
                    'average': float(df['close_price'].mean()) if not df['close_price'].empty else 0
                },
                'volume_stats': {
                    'total_volume': int(df['volume'].sum()) if not df['volume'].empty else 0,
                    'average_volume': int(df['volume'].mean()) if not df['volume'].empty else 0,
                    'max_volume': int(df['volume'].max()) if not df['volume'].empty else 0
                },
                'returns': self._calculate_returns(df),
                'volatility': volatility_data,
                'trends': self._identify_trends(df)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"时间序列分析失败 {symbol}: {e}")
            return {}
    
    def _calculate_returns(self, df: pd.DataFrame) -> Dict:
        """计算收益率指标"""
        if df.empty or 'close_price' not in df.columns:
            return {}
        
        df = df.copy()
        df['daily_return'] = df['close_price'].pct_change()
        df['cumulative_return'] = (1 + df['daily_return']).cumprod() - 1
        
        return {
            'daily_returns': [float(x) for x in df['daily_return'].dropna().tail(30).tolist()],
            'cumulative_return': float(df['cumulative_return'].iloc[-1]) if not df['cumulative_return'].empty else 0,
            'average_daily_return': float(df['daily_return'].mean()) if not df['daily_return'].empty else 0,
            'max_daily_gain': float(df['daily_return'].max()) if not df['daily_return'].empty else 0,
            'max_daily_loss': float(df['daily_return'].min()) if not df['daily_return'].empty else 0
        }
    
    def _calculate_volatility(self, df: pd.DataFrame) -> Dict:
        """计算波动率指标"""
        if df.empty or 'daily_return' not in df.columns:
            return {}
        
        returns = df['daily_return'].dropna()
        if len(returns) < 2:
            return {}
        
        daily_vol = float(returns.std())
        annualized_vol = daily_vol * (252 ** 0.5)  # 年化波动率
        
        return {
            'daily_volatility': daily_vol,
            'annualized_volatility': annualized_vol,
            'volatility_30d': float(returns.tail(30).std()) if len(returns) >= 30 else daily_vol
        }
    
    def _identify_trends(self, df: pd.DataFrame) -> Dict:
        """识别价格趋势"""
        if df.empty or 'close_price' not in df.columns:
            return {}
        
        prices = df['close_price'].dropna()
        if len(prices) < 20:
            return {}
        
        # 简单移动平均线
        sma_20 = prices.rolling(window=20).mean()
        sma_50 = prices.rolling(window=50).mean()
        
        current_price = float(prices.iloc[-1])
        ma_20 = float(sma_20.iloc[-1]) if not pd.isna(sma_20.iloc[-1]) else current_price
        ma_50 = float(sma_50.iloc[-1]) if not pd.isna(sma_50.iloc[-1]) else current_price
        
        # 趋势判断
        trend = 'neutral'
        if current_price > ma_20 > ma_50:
            trend = 'bullish'
        elif current_price < ma_20 < ma_50:
            trend = 'bearish'
        
        return {
            'trend': trend,
            'current_price_vs_ma20': (current_price - ma_20) / ma_20 * 100,
            'ma20_vs_ma50': (ma_20 - ma_50) / ma_50 * 100,
            'support_levels': self._find_support_levels(prices),
            'resistance_levels': self._find_resistance_levels(prices)
        }
    
    def _find_support_levels(self, prices: pd.Series, window: int = 20) -> List[float]:
        """寻找支撑位"""
        if len(prices) < window * 2:
            return []
        
        local_mins = []
        for i in range(window, len(prices) - window):
            if all(prices.iloc[i] <= prices.iloc[i-j] for j in range(1, window+1)) and \
               all(prices.iloc[i] <= prices.iloc[i+j] for j in range(1, window+1)):
                local_mins.append(float(prices.iloc[i]))
        
        return sorted(local_mins)[-3:] if local_mins else []  # 返回最近的3个支撑位
    
    def _find_resistance_levels(self, prices: pd.Series, window: int = 20) -> List[float]:
        """寻找阻力位"""
        if len(prices) < window * 2:
            return []
        
        local_maxs = []
        for i in range(window, len(prices) - window):
            if all(prices.iloc[i] >= prices.iloc[i-j] for j in range(1, window+1)) and \
               all(prices.iloc[i] >= prices.iloc[i+j] for j in range(1, window+1)):
                local_maxs.append(float(prices.iloc[i]))
        
        return sorted(local_maxs, reverse=True)[:3] if local_maxs else []  # 返回最近的3个阻力位
    
    def get_dashboard_data(self) -> Dict:
        """获取仪表板所需的核心数据"""
        try:
            dashboard_data = {
                'market_overview': self._get_market_overview(),
                'economic_indicators': self._get_latest_economic_indicators(),
                'portfolio_summary': self._get_portfolio_summary(),
                'recent_events': self._get_recent_crisis_events(),
                'data_quality': self.get_data_source_stats()
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"获取仪表板数据失败: {e}")
            return {}
    
    def _get_market_overview(self) -> List[Dict]:
        """获取市场概览数据"""
        cursor = self.connection.execute("""
            SELECT symbol, date, close_price, volume,
                   LAG(close_price) OVER (PARTITION BY symbol ORDER BY date) as prev_close
            FROM market_data 
            WHERE date >= date('now', '-30 days')
            ORDER BY symbol, date DESC
        """)
        
        results = cursor.fetchall()
        overview = {}
        
        for row in results:
            symbol = row['symbol']
            if symbol not in overview:
                overview[symbol] = {
                    'symbol': symbol,
                    'current_price': row['close_price'],
                    'volume': row['volume'],
                    'change_percent': 0
                }
            
            # 计算涨跌幅
            if row['prev_close'] and row['prev_close'] > 0:
                change_pct = (row['close_price'] - row['prev_close']) / row['prev_close'] * 100
                overview[symbol]['change_percent'] = round(change_pct, 2)
        
        return list(overview.values())
    
    def _get_latest_economic_indicators(self) -> List[Dict]:
        """获取最新经济指标"""
        cursor = self.connection.execute("""
            SELECT indicator_name, value, unit, date,
                   LAG(value) OVER (PARTITION BY indicator_name ORDER BY date) as prev_value
            FROM economic_indicators 
            WHERE date >= date('now', '-90 days')
            ORDER BY indicator_name, date DESC
        """)
        
        results = cursor.fetchall()
        latest_indicators = {}
        
        for row in results:
            indicator = row['indicator_name']
            if indicator not in latest_indicators:
                latest_indicators[indicator] = {
                    'name': indicator,
                    'current_value': row['value'],
                    'unit': row['unit'],
                    'latest_date': row['date'],
                    'change': 0
                }
                
                # 计算变化
                if row['prev_value']:
                    change = row['value'] - row['prev_value']
                    latest_indicators[indicator]['change'] = round(change, 2)
        
        return list(latest_indicators.values())
    
    def _get_portfolio_summary(self) -> Dict:
        """获取投资组合摘要"""
        cursor = self.connection.execute("""
            SELECT asset_class, SUM(allocation_percentage) as total_allocation,
                   SUM(market_value) as total_value
            FROM asset_allocation_history 
            WHERE date = (SELECT MAX(date) FROM asset_allocation_history)
            GROUP BY asset_class
        """)
        
        allocations = [dict(row) for row in cursor.fetchall()]
        
        return {
            'total_value': sum(item['total_value'] for item in allocations),
            'allocations': allocations,
            'allocation_breakdown': {item['asset_class']: item['total_allocation'] for item in allocations}
        }
    
    def _get_recent_crisis_events(self) -> List[Dict]:
        """获取近期危机事件"""
        cursor = self.connection.execute("""
            SELECT event_name, event_date, severity_level, event_category
            FROM crisis_event_analysis 
            WHERE event_date >= date('now', '-1 year') AND verified = TRUE
            ORDER BY event_date DESC
            LIMIT 5
        """)
        
        return [dict(row) for row in cursor.fetchall()]
    
    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            logger.info("🔒 数据库连接已关闭")

def main():
    """测试数据库访问功能"""
    try:
        accessor = DatabaseAccessor()
        
        # 测试市场数据查询
        print("📊 市场数据查询测试:")
        market_data = accessor.get_market_data('^GSPC', limit=5)
        for data in market_data:
            print(f"  {data['symbol']} | {data['date']} | ${data['close_price']} | {data['volume']:,}")
        
        # 测试时间序列分析
        print("\n📈 时间序列分析测试:")
        analysis = accessor.get_time_series_analysis('^GSPC', '2024-01-01', '2024-01-31')
        if analysis:
            print(f"  价格范围: ${analysis['price_stats']['low']:.2f} - ${analysis['price_stats']['high']:.2f}")
            print(f"  平均价格: ${analysis['price_stats']['average']:.2f}")
            print(f"  年化波动率: {analysis['volatility'].get('annualized_volatility', 0):.2%}")
            print(f"  趋势: {analysis['trends'].get('trend', 'unknown')}")
        
        # 测试仪表板数据
        print("\n🎯 仪表板数据测试:")
        dashboard_data = accessor.get_dashboard_data()
        if dashboard_data:
            print(f"  市场概览标的数: {len(dashboard_data['market_overview'])}")
            print(f"  经济指标数: {len(dashboard_data['economic_indicators'])}")
            print(f"  近期事件数: {len(dashboard_data['recent_events'])}")
        
        accessor.close()
        print("\n✅ 数据库访问测试完成!")
        
    except Exception as e:
        logger.error(f"❌ 数据库访问测试失败: {e}")
        raise

if __name__ == "__main__":
    main()