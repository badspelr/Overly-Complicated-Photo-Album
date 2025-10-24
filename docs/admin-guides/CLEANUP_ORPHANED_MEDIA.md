# Cleanup Orphaned Media Records

## Overview

When media files are deleted from disk but database records remain, the application will throw `FileNotFoundError` when trying to display those images or videos. The `cleanup_orphaned_media` management command scans your database and removes records for media files that no longer exist.

## When to Use This Command

Use this command when:

- You've manually deleted files from the `media/` directory
- You've restored from a database backup but not media files
- You see `FileNotFoundError` for missing photos/videos
- Albums display broken images or fail to load
- You want to sync database with actual media files on disk

## Command Options

### Dry Run (Recommended First)

See what would be deleted without actually deleting:

```bash
# Docker
docker-compose exec web python manage.py cleanup_orphaned_media --dry-run

# Non-Docker
python manage.py cleanup_orphaned_media --dry-run
```

**Output Example:**
```
Scanning for orphaned media records...
Checking 414 photos...
Checking 157 videos...

======================================================================
ORPHANED RECORDS FOUND:
======================================================================
Photos: 414 orphaned out of 414 total
Videos: 157 orphaned out of 157 total
======================================================================

Orphaned Photos (sample):
  - photos/1000004108.jpg (Album: Evan Photos)
  - photos/1000004105.jpg (Album: Evan Photos)
  ... and 404 more
```

### Interactive Mode (With Confirmation)

Delete with confirmation prompt:

```bash
# Docker
docker-compose exec web python manage.py cleanup_orphaned_media

# Non-Docker
python manage.py cleanup_orphaned_media
```

You'll be prompted:
```
⚠️  WARNING: This will permanently delete these database records!
Are you sure you want to continue? (yes/no):
```

Type `yes` to proceed.

### Force Mode (No Confirmation)

Delete without confirmation (useful for scripts):

```bash
# Docker
docker-compose exec web python manage.py cleanup_orphaned_media --force

# Non-Docker
python manage.py cleanup_orphaned_media --force
```

**⚠️ Warning:** This will immediately delete all orphaned records without asking!

## What Gets Deleted

The command checks:

1. **Photos**: Each `Photo` record's `image` field
   - If the file path doesn't exist on disk → record is marked for deletion
   - Also checks for `thumbnail` and other generated files

2. **Videos**: Each `Video` record's `video` field
   - If the video file doesn't exist on disk → record is marked for deletion
   - Thumbnails are also cleaned up automatically via Django's cascade delete

## Safety Features

✅ **Always shows summary before deleting**
- Shows total orphaned vs total records
- Displays sample of what will be deleted
- Shows which albums are affected

✅ **Dry run available**
- Test the command without making changes
- Review exactly what would be deleted

✅ **Confirmation prompt (unless --force)**
- Prevents accidental deletion
- Requires typing "yes" to proceed

✅ **Cascade deletion**
- When a Photo/Video is deleted, Django automatically cleans up:
  - Album cover references
  - Tags
  - Custom album associations
  - Generated thumbnails and caches

## Common Scenarios

### Scenario 1: Deleted Media Directory

```bash
# You accidentally deleted /media/photos/
rm -rf media/photos/

# Fix: Clean up orphaned records
docker-compose exec web python manage.py cleanup_orphaned_media --dry-run
# Review the output
docker-compose exec web python manage.py cleanup_orphaned_media --force
```

### Scenario 2: Database Restore Without Media

```bash
# Restored database from backup but media files are old/missing

# Step 1: See what's orphaned
docker-compose exec web python manage.py cleanup_orphaned_media --dry-run

# Step 2: Clean up
docker-compose exec web python manage.py cleanup_orphaned_media
# Type 'yes' when prompted
```

### Scenario 3: FileNotFoundError on Albums Page

```
FileNotFoundError at /albums/
[Errno 2] No such file or directory: '/app/media/photos/1000004108.jpg'
```

**Fix:**
```bash
docker-compose exec web python manage.py cleanup_orphaned_media --force
```

The albums page will now load correctly.

## Output Details

### Successful Cleanup

```
======================================================================
CLEANUP COMPLETE
======================================================================
Photos deleted: 414
Videos deleted: 157
Total deleted: 571
======================================================================

✓ Database cleaned successfully!
```

### No Orphaned Records

```
======================================================================
ORPHANED RECORDS FOUND:
======================================================================
Photos: 0 orphaned out of 100 total
Videos: 0 orphaned out of 50 total
======================================================================

✓ No orphaned records found! Database is clean.
```

## Preventing Orphaned Records

To avoid orphaned records in the future:

1. **Never manually delete media files** - Always delete through Django admin or app interface
2. **Use Django's delete methods** - They handle file cleanup automatically
3. **Backup media with database** - Keep media and database in sync
4. **Test restores** - Verify both database and media are restored together
5. **Run cleanup after bulk operations** - If you must manually delete files

## Related Commands

- `python manage.py cleanup_unused_files` - Delete files on disk that aren't in database (opposite operation)
- `python manage.py check_media_integrity` - Verify media files match database (if available)
- `python manage.py migrate` - Ensure database schema is up to date

## Troubleshooting

### Permission Errors

```bash
# Ensure the web container has access to media files
docker-compose exec web ls -la /app/media/photos/
```

### Large Database Performance

For very large databases (10,000+ media items), the command may take a few minutes:

```bash
# Run in background
docker-compose exec -d web python manage.py cleanup_orphaned_media --force

# Check logs
docker-compose logs -f web
```

### Partial Media Loss

If only some files are missing:

```bash
# Dry run shows exactly which files are missing
docker-compose exec web python manage.py cleanup_orphaned_media --dry-run

# Review the list carefully before proceeding
# You may want to restore specific files instead of deleting records
```

## Technical Details

- **Database**: Only deletes `Photo` and `Video` model records
- **Files**: Does NOT delete any files from disk (only database records)
- **Cascade**: Related objects cleaned up via Django's `on_delete=CASCADE`
- **Transaction**: Runs in a database transaction (atomic operation)
- **Logging**: Outputs detailed progress and summary

## See Also

- [Storage Management](../technical/STORAGE_MANAGEMENT.md)
- [Backup and Restore](../deployment/BACKUP_RESTORE.md)
- [Database Maintenance](../admin-guides/DATABASE_MAINTENANCE.md)
