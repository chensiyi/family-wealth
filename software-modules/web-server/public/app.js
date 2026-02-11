// 家族财富管理系统前端应用
// Family Wealth Management System Frontend Application

class FamilyWealthApp {
    constructor() {
        this.portfolio = null;
        this.newsData = [];
        this.settings = {
            initialCash: 1000000,
            currency: 'CNY',
            autoRefresh: true,
            refreshInterval: 30
        };
        this.init();
    }

    init() {
        this.loadSettings();
        this.setupEventListeners();
        this.initializePortfolio();
        this.loadDashboard();
        this.startAutoRefresh();
    }

    // 初始化投资组合
    initializePortfolio() {
        // 模拟初始投资组合数据
        this.portfolio = {
            cash: this.settings.initialCash,
            positions: [],
            transactions: [],
            totalValue: this.settings.initialCash,
            unrealizedPnl: 0,
            positionCount: 0
        };

        // 添加一些示例持仓
        this.addSamplePositions();
    }

    // 添加示例持仓数据
    addSamplePositions() {
        const samplePositions = [
            {
                symbol: 'NVDA',
                name: '英伟达',
                quantity: 100,
                costBasis: 850.00,
                currentPrice: 875.28,
                marketValue: 87528,
                unrealizedPnl: 2528,
                unrealizedPnlPercent: 2.97
            },
            {
                symbol: 'JNJ',
                name: '强生',
                quantity: 200,
                costBasis: 150.00,
                currentPrice: 152.40,
                marketValue: 30480,
                unrealizedPnl: 480,
                unrealizedPnlPercent: 1.60
            },
            {
                symbol: 'MSFT',
                name: '微软',
                quantity: 150,
                costBasis: 380.00,
                currentPrice: 395.50,
                marketValue: 59325,
                unrealizedPnl: 2325,
                unrealizedPnlPercent: 4.08
            }
        ];

        this.portfolio.positions = samplePositions;
        this.portfolio.positionCount = samplePositions.length;
        this.updatePortfolioValues();
    }

    // 更新投资组合价值计算
    updatePortfolioValues() {
        const positionsValue = this.portfolio.positions.reduce((sum, pos) => sum + pos.marketValue, 0);
        this.portfolio.positionsValue = positionsValue;
        this.portfolio.totalValue = this.portfolio.cash + positionsValue;
        this.portfolio.unrealizedPnl = this.portfolio.positions.reduce((sum, pos) => sum + pos.unrealizedPnl, 0);
    }

    // 设置事件监听器
    setupEventListeners() {
        // 导航标签切换
        document.querySelectorAll('[data-tab]').forEach(tab => {
            tab.addEventListener('click', (e) => {
                e.preventDefault();
                this.switchTab(tab.getAttribute('data-tab'));
            });
        });

        // 表单提交事件
        document.getElementById('buyForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleBuyStock();
        });

        document.getElementById('sellForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSellStock();
        });

        // 按钮点击事件
        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.refreshAllData();
        });

        document.getElementById('refreshNews').addEventListener('click', () => {
            this.loadNews();
        });

        document.getElementById('runScreening').addEventListener('click', () => {
            this.runStockScreening();
        });

        document.getElementById('saveSettings').addEventListener('click', () => {
            this.saveSettings();
        });

        // 下拉框变化事件
        document.getElementById('sellSymbol').addEventListener('change', (e) => {
            this.updateSellForm(e.target.value);
        });
    }

    // 切换标签页
    switchTab(tabName) {
        // 更新导航激活状态
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // 显示对应内容
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');

        // 加载对应页面数据
        switch(tabName) {
            case 'dashboard':
                this.loadDashboard();
                break;
            case 'portfolio':
                this.loadPortfolio();
                break;
            case 'trading':
                this.loadTradingForm();
                break;
            case 'news':
                this.loadNews();
                break;
            case 'analysis':
                this.loadAnalysis();
                break;
        }
    }

    // 加载仪表板数据
    loadDashboard() {
        this.updatePortfolioValues();
        
        // 更新统计数字
        document.getElementById('totalValue').textContent = this.formatCurrency(this.portfolio.totalValue);
        document.getElementById('cashBalance').textContent = this.formatCurrency(this.portfolio.cash);
        document.getElementById('unrealizedPnl').textContent = this.formatCurrency(this.portfolio.unrealizedPnl);
        document.getElementById('positionCount').textContent = this.portfolio.positionCount;

        // 更新持仓表格
        this.updatePositionsTable();
    }

    // 更新持仓表格
    updatePositionsTable() {
        const tbody = document.getElementById('positionsBody');
        if (this.portfolio.positions.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">暂无持仓数据</td></tr>';
            return;
        }

        tbody.innerHTML = this.portfolio.positions.map(position => `
            <tr>
                <td><strong>${position.symbol}</strong><br><small class="text-muted">${position.name}</small></td>
                <td>${position.quantity}</td>
                <td>${this.formatCurrency(position.costBasis)}</td>
                <td>${this.formatCurrency(position.currentPrice)}</td>
                <td>${this.formatCurrency(position.marketValue)}</td>
                <td class="${position.unrealizedPnl >= 0 ? 'text-success' : 'text-danger'}">
                    ${this.formatCurrency(position.unrealizedPnl)}
                </td>
                <td class="${position.unrealizedPnlPercent >= 0 ? 'text-success' : 'text-danger'}">
                    ${position.unrealizedPnlPercent.toFixed(2)}%
                </td>
            </tr>
        `).join('');
    }

    // 加载持仓管理页面
    loadPortfolio() {
        this.updatePortfolioValues();
        
        // 更新持仓统计
        document.getElementById('statsMarketValue').textContent = this.formatCurrency(this.portfolio.positionsValue);
        document.getElementById('statsCostValue').textContent = this.formatCurrency(
            this.portfolio.positions.reduce((sum, pos) => sum + (pos.quantity * pos.costBasis), 0)
        );
        document.getElementById('statsTotalPnl').textContent = this.formatCurrency(this.portfolio.unrealizedPnl);
        document.getElementById('statsPnlRate').textContent = 
            this.portfolio.positionsValue > 0 ? 
            ((this.portfolio.unrealizedPnl / (this.portfolio.totalValue - this.portfolio.unrealizedPnl)) * 100).toFixed(2) + '%' :
            '0.00%';

        // 更新持仓列表
        const tbody = document.getElementById('portfolioBody');
        tbody.innerHTML = this.portfolio.positions.map(position => `
            <tr>
                <td>
                    <strong>${position.symbol}</strong><br>
                    <small class="text-muted">${position.name}</small>
                </td>
                <td>${position.quantity}</td>
                <td>${this.formatCurrency(position.costBasis)}</td>
                <td>${this.formatCurrency(position.currentPrice)}</td>
                <td>${this.formatCurrency(position.marketValue)}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary me-1" onclick="app.showPositionDetail('${position.symbol}')">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="app.prepareSell('${position.symbol}')">
                        <i class="fas fa-arrow-down"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    }

    // 加载交易表单
    loadTradingForm() {
        // 更新卖出表单的股票选择
        const select = document.getElementById('sellSymbol');
        select.innerHTML = '<option value="">请选择持仓股票</option>' + 
            this.portfolio.positions.map(pos => 
                `<option value="${pos.symbol}">${pos.symbol} - ${pos.name}</option>`
            ).join('');
    }

    // 处理买入股票
    handleBuyStock() {
        const symbol = document.getElementById('buySymbol').value.toUpperCase();
        const quantity = parseFloat(document.getElementById('buyQuantity').value);
        const price = parseFloat(document.getElementById('buyPrice').value);
        const fee = parseFloat(document.getElementById('buyFee').value) || 0;
        const description = document.getElementById('buyDescription').value;

        if (!symbol || !quantity || !price) {
            this.showToast('请填写完整的交易信息', 'warning');
            return;
        }

        const totalCost = (quantity * price) + fee;
        if (totalCost > this.portfolio.cash) {
            this.showToast('资金不足，无法完成交易', 'danger');
            return;
        }

        // 创建新持仓或更新现有持仓
        let position = this.portfolio.positions.find(p => p.symbol === symbol);
        if (position) {
            // 更新现有持仓
            const totalShares = position.quantity + quantity;
            const totalCostBasis = (position.quantity * position.costBasis) + (quantity * price);
            position.costBasis = totalCostBasis / totalShares;
            position.quantity = totalShares;
            position.currentPrice = price;
        } else {
            // 创建新持仓
            position = {
                symbol: symbol,
                name: this.getCompanyName(symbol),
                quantity: quantity,
                costBasis: price,
                currentPrice: price,
                marketValue: quantity * price,
                unrealizedPnl: 0,
                unrealizedPnlPercent: 0
            };
            this.portfolio.positions.push(position);
            this.portfolio.positionCount++;
        }

        // 更新持仓价值
        position.marketValue = position.quantity * position.currentPrice;
        position.unrealizedPnl = position.marketValue - (position.quantity * position.costBasis);
        position.unrealizedPnlPercent = ((position.unrealizedPnl / (position.quantity * position.costBasis)) * 100);

        // 更新现金和总价值
        this.portfolio.cash -= totalCost;
        this.updatePortfolioValues();

        // 记录交易
        this.portfolio.transactions.push({
            id: Date.now(),
            symbol: symbol,
            type: 'BUY',
            quantity: quantity,
            price: price,
            fee: fee,
            amount: -totalCost,
            description: description,
            timestamp: new Date()
        });

        // 清空表单
        document.getElementById('buyForm').reset();

        // 更新界面
        this.loadDashboard();
        this.showToast('买入交易成功完成', 'success');
    }

    // 处理卖出股票
    handleSellStock() {
        const symbol = document.getElementById('sellSymbol').value;
        const quantity = parseFloat(document.getElementById('sellQuantity').value);
        const price = parseFloat(document.getElementById('sellPrice').value);
        const fee = parseFloat(document.getElementById('sellFee').value) || 0;
        const description = document.getElementById('sellDescription').value;

        if (!symbol || !quantity || !price) {
            this.showToast('请填写完整的交易信息', 'warning');
            return;
        }

        const position = this.portfolio.positions.find(p => p.symbol === symbol);
        if (!position || quantity > position.quantity) {
            this.showToast('卖出数量超过持仓数量', 'danger');
            return;
        }

        // 计算收入
        const proceeds = (quantity * price) - fee;
        this.portfolio.cash += proceeds;

        // 更新持仓
        position.quantity -= quantity;
        const realizedPnl = quantity * (price - position.costBasis);

        if (position.quantity === 0) {
            // 全部卖出，移除持仓
            this.portfolio.positions = this.portfolio.positions.filter(p => p.symbol !== symbol);
            this.portfolio.positionCount--;
        } else {
            // 部分卖出，更新持仓价值
            position.marketValue = position.quantity * position.currentPrice;
            position.unrealizedPnl = position.marketValue - (position.quantity * position.costBasis);
            position.unrealizedPnlPercent = ((position.unrealizedPnl / (position.quantity * position.costBasis)) * 100);
        }

        this.updatePortfolioValues();

        // 记录交易
        this.portfolio.transactions.push({
            id: Date.now(),
            symbol: symbol,
            type: 'SELL',
            quantity: quantity,
            price: price,
            fee: fee,
            amount: proceeds,
            realizedPnl: realizedPnl,
            description: description,
            timestamp: new Date()
        });

        // 清空表单
        document.getElementById('sellForm').reset();

        // 更新界面
        this.loadDashboard();
        this.loadTradingForm();
        this.showToast(`卖出交易成功完成，实现盈亏: ${this.formatCurrency(realizedPnl)}`, 'success');
    }

    // 更新卖出表单
    updateSellForm(symbol) {
        const position = this.portfolio.positions.find(p => p.symbol === symbol);
        if (position) {
            document.getElementById('sellQuantity').max = position.quantity;
            document.getElementById('sellPrice').value = position.currentPrice.toFixed(2);
        }
    }

    // 准备卖出操作
    prepareSell(symbol) {
        this.switchTab('trading');
        document.getElementById('sellSymbol').value = symbol;
        this.updateSellForm(symbol);
    }

    // 加载新闻数据
    loadNews() {
        const container = document.getElementById('newsContainer');
        container.innerHTML = '<div class="text-center"><i class="fas fa-spinner fa-spin"></i> 正在加载新闻...</div>';

        // 模拟新闻数据
        setTimeout(() => {
            const newsItems = this.generateSampleNews();
            this.newsData = newsItems;
            this.displayNews(newsItems);
        }, 1000);
    }

    // 生成示例新闻数据
    generateSampleNews() {
        const sectors = ['technology', 'energy', 'finance', 'healthcare'];
        const regions = ['us', 'cn', 'global'];
        const newsList = [];

        for (let i = 0; i < 15; i++) {
            const sector = sectors[Math.floor(Math.random() * sectors.length)];
            const region = regions[Math.floor(Math.random() * regions.length)];
            
            newsList.push({
                id: i + 1,
                title: this.generateNewsTitle(sector),
                summary: this.generateNewsSummary(sector),
                source: ['财经网', '华尔街日报', '路透社', '彭博社', '第一财经'][Math.floor(Math.random() * 5)],
                publishDate: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000),
                sector: sector,
                region: region,
                impactScore: (Math.random() * 0.9 + 0.1).toFixed(2)
            });
        }

        return newsList.sort((a, b) => b.publishDate - a.publishDate);
    }

    // 生成新闻标题
    generateNewsTitle(sector) {
        const titles = {
            technology: [
                '英伟达发布新一代AI芯片，性能提升3倍',
                '苹果公司推出革命性AR眼镜产品',
                '谷歌宣布量子计算重大突破',
                '台积电扩产计划获政府批准'
            ],
            energy: [
                '国际油价突破每桶90美元关口',
                '特斯拉发布新一代电池技术',
                '沙特阿美宣布大规模投资计划',
                '全球可再生能源投资创历史新高'
            ],
            finance: [
                '美联储暗示可能暂停加息周期',
                '中国央行下调存款准备金率',
                '摩根大通预测明年经济增长放缓',
                '比特币价格重回3万美元上方'
            ],
            healthcare: [
                '辉瑞新冠疫苗获新适应症批准',
                '基因编辑技术治疗遗传病获突破',
                '强生发布新型抗癌药物临床试验结果',
                '全球老龄化趋势推动医疗支出增长'
            ]
        };
        
        const sectorTitles = titles[sector] || titles.technology;
        return sectorTitles[Math.floor(Math.random() * sectorTitles.length)];
    }

    // 生成新闻摘要
    generateNewsSummary(sector) {
        const summaries = {
            technology: '科技行业迎来重大技术突破，相关概念股值得关注',
            energy: '能源市场波动加剧，投资者需密切关注政策变化',
            finance: '金融市场流动性充裕，央行政策走向成为焦点',
            healthcare: '医疗健康产业快速发展，创新药企前景广阔'
        };
        return summaries[sector] || '重要市场动态，建议投资者重点关注';
    }

    // 显示新闻
    displayNews(newsItems) {
        const container = document.getElementById('newsContainer');
        
        if (newsItems.length === 0) {
            container.innerHTML = '<div class="text-center text-muted">暂无相关新闻</div>';
            return;
        }

        container.innerHTML = newsItems.map(news => `
            <div class="news-item">
                <div class="d-flex justify-content-between align-items-start">
                    <h6>${news.title}</h6>
                    <span class="badge bg-primary">${this.getSectorName(news.sector)}</span>
                </div>
                <p class="text-muted mb-2">${news.summary}</p>
                <div class="d-flex justify-content-between align-items-center">
                    <small class="text-muted">
                        <i class="fas fa-clock me-1"></i>${news.publishDate.toLocaleDateString()}
                        <i class="fas fa-newspaper ms-2 me-1"></i>${news.source}
                    </small>
                    <small class="text-success">
                        <i class="fas fa-bolt me-1"></i>影响力: ${(parseFloat(news.impactScore) * 100).toFixed(0)}%
                    </small>
                </div>
            </div>
        `).join('');
    }

    // 运行股票筛选
    runStockScreening() {
        const criteria = document.getElementById('screeningCriteria').value;
        const resultsDiv = document.getElementById('screeningResults');
        
        resultsDiv.innerHTML = '<div class="text-center"><i class="fas fa-spinner fa-spin"></i> 正在筛选股票...</div>';

        // 模拟筛选过程
        setTimeout(() => {
            const screenedStocks = this.performStockScreening(criteria);
            this.displayScreeningResults(screenedStocks, criteria);
        }, 1500);
    }

    // 执行股票筛选
    performStockScreening(criteria) {
        const sampleStocks = [
            { symbol: 'NVDA', name: '英伟达', score: 0.92, reason: 'AI芯片龙头，业绩增长强劲' },
            { symbol: 'MSFT', name: '微软', score: 0.85, reason: '云计算业务持续扩张' },
            { symbol: 'GOOGL', name: '谷歌', score: 0.78, reason: '广告业务复苏明显' },
            { symbol: 'AMZN', name: '亚马逊', score: 0.88, reason: 'AWS云服务市场份额领先' },
            { symbol: 'TSLA', name: '特斯拉', score: 0.72, reason: '电动车市场竞争加剧' }
        ];
        
        return sampleStocks.sort((a, b) => b.score - a.score);
    }

    // 显示筛选结果
    displayScreeningResults(stocks, criteria) {
        const resultsDiv = document.getElementById('screeningResults');
        
        if (stocks.length === 0) {
            resultsDiv.innerHTML = '<div class="alert alert-info">未找到符合条件的股票</div>';
            return;
        }

        const criteriaNames = {
            'value': '价值投资',
            'growth': '成长投资', 
            'quality': '质量投资'
        };

        resultsDiv.innerHTML = `
            <div class="alert alert-success">
                <strong>${criteriaNames[criteria]}</strong> 筛选完成，共找到 ${stocks.length} 只符合条件的股票
            </div>
            <div class="list-group">
                ${stocks.map((stock, index) => `
                    <div class="list-group-item">
                        <div class="d-flex justify-content-between">
                            <div>
                                <h6 class="mb-1">${stock.symbol} - ${stock.name}</h6>
                                <p class="mb-1 text-muted">${stock.reason}</p>
                            </div>
                            <div class="text-end">
                                <span class="badge bg-primary">得分: ${(stock.score * 100).toFixed(0)}%</span>
                                <button class="btn btn-sm btn-outline-primary ms-2" 
                                        onclick="app.quickBuy('${stock.symbol}')">
                                    <i class="fas fa-plus"></i> 快速买入
                                </button>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    // 快速买入
    quickBuy(symbol) {
        this.switchTab('trading');
        document.getElementById('buySymbol').value = symbol;
        // 可以预填充其他字段
        this.showToast(`已为您准备买入 ${symbol} 的交易表单`, 'info');
    }

    // 加载分析数据
    loadAnalysis() {
        // 模拟风险指标数据
        document.getElementById('sharpeRatio').textContent = '1.25';
        document.getElementById('volatility').textContent = '15.8%';
        document.getElementById('maxDrawdown').textContent = '-8.3%';
        document.getElementById('totalReturn').textContent = '+12.6%';
    }

    // 刷新所有数据
    refreshAllData() {
        this.loadDashboard();
        this.showToast('数据已刷新', 'info');
    }

    // 开始自动刷新
    startAutoRefresh() {
        if (this.settings.autoRefresh) {
            setInterval(() => {
                // 模拟价格波动
                this.simulatePriceChanges();
                if (document.getElementById('dashboard-tab').classList.contains('active')) {
                    this.loadDashboard();
                }
            }, this.settings.refreshInterval * 1000);
        }
    }

    // 模拟价格变化
    simulatePriceChanges() {
        this.portfolio.positions.forEach(position => {
            // 随机价格波动 (-2% 到 +2%)
            const changePercent = (Math.random() - 0.5) * 0.04;
            position.currentPrice = position.currentPrice * (1 + changePercent);
            position.currentPrice = Math.round(position.currentPrice * 100) / 100;
            
            // 更新相关计算
            position.marketValue = position.quantity * position.currentPrice;
            position.unrealizedPnl = position.marketValue - (position.quantity * position.costBasis);
            position.unrealizedPnlPercent = ((position.unrealizedPnl / (position.quantity * position.costBasis)) * 100);
        });
        this.updatePortfolioValues();
    }

    // 工具函数
    formatCurrency(amount) {
        return new Intl.NumberFormat('zh-CN', {
            style: 'currency',
            currency: this.settings.currency,
            minimumFractionDigits: 2
        }).format(amount);
    }

    getCompanyName(symbol) {
        const names = {
            'NVDA': '英伟达',
            'JNJ': '强生',
            'MSFT': '微软',
            'AAPL': '苹果',
            'GOOGL': '谷歌',
            'AMZN': '亚马逊',
            'TSLA': '特斯拉',
            'META': 'Meta',
            'NFLX': '网飞'
        };
        return names[symbol] || symbol;
    }

    getSectorName(sector) {
        const names = {
            'technology': '科技',
            'energy': '能源',
            'finance': '金融',
            'healthcare': '医疗',
            'consumer': '消费'
        };
        return names[sector] || sector;
    }

    // 设置相关方法
    loadSettings() {
        const saved = localStorage.getItem('familyWealthSettings');
        if (saved) {
            this.settings = { ...this.settings, ...JSON.parse(saved) };
        }
    }

    saveSettings() {
        this.settings.initialCash = parseFloat(document.getElementById('initialCash').value);
        this.settings.currency = document.getElementById('currency').value;
        this.settings.autoRefresh = document.getElementById('autoRefresh').checked;
        this.settings.refreshInterval = parseInt(document.getElementById('refreshInterval').value);

        localStorage.setItem('familyWealthSettings', JSON.stringify(this.settings));
        this.showToast('设置已保存', 'success');
    }

    // Toast通知
    showToast(message, type = 'info') {
        const toastContainer = document.querySelector('.toast-container');
        const toast = document.createElement('div');
        toast.className = `toast show`;
        toast.style.backgroundColor = this.getToastColor(type);
        toast.innerHTML = `
            <div class="toast-body text-white">
                <i class="fas fa-${this.getToastIcon(type)} me-2"></i>
                ${message}
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        // 3秒后自动移除
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    getToastColor(type) {
        const colors = {
            'success': '#28a745',
            'danger': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8'
        };
        return colors[type] || colors.info;
    }

    getToastIcon(type) {
        const icons = {
            'success': 'check-circle',
            'danger': 'exclamation-circle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle'
        };
        return icons[type] || icons.info;
    }
}

// 初始化应用
const app = new FamilyWealthApp();