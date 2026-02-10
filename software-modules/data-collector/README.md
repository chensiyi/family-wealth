# 信息收集器 (Data Collector)

> **文件摘要**: 本文件详细定义信息收集器的技术架构、数据采集策略和质量控制规范。作为沙盘系统的数据基础，提供多源金融数据的采集、清洗、验证和存储功能。

## 🎯 系统定位与目标

信息收集器是家族财富管理系统的数据基础设施层，负责：
- **数据采集**：从权威金融数据源获取高质量数据
- **质量控制**：确保数据的准确性、完整性和时效性
- **存储管理**：建立高效可靠的数据存储体系
- **接口服务**：为上层应用提供标准化数据访问

## 🏗️ 系统架构规范

### 分层设计原则
```
数据源适配层 → 数据处理层 → 质量控制层 → 存储管理层
     ↓              ↓              ↓              ↓
  API客户端      数据清洗器      质量检查器      数据库存储
```

### 模块职责划分
- **数据源管理层**：统一管理各种数据源的接入和配置
- **采集调度层**：控制数据采集的时序和频率
- **处理引擎层**：执行数据清洗、转换和验证
- **质量监控层**：实时监控数据质量和系统健康度

## 📁 模块结构规范

```
data-collector/
├── README.md                 # 本文件 - 系统架构说明
├── data-sources/            # 数据源管理模块
│   ├── source_configs.py    # 数据源配置管理
│   ├── api_clients/         # API客户端实现
│   │   ├── fred_client.py   # FRED数据客户端
│   │   ├── yahoo_client.py  # Yahoo Finance客户端
│   │   └── sec_client.py    # SEC EDGAR客户端
│   └── scrapers/            # 网页抓取器
│       ├── html_parser.py   # HTML解析器
│       └── data_extractor.py # 数据提取器
├── processors/              # 数据处理器模块
│   ├── cleaner.py           # 数据清洗引擎
│   ├── transformer.py       # 格式转换器
│   ├── validator.py         # 数据验证器
│   └── enricher.py          # 数据增强器
├── storage/                 # 数据存储模块
│   ├── database.py          # 数据库操作接口
│   ├── cache.py             # 缓存管理器
│   └── archiver.py          # 历史数据归档
├── quality-control/         # 质量控制系统
│   ├── checker.py           # 质量检查器
│   ├── monitor.py           # 实时监控器
│   └── reporter.py          # 质量报告生成器
└── scheduler/               # 任务调度模块
    ├── task_manager.py      # 任务管理器
    ├── cron_scheduler.py    # 定时调度器
    └── priority_queue.py    # 优先级队列
```

## 🔧 核心功能规范

### 1. 多源数据采集系统
**支持的数据源类型**：
- 官方统计数据（FRED、World Bank、各国央行）
- 金融市场数据（Yahoo Finance、Alpha Vantage）
- 上市公司数据（SEC EDGAR、公司财报）
- 宏观经济指标（PMI、就业数据、通胀数据）
- 另类数据（新闻情感、社交媒体指标）

**采集策略规范**：
```python
class DataSourceManager:
    """数据源管理器 - 统一管理各类数据源的接入和配置"""
    
    def __init__(self):
        self.sources = {}  # 数据源注册表
        self.rate_limits = {}  # 访问频率限制
        self.credentials = {}  # 认证信息管理
        self.health_status = {}  # 健康状态监控
    
    def register_source(self, source_config):
        """注册数据源"""
        # 验证配置完整性
        # 初始化API客户端
        # 设置访问频率限制
        # 注册健康检查回调
        pass
    
    def fetch_data(self, source_name, parameters):
        """获取数据"""
        # 检查访问频率限制
        # 执行API调用
        # 处理响应数据
        # 记录访问日志
        pass
    
    def health_check(self, source_name):
        """健康状态检查"""
        # 检查API可用性
        # 验证响应时间
        # 监控错误率
        # 更新健康状态
        pass
```

### 2. 数据处理流水线
**处理步骤规范**：
1. **数据获取** - 从源获取原始数据
2. **格式标准化** - 统一数据格式和编码
3. **异常值检测** - 识别和标记异常数据
4. **缺失值处理** - 合理填补或标记缺失数据
5. **质量评分** - 评估数据质量等级

**处理实现示例**：
```python
# processors/cleaner.py
class DataCleaner:
    """数据清洗器 - 执行专业的数据清理操作"""
    
    def __init__(self):
        self.cleaning_rules = self._load_cleaning_rules()
        self.validation_rules = self._load_validation_rules()
    
    def clean_market_data(self, raw_data):
        """清洗市场数据"""
        # 数据类型验证
        cleaned_data = self._validate_data_types(raw_data)
        
        # 重复记录处理
        cleaned_data = self._remove_duplicates(cleaned_data)
        
        # 异常值检测和处理
        cleaned_data = self._detect_and_handle_outliers(cleaned_data)
        
        # 缺失值处理
        cleaned_data = self._handle_missing_values(cleaned_data)
        
        # 数据范围验证
        cleaned_data = self._validate_data_ranges(cleaned_data)
        
        return cleaned_data
    
    def _detect_outliers(self, data_series, method='iqr'):
        """异常值检测"""
        if method == 'iqr':
            Q1 = data_series.quantile(0.25)
            Q3 = data_series.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers = (data_series < lower_bound) | (data_series > upper_bound)
        elif method == 'zscore':
            z_scores = np.abs(stats.zscore(data_series))
            outliers = z_scores > 3
        return outliers
```

### 3. 质量控制系统
**质量评估维度**：
- **完整性**：数据是否完整无缺失（权重25%）
- **准确性**：数据值是否合理准确（权重30%）
- **时效性**：数据是否及时更新（权重20%）
- **一致性**：不同来源数据是否一致（权重15%）
- **可靠性**：数据源是否可信（权重10%）

**质量监控实现**：
```python
# quality-control/checker.py
class QualityChecker:
    """质量检查器 - 执行全面的数据质量评估"""
    
    def __init__(self):
        self.quality_weights = {
            'completeness': 0.25,
            'accuracy': 0.30,
            'timeliness': 0.20,
            'consistency': 0.15,
            'reliability': 0.10
        }
        self.thresholds = {
            'minimum_score': 0.80,
            'critical_error_threshold': 0.50
        }
    
    def assess_data_quality(self, data, source_info):
        """评估数据质量"""
        quality_scores = {}
        
        # 完整性检查
        quality_scores['completeness'] = self._check_completeness(data)
        
        # 准确性验证
        quality_scores['accuracy'] = self._check_accuracy(data, source_info)
        
        # 时效性评估
        quality_scores['timeliness'] = self._check_timeliness(data)
        
        # 一致性检查
        quality_scores['consistency'] = self._check_consistency(data)
        
        # 可靠性评分
        quality_scores['reliability'] = self._assess_reliability(source_info)
        
        # 计算综合质量分数
        overall_score = self._calculate_weighted_score(quality_scores)
        
        return {
            'scores': quality_scores,
            'overall_score': overall_score,
            'issues': self._identify_quality_issues(quality_scores),
            'recommendations': self._generate_improvement_suggestions(quality_scores)
        }
    
    def _check_completeness(self, data):
        """检查数据完整性"""
        total_records = len(data)
        complete_records = data.dropna().shape[0]
        completeness_ratio = complete_records / total_records
        return completeness_ratio
```

### 4. 存储管理策略
**存储分层规范**：
- **热数据**：最近1年的高频访问数据
- **温数据**：1-5年的中频访问数据
- **冷数据**：5年以上的低频访问数据

**数据库设计**：
```sql
-- 核心数据表结构
CREATE TABLE market_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    date DATE NOT NULL,
    open_price REAL,
    high_price REAL,
    low_price REAL,
    close_price REAL NOT NULL,
    volume INTEGER,
    adjusted_close REAL,
    dividend REAL DEFAULT 0,
    split_coefficient REAL DEFAULT 1,
    source TEXT NOT NULL,
    quality_score REAL DEFAULT 1.0,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, date, source)
);

-- 元数据表
CREATE TABLE data_source_metadata (
    source_name TEXT PRIMARY KEY,
    source_type TEXT NOT NULL,
    base_url TEXT,
    api_endpoint TEXT,
    last_accessed TIMESTAMP,
    success_rate REAL DEFAULT 1.0,
    average_response_time REAL,
    reliability_score REAL DEFAULT 1.0,
    supported_indicators TEXT,
    rate_limit INTEGER,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 质量监控表
CREATE TABLE data_quality_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_table TEXT NOT NULL,
    check_date DATE NOT NULL,
    completeness_score REAL,
    accuracy_score REAL,
    timeliness_score REAL,
    consistency_score REAL,
    overall_score REAL,
    issues_found TEXT,
    checked_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 📊 API接口规范

### 内部API设计
```python
class DataCollectorAPI:
    """数据收集器API接口 - 提供标准化的数据访问服务"""
    
    def get_latest_data(self, symbol, data_type="market"):
        """获取最新数据"""
        # 参数验证
        # 数据查询
        # 质量检查
        # 返回标准化格式
        pass
    
    def get_historical_data(self, symbol, start_date, end_date):
        """获取历史数据"""
        # 日期范围验证
        # 批量数据查询
        # 数据排序和格式化
        # 分页返回支持
        pass
    
    def get_data_quality_report(self, symbol=None, date_range=None):
        """获取数据质量报告"""
        # 质量指标查询
        # 统计分析计算
        # 报告格式化
        # 可视化数据准备
        pass
    
    def force_refresh_source(self, source_name):
        """强制刷新数据源"""
        # 权限验证
        # 立即执行采集
        # 状态更新
        # 结果反馈
        pass
```

### 外部接口规范（未来扩展）
```python
# RESTful API设计示例
@app.route('/api/v1/data/<symbol>', methods=['GET'])
def get_symbol_data(symbol):
    """获取指定标的的数据"""
    # 认证和授权检查
    # 参数解析和验证
    # 数据查询和处理
    # JSON格式响应
    pass

@app.route('/api/v1/quality/metrics', methods=['GET'])
def get_quality_metrics():
    """获取数据质量指标"""
    # 聚合质量统计数据
    # 计算各项指标
    # 返回标准化质量报告
    pass
```

## 🔧 配置管理规范

### 数据源配置文件
```yaml
# config/data_sources.yaml
sources:
  fred:
    name: "Federal Reserve Economic Data"
    type: "official"
    base_url: "https://api.stlouisfed.org/fred"
    api_key: "${FRED_API_KEY}"
    rate_limit: 120  # 每分钟请求数
    reliability: 0.99
    supported_series: 
      - "GDP"
      - "UNRATE"
      - "CPIAUCSL"
      - "FEDFUNDS"
  
  yahoo_finance:
    name: "Yahoo Finance API"
    type: "financial"
    base_url: "https://query1.finance.yahoo.com"
    rate_limit: 2000
    reliability: 0.95
    supported_symbols:
      - "^GSPC"  # S&P 500
      - "AAPL"
      - "GOOGL"
      - "MSFT"
  
  sec_edgar:
    name: "SEC EDGAR Database"
    type: "regulatory"
    base_url: "https://data.sec.gov"
    rate_limit: 10
    reliability: 0.98
    supported_forms:
      - "10-K"
      - "10-Q"
      - "13F-HR"

collection_schedule:
  real_time: ["market_data"]  # 实时更新
  daily: ["economic_indicators", "fundamental_data"]  # 每日更新
  weekly: ["company_filings", "alternative_data"]  # 每周更新
  monthly: ["macro_reports", "industry_analysis"]  # 每月更新
```

### 处理规则配置
```python
# config/processing_rules.py
PROCESSING_RULES = {
    'market_data': {
        'required_fields': ['symbol', 'date', 'close_price'],
        'validation_rules': {
            'price_range': (0, 1000000),  # 价格范围验证
            'volume_range': (0, 10000000000),  # 成交量范围
            'date_format': '%Y-%m-%d'  # 日期格式
        },
        'cleaning_rules': {
            'handle_duplicates': 'keep_latest',  # 重复数据处理策略
            'missing_price_strategy': 'forward_fill',  # 缺失价格填补
            'outlier_detection': 'modified_zscore',  # 异常值检测方法
            'outlier_threshold': 3.5  # 异常值阈值
        }
    },
    'economic_indicators': {
        'required_fields': ['indicator_name', 'date', 'value'],
        'validation_rules': {
            'value_range': (-1000000, 1000000),  # 指标值范围
            'frequency_options': ['daily', 'weekly', 'monthly', 'quarterly', 'yearly']
        }
    }
}
```

## 🚀 部署和运行规范

### 运行环境要求
```bash
# 系统依赖检查
python --version  # Python 3.14+
pip list | grep -E "(requests|pandas|numpy|sqlite3)"  # 核心依赖

# 环境变量设置
export FRED_API_KEY="your_api_key_here"
export DATA_COLLECTOR_CONFIG="config/data_sources.yaml"

# 系统启动
cd software-modules/data-collector
python collector_main.py --config config/data_sources.yaml

# 调度服务启动
python scheduler_service.py --daemon
```

### 系统监控规范
```python
class SystemMonitor:
    """系统监控器 - 实时监控数据收集器运行状态"""
    
    def __init__(self):
        self.metrics = {
            'collection_success_rate': 0.0,
            'average_processing_time': 0.0,
            'data_quality_score': 0.0,
            'storage_utilization': 0.0,
            'active_connections': 0
        }
        self.alert_thresholds = {
            'success_rate': 0.95,
            'processing_time': 30.0,  # 秒
            'quality_score': 0.80,
            'storage_usage': 0.85
        }
    
    def collect_system_metrics(self):
        """收集系统指标"""
        # CPU和内存使用率
        # 磁盘空间使用情况
        # 网络连接状态
        # 数据库性能指标
        pass
    
    def generate_health_report(self):
        """生成健康报告"""
        # 系统状态评估
        # 性能瓶颈识别
        # 改进建议生成
        # 告警信息汇总
        pass
```

## 📈 性能优化规范

### 并发处理机制
```python
class ConcurrentCollector:
    """并发收集器 - 支持多数据源并行采集"""
    
    def __init__(self, max_workers=10):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.semaphores = {}  # 用于控制访问频率
        self.timeout_settings = {}  # 超时配置
    
    def collect_multiple_sources(self, source_configs):
        """并发收集多个数据源"""
        futures = []
        for config in source_configs:
            # 应用访问频率控制
            semaphore = self._get_semaphore(config['source_name'])
            future = self.executor.submit(
                self._collect_with_semaphore, 
                config, 
                semaphore
            )
            futures.append(future)
        
        # 等待所有任务完成
        results = []
        for future in futures:
            try:
                result = future.result(timeout=300)  # 5分钟超时
                results.append(result)
            except Exception as e:
                logger.error(f"数据采集失败: {e}")
                results.append(None)
        
        return results
```

### 缓存优化策略
```python
class SmartCache:
    """智能缓存管理器 - 优化数据访问性能"""
    
    def __init__(self):
        self.cache = {}  # 内存缓存
        self.redis_client = None  # Redis客户端（可选）
        self.access_patterns = {}  # 访问模式统计
        self.expiration_policies = {}  # 过期策略
    
    def get_with_ttl(self, key, ttl=3600):
        """带TTL的缓存获取"""
        # 检查内存缓存
        if key in self.cache:
            data, expiry_time = self.cache[key]
            if time.time() < expiry_time:
                self._update_access_pattern(key)
                return data
            else:
                del self.cache[key]
        
        # 检查持久化缓存
        if self.redis_client:
            cached_data = self.redis_client.get(key)
            if cached_data:
                self.cache[key] = (cached_data, time.time() + ttl)
                return cached_data
        
        return None
    
    def set_with_ttl(self, key, data, ttl=3600):
        """带TTL的缓存设置"""
        expiry_time = time.time() + ttl
        self.cache[key] = (data, expiry_time)
        
        # 同步到持久化存储
        if self.redis_client:
            self.redis_client.setex(key, ttl, data)
        
        self._update_access_pattern(key)
```

## 🔐 安全与合规规范

### 访问控制机制
```python
class AccessController:
    """访问控制器 - 管理数据访问权限和安全控制"""
    
    def __init__(self):
        self.api_keys = {}  # API密钥管理
        self.rate_limits = {}  # 访问频率限制
        self.blocked_ips = set()  # 黑名单IP
        self.access_logs = []  # 访问日志
    
    def validate_api_key(self, api_key, required_permissions=None):
        """验证API密钥权限"""
        if api_key not in self.api_keys:
            raise AuthenticationError("无效的API密钥")
        
        key_info = self.api_keys[api_key]
        if key_info['status'] != 'active':
            raise AuthorizationError("API密钥已被禁用")
        
        if required_permissions:
            user_permissions = set(key_info['permissions'])
            required_set = set(required_permissions)
            if not required_set.issubset(user_permissions):
                raise AuthorizationError("权限不足")
        
        return True
    
    def check_rate_limit(self, client_identifier, endpoint=None):
        """检查访问频率限制"""
        current_time = time.time()
        window_start = current_time - 3600  # 1小时窗口
        
        # 清理过期记录
        self.access_logs = [
            log for log in self.access_logs 
            if log['timestamp'] > window_start
        ]
        
        # 统计当前访问次数
        recent_accesses = [
            log for log in self.access_logs 
            if log['client'] == client_identifier
        ]
        
        if len(recent_accesses) >= self.rate_limits.get(endpoint, 1000):
            raise RateLimitError("访问频率超出限制")
        
        # 记录本次访问
        self.access_logs.append({
            'client': client_identifier,
            'endpoint': endpoint,
            'timestamp': current_time
        })
```

### 数据合规要求
- 严格遵守各数据源的使用条款和许可协议
- 建立完整的数据使用日志和审计追踪
- 定期审查数据采集和使用合规性
- 实施数据最小化原则，只采集必要数据
- 建立数据删除和清理机制

## 🛠️ 维护和支持规范

### 日志系统规范
```python
import logging
import logging.handlers

class DataCollectorLogger:
    """数据收集器日志系统 - 提供完整的日志记录功能"""
    
    def __init__(self, log_level=logging.INFO):
        self.logger = logging.getLogger('data_collector')
        self.logger.setLevel(log_level)
        
        # 文件处理器
        file_handler = logging.handlers.RotatingFileHandler(
            'logs/data_collector.log',
            maxBytes=50*1024*1024,  # 50MB
            backupCount=5
        )
        file_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        )
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter(
                '%(levelname)s - %(message)s'
            )
        )
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def log_collection_attempt(self, source, status, details=None):
        """记录数据采集尝试"""
        message = f"数据采集 [{source}] - 状态: {status}"
        if details:
            message += f" - 详情: {details}"
        
        if status == 'SUCCESS':
            self.logger.info(message)
        elif status == 'FAILED':
            self.logger.error(message)
        else:
            self.logger.warning(message)
    
    def log_data_quality_issue(self, issue_type, severity, details):
        """记录数据质量问题"""
        message = f"数据质量问题 [{issue_type}] - 严重性: {severity} - {details}"
        if severity == 'HIGH':
            self.logger.error(message)
        elif severity == 'MEDIUM':
            self.logger.warning(message)
        else:
            self.logger.info(message)
```

### 故障恢复机制
```python
class RecoveryManager:
    """故障恢复管理器 - 处理系统故障和异常情况"""
    
    def __init__(self):
        self.retry_policies = {
            'network_errors': {'max_attempts': 3, 'delay': 5},
            'api_errors': {'max_attempts': 2, 'delay': 10},
            'database_errors': {'max_attempts': 1, 'delay': 0}
        }
        self.backup_sources = {}  # 备用数据源配置
        self.failure_history = []  # 故障历史记录
    
    def handle_source_failure(self, source_name, error):
        """处理数据源故障"""
        # 记录故障信息
        failure_record = {
            'source': source_name,
            'error': str(error),
            'timestamp': datetime.now(),
            'attempt_count': 1
        }
        self.failure_history.append(failure_record)
        
        # 尝试备用方案
        if source_name in self.backup_sources:
            return self._switch_to_backup_source(source_name)
        
        # 实施重试策略
        retry_policy = self._get_retry_policy(error)
        return self._execute_retry_strategy(source_name, error, retry_policy)
    
    def _switch_to_backup_source(self, primary_source):
        """切换到备用数据源"""
        backup_config = self.backup_sources[primary_source]
        # 初始化备用源连接
        # 验证备用源可用性
        # 更新数据源配置
        pass
```

## 🔄 更新原则

### 文档维护要求
- 每次功能更新必须同步更新相关文档
- 保持与主知识体系文档的一致性
- 维护完整的版本变更记录
- 定期进行文档质量审查

### 质量保证措施
- 代码审查和同行评审制度
- 单元测试和集成测试覆盖≥90%
- 数据质量持续监控和报告
- 用户反馈收集和处理机制

---
*本文档遵循项目架构设计规范，任何修改都必须经过严格评审和测试验证*