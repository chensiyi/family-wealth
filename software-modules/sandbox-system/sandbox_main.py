#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
沙盘系统主入口 - 集成实时交易大厅
Family Wealth Sandbox System Main Entry with Real Trading Hall Integration
"""

import sys
import os
from pathlib import Path
import logging
from datetime import datetime

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.append(str(Path(__file__).parent.parent / 'data-hub'))
sys.path.append(str(Path(__file__).parent / 'portfolio-module'))

# 导入模块
# 直接从portfolio-module目录导入
portfolio_module_path = Path(__file__).parent / 'portfolio-module'
sys.path.insert(0, str(portfolio_module_path))

from portfolio_manager import PortfolioManager
from utils.data_hub_adapter import create_sandbox_data_adapter, create_legacy_adapter

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sandbox_system.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class SandboxSystem:
    """沙盘系统主控制器"""
    
    def __init__(self):
        self.portfolio = None
        self.data_adapter = None
        self.legacy_adapter = None
        self.system_initialized = False
        self.start_time = datetime.now()
        
    def initialize_system(self, initial_cash: float = 1000000.0):
        """初始化沙盘系统"""
        try:
            logger.info("🚀 开始初始化沙盘系统...")
            
            # 1. 初始化投资组合管理器
            self.portfolio = PortfolioManager(initial_cash=initial_cash)
            logger.info(f"✅ 投资组合管理器初始化完成，初始资金: ${initial_cash:,.2f}")
            
            # 2. 初始化数据中台适配器
            self.data_adapter = create_sandbox_data_adapter()
            self.legacy_adapter = create_legacy_adapter()
            logger.info("✅ 数据中台适配器初始化完成")
            
            # 3. 系统健康检查
            health_status = self.data_adapter.health_check()
            logger.info(f"✅ 数据中台状态: {health_status['status']}")
            
            # 4. 加载历史数据（如果存在）
            self._load_existing_portfolio()
            
            self.system_initialized = True
            logger.info("✅ 沙盘系统初始化完成!")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 沙盘系统初始化失败: {e}")
            return False
    
    def _load_existing_portfolio(self):
        """加载已存在的投资组合数据"""
        portfolio_file = "portfolio_backup.json"
        if os.path.exists(portfolio_file):
            try:
                loaded_portfolio = PortfolioManager.load_from_file(portfolio_file)
                if loaded_portfolio:
                    self.portfolio = loaded_portfolio
                    logger.info(f"✅ 已加载历史投资组合数据")
            except Exception as e:
                logger.warning(f"⚠️ 加载历史投资组合失败: {e}")
    
    def get_system_status(self):
        """获取系统状态信息"""
        if not self.system_initialized:
            return {"status": "not_initialized", "message": "系统未初始化"}
        
        portfolio_summary = self.portfolio.get_portfolio_summary()
        health_status = self.data_adapter.health_check()
        
        return {
            "status": "running",
            "start_time": self.start_time.isoformat(),
            "runtime": str(datetime.now() - self.start_time),
            "portfolio_summary": portfolio_summary,
            "data_hub_status": health_status,
            "available_features": [
                "real_time_trading",
                "portfolio_management", 
                "risk_analysis",
                "market_data",
                "transaction_history"
            ]
        }
    
    def execute_trade(self, symbol: str, action: str, quantity: float, price: float, 
                     fees: float = 0.0, description: str = ""):
        """执行交易操作"""
        if not self.system_initialized:
            return {"success": False, "error": "系统未初始化"}
        
        try:
            if action.lower() == "buy":
                success = self.portfolio.buy_stock(symbol, quantity, price, fees, description)
                action_type = "买入"
            elif action.lower() == "sell":
                success = self.portfolio.sell_stock(symbol, quantity, price, fees, description)
                action_type = "卖出"
            else:
                return {"success": False, "error": "无效的操作类型"}
            
            if success:
                # 保存投资组合状态
                self.portfolio.save_to_file("portfolio_backup.json")
                logger.info(f"✅ {action_type}操作成功: {symbol} {quantity}@${price}")
                return {
                    "success": True,
                    "message": f"{action_type}成功",
                    "portfolio_summary": self.portfolio.get_portfolio_summary()
                }
            else:
                return {"success": False, "error": "交易执行失败"}
                
        except Exception as e:
            logger.error(f"❌ 交易执行异常: {e}")
            return {"success": False, "error": str(e)}
    
    def get_portfolio_positions(self):
        """获取持仓详情"""
        if not self.system_initialized:
            return {"success": False, "error": "系统未初始化"}
        
        positions = self.portfolio.get_all_positions()
        positions_data = []
        
        for pos in positions:
            positions_data.append({
                'symbol': pos.symbol,
                'quantity': pos.quantity,
                'cost_basis': pos.cost_basis,
                'current_price': pos.current_price,
                'market_value': pos.market_value,
                'unrealized_pnl': pos.unrealized_pnl,
                'unrealized_pnl_percent': pos.unrealized_pnl_percent
            })
        
        return {
            "success": True,
            "positions": positions_data,
            "summary": self.portfolio.get_portfolio_summary()
        }
    
    def get_transaction_history(self, symbol: str = None):
        """获取交易历史"""
        if not self.system_initialized:
            return {"success": False, "error": "系统未初始化"}
        
        transactions = self.portfolio.get_transactions(symbol)
        transactions_data = []
        
        for txn in transactions:
            transactions_data.append({
                'symbol': txn.symbol,
                'type': txn.type.value,
                'quantity': txn.quantity,
                'price': txn.price,
                'amount': abs(txn.amount),
                'fees': txn.fees,
                'timestamp': txn.timestamp.isoformat(),
                'description': txn.description
            })
        
        return {
            "success": True,
            "transactions": transactions_data,
            "count": len(transactions_data)
        }
    
    def update_market_prices(self, prices: dict):
        """更新市场价格"""
        if not self.system_initialized:
            return {"success": False, "error": "系统未初始化"}
        
        try:
            self.portfolio.update_prices(prices)
            self.portfolio.save_to_file("portfolio_backup.json")
            logger.info(f"✅ 市场价格更新完成: {len(prices)} 个标的")
            return {
                "success": True,
                "message": "价格更新成功",
                "portfolio_summary": self.portfolio.get_portfolio_summary()
            }
        except Exception as e:
            logger.error(f"❌ 价格更新失败: {e}")
            return {"success": False, "error": str(e)}
    
    def get_risk_analysis(self):
        """获取风险分析"""
        if not self.system_initialized:
            return {"success": False, "error": "系统未初始化"}
        
        try:
            risk_metrics = self.portfolio.get_risk_metrics()
            portfolio_summary = self.portfolio.get_portfolio_summary()
            
            return {
                "success": True,
                "risk_metrics": risk_metrics,
                "portfolio_summary": portfolio_summary
            }
        except Exception as e:
            logger.error(f"❌ 风险分析失败: {e}")
            return {"success": False, "error": str(e)}

def main():
    """主函数"""
    print("=" * 60)
    print("🏛️  家族财富管理系统 - 沙盘系统")
    print("=" * 60)
    
    # 创建沙盘系统实例
    sandbox = SandboxSystem()
    
    # 初始化系统
    if not sandbox.initialize_system(initial_cash=1000000.0):
        print("❌ 系统初始化失败，退出程序")
        return
    
    # 显示系统状态
    status = sandbox.get_system_status()
    print(f"\n✅ 系统启动成功!")
    print(f"🕒 启动时间: {status['start_time']}")
    print(f"💰 初始资金: ${status['portfolio_summary']['cash']:,.2f}")
    print(f"📊 可用功能: {', '.join(status['available_features'])}")
    
    # 简单的交互循环（演示用途）
    print(f"\n💡 系统已准备就绪，可通过API接口进行操作")
    print("🔧 可用的API方法:")
    print("  - sandbox.execute_trade(symbol, action, quantity, price)")
    print("  - sandbox.get_portfolio_positions()")
    print("  - sandbox.get_transaction_history()")
    print("  - sandbox.update_market_prices(prices_dict)")
    print("  - sandbox.get_risk_analysis()")
    print("  - sandbox.get_system_status()")
    
    return sandbox

if __name__ == "__main__":
    system = main()