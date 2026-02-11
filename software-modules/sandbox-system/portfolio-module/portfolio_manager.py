"""
投资组合管理器
Main portfolio management class that handles positions, transactions and risk metrics
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
import json
import logging
from decimal import Decimal

from position import Position
from transaction import Transaction, TransactionType
from risk_metrics import RiskMetrics

logger = logging.getLogger(__name__)

class PortfolioManager:
    """投资组合管理器"""
    
    def __init__(self, initial_cash: float = 100000.0, currency: str = "USD"):
        """
        初始化投资组合管理器
        
        Args:
            initial_cash: 初始现金
            currency: 货币类型
        """
        self.initial_cash = float(initial_cash)
        self.cash = float(initial_cash)
        self.currency = currency
        self.positions: Dict[str, Position] = {}
        self.transactions: List[Transaction] = []
        self.portfolio_history: List[Dict[str, Any]] = []
        self.risk_metrics = RiskMetrics()
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
        
        # 记录初始状态
        self._record_portfolio_state()
        
    @property
    def total_value(self) -> float:
        """总投资组合价值"""
        positions_value = sum(pos.market_value for pos in self.positions.values())
        return self.cash + positions_value
    
    @property
    def positions_value(self) -> float:
        """持仓总价值"""
        return sum(pos.market_value for pos in self.positions.values())
    
    @property
    def unrealized_pnl(self) -> float:
        """未实现盈亏总额"""
        return sum(pos.unrealized_pnl for pos in self.positions.values())
    
    @property
    def realized_pnl(self) -> float:
        """已实现盈亏总额"""
        return sum(t.amount for t in self.transactions if t.is_sell)
    
    def buy_stock(self, symbol: str, quantity: float, price: float, 
                  fees: float = 0.0, description: str = "") -> bool:
        """
        买入股票
        
        Args:
            symbol: 股票代码
            quantity: 买入数量
            price: 买入价格
            fees: 交易费用
            description: 交易描述
            
        Returns:
            bool: 交易是否成功
        """
        total_cost = (quantity * price) + fees
        
        if total_cost > self.cash:
            logger.error(f"资金不足: 需要${total_cost:.2f}, 可用${self.cash:.2f}")
            return False
        
        # 创建交易记录
        transaction = Transaction(
            symbol=symbol,
            transaction_type=TransactionType.BUY,
            quantity=quantity,
            price=price,
            fees=fees,
            description=description
        )
        
        # 更新现金
        self.cash -= total_cost
        
        # 更新或创建持仓
        symbol_upper = symbol.upper()
        if symbol_upper in self.positions:
            self.positions[symbol_upper].add_shares(quantity, price)
        else:
            self.positions[symbol_upper] = Position(symbol_upper, quantity, price)
        
        # 记录交易
        self.transactions.append(transaction)
        self.last_updated = datetime.now()
        
        # 记录投资组合状态
        self._record_portfolio_state()
        
        logger.info(f"买入成功: {transaction}")
        return True
    
    def sell_stock(self, symbol: str, quantity: float, price: float,
                   fees: float = 0.0, description: str = "") -> bool:
        """
        卖出股票
        
        Args:
            symbol: 股票代码
            quantity: 卖出数量
            price: 卖出价格
            fees: 交易费用
            description: 交易描述
            
        Returns:
            bool: 交易是否成功
        """
        symbol_upper = symbol.upper()
        
        if symbol_upper not in self.positions:
            logger.error(f"持仓不存在: {symbol}")
            return False
            
        position = self.positions[symbol_upper]
        if quantity > position.quantity:
            logger.error(f"卖出数量超过持仓: {quantity} > {position.quantity}")
            return False
        
        # 创建交易记录
        transaction = Transaction(
            symbol=symbol,
            transaction_type=TransactionType.SELL,
            quantity=quantity,
            price=price,
            fees=fees,
            description=description
        )
        
        # 计算收入
        proceeds = (quantity * price) - fees
        self.cash += proceeds
        
        # 更新持仓
        realized_pnl = position.remove_shares(quantity, price)
        
        # 如果持仓清空，移除该持仓
        if position.quantity == 0:
            del self.positions[symbol_upper]
        
        # 记录交易
        self.transactions.append(transaction)
        self.last_updated = datetime.now()
        
        # 记录投资组合状态
        self._record_portfolio_state()
        
        logger.info(f"卖出成功: {transaction}, 实现盈亏: ${realized_pnl:.2f}")
        return True
    
    def update_prices(self, prices: Dict[str, float]) -> None:
        """
        更新持仓价格
        
        Args:
            prices: 股票代码到价格的映射
        """
        updated_count = 0
        for symbol, price in prices.items():
            symbol_upper = symbol.upper()
            if symbol_upper in self.positions:
                self.positions[symbol_upper].update_price(price)
                updated_count += 1
        
        if updated_count > 0:
            self.last_updated = datetime.now()
            self._record_portfolio_state()
            logger.info(f"更新了{updated_count}个持仓的价格")
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """获取指定股票的持仓"""
        return self.positions.get(symbol.upper())
    
    def get_all_positions(self) -> List[Position]:
        """获取所有持仓"""
        return list(self.positions.values())
    
    def get_transactions(self, symbol: Optional[str] = None) -> List[Transaction]:
        """获取交易记录"""
        if symbol:
            return [t for t in self.transactions if t.symbol == symbol.upper()]
        return self.transactions.copy()
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """获取投资组合摘要"""
        positions_list = []
        for pos in self.positions.values():
            positions_list.append({
                'symbol': pos.symbol,
                'quantity': pos.quantity,
                'current_price': pos.current_price,
                'cost_basis': pos.cost_basis,
                'market_value': pos.market_value,
                'unrealized_pnl': pos.unrealized_pnl,
                'unrealized_pnl_percent': pos.unrealized_pnl_percent
            })
        
        return {
            'cash': self.cash,
            'positions_value': self.positions_value,
            'total_value': self.total_value,
            'unrealized_pnl': self.unrealized_pnl,
            'realized_pnl': self.realized_pnl,
            'total_pnl': self.unrealized_pnl + self.realized_pnl,
            'positions': positions_list,
            'position_count': len(self.positions),
            'transaction_count': len(self.transactions),
            'currency': self.currency,
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat()
        }
    
    def get_risk_metrics(self) -> Dict[str, Any]:
        """获取风险指标"""
        return self.risk_metrics.get_portfolio_metrics(self.portfolio_history)
    
    def _record_portfolio_state(self) -> None:
        """记录投资组合当前状态"""
        state = {
            'date': datetime.now(),
            'total_value': self.total_value,
            'cash': self.cash,
            'positions_value': self.positions_value,
            'unrealized_pnl': self.unrealized_pnl,
            'realized_pnl': self.realized_pnl
        }
        self.portfolio_history.append(state)
    
    def save_to_file(self, filepath: str) -> bool:
        """保存投资组合到文件"""
        try:
            data = {
                'initial_cash': self.initial_cash,
                'cash': self.cash,
                'currency': self.currency,
                'created_at': self.created_at.isoformat(),
                'positions': [pos.to_dict() for pos in self.positions.values()],
                'transactions': [txn.to_dict() for txn in self.transactions],
                'portfolio_history': [
                    {
                        'date': entry['date'].isoformat(),
                        'total_value': entry['total_value'],
                        'cash': entry['cash'],
                        'positions_value': entry['positions_value'],
                        'unrealized_pnl': entry['unrealized_pnl'],
                        'realized_pnl': entry['realized_pnl']
                    }
                    for entry in self.portfolio_history
                ]
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            logger.info(f"投资组合已保存到: {filepath}")
            return True
        except Exception as e:
            logger.error(f"保存投资组合失败: {e}")
            return False
    
    @classmethod
    def load_from_file(cls, filepath: str) -> Optional['PortfolioManager']:
        """从文件加载投资组合"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            portfolio = cls(
                initial_cash=data['initial_cash'],
                currency=data['currency']
            )
            
            portfolio.cash = data['cash']
            portfolio.created_at = datetime.fromisoformat(data['created_at'])
            
            # 加载持仓
            for pos_data in data['positions']:
                position = Position.from_dict(pos_data)
                portfolio.positions[position.symbol] = position
            
            # 加载交易
            for txn_data in data['transactions']:
                transaction = Transaction.from_dict(txn_data)
                portfolio.transactions.append(transaction)
            
            # 加载历史记录
            for hist_data in data['portfolio_history']:
                portfolio.portfolio_history.append({
                    'date': datetime.fromisoformat(hist_data['date']),
                    'total_value': hist_data['total_value'],
                    'cash': hist_data['cash'],
                    'positions_value': hist_data['positions_value'],
                    'unrealized_pnl': hist_data['unrealized_pnl'],
                    'realized_pnl': hist_data['realized_pnl']
                })
            
            portfolio.last_updated = datetime.now()
            logger.info(f"投资组合已从 {filepath} 加载")
            return portfolio
            
        except Exception as e:
            logger.error(f"加载投资组合失败: {e}")
            return None
    
    def __str__(self) -> str:
        return f"Portfolio(cash=${self.cash:.2f}, positions={len(self.positions)}, total=${self.total_value:.2f})"
    
    def __repr__(self) -> str:
        return f"PortfolioManager(initial_cash={self.initial_cash}, currency='{self.currency}')"