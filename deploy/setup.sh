#!/bin/bash
# 服务器初始化脚本 — psy_website
# 使用前确认：
#   1. 已将项目克隆/上传到 /opt/psy_website
#   2. 已复制 backend/.env.example -> backend/.env 并填写所有密钥
#   3. 以 root 或 sudo 权限运行此脚本
set -e

DEPLOY_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$DEPLOY_DIR")"
CONDA_DIR="/opt/miniconda3"
SERVICE_MODE="${1:-hiagent}"  # 参数: hiagent 或 ai

echo "=== [1/7] 安装系统依赖 ==="
apt-get update -qq
apt-get install -y -qq nginx postgresql postgresql-contrib nodejs npm

# ── pgvector 扩展（需从源码编译或包管理器安装）──────────────────────────────
if ! sudo -u postgres psql -c "SELECT 1 FROM pg_extension WHERE extname='vector'" 2>/dev/null | grep -q 1; then
    echo "  安装 pgvector..."
    apt-get install -y -qq postgresql-server-dev-all build-essential git
    PGVECTOR_TMP=$(mktemp -d)
    git clone --depth 1 https://github.com/pgvector/pgvector.git "$PGVECTOR_TMP"
    make -C "$PGVECTOR_TMP" && make -C "$PGVECTOR_TMP" install
    rm -rf "$PGVECTOR_TMP"
fi

echo "=== [2/7] 初始化 PostgreSQL 数据库 ==="
DB_NAME="psy_db"
DB_USER="psy_user"
DB_PASS=$(grep DATABASE_URL "$PROJECT_DIR/backend/.env" | sed 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/')

sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
sudo -u postgres psql -d "$DB_NAME" -c "CREATE EXTENSION IF NOT EXISTS vector;"
sudo -u postgres psql -d "$DB_NAME" -U postgres -f "$PROJECT_DIR/backend/ai_engine/knowledge_base/migration.sql"
echo "  数据库和表结构初始化完成"

echo "=== [3/7] 安装 / 更新 Conda 环境（仅 AI 模式需要）==="
if [ "$SERVICE_MODE" = "ai" ]; then
    if [ ! -f "$CONDA_DIR/bin/conda" ]; then
        echo "  下载 Miniconda..."
        curl -sSL https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o /tmp/miniconda.sh
        bash /tmp/miniconda.sh -b -p "$CONDA_DIR"
        rm /tmp/miniconda.sh
    fi
    "$CONDA_DIR/bin/conda" env create -f "$DEPLOY_DIR/environment.yml" --name psy_agent || \
        "$CONDA_DIR/bin/conda" env update -f "$DEPLOY_DIR/environment.yml" --name psy_agent

    # CPU 版 PyTorch（替换可能带有 CUDA 后缀的版本）
    "$CONDA_DIR/envs/psy_agent/bin/pip" install torch --index-url https://download.pytorch.org/whl/cpu --upgrade -q
    echo "  psy_agent conda 环境准备完成"
else
    echo "  HiAgent 模式 — 使用 Python venv"
    python3 -m venv "$PROJECT_DIR/.venv"
    "$PROJECT_DIR/.venv/bin/pip" install -q -r "$PROJECT_DIR/backend/requirements.txt"
fi

echo "=== [4/7] 构建前端 ==="
cd "$PROJECT_DIR/frontend"
npm ci --silent
npm run build
echo "  前端构建完成 -> frontend/dist/"

echo "=== [5/7] 配置 nginx ==="
cp "$DEPLOY_DIR/nginx.conf" /etc/nginx/sites-available/psy_website
ln -sf /etc/nginx/sites-available/psy_website /etc/nginx/sites-enabled/psy_website
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx
echo "  nginx 配置完成"

echo "=== [6/7] 安装 systemd 服务 ==="
chown -R www-data:www-data "$PROJECT_DIR"

if [ "$SERVICE_MODE" = "ai" ]; then
    SERVICE_FILE="psy-ai.service"
    SERVICE_NAME="psy-ai"
else
    SERVICE_FILE="psy-hiagent.service"
    SERVICE_NAME="psy-hiagent"
fi

cp "$DEPLOY_DIR/$SERVICE_FILE" "/etc/systemd/system/$SERVICE_NAME.service"
systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl restart "$SERVICE_NAME"
echo "  服务 $SERVICE_NAME 已启动"

echo "=== [7/7] 检查服务状态 ==="
systemctl --no-pager status "$SERVICE_NAME"
nginx -t

echo ""
echo "✓ 部署完成。访问 http://<服务器IP> 验证"
echo "  日志查看: journalctl -u $SERVICE_NAME -f"
