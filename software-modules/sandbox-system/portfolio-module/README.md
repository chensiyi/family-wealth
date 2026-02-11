# 持仓模块 (Portfolio Module)

> **模块摘要**: 持仓模块提供完整的股票投资组合管理功能，包括持仓管理、交易记录、风险指标计算等功能，支持真实的股票交易模拟。

## 🎯 模块功能

### 核心特性
- **持仓管理**: 完整的股票持仓跟踪和管理
- **交易模拟**: 支持买入、卖出等交易操作
- **风险计算**: 多维度风险指标分析
- **绩效评估**: 投资组合收益和风险评估
- **数据持久化**: 投资组合状态保存和加载

## 📁 模块结构

```
portfolio-module/
├── __init__.py              # 模块初始化
├── position.py              # 持仓对象类
├── transaction.py           # 交易记录类
├── risk_metrics.py          # 风险指标计算类
├── portfolio_manager.py     # 投资组合管理器
└── README.md               # 本文件
```

## 🔧 核心类说明

### Position (持仓类)
管理单个股票的持仓信息

```python
from portfolio_module import Position

# 创建持仓
position = Position("AAPL", 100, 150.00)  # 100股AAPL，成本$150/股

# 更新价格
position.update_price(155.50)

# 买入更多股份
position.add_shares(50, 153.25)

# 卖出股份
realized_pnl = position.remove_shares(30, 158.00)

# 获取持仓信息
print(f"市值: ${position.market_value:.2f}")
print(f"未实现盈亏: ${position.unrealized_pnl:.2f}")
print(f"盈亏比例: {position.unrealized_pnl_percent:.2f}%")
```

### Transaction (交易类)
记录所有的交易活动

```python
from portfolio_module import Transaction, TransactionType

# 创建买入交易
buy_txn = Transaction("AAPL", TransactionType.BUY, 100, 150.00, fees=10.00)

# 创建卖出交易
sell_txn = Transaction("AAPL", TransactionType.SELL, 50, 158.00, fees=10.00)

# 交易信息
print(f"交易类型: {buy_txn.type.value}")
print(f"交易金额: ${buy_txn.amount:.2f}")
print(f"是否买入: {buy_txn.is_buy}")
```

### RiskMetrics (风险指标类)
计算各种投资风险指标

```python
from portfolio_module import RiskMetrics

risk_calc = RiskMetrics()

# 计算收益率
return_rate = risk_calc.calculate_portfolio_return(100000, 120000)  # 20%

# 计算波动率
volatility = risk_calc.calculate_volatility([0.02, -0.01, 0.03, -0.02])

# 计算夏普比率
sharpe = risk_calc.calculate_sharpe_ratio([0.02, -0.01, 0.03, -0.02])

# 计算最大回撤
drawdown_info = risk_calc.calculate_max_drawdown([100000, 105000, 98000, 102000])

# 计算VaR
var_95 = risk_calc.calculate_var([-0.02, -0.01, 0.03, -0.04, 0.02], 0.95)
```

### PortfolioManager (投资组合管理器)
主控制器，整合所有功能

```python
from portfolio_module import PortfolioManager

# 创建投资组合
portfolio = PortfolioManager(initial_cash=100000.0)

# 买入股票
success = portfolio.buy_stock("AAPL", 100, 150.00, fees=10.00, description="首次建仓")

# 卖出股票
success = portfolio.sell_stock("AAPL", 50, 158.00, fees=10.00, description="部分获利了结")

# 更新股价
portfolio.update_prices({"AAPL": 155.50, "GOOGL": 2800.00})

# 获取投资组合摘要
summary = portfolio.get_portfolio_summary()
print(f"总资产: ${summary['total_value']:.2f}")
print(f"现金: ${summary['cash']:.2f}")
print(f"持仓数量: {summary['position_count']}")

# 获取风险指标
risk_metrics = portfolio.get_risk_metrics()
print(f"总收益率: {risk_metrics['total_return']*100:.2f}%")
print(f"夏普比率: {risk_metrics['sharpe_ratio']:.2f}")
print(f"最大回撤: {risk_metrics['max_drawdown']['max_drawdown']*100:.2f}%")

# 保存投资组合
portfolio.save_to_file("my_portfolio.json")

# 加载投资组合
loaded_portfolio = PortfolioManager.load_from_file("my_portfolio.json")
```

## 📊 支持的风险指标

### 基础指标
- **总收益率**: 投资组合的整体收益表现
- **波动率**: 价格变动的标准差
- **夏普比率**: 风险调整后的收益表现

### 高级指标
- **最大回撤**: 投资组合从峰值到谷底的最大跌幅
- **贝塔系数**: 相对于市场的敏感度
- **风险价值(VaR)**: 在给定置信水平下的最大可能损失
- **跟踪误差**: 相对于基准的表现偏差

## 💰 交易功能

### 买入操作
```python
# 基本买入
portfolio.buy_stock("MSFT", 100, 300.00)

# 带费用的买入
portfolio.buy_stock("MSFT", 100, 300.00, fees=15.00, description="技术分析买入")
```

### 卖出操作
```python
# 基本卖出
portfolio.sell_stock("MSFT", 50, 310.00)

# 带费用的卖出
portfolio.sell_stock("MSFT", 50, 310.00, fees=15.00, description="获利了结")
```

## 📈 数据持久化

### 保存投资组合
```python
portfolio.save_to_file("portfolio_backup.json")
```

### 加载投资组合
```python
restored_portfolio = PortfolioManager.load_from_file("portfolio_backup.json")
```

## 🔒 安全特性

- **资金验证**: 买入前检查可用资金
- **持仓验证**: 卖出前验证持仓数量
- **价格保护**: 防止负价格输入
- **交易记录**: 完整的交易历史记录

## 🚀 使用示例

```python
# 完整的投资组合管理示例
from portfolio_module import PortfolioManager, TransactionType

# 1. 创建投资组合
portfolio = PortfolioManager(initial_cash=50000.0)

# 2. 进行交易
portfolio.buy_stock("AAPL", 100, 150.00, fees=10.00, description="苹果公司建仓")
portfolio.buy_stock("GOOGL", 10, 2800.00, fees=10.00, description="谷歌建仓")

# 3. 更新市场价格
portfolio.update_prices({
    "AAPL": 155.50,
    "GOOGL": 2850.00
})

# 4. 查看投资组合状态
summary = portfolio.get_portfolio_summary()
print("=== 投资组合摘要 ===")
print(f"现金: ${summary['cash']:,.2f}")
print(f"持仓价值: ${summary['positions_value']:,.2f}")
print(f"总资产: ${summary['total_value']:,.2f}")
print(f"未实现盈亏: ${summary['unrealized_pnl']:,.2f}")

# 5. 风险分析
metrics = portfolio.get_risk_metrics()
print("\n=== 风险指标 ===")
print(f"总收益率: {metrics['total_return']*100:.2f}%")
print(f"夏普比率: {metrics['sharpe_ratio']:.2f}")
print(f"波动率: {metrics['volatility']*100:.2f}%")

# 6. 保存进度
portfolio.save_to_file("demo_portfolio.json")
```

## 📋 注意事项

1. **货币单位**: 所有金额均以美元(USD)为单位
2. **精度处理**: 使用浮点数处理，注意精度问题
3. **时间记录**: 所有时间戳使用ISO格式
4. **数据验证**: 输入数据会进行基本验证
5. **异常处理**: 关键操作包含适当的错误处理

---
*本模块为家族财富管理系统的持仓模拟核心组件*