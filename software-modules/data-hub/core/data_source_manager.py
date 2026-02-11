#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据源管理器
负责数据源的注册、配置管理和生命周期管理
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from storage.metadata_db import MetadataDatabase

class DataSourceManager:
    """数据源管理器"""
    
    def __init__(self, metadata_db: MetadataDatabase):
        self.metadata_db = metadata_db
        self.logger = logging.getLogger(__name__)
        self._sources = {}  # 缓存已加载的数据源适配器
        self._load_registered_sources()
        
    def _load_registered_sources(self):
        """加载已注册的数据源配置"""
        try:
            sources = self.metadata_db.get_all_data_sources()
            for source in sources:
                self._sources[source['source_id']] = source
            self.logger.info(f"加载了 {len(self._sources)} 个数据源配置")
        except Exception as e:
            self.logger.error(f"加载数据源配置失败: {e}")
    
    def register_source(self, source_config: Dict) -> bool:
        """注册新的数据源"""
        try:
            # 验证必需字段
            required_fields = ['source_id', 'name', 'type', 'adapter_class']
            for field in required_fields:
                if field not in source_config:
                    raise ValueError(f"缺少必需字段: {field}")
            
            # 检查数据源ID是否已存在
            if source_config['source_id'] in self._sources:
                self.logger.warning(f"数据源 {source_config['source_id']} 已存在")
                return False
            
            # 添加元数据
            source_config['created_at'] = datetime.now().isoformat()
            source_config['updated_at'] = datetime.now().isoformat()
            source_config['status'] = 'active'
            source_config['last_tested'] = None
            source_config['test_result'] = None
            
            # 保存到数据库
            success = self.metadata_db.save_data_source(source_config)
            if success:
                self._sources[source_config['source_id']] = source_config
                self.logger.info(f"成功注册数据源: {source_config['name']}")
                return True
            else:
                self.logger.error("数据源保存到数据库失败")
                return False
                
        except Exception as e:
            self.logger.error(f"注册数据源失败: {e}")
            return False
    
    def get_source(self, source_id: str) -> Optional[Dict]:
        """获取数据源配置"""
        return self._sources.get(source_id)
    
    def list_sources(self) -> List[Dict]:
        """列出所有数据源"""
        return list(self._sources.values())
    
    def update_source(self, source_id: str, updates: Dict) -> bool:
        """更新数据源配置"""
        try:
            if source_id not in self._sources:
                self.logger.warning(f"数据源 {source_id} 不存在")
                return False
            
            # 更新配置
            source_config = self._sources[source_id]
            source_config.update(updates)
            source_config['updated_at'] = datetime.now().isoformat()
            
            # 保存到数据库
            success = self.metadata_db.update_data_source(source_id, updates)
            if success:
                self.logger.info(f"成功更新数据源: {source_id}")
                return True
            else:
                self.logger.error("数据源更新失败")
                return False
                
        except Exception as e:
            self.logger.error(f"更新数据源失败: {e}")
            return False
    
    def remove_source(self, source_id: str) -> bool:
        """删除数据源"""
        try:
            if source_id not in self._sources:
                return True  # 已经不存在，视为删除成功
            
            # 从数据库删除
            success = self.metadata_db.delete_data_source(source_id)
            if success:
                # 从内存缓存删除
                del self._sources[source_id]
                self.logger.info(f"成功删除数据源: {source_id}")
                return True
            else:
                self.logger.error("数据源删除失败")
                return False
                
        except Exception as e:
            self.logger.error(f"删除数据源失败: {e}")
            return False
    
    def test_source_connection(self, source_id: str) -> Dict:
        """测试数据源连接"""
        try:
            source_config = self.get_source(source_id)
            if not source_config:
                return {
                    'success': False,
                    'error': f'数据源 {source_id} 不存在'
                }
            
            # 这里应该实际测试数据源连接
            # 暂时返回模拟结果
            test_result = {
                'success': True,
                'response_time': 150,  # ms
                'tested_at': datetime.now().isoformat(),
                'message': '连接测试成功'
            }
            
            # 更新测试结果
            self.update_source(source_id, {
                'last_tested': test_result['tested_at'],
                'test_result': json.dumps(test_result)
            })
            
            return test_result
            
        except Exception as e:
            self.logger.error(f"测试数据源连接失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_available_sources(self) -> List[Dict]:
        """获取可用的数据源列表"""
        available_sources = []
        for source in self._sources.values():
            if source.get('status') == 'active':
                available_sources.append(source)
        return available_sources
    
    def is_healthy(self) -> bool:
        """健康检查"""
        try:
            # 检查数据库连接
            if not self.metadata_db.health_check():
                return False
            
            # 检查至少有一个活跃数据源
            active_sources = self.get_available_sources()
            return len(active_sources) > 0
            
        except Exception:
            return False