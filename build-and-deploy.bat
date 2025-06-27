@echo off
echo ====================================
echo Vue.js SPA 构建和部署脚本
echo ====================================
echo.

echo [1/4] 检查Node.js环境...
node --version
if %errorlevel% neq 0 (
    echo 错误: 未找到Node.js，请先安装Node.js
    pause
    exit /b 1
)

echo [2/4] 进入前端目录并安装依赖...
cd frontend
if not exist node_modules (
    echo 安装依赖包...
    npm install
    if %errorlevel% neq 0 (
        echo 错误: 依赖安装失败
        pause
        exit /b 1
    )
)

echo [3/4] 构建生产版本...
npm run build
if %errorlevel% neq 0 (
    echo 错误: 构建失败
    pause
    exit /b 1
)

echo [4/4] 构建完成！
echo.
echo ====================================
echo 构建成功！
echo ====================================
echo.
echo 接下来的步骤：
echo 1. 将 frontend/dist/ 目录下的所有文件上传到服务器
echo 2. 应用 nginx.conf 中的配置到宝塔面板
echo 3. 确保后端Python服务正在运行
echo 4. 测试 https://englishpod666.icu/login 是否正常
echo.
echo 详细部署说明请查看: SPA_DEPLOYMENT_GUIDE.md
echo.
pause