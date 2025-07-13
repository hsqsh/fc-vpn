# 停止所有服务

Write-Host "正在停止代理服务管理平台..." -ForegroundColor Yellow

# 停止 Docker Compose 服务
if (Test-Path "docker-compose.yml") {
    Write-Host "停止 Docker Compose 服务..." -ForegroundColor Yellow
    docker-compose down
}

# 停止可能运行的 Python 进程
Write-Host "停止 Python 进程..." -ForegroundColor Yellow
Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*venv*" } | Stop-Process -Force

# 停止可能运行的 Node.js 进程
Write-Host "停止 Node.js 进程..." -ForegroundColor Yellow
Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*vite*" } | Stop-Process -Force

# 清理端口占用
Write-Host "检查端口占用..." -ForegroundColor Yellow
$ports = @(3000, 5000, 8888)
foreach ($port in $ports) {
    $process = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($process) {
        $pid = $process.OwningProcess
        Write-Host "停止占用端口 $port 的进程 (PID: $pid)..." -ForegroundColor Yellow
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "所有服务已停止!" -ForegroundColor Green
