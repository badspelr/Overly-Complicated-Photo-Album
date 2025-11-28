# Server-Side Media Uploads

This document explains how to bulk import media files from the server filesystem into the Django photo album application.

## Overview

Instead of uploading files through the web interface, you can:
1. Upload files directly to the server via SFTP/SCP/rsync
2. Import them through the web interface (for regular users) or Django admin (for admin users)

This is useful for:
- Bulk imports of existing photo/video collections
- Migration from other systems
- Automated uploads via scripts

## Upload Directory Structure

Each user has their own personal upload directory:
```
/home/dniel/django/photo_album/media/server_uploads/<username>/
```

For example:
- Admin user: `/home/dniel/django/photo_album/media/server_uploads/admin/`
- Regular user: `/home/dniel/django/photo_album/media/server_uploads/amandanielsen221@gmail.com/`

**Important:** Users can only import files from their own directory. This prevents conflicts and ensures privacy.

## Supported File Types

### Photos
- `.jpg`, `.jpeg`
- `.png`
- `.gif`
- `.webp`
- `.bmp`

### Videos
- `.mp4`
- `.avi`
- `.mov`
- `.mkv`
- `.webm`
- `.flv`
- `.wmv`

## Import Process

### For Regular Users (Recommended)

1. Upload image/video files to your personal directory: `/home/dniel/django/photo_album/media/server_uploads/<your-username>/`
2. Log into the web application
3. Navigate to **Import from Server** page at `/server-import/`
4. Select whether you're importing **Photos** or **Videos**
5. Choose an existing album or create a new one
6. Click **"Import Selected Media"**

The system will:
- Show you a preview of files available in your directory
- Let you choose which album to import into (or create a new one)
- Verify each file is valid
- Create Photo/Video records
- Move files from your upload directory to the appropriate media folder
- Delete the original files from your upload directory

### For Admin Users (Alternative)

Admins can also use the Django admin interface:

1. Upload files to `/home/dniel/django/photo_album/media/server_uploads/admin/`
2. Log into Django admin at `/admin/`
3. Navigate to **Photos** or **Videos** section
4. Select any item and choose **"Import photos/videos from server uploads directory"**
5. Select target album or create a new one
6. Click **Go**

## Important Notes

1. **Mixed Media**: If you have both photos and videos in `server_uploads/`, run both import actions separately (photos first, then videos)

2. **Default Album**: All imported media goes into the "Server Uploads" album. You can:
   - Move files to other albums via the admin interface
   - Edit metadata (title, description, tags, category) after import
   
3. **File Cleanup**: Original files are **deleted** from `server_uploads/` after successful import. Failed imports leave the files in place.

4. **Error Handling**: If a file fails to import (corrupt, unsupported format, etc.), an error message will appear in the admin interface, and that file will remain in `server_uploads/`.

5. **AI Processing**: Imported media will be queued for AI analysis based on your AI Processing Settings (auto-process or scheduled batch processing).

6. **Permissions**: The web server user (typically www-data or the user running gunicorn) must have read/write access to `server_uploads/`.

## Example SFTP Upload

```bash
# Upload to your personal directory
sftp user@your-server.com
cd /home/dniel/django/photo_album/media/server_uploads/<your-username>/
put vacation_photo.jpg

# Upload multiple files
cd /home/dniel/django/photo_album/media/server_uploads/<your-username>/
mput *.jpg

# Or use SCP
scp *.jpg user@your-server.com:/home/dniel/django/photo_album/media/server_uploads/<your-username>/

# Or use rsync
rsync -av --progress /local/photos/ user@your-server.com:/home/dniel/django/photo_album/media/server_uploads/<your-username>/
```

Replace `<your-username>` with your actual username (e.g., `admin` or `amandanielsen221@gmail.com`).

## Security Considerations

1. Limit SFTP/SSH access to trusted users only
2. Consider using a dedicated upload user with restricted permissions
3. The `server_uploads/` directory should NOT be web-accessible
4. Files are validated before import (images are verified with PIL)

## Troubleshooting

### "Server uploads directory does not exist"
Run this on the server:
```bash
mkdir -p /home/dniel/django/photo_album/media/server_uploads/
chown www-data:www-data /home/dniel/django/photo_album/media/server_uploads/
chmod 755 /home/dniel/django/photo_album/media/server_uploads/
```

### "No image/video files found"
- Check that files have correct extensions
- Verify you're uploading to the right directory
- Ensure filenames don't have special characters that might cause issues

### Files imported but thumbnails missing
- This is normal - thumbnails are generated asynchronously
- Check Celery worker logs
- Verify ImageKit settings in `settings.py`

### Permission denied errors
```bash
# Fix permissions
sudo chown -R www-data:www-data /home/dniel/django/photo_album/media/
sudo chmod -R 755 /home/dniel/django/photo_album/media/
```
