#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
沙盒系统数据中台适配器
将沙盒系统数据访问重定向到数据中台模块
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Any

# 延迟导入，避免循环依赖
def get_data_hub():
    """延迟获取数据中台实例"""
    # 添加数据中台模块路径（相对于项目根目录）
    project_root = Path(__file__).parent.parent.parent
    data_hub_path = project_root / 'data-hub'
    
    if str(data_hub_path) not in sys.path:
        sys.path.insert(0, str(data_hub_path))
    
    # 直接导入而不是通过main模块
    import importlib.util
    main_path = data_hub_path / 'main.py'
    
    if not main_path.exists():
        raise FileNotFoundError(f"数据中台主文件不存在: {main_path}")
    
    spec = importlib.util.spec_from_file_location("data_hub_main", str(main_path))
    data_hub_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(data_hub_module)
    
    return data_hub_module.DataHub()

class SandboxDataHubAdapter:
    """沙盒系统数据中台适配器"""
    
    def __init__(self):
        """初始化适配器"""
        self._data_hub = None
        self._data_service = None
        self._source_manager = None
        self._cache_manager = None
    
    @property
    def data_hub(self):
        if self._data_hub is None:
            self._data_hub = get_data_hub()
        return self._data_hub
    
    @property
    def data_service(self):
        if self._data_service is None:
            self._data_service = self.data_hub.get_data_access_service()
        return self._data_service
    
    @property
    def source_manager(self):
        if self._source_manager is None:
            self._source_manager = self.data_hub.get_source_manager()
        return self._source_manager
    
    @property
    def cache_manager(self):
        if self._cache_manager is None:
            self._cache_manager = self.data_hub.get_cache_manager()
        return self._cache_manager
    
    def get_financial_data(self, symbol: str, data_type: str = 'prices',
                          start_date: str = None, end_date: str = None,
                          force_refresh: bool = False) -> Dict:
        """获取金融数据 - 适配沙盒系统接口"""
        return self.data_service.get_financial_data(
            symbol=symbol,
            data_type=data_type,
            start_date=start_date,
            end_date=end_date,
            force_refresh=force_refresh
        )
    
    def get_economic_indicators(self, indicators: List[str],
                               country: str = 'US',
                               start_date: str = None, end_date: str = None,
                               force_refresh: bool = False) -> Dict:
        """获取经济指标数据"""
        return self.data_service.get_economic_indicators(
            indicators=indicators,
            country=country,
            start_date=start_date,
            end_date=end_date,
            force_refresh=force_refresh
        )
    
    def get_corporate_data(self, symbol: str, data_fields: List[str],
                          force_refresh: bool = False) -> Dict:
        """获取企业数据"""
        return self.data_service.get_corporate_data(
            symbol=symbol,
            data_fields=data_fields,
            force_refresh=force_refresh
        )
    
    def get_sandbox_simulation_data(self, scenario_config: Dict) -> Dict:
        """获取沙盒模拟所需的基础数据"""
        try:
            # 获取必要的金融数据
            market_data = self.get_financial_data(
                symbol=scenario_config.get('benchmark_symbol', 'SPY'),
                data_type='prices',
                start_date=scenario_config.get('start_date'),
                end_date=scenario_config.get('end_date')
            )
            
            # 获取经济指标
            economic_data = self.get_economic_indicators(
                indicators=['GDP', 'UNRATE', 'CPIAUCSL'],
                start_date=scenario_config.get('start_date'),
                end_date=scenario_config.get('end_date')
            )
            
            return {
                'success': True,
                'market_data': market_data,
                'economic_data': economic_data,
                'scenario_config': scenario_config
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def health_check(self) -> Dict:
        """健康检查"""
        return self.data_hub.health_check()
    
    def get_available_data_sources(self) -> List[Dict]:
        """获取可用数据源列表"""
        return self.source_manager.list_sources()
    
    def clear_cache(self) -> bool:
        """清理缓存"""
        # 清理过期缓存
        cleaned_count = self.cache_manager.clear_expired_cache()
        return cleaned_count >= 0

# 兼容性包装器 - 保持原有接口
class LegacyDataAdapter:
    """遗留数据访问接口兼容包装器"""
    
    def __init__(self, adapter: SandboxDataHubAdapter):
        self.adapter = adapter
    
    def get_market_data(self, symbol: str, start_date: str = None, 
                       end_date: str = None, limit: int = None) -> List[Dict]:
        """兼容原有的市场数据获取接口"""
        result = self.adapter.get_financial_data(
            symbol=symbol,
            data_type='prices',
            start_date=start_date,
            end_date=end_date
        )
        
        if result['success']:
            # 转换为原有格式
            data = result['data']
            formatted_data = []
            for i, price in enumerate(data.get('prices', [])):
                formatted_data.append({
                    'symbol': symbol,
                    'date': data.get('dates', [])[i] if i < len(data.get('dates', [])) else '',
                    'price': price
                })
            return formatted_data[:limit] if limit else formatted_data
        else:
            return []
    
    def get_economic_data(self, indicator: str, start_date: str = None, 
                         end_date: str = None) -> List[Dict]:
        """兼容原有的经济数据获取接口"""
        result = self.adapter.get_economic_indicators(
            indicators=[indicator],
            start_date=start_date,
            end_date=end_date
        )
        
        if result['success']:
            return result['data'].get('processed_data', [])
        else:
            return []

# 工厂函数
def create_sandbox_data_adapter() -> SandboxDataHubAdapter:
    """创建沙盒数据适配器实例"""
    return SandboxDataHubAdapter()

def create_legacy_adapter() -> LegacyDataAdapter:
    """创建遗留接口适配器"""
    hub_adapter = SandboxDataHubAdapter()
    return LegacyDataAdapter(hub_adapter)