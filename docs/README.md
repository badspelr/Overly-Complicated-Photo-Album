# Django Photo Album - Documentation Hub

Welcome to the Django Photo Album documentation! This guide will help you get started, use, and maintain your photo album application.

## 📚 Documentation Overview

**📍 [Quick Reference Map](QUICK_REFERENCE.md)** - Fast navigation to any documentation file

### 🚀 Getting Started
Start here if you're new to Django Photo Album:

- **[Overview](getting-started/OVERVIEW.md)** - Features, architecture, and capabilities
- **[Installation Guide](getting-started/INSTALL.md)** - Complete setup instructions

### 👤 User Guides
Documentation for end users:

- **[User Manual](user-guides/USER_MANUAL.md)** - Comprehensive guide for using the application
- **[AI Commands Reference](user-guides/AI_COMMANDS_REFERENCE.md)** - AI processing features and commands

### 🔧 Administrator Guides
For system administrators and advanced users:

- **[AI Settings Management](admin-guides/ADMIN_GUIDE_AI_SETTINGS.md)** - Configure AI processing settings
- **[Celery Background Processing](admin-guides/CELERY.md)** - Complete guide for async task processing
- **[Management Commands](admin-guides/MANAGEMENT_COMMANDS.md)** - Django management command reference

### 🚀 Deployment
Production deployment and hosting:

- **[Deployment Checklist](deployment/DEPLOYMENT_CHECKLIST.md)** - Pre-deployment verification
- **[Systemd Deployment](deployment/DEPLOYMENT_SYSTEMD.md)** - Production deployment with systemd
- **[Docker Guide](deployment/DOCKER.md)** - Complete Docker deployment guide with resource optimization
- **[Celery Production Validation](deployment/CELERY_PRODUCTION_VALIDATION.md)** - Complete testing checklist for Celery in production

### 📜 Policies & Legal
Terms, policies, and legal compliance:

- **[Terms of Conduct](TERMS_OF_CONDUCT.md)** - User agreement and acceptable use policy
- **[CSAM Policy](CSAM_POLICY.md)** - Child safety and abuse material policy

### 🔬 Technical Documentation
Implementation details and technical notes:

- **[Implementation Notes](technical/IMPLEMENTATION_NOTES.md)** - Consolidated feature implementations and fixes
- **[Implementation Summary](technical/IMPLEMENTATION_SUMMARY.md)** - Technical architecture overview
- **[Terms Acceptance Implementation](technical/TERMS_ACCEPTANCE_IMPLEMENTATION.md)** - User registration terms acceptance system
- **[Documentation Reorganization](technical/DOCUMENTATION_REORGANIZATION_2025-10-18.md)** - Doc restructuring audit

---

## 🎯 Quick Links by Task

### I want to...

**Install the application:**
1. Read [Overview](getting-started/OVERVIEW.md) to understand features
2. Follow [Installation Guide](getting-started/INSTALL.md) step-by-step
3. Check [Deployment Checklist](deployment/DEPLOYMENT_CHECKLIST.md) before going live

**Use the application:**
- See [User Manual](user-guides/USER_MANUAL.md) for complete usage guide
- Visit `/user-manual/` in the app for the enhanced HTML version with 15 sections

**Configure AI processing:**
- Use [AI Settings Management](admin-guides/ADMIN_GUIDE_AI_SETTINGS.md) for web-based configuration
- Reference [AI Commands](user-guides/AI_COMMANDS_REFERENCE.md) for manual processing

**Deploy to production:**
1. Complete [Deployment Checklist](deployment/DEPLOYMENT_CHECKLIST.md)
2. Follow [Systemd Deployment](deployment/DEPLOYMENT_SYSTEMD.md) for traditional hosting
3. Or use [Docker Guide](deployment/DOCKER_GUIDE.md) for containerized deployment
4. Set up [Celery](admin-guides/CELERY_SETUP.md) for background processing

**Troubleshoot issues:**
- Check [Celery Quick Reference](admin-guides/CELERY_QUICKREF.md) for common problems
- Review [User Manual Troubleshooting](user-guides/USER_MANUAL.md#troubleshooting) section
- See technical docs for specific implementation details

---

## 📋 Additional Resources

- **[Changelog](../CHANGELOG.md)** - Version history and feature additions
- **[README](../README.md)** - Project overview and quick start

---

## 🤝 Contributing to Documentation

If you find errors or want to improve the documentation:

1. Documentation files are in Markdown format
2. Follow the existing structure and style
3. Update this index when adding new docs
4. Test all links before committing

---

## 📖 Documentation Structure

```
docs/
├── README.md (this file)
├── getting-started/    # Installation and overview
├── user-guides/        # End-user documentation
├── admin-guides/       # Administrator documentation
├── deployment/         # Production deployment
└── technical/          # Implementation details
```

---

**Last Updated:** October 18, 2025  
**Version:** 1.2.0
