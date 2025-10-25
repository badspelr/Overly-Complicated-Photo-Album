# Versioning Guide

## Current Version: **1.3.0** (October 24, 2025)

Django Photo Album follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html) (SemVer).

---

## Version Format: MAJOR.MINOR.PATCH

### MAJOR (X.0.0)
Incremented when making **incompatible API changes** or **breaking changes**.

**Examples:**
- Database schema changes requiring migration
- Removing deprecated features
- Changing API endpoints that break backwards compatibility
- Major architectural changes
- Python or Django version requirements changes

**Current:** 1 (stable API)

### MINOR (x.X.0)
Incremented when adding **functionality in a backwards-compatible manner**.

**Examples:**
- New features (e.g., face recognition, photo editor)
- New API endpoints
- New management commands
- Enhanced AI capabilities
- Performance improvements
- New optional dependencies

**Current:** 3 (third feature release in v1)

### PATCH (x.x.X)
Incremented for **backwards-compatible bug fixes**.

**Examples:**
- Security patches
- Bug fixes
- Documentation updates
- Performance optimizations
- UI improvements
- Minor tweaks

**Current:** 0 (no patches yet in 1.3)

---

## Version History

### [1.3.0] - 2025-10-24 (Current)
**Public Release Ready** 🎉

**Added:**
- Comprehensive TODO roadmap (98 tasks)
- RELEASE_READY.md documentation
- First Time Setup guide
- Cleanup orphaned media command
- Version management system

**Changed:**
- Removed default admin account (security)
- Marked Auto Process on Upload as future feature
- Enhanced documentation with security focus

**Fixed:**
- CORS misconfiguration (HIGH SEVERITY)
- Cache backend multi-worker issue (HIGH SEVERITY)

**Assessment:** A- (89/100)

---

### [1.2.0] - 2024-10-18
**Feature Complete**

**Added:**
- Comprehensive test suite (167 tests, 37% coverage)
- AI Settings admin interface
- Cookie consent system
- About and Contact pages
- User manual (991 lines)
- Registration control feature

---

### [1.1.0] - 2024-09-15
**AI Enhancement**

**Added:**
- Automatic AI processing with Celery
- Scheduled batch processing
- Video metadata editing
- Album admin processing limits

**Improved:**
- Performance optimizations
- Background task handling

---

### [1.0.0] - 2024-08-01
**Initial Release**

**Core Features:**
- Photo/video management
- AI-powered search (CLIP, BLIP)
- REST API
- Docker deployment
- User authentication
- Album permissions

---

## How to Check Version

### Command Line

```bash
# Full version information
docker-compose exec web python manage.py appversion

# Just the version number
docker-compose exec web python manage.py appversion --short

# Version history
docker-compose exec web python manage.py appversion --history
```

### Python Code

```python
# In your code
from photo_album import __version__

print(f"Django Photo Album v{__version__}")
```

### Files

```bash
# Read VERSION file
cat VERSION

# Check __version__.py
cat photo_album/__version__.py
```

### Docker Image

```bash
# Docker image tag
docker images | grep photo_album
```

---

## Releasing New Versions

### Step 1: Decide Version Number

**Bug fix?** → Increment PATCH (1.3.0 → 1.3.1)
**New feature?** → Increment MINOR (1.3.0 → 1.4.0)
**Breaking change?** → Increment MAJOR (1.3.0 → 2.0.0)

### Step 2: Update Version Files

```bash
# 1. Update photo_album/__version__.py
#    - Change __version__
#    - Change __version_info__
#    - Add entry to VERSION_HISTORY

# 2. Update VERSION file
echo "1.4.0" > VERSION

# 3. Update CHANGELOG.md
#    - Move [Unreleased] items to new version section
#    - Add release date
#    - Document all changes

# 4. Update README.md
#    - Update version number in footer
#    - Update release date
```

### Step 3: Commit and Tag

```bash
# Commit changes
git add -A
git commit -m "Release version 1.4.0

- Feature 1
- Feature 2
- Bug fix 3"

# Create git tag
git tag -a v1.4.0 -m "Version 1.4.0"

# Push to GitHub
git push origin main
git push origin v1.4.0
```

### Step 4: Create GitHub Release

1. Go to GitHub repository
2. Click "Releases" → "Create a new release"
3. Select tag: `v1.4.0`
4. Title: "Version 1.4.0 - Release Name"
5. Description: Copy from CHANGELOG.md
6. Upload artifacts (optional):
   - Source code (auto-generated)
   - Docker compose files
   - Documentation PDFs
7. Publish release

### Step 5: Update Docker Images (Optional)

```bash
# Build and tag Docker image
docker build -t photo-album:1.4.0 .
docker tag photo-album:1.4.0 photo-album:latest

# Push to Docker Hub (if applicable)
docker push yourusername/photo-album:1.4.0
docker push yourusername/photo-album:latest
```

---

## Version Lifecycle

### Supported Versions

| Version | Status | Support Until | Notes |
|---------|--------|---------------|-------|
| 1.3.x | ✅ Current | Ongoing | Production-ready |
| 1.2.x | ⚠️ Maintenance | 2025-12-31 | Security fixes only |
| 1.1.x | ❌ End of Life | 2025-10-24 | Upgrade recommended |
| 1.0.x | ❌ End of Life | 2024-12-31 | No longer supported |

### Support Policy

- **Current version:** Full support (features, bugs, security)
- **Previous MINOR:** Security and critical bug fixes only
- **Older versions:** No support, upgrade required

---

## Deprecation Policy

### Timeline

1. **Announce deprecation** - In release notes and documentation
2. **Warning period** - At least 1 MINOR version (e.g., deprecated in 1.4, removed in 1.5)
3. **Final warning** - In last supported version
4. **Removal** - In next MAJOR or MINOR version

### Example

```
Version 1.4.0: Feature X deprecated (warning in logs)
Version 1.5.0: Feature X still works (final warning)
Version 1.6.0: Feature X removed
```

---

## Version Badges

### For README.md

```markdown
![Version](https://img.shields.io/badge/version-1.3.0-blue.svg)
![Status](https://img.shields.io/badge/status-stable-green.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)
```

### For Documentation

```html
<a href="https://github.com/badspelr/Overly-Complicated-Photo-Album/releases">
  <img src="https://img.shields.io/badge/version-1.3.0-blue.svg" alt="Version">
</a>
```

---

## Roadmap

### Planned Versions

**1.4.0** (Q1 2026) - Monitoring & Observability
- Sentry error tracking
- Prometheus metrics
- Grafana dashboards
- OpenAPI documentation

**1.5.0** (Q2 2026) - Testing & Quality
- Test coverage to 60%+
- Performance tests
- Load testing
- Frontend decision implementation

**1.6.0** (Q3 2026) - Growth Features
- Enhanced analytics
- CDN integration
- Internationalization (i18n)
- Mobile PWA

**2.0.0** (Q4 2026) - Major Update
- Django 6.0 upgrade
- Python 3.12+ requirement
- API v2 (breaking changes)
- Database schema improvements

See [TODO_REVIEW.md](TODO_REVIEW.md) for complete roadmap.

---

## Breaking Changes Log

### Version 2.0.0 (Planned)
- Django 6.0 minimum requirement
- Python 3.12+ minimum requirement
- API endpoint changes
- Database schema changes

### Version 1.0.0 (Released)
- Initial stable release
- No breaking changes (baseline)

---

## FAQ

### Q: How often are new versions released?

**A:** 
- **PATCH:** As needed (bug fixes, security)
- **MINOR:** Every 1-2 months (new features)
- **MAJOR:** Once per year (breaking changes)

### Q: Do I need to upgrade immediately?

**A:** 
- **PATCH:** Recommended within 1 week (especially security)
- **MINOR:** Upgrade when convenient (no breaking changes)
- **MAJOR:** Plan migration carefully (breaking changes)

### Q: How do I upgrade?

**A:**
1. Read CHANGELOG.md for changes
2. Back up database and media files
3. Update code: `git pull origin main`
4. Run migrations: `python manage.py migrate`
5. Restart services: `docker compose restart`
6. Test thoroughly

### Q: What if I skip a version?

**A:** You can upgrade across multiple versions, but:
- Read all intermediate CHANGELOGs
- Run all migrations in order
- Test thoroughly
- Consider staged upgrade (1.2→1.3→1.4)

### Q: Where can I see what's coming next?

**A:** Check:
- [CHANGELOG.md](CHANGELOG.md) - [Unreleased] section
- [TODO_REVIEW.md](TODO_REVIEW.md) - Roadmap
- GitHub Issues - Planned features
- GitHub Projects - Development board

---

**Current Version:** 1.3.0  
**Release Date:** October 24, 2025  
**Status:** Production/Stable  
**Next Version:** 1.4.0 (Planned Q1 2026)
