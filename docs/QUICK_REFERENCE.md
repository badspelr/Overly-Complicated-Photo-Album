# Documentation Quick Reference Map

**Quick navigation for all documentation files**

## 📍 Start Here

| What You Want | Go To |
|---------------|-------|
| **First time here?** | [README.md](../README.md) |
| **Install the app** | [docs/getting-started/INSTALL.md](getting-started/INSTALL.md) |
| **Learn features** | [docs/getting-started/OVERVIEW.md](getting-started/OVERVIEW.md) |
| **Use the app** | [docs/user-guides/USER_MANUAL.md](user-guides/USER_MANUAL.md) |
| **Deploy to production** | [docs/deployment/](deployment/) |
| **Configure AI settings** | [docs/admin-guides/ADMIN_GUIDE_AI_SETTINGS.md](admin-guides/ADMIN_GUIDE_AI_SETTINGS.md) |
| **What's new?** | [CHANGELOG.md](../CHANGELOG.md) |

## 📂 Complete File Listing

### Root Directory
```
/
├── README.md ......................... Project overview and quick start
└── CHANGELOG.md ...................... Version history and changes
```

### Getting Started (Installation & Overview)
```
docs/getting-started/
├── INSTALL.md ........................ Complete installation guide
└── OVERVIEW.md ....................... Features and architecture
```

### User Guides (How to Use)
```
docs/user-guides/
├── USER_MANUAL.md .................... Complete user guide
└── AI_COMMANDS_REFERENCE.md .......... AI processing commands
```

### Admin Guides (Configuration & Management)
```
docs/admin-guides/
├── ADMIN_GUIDE_AI_SETTINGS.md ........ Configure AI processing
├── CELERY.md ......................... Complete Celery guide
└── MANAGEMENT_COMMANDS.MD ............ Django management commands
```

### Deployment (Production Setup)
```
docs/deployment/
├── DEPLOYMENT_CHECKLIST.md ........... Pre-deployment verification
├── DEPLOYMENT_SYSTEMD.md ............. Production deployment guide
├── DOCKER.md ......................... Complete Docker guide
└── CELERY_PRODUCTION_VALIDATION.md ... Celery testing checklist
```

### Policies & Legal
```
docs/
├── TERMS_OF_CONDUCT.md ............... User terms and acceptable use
└── CSAM_POLICY.md .................... Child safety policy
```

### Technical (Implementation Details)
```
docs/technical/
├── IMPLEMENTATION_NOTES.md ........... Consolidated feature docs
├── IMPLEMENTATION_SUMMARY.md ......... Technical architecture
└── DOCUMENTATION_REORGANIZATION_2025-10-18.md  This reorganization
```

## 🔗 External Links

- **Live User Manual (HTML):** `/user-manual/` (in-app)
- **AI Settings Interface:** `/ai-settings/` (admin only)
- **Cookie Policy:** `/cookie-policy/`
- **About Page:** `/about/`
- **Contact Form:** `/contact/`

## 📊 Documentation by Audience

### 👤 End Users
1. [User Manual](user-guides/USER_MANUAL.md)
2. [AI Commands Reference](user-guides/AI_COMMANDS_REFERENCE.md)
3. In-app user manual at `/user-manual/`

### 🔧 System Administrators  
1. [AI Settings Management](admin-guides/ADMIN_GUIDE_AI_SETTINGS.md)
2. [Celery Setup](admin-guides/CELERY_SETUP.md)
3. [Celery Quick Reference](admin-guides/CELERY_QUICKREF.md)
4. [Management Commands](admin-guides/MANAGEMENT_COMMANDS.md)
5. [Deployment Checklist](deployment/DEPLOYMENT_CHECKLIST.md)

### 🚀 DevOps / Deployment
1. [Installation Guide](getting-started/INSTALL.md)
2. [Deployment Checklist](deployment/DEPLOYMENT_CHECKLIST.md)
3. [Systemd Deployment](deployment/DEPLOYMENT_SYSTEMD.md)
4. [Docker Guide](deployment/DOCKER_GUIDE.md)
5. [Docker Resource Guide](deployment/DOCKER_RESOURCE_GUIDE.md)

### 💻 Developers / Maintainers
1. [Overview](getting-started/OVERVIEW.md)
2. [Implementation Summary](technical/IMPLEMENTATION_SUMMARY.md)
3. Technical documentation in [technical/](technical/)
4. [Changelog](../CHANGELOG.md)

## 🔍 Documentation by Topic

### Installation & Setup
- [Installation Guide](getting-started/INSTALL.md)
- [Deployment Checklist](deployment/DEPLOYMENT_CHECKLIST.md)
- [Docker Guide](deployment/DOCKER_GUIDE.md)

### AI Features
- [Overview - AI Section](getting-started/OVERVIEW.md#ai-powered-intelligence)
- [AI Commands Reference](user-guides/AI_COMMANDS_REFERENCE.md)
- [AI Settings Management](admin-guides/ADMIN_GUIDE_AI_SETTINGS.md)

### Background Processing
- [Celery Setup](admin-guides/CELERY_SETUP.md)
- [Celery Quick Reference](admin-guides/CELERY_QUICKREF.md)
- [Deployment - Celery Section](deployment/DEPLOYMENT_SYSTEMD.md)

### Docker & Containers
- [Docker Guide](deployment/DOCKER_GUIDE.md)
- [Docker Resource Guide](deployment/DOCKER_RESOURCE_GUIDE.md)

### User Features
- [User Manual](user-guides/USER_MANUAL.md)
- [Overview - Features](getting-started/OVERVIEW.md#key-features)

### Security & Privacy
- [Overview - Security Features](getting-started/OVERVIEW.md#security-features)
- [Album Owner Permissions](technical/ALBUM_OWNER_PERMISSIONS_FIX.md)

### Administration
- [AI Settings Management](admin-guides/ADMIN_GUIDE_AI_SETTINGS.md)
- [Management Commands](admin-guides/MANAGEMENT_COMMANDS.md)
- [Celery Quick Reference](admin-guides/CELERY_QUICKREF.md)

## 📝 File Sizes

| File | Size | Lines |
|------|------|-------|
| README.md (root) | 4.7K | ~150 |
| CHANGELOG.md | 5.3K | ~150 |
| docs/README.md | ~4K | ~140 |
| INSTALL.md | 8.3K | 325 |
| OVERVIEW.md | 15K | 312 |
| USER_MANUAL.md | 20K | 560 |
| AI_COMMANDS_REFERENCE.md | 9.7K | ~300 |
| ADMIN_GUIDE_AI_SETTINGS.md | 6.3K | 276 |
| CELERY_SETUP.md | 6.7K | ~250 |
| CELERY_QUICKREF.md | 5.1K | ~200 |
| DEPLOYMENT_SYSTEMD.md | 12K | ~400 |
| IMPLEMENTATION_SUMMARY.md | 11K | ~350 |

## 🎯 Common Workflows

### New User Setup
1. [README.md](../README.md) - Understand the project
2. [INSTALL.md](getting-started/INSTALL.md) - Install locally
3. [USER_MANUAL.md](user-guides/USER_MANUAL.md) - Learn to use

### Production Deployment
1. [OVERVIEW.md](getting-started/OVERVIEW.md) - Understand architecture
2. [DEPLOYMENT_CHECKLIST.md](deployment/DEPLOYMENT_CHECKLIST.md) - Verify readiness
3. [DEPLOYMENT_SYSTEMD.md](deployment/DEPLOYMENT_SYSTEMD.md) - Deploy
4. [CELERY_SETUP.md](admin-guides/CELERY_SETUP.md) - Configure background tasks
5. [AI Settings](admin-guides/ADMIN_GUIDE_AI_SETTINGS.md) - Configure AI

### Troubleshooting
1. [CELERY_QUICKREF.md](admin-guides/CELERY_QUICKREF.md) - Check Celery issues
2. [USER_MANUAL.md](user-guides/USER_MANUAL.md#troubleshooting) - User issues
3. [CHANGELOG.md](../CHANGELOG.md) - Check for known issues

---

**Last Updated:** October 18, 2025  
**Total Documentation Files:** 19  
**Documentation Version:** 1.2.0
