#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据中台主入口文件
Family Wealth Data Hub Main Entry Point
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
current_dir_str = str(current_dir)
if current_dir_str not in sys.path:
    sys.path.insert(0, current_dir_str)

from core.data_source_manager import DataSourceManager
from core.cache_manager import CacheManager
from core.data_access_service import DataAccessService
from storage.metadata_db import MetadataDatabase
from storage.cache_db import CacheDatabase
from utils.logger import setup_logger

class DataHub:
    """数据中台主类"""
    
    def __init__(self, config_path: str = None):
        """初始化数据中台"""
        self.logger = setup_logger('data_hub')
        self.logger.info("🚀 启动家族财富数据中台...")
        
        # 初始化存储层
        self.metadata_db = MetadataDatabase()
        self.cache_db = CacheDatabase()
        
        # 初始化核心服务
        self.source_manager = DataSourceManager(self.metadata_db)
        self.cache_manager = CacheManager(self.cache_db)
        self.data_service = DataAccessService(
            self.source_manager, 
            self.cache_manager
        )
        
        self.logger.info("✅ 数据中台初始化完成!")
        
    def get_data_access_service(self):
        """获取数据访问服务实例"""
        return self.data_service
        
    def get_source_manager(self):
        """获取数据源管理器实例"""
        return self.source_manager
        
    def get_cache_manager(self):
        """获取缓存管理器实例"""
        return self.cache_manager
        
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            # 检查数据库连接
            db_status = self.metadata_db.health_check() and self.cache_db.health_check()
            
            # 检查核心服务
            services_status = {
                'source_manager': self.source_manager.is_healthy(),
                'cache_manager': self.cache_manager.is_healthy(),
                'data_service': self.data_service.is_healthy()
            }
            
            overall_status = db_status and all(services_status.values())
            
            return {
                'status': 'healthy' if overall_status else 'unhealthy',
                'database': db_status,
                'services': services_status,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"健康检查失败: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

def main():
    """主函数"""
    try:
        # 创建数据中台实例
        hub = DataHub()
        
        print("📡 家族财富数据中台已启动")
        print("📊 可用服务:")
        print("  - 数据访问服务: hub.get_data_access_service()")
        print("  - 数据源管理: hub.get_source_manager()")
        print("  - 缓存管理: hub.get_cache_manager()")
        print("  - 健康检查: hub.health_check()")
        
        return hub
        
    except Exception as e:
        print(f"❌ 数据中台启动失败: {e}")
        return None

if __name__ == "__main__":
    data_hub = main()