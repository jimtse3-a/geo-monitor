@echo off
chcp 65001 > nul
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║         GEO AI 搜索引擎监测工具 - 演示版                    ║
echo ║         监测品牌在 AI 平台的可见率与关键词录用情况          ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

:MENU
echo 请选择操作：
echo.
echo  [1] 启动交互式 WEB 仪表盘（推荐）
echo  [2] 生成演示数据（7天）
echo  [3] 生成演示数据（30天）
echo  [4] 运行完整监测
echo  [5] 生成 HTML 报告
echo  [6] 查看帮助
echo  [0] 退出
echo.
set /p choice="请输入选项 (0-6): "

if "%choice%"=="1" goto DASHBOARD
if "%choice%"=="2" goto DEMO_7
if "%choice%"=="3" goto DEMO_30
if "%choice%"=="4" goto MONITOR
if "%choice%"=="5" goto REPORT
if "%choice%"=="6" goto HELP
if "%choice%"=="0" goto EXIT

echo.
echo 无效选项，请重新选择。
echo.
goto MENU

:DASHBOARD
echo.
echo 正在启动交互式仪表盘...
start index.html
echo ✅ 已在浏览器中打开 index.html
echo.
pause
goto MENU

:DEMO_7
echo.
echo 正在生成 7 天演示数据...
python monitor.py --demo --days 7
echo.
pause
goto MENU

:DEMO_30
echo.
echo 正在生成 30 天演示数据...
python monitor.py --demo --days 30
echo.
pause
goto MENU

:MONITOR
echo.
echo 正在运行完整监测...
python monitor.py
echo.
pause
goto MENU

:REPORT
echo.
echo 正在生成报告...
python monitor.py --report
echo.
pause
goto MENU

:HELP
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                         使用帮助                            ║
echo ╠════════════════════════════════════════════════════════════╣
echo ║  1. WEB 仪表盘 - 可视化界面，支持多品牌/多平台监测          ║
echo ║  2. 命令行模式 - 适合自动化和批处理                          ║
echo ║                                                            ║
echo ║  命令行参数：                                              ║
echo ║    python monitor.py --platforms kimi doubao               ║
echo ║    python monitor.py --brands 印暨咖啡 星巴克               ║
echo ║    python monitor.py --demo --days 30                      ║
echo ║                                                            ║
echo ║  支持的平台：                                              ║
echo ║    kimi, doubao, qianwen, deepseek, wenxin, hunyuan, zhipu ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
pause
goto MENU

:EXIT
echo.
echo 感谢使用 GEO 监测工具！
echo.
exit /b 0
