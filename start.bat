@echo off
chcp 65001 >nul
title oapp_limit
cd /d "%~dp0"

echo.
echo  ============================================
echo   oapp_limit  -  ระบบจำกัดนัดคลินิก
echo  ============================================
echo.

:: ติดตั้ง dependencies ถ้ายังไม่มี
if not exist "node_modules" (
    echo  กำลังติดตั้ง dependencies...
    npm install
)

:: เปิด browser หลัง 2 วินาที
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:3300"

:: รัน server
echo  Server: http://localhost:3300
echo  กด Ctrl+C เพื่อหยุด
echo.
node server.js

pause
