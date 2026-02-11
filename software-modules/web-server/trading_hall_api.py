#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时交易大厅后端API服务
提供完整的股票交易、持仓管理、市场数据等接口
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

app = Flask(__name__)
CORS(app)

class TradingHallBackend:
    def __init__(self):
        self.portfolio = {
            'cash': 1000000.0,
            'positions': {},
            'orders': [],
            'trades': [],
            'order_counter': 1000
        }
        
        self.market_data = {}
        self.initialize_market_data()
        
    def initialize_market_data(self):
        """初始化市场数据"""
        stocks = [
            {'symbol': 'NVDA', 'name': '英伟达', 'base_price': 875.28},
            {'symbol': 'JNJ', 'name': '强生', 'base_price': 152.40},
            {'symbol': 'MSFT', 'name': '微软', 'base_price': 395.50},
            {'symbol': 'AAPL', 'name': '苹果', 'base_price': 182.52},
            {'symbol': 'GOOGL', 'name': '谷歌', 'base_price': 142.36},
            {'symbol': 'AMZN', 'name': '亚马逊', 'base_price': 155.89},
            {'symbol': 'TSLA', 'name': '特斯拉', 'base_price': 248.42},
            {'symbol': 'META', 'name': 'Meta', 'base_price': 485.75}
        ]
        
        for stock in stocks:
            self.market_data[stock['symbol']] = {
                'symbol': stock['symbol'],
                'name': stock['name'],
                'price': stock['base_price'],
                'prev_close': stock['base_price'] * (0.98 + random.random() * 0.04),
                'volume': random.randint(1000000, 10000000),
                'high': stock['base_price'] * (1 + random.random() * 0.05),
                'low': stock['base_price'] * (0.95 + random.random() * 0.05),
                'change': 0,
                'change_percent': 0,
                'timestamp': datetime.now().isoformat()
            }
            self.update_price_change(stock['symbol'])
    
    def update_price_change(self, symbol: str):
        """更新价格变化"""
        data = self.market_data[symbol]
        data['change'] = data['price'] - data['prev_close']
        data['change_percent'] = (data['change'] / data['prev_close']) * 100
    
    def simulate_price_movement(self):
        """模拟价格波动"""
        for symbol in self.market_data:
            # 随机价格波动 (-1% 到 +1%)
            change_percent = (random.random() - 0.5) * 0.02
            self.market_data[symbol]['price'] *= (1 + change_percent)
            self.market_data[symbol]['price'] = round(self.market_data[symbol]['price'], 2)
            self.update_price_change(symbol)
            self.market_data[symbol]['timestamp'] = datetime.now().isoformat()
    
    def get_market_snapshot(self) -> Dict:
        """获取市场快照"""
        return {
            'timestamp': datetime.now().isoformat(),
            'stocks': list(self.market_data.values())
        }
    
    def get_portfolio_summary(self) -> Dict:
        """获取投资组合摘要"""
        positions_value = sum(
            pos['quantity'] * pos['current_price'] 
            for pos in self.portfolio['positions'].values()
        )
        total_value = self.portfolio['cash'] + positions_value
        unrealized_pnl = sum(
            pos['unrealized_pnl'] 
            for pos in self.portfolio['positions'].values()
        )
        
        return {
            'cash_balance': self.portfolio['cash'],
            'positions_value': positions_value,
            'total_value': total_value,
            'unrealized_pnl': unrealized_pnl,
            'position_count': len(self.portfolio['positions'])
        }
    
    def place_order(self, symbol: str, order_type: str, quantity: int, 
                   price: float, order_subtype: str = 'limit') -> Dict:
        """下单"""
        # 检查资金和持仓
        if order_type == 'buy':
            total_cost = quantity * price
            if total_cost > self.portfolio['cash']:
                return {
                    'success': False,
                    'error': '资金不足'
                }
        elif order_type == 'sell':
            if symbol not in self.portfolio['positions'] or \
               self.portfolio['positions'][symbol]['quantity'] < quantity:
                return {
                    'success': False,
                    'error': '持仓不足'
                }
        
        # 创建订单
        order_id = self.portfolio['order_counter']
        self.portfolio['order_counter'] += 1
        
        order = {
            'order_id': order_id,
            'symbol': symbol,
            'type': order_type,
            'subtype': order_subtype,
            'quantity': quantity,
            'price': price,
            'status': 'pending',
            'timestamp': datetime.now().isoformat(),
            'filled_quantity': 0,
            'average_fill_price': 0
        }
        
        self.portfolio['orders'].append(order)
        
        # 立即撮合市价单
        if order_subtype == 'market':
            self.execute_market_order(order)
        
        return {
            'success': True,
            'order_id': order_id,
            'message': f'{order_type}单已提交'
        }
    
    def execute_market_order(self, order: Dict):
        """执行市价单"""
        current_price = self.market_data[order['symbol']]['price']
        filled_value = order['quantity'] * current_price
        
        if order['type'] == 'buy':
            # 扣除现金
            self.portfolio['cash'] -= filled_value
            # 更新持仓
            if order['symbol'] in self.portfolio['positions']:
                pos = self.portfolio['positions'][order['symbol']]
                total_cost = pos['quantity'] * pos['avg_price'] + filled_value
                total_qty = pos['quantity'] + order['quantity']
                pos['avg_price'] = total_cost / total_qty
                pos['quantity'] = total_qty
            else:
                self.portfolio['positions'][order['symbol']] = {
                    'symbol': order['symbol'],
                    'name': self.market_data[order['symbol']]['name'],
                    'quantity': order['quantity'],
                    'avg_price': current_price,
                    'current_price': current_price,
                    'market_value': filled_value,
                    'unrealized_pnl': 0,
                    'unrealized_pnl_percent': 0
                }
        else:
            # 卖出
            pos = self.portfolio['positions'][order['symbol']]
            # 增加现金
            self.portfolio['cash'] += filled_value
            # 更新持仓
            pos['quantity'] -= order['quantity']
            if pos['quantity'] == 0:
                del self.portfolio['positions'][order['symbol']]
        
        # 记录交易
        trade = {
            'trade_id': f"T{int(time.time())}",
            'symbol': order['symbol'],
            'type': order['type'],
            'quantity': order['quantity'],
            'price': current_price,
            'amount': filled_value,
            'timestamp': datetime.now().isoformat()
        }
        self.portfolio['trades'].append(trade)
        
        # 更新订单状态
        order['status'] = 'filled'
        order['filled_quantity'] = order['quantity']
        order['average_fill_price'] = current_price
    
    def get_order_book(self, symbol: str) -> Dict:
        """获取买卖盘数据"""
        current_price = self.market_data[symbol]['price']
        
        # 生成买盘数据
        bids = []
        for i in range(5):
            price = current_price * (1 - (i + 1) * 0.001)
            quantity = random.randint(100, 1000)
            bids.append({
                'price': round(price, 2),
                'quantity': quantity,
                'value': round(price * quantity, 2)
            })
        
        # 生成卖盘数据
        asks = []
        for i in range(5):
            price = current_price * (1 + (i + 1) * 0.001)
            quantity = random.randint(100, 1000)
            asks.append({
                'price': round(price, 2),
                'quantity': quantity,
                'value': round(price * quantity, 2)
            })
        
        return {
            'symbol': symbol,
            'bids': bids,
            'asks': asks,
            'spread': round(asks[0]['price'] - bids[0]['price'], 2) if bids and asks else 0
        }
    
    def cancel_order(self, order_id: int) -> Dict:
        """撤销订单"""
        for order in self.portfolio['orders']:
            if order['order_id'] == order_id:
                if order['status'] == 'filled':
                    return {
                        'success': False,
                        'error': '订单已成交，无法撤销'
                    }
                order['status'] = 'cancelled'
                return {
                    'success': True,
                    'message': '订单已撤销'
                }
        
        return {
            'success': False,
            'error': '订单不存在'
        }

# 初始化后端服务
trading_backend = TradingHallBackend()

# API路由
@app.route('/api/market/snapshot', methods=['GET'])
def get_market_snapshot():
    """获取市场快照"""
    return jsonify(trading_backend.get_market_snapshot())

@app.route('/api/portfolio/summary', methods=['GET'])
def get_portfolio_summary():
    """获取投资组合摘要"""
    return jsonify(trading_backend.get_portfolio_summary())

@app.route('/api/portfolio/positions', methods=['GET'])
def get_positions():
    """获取持仓明细"""
    return jsonify({
        'success': True,
        'positions': list(trading_backend.portfolio['positions'].values())
    })

@app.route('/api/trading/order', methods=['POST'])
def place_order():
    """下单"""
    data = request.get_json()
    result = trading_backend.place_order(
        symbol=data['symbol'],
        order_type=data['type'],
        quantity=data['quantity'],
        price=data['price'],
        order_subtype=data.get('subtype', 'limit')
    )
    return jsonify(result)

@app.route('/api/trading/orders', methods=['GET'])
def get_orders():
    """获取订单列表"""
    return jsonify({
        'success': True,
        'orders': trading_backend.portfolio['orders'][-20:]  # 最近20笔订单
    })

@app.route('/api/trading/order/<int:order_id>', methods=['DELETE'])
def cancel_order(order_id):
    """撤销订单"""
    result = trading_backend.cancel_order(order_id)
    return jsonify(result)

@app.route('/api/trading/trades', methods=['GET'])
def get_trades():
    """获取交易历史"""
    return jsonify({
        'success': True,
        'trades': trading_backend.portfolio['trades'][-50:]  # 最近50笔交易
    })

@app.route('/api/market/orderbook/<symbol>', methods=['GET'])
def get_order_book(symbol):
    """获取买卖盘"""
    return jsonify(trading_backend.get_order_book(symbol))

@app.route('/api/market/realtime/<symbol>', methods=['GET'])
def get_realtime_data(symbol):
    """获取实时行情"""
    if symbol in trading_backend.market_data:
        return jsonify({
            'success': True,
            'data': trading_backend.market_data[symbol]
        })
    else:
        return jsonify({
            'success': False,
            'error': '股票代码不存在'
        }), 404

# 启动定时任务模拟价格变动
import threading

def price_update_worker():
    """价格更新工作线程"""
    while True:
        time.sleep(3)  # 每3秒更新一次价格
        trading_backend.simulate_price_movement()

# 启动价格更新线程
price_thread = threading.Thread(target=price_update_worker, daemon=True)
price_thread.start()

if __name__ == '__main__':
    print("🚀 实时交易大厅后端服务启动...")
    print("📡 API地址: http://localhost:5001")
    print("📊 可用接口:")
    print("   GET  /api/market/snapshot     - 市场快照")
    print("   GET  /api/portfolio/summary   - 投资组合摘要")
    print("   GET  /api/portfolio/positions - 持仓明细")
    print("   POST /api/trading/order       - 下单")
    print("   GET  /api/trading/orders      - 订单列表")
    print("   DELETE /api/trading/order/<id> - 撤销订单")
    print("   GET  /api/trading/trades      - 交易历史")
    print("   GET  /api/market/orderbook/<symbol> - 买卖盘")
    print("   GET  /api/market/realtime/<symbol> - 实时行情")
    
    app.run(host='0.0.0.0', port=5001, debug=True)