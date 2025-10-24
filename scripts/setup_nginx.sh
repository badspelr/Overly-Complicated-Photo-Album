#!/bin/bash
# Quick setup script for Nginx with Let's Encrypt SSL

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Photo Album - Nginx Setup Script${NC}"
echo "======================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root (sudo)${NC}"
    exit 1
fi

# Get domain name
read -p "Enter your domain name (e.g., example.com): " DOMAIN
if [ -z "$DOMAIN" ]; then
    echo -e "${RED}Domain name is required${NC}"
    exit 1
fi

# Get email for Let's Encrypt
read -p "Enter your email for Let's Encrypt: " EMAIL
if [ -z "$EMAIL" ]; then
    echo -e "${RED}Email is required${NC}"
    exit 1
fi

# Ask about www subdomain
read -p "Also configure www.$DOMAIN? (y/n): " SETUP_WWW
if [ "$SETUP_WWW" = "y" ]; then
    DOMAIN_LIST="$DOMAIN,www.$DOMAIN"
else
    DOMAIN_LIST="$DOMAIN"
fi

echo ""
echo -e "${YELLOW}Configuration:${NC}"
echo "Domain: $DOMAIN_LIST"
echo "Email: $EMAIL"
echo ""
read -p "Continue? (y/n): " CONFIRM
if [ "$CONFIRM" != "y" ]; then
    echo "Aborted."
    exit 0
fi

# Create necessary directories
echo -e "${GREEN}Creating directories...${NC}"
mkdir -p nginx/ssl
mkdir -p nginx/certbot
mkdir -p logs/nginx

# Copy example config
if [ ! -f "nginx/nginx.conf" ]; then
    echo -e "${GREEN}Creating Nginx configuration...${NC}"
    cp nginx/nginx.conf.example nginx/nginx.conf
    
    # Update domain in config
    sed -i "s/yourdomain.com/$DOMAIN/g" nginx/nginx.conf
    
    echo -e "${YELLOW}Please review nginx/nginx.conf and adjust settings as needed${NC}"
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Start services without SSL first
echo -e "${GREEN}Starting services...${NC}"
docker-compose -f docker-compose.nginx.yml up -d

# Wait for services to be healthy
echo -e "${YELLOW}Waiting for services to be healthy...${NC}"
sleep 10

# Obtain SSL certificate
echo -e "${GREEN}Obtaining SSL certificate from Let's Encrypt...${NC}"
docker-compose -f docker-compose.nginx.yml run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN_LIST

if [ $? -eq 0 ]; then
    echo -e "${GREEN}SSL certificate obtained successfully!${NC}"
    
    # Update Nginx config to enable SSL
    echo -e "${GREEN}Enabling SSL in Nginx configuration...${NC}"
    sed -i 's/# return 301 https/return 301 https/g' nginx/nginx.conf
    
    # Reload Nginx
    docker-compose -f docker-compose.nginx.yml exec nginx nginx -s reload
    
    echo ""
    echo -e "${GREEN}✓ Setup complete!${NC}"
    echo ""
    echo "Your Photo Album is now accessible at:"
    echo -e "${GREEN}https://$DOMAIN${NC}"
    echo ""
    echo "SSL certificate will auto-renew via the certbot container."
else
    echo -e "${RED}Failed to obtain SSL certificate${NC}"
    echo "Your site is accessible at: http://$DOMAIN"
    echo "You can try obtaining the certificate manually later."
fi

# Show status
echo ""
echo -e "${GREEN}Container Status:${NC}"
docker-compose -f docker-compose.nginx.yml ps

echo ""
echo -e "${YELLOW}Useful commands:${NC}"
echo "  View logs:       docker-compose -f docker-compose.nginx.yml logs -f"
echo "  Restart Nginx:   docker-compose -f docker-compose.nginx.yml restart nginx"
echo "  Check cert:      docker-compose -f docker-compose.nginx.yml exec certbot certbot certificates"
echo "  Renew cert:      docker-compose -f docker-compose.nginx.yml exec certbot certbot renew"
