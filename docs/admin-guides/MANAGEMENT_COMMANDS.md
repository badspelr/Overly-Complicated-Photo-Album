# Management Commands Guide

This document provides an overview of the essential management commands available in the Django Photo Album project. These scripts are designed to be run from the command line and are used for setup, maintenance, and core application tasks.

## How to Run Commands

All commands must be run from the root directory of the project with your virtual environment activated. The basic syntax is:

```bash
python manage.py <command_name> [options]
```

---

## Essential Commands

### 1. Initial Setup

These commands are typically run once during the initial installation and setup of the application.

#### `enable_vector`
Enables the `pgvector` extension in your PostgreSQL database. This is a critical step for enabling AI-powered search features.

**Usage:**
```bash
python manage.py enable_vector
```

#### `setup_groups`
Creates the initial user groups (`Album Admin`, `Viewer`) and assigns the necessary permissions to them. This should be run after the initial database migration.

**Usage:**
```bash
python manage.py setup_groups
```

---

### 2. AI & Media Processing

These commands are used to process your media files, generate data for AI features, and create thumbnails. They can be run initially to process all existing media and then periodically (e.g., in a cron job) to process new uploads.

#### `analyze_photos`
Analyzes photos using local BLIP (Bootstrapping Language-Image Pre-training) models to automatically generate descriptive text and relevant tags. Uses GPU acceleration when available for faster processing.

**Usage:**
```bash
# Analyze all photos that haven't been processed yet
python manage.py analyze_photos

# Force re-analysis of all photos, even if they have existing descriptions
python manage.py analyze_photos --force

# Limit the analysis to a specific number of photos (useful for testing)
python manage.py analyze_photos --limit 100

# Process only photos from a specific album
python manage.py analyze_photos --album "Family Photos"
```

**Web Interface Alternative:** Access user-friendly processing at `/process-photos-ai/` with real-time progress indicators.

#### `analyze_videos`
Analyzes video thumbnails using local BLIP models to generate descriptions and tags for videos. Requires video thumbnails to be generated first.

**Usage:**
```bash
# Analyze all videos that haven't been processed yet
python manage.py analyze_videos

# Force re-analysis of all videos
python manage.py analyze_videos --force

# Process only videos from a specific album
python manage.py analyze_videos --album "Events"

# Limit processing to 50 videos
python manage.py analyze_videos --limit 50
```

**Prerequisites:** Run `python manage.py generate_video_thumbnails` first to ensure thumbnails exist.
**Web Interface Alternative:** Access user-friendly processing at `/process-videos-ai/` with album-scoped permissions.

#### `generate_embeddings`
Generates vector embeddings from your photos, which are used for the AI similarity search.

**Usage:**
```bash
# Generate embeddings for all photos that don't have them
python manage.py generate_embeddings

# Force regeneration of embeddings for all photos
python manage.py generate_embeddings --force
```

---

### 3. Maintenance & Utilities

These commands are used for ongoing maintenance and utility tasks.

#### `generate_thumbnails`
Pre-generates thumbnail images for photos. This is useful for improving page load performance.

**Usage:**
```bash
# Generate thumbnails for all photos
python manage.py generate_thumbnails

# Force regeneration of existing thumbnails
python manage.py generate_thumbnails --force
```

#### `generate_video_thumbnails`
Generates thumbnail images for videos that are missing them.

**Usage:**
```bash
# Generate thumbnails for videos without them
python manage.py generate_video_thumbnails

# Force regeneration of all video thumbnails
python manage.py generate_video_thumbnails --force
```

#### `regenerate_thumbnails`
A more forceful utility to regenerate all thumbnails for all photos. This is useful if you've changed your thumbnail settings or have issues with broken thumbnails.

**Usage:**
```bash
python manage.py regenerate_thumbnails
```

#### `manage_cache`
A utility for managing the application's Redis cache.

**Usage:**
```bash
# Clear the entire cache
python manage.py manage_cache clear

# Check if the cache is running and accessible
python manage.py manage_cache status

# Warm the cache for a specific user (loads their data into the cache)
python manage.py manage_cache warm --user-id 1
```

#### `reprocess_metadata`
Scans existing photos and attempts to extract and save EXIF metadata, such as "Date Taken", camera model, and GPS coordinates. This is especially useful after a code change to the metadata extraction logic or for fixing photos that are missing this information.

**Usage:**
```bash
# Default: Process only photos that are missing a "Date Taken"
python manage.py reprocess_metadata

# Simulate the process without making any database changes
python manage.py reprocess_metadata --dry-run

# Force the script to re-process ALL photos, even if they already have a "Date Taken"
python manage.py reprocess_metadata --force
```
**Note:** This command only updates metadata fields on the photo. It does not change albums, categories, tags, or other relationships.
