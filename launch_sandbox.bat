@echo off
echo ========================================
echo 家族财富沙盘系统启动器
echo ========================================
echo.

cd /d "%~dp0software-modules\sandbox-system"

echo 🚀 启动沙盘系统...
echo.

echo 选项:
echo 1. 运行功能测试
echo 2. 启动主程序
echo 3. 启动Web仪表板
echo 4. 查看数据库结构
echo 5. 退出
echo.

choice /c 12345 /m "请选择操作"

if errorlevel 5 goto :exit
if errorlevel 4 goto :check_db
if errorlevel 3 goto :start_web
if errorlevel 2 goto :start_main
if errorlevel 1 goto :run_test

:run_test
echo.
echo 🧪 运行功能测试...
python test_sandbox.py
goto :menu

:start_main
echo.
echo 🚀 启动主程序...
python main.py
goto :menu

:start_web
echo.
echo 🌐 启动Web仪表板...
cd dashboard
start http://localhost:8080/financial_analysis_dashboard.html
python -m http.server 8080
goto :menu

:check_db
echo.
echo 📊 查看数据库结构...
python check_db_structure.py
goto :menu

:menu
echo.
echo 按任意键返回菜单...
pause >nul
cls
goto :start

:exit
echo.
echo 👋 再见！
exit /b 0