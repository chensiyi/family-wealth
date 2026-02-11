"""
数据收集器模块
Data Collector Module
负责从各种数据源收集和处理数据
"""

import requests
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import feedparser
from bs4 import BeautifulSoup
import asyncio
import aiohttp
from dataclasses import dataclass

from core.data_source_manager import DataSourceManager, DataSourceConfig, DataSourceType

logger = logging.getLogger(__name__)

@dataclass
class CollectedData:
    """收集到的数据结构"""
    source_id: str
    data_type: str
    content: Dict[str, Any]
    timestamp: datetime
    metadata: Dict[str, Any]

class DataCollector:
    """数据收集器"""
    
    def __init__(self, db_path: str = "data_cache.db"):
        self.db_path = db_path
        self.data_source_manager = DataSourceManager()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Family Wealth Management System/1.0'
        })
        self.init_database()
    
    def init_database(self) -> None:
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建数据缓存表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id TEXT NOT NULL,
                data_type TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建数据源状态表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS source_status (
                source_id TEXT PRIMARY KEY,
                last_success DATETIME,
                last_error DATETIME,
                error_count INTEGER DEFAULT 0,
                status TEXT DEFAULT 'unknown'
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("数据库初始化完成")
    
    async def collect_all_data(self) -> Dict[str, List[CollectedData]]:
        """收集所有类型的数据"""
        results = {
            'economic_indicators': [],
            'etf_data': [],
            'news': [],
            'other': []
        }
        
        # 并发收集不同类型的数据
        tasks = []
        
        # 收集经济指标
        economic_sources = self.data_source_manager.get_sources_by_type(DataSourceType.ECONOMIC_INDICATOR)
        tasks.append(self.collect_economic_indicators(economic_sources))
        
        # 收集ETF数据
        etf_sources = self.data_source_manager.get_sources_by_type(DataSourceType.ETF_DATA)
        tasks.append(self.collect_etf_data(etf_sources))
        
        # 收集新闻
        news_sources = self.data_source_manager.get_sources_by_type(DataSourceType.NEWS_SOURCE)
        tasks.append(self.collect_news(news_sources))
        
        # 执行并发任务
        collected_data_lists = await asyncio.gather(*tasks)
        
        # 整理结果
        for data_list in collected_data_lists:
            for data in data_list:
                if data.data_type == 'economic_indicator':
                    results['economic_indicators'].append(data)
                elif data.data_type == 'etf_data':
                    results['etf_data'].append(data)
                elif data.data_type == 'news':
                    results['news'].append(data)
                else:
                    results['other'].append(data)
        
        return results
    
    async def collect_economic_indicators(self, sources: List[DataSourceConfig]) -> List[CollectedData]:
        """收集经济指标数据"""
        collected_data = []
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for source in sources:
                if source.enabled:
                    task = self._collect_single_economic_indicator(session, source)
                    tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, CollectedData):
                    collected_data.append(result)
                elif isinstance(result, Exception):
                    logger.error(f"收集经济指标数据失败: {result}")
        
        return collected_data
    
    async def _collect_single_economic_indicator(self, session: aiohttp.ClientSession, 
                                              source: DataSourceConfig) -> CollectedData:
        """收集单个经济指标数据源"""
        try:
            # 根据不同国家和机构采用不同的API调用方式
            if 'fred' in source.source_id:
                data = await self._collect_fred_data(session, source)
            elif 'bea' in source.source_id:
                data = await self._collect_bea_data(session, source)
            elif 'bls' in source.source_id:
                data = await self._collect_bls_data(session, source)
            elif 'nbs' in source.source_id:
                data = await self._collect_cn_nbs_data(session, source)
            elif 'pbc' in source.source_id:
                data = await self._collect_cn_pbc_data(session, source)
            else:
                # 默认处理方式
                data = await self._collect_generic_economic_data(session, source)
            
            collected = CollectedData(
                source_id=source.source_id,
                data_type='economic_indicator',
                content=data,
                timestamp=datetime.now(),
                metadata={
                    'country': self._extract_country_from_source(source.source_id),
                    'source_name': source.name,
                    'url': source.url
                }
            )
            
            self._cache_data(collected)
            self.data_source_manager.update_source_status(source.source_id, 'active')
            return collected
            
        except Exception as e:
            logger.error(f"收集经济指标数据失败 {source.source_id}: {e}")
            self.data_source_manager.update_source_status(source.source_id, 'error', str(e))
            raise
    
    async def collect_etf_data(self, sources: List[DataSourceConfig]) -> List[CollectedData]:
        """收集ETF数据"""
        collected_data = []
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for source in sources:
                if source.enabled:
                    task = self._collect_single_etf_data(session, source)
                    tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, CollectedData):
                    collected_data.append(result)
                elif isinstance(result, Exception):
                    logger.error(f"收集ETF数据失败: {result}")
        
        return collected_data
    
    async def _collect_single_etf_data(self, session: aiohttp.ClientSession, 
                                     source: DataSourceConfig) -> CollectedData:
        """收集单个ETF数据源"""
        try:
            if 'yahoo' in source.source_id:
                data = await self._collect_yahoo_etf_data(session, source)
            elif 'alpha_vantage' in source.source_id:
                data = await self._collect_alpha_vantage_etf_data(session, source)
            elif 'iex' in source.source_id:
                data = await self._collect_iex_etf_data(session, source)
            else:
                data = await self._collect_generic_etf_data(session, source)
            
            collected = CollectedData(
                source_id=source.source_id,
                data_type='etf_data',
                content=data,
                timestamp=datetime.now(),
                metadata={
                    'source_name': source.name,
                    'url': source.url
                }
            )
            
            self._cache_data(collected)
            self.data_source_manager.update_source_status(source.source_id, 'active')
            return collected
            
        except Exception as e:
            logger.error(f"收集ETF数据失败 {source.source_id}: {e}")
            self.data_source_manager.update_source_status(source.source_id, 'error', str(e))
            raise
    
    async def collect_news(self, sources: List[DataSourceConfig]) -> List[CollectedData]:
        """收集新闻数据"""
        collected_data = []
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for source in sources:
                if source.enabled:
                    task = self._collect_single_news_source(session, source)
                    tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, CollectedData):
                    collected_data.append(result)
                elif isinstance(result, Exception):
                    logger.error(f"收集新闻数据失败: {result}")
        
        return collected_data
    
    async def _collect_single_news_source(self, session: aiohttp.ClientSession, 
                                        source: DataSourceConfig) -> CollectedData:
        """收集单个新闻源"""
        try:
            if source.source_id in ['google_news', 'bbc_news', 'reuters', 'bloomberg']:
                data = await self._collect_rss_news(session, source)
            elif source.source_id in ['cctv_news', 'xinhua', 'caixin']:
                data = await self._collect_chinese_news(session, source)
            elif source.source_id in ['wall_street_journal', 'financial_times', 'cnbc']:
                data = await self._collect_financial_news(session, source)
            else:
                data = await self._collect_generic_news(session, source)
            
            collected = CollectedData(
                source_id=source.source_id,
                data_type='news',
                content=data,
                timestamp=datetime.now(),
                metadata={
                    'source_name': source.name,
                    'url': source.url,
                    'original_link': data.get('original_link', source.url)
                }
            )
            
            self._cache_data(collected)
            self.data_source_manager.update_source_status(source.source_id, 'active')
            return collected
            
        except Exception as e:
            logger.error(f"收集新闻数据失败 {source.source_id}: {e}")
            self.data_source_manager.update_source_status(source.source_id, 'error', str(e))
            raise
    
    def _cache_data(self, data: CollectedData) -> None:
        """缓存收集到的数据"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO data_cache (source_id, data_type, content, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                data.source_id,
                data.data_type,
                json.dumps(data.content, ensure_ascii=False),
                data.timestamp.isoformat(),
                json.dumps(data.metadata, ensure_ascii=False)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"缓存数据失败: {e}")
    
    def get_cached_data(self, data_type: str, hours: int = 24) -> List[Dict[str, Any]]:
        """获取缓存的数据"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            since_time = datetime.now() - timedelta(hours=hours)
            
            cursor.execute('''
                SELECT source_id, data_type, content, timestamp, metadata
                FROM data_cache
                WHERE data_type = ? AND timestamp > ?
                ORDER BY timestamp DESC
            ''', (data_type, since_time.isoformat()))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [{
                'source_id': row[0],
                'data_type': row[1],
                'content': json.loads(row[2]),
                'timestamp': row[3],
                'metadata': json.loads(row[4])
            } for row in rows]
            
        except Exception as e:
            logger.error(f"获取缓存数据失败: {e}")
            return []
    
    # 以下是具体的API调用实现（示例）
    async def _collect_fred_data(self, session: aiohttp.ClientSession, source: DataSourceConfig) -> Dict[str, Any]:
        """收集美联储数据"""
        # 实际实现需要FRED API密钥
        return {
            'series': ['GDP', 'CPI', 'Unemployment Rate'],
            'latest_values': {
                'GDP': 21.7,
                'CPI': 3.2,
                'Unemployment_Rate': 3.7
            }
        }
    
    async def _collect_bea_data(self, session: aiohttp.ClientSession, source: DataSourceConfig) -> Dict[str, Any]:
        """收集美国经济分析局数据"""
        return {
            'gdp_components': ['Consumption', 'Investment', 'Government', 'Net Exports'],
            'quarterly_data': 'latest_quarter_data'
        }
    
    async def _collect_bls_data(self, session: aiohttp.ClientSession, source: DataSourceConfig) -> Dict[str, Any]:
        """收集劳工统计局数据"""
        return {
            'employment_data': 'latest_employment_statistics',
            'cpi_data': 'latest_consumer_price_index'
        }
    
    async def _collect_cn_nbs_data(self, session: aiohttp.ClientSession, source: DataSourceConfig) -> Dict[str, Any]:
        """收集中国国家统计局数据"""
        return {
            'macro_indicators': ['GDP', 'CPI', 'PPI', 'PMI'],
            'latest_values': 'latest_chinese_economic_data'
        }
    
    async def _collect_cn_pbc_data(self, session: aiohttp.ClientSession, source: DataSourceConfig) -> Dict[str, Any]:
        """收集中国人民银行数据"""
        return {
            'monetary_policy': ['M2', 'Loan Prime Rate', 'Reserve Requirement Ratio'],
            'latest_values': 'latest_monetary_data'
        }
    
    async def _collect_yahoo_etf_data(self, session: aiohttp.ClientSession, source: DataSourceConfig) -> Dict[str, Any]:
        """收集雅虎财经ETF数据"""
        return {
            'popular_etfs': ['SPY', 'QQQ', 'IWM', 'VTI', 'VEA'],
            'prices': 'real_time_etf_prices'
        }
    
    async def _collect_alpha_vantage_etf_data(self, session: aiohttp.ClientSession, source: DataSourceConfig) -> Dict[str, Any]:
        """收集Alpha Vantage ETF数据"""
        return {
            'technical_indicators': ['RSI', 'MACD', 'BBANDS'],
            'etf_performance': 'etf_technical_analysis'
        }
    
    async def _collect_rss_news(self, session: aiohttp.ClientSession, source: DataSourceConfig) -> Dict[str, Any]:
        """收集RSS新闻"""
        async with session.get(source.url) as response:
            content = await response.text()
            feed = feedparser.parse(content)
            
            articles = []
            for entry in feed.entries[:10]:  # 获取最新的10篇文章
                articles.append({
                    'title': entry.title,
                    'summary': getattr(entry, 'summary', ''),
                    'link': entry.link,
                    'published': getattr(entry, 'published', ''),
                    'original_link': entry.link
                })
            
            return {
                'articles': articles,
                'feed_title': getattr(feed.feed, 'title', ''),
                'updated': getattr(feed.feed, 'updated', '')
            }
    
    def _extract_country_from_source(self, source_id: str) -> str:
        """从源ID提取国家信息"""
        country_mapping = {
            'us_': 'United States',
            'cn_': 'China',
            'jp_': 'Japan',
            'ru_': 'Russia',
            'de_': 'Germany',
            'fr_': 'France',
            'vn_': 'Vietnam'
        }
        
        for prefix, country in country_mapping.items():
            if source_id.startswith(prefix):
                return country
        return 'Unknown'
    
    def get_collection_summary(self) -> Dict[str, Any]:
        """获取数据收集摘要"""
        return {
            'total_sources': len(self.data_source_manager.data_sources),
            'active_sources': len(self.data_source_manager.get_active_sources()),
            'cached_records': self._get_cached_record_count(),
            'last_collection': self._get_last_collection_time(),
            'source_statistics': self.data_source_manager.get_source_statistics()
        }
    
    def _get_cached_record_count(self) -> int:
        """获取缓存记录数"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM data_cache')
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception:
            return 0
    
    def _get_last_collection_time(self) -> Optional[str]:
        """获取最后收集时间"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT MAX(timestamp) FROM data_cache')
            result = cursor.fetchone()[0]
            conn.close()
            return result
        except Exception:
            return None

if __name__ == "__main__":
    # 测试数据收集器
    collector = DataCollector()
    print("数据收集器初始化完成")
    print(f"配置的数据源数量: {len(collector.data_source_manager.data_sources)}")