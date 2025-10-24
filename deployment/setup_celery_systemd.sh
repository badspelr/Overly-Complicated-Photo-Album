#!/bin/bash
# Photo Album Celery Setup Script
# This script helps set up Celery workers as systemd services

set -e  # Exit on error

echo "================================================"
echo "  Photo Album - Celery Systemd Setup Script"
echo "================================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
APP_DIR="/var/www/photo_album"
VENV_DIR="$APP_DIR/venv"
APP_USER="www-data"
APP_GROUP="www-data"
CONCURRENCY=2

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}ERROR: This script must be run as root (use sudo)${NC}"
    exit 1
fi

echo "Current Configuration:"
echo "  Application Directory: $APP_DIR"
echo "  Virtual Environment: $VENV_DIR"
echo "  User: $APP_USER"
echo "  Group: $APP_GROUP"
echo "  Worker Concurrency: $CONCURRENCY"
echo ""

read -p "Are these settings correct? (y/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    read -p "Enter application directory [$APP_DIR]: " INPUT_DIR
    APP_DIR=${INPUT_DIR:-$APP_DIR}
    
    read -p "Enter virtual environment directory [$VENV_DIR]: " INPUT_VENV
    VENV_DIR=${INPUT_VENV:-$VENV_DIR}
    
    read -p "Enter application user [$APP_USER]: " INPUT_USER
    APP_USER=${INPUT_USER:-$APP_USER}
    
    read -p "Enter application group [$APP_GROUP]: " INPUT_GROUP
    APP_GROUP=${INPUT_GROUP:-$APP_GROUP}
    
    read -p "Enter worker concurrency (1-8) [$CONCURRENCY]: " INPUT_CONCURRENCY
    CONCURRENCY=${INPUT_CONCURRENCY:-$CONCURRENCY}
fi

echo ""
echo -e "${GREEN}Step 1: Checking prerequisites...${NC}"

# Check if Redis is installed
if ! command -v redis-cli &> /dev/null; then
    echo -e "${YELLOW}Warning: Redis is not installed${NC}"
    read -p "Install Redis? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        apt update
        apt install -y redis-server
        systemctl start redis-server
        systemctl enable redis-server
        echo -e "${GREEN}✓ Redis installed and started${NC}"
    fi
else
    echo -e "${GREEN}✓ Redis is installed${NC}"
fi

# Check if Redis is running
if redis-cli ping &> /dev/null; then
    echo -e "${GREEN}✓ Redis is running${NC}"
else
    echo -e "${RED}✗ Redis is not running${NC}"
    echo "Starting Redis..."
    systemctl start redis-server
fi

# Check if application directory exists
if [ -d "$APP_DIR" ]; then
    echo -e "${GREEN}✓ Application directory exists${NC}"
else
    echo -e "${RED}✗ Application directory not found: $APP_DIR${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ -d "$VENV_DIR" ]; then
    echo -e "${GREEN}✓ Virtual environment exists${NC}"
else
    echo -e "${RED}✗ Virtual environment not found: $VENV_DIR${NC}"
    exit 1
fi

# Check if user exists
if id "$APP_USER" &>/dev/null; then
    echo -e "${GREEN}✓ User $APP_USER exists${NC}"
else
    echo -e "${RED}✗ User $APP_USER does not exist${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}Step 2: Creating required directories...${NC}"

# Create directories
mkdir -p /var/run/celery
mkdir -p /var/log/celery

# Set ownership
chown $APP_USER:$APP_GROUP /var/run/celery
chown $APP_USER:$APP_GROUP /var/log/celery

# Set permissions
chmod 755 /var/run/celery
chmod 755 /var/log/celery

echo -e "${GREEN}✓ Directories created${NC}"

echo ""
echo -e "${GREEN}Step 3: Customizing service files...${NC}"

# Create temporary service files with custom paths
WORKER_SERVICE="/tmp/photo-album-celery-worker.service"
BEAT_SERVICE="/tmp/photo-album-celery-beat.service"

# Worker service
cat > $WORKER_SERVICE << EOF
[Unit]
Description=Photo Album Celery Worker
After=network.target redis.service postgresql.service
Wants=redis.service

[Service]
Type=forking
User=$APP_USER
Group=$APP_GROUP
WorkingDirectory=$APP_DIR
Environment="PATH=$VENV_DIR/bin:/usr/local/bin:/usr/bin:/bin"
Environment="DJANGO_SETTINGS_MODULE=photo_album.settings"

ExecStart=$VENV_DIR/bin/celery \\
    --app=photo_album \\
    worker \\
    --loglevel=info \\
    --concurrency=$CONCURRENCY \\
    --max-tasks-per-child=50 \\
    --time-limit=300 \\
    --soft-time-limit=240 \\
    --pidfile=/var/run/celery/worker.pid \\
    --logfile=/var/log/celery/worker.log \\
    --detach

ExecStop=/bin/kill -TERM \$MAINPID

Restart=always
RestartSec=10
StartLimitInterval=200
StartLimitBurst=5

PrivateTmp=true
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
EOF

# Beat service
cat > $BEAT_SERVICE << EOF
[Unit]
Description=Photo Album Celery Beat Scheduler
After=network.target redis.service postgresql.service photo-album-celery-worker.service
Wants=redis.service
Requires=photo-album-celery-worker.service

[Service]
Type=simple
User=$APP_USER
Group=$APP_GROUP
WorkingDirectory=$APP_DIR
Environment="PATH=$VENV_DIR/bin:/usr/local/bin:/usr/bin:/bin"
Environment="DJANGO_SETTINGS_MODULE=photo_album.settings"

ExecStart=$VENV_DIR/bin/celery \\
    --app=photo_album \\
    beat \\
    --loglevel=info \\
    --pidfile=/var/run/celery/beat.pid \\
    --logfile=/var/log/celery/beat.log

ExecStop=/bin/kill -TERM \$MAINPID

Restart=always
RestartSec=10
StartLimitInterval=200
StartLimitBurst=5

PrivateTmp=true
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✓ Service files customized${NC}"

echo ""
echo -e "${GREEN}Step 4: Installing service files...${NC}"

# Copy service files
cp $WORKER_SERVICE /etc/systemd/system/photo-album-celery-worker.service
cp $BEAT_SERVICE /etc/systemd/system/photo-album-celery-beat.service

# Set permissions
chmod 644 /etc/systemd/system/photo-album-celery-worker.service
chmod 644 /etc/systemd/system/photo-album-celery-beat.service

# Reload systemd
systemctl daemon-reload

echo -e "${GREEN}✓ Service files installed${NC}"

echo ""
echo -e "${GREEN}Step 5: Enabling services...${NC}"

systemctl enable photo-album-celery-worker
systemctl enable photo-album-celery-beat

echo -e "${GREEN}✓ Services enabled (will start on boot)${NC}"

echo ""
echo -e "${GREEN}Step 6: Starting services...${NC}"

systemctl start photo-album-celery-worker
systemctl start photo-album-celery-beat

# Wait a moment for services to start
sleep 2

echo -e "${GREEN}✓ Services started${NC}"

echo ""
echo -e "${GREEN}Step 7: Verifying services...${NC}"

# Check worker status
if systemctl is-active --quiet photo-album-celery-worker; then
    echo -e "${GREEN}✓ Celery worker is running${NC}"
else
    echo -e "${RED}✗ Celery worker failed to start${NC}"
    echo "Check logs: sudo journalctl -u photo-album-celery-worker -n 50"
fi

# Check beat status
if systemctl is-active --quiet photo-album-celery-beat; then
    echo -e "${GREEN}✓ Celery beat is running${NC}"
else
    echo -e "${RED}✗ Celery beat failed to start${NC}"
    echo "Check logs: sudo journalctl -u photo-album-celery-beat -n 50"
fi

echo ""
echo "================================================"
echo -e "${GREEN}Setup Complete!${NC}"
echo "================================================"
echo ""
echo "Service Management Commands:"
echo "  Status:  sudo systemctl status photo-album-celery-worker"
echo "  Status:  sudo systemctl status photo-album-celery-beat"
echo "  Stop:    sudo systemctl stop photo-album-celery-worker"
echo "  Start:   sudo systemctl start photo-album-celery-worker"
echo "  Restart: sudo systemctl restart photo-album-celery-worker"
echo ""
echo "View Logs:"
echo "  sudo tail -f /var/log/celery/worker.log"
echo "  sudo tail -f /var/log/celery/beat.log"
echo ""
echo "Monitor Tasks:"
echo "  cd $APP_DIR"
echo "  source $VENV_DIR/bin/activate"
echo "  celery -A photo_album inspect active"
echo ""
echo "For detailed documentation, see:"
echo "  DEPLOYMENT_SYSTEMD.md"
echo "  CELERY_SETUP.md"
echo ""
