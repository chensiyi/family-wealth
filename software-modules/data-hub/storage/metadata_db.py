#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
元数据数据库管理
负责存储数据源配置、系统配置等元数据信息
"""

import sqlite3
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime

class MetadataDatabase:
    """元数据数据库管理器"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # 使用相对于data-hub模块的路径
            from pathlib import Path
            module_dir = Path(__file__).parent
            db_path = str(module_dir / 'metadata.db')
        
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
            self.logger.info(f"✅ 元数据数据库连接成功: {self.db_path}")
        except Exception as e:
            self.logger.error(f"❌ 元数据数据库连接失败: {e}")
            raise
    
    def _initialize_schema(self):
        """初始化数据库表结构"""
        try:
            cursor = self.connection.cursor()
            
            # 数据源配置表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS data_sources (
                    source_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    type TEXT NOT NULL,
                    adapter_class TEXT NOT NULL,
                    config TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT,
                    updated_at TEXT,
                    last_tested TEXT,
                    test_result TEXT
                )
            ''')
            
            # 系统配置表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_config (
                    config_key TEXT PRIMARY KEY,
                    config_value TEXT,
                    description TEXT,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 数据访问日志表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS access_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_id TEXT,
                    operation TEXT,
                    status TEXT,
                    request_params TEXT,
                    response_time INTEGER,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (source_id) REFERENCES data_sources (source_id)
                )
            ''')
            
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_data_sources_status ON data_sources(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_access_logs_timestamp ON access_logs(timestamp)')
            
            self.connection.commit()
            self.logger.info("✅ 元数据数据库表结构初始化完成")
            
        except Exception as e:
            self.logger.error(f"❌ 数据库表结构初始化失败: {e}")
            raise
    
    def save_data_source(self, source_config: Dict) -> bool:
        """保存数据源配置"""
        try:
            cursor = self.connection.cursor()
            
            # 序列化复杂配置
            config_json = json.dumps(source_config.get('config', {}))
            
            cursor.execute('''
                INSERT OR REPLACE INTO data_sources 
                (source_id, name, description, type, adapter_class, config, 
                 status, created_at, updated_at, last_tested, test_result)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                source_config['source_id'],
                source_config['name'],
                source_config.get('description', ''),
                source_config['type'],
                source_config['adapter_class'],
                config_json,
                source_config.get('status', 'active'),
                source_config.get('created_at'),
                source_config.get('updated_at'),
                source_config.get('last_tested'),
                source_config.get('test_result')
            ))
            
            self.connection.commit()
            return True
            
        except Exception as e:
            self.logger.error(f"保存数据源配置失败: {e}")
            return False
    
    def get_data_source(self, source_id: str) -> Optional[Dict]:
        """获取数据源配置"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT * FROM data_sources WHERE source_id = ?', (source_id,))
            row = cursor.fetchone()
            
            if row:
                # 反序列化配置
                config = json.loads(row['config']) if row['config'] else {}
                return {
                    'source_id': row['source_id'],
                    'name': row['name'],
                    'description': row['description'],
                    'type': row['type'],
                    'adapter_class': row['adapter_class'],
                    'config': config,
                    'status': row['status'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at'],
                    'last_tested': row['last_tested'],
                    'test_result': row['test_result']
                }
            return None
            
        except Exception as e:
            self.logger.error(f"获取数据源配置失败: {e}")
            return None
    
    def get_all_data_sources(self) -> List[Dict]:
        """获取所有数据源配置"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT * FROM data_sources ORDER BY name')
            rows = cursor.fetchall()
            
            sources = []
            for row in rows:
                config = json.loads(row['config']) if row['config'] else {}
                sources.append({
                    'source_id': row['source_id'],
                    'name': row['name'],
                    'description': row['description'],
                    'type': row['type'],
                    'adapter_class': row['adapter_class'],
                    'config': config,
                    'status': row['status'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at'],
                    'last_tested': row['last_tested'],
                    'test_result': row['test_result']
                })
            
            return sources
            
        except Exception as e:
            self.logger.error(f"获取所有数据源配置失败: {e}")
            return []
    
    def update_data_source(self, source_id: str, updates: Dict) -> bool:
        """更新数据源配置"""
        try:
            cursor = self.connection.cursor()
            
            # 构建更新语句
            set_clauses = []
            values = []
            
            for key, value in updates.items():
                if key == 'config':
                    set_clauses.append('config = ?')
                    values.append(json.dumps(value))
                else:
                    set_clauses.append(f'{key} = ?')
                    values.append(value)
            
            set_clauses.append('updated_at = ?')
            values.append(datetime.now().isoformat())
            values.append(source_id)
            
            sql = f"UPDATE data_sources SET {', '.join(set_clauses)} WHERE source_id = ?"
            cursor.execute(sql, values)
            
            self.connection.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            self.logger.error(f"更新数据源配置失败: {e}")
            return False
    
    def delete_data_source(self, source_id: str) -> bool:
        """删除数据源配置"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('DELETE FROM data_sources WHERE source_id = ?', (source_id,))
            self.connection.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            self.logger.error(f"删除数据源配置失败: {e}")
            return False
    
    def save_system_config(self, key: str, value: str, description: str = '') -> bool:
        """保存系统配置"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO system_config 
                (config_key, config_value, description, updated_at)
                VALUES (?, ?, ?, ?)
            ''', (key, value, description, datetime.now().isoformat()))
            
            self.connection.commit()
            return True
            
        except Exception as e:
            self.logger.error(f"保存系统配置失败: {e}")
            return False
    
    def get_system_config(self, key: str) -> Optional[str]:
        """获取系统配置"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT config_value FROM system_config WHERE config_key = ?', (key,))
            row = cursor.fetchone()
            return row[0] if row else None
            
        except Exception as e:
            self.logger.error(f"获取系统配置失败: {e}")
            return None
    
    def log_access(self, source_id: str, operation: str, status: str, 
                   params: Dict = None, response_time: int = None) -> bool:
        """记录数据访问日志"""
        try:
            cursor = self.connection.cursor()
            params_json = json.dumps(params) if params else None
            
            cursor.execute('''
                INSERT INTO access_logs 
                (source_id, operation, status, request_params, response_time)
                VALUES (?, ?, ?, ?, ?)
            ''', (source_id, operation, status, params_json, response_time))
            
            self.connection.commit()
            return True
            
        except Exception as e:
            self.logger.error(f"记录访问日志失败: {e}")
            return False
    
    def get_access_stats(self, hours: int = 24) -> Dict:
        """获取访问统计"""
        try:
            cursor = self.connection.cursor()
            since_time = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            cursor.execute('''
                SELECT source_id, operation, status, COUNT(*) as count
                FROM access_logs 
                WHERE timestamp >= ?
                GROUP BY source_id, operation, status
            ''', (since_time,))
            
            stats = {}
            for row in cursor.fetchall():
                source_stats = stats.setdefault(row['source_id'], {})
                op_stats = source_stats.setdefault(row['operation'], {})
                op_stats[row['status']] = row['count']
            
            return stats
            
        except Exception as e:
            self.logger.error(f"获取访问统计失败: {e}")
            return {}
    
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
            self.logger.info("元数据数据库连接已关闭")