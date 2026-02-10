const express = require('express');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// 中间件配置
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '../sandbox-system/dashboard')));

// 基础路由
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '../sandbox-system/dashboard/improved_dashboard.html'));
});

// API路由示例
app.get('/api/health', (req, res) => {
    res.json({ 
        status: 'ok', 
        timestamp: new Date().toISOString(),
        service: 'Family Wealth Management System'
    });
});

// 启动服务器
app.listen(PORT, () => {
    console.log(`🚀 家族财富管理系统服务器启动`);
    console.log(`📡 监听端口: ${PORT}`);
    console.log(`🏠 访问地址: http://localhost:${PORT}`);
});