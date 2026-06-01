#Requires -Version 5.1
Set-Location $PSScriptRoot
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Write-Step($msg) { Write-Host "`n  $msg" -ForegroundColor Cyan }
function Write-OK($msg)   { Write-Host "  [OK] $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "  [..] $msg" -ForegroundColor Yellow }
function Write-Fail($msg) { Write-Host "  [!!] $msg" -ForegroundColor Red }

Write-Host ""
Write-Host "  ============================================" -ForegroundColor DarkBlue
Write-Host "   oapp_limit  -  ระบบจำกัดนัดคลินิก" -ForegroundColor White
Write-Host "  ============================================" -ForegroundColor DarkBlue

# ── 1. หา Python ─────────────────────────────────────────────────────────
Write-Step "ตรวจสอบ Python..."

function Find-PythonExe {
    # ลองจาก PATH ก่อน
    foreach ($cmd in @("python", "python3")) {
        $found = Get-Command $cmd -ErrorAction SilentlyContinue
        if ($found) {
            $v = & $found.Source --version 2>&1
            if ($v -match "Python 3") { return $found.Source }
        }
    }
    # ลองตาม path ที่ติดตั้งทั่วไป
    $candidates = @(
        "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
        "C:\Python313\python.exe",
        "C:\Python312\python.exe",
        "C:\Program Files\Python313\python.exe",
        "C:\Program Files\Python312\python.exe"
    )
    foreach ($p in $candidates) {
        if (Test-Path $p) { return $p }
    }
    return $null
}

$pythonExe = Find-PythonExe

# ── 2. ติดตั้ง Python ถ้ายังไม่มี ────────────────────────────────────────
if (-not $pythonExe) {
    Write-Warn "ไม่พบ Python — กำลังติดตั้งอัตโนมัติ..."

    # ลอง winget ก่อน (มีใน Windows 10/11)
    $wingetExe = Get-Command winget -ErrorAction SilentlyContinue
    $installed = $false

    if ($wingetExe) {
        Write-Warn "ใช้ winget ติดตั้ง Python 3.12..."
        try {
            & winget install Python.Python.3.12 `
                --silent `
                --accept-source-agreements `
                --accept-package-agreements `
                --scope user 2>&1 | Out-Null
            $installed = $true
        } catch { $installed = $false }
    }

    # Fallback: ดาวน์โหลด installer โดยตรง
    if (-not $installed) {
        $pyUrl  = "https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe"
        $pyInst = "$env:TEMP\python_installer.exe"
        Write-Warn "ดาวน์โหลด Python 3.12.7 (ประมาณ 25 MB)..."
        try {
            Invoke-WebRequest -Uri $pyUrl -OutFile $pyInst -UseBasicParsing
            Write-Warn "กำลังติดตั้ง Python (silent)..."
            Start-Process -FilePath $pyInst `
                -ArgumentList "/quiet InstallAllUsers=0 PrependPath=1 Include_test=0 SimpleInstall=1" `
                -Wait
            $installed = $true
        } catch {
            Write-Fail "ดาวน์โหลดล้มเหลว: $_"
        }
    }

    # รีเฟรช PATH
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" +
                [System.Environment]::GetEnvironmentVariable("PATH","User")

    $pythonExe = Find-PythonExe
}

if (-not $pythonExe) {
    Write-Fail "ไม่สามารถติดตั้ง Python ได้ กรุณาติดตั้งเองจาก https://www.python.org/downloads/"
    Start-Process "https://www.python.org/downloads/"
    Read-Host "`n  กด Enter เพื่อปิด"
    exit 1
}

$pyVer = & $pythonExe --version 2>&1
Write-OK "พบ $pyVer  ($pythonExe)"

# ── 3. อัปเกรด pip ─────────────────────────────────────────────────────────
Write-Step "อัปเกรด pip..."
& $pythonExe -m pip install --upgrade pip --quiet
Write-OK "pip พร้อม"

# ── 4. ติดตั้ง requirements ───────────────────────────────────────────────
Write-Step "ติดตั้ง Flask + MySQL + PostgreSQL drivers..."
& $pythonExe -m pip install -r requirements.txt --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Fail "pip install ล้มเหลว"
    Read-Host "`n  กด Enter เพื่อปิด"
    exit 1
}
Write-OK "ติดตั้ง dependencies เรียบร้อย"

# ── 5. เปิด browser หลัง 2 วินาที ────────────────────────────────────────
Write-Step "เตรียมเปิด browser..."
Start-Job -ScriptBlock {
    Start-Sleep -Seconds 2
    Start-Process "http://localhost:3300"
} | Out-Null

# ── 6. รัน Flask ──────────────────────────────────────────────────────────
Write-Host ""
Write-Host "  ============================================" -ForegroundColor DarkGreen
Write-Host "   Server: http://localhost:3300" -ForegroundColor Green
Write-Host "   กด Ctrl+C เพื่อหยุด server" -ForegroundColor Gray
Write-Host "  ============================================" -ForegroundColor DarkGreen
Write-Host ""

& $pythonExe app.py
