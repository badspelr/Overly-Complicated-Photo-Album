# Virtual Domains Setup Guide

This guide explains how to run the Django Photo Album application on a server with virtual domains (also called virtual hosts). This allows you to host multiple websites on a single server, each with its own domain name.

## Table of Contents
- [What Are Virtual Domains?](#what-are-virtual-domains)
- [Prerequisites](#prerequisites)
- [Setup Scenarios](#setup-scenarios)
- [Single Domain Setup](#single-domain-setup)
- [Multiple Domains Setup](#multiple-domains-setup)
- [Subdomain Setup](#subdomain-setup)
- [Complete Step-by-Step Example](#complete-step-by-step-example)
- [Troubleshooting](#troubleshooting)

## What Are Virtual Domains?

**Virtual domains** (or virtual hosts) allow you to run multiple websites on a single server, each with its own domain name. For example:

- `photos.example.com` → Photo Album app
- `blog.example.com` → Your blog
- `shop.example.com` → Your online store

All running on the same physical server, sharing the same IP address.

### Common Use Cases

1. **Single Application, One Domain**
   - `photos.mydomain.com` → Your photo album
   - Most common scenario

2. **Multiple Applications**
   - `photos.mydomain.com` → Photo album
   - `www.mydomain.com` → Main website
   - `api.mydomain.com` → API service

3. **Development vs Production**
   - `photos.example.com` → Production site
   - `dev.photos.example.com` → Development site
   - Both on same server

## Prerequisites

Before starting, ensure you have:

1. **A Server** (VPS, dedicated server, or cloud instance)
   - Ubuntu 20.04+ or similar Linux distribution
   - At least 2GB RAM (4GB+ recommended for AI features)
   - Docker and Docker Compose installed

2. **Domain Name(s)**
   - Registered domain (e.g., `example.com`)
   - Access to DNS management panel

3. **DNS Configuration**
   - A record pointing to your server's IP address
   - Time for DNS propagation (5 minutes to 48 hours)

4. **Server Access**
   - SSH access with sudo privileges
   - Firewall configured (ports 80, 443 open)

## Setup Scenarios

### Scenario 1: Single Domain

**Goal:** Run photo album at `photos.example.com`

**What you need:**
- One domain or subdomain
- One Nginx configuration
- One SSL certificate

**Best for:**
- Single application deployment
- Simple setup
- Most common scenario

### Scenario 2: Multiple Applications on Same Server

**Goal:** Run multiple apps on different domains:
- `photos.example.com` → Photo Album
- `www.example.com` → Main Website
- `blog.example.com` → Blog

**What you need:**
- Multiple domain names
- Separate Nginx config for each
- Separate SSL certificates
- Multiple Docker containers (optional)

**Best for:**
- Hosting multiple services
- Different applications on one server
- Resource optimization

### Scenario 3: www and non-www

**Goal:** Handle both:
- `photos.example.com` → Main site
- `www.photos.example.com` → Redirect to main

**What you need:**
- One Nginx config with redirect
- One SSL certificate (covers both)

**Best for:**
- Professional appearance
- SEO optimization
- User convenience

## Single Domain Setup

This is the most common scenario: one domain for your photo album.

### Step 1: Configure DNS

In your domain registrar's DNS panel (GoDaddy, Namecheap, Cloudflare, etc.):

```
Type: A
Name: photos (or @, or subdomain name)
Value: YOUR_SERVER_IP
TTL: 3600 (or Auto)
```

**Examples:**
- `photos.example.com` → Use "photos" as name
- `example.com` → Use "@" as name
- `album.photos.example.com` → Use "album.photos" as name

**Verify DNS propagation:**
```bash
# From your local machine
dig photos.example.com

# Or use online tool:
# https://www.whatsmydns.net/
```

### Step 2: Update .env File

On your server, edit `.env`:

```bash
cd /home/yourusername/photo_album
nano .env
```

Update these settings:

```bash
# Domain configuration
ALLOWED_HOSTS=photos.example.com,www.photos.example.com,localhost,127.0.0.1

# Site URL (for emails, links)
SITE_URL=https://photos.example.com

# If using HTTPS (recommended)
CSRF_TRUSTED_ORIGINS=https://photos.example.com,https://www.photos.example.com

# Email settings (optional but recommended)
DEFAULT_FROM_EMAIL=noreply@photos.example.com
SERVER_EMAIL=admin@photos.example.com
```

### Step 3: Configure Nginx

Create Nginx configuration:

```bash
sudo nano /etc/nginx/sites-available/photo-album
```

**Basic configuration (HTTP only - for testing):**

```nginx
server {
    listen 80;
    server_name photos.example.com www.photos.example.com;
    
    client_max_body_size 500M;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /home/yourusername/photo_album/staticfiles/;
        expires 30d;
    }
    
    location /media/ {
        alias /home/yourusername/photo_album/media/;
        expires 7d;
    }
}
```

**Enable the site:**

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/photo-album /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### Step 4: Start Docker Containers

```bash
cd /home/yourusername/photo_album

# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f web
```

### Step 5: Add SSL Certificate (Recommended)

Use Let's Encrypt for free SSL:

```bash
# Install Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Obtain certificate (automatic Nginx configuration)
sudo certbot --nginx -d photos.example.com -d www.photos.example.com

# Enter your email when prompted
# Agree to terms
# Choose whether to redirect HTTP to HTTPS (recommended: yes)

# Test auto-renewal
sudo certbot renew --dry-run
```

Certbot will automatically:
- Obtain SSL certificate
- Update Nginx configuration
- Set up auto-renewal (cron job)

### Step 6: Verify

Visit your site:
- `http://photos.example.com` (should redirect to HTTPS)
- `https://photos.example.com` (should work)
- `https://www.photos.example.com` (should work)

## Multiple Domains Setup

Running multiple applications on the same server.

### Architecture Example

```
Server (IP: 203.0.113.10)
├── photos.example.com:80,443 → Docker (port 8000) → Photo Album
├── blog.example.com:80,443 → Docker (port 8001) → Blog
└── api.example.com:80,443 → Docker (port 8002) → API
```

### Step 1: DNS Configuration

Create A records for each domain:

```
Type: A, Name: photos, Value: 203.0.113.10
Type: A, Name: blog, Value: 203.0.113.10
Type: A, Name: api, Value: 203.0.113.10
```

### Step 2: Docker Port Mapping

Edit `docker-compose.prod.yml` to use different ports:

**Photo Album (port 8000):**
```yaml
services:
  web:
    ports:
      - "8000:8000"  # Photo album
```

**Other apps would use 8001, 8002, etc.**

### Step 3: Nginx Configuration

Create separate config for each domain:

**Photo Album (`/etc/nginx/sites-available/photo-album`):**

```nginx
server {
    listen 80;
    server_name photos.example.com www.photos.example.com;
    
    client_max_body_size 500M;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /home/yourusername/photo_album/staticfiles/;
        expires 30d;
    }
    
    location /media/ {
        alias /home/yourusername/photo_album/media/;
        expires 7d;
    }
}
```

**Blog (`/etc/nginx/sites-available/blog`):**

```nginx
server {
    listen 80;
    server_name blog.example.com www.blog.example.com;
    
    location / {
        proxy_pass http://localhost:8001;  # Different port!
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Enable both sites:**

```bash
sudo ln -s /etc/nginx/sites-available/photo-album /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/blog /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Step 4: SSL Certificates for Each Domain

```bash
# Photo album
sudo certbot --nginx -d photos.example.com -d www.photos.example.com

# Blog
sudo certbot --nginx -d blog.example.com -d www.blog.example.com
```

## Subdomain Setup

Running the app on a subdomain of your main domain.

### Example: Main Site with Photo Subdomain

- `example.com` → Your main website (WordPress, static site, etc.)
- `photos.example.com` → Photo Album application

### DNS Configuration

```
Type: A, Name: @, Value: 203.0.113.10 (main site)
Type: A, Name: photos, Value: 203.0.113.10 (photo album)
```

### Nginx Configuration

**Main site (`/etc/nginx/sites-available/main-site`):**

```nginx
server {
    listen 80;
    server_name example.com www.example.com;
    
    root /var/www/html;
    index index.html index.php;
    
    location / {
        try_files $uri $uri/ =404;
    }
}
```

**Photo album subdomain (`/etc/nginx/sites-available/photo-album`):**

```nginx
server {
    listen 80;
    server_name photos.example.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /home/yourusername/photo_album/staticfiles/;
        expires 30d;
    }
    
    location /media/ {
        alias /home/yourusername/photo_album/media/;
        expires 7d;
    }
}
```

Both configurations can coexist on the same server!

## Complete Step-by-Step Example

Real-world example: Setting up `photos.mysite.com`

### 1. Server Setup (One-Time)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose

# Install Nginx
sudo apt install nginx

# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Configure firewall
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP
sudo ufw allow 443/tcp # HTTPS
sudo ufw enable
```

### 2. DNS Configuration

In your DNS provider (example: Cloudflare, Namecheap):

```
Type: A
Name: photos
Value: YOUR_SERVER_IP (e.g., 203.0.113.10)
TTL: Auto
Proxy: Disabled (if using Cloudflare, disable orange cloud)
```

Wait 5-60 minutes for DNS propagation.

**Verify DNS is working:**
```bash
dig photos.mysite.com
# Should show your server IP
```

### 3. Clone and Configure Application

```bash
# Create directory
mkdir -p ~/apps
cd ~/apps

# Clone repository
git clone https://github.com/badspelr/Overly-Complicated-Photo-Album.git photo_album
cd photo_album

# Create environment file
cp .env.example .env
nano .env
```

**Edit .env file:**

```bash
# Django settings
SECRET_KEY=your-very-long-random-secret-key-here-change-this
DEBUG=False
ALLOWED_HOSTS=photos.mysite.com,localhost,127.0.0.1

# Database
DB_NAME=photo_album
DB_USER=postgres
DB_PASSWORD=your-secure-database-password-here
DB_HOST=db
DB_PORT=5432

# Site configuration
SITE_URL=https://photos.mysite.com
CSRF_TRUSTED_ORIGINS=https://photos.mysite.com

# Email (optional but recommended)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@mysite.com

# Redis
REDIS_URL=redis://redis:6379/0

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
```

### 4. Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/photo-album
```

**Paste this configuration:**

```nginx
server {
    listen 80;
    server_name photos.mysite.com;
    
    # Max upload size
    client_max_body_size 500M;
    client_body_timeout 600s;
    
    # Proxy to Docker
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts for uploads
        proxy_connect_timeout 600;
        proxy_send_timeout 600;
        proxy_read_timeout 600;
    }
    
    # Static files
    location /static/ {
        alias /home/yourusername/apps/photo_album/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /media/ {
        alias /home/yourusername/apps/photo_album/media/;
        expires 7d;
        add_header Cache-Control "public";
    }
}
```

**Enable site:**

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/photo-album /etc/nginx/sites-enabled/

# Remove default site (optional)
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Should show:
# nginx: configuration file /etc/nginx/nginx.conf test is successful

# Reload Nginx
sudo systemctl reload nginx
```

### 5. Start Application

```bash
cd ~/apps/photo_album

# Start all containers
docker-compose -f docker-compose.prod.yml up -d

# Wait for containers to be healthy (30-60 seconds)
docker-compose -f docker-compose.prod.yml ps

# Run migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Create superuser
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# Collect static files
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Check logs
docker-compose -f docker-compose.prod.yml logs -f web
```

### 6. Test HTTP Access

Visit `http://photos.mysite.com` in your browser.

You should see the photo album homepage!

If it doesn't work:
```bash
# Check Nginx
sudo nginx -t
sudo systemctl status nginx

# Check Docker
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs web

# Check if port 8000 is listening
sudo netstat -tlnp | grep 8000
```

### 7. Add SSL Certificate

```bash
# Obtain certificate
sudo certbot --nginx -d photos.mysite.com

# Follow prompts:
# 1. Enter email address
# 2. Agree to terms (Y)
# 3. Share email? (N is fine)
# 4. Redirect HTTP to HTTPS? (Yes - option 2)

# Certbot will:
# - Obtain SSL certificate
# - Update Nginx config automatically
# - Set up auto-renewal
```

### 8. Verify HTTPS

Visit `https://photos.mysite.com`

You should see:
- 🔒 Padlock in browser
- HTTPS in URL
- Your photo album working!

### 9. Auto-Renewal Check

```bash
# Test renewal process
sudo certbot renew --dry-run

# Should show:
# Congratulations, all simulated renewals succeeded
```

## Troubleshooting

### DNS Not Resolving

**Problem:** Domain doesn't point to your server

**Check:**
```bash
dig photos.example.com
# Should show your server IP
```

**Solutions:**
- Wait longer (DNS propagation can take 24-48 hours)
- Check DNS records in your registrar
- Verify A record points to correct IP
- Try flushing local DNS: `sudo systemd-resolve --flush-caches`

### 502 Bad Gateway

**Problem:** Nginx can't connect to Docker

**Check:**
```bash
# Is Docker running?
docker-compose -f docker-compose.prod.yml ps

# Is web container healthy?
docker-compose -f docker-compose.prod.yml logs web

# Is port 8000 listening?
curl http://localhost:8000
```

**Solutions:**
- Restart Docker: `docker compose -f docker-compose.prod.yml restart`
- Check .env file has correct settings
- Verify ALLOWED_HOSTS includes your domain

### SSL Certificate Failed

**Problem:** Certbot can't verify domain

**Check:**
```bash
# Is Nginx serving the domain?
curl -I http://photos.example.com

# Is port 80 accessible?
sudo netstat -tlnp | grep :80
```

**Solutions:**
- Ensure Nginx config is correct
- Verify DNS is fully propagated
- Check firewall allows port 80
- Temporarily disable Nginx and try standalone: `sudo certbot certonly --standalone -d photos.example.com`

### Static Files Not Loading

**Problem:** CSS/images broken

**Check:**
```bash
# Are static files collected?
ls -la staticfiles/

# Are permissions correct?
ls -la staticfiles/ media/
```

**Solutions:**
```bash
# Collect static files
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Fix permissions
sudo chown -R $USER:$USER staticfiles/ media/
sudo chmod -R 755 staticfiles/ media/
```

### Django Shows Wrong Domain

**Problem:** Links point to localhost

**Check `.env` file:**
```bash
ALLOWED_HOSTS=photos.example.com,localhost,127.0.0.1
SITE_URL=https://photos.example.com
CSRF_TRUSTED_ORIGINS=https://photos.example.com
```

**Solution:**
- Update .env with correct domain
- Restart: `docker compose -f docker-compose.prod.yml restart`

## Additional Resources

- [Nginx Virtual Host Documentation](https://nginx.org/en/docs/http/ngx_http_core_module.html#server)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

## Next Steps

After setup:

1. **Enable registration control** (optional)
   - Admin → Site Settings → Uncheck "Allow registration"

2. **Configure email** (recommended)
   - For invitations and password resets

3. **Set up backups** (critical)
   - See [BACKUP_STRATEGY.md](BACKUP_STRATEGY.md)

4. **Monitor logs**
   - `docker compose logs -f`

5. **Update regularly**
   - `git pull && docker-compose up -d --build`

For production hardening, see [PRODUCTION_READINESS_ASSESSMENT.md](../admin-guides/PRODUCTION_READINESS_ASSESSMENT.md).
