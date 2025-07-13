# 构建和部署脚本

param(
    [string]$Environment = "local",
    [string]$ImageTag = "latest"
)

Write-Host "开始构建代理服务管理平台..." -ForegroundColor Green
Write-Host "环境: $Environment" -ForegroundColor Yellow
Write-Host "镜像标签: $ImageTag" -ForegroundColor Yellow

switch ($Environment) {
    "local" {
        Write-Host "本地 Docker 部署..." -ForegroundColor Cyan
        
        # 构建镜像
        Write-Host "构建 Docker 镜像..." -ForegroundColor Yellow
        docker build -t proxy-web:$ImageTag .
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "镜像构建成功!" -ForegroundColor Green
            
            # 启动服务
            Write-Host "启动服务..." -ForegroundColor Yellow
            docker-compose up -d
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "服务启动成功!" -ForegroundColor Green
                Write-Host "Web 界面: http://localhost:5000" -ForegroundColor Cyan
                Write-Host "SOCKS5 代理: localhost:8888" -ForegroundColor Cyan
                
                # 显示服务状态
                Write-Host "`n服务状态:" -ForegroundColor Yellow
                docker-compose ps
            } else {
                Write-Host "服务启动失败!" -ForegroundColor Red
            }
        } else {
            Write-Host "镜像构建失败!" -ForegroundColor Red
        }
    }
    
    "eks" {
        Write-Host "EKS 集群部署..." -ForegroundColor Cyan
        
        # 检查 kubectl 是否可用
        if (!(Get-Command kubectl -ErrorAction SilentlyContinue)) {
            Write-Host "错误: 未找到 kubectl。请先安装并配置 kubectl。" -ForegroundColor Red
            exit 1
        }
        
        # 检查集群连接
        Write-Host "检查 Kubernetes 集群连接..." -ForegroundColor Yellow
        kubectl cluster-info
        
        if ($LASTEXITCODE -eq 0) {
            # 构建并推送镜像到 ECR
            Write-Host "构建镜像..." -ForegroundColor Yellow
            docker build -t proxy-web:$ImageTag .
            
            # 这里需要根据实际的 ECR 仓库地址进行配置
            $ECR_REPO = "your-account.dkr.ecr.region.amazonaws.com/proxy-web"
            
            Write-Host "标记镜像..." -ForegroundColor Yellow
            docker tag proxy-web:$ImageTag $ECR_REPO:$ImageTag
            
            Write-Host "推送镜像到 ECR..." -ForegroundColor Yellow
            # docker push $ECR_REPO:$ImageTag
            
            # 更新 Kubernetes 部署文件中的镜像标签
            Write-Host "更新 Kubernetes 配置..." -ForegroundColor Yellow
            (Get-Content k8s\deployment.yaml) -replace 'proxy-web:latest', "$ECR_REPO:$ImageTag" | Set-Content k8s\deployment.yaml
            
            # 部署到 Kubernetes
            Write-Host "部署到 Kubernetes 集群..." -ForegroundColor Yellow
            kubectl apply -f k8s\deployment.yaml
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "部署成功!" -ForegroundColor Green
                
                Write-Host "检查部署状态..." -ForegroundColor Yellow
                kubectl get pods -n proxy-service
                kubectl get svc -n proxy-service
                
                Write-Host "`n获取服务访问地址..." -ForegroundColor Yellow
                kubectl get ingress -n proxy-service
            } else {
                Write-Host "部署失败!" -ForegroundColor Red
            }
        } else {
            Write-Host "无法连接到 Kubernetes 集群!" -ForegroundColor Red
        }
    }
    
    default {
        Write-Host "不支持的环境: $Environment" -ForegroundColor Red
        Write-Host "支持的环境: local, eks" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host "`n部署完成!" -ForegroundColor Green
