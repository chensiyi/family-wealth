#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存数据库管理
负责存储缓存数据、缓存元信息和访问统计
"""

import sqlite3
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

class CacheDatabase:
    """缓存数据库管理器"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # 使用相对于data-hub模块的路径
            from pathlib import Path
            module_dir = Path(__file__).parent
            db_path = str(module_dir / 'cache.db')
        
        self.db_path = db_path
        self.connection = None
        self.logger = logging.getLogger(__name__)
        self._connect()
        self._initialize_schema()
    
    def _connect(self):
        """建立数据库连接"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            self.connection.execute('PRAGMA journal_mode=WAL')  # 启用WAL模式提高并发性能
            self.logger.info(f"✅ 缓存数据库连接成功: {self.db_path}")
        except Exception as e:
            self.logger.error(f"❌ 缓存数据库连接失败: {e}")
            raise
    
    def _initialize_schema(self):
        """初始化数据库表结构"""
        try:
            cursor = self.connection.cursor()
            
            # 缓存数据表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cache_entries (
                    cache_key TEXT PRIMARY KEY,
                    data BLOB NOT NULL,
                    expires_at TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    accessed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    access_count INTEGER DEFAULT 0,
                    data_size INTEGER NOT NULL,
                    source_id TEXT,
                    cache_type TEXT DEFAULT 'general'
                )
            ''')
            
            # 缓存统计表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cache_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stat_type TEXT NOT NULL,
                    stat_key TEXT,
                    stat_value REAL,
                    recorded_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 访问日志表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cache_access_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cache_key TEXT,
                    access_type TEXT,  -- hit, miss, set, delete
                    source_ip TEXT,
                    user_agent TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (cache_key) REFERENCES cache_entries (cache_key)
                )
            ''')
            
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_cache_entries_expires ON cache_entries(expires_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_cache_entries_accessed ON cache_entries(accessed_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_cache_entries_source ON cache_entries(source_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_cache_access_log_key ON cache_access_log(cache_key)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_cache_access_log_time ON cache_access_log(timestamp)')
            
            self.connection.commit()
            self.logger.info("✅ 缓存数据库表结构初始化完成")
            
        except Exception as e:
            self.logger.error(f"❌ 缓存数据库表结构初始化失败: {e}")
            raise
    
    def get_cached_data(self, cache_key: str) -> Optional[Dict]:
        """获取缓存数据"""
        try:
            cursor = self.connection.cursor()
            
            # 查询缓存数据
            cursor.execute('''
                SELECT cache_key, data, expires_at, created_at, accessed_at, 
                       access_count, data_size, source_id
                FROM cache_entries 
                WHERE cache_key = ?
            ''', (cache_key,))
            
            row = cursor.fetchone()
            if not row:
                self._log_cache_access(cache_key, 'miss')
                return None
            
            # 更新访问时间和计数
            cursor.execute('''
                UPDATE cache_entries 
                SET accessed_at = ?, access_count = access_count + 1
                WHERE cache_key = ?
            ''', (datetime.now().isoformat(), cache_key))
            
            self.connection.commit()
            self._log_cache_access(cache_key, 'hit')
            
            return {
                'cache_key': row['cache_key'],
                'data': row['data'],
                'expires_at': row['expires_at'],
                'created_at': row['created_at'],
                'accessed_at': row['accessed_at'],
                'access_count': row['access_count'],
                'data_size': row['data_size'],
                'source_id': row['source_id']
            }
            
        except Exception as e:
            self.logger.error(f"获取缓存数据失败: {e}")
            return None
    
    def set_cached_data(self, cache_key: str, data: bytes, expires_at: str, 
                       data_size: int, source_id: str = None, cache_type: str = 'general') -> bool:
        """设置缓存数据"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO cache_entries 
                (cache_key, data, expires_at, created_at, accessed_at, 
                 access_count, data_size, source_id, cache_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                cache_key, data, expires_at, datetime.now().isoformat(),
                datetime.now().isoformat(), 0, data_size, source_id, cache_type
            ))
            
            self.connection.commit()
            self._log_cache_access(cache_key, 'set')
            return True
            
        except Exception as e:
            self.logger.error(f"设置缓存数据失败: {e}")
            return False
    
    def delete_cached_data(self, cache_key: str) -> bool:
        """删除缓存数据"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('DELETE FROM cache_entries WHERE cache_key = ?', (cache_key,))
            self.connection.commit()
            self._log_cache_access(cache_key, 'delete')
            return cursor.rowcount > 0
            
        except Exception as e:
            self.logger.error(f"删除缓存数据失败: {e}")
            return False
    
    def clear_expired_cache(self) -> int:
        """清理过期缓存"""
        try:
            cursor = self.connection.cursor()
            current_time = datetime.now().isoformat()
            
            # 查询过期的缓存键
            cursor.execute('SELECT cache_key FROM cache_entries WHERE expires_at < ?', (current_time,))
            expired_keys = [row[0] for row in cursor.fetchall()]
            
            # 删除过期缓存
            cursor.execute('DELETE FROM cache_entries WHERE expires_at < ?', (current_time,))
            deleted_count = cursor.rowcount
            
            # 记录删除日志
            for key in expired_keys:
                self._log_cache_access(key, 'expire')
            
            self.connection.commit()
            self.logger.info(f"清理过期缓存: {deleted_count} 条")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"清理过期缓存失败: {e}")
            return 0
    
    def get_cache_stats(self) -> Dict:
        """获取缓存统计信息"""
        try:
            cursor = self.connection.cursor()
            
            # 总缓存条目数
            cursor.execute('SELECT COUNT(*) as total FROM cache_entries')
            total_entries = cursor.fetchone()['total']
            
            # 总缓存大小
            cursor.execute('SELECT COALESCE(SUM(data_size), 0) as size FROM cache_entries')
            total_size = cursor.fetchone()['size']
            
            # 过期缓存数
            current_time = datetime.now().isoformat()
            cursor.execute('SELECT COUNT(*) as expired FROM cache_entries WHERE expires_at < ?', (current_time,))
            expired_count = cursor.fetchone()['expired']
            
            # 缓存命中统计（最近24小时）
            since_time = (datetime.now() - timedelta(hours=24)).isoformat()
            cursor.execute('''
                SELECT access_type, COUNT(*) as count
                FROM cache_access_log 
                WHERE timestamp >= ? AND access_type IN ('hit', 'miss')
                GROUP BY access_type
            ''', (since_time,))
            
            hit_stats = {row['access_type']: row['count'] for row in cursor.fetchall()}
            hit_count = hit_stats.get('hit', 0)
            miss_count = hit_stats.get('miss', 0)
            hit_rate = hit_count / (hit_count + miss_count) if (hit_count + miss_count) > 0 else 0
            
            return {
                'total_entries': total_entries,
                'total_size': total_size,
                'expired_count': expired_count,
                'active_entries': total_entries - expired_count,
                'hit_count': hit_count,
                'miss_count': miss_count,
                'hit_rate': round(hit_rate, 4)
            }
            
        except Exception as e:
            self.logger.error(f"获取缓存统计失败: {e}")
            return {}
    
    def get_source_cache_keys(self, source_id: str) -> List[str]:
        """获取指定数据源的所有缓存键"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT cache_key FROM cache_entries WHERE source_id = ?', (source_id,))
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"获取数据源缓存键失败: {e}")
            return []
    
    def get_largest_cache_entries(self, limit: int = 10) -> List[Dict]:
        """获取最大的缓存条目"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT cache_key, data_size, access_count, created_at
                FROM cache_entries 
                ORDER BY data_size DESC 
                LIMIT ?
            ''', (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"获取最大缓存条目失败: {e}")
            return []
    
    def _log_cache_access(self, cache_key: str, access_type: str):
        """记录缓存访问日志"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO cache_access_log (cache_key, access_type)
                VALUES (?, ?)
            ''', (cache_key, access_type))
        except Exception as e:
            # 访问日志记录失败不影响主要功能
            self.logger.debug(f"缓存访问日志记录失败: {e}")
    
    def record_statistic(self, stat_type: str, stat_key: str, stat_value: float) -> bool:
        """记录统计信息"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO cache_stats (stat_type, stat_key, stat_value)
                VALUES (?, ?, ?)
            ''', (stat_type, stat_key, stat_value))
            
            self.connection.commit()
            return True
        except Exception as e:
            self.logger.error(f"记录统计信息失败: {e}")
            return False
    
    def get_recent_statistics(self, stat_type: str, hours: int = 24) -> List[Dict]:
        """获取最近的统计数据"""
        try:
            cursor = self.connection.cursor()
            since_time = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            cursor.execute('''
                SELECT stat_key, stat_value, recorded_at
                FROM cache_stats 
                WHERE stat_type = ? AND recorded_at >= ?
                ORDER BY recorded_at DESC
            ''', (stat_type, since_time))
            
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"获取统计数据失败: {e}")
            return []
    
    def health_check(self) -> bool:
        """健康检查"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT 1')
            return cursor.fetchone() is not None
        except Exception:
            return False
    
    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            self.logger.info("缓存数据库连接已关闭")