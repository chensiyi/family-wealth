#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据中台功能测试脚本
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from core.data_access_service import DataAccessService
from core.data_source_manager import DataSourceManager
from core.cache_manager import CacheManager
from core.data_warehouse_interface import DataWarehouseInterface
from storage.cache_db import CacheDatabase
from storage.metadata_db import MetadataDatabase

def test_data_hub_functions():
    """测试数据中台核心功能"""
    print("🚀 开始测试数据中台功能...")
    
    try:
        # 初始化组件
        print("1. 初始化数据源管理器...")
        source_manager = DataSourceManager()
        print("✅ 数据源管理器初始化成功")
        
        print("2. 初始化缓存数据库...")
        cache_db = CacheDatabase()
        print("✅ 缓存数据库初始化成功")
        
        print("3. 初始化元数据数据库...")
        metadata_db = MetadataDatabase()
        print("✅ 元数据数据库初始化成功")
        
        print("4. 初始化缓存管理器...")
        cache_manager = CacheManager(cache_db)
        print("✅ 缓存管理器初始化成功")
        
        print("5. 初始化数据访问服务...")
        data_service = DataAccessService(source_manager, cache_manager)
        print("✅ 数据访问服务初始化成功")
        
        print("6. 初始化数据仓库接口...")
        warehouse = DataWarehouseInterface(data_service, cache_manager, metadata_db)
        print("✅ 数据仓库接口初始化成功")
        
        # 测试投资组合数据获取
        print("\n7. 测试投资组合数据获取...")
        portfolio_result = data_service.get_portfolio_data('test_portfolio_001')
        print(f"📊 投资组合数据获取结果: {portfolio_result['success']}")
        if portfolio_result['success']:
            data = portfolio_result['data']
            print(f"   - 现金余额: ${data['cash_balance']:,.2f}")
            print(f"   - 持仓价值: ${data['positions_value']:,.2f}")
            print(f"   - 总资产: ${data['total_value']:,.2f}")
            print(f"   - 未实现盈亏: ${data['unrealized_pnl']:,.2f}")
            print(f"   - 持仓数量: {data['position_count']}")
            print(f"   - 数据来源: {portfolio_result['source']}")
        
        # 测试数据持久化
        print("\n8. 测试数据持久化功能...")
        portfolio_data = {
            'portfolio_id': 'test_portfolio_001',
            'cash_balance': 1000000.00,
            'positions': [
                {
                    'symbol': 'NVDA',
                    'name': '英伟达',
                    'quantity': 100,
                    'avg_price': 850.00,
                    'current_price': 875.28,
                    'market_value': 87528.00,
                    'unrealized_pnl': 2528.00,
                    'unrealized_pnl_percent': 2.97
                }
            ],
            'positions_value': 87528.00,
            'total_value': 1087528.00,
            'unrealized_pnl': 2528.00
        }
        
        persist_result = warehouse.store_portfolio_data(portfolio_data)
        print(f"💾 投资组合数据持久化结果: {persist_result['success']}")
        if persist_result['success']:
            print(f"   - 存储时间: {persist_result['stored_at']}")
            print(f"   - 消息: {persist_result['message']}")
        
        # 测试交易数据存储
        print("\n9. 测试交易数据存储...")
        transaction_data = {
            'transaction_id': 'txn_001',
            'portfolio_id': 'test_portfolio_001',
            'symbol': 'NVDA',
            'type': 'BUY',
            'quantity': 100,
            'price': 875.28,
            'timestamp': '2026-02-11T16:30:00',
            'fees': 10.00,
            'description': '买入英伟达股票'
        }
        
        trade_result = warehouse.store_transaction_data(transaction_data)
        print(f"💰 交易数据存储结果: {trade_result['success']}")
        if trade_result['success']:
            print(f"   - 交易ID: {trade_result['transaction_id']}")
            print(f"   - 存储时间: {trade_result['stored_at']}")
        
        # 测试投资组合历史数据
        print("\n10. 测试投资组合历史数据获取...")
        history_result = warehouse.get_portfolio_history('test_portfolio_001', days=7)
        print(f"📈 历史数据获取结果: {history_result['success']}")
        if history_result['success']:
            print(f"   - 历史记录数量: {history_result['count']}")
            if history_result['history_data']:
                latest = history_result['history_data'][-1]
                print(f"   - 最新总价值: ${latest['total_value']:,.2f}")
                print(f"   - 最新日期: {latest['date'][:10]}")
        
        print("\n🎉 所有测试完成!")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_data_hub_functions()