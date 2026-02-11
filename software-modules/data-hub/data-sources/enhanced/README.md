# 增强数据源模块 (Enhanced Data Sources)

> **模块摘要**: 增强数据源模块提供类似选股软件级别的数据收集和分析功能，包括全球行业新闻收集、金融数据分析、板块跟踪和经济指标监控。

## 🎯 模块功能

### 核心特性
- **全球新闻收集**: 覆盖7大重点行业，5大主要地区
- **金融数据分析**: 价值、成长、质量三维度股票筛选
- **技术指标计算**: 完整的技术分析工具集
- **板块跟踪**: 实时监控行业动态和发展趋势
- **经济指标**: 各国央行政策和宏观经济数据

## 📁 模块结构

```
enhanced/
├── __init__.py              # 模块初始化
├── news_collector.py        # 新闻收集器
├── financial_analyzer.py    # 金融分析器
├── sector_tracker.py        # 板块跟踪器
├── economic_indicator.py    # 经济指标监控
└── README.md               # 本文件
```

## 🔧 核心组件说明

### NewsCollector (新闻收集器)
收集和分析全球重点行业新闻

```python
from enhanced.news_collector import NewsCollector

# 创建新闻收集器
news_collector = NewsCollector()

# 收集科技行业新闻
tech_news = news_collector.collect_sector_news('technology', 'us', days_back=7)
print(f"收集到 {len(tech_news)} 条科技新闻")

# 获取行业摘要
summary = news_collector.get_sector_summary('energy', 'global', days_back=30)
print(f"能源行业新闻总数: {summary['news_count']}")
print(f"情绪分布: {summary['sentiment_distribution']}")

# 搜索特定关键词
search_results = news_collector.search_news('人工智能', ['technology'], ['us', 'cn'])
```

### FinancialAnalyzer (金融分析器)
提供专业的股票筛选和分析功能

```python
from enhanced.financial_analyzer import FinancialAnalyzer

# 创建分析器
analyzer = FinancialAnalyzer()

# 价值型股票筛选
stocks_data = [
    {'symbol': 'AAPL', 'pe_ratio': 28.5, 'pb_ratio': 35.2, 'dividend_yield': 0.6},
    {'symbol': 'KO', 'pe_ratio': 24.1, 'pb_ratio': 9.8, 'dividend_yield': 2.9},
    # ... 更多股票数据
]

value_stocks = analyzer.screen_stocks(stocks_data, 'value')
print(f"筛选出 {len(value_stocks)} 只价值型股票")

# 技术指标计算
price_data = [
    {'date': '2024-01-15', 'open': 185.5, 'high': 187.2, 'low': 184.8, 'close': 186.9, 'volume': 45000000},
    # ... 更多价格数据
]

tech_indicators = analyzer.calculate_technical_indicators(price_data)
print(f"5日均线: ${tech_indicators['ma_5']:.2f}")
print(f"RSI(14): {tech_indicators['rsi_14']:.2f}")
print(f"MACD: {tech_indicators['macd']:.4f}")

# 生成投资评级
stock_data = {'current_price': 186.9, 'pe_ratio': 28.5, 'pb_ratio': 35.2}
rating = analyzer.generate_investment_rating(stock_data, tech_indicators)
print(f"综合评级: {rating['overall_rating']}")
print(f"价值评级: {rating['value_rating']}")
print(f"技术评级: {rating['technical_rating']}")
```

## 📊 支持的行业和地区

### 重点行业
- **Technology (科技)**: 半导体、人工智能、云计算、芯片、软件
- **Energy (能源)**: 石油、天然气、新能源、电池、太阳能
- **Finance (金融)**: 银行、保险、证券、金融科技、支付
- **Healthcare (医疗健康)**: 医药、生物科技、医疗器械、疫苗、基因
- **Consumer (消费品)**: 零售、电商、食品饮料、奢侈品、快消品
- **Industrial (工业制造)**: 制造业、机械、建筑、交通、物流
- **Telecom (通信)**: 通信、5G、物联网、数据中心、网络设备

### 覆盖地区
- **US (美国)**
- **CN (中国)**
- **EU (欧洲)**
- **JP (日本)**
- **KR (韩国)**
- **Global (全球)**

## 📈 股票筛选标准

### 价值投资筛选
```
PE比率: 0-25倍
PB比率: 0-3倍
股息收益率: 1%-10%
```

### 成长投资筛选
```
营收增长率: 5%-100%
盈利增长率: 10%-100%
账面价值增长率: 5%-50%
```

### 质量投资筛选
```
负债权益比: 0-1
流动比率: 1.5-10
资产回报率(ROA): 5%-100%
股权回报率(ROE): 10%-100%
```

## 📊 技术分析指标

### 趋势指标
- **移动平均线**: MA(5), MA(20), MA(50)
- **MACD**: 异同移动平均线
- **布林带**: Bollinger Bands

### 震荡指标
- **RSI**: 相对强弱指数(14日)
- **成交量比率**: 相对成交量分析

### 泵动指标
- **波动率**: 30日年化波动率
- **支撑阻力**: 关键价位识别

## 🔍 使用示例

```python
# 完整的选股分析流程
from enhanced.news_collector import NewsCollector
from enhanced.financial_analyzer import FinancialAnalyzer

# 1. 收集行业新闻
news_collector = NewsCollector()
tech_news = news_collector.collect_sector_news('technology', 'global', 7)
print(f"=== 科技行业最新动态 ===")
for news in tech_news[:3]:
    print(f"[{news['publish_date'][:10]}] {news['title']}")

# 2. 股票筛选
analyzer = FinancialAnalyzer()

# 模拟股票数据
sample_stocks = [
    {
        'symbol': 'NVDA',
        'company': '英伟达',
        'current_price': 875.28,
        'pe_ratio': 65.2,
        'pb_ratio': 25.8,
        'dividend_yield': 0.02,
        'revenue_growth': 120.5,
        'earnings_growth': 145.3,
        'debt_equity_ratio': 0.25,
        'current_ratio': 8.2,
        'roa': 28.5,
        'roe': 52.1
    },
    {
        'symbol': 'JNJ',
        'company': '强生',
        'current_price': 152.40,
        'pe_ratio': 24.8,
        'pb_ratio': 3.2,
        'dividend_yield': 2.8,
        'revenue_growth': 3.2,
        'earnings_growth': 2.1,
        'debt_equity_ratio': 0.45,
        'current_ratio': 1.8,
        'roa': 12.3,
        'roe': 24.7
    }
]

# 价值筛选
value_stocks = analyzer.screen_stocks(sample_stocks, 'value')
print(f"\n=== 价值型股票筛选结果 ===")
for stock in value_stocks:
    print(f"{stock['symbol']} - 得分: {stock['screening_score']:.2f}")

# 成长筛选
growth_stocks = analyzer.screen_stocks(sample_stocks, 'growth')
print(f"\n=== 成长型股票筛选结果 ===")
for stock in growth_stocks:
    print(f"{stock['symbol']} - 得分: {stock['screening_score']:.2f}")

# 3. 技术分析
price_data = [
    {'date': '2024-02-10', 'open': 850.0, 'high': 880.0, 'low': 845.0, 'close': 875.28, 'volume': 52000000},
    {'date': '2024-02-09', 'open': 840.0, 'high': 855.0, 'low': 835.0, 'close': 850.0, 'volume': 48000000},
    # ... 更多历史数据
]

tech_indicators = analyzer.calculate_technical_indicators(price_data)
print(f"\n=== NVDA 技术分析 ===")
print(f"价格: ${tech_indicators['ma_5']:.2f} (5日均线)")
print(f"RSI: {tech_indicators['rsi_14']:.2f}")
print(f"MACD: {tech_indicators['macd']:.4f}")
print(f"布林带上轨: ${tech_indicators['bb_upper']:.2f}")
print(f"布林带下轨: ${tech_indicators['bb_lower']:.2f}")

# 4. 投资评级
stock_data = sample_stocks[0]
rating = analyzer.generate_investment_rating(stock_data, tech_indicators)
print(f"\n=== 投资评级 ===")
print(f"综合评级: {rating['overall_rating']}")
print(f"价值评级: {rating['value_rating']}")
print(f"技术评级: {rating['technical_rating']}")
```

## ⚠️ 注意事项

1. **数据时效性**: 新闻数据具有时效性，建议定期更新
2. **模拟数据**: 当前使用模拟数据进行演示，生产环境需要连接真实数据源
3. **筛选标准**: 可根据投资策略调整筛选参数
4. **技术指标**: 需要足够的历史数据才能准确计算
5. **风险提示**: 所有分析仅供参考，不构成投资建议

---
*本模块为家族财富管理系统提供专业级的金融数据服务*