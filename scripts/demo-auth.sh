#!/bin/bash

# BabelNet 用户认证功能演示脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
BACKEND_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:8080"
DEMO_USER="demouser_$(date +%s)"
DEMO_PASS="demopass123"

echo -e "${BLUE}=== BabelNet 用户认证功能演示 ===${NC}"
echo ""

# 检查后端服务
echo -e "${YELLOW}1. 检查后端服务状态...${NC}"
if curl -s "$BACKEND_URL/healthz" > /dev/null; then
    echo -e "${GREEN}✓ 后端服务正常运行${NC}"
else
    echo -e "${RED}✗ 后端服务未运行，请先启动后端服务${NC}"
    echo "   cd backend && uvicorn main:app --reload"
    exit 1
fi

# 检查前端服务
echo -e "${YELLOW}2. 检查前端服务状态...${NC}"
if curl -s "$FRONTEND_URL" > /dev/null; then
    echo -e "${GREEN}✓ 前端服务正常运行${NC}"
else
    echo -e "${RED}✗ 前端服务未运行，请先启动前端服务${NC}"
    echo "   cd frontend && npm run serve"
    exit 1
fi

echo ""
echo -e "${BLUE}=== 功能演示 ===${NC}"

# 演示1: 用户注册
echo -e "${YELLOW}3. 演示用户注册...${NC}"
echo "   用户名: $DEMO_USER"
echo "   密码: $DEMO_PASS"

REGISTER_RESPONSE=$(curl -s -X POST "$BACKEND_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$DEMO_USER\",\"password\":\"$DEMO_PASS\"}")

if echo "$REGISTER_RESPONSE" | grep -q "Register success"; then
    echo -e "${GREEN}✓ 注册成功${NC}"
else
    echo -e "${RED}✗ 注册失败: $REGISTER_RESPONSE${NC}"
    exit 1
fi

# 演示2: 用户登录
echo -e "${YELLOW}4. 演示用户登录...${NC}"

LOGIN_RESPONSE=$(curl -s -X POST "$BACKEND_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$DEMO_USER\",\"password\":\"$DEMO_PASS\"}")

if echo "$LOGIN_RESPONSE" | grep -q "Login success"; then
    echo -e "${GREEN}✓ 登录成功${NC}"
    USERNAME=$(echo "$LOGIN_RESPONSE" | grep -o '"username":"[^"]*"' | cut -d'"' -f4)
    echo "   欢迎用户: $USERNAME"
else
    echo -e "${RED}✗ 登录失败: $LOGIN_RESPONSE${NC}"
    exit 1
fi

# 演示3: 重复注册（应该失败）
echo -e "${YELLOW}5. 演示重复注册（应该失败）...${NC}"

DUPLICATE_RESPONSE=$(curl -s -X POST "$BACKEND_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$DEMO_USER\",\"password\":\"$DEMO_PASS\"}")

if echo "$DUPLICATE_RESPONSE" | grep -q "already exists"; then
    echo -e "${GREEN}✓ 重复注册被正确拒绝${NC}"
else
    echo -e "${YELLOW}⚠ 重复注册响应: $DUPLICATE_RESPONSE${NC}"
fi

# 演示4: 错误密码登录（应该失败）
echo -e "${YELLOW}6. 演示错误密码登录（应该失败）...${NC}"

WRONG_PASS_RESPONSE=$(curl -s -X POST "$BACKEND_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$DEMO_USER\",\"password\":\"wrongpass\"}")

if echo "$WRONG_PASS_RESPONSE" | grep -q "Invalid credentials"; then
    echo -e "${GREEN}✓ 错误密码被正确拒绝${NC}"
else
    echo -e "${YELLOW}⚠ 错误密码响应: $WRONG_PASS_RESPONSE${NC}"
fi

echo ""
echo -e "${BLUE}=== 前端功能演示 ===${NC}"
echo -e "${YELLOW}7. 前端功能演示...${NC}"
echo ""
echo -e "${GREEN}✓ 后端API测试完成！${NC}"
echo ""
echo -e "${BLUE}现在请在浏览器中测试前端功能：${NC}"
echo -e "${YELLOW}1. 访问注册页面: ${NC}$FRONTEND_URL/#/register"
echo -e "${YELLOW}2. 注册新用户（将自动登录并跳转到仪表板）${NC}"
echo -e "${YELLOW}3. 在仪表板右上角点击用户名，测试退出登录功能${NC}"
echo -e "${YELLOW}4. 访问登录页面: ${NC}$FRONTEND_URL/#/login"
echo -e "${YELLOW}5. 使用刚才注册的账户登录${NC}"
echo ""
echo -e "${BLUE}演示账户信息：${NC}"
echo -e "   用户名: ${GREEN}$DEMO_USER${NC}"
echo -e "   密码: ${GREEN}$DEMO_PASS${NC}"
echo ""
echo -e "${BLUE}=== 演示完成 ===${NC}" 