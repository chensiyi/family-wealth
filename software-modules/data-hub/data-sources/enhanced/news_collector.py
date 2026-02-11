"""
全球重点行业新闻收集器
Collects key news from global industries and sectors
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import requests
import json
import logging
from urllib.parse import quote

logger = logging.getLogger(__name__)

class NewsCollector:
    """全球重点行业新闻收集器"""
    
    def __init__(self):
        self.supported_sectors = {
            'technology': ['半导体', '人工智能', '云计算', '芯片', '软件'],
            'energy': ['石油', '天然气', '新能源', '电池', '太阳能'],
            'finance': ['银行', '保险', '证券', '金融科技', '支付'],
            'healthcare': ['医药', '生物科技', '医疗器械', '疫苗', '基因'],
            'consumer': ['零售', '电商', '食品饮料', '奢侈品', '快消品'],
            'industrial': ['制造业', '机械', '建筑', '交通', '物流'],
            'telecom': ['通信', '5G', '物联网', '数据中心', '网络设备']
        }
        
        self.regions = {
            'us': '美国',
            'cn': '中国', 
            'eu': '欧洲',
            'jp': '日本',
            'kr': '韩国'
        }
        
        self.news_cache = {}
        self.last_update = {}
    
    def collect_sector_news(self, sector: str, region: str = 'global', 
                          days_back: int = 7) -> List[Dict[str, Any]]:
        """
        收集指定行业的新闻
        
        Args:
            sector: 行业类别
            region: 地区 ('us', 'cn', 'eu', 'jp', 'kr', 'global')
            days_back: 回溯天数
            
        Returns:
            新闻列表
        """
        if sector not in self.supported_sectors:
            logger.warning(f"不支持的行业: {sector}")
            return []
        
        cache_key = f"{sector}_{region}_{days_back}"
        if cache_key in self.news_cache:
            cached_time = self.last_update.get(cache_key, datetime.min)
            if datetime.now() - cached_time < timedelta(hours=1):
                logger.info(f"使用缓存的新闻数据: {cache_key}")
                return self.news_cache[cache_key]
        
        keywords = self.supported_sectors[sector]
        news_list = []
        
        try:
            # 这里使用模拟数据，实际应用中需要连接真实的新闻API
            for keyword in keywords:
                simulated_news = self._generate_simulated_news(
                    keyword, sector, region, days_back
                )
                news_list.extend(simulated_news)
            
            # 去重和排序
            news_list = self._deduplicate_news(news_list)
            news_list.sort(key=lambda x: x['publish_date'], reverse=True)
            
            # 缓存结果
            self.news_cache[cache_key] = news_list[:50]  # 限制缓存数量
            self.last_update[cache_key] = datetime.now()
            
            logger.info(f"收集到 {len(news_list)} 条{sector}行业新闻")
            return news_list[:50]
            
        except Exception as e:
            logger.error(f"收集新闻失败: {e}")
            return []
    
    def _generate_simulated_news(self, keyword: str, sector: str, 
                               region: str, days_back: int) -> List[Dict[str, Any]]:
        """生成模拟新闻数据（用于演示）"""
        import random
        from datetime import datetime, timedelta
        
        news_templates = [
            "{company}在{sector}领域取得重大突破",
            "{region}{sector}市场迎来新机遇",
            "{company}发布{keyword}相关新产品",
            "{sector}行业监管政策发生重要变化",
            "{company}获得{amount}亿美元投资",
            "{keyword}技术发展推动{sector}变革"
        ]
        
        companies = {
            'technology': ['苹果', '谷歌', '微软', '英伟达', '台积电'],
            'energy': ['壳牌', '埃克森美孚', '特斯拉', '宁德时代', '隆基股份'],
            'finance': ['摩根大通', '伯克希尔', '蚂蚁集团', '招商银行', 'Visa'],
            'healthcare': ['辉瑞', '强生', '药明康德', '迈瑞医疗', 'Moderna'],
            'consumer': ['亚马逊', '阿里巴巴', '沃尔玛', '茅台', '耐克'],
            'industrial': ['西门子', '通用电气', '卡特彼勒', '三一重工', '比亚迪'],
            'telecom': ['华为', '爱立信', '诺基亚', '中兴通讯', '思科']
        }
        
        regions_full = {
            'us': '美国',
            'cn': '中国',
            'eu': '欧洲',
            'jp': '日本', 
            'kr': '韩国',
            'global': '全球'
        }
        
        news_list = []
        company_list = companies.get(sector, ['知名企业'])
        region_name = regions_full.get(region, '全球')
        
        # 生成随机新闻
        for i in range(random.randint(3, 8)):
            template = random.choice(news_templates)
            company = random.choice(company_list)
            amount = random.randint(10, 1000)
            
            title = template.format(
                company=company,
                sector=self._get_sector_chinese(sector),
                keyword=keyword,
                region=region_name,
                amount=amount
            )
            
            # 生成随机发布时间
            days_ago = random.randint(0, days_back)
            hours_ago = random.randint(0, 23)
            publish_time = datetime.now() - timedelta(days=days_ago, hours=hours_ago)
            
            news_item = {
                'title': title,
                'summary': f'{keyword}相关新闻报道，涉及{company}在{region_name}{self._get_sector_chinese(sector)}领域的重要进展。',
                'source': random.choice(['财经网', '华尔街日报', '路透社', '彭博社', '第一财经']),
                'url': f'https://example.com/news/{random.randint(1000, 9999)}',
                'publish_date': publish_time.isoformat(),
                'sector': sector,
                'region': region,
                'keywords': [keyword],
                'sentiment': random.choice(['positive', 'negative', 'neutral']),
                'impact_score': round(random.uniform(0.1, 1.0), 2)
            }
            
            news_list.append(news_item)
        
        return news_list
    
    def _deduplicate_news(self, news_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """新闻去重"""
        seen_titles = set()
        unique_news = []
        
        for news in news_list:
            title = news['title']
            if title not in seen_titles:
                seen_titles.add(title)
                unique_news.append(news)
        
        return unique_news
    
    def _get_sector_chinese(self, sector: str) -> str:
        """获取行业中文化名称"""
        sector_names = {
            'technology': '科技',
            'energy': '能源',
            'finance': '金融',
            'healthcare': '医疗健康',
            'consumer': '消费品',
            'industrial': '工业制造',
            'telecom': '通信'
        }
        return sector_names.get(sector, sector)
    
    def get_sector_summary(self, sector: str, region: str = 'global', 
                          days_back: int = 7) -> Dict[str, Any]:
        """获取行业新闻摘要"""
        news_list = self.collect_sector_news(sector, region, days_back)
        
        if not news_list:
            return {
                'sector': sector,
                'region': region,
                'news_count': 0,
                'date_range': f"最近{days_back}天",
                'summary': '暂无相关新闻'
            }
        
        # 统计信息
        sentiments = {}
        sources = {}
        keywords = {}
        
        for news in news_list:
            # 情绪统计
            sentiment = news['sentiment']
            sentiments[sentiment] = sentiments.get(sentiment, 0) + 1
            
            # 来源统计
            source = news['source']
            sources[source] = sources.get(source, 0) + 1
            
            # 关键词统计
            for keyword in news['keywords']:
                keywords[keyword] = keywords.get(keyword, 0) + 1
        
        return {
            'sector': sector,
            'region': region,
            'news_count': len(news_list),
            'date_range': f"最近{days_back}天",
            'latest_news_date': news_list[0]['publish_date'] if news_list else None,
            'sentiment_distribution': sentiments,
            'top_sources': dict(sorted(sources.items(), key=lambda x: x[1], reverse=True)[:5]),
            'top_keywords': dict(sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:10]),
            'average_impact_score': sum(n['impact_score'] for n in news_list) / len(news_list) if news_list else 0
        }
    
    def search_news(self, query: str, sectors: List[str] = None, 
                   regions: List[str] = None, days_back: int = 30) -> List[Dict[str, Any]]:
        """搜索新闻"""
        if sectors is None:
            sectors = list(self.supported_sectors.keys())
        if regions is None:
            regions = list(self.regions.keys())
        
        all_news = []
        for sector in sectors:
            for region in regions:
                news_list = self.collect_sector_news(sector, region, days_back)
                # 简单的文本匹配
                filtered_news = [
                    news for news in news_list 
                    if query.lower() in news['title'].lower() or 
                       query.lower() in news['summary'].lower()
                ]
                all_news.extend(filtered_news)
        
        # 去重和排序
        all_news = self._deduplicate_news(all_news)
        all_news.sort(key=lambda x: x['publish_date'], reverse=True)
        
        return all_news[:100]  # 限制返回数量

    def __str__(self) -> str:
        return f"NewsCollector(supported_sectors={len(self.supported_sectors)})"

    def __repr__(self) -> str:
        return f"NewsCollector(supported_sectors={list(self.supported_sectors.keys())})"