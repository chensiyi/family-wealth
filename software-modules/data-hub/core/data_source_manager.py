"""
数据源管理模块
DataSource Manager Module
负责管理各种数据源的接入、配置和数据收集
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
import json
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class DataSourceType(Enum):
    """数据源类型枚举"""
    ECONOMIC_INDICATOR = "economic_indicator"  # 经济指标
    ETF_DATA = "etf_data"                      # ETF数据
    NEWS_SOURCE = "news_source"                # 新闻源
    STOCK_PRICE = "stock_price"                # 股票价格
    FINANCIAL_STATEMENT = "financial_statement" # 财务报表
    COMMODITY_PRICE = "commodity_price"        # 商品价格
    CURRENCY_RATE = "currency_rate"            # 汇率数据
    BOND_YIELD = "bond_yield"                  # 债券收益率

class DataSourceCategory(Enum):
    """数据源分类"""
    GOVERNMENT = "government"      # 政府官方
    FINANCIAL = "financial"        # 金融机构
    MEDIA = "media"                # 媒体机构
    COMMERCIAL = "commercial"      # 商业数据提供商
    EXCHANGE = "exchange"          # 交易所

class DataSourceConfig:
    """数据源配置类"""
    
    def __init__(self, source_id: str, name: str, source_type: DataSourceType,
                 category: DataSourceCategory, url: str, api_key: Optional[str] = None,
                 frequency: str = "daily", enabled: bool = True):
        self.source_id = source_id
        self.name = name
        self.source_type = source_type
        self.category = category
        self.url = url
        self.api_key = api_key
        self.frequency = frequency  # 更新频率: real-time, hourly, daily, weekly, monthly
        self.enabled = enabled
        self.last_updated = None
        self.status = "unknown"  # unknown, active, inactive, error
        self.error_count = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'source_id': self.source_id,
            'name': self.name,
            'source_type': self.source_type.value,
            'category': self.category.value,
            'url': self.url,
            'api_key': self.api_key,
            'frequency': self.frequency,
            'enabled': self.enabled,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'status': self.status,
            'error_count': self.error_count
        }

class DataSourceManager:
    """数据源管理器"""
    
    def __init__(self, config_file: str = "data_sources_config.json"):
        self.config_file = config_file
        self.data_sources: Dict[str, DataSourceConfig] = {}
        self.load_configurations()
        
    def load_configurations(self) -> None:
        """加载数据源配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                for source_data in config_data.get('data_sources', []):
                    source = DataSourceConfig(
                        source_id=source_data['source_id'],
                        name=source_data['name'],
                        source_type=DataSourceType(source_data['source_type']),
                        category=DataSourceCategory(source_data['category']),
                        url=source_data['url'],
                        api_key=source_data.get('api_key'),
                        frequency=source_data.get('frequency', 'daily'),
                        enabled=source_data.get('enabled', True)
                    )
                    if source_data.get('last_updated'):
                        source.last_updated = datetime.fromisoformat(source_data['last_updated'])
                    source.status = source_data.get('status', 'unknown')
                    source.error_count = source_data.get('error_count', 0)
                    self.data_sources[source.source_id] = source
                    
            logger.info(f"加载了 {len(self.data_sources)} 个数据源配置")
        except FileNotFoundError:
            logger.info("配置文件不存在，将创建默认配置")
            self.create_default_configurations()
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            self.create_default_configurations()
    
    def save_configurations(self) -> bool:
        """保存数据源配置"""
        try:
            config_data = {
                'data_sources': [source.to_dict() for source in self.data_sources.values()],
                'last_modified': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
                
            logger.info("数据源配置已保存")
            return True
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
            return False
    
    def create_default_configurations(self) -> None:
        """创建默认数据源配置"""
        # 经济关键数据源
        economic_sources = [
            # 美国
            DataSourceConfig("us_fred", "美联储经济数据库", DataSourceType.ECONOMIC_INDICATOR,
                           DataSourceCategory.GOVERNMENT, "https://fred.stlouisfed.org/api"),
            DataSourceConfig("us_bea", "美国经济分析局", DataSourceType.ECONOMIC_INDICATOR,
                           DataSourceCategory.GOVERNMENT, "https://apps.bea.gov/api"),
            DataSourceConfig("us_bls", "美国劳工统计局", DataSourceType.ECONOMIC_INDICATOR,
                           DataSourceCategory.GOVERNMENT, "https://api.bls.gov/publicAPI"),
            
            # 中国
            DataSourceConfig("cn_nbs", "国家统计局", DataSourceType.ECONOMIC_INDICATOR,
                           DataSourceCategory.GOVERNMENT, "http://www.stats.gov.cn/api"),
            DataSourceConfig("cn_pbc", "中国人民银行", DataSourceType.ECONOMIC_INDICATOR,
                           DataSourceCategory.GOVERNMENT, "http://www.pbc.gov.cn/api"),
            
            # 日本
            DataSourceConfig("jp_meti", "经济产业省", DataSourceType.ECONOMIC_INDICATOR,
                           DataSourceCategory.GOVERNMENT, "https://www.meti.go.jp/statistics"),
            DataSourceConfig("jp_boj", "日本银行", DataSourceType.ECONOMIC_INDICATOR,
                           DataSourceCategory.GOVERNMENT, "https://www.boj.or.jp/en/statistics"),
            
            # 俄罗斯
            DataSourceConfig("ru_rosstat", "俄罗斯联邦统计局", DataSourceType.ECONOMIC_INDICATOR,
                           DataSourceCategory.GOVERNMENT, "https://rosstat.gov.ru/api"),
            
            # 德国
            DataSourceConfig("de_destatis", "德国联邦统计局", DataSourceType.ECONOMIC_INDICATOR,
                           DataSourceCategory.GOVERNMENT, "https://www.destatis.de/api"),
            
            # 法国
            DataSourceConfig("fr_insee", "法国国家统计局", DataSourceType.ECONOMIC_INDICATOR,
                           DataSourceCategory.GOVERNMENT, "https://api.insee.fr"),
            
            # 越南
            DataSourceConfig("vn_gso", "越南统计局", DataSourceType.ECONOMIC_INDICATOR,
                           DataSourceCategory.GOVERNMENT, "https://www.gso.gov.vn/api")
        ]
        
        # ETF数据源
        etf_sources = [
            DataSourceConfig("etf_yahoo", "雅虎财经ETF", DataSourceType.ETF_DATA,
                           DataSourceCategory.FINANCIAL, "https://query1.finance.yahoo.com/v8/finance/chart"),
            DataSourceConfig("etf_alpha_vantage", "Alpha Vantage ETF", DataSourceType.ETF_DATA,
                           DataSourceCategory.COMMERCIAL, "https://www.alphavantage.co/query"),
            DataSourceConfig("etf_iex", "IEX Cloud ETF", DataSourceType.ETF_DATA,
                           DataSourceCategory.FINANCIAL, "https://cloud.iexapis.com/stable"),
            DataSourceConfig("nyse_etf", "纽约证券交易所ETF", DataSourceType.ETF_DATA,
                           DataSourceCategory.EXCHANGE, "https://www.nyse.com/api"),
            DataSourceConfig("nasdaq_etf", "纳斯达克ETF", DataSourceType.ETF_DATA,
                           DataSourceCategory.EXCHANGE, "https://api.nasdaq.com/api")
        ]
        
        # 新闻数据源
        news_sources = [
            # 国际媒体
            DataSourceConfig("google_news", "Google News", DataSourceType.NEWS_SOURCE,
                           DataSourceCategory.MEDIA, "https://news.google.com/rss"),
            DataSourceConfig("bbc_news", "BBC News", DataSourceType.NEWS_SOURCE,
                           DataSourceCategory.MEDIA, "http://feeds.bbci.co.uk/news/rss.xml"),
            DataSourceConfig("reuters", "路透社", DataSourceType.NEWS_SOURCE,
                           DataSourceCategory.MEDIA, "https://www.reutersagency.com/feed"),
            DataSourceConfig("bloomberg", "彭博社", DataSourceType.NEWS_SOURCE,
                           DataSourceCategory.MEDIA, "https://news.bloomberght.com/rss"),
            
            # 中文媒体
            DataSourceConfig("cctv_news", "央视新闻", DataSourceType.NEWS_SOURCE,
                           DataSourceCategory.MEDIA, "http://news.cctv.com/2019/07/gaiban/cmsdatainterface/page/news_1.jsonp"),
            DataSourceConfig("xinhua", "新华社", DataSourceType.NEWS_SOURCE,
                           DataSourceCategory.MEDIA, "http://www.news.cn/rss/"),
            DataSourceConfig("caixin", "财新网", DataSourceType.NEWS_SOURCE,
                           DataSourceCategory.MEDIA, "https://datanews.caixin.com/datanews/jsondata/"),
            
            # 专业财经媒体
            DataSourceConfig("wall_street_journal", "华尔街日报", DataSourceType.NEWS_SOURCE,
                           DataSourceCategory.MEDIA, "https://feeds.a.dj.com/rss/RSSMarketsMain.xml"),
            DataSourceConfig("financial_times", "金融时报", DataSourceType.NEWS_SOURCE,
                           DataSourceCategory.MEDIA, "https://www.ft.com/rss/home"),
            DataSourceConfig("cnbc", "CNBC", DataSourceType.NEWS_SOURCE,
                           DataSourceCategory.MEDIA, "https://search.cnbc.com/rs/search/combinedcms/view.xml"),
            
            # 行业专业媒体
            DataSourceConfig("techcrunch", "TechCrunch", DataSourceType.NEWS_SOURCE,
                           DataSourceCategory.MEDIA, "https://techcrunch.com/feed"),
            DataSourceConfig("coindesk", "CoinDesk", DataSourceType.NEWS_SOURCE,
                           DataSourceCategory.MEDIA, "https://www.coindesk.com/arc/outboundfeeds/rss"),
            DataSourceConfig("forbes", "福布斯", DataSourceType.NEWS_SOURCE,
                           DataSourceCategory.MEDIA, "https://www.forbes.com/news/rss.xml")
        ]
        
        # 我建议补充的数据源
        additional_sources = [
            # 商品价格
            DataSourceConfig("commodity_lme", "伦敦金属交易所", DataSourceType.COMMODITY_PRICE,
                           DataSourceCategory.EXCHANGE, "https://www.lme.com/api"),
            DataSourceConfig("commodity_cme", "芝加哥商品交易所", DataSourceType.COMMODITY_PRICE,
                           DataSourceCategory.EXCHANGE, "https://www.cmegroup.com/CmeWS/mvc/Quotes/Future"),
            
            # 汇率数据
            DataSourceConfig("fx_oanda", "OANDA汇率", DataSourceType.CURRENCY_RATE,
                           DataSourceCategory.FINANCIAL, "https://fxds.oanda.com/api"),
            DataSourceConfig("fx_ecb", "欧洲央行汇率", DataSourceType.CURRENCY_RATE,
                           DataSourceCategory.GOVERNMENT, "https://www.ecb.europa.eu/stats/eurofxref"),
            
            # 债券收益率
            DataSourceConfig("bond_treasury", "美国国债", DataSourceType.BOND_YIELD,
                           DataSourceCategory.GOVERNMENT, "https://home.treasury.gov/resource-center/data-chart-center/interest-rates"),
            DataSourceConfig("bond_china", "中国国债", DataSourceType.BOND_YIELD,
                           DataSourceCategory.GOVERNMENT, "http://yield.chinabond.com.cn/cbweb-mn/yc/searchYc"),
            
            # 全球主要市场指数
            DataSourceConfig("index_msci", "MSCI指数", DataSourceType.STOCK_PRICE,
                           DataSourceCategory.FINANCIAL, "https://www.msci.com/eqb/custom_indexes"),
            DataSourceConfig("index_ftse", "富时指数", DataSourceType.STOCK_PRICE,
                           DataSourceCategory.FINANCIAL, "https://www.ftserussell.com/api"),
            
            # 加密货币数据
            DataSourceConfig("crypto_coinmarketcap", "CoinMarketCap", DataSourceType.STOCK_PRICE,
                           DataSourceCategory.COMMERCIAL, "https://pro-api.coinmarketcap.com/v1"),
            DataSourceConfig("crypto_coingecko", "CoinGecko", DataSourceType.STOCK_PRICE,
                           DataSourceCategory.COMMERCIAL, "https://api.coingecko.com/api/v3")
        ]
        
        # 添加所有数据源
        all_sources = economic_sources + etf_sources + news_sources + additional_sources
        for source in all_sources:
            self.data_sources[source.source_id] = source
            
        self.save_configurations()
        logger.info(f"创建了 {len(all_sources)} 个默认数据源配置")
    
    def get_sources_by_type(self, source_type: DataSourceType) -> List[DataSourceConfig]:
        """按类型获取数据源"""
        return [source for source in self.data_sources.values() 
                if source.source_type == source_type and source.enabled]
    
    def get_sources_by_category(self, category: DataSourceCategory) -> List[DataSourceConfig]:
        """按分类获取数据源"""
        return [source for source in self.data_sources.values() 
                if source.category == category and source.enabled]
    
    def get_active_sources(self) -> List[DataSourceConfig]:
        """获取所有启用的数据源"""
        return [source for source in self.data_sources.values() if source.enabled]
    
    def add_source(self, source: DataSourceConfig) -> bool:
        """添加新的数据源"""
        if source.source_id in self.data_sources:
            logger.warning(f"数据源 {source.source_id} 已存在")
            return False
        
        self.data_sources[source.source_id] = source
        self.save_configurations()
        logger.info(f"添加数据源: {source.name}")
        return True
    
    def update_source_status(self, source_id: str, status: str, error_msg: Optional[str] = None) -> None:
        """更新数据源状态"""
        if source_id in self.data_sources:
            source = self.data_sources[source_id]
            source.status = status
            source.last_updated = datetime.now()
            
            if status == "error":
                source.error_count += 1
                logger.error(f"数据源 {source_id} 错误: {error_msg}")
            else:
                source.error_count = 0
                
            self.save_configurations()
    
    def get_source_statistics(self) -> Dict[str, Any]:
        """获取数据源统计信息"""
        total_sources = len(self.data_sources)
        active_sources = len(self.get_active_sources())
        
        type_stats = {}
        category_stats = {}
        
        for source in self.data_sources.values():
            # 类型统计
            type_key = source.source_type.value
            type_stats[type_key] = type_stats.get(type_key, 0) + 1
            
            # 分类统计
            category_key = source.category.value
            category_stats[category_key] = category_stats.get(category_key, 0) + 1
        
        return {
            'total_sources': total_sources,
            'active_sources': active_sources,
            'by_type': type_stats,
            'by_category': category_stats,
            'last_updated': datetime.now().isoformat()
        }
    
    def __str__(self) -> str:
        stats = self.get_source_statistics()
        return f"DataSourceManager(总计:{stats['total_sources']}, 启用:{stats['active_sources']})"

    def __repr__(self) -> str:
        return f"DataSourceManager(config_file='{self.config_file}', sources={len(self.data_sources)})"