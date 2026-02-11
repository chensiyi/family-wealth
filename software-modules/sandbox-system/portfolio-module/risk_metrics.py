"""
风险指标计算类
Calculates various risk metrics for the portfolio
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import math
import statistics
import logging

logger = logging.getLogger(__name__)

class RiskMetrics:
    """风险指标计算器"""
    
    def __init__(self):
        self.risk_free_rate = 0.02  # 无风险利率假设为2%
        
    def calculate_portfolio_return(self, initial_value: float, final_value: float) -> float:
        """计算投资组合收益率"""
        if initial_value == 0:
            return 0.0
        return (final_value - initial_value) / initial_value
    
    def calculate_volatility(self, returns: List[float]) -> float:
        """计算波动率（标准差）"""
        if len(returns) < 2:
            return 0.0
        return statistics.stdev(returns)
    
    def calculate_sharpe_ratio(self, returns: List[float], risk_free_rate: Optional[float] = None) -> float:
        """计算夏普比率"""
        if len(returns) < 2:
            return 0.0
            
        rf = risk_free_rate or self.risk_free_rate
        avg_return = statistics.mean(returns)
        volatility = self.calculate_volatility(returns)
        
        if volatility == 0:
            return 0.0
            
        return (avg_return - rf) / volatility
    
    def calculate_max_drawdown(self, values: List[float]) -> Dict[str, Any]:
        """计算最大回撤"""
        if len(values) < 2:
            return {
                'max_drawdown': 0.0,
                'peak_value': values[0] if values else 0.0,
                'trough_value': values[-1] if values else 0.0,
                'recovery_time': None
            }
        
        peak = values[0]
        max_dd = 0.0
        peak_index = 0
        
        for i, value in enumerate(values):
            if value > peak:
                peak = value
                peak_index = i
            else:
                drawdown = (peak - value) / peak
                if drawdown > max_dd:
                    max_dd = drawdown
        
        # 计算恢复时间
        recovery_time = None
        if max_dd > 0:
            trough_index = values.index(min(values))
            for i in range(trough_index + 1, len(values)):
                if values[i] >= values[peak_index]:
                    recovery_time = i - trough_index
                    break
        
        return {
            'max_drawdown': max_dd,
            'peak_value': peak,
            'trough_value': min(values),
            'recovery_time': recovery_time
        }
    
    def calculate_beta(self, portfolio_returns: List[float], market_returns: List[float]) -> float:
        """计算贝塔系数"""
        if len(portfolio_returns) != len(market_returns) or len(portfolio_returns) < 2:
            return 0.0
            
        # 计算协方差和市场方差
        portfolio_mean = statistics.mean(portfolio_returns)
        market_mean = statistics.mean(market_returns)
        
        covariance = sum((p - portfolio_mean) * (m - market_mean) 
                        for p, m in zip(portfolio_returns, market_returns)) / (len(portfolio_returns) - 1)
        
        market_variance = sum((m - market_mean) ** 2 
                            for m in market_returns) / (len(market_returns) - 1)
        
        if market_variance == 0:
            return 0.0
            
        return covariance / market_variance
    
    def calculate_var(self, returns: List[float], confidence_level: float = 0.95) -> float:
        """计算风险价值(VaR)"""
        if len(returns) < 2:
            return 0.0
            
        sorted_returns = sorted(returns)
        index = int(len(sorted_returns) * (1 - confidence_level))
        return abs(sorted_returns[index])
    
    def calculate_tracking_error(self, portfolio_returns: List[float], benchmark_returns: List[float]) -> float:
        """计算跟踪误差"""
        if len(portfolio_returns) != len(benchmark_returns) or len(portfolio_returns) < 2:
            return 0.0
            
        differences = [p - b for p, b in zip(portfolio_returns, benchmark_returns)]
        return statistics.stdev(differences)
    
    def get_portfolio_metrics(self, portfolio_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """获取投资组合综合风险指标"""
        if not portfolio_history:
            return {}
        
        # 提取价值序列
        values = [entry['total_value'] for entry in portfolio_history]
        dates = [entry['date'] for entry in portfolio_history]
        
        # 计算收益率
        returns = []
        for i in range(1, len(values)):
            if values[i-1] != 0:
                ret = (values[i] - values[i-1]) / values[i-1]
                returns.append(ret)
        
        # 基准收益率（假设市场指数）
        market_returns = [r * 1.1 for r in returns]  # 简化假设
        
        metrics = {
            'total_return': self.calculate_portfolio_return(values[0], values[-1]),
            'volatility': self.calculate_volatility(returns),
            'sharpe_ratio': self.calculate_sharpe_ratio(returns),
            'max_drawdown': self.calculate_max_drawdown(values),
            'beta': self.calculate_beta(returns, market_returns),
            'var_95': self.calculate_var(returns, 0.95),
            'tracking_error': self.calculate_tracking_error(returns, market_returns),
            'current_value': values[-1],
            'initial_value': values[0],
            'period_days': (dates[-1] - dates[0]).days if len(dates) > 1 else 0
        }
        
        return metrics
    
    def __str__(self) -> str:
        return "RiskMetrics(risk_free_rate={})".format(self.risk_free_rate)