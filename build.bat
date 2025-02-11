@echo off
chcp 65001
cls

echo 检查并安装必要组件...
python -m pip install pyinstaller
if errorlevel 1 (
    echo 安装 PyInstaller 失败！
    echo 请确保已安装 Python 并添加到系统环境变量
    pause
    exit /b
)
echo PyInstaller 安装完成
echo.

echo 开始打包程序...
echo 当前目录：%CD%
echo.

echo 检查必要文件...
if not exist code_compare_gui.py (
    echo 错误：找不到 code_compare_gui.py 文件
    pause
    exit /b
)
if not exist code_compare.spec (
    echo 错误：找不到 code_compare.spec 文件
    pause
    exit /b
)
if not exist icon.ico (
    echo 警告：找不到 icon.ico 文件，将使用默认图标
)
echo 文件检查完成
echo.

echo 清理旧的构建文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo.

echo 正在打包程序...
python -m PyInstaller --clean code_compare.spec
if errorlevel 1 (
    echo 打包失败！
    pause
    exit /b
)

echo.
echo 打包完成！
echo 程序文件位于 dist 目录中
echo.
pause 