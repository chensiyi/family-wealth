#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存管理器
负责多级缓存的管理，包括内存缓存和磁盘缓存
"""

import hashlib
import json
import logging
import pickle
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
from storage.cache_db import CacheDatabase

class CacheManager:
    """多级缓存管理器"""
    
    def __init__(self, cache_db: CacheDatabase):
        self.cache_db = cache_db
        self.logger = logging.getLogger(__name__)
        self._memory_cache = {}  # 内存缓存
        self._memory_cache_size = 1000  # 内存缓存最大条目数
        
    def _generate_cache_key(self, *args, **kwargs) -> str:
        """生成缓存键"""
        # 将参数序列化并生成MD5哈希作为缓存键
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get_cached_data(self, cache_key: str) -> Optional[Any]:
        """从缓存获取数据"""
        try:
            # 1. 先检查内存缓存
            if cache_key in self._memory_cache:
                cached_item = self._memory_cache[cache_key]
                if not self._is_expired(cached_item['expires_at']):
                    self.logger.debug(f"内存缓存命中: {cache_key}")
                    return cached_item['data']
                else:
                    # 内存缓存过期，删除
                    del self._memory_cache[cache_key]
            
            # 2. 检查磁盘缓存
            disk_data = self.cache_db.get_cached_data(cache_key)
            if disk_data and not self._is_expired(disk_data['expires_at']):
                self.logger.debug(f"磁盘缓存命中: {cache_key}")
                
                # 反序列化数据
                try:
                    data = pickle.loads(disk_data['data'])
                except Exception:
                    # 如果pickle失败，尝试JSON反序列化
                    data = json.loads(disk_data['data'])
                
                # 更新内存缓存
                self._update_memory_cache(cache_key, data, disk_data['expires_at'])
                return data
            else:
                self.logger.debug(f"缓存未命中: {cache_key}")
                return None
                
        except Exception as e:
            self.logger.error(f"获取缓存数据失败: {e}")
            return None
    
    def set_cached_data(self, cache_key: str, data: Any, ttl: int = 3600) -> bool:
        """设置缓存数据"""
        try:
            # 计算过期时间
            expires_at = (datetime.now() + timedelta(seconds=ttl)).isoformat()
            
            # 1. 更新内存缓存
            self._update_memory_cache(cache_key, data, expires_at)
            
            # 2. 更新磁盘缓存
            try:
                # 尝试使用pickle序列化
                serialized_data = pickle.dumps(data)
            except Exception:
                # pickle失败则使用JSON序列化
                serialized_data = json.dumps(data, default=str).encode('utf-8')
            
            success = self.cache_db.set_cached_data(
                cache_key, serialized_data, expires_at, len(serialized_data)
            )
            
            if success:
                self.logger.debug(f"缓存设置成功: {cache_key}")
                return True
            else:
                self.logger.error(f"磁盘缓存设置失败: {cache_key}")
                return False
                
        except Exception as e:
            self.logger.error(f"设置缓存数据失败: {e}")
            return False
    
    def _update_memory_cache(self, cache_key: str, data: Any, expires_at: str):
        """更新内存缓存"""
        # 检查缓存大小，如果超过限制则清除最旧的条目
        if len(self._memory_cache) >= self._memory_cache_size:
            oldest_key = next(iter(self._memory_cache))
            del self._memory_cache[oldest_key]
        
        self._memory_cache[cache_key] = {
            'data': data,
            'expires_at': expires_at,
            'cached_at': datetime.now().isoformat()
        }
    
    def _is_expired(self, expires_at: str) -> bool:
        """检查缓存是否过期"""
        try:
            expire_time = datetime.fromisoformat(expires_at)
            return datetime.now() > expire_time
        except Exception:
            return True
    
    def invalidate_cache(self, cache_key: str) -> bool:
        """失效指定缓存"""
        try:
            # 删除内存缓存
            if cache_key in self._memory_cache:
                del self._memory_cache[cache_key]
            
            # 删除磁盘缓存
            success = self.cache_db.delete_cached_data(cache_key)
            
            if success:
                self.logger.debug(f"缓存失效成功: {cache_key}")
                return True
            else:
                self.logger.warning(f"磁盘缓存失效失败: {cache_key}")
                return False
                
        except Exception as e:
            self.logger.error(f"缓存失效失败: {e}")
            return False
    
    def clear_expired_cache(self) -> int:
        """清理过期缓存"""
        try:
            # 清理内存过期缓存
            expired_keys = []
            for key, item in self._memory_cache.items():
                if self._is_expired(item['expires_at']):
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._memory_cache[key]
            
            # 清理磁盘过期缓存
            disk_cleaned = self.cache_db.clear_expired_cache()
            
            total_cleaned = len(expired_keys) + disk_cleaned
            self.logger.info(f"清理过期缓存: {total_cleaned} 条")
            return total_cleaned
            
        except Exception as e:
            self.logger.error(f"清理过期缓存失败: {e}")
            return 0
    
    def get_cache_stats(self) -> Dict:
        """获取缓存统计信息"""
        try:
            disk_stats = self.cache_db.get_cache_stats()
            return {
                'memory_cache_size': len(self._memory_cache),
                'memory_cache_limit': self._memory_cache_size,
                'disk_cache_entries': disk_stats.get('total_entries', 0),
                'disk_cache_size': disk_stats.get('total_size', 0),
                'disk_cache_hits': disk_stats.get('hit_count', 0),
                'disk_cache_misses': disk_stats.get('miss_count', 0)
            }
        except Exception as e:
            self.logger.error(f"获取缓存统计失败: {e}")
            return {}
    
    def refresh_cache(self, source_id: str) -> bool:
        """刷新指定数据源的缓存"""
        try:
            # 查找属于该数据源的所有缓存键
            cache_keys = self.cache_db.get_source_cache_keys(source_id)
            
            # 失效所有相关缓存
            success_count = 0
            for cache_key in cache_keys:
                if self.invalidate_cache(cache_key):
                    success_count += 1
            
            self.logger.info(f"刷新数据源 {source_id} 缓存: {success_count}/{len(cache_keys)} 条")
            return success_count == len(cache_keys)
            
        except Exception as e:
            self.logger.error(f"刷新缓存失败: {e}")
            return False
    
    def batch_get_cached_data(self, cache_keys: list) -> Dict[str, Any]:
        """批量获取缓存数据"""
        results = {}
        for key in cache_keys:
            data = self.get_cached_data(key)
            if data is not None:
                results[key] = data
        return results
    
    def batch_set_cached_data(self, data_dict: Dict[str, Any], ttl: int = 3600) -> bool:
        """批量设置缓存数据"""
        try:
            success_count = 0
            for key, data in data_dict.items():
                if self.set_cached_data(key, data, ttl):
                    success_count += 1
            
            return success_count == len(data_dict)
        except Exception as e:
            self.logger.error(f"批量设置缓存失败: {e}")
            return False
    
    def is_healthy(self) -> bool:
        """健康检查"""
        try:
            return self.cache_db.health_check()
        except Exception:
            return False