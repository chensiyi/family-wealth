# 沙盘系统 (Sandbox System) - 重构版

> **系统摘要**: 沙盘系统是家族财富管理系统的专业模拟交易平台，集成实时交易大厅功能，提供完整的股票交易模拟、投资组合管理、风险分析等核心功能。

## 🎯 系统功能

### 核心特性
- **实时交易大厅**: 专业的股票交易模拟环境，支持限价单、市价单等多种交易方式
- **投资组合管理**: 完整的持仓跟踪、盈亏分析和绩效评估
- **风险管理**: 多维度风险指标计算和实时监控
- **交易历史**: 完整的交易记录和回溯分析
- **数据集成**: 与数据中台无缝对接，支持真实市场数据
- **模拟环境**: 安全的策略测试和验证平台

## 📁 系统结构

```
sandbox-system/
├── sandbox_main.py         # 主入口文件（推荐使用）
├── main.py                 # 旧版主入口（已废弃）
├── sandbox_adapter.py      # 数据库适配器
├── portfolio-module/       # 持仓管理模块
│   ├── portfolio_manager.py  # 投资组合管理器
│   ├── position.py           # 持仓对象类
│   ├── transaction.py        # 交易记录类
│   └── risk_metrics.py       # 风险指标计算类
├── config/                 # 配置文件
│   └── database_config.py
├── dashboard/              # 仪表板组件
│   ├── crisis_dashboard.py
│   ├── participant_dashboard.py
│   └── decision_dashboard.py
├── analysis-engine/        # 分析引擎
│   ├── event_analyzer.py
│   ├── behavior_analyzer.py
│   └── performance_analyzer.py
├── utils/                  # 工具模块
│   └── data_converter.py
├── storage/                # 数据存储
│   └── sandbox_database.db
└── README.md              # 本文件
```

## 🔧 使用方法

### 1. 系统启动

```python
from sandbox_main import main

# 启动沙盘系统
sandbox = main()
```

### 2. 交易操作

```python
# 买入股票
result = sandbox.execute_trade(
    symbol="NVDA", 
    action="buy", 
    quantity=100, 
    price=875.28,
    fees=10.00,
    description="AI芯片龙头建仓"
)

# 卖出股票
result = sandbox.execute_trade(
    symbol="NVDA",
    action="sell",
    quantity=50,
    price=890.50,
    fees=10.00,
    description="部分获利了结"
)
```

### 3. 查询持仓

```python
# 获取持仓详情
positions = sandbox.get_portfolio_positions()
print(f"持仓数量: {positions['summary']['position_count']}")
print(f"总资产: ${positions['summary']['total_value']:,.2f}")

# 获取特定股票持仓
nvda_position = None
for pos in positions['positions']:
    if pos['symbol'] == 'NVDA':
        nvda_position = pos
        break
```

### 4. 交易历史

```python
# 获取所有交易记录
history = sandbox.get_transaction_history()
for txn in history['transactions']:
    print(f"{txn['timestamp']}: {txn['type']} {txn['symbol']} {txn['quantity']}@${txn['price']}")

# 获取特定股票交易记录
nvda_history = sandbox.get_transaction_history(symbol="NVDA")
```

### 5. 风险分析

```python
# 获取风险指标
risk_analysis = sandbox.get_risk_analysis()
risk_metrics = risk_analysis['risk_metrics']

print(f"夏普比率: {risk_metrics['sharpe_ratio']:.2f}")
print(f"波动率: {risk_metrics['volatility']*100:.2f}%")
print(f"最大回撤: {risk_metrics['max_drawdown']['max_drawdown']*100:.2f}%")
```

### 6. 市场数据更新

```python
# 更新市场价格
prices = {
    "NVDA": 880.25,
    "JNJ": 152.40,
    "MSFT": 395.50
}

result = sandbox.update_market_prices(prices)
print(f"更新结果: {result['message']}")
```

## 📊 核心数据模型

### 投资组合 (Portfolio)
- 现金余额、持仓总值
- 总资产、未实现盈亏
- 持仓数量、交易次数

### 持仓 (Positions)
- 股票代码、持有数量
- 成本基础、当前价格
- 市值、未实现盈亏
- 盈亏比例

### 交易记录 (Transactions)
- 交易ID、股票代码
- 交易类型（买入/卖出）
- 数量、价格、费用
- 时间戳、描述

### 风险指标 (Risk Metrics)
- 总收益率、波动率
- 夏普比率、最大回撤
- VaR、贝塔系数

## 🚀 高级功能

### 1. 系统状态监控
```python
# 获取系统运行状态
status = sandbox.get_system_status()
print(f"系统状态: {status['status']}")
print(f"运行时间: {status['runtime']}")
print(f"可用功能: {status['available_features']}")
```

### 2. 投资组合分析
```python
# 获取详细的持仓分析
positions = sandbox.get_portfolio_positions()
for position in positions['positions']:
    print(f"{position['symbol']}: {position['quantity']}股")
    print(f"  成本: ${position['cost_basis']:.2f}")
    print(f"  当前: ${position['current_price']:.2f}")
    print(f"  盈亏: ${position['unrealized_pnl']:.2f} ({position['unrealized_pnl_percent']:.2f}%)")
```

### 3. 风险管理
```python
# 获取风险分析报告
risk_analysis = sandbox.get_risk_analysis()
metrics = risk_analysis['risk_metrics']

print("=== 风险分析报告 ===")
print(f"总收益率: {metrics['total_return']*100:.2f}%")
print(f"夏普比率: {metrics['sharpe_ratio']:.2f}")
print(f"波动率: {metrics['volatility']*100:.2f}%")
print(f"最大回撤: {metrics['max_drawdown']['max_drawdown']*100:.2f}%")

if metrics['sharpe_ratio'] < 1:
    print("⚠️  风险调整后收益较低，建议优化投资组合")
```

### 4. 交易策略回测
```python
# 模拟交易策略
def simple_moving_average_strategy(sandbox, symbol, window=20):
    """简单的移动平均线策略"""
    # 这里可以集成更复杂的策略逻辑
    pass

# 执行策略回测
# strategy_results = simple_moving_average_strategy(sandbox, "NVDA")
```

## 🔧 API接口说明

### 核心API方法

| 方法 | 功能 | 参数 | 返回值 |
|------|------|------|--------|
| `execute_trade()` | 执行交易 | symbol, action, quantity, price, fees, description | 交易结果 |
| `get_portfolio_positions()` | 获取持仓 | 无 | 持仓详情 |
| `get_transaction_history()` | 获取交易历史 | symbol=None | 交易记录 |
| `update_market_prices()` | 更新价格 | prices_dict | 更新结果 |
| `get_risk_analysis()` | 风险分析 | 无 | 风险指标 |
| `get_system_status()` | 系统状态 | 无 | 状态信息 |

### 数据持久化
- 自动保存投资组合状态到 `portfolio_backup.json`
- 交易记录永久保存
- 支持从文件恢复历史投资组合

## 🛡️ 安全特性

### 资金管理
- 买入前自动验证资金充足性
- 防止透支交易
- 交易费用自动扣除

### 持仓验证
- 卖出前验证持仓数量
- 防止卖空操作
- 持仓数量边界检查

### 数据保护
- 完整的交易日志记录
- 异常操作预警机制
- 数据备份和恢复功能

## 📈 性能优化

### 实时更新
- 市场价格实时更新
- 持仓价值动态计算
- 风险指标即时重算

### 数据缓存
- 频繁访问数据缓存
- 计算结果缓存优化
- 内存使用效率优化

## 🚀 部署说明

### 环境要求
- Python 3.8+
- 必要依赖包：numpy, pandas, flask
- 推荐8GB以上内存

### 启动步骤
```bash
cd software-modules/sandbox-system
python sandbox_main.py
```

### 集成Web界面
系统可与web-server中的实时交易大厅集成，提供完整的图形化操作界面。

---
*本系统为家族财富管理的专业模拟交易平台，所有交易均为虚拟操作，不涉及真实资金。*