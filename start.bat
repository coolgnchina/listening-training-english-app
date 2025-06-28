@echo off
chcp 65001
color 0B
echo 正在启动后端服务...
start "后端服务" /D ".\backend" python app.py

echo 正在启动前端服务...
start "前端服务" /D ".\frontend" cmd /k "npm run dev"

echo 正在打开浏览器...
timeout /t 5 > nul
start http://localhost:5173/

echo.
echo ▄████████████▄
echo ■■■ 服务启动完成 ■■■
echo ■ 前端访问: http://localhost:5173/
echo ■ 后端API: http://localhost:5000
echo ■■■■■■■■■■■■■■■■■■
echo 请保持终端窗口开启，按任意键退出...
pause > nul