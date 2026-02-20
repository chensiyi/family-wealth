@echo off
echo ========================================
echo 家族财富管理系统启动器
echo Family Wealth Management System Launcher
echo ========================================

echo.
echo 📁 当前软件模块结构:
echo software-modules/
echo ├── sandbox-system/        (沙盘系统)
echo │   ├── analysis-engine/   (分析引擎)
echo │   ├── dashboard/         (仪表板)
echo │   ├── simulation-core/   (模拟核心)
echo │   ├── utils/             (工具组件)
echo │   └── storage/           (数据存储)
echo └── data-collector/        (信息收集器)
echo     ├── data-sources/      (数据源)
echo     ├── processors/        (处理器)
echo     ├── storage/           (数据存储)
echo     └── quality-control/   (质量控制)

echo.
echo 🚀 可用系统:

echo.
echo 1. 沙盘系统 (Sandbox System)
echo    功能: 数据分析、仪表板展示、模拟计算
echo    启动: cd software-modules/sandbox-system && python main.py

echo.
echo 2. 信息收集器 (Data Collector)  
echo    功能: 数据采集、存储管理、质量控制
echo    启动: cd software-modules/data-collector && python main.py

echo.
echo 3. 独立仪表板
echo    financial_analysis_dashboard.html - 基础仪表板
echo    improved_dashboard.html - 改进版仪表板
echo    sandbox_dashboard.html - 沙盘仪表板

echo.
echo 🛠️  开发工具:
echo    lightweight_data_generator.py - 轻量级数据生成器
echo    enhanced_data_generator.py - 增强数据生成器
echo    database_accessor.py - 数据库访问器
echo    sandbox_observer.py - 系统观察器

echo.
echo 📊 数据库文件:
echo    family_wealth_professional.db - 专业金融数据库
echo    sandbox_data.db - 沙盘系统数据库

echo.
echo 💡 使用建议:
echo    1. 先启动信息收集器初始化数据
echo    2. 再启动沙盘系统进行分析
echo    3. 通过仪表板查看实时数据

echo.
pause