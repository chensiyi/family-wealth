"""
金融数据分析器
Analyzes financial data for stock screening and investment decisions
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import math
import statistics
import logging

logger = logging.getLogger(__name__)

class FinancialAnalyzer:
    """金融数据分析器"""
    
    def __init__(self):
        self.screening_criteria = {
            'value': {
                'pe_ratio': {'min': 0, 'max': 25},
                'pb_ratio': {'min': 0, 'max': 3},
                'dividend_yield': {'min': 1, 'max': 10}
            },
            'growth': {
                'revenue_growth': {'min': 5, 'max': 100},
                'earnings_growth': {'min': 10, 'max': 100},
                'book_value_growth': {'min': 5, 'max': 50}
            },
            'quality': {
                'debt_equity_ratio': {'min': 0, 'max': 1},
                'current_ratio': {'min': 1.5, 'max': 10},
                'roa': {'min': 5, 'max': 100},
                'roe': {'min': 10, 'max': 100}
            }
        }
    
    def screen_stocks(self, stocks_data: List[Dict[str, Any]], 
                     criteria_type: str = 'value') -> List[Dict[str, Any]]:
        """
        股票筛选
        
        Args:
            stocks_data: 股票数据列表
            criteria_type: 筛选标准类型 ('value', 'growth', 'quality')
            
        Returns:
            筛选后的股票列表
        """
        if criteria_type not in self.screening_criteria:
            logger.warning(f"未知的筛选标准: {criteria_type}")
            return []
        
        criteria = self.screening_criteria[criteria_type]
        screened_stocks = []
        
        for stock in stocks_data:
            if self._meets_criteria(stock, criteria):
                score = self._calculate_screening_score(stock, criteria_type)
                stock_copy = stock.copy()
                stock_copy['screening_score'] = score
                stock_copy['screening_type'] = criteria_type
                screened_stocks.append(stock_copy)
        
        # 按得分排序
        screened_stocks.sort(key=lambda x: x['screening_score'], reverse=True)
        return screened_stocks
    
    def _meets_criteria(self, stock: Dict[str, Any], criteria: Dict[str, Dict]) -> bool:
        """检查股票是否满足筛选条件"""
        for metric, bounds in criteria.items():
            value = stock.get(metric)
            if value is None:
                return False
            
            if not (bounds['min'] <= value <= bounds['max']):
                return False
        
        return True
    
    def _calculate_screening_score(self, stock: Dict[str, Any], criteria_type: str) -> float:
        """计算筛选得分"""
        scores = []
        
        if criteria_type == 'value':
            # 价值型评分
            pe_score = max(0, (25 - stock.get('pe_ratio', 25)) / 25)
            pb_score = max(0, (3 - stock.get('pb_ratio', 3)) / 3)
            div_score = min(1, stock.get('dividend_yield', 0) / 5)
            scores = [pe_score, pb_score, div_score]
            
        elif criteria_type == 'growth':
            # 成长型评分
            rev_growth = min(1, stock.get('revenue_growth', 0) / 30)
            earn_growth = min(1, stock.get('earnings_growth', 0) / 30)
            bv_growth = min(1, stock.get('book_value_growth', 0) / 20)
            scores = [rev_growth, earn_growth, bv_growth]
            
        elif criteria_type == 'quality':
            # 质量型评分
            de_ratio = max(0, (1 - stock.get('debt_equity_ratio', 1)))
            current_ratio = min(1, (stock.get('current_ratio', 1) - 1) / 2)
            roa_score = min(1, stock.get('roa', 0) / 15)
            roe_score = min(1, stock.get('roe', 0) / 20)
            scores = [de_ratio, current_ratio, roa_score, roe_score]
        
        return sum(scores) / len(scores) if scores else 0
    
    def calculate_technical_indicators(self, price_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        计算技术指标
        
        Args:
            price_data: 价格数据列表，按时间倒序排列
            
        Returns:
            技术指标字典
        """
        if len(price_data) < 20:
            logger.warning("价格数据不足，无法计算技术指标")
            return {}
        
        # 提取收盘价
        closes = [float(d['close']) for d in price_data]
        highs = [float(d.get('high', d['close'])) for d in price_data]
        lows = [float(d.get('low', d['close'])) for d in price_data]
        
        indicators = {}
        
        # 移动平均线
        indicators['ma_5'] = self._calculate_ma(closes, 5)
        indicators['ma_20'] = self._calculate_ma(closes, 20)
        indicators['ma_50'] = self._calculate_ma(closes, 50)
        
        # 相对强弱指数 (RSI)
        indicators['rsi_14'] = self._calculate_rsi(closes, 14)
        
        # MACD
        macd_result = self._calculate_macd(closes)
        indicators['macd'] = macd_result['macd']
        indicators['macd_signal'] = macd_result['signal']
        indicators['macd_histogram'] = macd_result['histogram']
        
        # 布林带
        bb_result = self._calculate_bollinger_bands(closes, 20)
        indicators['bb_upper'] = bb_result['upper']
        indicators['bb_middle'] = bb_result['middle']
        indicators['bb_lower'] = bb_result['lower']
        indicators['bb_width'] = bb_result['bandwidth']
        
        # 成交量指标
        volumes = [float(d.get('volume', 0)) for d in price_data]
        if len(volumes) >= 20:
            indicators['volume_ma_20'] = self._calculate_ma(volumes, 20)
            indicators['volume_ratio'] = volumes[0] / indicators['volume_ma_20'] if indicators['volume_ma_20'] > 0 else 0
        
        # 波动率
        indicators['volatility_30'] = self._calculate_volatility(closes, 30)
        
        # 支撑阻力位
        sr_levels = self._calculate_support_resistance(closes, highs, lows)
        indicators['support_level'] = sr_levels['support']
        indicators['resistance_level'] = sr_levels['resistance']
        
        return indicators
    
    def _calculate_ma(self, data: List[float], period: int) -> float:
        """计算移动平均"""
        if len(data) < period:
            return data[0] if data else 0
        return sum(data[:period]) / period
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """计算相对强弱指数"""
        if len(prices) < period + 1:
            return 50.0
        
        gains = []
        losses = []
        
        for i in range(1, min(period + 1, len(prices))):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        if not gains or not losses:
            return 50.0
            
        avg_gain = sum(gains) / len(gains)
        avg_loss = sum(losses) / len(losses)
        
        if avg_loss == 0:
            return 100.0
            
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices: List[float]) -> Dict[str, float]:
        """计算MACD指标"""
        if len(prices) < 26:
            return {'macd': 0, 'signal': 0, 'histogram': 0}
        
        # 计算12日和26日EMA
        ema_12 = self._calculate_ema(prices, 12)
        ema_26 = self._calculate_ema(prices, 26)
        
        macd_line = ema_12 - ema_26
        
        # 计算信号线（9日EMA of MACD）
        # 简化处理：使用MACD的历史数据计算
        macd_history = [macd_line]  # 简化的MACD历史
        signal_line = self._calculate_ema(macd_history, 9)
        
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """计算指数移动平均"""
        if len(prices) < period:
            return prices[0] if prices else 0
            
        multiplier = 2 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:period]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
            
        return ema
    
    def _calculate_bollinger_bands(self, prices: List[float], period: int = 20) -> Dict[str, float]:
        """计算布林带"""
        if len(prices) < period:
            return {'upper': 0, 'middle': 0, 'lower': 0, 'bandwidth': 0}
        
        ma = self._calculate_ma(prices, period)
        std_dev = statistics.stdev(prices[:period]) if len(prices[:period]) > 1 else 0
        
        upper_band = ma + (2 * std_dev)
        lower_band = ma - (2 * std_dev)
        bandwidth = (upper_band - lower_band) / ma if ma > 0 else 0
        
        return {
            'upper': upper_band,
            'middle': ma,
            'lower': lower_band,
            'bandwidth': bandwidth
        }
    
    def _calculate_volatility(self, prices: List[float], period: int = 30) -> float:
        """计算波动率"""
        if len(prices) < period + 1:
            return 0.0
        
        returns = []
        for i in range(1, min(period + 1, len(prices))):
            if prices[i-1] != 0:
                ret = (prices[i] - prices[i-1]) / prices[i-1]
                returns.append(ret)
        
        if len(returns) < 2:
            return 0.0
            
        return statistics.stdev(returns) * math.sqrt(252)  # 年化波动率
    
    def _calculate_support_resistance(self, closes: List[float], highs: List[float], 
                                    lows: List[float]) -> Dict[str, float]:
        """计算支撑阻力位"""
        if len(closes) < 10:
            return {'support': closes[0] if closes else 0, 'resistance': closes[0] if closes else 0}
        
        # 简化的支撑阻力计算
        recent_highs = highs[:10]
        recent_lows = lows[:10]
        
        resistance = max(recent_highs)
        support = min(recent_lows)
        
        return {
            'support': support,
            'resistance': resistance
        }
    
    def generate_investment_rating(self, stock_data: Dict[str, Any], 
                                 technical_indicators: Dict[str, Any]) -> Dict[str, Any]:
        """生成投资评级"""
        ratings = {
            'overall_rating': '',
            'value_rating': '',
            'technical_rating': '',
            'momentum_rating': '',
            'risk_rating': ''
        }
        
        # 价值评级
        pe_ratio = stock_data.get('pe_ratio', 0)
        pb_ratio = stock_data.get('pb_ratio', 0)
        
        if pe_ratio < 15 and pb_ratio < 2:
            ratings['value_rating'] = 'Strong Buy'
        elif pe_ratio < 20 and pb_ratio < 3:
            ratings['value_rating'] = 'Buy'
        elif pe_ratio < 25 and pb_ratio < 4:
            ratings['value_rating'] = 'Hold'
        else:
            ratings['value_rating'] = 'Sell'
        
        # 技术评级
        current_price = stock_data.get('current_price', 0)
        ma_20 = technical_indicators.get('ma_20', 0)
        rsi = technical_indicators.get('rsi_14', 50)
        
        if current_price > ma_20 and 30 < rsi < 70:
            ratings['technical_rating'] = 'Buy'
        elif current_price < ma_20 or rsi > 80 or rsi < 20:
            ratings['technical_rating'] = 'Sell'
        else:
            ratings['technical_rating'] = 'Hold'
        
        # 综合评级
        value_score = 1 if ratings['value_rating'] in ['Strong Buy', 'Buy'] else \
                     -1 if ratings['value_rating'] == 'Sell' else 0
        tech_score = 1 if ratings['technical_rating'] == 'Buy' else \
                    -1 if ratings['technical_rating'] == 'Sell' else 0
        
        total_score = value_score + tech_score
        
        if total_score >= 1:
            ratings['overall_rating'] = 'Buy'
        elif total_score <= -1:
            ratings['overall_rating'] = 'Sell'
        else:
            ratings['overall_rating'] = 'Hold'
        
        return ratings

    def __str__(self) -> str:
        return "FinancialAnalyzer(screening_criteria={})".format(list(self.screening_criteria.keys()))

    def __repr__(self) -> str:
        return f"FinancialAnalyzer(criteria_types={list(self.screening_criteria.keys())})"