# 项目状态检查脚本

Write-Host "=== 代理服务管理平台状态检查 ===" -ForegroundColor Green

# 检查文件结构
Write-Host "`n检查项目文件..." -ForegroundColor Yellow
$requiredFiles = @(
    "app.py",
    "requirements.txt",
    "Dockerfile",
    "docker-compose.yml",
    "frontend\package.json",
    "frontend\src\App.vue",
    "k8s\deployment.yaml"
)

$missingFiles = @()
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "✓ $file" -ForegroundColor Green
    } else {
        Write-Host "✗ $file" -ForegroundColor Red
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host "`n警告: 缺少 $($missingFiles.Count) 个必要文件" -ForegroundColor Red
}

# 检查虚拟环境
Write-Host "`n检查 Python 虚拟环境..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "✓ Python 虚拟环境已创建" -ForegroundColor Green
    
    # 检查已安装的包
    if (Test-Path "venv\Scripts\pip.exe") {
        $installedPackages = & ".\venv\Scripts\pip.exe" list --format=freeze 2>$null
        $requiredPackages = Get-Content requirements.txt
        
        Write-Host "检查 Python 依赖..." -ForegroundColor Cyan
        foreach ($package in $requiredPackages) {
            $packageName = $package.Split("==")[0]
            if ($installedPackages -match $packageName) {
                Write-Host "  ✓ $packageName" -ForegroundColor Green
            } else {
                Write-Host "  ✗ $packageName (未安装)" -ForegroundColor Red
            }
        }
    }
} else {
    Write-Host "✗ Python 虚拟环境未创建" -ForegroundColor Red
}

# 检查前端依赖
Write-Host "`n检查前端依赖..." -ForegroundColor Yellow
if (Test-Path "frontend\node_modules") {
    Write-Host "✓ 前端依赖已安装" -ForegroundColor Green
} else {
    Write-Host "✗ 前端依赖未安装" -ForegroundColor Red
}

# 检查端口占用
Write-Host "`n检查端口占用..." -ForegroundColor Yellow
$ports = @(
    @{Port=3000; Service="前端开发服务器"},
    @{Port=5000; Service="Flask API"},
    @{Port=8888; Service="SOCKS5 代理"}
)

foreach ($portInfo in $ports) {
    $port = $portInfo.Port
    $service = $portInfo.Service
    
    $connection = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    if ($connection) {
        $process = Get-Process -Id $connection.OwningProcess -ErrorAction SilentlyContinue
        Write-Host "⚠ 端口 $port ($service) 被占用 - 进程: $($process.ProcessName)" -ForegroundColor Yellow
    } else {
        Write-Host "✓ 端口 $port ($service) 可用" -ForegroundColor Green
    }
}

# 检查 Docker 状态 (如果已安装)
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "`n检查 Docker 状态..." -ForegroundColor Yellow
    try {
        $dockerInfo = docker info 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Docker 运行正常" -ForegroundColor Green
            
            # 检查镜像
            $images = docker images proxy-web --format "table {{.Repository}}:{{.Tag}}" 2>$null
            if ($images -and $images.Count -gt 1) {
                Write-Host "✓ proxy-web 镜像已构建" -ForegroundColor Green
            } else {
                Write-Host "○ proxy-web 镜像未构建" -ForegroundColor Yellow
            }
            
            # 检查容器状态
            $containers = docker ps --filter "name=vpn" --format "table {{.Names}}\t{{.Status}}" 2>$null
            if ($containers -and $containers.Count -gt 1) {
                Write-Host "容器状态:" -ForegroundColor Cyan
                Write-Host $containers -ForegroundColor White
            } else {
                Write-Host "○ 暂无运行中的容器" -ForegroundColor Yellow
            }
        } else {
            Write-Host "✗ Docker 未运行" -ForegroundColor Red
        }
    } catch {
        Write-Host "✗ Docker 检查失败" -ForegroundColor Red
    }
}

# 网络连接测试
Write-Host "`n网络连接测试..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -TimeoutSec 5 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ API 服务运行正常" -ForegroundColor Green
    } else {
        Write-Host "✗ API 服务响应异常" -ForegroundColor Red
    }
} catch {
    Write-Host "○ API 服务未运行" -ForegroundColor Yellow
}

try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ 前端服务运行正常" -ForegroundColor Green
    } else {
        Write-Host "✗ 前端服务响应异常" -ForegroundColor Red
    }
} catch {
    Write-Host "○ 前端服务未运行" -ForegroundColor Yellow
}

Write-Host "`n=== 状态检查完成 ===" -ForegroundColor Green

# 提供建议
Write-Host "`n建议操作:" -ForegroundColor Cyan
if (!(Test-Path "venv") -or !(Test-Path "frontend\node_modules")) {
    Write-Host "- 运行 './install.ps1' 安装依赖" -ForegroundColor White
}
Write-Host "- 运行 './start-dev.ps1' 启动开发环境" -ForegroundColor White
Write-Host "- 运行 './deploy.ps1 -Environment local' 进行 Docker 部署" -ForegroundColor White
Write-Host "- 运行 './status.ps1' 查看当前状态" -ForegroundColor White
