# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **Gunicorn Upgrade:** Updated Gunicorn from v22.0 to v23.0
  - Fixes Python 3.13 compatibility issues with InvalidHTTPVersion errors
  - Improves worker stability and error handling
  - Reduces worker crashes from malformed HTTP requests
- **Docker GPU Support:** Refactored GPU configuration for better compatibility
  - CPU-only deployment by default (maximum server compatibility)
  - Optional GPU support via `docker-compose.gpu.yml` overlay file
  - Eliminates "could not select device driver 'nvidia'" errors on CPU-only servers
  - GPU users can opt-in: `docker compose -f docker-compose.prod.yml -f docker-compose.gpu.yml up -d`
- **Health Checks:** Improved Docker health check reliability
  - Now follows HTTP redirects with `-L` flag
  - Uses HEAD requests with `-I` flag for faster checks
  - Increased start period to 60 seconds for AI model loading
  - Reduces false-positive "unhealthy" container status

### Added
- **GPU Support Documentation:** New comprehensive GPU configuration guide
  - Located at `docs/deployment/GPU_SUPPORT.md`
  - Covers CPU vs GPU deployment options
  - Prerequisites and troubleshooting for NVIDIA GPUs
  - Performance comparison between CPU and GPU processing

### Fixed
- **Docker Deployment:** Fixed NVIDIA driver requirement errors on CPU-only servers
- **Health Check Failures:** Resolved false health check failures due to auth redirects
- **Worker Crashes:** Eliminated Gunicorn worker crashes with Python 3.13

## [1.2.0] - 2025-10-18

### Added
- **Cookie Consent System:** GDPR-compliant cookie consent implementation
  - Cookie consent banner with localStorage persistence
  - Detailed cookie policy page at `/cookie-policy/` with cookie tables
  - Accept All and Essential Only options
  - Footer link to cookie policy on all pages
- **AI Settings Admin Interface:** Web-based AI configuration at `/ai-settings/`
  - Form-based management of AI processing settings
  - Admin-only access control
  - Configure auto-processing, scheduled processing, batch sizes, timeouts
  - Real-time settings updates without code deployment
- **Comprehensive User Manual:** Expanded in-app user manual
  - 991-line HTML user manual with 15 detailed sections
  - Quick navigation menu and visual styling
  - Step-by-step guides for all features
  - Accessible at `/user-manual/` for authenticated users
- **About and Contact Pages:** Static information pages
  - About page with feature list and mission statement
  - Contact form with pre-filled user data
  - Footer navigation links on all pages
  - Email notifications to site admins

### Changed
- **User Documentation:** Migrated primary user manual to HTML template format
  - More maintainable and visually appealing than Markdown
  - Integrated into application navigation
  - Better organization with collapsible sections

### Fixed
- **Cookie Persistence:** Fixed cookie consent banner reappearing on each page
  - Switched from document.cookie to localStorage for reliable persistence
  - Works correctly on both HTTP (localhost) and HTTPS (production)

## [1.1.0] - 2025-10-16

### Added
- **Web-based AI Processing Interfaces:** New user-friendly web pages for AI photo and video processing
  - Accessible at `/process-photos-ai/` and `/process-videos-ai/` 
  - Modern dark theme design with Material Design components
  - Real-time processing progress modals with JavaScript feedback
  - Album-scoped processing for album administrators
- **Album-Scoped Permissions:** Enhanced security model for AI processing
  - Album admins can only process AI for albums they own or have viewer access to
  - Site admins retain system-wide processing capabilities
  - Unified permission model across both photos and videos processing
- **Orphaned Record Detection and Cleanup:** Intelligent handling of database inconsistencies
  - Automatic detection of database records with missing media files
  - Accurate statistics that exclude orphaned records
  - Clear user messaging about skipped files during processing
- **Processing Progress Feedback:** Enhanced user experience during AI analysis
  - Loading modals with progress indicators
  - Real-time status updates during processing
  - Clear success/error messaging with processing statistics

### Changed
- **AI Processing Backend:** Migrated from Hugging Face API to local BLIP models
  - Local GPU-accelerated image analysis using BLIP (Bootstrapping Language-Image Pre-training)
  - Faster processing with ~0.4 seconds per photo on GPU
  - Removed dependency on external API tokens
- **UI Design Overhaul:** Complete redesign of AI processing interfaces
  - Consistent dark theme matching site design
  - Professional card-based layout with CSS variables
  - Responsive design for mobile and desktop
  - Material Icons integration

### Fixed
- **Inconsistent AI Processing Permissions:** Resolved permission disparities between photos and videos
  - Previously: videos required superuser access, photos had no restrictions
  - Now: both require album admin or site admin permissions
- **Misleading Processing Statistics:** Fixed incorrect "pending" counts in AI processing pages
  - Database records without corresponding files no longer counted as "pending"
  - Accurate statistics showing only processable media
- **Missing User Feedback:** Added comprehensive user communication during processing operations
  - Progress indicators prevent user confusion during long operations
  - Clear error handling and status reporting

## [1.0.0] - 2025-09-21

### Added
- **Bulk Editing:** Users can now select multiple media items on the album detail page to:
    - Add or remove a category for all selected items.
    - Add a common set of tags to all selected items.
- **Expanded Test Coverage:**
    - Added a comprehensive test suite for permissions to ensure users can only access content they are authorized to view.
    - Created tests for the new bulk editing API endpoints to verify correct permissions and functionality.
- **Official Release Preparation:**
    - Separated production and development dependencies into `requirements.txt` and `requirements-dev.txt`.
    - Updated the installation guide to reflect the new dependency setup.
    - Added a `__version__` attribute to the project.

### Fixed
- Resolved numerous bugs in the test suite and application uncovered by the expanded test coverage.
- Corrected permission logic to allow unauthenticated users to view public albums.
- Fixed various issues with URL routing and namespacing that were causing errors in the tests.
