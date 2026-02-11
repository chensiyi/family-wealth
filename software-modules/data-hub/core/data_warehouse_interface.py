#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据仓库接口标准定义
为其他模块提供规范化数据访问和持久化接口
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from core.data_access_service import DataAccessService
from core.cache_manager import CacheManager
from storage.metadata_db import MetadataDatabase
import logging

class DataWarehouseInterface:
    """标准数据仓库接口
    
    提供统一的数据访问、存储和管理接口，确保各模块规范化获取数据
    """
    
    def __init__(self, data_access_service: DataAccessService, 
                 cache_manager: CacheManager,
                 metadata_db: MetadataDatabase):
        self.data_access_service = data_access_service
        self.cache_manager = cache_manager
        self.metadata_db = metadata_db
        self.logger = logging.getLogger(__name__)
    
    # ===== 标准数据访问接口 =====
    
    def get_market_data(self, symbol: str, 
                       data_type: str = 'prices',
                       start_date: str = None,
                       end_date: str = None,
                       force_refresh: bool = False) -> Dict:
        """获取市场数据（标准化接口）"""
        return self.data_access_service.get_financial_data(
            symbol, data_type, start_date, end_date, force_refresh
        )
    
    def get_economic_data(self, indicators: List[str],
                         country: str = 'US',
                         start_date: str = None,
                         end_date: str = None,
                         force_refresh: bool = False) -> Dict:
        """获取经济数据（标准化接口）"""
        return self.data_access_service.get_economic_indicators(
            indicators, country, start_date, end_date, force_refresh
        )
    
    def get_corporate_data(self, symbol: str,
                          data_fields: List[str] = None,
                          force_refresh: bool = False) -> Dict:
        """获取企业数据（标准化接口）"""
        if data_fields is None:
            data_fields = ['financials', 'profile', 'ownership']
        return self.data_access_service.get_corporate_data(
            symbol, data_fields, force_refresh
        )
    
    # ===== 交易数据接口 =====
    
    def store_trade_record(self, trade_data: Dict) -> Dict:
        """存储交易记录（通过中台层）"""
        try:
            # 验证交易数据格式
            required_fields = ['trade_id', 'symbol', 'type', 'quantity', 'price', 
                             'timestamp', 'portfolio_id']
            if not all(field in trade_data for field in required_fields):
                return {
                    'success': False,
                    'error': f'交易数据缺少必要字段: {required_fields}'
                }
            
            # 生成缓存键
            cache_key = f"trade:{trade_data['trade_id']}"
            
            # 存储到数据库（模拟成功）
            success = True
            
            if success:
                # 缓存交易记录（短期缓存）
                ttl = 3600  # 1小时
                self.cache_manager.set_cached_data(cache_key, trade_data, ttl)
                
                # 更新元数据
                self._update_metadata('trades', trade_data)
                
                return {
                    'success': True,
                    'trade_id': trade_data['trade_id'],
                    'stored_at': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': '数据库存储失败'
                }
                
        except Exception as e:
            self.logger.error(f"存储交易记录失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_trade_records(self, portfolio_id: str = None,
                         symbol: str = None,
                         start_date: str = None,
                         end_date: str = None,
                         limit: int = 100) -> Dict:
        """获取交易记录（标准化接口）"""
        try:
            # 构建查询条件
            query_conditions = {}
            if portfolio_id:
                query_conditions['portfolio_id'] = portfolio_id
            if symbol:
                query_conditions['symbol'] = symbol
            if start_date:
                query_conditions['timestamp >='] = start_date
            if end_date:
                query_conditions['timestamp <='] = end_date
            
            # 从数据库查询（模拟数据）
            mock_records = [
                {
                    'trade_id': 'TRD001',
                    'symbol': 'NVDA',
                    'type': 'BUY',
                    'quantity': 100,
                    'price': 850.00,
                    'timestamp': '2024-01-15T10:30:00',
                    'portfolio_id': 'PORT001',
                    'amount': -85000.00,
                    'fees': 10.00
                },
                {
                    'trade_id': 'TRD002',
                    'symbol': 'JNJ',
                    'type': 'BUY',
                    'quantity': 200,
                    'price': 150.00,
                    'timestamp': '2024-01-15T11:15:00',
                    'portfolio_id': 'PORT001',
                    'amount': -30000.00,
                    'fees': 8.00
                }
            ]
            
            # 缓存结果
            cache_key = f"trades:{portfolio_id or 'all'}:{symbol or 'all'}"
            self.cache_manager.set_cached_data(cache_key, mock_records, 300)  # 5分钟缓存
            
            return {
                'success': True,
                'records': mock_records,
                'count': len(mock_records),
                'queried_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"获取交易记录失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_portfolio_summary(self, portfolio_id: str) -> Dict:
        """获取投资组合摘要（标准化接口）"""
        try:
            # 获取持仓数据（模拟）
            positions = [
                {
                    'symbol': 'NVDA',
                    'name': '英伟达',
                    'quantity': 100,
                    'avg_price': 850.00,
                    'current_price': 875.28,
                    'market_value': 87528.00,
                    'unrealized_pnl': 2528.00,
                    'unrealized_pnl_percent': 2.97
                },
                {
                    'symbol': 'JNJ',
                    'name': '强生',
                    'quantity': 200,
                    'avg_price': 150.00,
                    'current_price': 152.40,
                    'market_value': 30480.00,
                    'unrealized_pnl': 480.00,
                    'unrealized_pnl_percent': 1.60
                }
            ]
            
            # 获取现金余额（模拟）
            cash_balance = 1000000.00
            
            # 计算总值
            total_value = cash_balance + sum(pos['market_value'] for pos in positions)
            
            return {
                'success': True,
                'portfolio_id': portfolio_id,
                'cash_balance': cash_balance,
                'positions_count': len(positions),
                'total_value': total_value,
                'positions': positions,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"获取投资组合摘要失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    # ===== 数据持久化接口 =====
    
    def persist_data(self, data_type: str, data: Dict, 
                    metadata: Dict = None) -> Dict:
        """持久化数据到数据仓库"""
        try:
            # 生成唯一标识符
            data_id = self._generate_data_id(data_type, data)
            
            # 存储到主数据库（模拟）
            success = True
            
            if success:
                # 更新元数据
                if metadata:
                    self._update_metadata(data_type, metadata, data_id)
                
                # 设置缓存
                cache_key = f"data:{data_type}:{data_id}"
                self.cache_manager.set_cached_data(cache_key, data, 86400)  # 默认1天缓存
                
                return {
                    'success': True,
                    'data_id': data_id,
                    'stored_at': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': '数据持久化失败'
                }
                
        except Exception as e:
            self.logger.error(f"数据持久化失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    # ===== 投资组合专用接口 =====
    
    def store_portfolio_data(self, portfolio_data: Dict) -> Dict:
        """存储投资组合数据到数据仓库"""
        try:
            # 验证数据完整性
            required_fields = ['portfolio_id', 'cash_balance', 'positions', 'total_value']
            if not all(field in portfolio_data for field in required_fields):
                return {
                    'success': False,
                    'error': f'投资组合数据缺少必要字段: {required_fields}'
                }
            
            # 生成唯一标识
            portfolio_id = portfolio_data['portfolio_id']
            timestamp = datetime.now().isoformat()
            
            # 准备存储数据
            storage_data = {
                'portfolio_id': portfolio_id,
                'data': portfolio_data,
                'timestamp': timestamp,
                'version': '1.0'
            }
            
            # 存储到本地数据库（这里应该调用实际的数据库操作）
            # 模拟存储成功
            success = True
            
            if success:
                # 缓存数据
                cache_key = f"portfolio_{portfolio_id}"
                ttl = 3600  # 1小时缓存
                self.cache_manager.set_cached_data(cache_key, storage_data, ttl)
                
                return {
                    'success': True,
                    'portfolio_id': portfolio_id,
                    'stored_at': timestamp,
                    'message': '投资组合数据存储成功'
                }
            else:
                return {
                    'success': False,
                    'error': '投资组合数据存储失败'
                }
                
        except Exception as e:
            self.logger.error(f"存储投资组合数据失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_portfolio_history(self, portfolio_id: str, days: int = 30) -> Dict:
        """获取投资组合历史数据"""
        try:
            # 从数据库获取历史数据
            # 这里应该查询历史记录表
            history_data = []
            
            # 模拟历史数据
            base_date = datetime.now() - timedelta(days=days)
            for i in range(days):
                date = base_date + timedelta(days=i)
                daily_data = {
                    'date': date.isoformat(),
                    'total_value': 1000000 + (i * 1000) + (hash(f"{portfolio_id}_{i}") % 50000),
                    'positions_value': 800000 + (i * 800) + (hash(f"pos_{portfolio_id}_{i}") % 40000),
                    'cash_balance': 200000 - (i * 200) + (hash(f"cash_{portfolio_id}_{i}") % 10000),
                    'unrealized_pnl': (i * 500) + (hash(f"pnl_{portfolio_id}_{i}") % 25000)
                }
                history_data.append(daily_data)
            
            return {
                'success': True,
                'portfolio_id': portfolio_id,
                'history_data': history_data,
                'count': len(history_data)
            }
            
        except Exception as e:
            self.logger.error(f"获取投资组合历史数据失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def store_transaction_data(self, transaction_data: Dict) -> Dict:
        """存储交易数据到数据仓库"""
        try:
            # 验证交易数据
            required_fields = ['transaction_id', 'portfolio_id', 'symbol', 'type', 
                             'quantity', 'price', 'timestamp']
            if not all(field in transaction_data for field in required_fields):
                return {
                    'success': False,
                    'error': f'交易数据缺少必要字段: {required_fields}'
                }
            
            # 生成交易记录
            transaction_record = {
                'transaction_id': transaction_data['transaction_id'],
                'portfolio_id': transaction_data['portfolio_id'],
                'symbol': transaction_data['symbol'],
                'type': transaction_data['type'],  # BUY/SELL
                'quantity': transaction_data['quantity'],
                'price': transaction_data['price'],
                'amount': transaction_data['quantity'] * transaction_data['price'],
                'timestamp': transaction_data['timestamp'],
                'fees': transaction_data.get('fees', 0),
                'description': transaction_data.get('description', '')
            }
            
            # 存储到数据库（模拟）
            success = True
            
            if success:
                # 缓存交易记录
                cache_key = f"transaction_{transaction_record['transaction_id']}"
                ttl = 86400  # 24小时缓存
                self.cache_manager.set_cached_data(cache_key, transaction_record, ttl)
                
                return {
                    'success': True,
                    'transaction_id': transaction_record['transaction_id'],
                    'stored_at': datetime.now().isoformat(),
                    'message': '交易数据存储成功'
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
