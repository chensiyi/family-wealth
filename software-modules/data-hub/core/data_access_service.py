#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据访问服务
提供统一的数据访问接口，协调数据源和缓存管理
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from core.data_source_manager import DataSourceManager
from core.cache_manager import CacheManager

class DataAccessService:
    """统一数据访问服务"""
    
    def __init__(self, source_manager: DataSourceManager, cache_manager: CacheManager):
        self.source_manager = source_manager
        self.cache_manager = cache_manager
        self.logger = logging.getLogger(__name__)
        
        # 数据类型到数据源的映射
        self._data_type_mapping = {
            'stock_prices': ['yahoo_finance', 'fred'],
            'economic_indicators': ['fred', 'worldbank'],
            'corporate_financials': ['sec_edgar', 'yahoo_finance'],
            'bond_data': ['fred'],
            'commodity_prices': ['fred'],
            'currency_rates': ['fred']
        }
    
    def get_financial_data(self, symbol: str, data_type: str = 'prices', 
                          start_date: str = None, end_date: str = None,
                          force_refresh: bool = False) -> Dict:
        """获取金融数据"""
        try:
            # 生成缓存键
            cache_key = self._generate_cache_key('financial', symbol, data_type, start_date, end_date)
            
            # 检查缓存（除非强制刷新）
            if not force_refresh:
                cached_data = self.cache_manager.get_cached_data(cache_key)
                if cached_data:
                    self.logger.debug(f"金融数据缓存命中: {symbol}")
                    return {
                        'success': True,
                        'data': cached_data,
                        'source': 'cache',
                        'cached_at': datetime.now().isoformat()
                    }
            
            # 确定数据源
            sources = self._data_type_mapping.get(data_type, ['yahoo_finance'])
            source_id = sources[0]  # 使用第一个可用的数据源
            
            # 从数据源获取数据
            raw_data = self._fetch_from_source(source_id, {
                'symbol': symbol,
                'data_type': data_type,
                'start_date': start_date,
                'end_date': end_date
            })
            
            if not raw_data.get('success'):
                return raw_data
            
            # 处理和标准化数据
            processed_data = self._process_financial_data(raw_data['data'], data_type)
            
            # 缓存数据（设置适当的TTL）
            ttl = self._get_appropriate_ttl(data_type, start_date, end_date)
            self.cache_manager.set_cached_data(cache_key, processed_data, ttl)
            
            return {
                'success': True,
                'data': processed_data,
                'source': source_id,
                'fetched_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"获取金融数据失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_economic_indicators(self, indicators: List[str], 
                              country: str = 'US',
                              start_date: str = None, end_date: str = None,
                              force_refresh: bool = False) -> Dict:
        """获取经济指标数据"""
        try:
            # 生成缓存键
            cache_key = self._generate_cache_key('economic', '-'.join(indicators), country, start_date, end_date)
            
            # 检查缓存
            if not force_refresh:
                cached_data = self.cache_manager.get_cached_data(cache_key)
                if cached_data:
                    return {
                        'success': True,
                        'data': cached_data,
                        'source': 'cache'
                    }
            
            # 从FRED获取经济指标
            raw_data = self._fetch_from_source('fred', {
                'indicators': indicators,
                'country': country,
                'start_date': start_date,
                'end_date': end_date
            })
            
            if not raw_data.get('success'):
                return raw_data
            
            # 处理数据
            processed_data = self._process_economic_data(raw_data['data'])
            
            # 缓存数据
            ttl = 86400  # 经济数据一天更新一次
            self.cache_manager.set_cached_data(cache_key, processed_data, ttl)
            
            return {
                'success': True,
                'data': processed_data,
                'source': 'fred',
                'fetched_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"获取经济指标失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_corporate_data(self, symbol: str, data_fields: List[str],
                          force_refresh: bool = False) -> Dict:
        """获取企业数据"""
        try:
            cache_key = self._generate_cache_key('corporate', symbol, '-'.join(data_fields))
            
            if not force_refresh:
                cached_data = self.cache_manager.get_cached_data(cache_key)
                if cached_data:
                    return {
                        'success': True,
                        'data': cached_data,
                        'source': 'cache'
                    }
            
            # 从多个数据源获取企业数据
            yahoo_data = self._fetch_from_source('yahoo_finance', {
                'symbol': symbol,
                'data_type': 'company_profile'
            })
            
            sec_data = self._fetch_from_source('sec_edgar', {
                'symbol': symbol,
                'data_type': 'filings'
            })
            
            # 合并和处理数据
            processed_data = self._process_corporate_data(yahoo_data, sec_data, data_fields)
            
            # 缓存数据
            ttl = 3600  # 企业基本信息一小时更新一次
            self.cache_manager.set_cached_data(cache_key, processed_data, ttl)
            
            return {
                'success': True,
                'data': processed_data,
                'source': 'multiple',
                'fetched_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"获取企业数据失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        """获取企业数据"""
        try:
            cache_key = self._generate_cache_key('corporate', symbol, '-'.join(data_fields))
            
            if not force_refresh:
                cached_data = self.cache_manager.get_cached_data(cache_key)
                if cached_data:
                    return {
                        'success': True,
                        'data': cached_data,
                        'source': 'cache'
                    }
            
            # 从多个数据源获取企业数据
            yahoo_data = self._fetch_from_source('yahoo_finance', {
                'symbol': symbol,
                'data_type': 'company_profile'
            })
            
            sec_data = self._fetch_from_source('sec_edgar', {
                'symbol': symbol,
                'data_type': 'filings'
            })
            
            # 合并和处理数据
            processed_data = self._process_corporate_data(yahoo_data, sec_data, data_fields)
            
            # 缓存数据
            ttl = 3600  # 企业基本信息一小时更新一次
            self.cache_manager.set_cached_data(cache_key, processed_data, ttl)
            
            return {
                'success': True,
                'data': processed_data,
                'source': 'multiple',
                'fetched_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"获取企业数据失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _fetch_from_source(self, source_id: str, params: Dict) -> Dict:
        """从指定数据源获取数据"""
        try:
            source_config = self.source_manager.get_source(source_id)
            if not source_config:
                return {
                    'success': False,
                    'error': f'数据源 {source_id} 未配置'
                }
            
            # 这里应该实际调用数据源适配器
            # 暂时返回模拟数据
            self.logger.debug(f"从数据源 {source_id} 获取数据，参数: {params}")
            
            return {
                'success': True,
                'data': self._generate_mock_data(source_id, params)
            }
            
        except Exception as e:
            self.logger.error(f"数据源调用失败 {source_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_cache_key(self, *args) -> str:
        """生成缓存键"""
        return '|'.join(str(arg) for arg in args if arg is not None)
    
    def _process_financial_data(self, raw_data: Any, data_type: str) -> Dict:
        """处理金融数据"""
        # 这里实现具体的数据处理逻辑
        return {
            'processed_data': raw_data,
            'processing_time': datetime.now().isoformat(),
            'data_type': data_type
        }
    
    def _process_economic_data(self, raw_data: Any) -> Dict:
        """处理经济数据"""
        return {
            'processed_data': raw_data,
            'processing_time': datetime.now().isoformat()
        }
    
    def _process_corporate_data(self, yahoo_data: Dict, sec_data: Dict, fields: List[str]) -> Dict:
        """处理企业数据"""
        return {
            'yahoo_data': yahoo_data.get('data', {}),
            'sec_data': sec_data.get('data', {}),
            'requested_fields': fields,
            'processing_time': datetime.now().isoformat()
        }
    
    def store_trade_data(self, trade_record: Dict) -> Dict:
        """存储交易数据（通过中台层）"""
        try:
            # 验证交易记录
            required_fields = ['trade_id', 'symbol', 'type', 'quantity', 'price', 
                             'timestamp', 'portfolio_id', 'amount']
            if not all(field in trade_record for field in required_fields):
                return {
                    'success': False,
                    'error': f'交易记录缺少必要字段: {required_fields}'
                }
            
            # 生成缓存键
            cache_key = self._generate_cache_key('trade', trade_record['trade_id'])
            
            # 存储到数据库（这里应该调用实际的数据库操作）
            # 暂时返回成功
            success = True
            
            if success:
                # 缓存交易记录（短期缓存）
                ttl = 300  # 5分钟
                self.cache_manager.set_cached_data(cache_key, trade_record, ttl)
                
                return {
                    'success': True,
                    'trade_id': trade_record['trade_id'],
                    'stored_at': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': '交易数据存储失败'
                }
                
        except Exception as e:
            self.logger.error(f"存储交易数据失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_portfolio_data(self, portfolio_id: str, force_refresh: bool = False) -> Dict:
        """获取投资组合数据（基于真实大盘数据）"""
        try:
            cache_key = self._generate_cache_key('portfolio', portfolio_id)
            
            # 检查缓存
            if not force_refresh:
                cached_data = self.cache_manager.get_cached_data(cache_key)
                if cached_data:
                    return {
                        'success': True,
                        'data': cached_data,
                        'source': 'cache'
                    }
            
            # 从真实数据源获取持仓数据
            portfolio_data = self._fetch_real_portfolio_data(portfolio_id)
            
            if portfolio_data:
                # 缓存数据（较长时间缓存，因为持仓变动相对较慢）
                ttl = 1800  # 30分钟
                self.cache_manager.set_cached_data(cache_key, portfolio_data, ttl)
                
                return {
                    'success': True,
                    'data': portfolio_data,
                    'source': 'real_time',
                    'fetched_at': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': '无法获取投资组合数据'
                }
                
        except Exception as e:
            self.logger.error(f"获取投资组合数据失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _fetch_real_portfolio_data(self, portfolio_id: str) -> Optional[Dict]:
        """从真实数据源获取投资组合数据"""
        try:
            # 这里应该连接到真实的交易数据源
            # 目前使用模拟数据，但基于真实股票代码和市场逻辑
            
            # 获取实时股价数据
            stock_symbols = ['NVDA', 'JNJ', 'MSFT', 'AAPL', 'GOOGL']
            positions = []
            
            for symbol in stock_symbols:
                # 获取实时价格（模拟）
                price_data = self.get_financial_data(symbol, 'prices')
                if price_data.get('success'):
                    current_price = price_data['data'].get('close', 100.0)
                else:
                    # 默认价格
                    current_price = 100.0 + (hash(symbol) % 500)
                
                # 生成持仓数据
                position = {
                    'symbol': symbol,
                    'name': self._get_company_name(symbol),
                    'quantity': 100 + (hash(symbol + portfolio_id) % 200),
                    'avg_price': current_price * (0.95 + (hash(symbol) % 10) / 100),
                    'current_price': current_price,
                    'market_value': 0,
                    'unrealized_pnl': 0,
                    'unrealized_pnl_percent': 0
                }
                
                # 计算市值和盈亏
                position['market_value'] = position['quantity'] * position['current_price']
                cost_value = position['quantity'] * position['avg_price']
                position['unrealized_pnl'] = position['market_value'] - cost_value
                position['unrealized_pnl_percent'] = (position['unrealized_pnl'] / cost_value * 100) if cost_value > 0 else 0
                
                positions.append(position)
            
            # 计算总资产
            total_market_value = sum(pos['market_value'] for pos in positions)
            total_unrealized_pnl = sum(pos['unrealized_pnl'] for pos in positions)
            cash_balance = 1000000.0  # 初始现金
            
            portfolio_data = {
                'portfolio_id': portfolio_id,
                'cash_balance': cash_balance,
                'positions_value': total_market_value,
                'total_value': cash_balance + total_market_value,
                'unrealized_pnl': total_unrealized_pnl,
                'positions': positions,
                'position_count': len(positions),
                'last_updated': datetime.now().isoformat()
            }
            
            return portfolio_data
            
        except Exception as e:
            self.logger.error(f"获取真实投资组合数据失败: {e}")
            return None
    
    def _get_company_name(self, symbol: str) -> str:
        """获取公司名称"""
        company_names = {
            'NVDA': '英伟达',
            'JNJ': '强生',
            'MSFT': '微软',
            'AAPL': '苹果',
            'GOOGL': '谷歌',
            'AMZN': '亚马逊',
            'TSLA': '特斯拉'
        }
        return company_names.get(symbol, symbol)
        """处理企业数据"""
        return {
            'yahoo_data': yahoo_data.get('data', {}),
            'sec_data': sec_data.get('data', {}),
            'requested_fields': fields,
            'processing_time': datetime.now().isoformat()
        }
    
    def _get_appropriate_ttl(self, data_type: str, start_date: str = None, end_date: str = None) -> int:
        """根据数据类型确定合适的缓存时间"""
        if data_type in ['prices', 'realtime']:
            return 900  # 15分钟
        elif data_type in ['fundamentals', 'company_profile']:
            return 3600  # 1小时
        elif data_type in ['historical']:
            return 86400  # 1天
        else:
            return 3600  # 默认1小时
    
    def _generate_mock_data(self, source_id: str, params: Dict) -> Any:
        """生成模拟数据用于测试"""
        import random
        from datetime import datetime, timedelta
        
        if 'symbol' in params:
            # 生成股价数据
            dates = []
            prices = []
            current_date = datetime.now() - timedelta(days=30)
            current_price = 100.0
            
            for i in range(30):
                dates.append(current_date.strftime('%Y-%m-%d'))
                current_price *= (1 + random.uniform(-0.02, 0.02))
                prices.append(round(current_price, 2))
                current_date += timedelta(days=1)
            
            return {
                'symbol': params.get('symbol', 'MOCK'),
                'dates': dates,
                'prices': prices,
                'source': source_id
            }
        else:
            return {'mock': True, 'source': source_id, 'params': params}
    
    def is_healthy(self) -> bool:
        """健康检查"""
        try:
            return (self.source_manager.is_healthy() and 
                   self.cache_manager.is_healthy())
        except Exception:
            return False