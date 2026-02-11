#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据中台数据库初始化脚本
初始化元数据数据库和缓存数据库
"""

import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 添加当前目录到Python路径
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from storage.metadata_db import MetadataDatabase
from storage.cache_db import CacheDatabase

def setup_logging():
    """设置日志配置"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('data_hub_init.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def initialize_databases():
    """初始化数据中台数据库"""
    logger = logging.getLogger(__name__)
    logger.info("🚀 开始初始化数据中台数据库...")
    
    try:
        # 确保存储目录存在
        storage_dir = Path('storage')
        storage_dir.mkdir(exist_ok=True)
        
        # 初始化元数据数据库
        logger.info("📋 初始化元数据数据库...")
        metadata_db = MetadataDatabase('storage/metadata.db')
        
        # 初始化缓存数据库
        logger.info("💾 初始化缓存数据库...")
        cache_db = CacheDatabase('storage/cache.db')
        
        # 注册默认数据源
        logger.info("🔌 注册默认数据源...")
        default_sources = [
            {
                'source_id': 'fred',
                'name': 'Federal Reserve Economic Data',
                'description': '美联储经济数据库',
                'type': 'economic',
                'adapter_class': 'FredAdapter',
                'config': {
                    'base_url': 'https://api.stlouisfed.org',
                    'api_key': 'YOUR_FRED_API_KEY',
                    'rate_limit': 120
                }
            },
            {
                'source_id': 'yahoo_finance',
                'name': 'Yahoo Finance',
                'description': '雅虎财经数据',
                'type': 'financial',
                'adapter_class': 'YahooFinanceAdapter',
                'config': {
                    'base_url': 'https://query1.finance.yahoo.com',
                    'rate_limit': 2000
                }
            },
            {
                'source_id': 'sec_edgar',
                'name': 'SEC EDGAR Database',
                'description': '美国证券交易委员会数据库',
                'type': 'corporate',
                'adapter_class': 'SecEdgarAdapter',
                'config': {
                    'base_url': 'https://data.sec.gov',
                    'rate_limit': 10
                }
            },
            {
                'source_id': 'worldbank',
                'name': 'World Bank Open Data',
                'description': '世界银行开放数据',
                'type': 'economic',
                'adapter_class': 'WorldBankAdapter',
                'config': {
                    'base_url': 'http://api.worldbank.org',
                    'rate_limit': 150
                }
            }
        ]
        
        # 注册数据源
        registered_count = 0
        for source in default_sources:
            if metadata_db.save_data_source(source):
                logger.info(f"✅ 注册数据源: {source['name']}")
                registered_count += 1
            else:
                logger.error(f"❌ 注册数据源失败: {source['name']}")
        
        # 设置默认系统配置
        logger.info("⚙️ 设置系统配置...")
        system_configs = [
            ('cache.default_ttl', '3600', '默认缓存时间（秒）'),
            ('cache.memory_limit', '100MB', '内存缓存限制'),
            ('cache.disk_limit', '1GB', '磁盘缓存限制'),
            ('api.rate_limit', '1000', 'API请求频率限制'),
            ('scheduler.enabled', 'true', '调度器启用状态')
        ]
        
        for key, value, desc in system_configs:
            if metadata_db.save_system_config(key, value, desc):
                logger.info(f"✅ 设置配置: {key} = {value}")
            else:
                logger.error(f"❌ 设置配置失败: {key}")
        
        # 验证数据库健康状态
        logger.info("🔍 验证数据库健康状态...")
        if metadata_db.health_check() and cache_db.health_check():
            logger.info("✅ 数据库初始化成功！")
            
            # 输出统计信息
            stats = cache_db.get_cache_stats()
            logger.info(f"📊 缓存统计: {stats}")
            logger.info(f"📊 已注册数据源: {registered_count} 个")
            
            return True
        else:
            logger.error("❌ 数据库健康检查失败")
            return False
            
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        return False
    finally:
        # 关闭数据库连接
        try:
            if 'metadata_db' in locals():
                metadata_db.close()
            if 'cache_db' in locals():
                cache_db.close()
        except:
            pass

def main():
    """主函数"""
    setup_logging()
    
    print("=" * 50)
    print("家族财富数据中台数据库初始化")
    print("=" * 50)
    
    success = initialize_databases()
    
    print("=" * 50)
    if success:
        print("✅ 数据库初始化完成！")
        print("📁 数据库文件位置:")
        print("   - 元数据数据库: storage/metadata.db")
        print("   - 缓存数据库: storage/cache.db")
        print("📊 可用数据源:")
        print("   - FRED 经济数据")
        print("   - Yahoo Finance 金融数据")
        print("   - SEC EDGAR 企业数据")
        print("   - World Bank 世界经济数据")
    else:
        print("❌ 数据库初始化失败，请查看日志文件")
    print("=" * 50)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)