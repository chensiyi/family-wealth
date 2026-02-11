const express = require('express');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// 中间件配置
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// API路由
app.get('/api/portfolio', (req, res) => {
    // 返回投资组合数据
    res.json({
        cash: 1000000,
        positions: [
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
            }
        ],
        totalValue: 1105000,
        unrealizedPnl: 3008,
        positionCount: 2
    });
});

app.get('/api/news', (req, res) => {
    // 返回新闻数据
    res.json({
        news: [
            {
                id: 1,
                title: '英伟达发布新一代AI芯片',
                summary: '科技行业迎来重大技术突破',
                source: '财经网',
                publishDate: new Date().toISOString(),
                sector: 'technology',
                region: 'global',
                impactScore: 0.85
            }
        ]
    });
});

app.post('/api/trade/buy', (req, res) => {
    // 处理买入交易
    const { symbol, quantity, price, fee, description } = req.body;
    res.json({
        success: true,
        message: `成功买入 ${quantity} 股 ${symbol}`,
        transactionId: Date.now()
    });
});

app.post('/api/trade/sell', (req, res) => {
    // 处理卖出交易
    const { symbol, quantity, price, fee, description } = req.body;
    res.json({
        success: true,
        message: `成功卖出 ${quantity} 股 ${symbol}`,
        transactionId: Date.now(),
        realizedPnl: quantity * (price - 850) // 示例计算
    });
});

// 基础路由
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public/index.html'));
});

app.get('/professional', (req, res) => {
    res.sendFile(path.join(__dirname, 'public/professional_trading.html'));
});

app.get('/trading-hall', (req, res) => {
    res.sendFile(path.join(__dirname, 'public/realtime_trading_hall.html'));
});

app.get('/demo', (req, res) => {
    res.sendFile(path.join(__dirname, 'public/demo.html'));
});

// 启动服务器
app.listen(PORT, () => {
    console.log(`🚀 家族财富管理系统服务器启动`);
    console.log(`📡 监听端口: ${PORT}`);
    console.log(`🏠 访问地址: http://localhost:${PORT}`);
});