# Duplicate Cleanup Scripts

## Overview

This directory contains scripts to help clean up duplicate photos and videos from your photo album application.

## Scripts

### `cleanup_all_duplicates.sh`

Automatically finds and removes duplicate photos from all albums in the system.

**Features:**
- Scans all albums with 2+ photos for duplicates
- Uses MD5 hash comparison to detect identical files
- Keeps the oldest upload, deletes newer duplicates
- Shows space freed after cleanup
- Supports dry-run mode for safe preview

**Usage:**

```bash
# Preview what would be deleted (RECOMMENDED FIRST)
./scripts/cleanup_all_duplicates.sh --dry-run

# Actually delete duplicates
./scripts/cleanup_all_duplicates.sh
```

**On Production Server:**

```bash
# 1. Pull latest code from GitHub
cd /path/to/photo_album
git pull origin main  # or dev

# 2. Activate virtual environment (if using one)
source venv/bin/activate

# 3. Run dry-run first to preview
python manage.py shell -c "from album.models import Album, Photo; from django.contrib.auth import get_user_model; User = get_user_model(); print('Users:', User.objects.count(), 'Albums:', Album.objects.count(), 'Photos:', Photo.objects.count())"

./scripts/cleanup_all_duplicates.sh --dry-run

# 4. Review the output, then run for real
./scripts/cleanup_all_duplicates.sh
```

## Manual Command

You can also remove duplicates from specific albums using the management command directly:

```bash
# Dry-run for specific album
python manage.py remove_duplicates --username user@example.com --album "Album Name" --dry-run

# Actually delete duplicates
python manage.py remove_duplicates --username user@example.com --album "Album Name"
```

## How It Works

1. **Detection**: Calculates MD5 hash of each photo's file content
2. **Grouping**: Groups photos with identical hashes (exact duplicates)
3. **Selection**: Sorts by upload date and keeps the oldest one
4. **Deletion**: Deletes the file and database record for newer duplicates
5. **Reporting**: Shows how many photos deleted and space freed

## Safety Features

- **Dry-run mode**: Preview changes before committing
- **Confirmation prompt**: Requires "yes" to proceed with deletions
- **Detailed output**: Shows exactly which photos will be kept/deleted
- **Album-scoped**: Only checks for duplicates within the same album
- **Color-coded**: Green for kept, red for deleted, yellow for warnings

## Output Limiting

The script limits output to prevent overwhelming logs:
- **Dry-run mode**: Shows first 100 lines per album
- **Actual deletion**: Shows last 20 lines (summary) per album

## Notes

- Duplicates are detected by file content (MD5 hash), not filename
- The same photo can exist in multiple albums (not considered duplicates)
- Only photos with identical file content are affected
- Original files are permanently deleted from disk

## Troubleshooting

**No albums found:**
- Check that albums have at least 2 photos
- Verify database connection is working

**Permission denied:**
- Make script executable: `chmod +x scripts/cleanup_all_duplicates.sh`

**Django not found:**
- Activate your virtual environment first
- Verify you're in the correct directory (where manage.py is)
