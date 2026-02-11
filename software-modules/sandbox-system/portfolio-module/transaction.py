"""
交易记录类
Represents a single transaction in the portfolio
"""

from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional
import uuid
import logging

logger = logging.getLogger(__name__)

class TransactionType(Enum):
    """交易类型枚举"""
    BUY = "BUY"
    SELL = "SELL"
    DIVIDEND = "DIVIDEND"
    SPLIT = "SPLIT"

class Transaction:
    """交易记录对象"""
    
    def __init__(self, symbol: str, transaction_type: TransactionType, 
                 quantity: float, price: float, fees: float = 0.0,
                 transaction_date: Optional[datetime] = None, 
                 description: str = ""):
        """
        初始化交易记录
        
        Args:
            symbol: 股票代码
            transaction_type: 交易类型
            quantity: 交易数量
            price: 交易价格
            fees: 交易费用
            transaction_date: 交易日期
            description: 交易描述
        """
        self.id = str(uuid.uuid4())
        self.symbol = symbol.upper()
        self.type = transaction_type
        self.quantity = float(quantity)
        self.price = float(price)
        self.fees = float(fees)
        self.transaction_date = transaction_date or datetime.now()
        self.description = description
        self.timestamp = datetime.now()
        
        # 计算交易金额
        self.amount = abs(self.quantity * self.price) + self.fees
        if self.type == TransactionType.SELL:
            self.amount = -self.amount  # 卖出为负值
            
    @property
    def is_buy(self) -> bool:
        """是否为买入交易"""
        return self.type == TransactionType.BUY
    
    @property
    def is_sell(self) -> bool:
        """是否为卖出交易"""
        return self.type == TransactionType.SELL
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'type': self.type.value,
            'quantity': self.quantity,
            'price': self.price,
            'fees': self.fees,
            'amount': self.amount,
            'transaction_date': self.transaction_date.isoformat(),
            'description': self.description,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        """从字典创建交易对象"""
        transaction = cls(
            symbol=data['symbol'],
            transaction_type=TransactionType(data['type']),
            quantity=data['quantity'],
            price=data['price'],
            fees=data.get('fees', 0.0),
            transaction_date=datetime.fromisoformat(data['transaction_date']),
            description=data.get('description', '')
        )
        transaction.id = data.get('id', str(uuid.uuid4()))
        transaction.timestamp = datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat()))
        return transaction
    
    def __str__(self) -> str:
        fee_str = f" + ${self.fees:.2f}费用" if self.fees > 0 else ""
        return f"{self.type.value} {self.symbol}: {self.quantity:.2f}股 @ ${self.price:.2f}{fee_str}"
    
    def __repr__(self) -> str:
        return f"Transaction('{self.id}', '{self.symbol}', {self.type}, {self.quantity}, {self.price})"