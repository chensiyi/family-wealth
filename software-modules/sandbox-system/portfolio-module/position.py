"""
持仓对象类
Represents a single position in the portfolio
"""

from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class Position:
    """持仓对象，代表投资组合中的单个持仓"""
    
    def __init__(self, symbol: str, quantity: float, cost_basis: float, 
                 purchase_date: Optional[datetime] = None):
        """
        初始化持仓
        
        Args:
            symbol: 股票代码
            quantity: 持仓数量
            cost_basis: 成本基础（每股成本）
            purchase_date: 购买日期
        """
        self.symbol = symbol.upper()
        self.quantity = float(quantity)
        self.cost_basis = float(cost_basis)
        self.purchase_date = purchase_date or datetime.now()
        self.current_price = cost_basis  # 初始价格等于成本价
        self.last_updated = datetime.now()
        
    @property
    def market_value(self) -> float:
        """市场价值"""
        return self.quantity * self.current_price
    
    @property
    def cost_value(self) -> float:
        """成本价值"""
        return self.quantity * self.cost_basis
    
    @property
    def unrealized_pnl(self) -> float:
        """未实现盈亏"""
        return self.market_value - self.cost_value
    
    @property
    def unrealized_pnl_percent(self) -> float:
        """未实现盈亏百分比"""
        if self.cost_value == 0:
            return 0.0
        return (self.unrealized_pnl / self.cost_value) * 100
    
    def update_price(self, new_price: float) -> None:
        """更新当前价格"""
        old_price = self.current_price
        self.current_price = float(new_price)
        self.last_updated = datetime.now()
        logger.debug(f"更新 {self.symbol} 价格: {old_price} -> {new_price}")
    
    def add_shares(self, quantity: float, price: float) -> None:
        """增加持股数量（买入）"""
        if quantity <= 0:
            raise ValueError("买入数量必须大于0")
            
        total_cost = self.cost_value + (quantity * price)
        total_shares = self.quantity + quantity
        
        # 重新计算平均成本
        self.cost_basis = total_cost / total_shares
        self.quantity = total_shares
        self.current_price = price
        self.last_updated = datetime.now()
        
        logger.info(f"买入 {self.symbol}: {quantity}股 @ ${price:.2f}")
    
    def remove_shares(self, quantity: float, price: float) -> float:
        """减少持股数量（卖出），返回实现的盈亏"""
        if quantity <= 0:
            raise ValueError("卖出数量必须大于0")
        if quantity > self.quantity:
            raise ValueError(f"卖出数量({quantity})超过持仓数量({self.quantity})")
            
        realized_pnl = quantity * (price - self.cost_basis)
        self.quantity -= quantity
        
        if self.quantity == 0:
            # 全部卖出
            self.cost_basis = 0
            logger.info(f"清仓 {self.symbol}: {quantity}股 @ ${price:.2f}, 实现盈亏: ${realized_pnl:.2f}")
        else:
            logger.info(f"卖出 {self.symbol}: {quantity}股 @ ${price:.2f}, 实现盈亏: ${realized_pnl:.2f}")
            
        return realized_pnl
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'symbol': self.symbol,
            'quantity': self.quantity,
            'cost_basis': self.cost_basis,
            'current_price': self.current_price,
            'purchase_date': self.purchase_date.isoformat(),
            'last_updated': self.last_updated.isoformat(),
            'market_value': self.market_value,
            'cost_value': self.cost_value,
            'unrealized_pnl': self.unrealized_pnl,
            'unrealized_pnl_percent': self.unrealized_pnl_percent
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Position':
        """从字典创建持仓对象"""
        position = cls(
            symbol=data['symbol'],
            quantity=data['quantity'],
            cost_basis=data['cost_basis'],
            purchase_date=datetime.fromisoformat(data['purchase_date'])
        )
        position.current_price = data.get('current_price', data['cost_basis'])
        position.last_updated = datetime.fromisoformat(data.get('last_updated', datetime.now().isoformat()))
        return position
    
    def __str__(self) -> str:
        return f"{self.symbol}: {self.quantity:.2f}股 @ ${self.current_price:.2f} (成本${self.cost_basis:.2f})"
    
    def __repr__(self) -> str:
        return f"Position('{self.symbol}', {self.quantity}, {self.cost_basis})"