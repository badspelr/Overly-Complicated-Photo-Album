# Nginx Setup Guide

This guide covers setting up Nginx as a reverse proxy for the Django Photo Album application in production.

> 🌍 **Setting up multiple domains?** See [Virtual Domains Setup Guide](VIRTUAL_DOMAINS_SETUP.md) for detailed instructions on configuring multiple websites or subdomains on one server.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Option 1: Nginx with Docker Compose](#option-1-nginx-with-docker-compose)
- [Option 2: System Nginx as Reverse Proxy](#option-2-system-nginx-as-reverse-proxy)
- [SSL/TLS Configuration](#ssltls-configuration)
- [Performance Optimization](#performance-optimization)
- [Troubleshooting](#troubleshooting)

## Prerequisites

- Docker and Docker Compose installed
- Domain name pointed to your server (for SSL)
- Photo Album application running (see [DOCKER.md](DOCKER.md))

> 📝 **Note:** This guide assumes a single domain setup. For multiple domains/subdomains on the same server, see the [Virtual Domains Setup Guide](VIRTUAL_DOMAINS_SETUP.md).

## Option 1: Nginx with Docker Compose

### 1. Create Nginx Configuration

Create `nginx/nginx.conf`:

```nginx
upstream photo_album {
    server web:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    client_max_body_size 500M;

    # Redirect to HTTPS (comment out if not using SSL)
    # return 301 https://$server_name$request_uri;

    location / {
        proxy_pass http://photo_album;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts for large file uploads
        proxy_connect_timeout 600;
        proxy_send_timeout 600;
        proxy_read_timeout 600;
        send_timeout 600;
    }

    location /static/ {
        alias /app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /app/media/;
        expires 7d;
        add_header Cache-Control "public";
        
        # Security headers for media files
        add_header X-Content-Type-Options "nosniff";
    }

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript 
               application/json application/javascript application/xml+rss 
               application/rss+xml font/truetype font/opentype 
               application/vnd.ms-fontobject image/svg+xml;
}
```

### 2. Update docker-compose.prod.yml

Add Nginx service to your `docker-compose.prod.yml`:

```yaml
services:
  nginx:
    image: nginx:alpine
    container_name: photo_album_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - static_data:/app/staticfiles:ro
      - media_data:/app/media:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro  # For SSL certificates
    depends_on:
      - web
    networks:
      - photo_album_network

  web:
    # ... existing web service config ...
    # Remove the ports mapping since Nginx will handle it
    # ports:
    #   - "8000:8000"
    expose:
      - "8000"
```

### 3. Deploy with Nginx

```bash
# Start all services including Nginx
docker-compose -f docker-compose.prod.yml up -d

# Check Nginx logs
docker-compose -f docker-compose.prod.yml logs nginx

# Test Nginx configuration
docker-compose -f docker-compose.prod.yml exec nginx nginx -t
```

## Option 2: System Nginx as Reverse Proxy

Use this option if you want Nginx installed directly on your host system.

> 💡 **Tip:** If you're setting up multiple websites on the same server (e.g., photos.example.com + blog.example.com), see the [Virtual Domains Setup Guide](VIRTUAL_DOMAINS_SETUP.md) for detailed instructions on configuring virtual hosts.

### 1. Install Nginx

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install nginx
```

**CentOS/RHEL:**
```bash
sudo yum install epel-release
sudo yum install nginx
```

### 2. Create Nginx Site Configuration

Create `/etc/nginx/sites-available/photo-album`:

```nginx
upstream photo_album {
    server localhost:8000;
    keepalive 32;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Max upload size (adjust based on your needs)
    client_max_body_size 500M;
    client_body_buffer_size 128k;
    
    # Logging
    access_log /var/log/nginx/photo-album-access.log;
    error_log /var/log/nginx/photo-album-error.log;

    location / {
        proxy_pass http://photo_album;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts for large uploads
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
    }

    location /static/ {
        alias /home/dniel/django/photo_album/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    location /media/ {
        alias /home/dniel/django/photo_album/media/;
        expires 7d;
        add_header Cache-Control "public";
        
        # Security for media files
        add_header X-Content-Type-Options "nosniff";
        add_header X-Frame-Options "SAMEORIGIN";
    }

    # Security headers
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript 
               application/json application/javascript application/xml+rss 
               application/rss+xml font/truetype font/opentype 
               application/vnd.ms-fontobject image/svg+xml;
}
```

### 3. Enable the Site

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/photo-album /etc/nginx/sites-enabled/

# Remove default site (optional)
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx

# Enable Nginx to start on boot
sudo systemctl enable nginx
```

### 4. Update ALLOWED_HOSTS

In your `.env` file:

```bash
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,localhost,127.0.0.1
```

Then restart your containers:

```bash
docker-compose restart web
```

## SSL/TLS Configuration

### Using Let's Encrypt (Recommended)

#### 1. Install Certbot

**Ubuntu/Debian:**
```bash
sudo apt install certbot python3-certbot-nginx
```

**CentOS/RHEL:**
```bash
sudo yum install certbot python3-certbot-nginx
```

#### 2. Obtain Certificate

```bash
# Make sure port 80 is accessible
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

Certbot will automatically update your Nginx configuration with SSL settings.

#### 3. Auto-renewal

```bash
# Test renewal
sudo certbot renew --dry-run

# Certbot will automatically set up a cron job for renewal
```

### Manual SSL Configuration

If you have your own certificates, update your Nginx config:

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    
    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # HSTS (optional but recommended)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # ... rest of your location blocks ...
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

## Performance Optimization

### 1. Enable Caching

Add to your Nginx configuration:

```nginx
# Define cache zones
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=photo_cache:10m 
                 max_size=1g inactive=60m use_temp_path=off;

server {
    # ... existing config ...
    
    location / {
        proxy_pass http://photo_album;
        
        # Enable caching
        proxy_cache photo_cache;
        proxy_cache_valid 200 10m;
        proxy_cache_valid 404 1m;
        proxy_cache_bypass $http_cache_control;
        add_header X-Cache-Status $upstream_cache_status;
        
        # ... rest of proxy settings ...
    }
}
```

### 2. Connection Optimization

```nginx
http {
    # Keep connections alive
    keepalive_timeout 65;
    keepalive_requests 100;
    
    # Buffer sizes
    client_body_buffer_size 128k;
    client_header_buffer_size 1k;
    large_client_header_buffers 4 16k;
    
    # File upload optimization
    client_max_body_size 500M;
    client_body_timeout 600s;
}
```

### 3. Static File Optimization

```nginx
location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
    access_log off;
    
    # Enable sendfile for better performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
}
```

## Monitoring and Logs

### View Nginx Logs

**System Nginx:**
```bash
# Access logs
sudo tail -f /var/log/nginx/photo-album-access.log

# Error logs
sudo tail -f /var/log/nginx/photo-album-error.log

# Search for errors
sudo grep "error" /var/log/nginx/photo-album-error.log
```

**Docker Nginx:**
```bash
# Real-time logs
docker-compose -f docker-compose.prod.yml logs -f nginx

# Last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100 nginx
```

### Log Rotation

For system Nginx, log rotation is usually configured automatically. Verify:

```bash
cat /etc/logrotate.d/nginx
```

## Troubleshooting

### Issue: 502 Bad Gateway

**Cause:** Nginx can't connect to the Django application.

**Solutions:**
```bash
# Check if web container is running
docker-compose ps

# Check web container logs
docker-compose logs web

# Verify port 8000 is exposed
docker-compose exec web netstat -tlnp | grep 8000

# Test connection from host
curl http://localhost:8000
```

### Issue: 413 Request Entity Too Large

**Cause:** File upload exceeds `client_max_body_size`.

**Solution:** Increase the limit in your Nginx config:
```nginx
client_max_body_size 500M;  # Or higher
```

Then reload Nginx:
```bash
sudo systemctl reload nginx
# or
docker-compose restart nginx
```

### Issue: Static Files Not Loading

**Cause:** Incorrect static file path or permissions.

**Solutions:**
```bash
# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Check permissions (for system Nginx)
sudo chown -R www-data:www-data /home/dniel/django/photo_album/staticfiles/
sudo chmod -R 755 /home/dniel/django/photo_album/staticfiles/

# Verify path in Nginx config matches actual location
ls -la /home/dniel/django/photo_album/staticfiles/
```

### Issue: SSL Certificate Errors

**Solutions:**
```bash
# Test SSL certificate
sudo certbot certificates

# Renew certificate manually
sudo certbot renew

# Check certificate expiration
echo | openssl s_client -servername yourdomain.com -connect yourdomain.com:443 2>/dev/null | openssl x509 -noout -dates
```

### Issue: Timeout on Large Uploads

**Solution:** Increase timeout values:
```nginx
# In Nginx config
proxy_connect_timeout 600;
proxy_send_timeout 600;
proxy_read_timeout 600;
send_timeout 600;

# Also update in docker-compose.yml web service
environment:
  - GUNICORN_TIMEOUT=600
```

### Testing Nginx Configuration

```bash
# Test system Nginx config
sudo nginx -t

# Test Docker Nginx config
docker-compose exec nginx nginx -t

# Check which config file is being used
sudo nginx -T | grep "configuration file"

# Verify upstream is reachable
curl -v http://localhost:8000
```

## Security Best Practices

### 1. Limit Request Methods

```nginx
if ($request_method !~ ^(GET|HEAD|POST|PUT|DELETE|OPTIONS)$) {
    return 405;
}
```

### 2. Rate Limiting

```nginx
# Define rate limit zones
limit_req_zone $binary_remote_addr zone=upload_limit:10m rate=10r/m;
limit_req_zone $binary_remote_addr zone=general_limit:10m rate=100r/s;

server {
    # Apply to upload endpoints
    location /upload/ {
        limit_req zone=upload_limit burst=5;
        # ... rest of config ...
    }
    
    # Apply to general requests
    location / {
        limit_req zone=general_limit burst=50;
        # ... rest of config ...
    }
}
```

### 3. Hide Nginx Version

```nginx
http {
    server_tokens off;
}
```

### 4. Prevent Hotlinking

```nginx
location ~* \.(jpg|jpeg|png|gif)$ {
    valid_referers none blocked yourdomain.com *.yourdomain.com;
    if ($invalid_referer) {
        return 403;
    }
}
```

## Health Check Endpoint

Create a health check endpoint in Nginx:

```nginx
location /health {
    access_log off;
    return 200 "healthy\n";
    add_header Content-Type text/plain;
}
```

## Complete Example Configuration

See [nginx/nginx.conf.example](../../nginx/nginx.conf.example) for a complete, production-ready configuration file.

## Additional Resources

- [Official Nginx Documentation](https://nginx.org/en/docs/)
- [Certbot Documentation](https://certbot.eff.org/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Nginx Reverse Proxy Guide](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)
- **[Virtual Domains Setup Guide](VIRTUAL_DOMAINS_SETUP.md)** - Multiple domains/subdomains on one server

## Virtual Domains / Multiple Sites

If you need to run multiple websites on the same server (e.g., `photos.example.com`, `blog.example.com`, `www.example.com`), see our comprehensive **[Virtual Domains Setup Guide](VIRTUAL_DOMAINS_SETUP.md)**.

This guide covers:
- Setting up multiple domains on one server
- Subdomain configuration (photos.example.com)
- DNS configuration for virtual hosts
- Nginx virtual host setup
- SSL certificates for multiple domains
- Complete step-by-step examples

## Next Steps

After setting up Nginx:
1. Configure SSL/TLS certificates
2. **Set up virtual domains** (if hosting multiple sites) - see [VIRTUAL_DOMAINS_SETUP.md](VIRTUAL_DOMAINS_SETUP.md)
3. Set up monitoring (see [MONITORING.md](MONITORING.md))
4. Configure backups (see [BACKUP_STRATEGY.md](BACKUP_STRATEGY.md))
5. Review security settings (see [SECURITY_HARDENING.md](SECURITY_HARDENING.md))
