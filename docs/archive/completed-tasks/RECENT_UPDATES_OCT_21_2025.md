# Recent Updates - October 21, 2025

## Summary of Changes

This document summarizes the recent improvements and bug fixes made to the Django Photo Album application on October 21, 2025.

---

## 🎯 New Features

### 1. Configurable Album Admin Processing Limit

**What Changed:**
- Album admins can now process AI batches with a configurable limit (previously hardcoded at 50)
- New setting in Django Admin: `album_admin_processing_limit`
- Applies to both photo and video AI processing

**How to Use:**
1. Go to Django Admin → AI Processing Settings
2. Adjust "Album admin processing limit" field (default: 50)
3. Save settings
4. Album admins will be limited to this number per batch
5. Site admins always have unlimited processing

**Implementation Details:**
- New field: `AIProcessingSettings.album_admin_processing_limit`
- Default value: 50
- Validation: Must be at least 1
- Updated views: `process_photos_ai` and `process_videos_ai`
- Migration: `0007_add_album_admin_processing_limit`

**Files Modified:**
- `album/models.py` - Added field and validation
- `album/admin.py` - Added to admin interface
- `album/views/media_views.py` - Updated both processing views
- `album/migrations/0007_add_album_admin_processing_limit.py` - Database migration

---

### 2. Album Owner AI Processing Access

**What Changed:**
- Album owners can now see and access AI processing tools in the navigation menu
- Previously only site admins could see these options
- Links added: "Process Photos AI" and "Process Videos AI"

**User Experience:**
- Album owners see these links alongside "Manage Categories" and "Invite User"
- Permission checks remain in place - album owners can only process their own albums
- Site admins continue to have full access to all albums

**Implementation Details:**
- Updated navigation template: `album/templates/album/base.html`
- Added links to `{% elif user.is_album_owner %}` section
- Backend permissions already supported this (just UI was missing)

**Files Modified:**
- `album/templates/album/base.html` - Added navigation links for album owners

---

## 🐛 Bug Fixes

### 1. Bulk Media Operations ID Parsing

**Issue:**
- Bulk delete and download operations failed with: `ValueError: Field 'id' expected a number but got 'photo-383'`
- Frontend sends prefixed IDs like "photo-383" or "video-42" from checkboxes
- Backend expected raw numeric IDs

**Solution:**
- Added ID parsing logic to extract media type and numeric ID
- Format: Split on '-', get type (photo/video) and numeric ID
- Try appropriate model based on parsed type

**Implementation:**
```python
# Parse ID format: "photo-383" or "video-42"
parts = media_id.split('-')
media_type = parts[0]
numeric_id = int(parts[1])

if media_type == 'photo':
    media_obj = Photo.objects.get(pk=numeric_id)
elif media_type == 'video':
    media_obj = Video.objects.get(pk=numeric_id)
```

**Files Modified:**
- `album/views/media_views.py` - Updated `bulk_delete` (lines 589-640)
- `album/views/media_views.py` - Updated `bulk_download` (lines 654-710)

---

### 2. Album Cover Display for Video-Only Albums

**Issue:**
- Albums containing only videos didn't show cover images
- Template only checked for `album.photos.first.thumbnail`
- Videos have thumbnails too but weren't being used

**Solution:**
- Added fallback chain: cover_image → photos.first.thumbnail → videos.first.thumbnail
- Updated both dashboard and album list templates

**Implementation:**
```django
{% if album.cover_image %}
    <img src="{{ album.cover_image.url }}" alt="{{ album.title }}">
{% elif album.photos.first.thumbnail %}
    <img src="{{ album.photos.first.thumbnail.url }}" alt="{{ album.title }}">
{% elif album.videos.first.thumbnail %}
    <img src="{{ album.videos.first.thumbnail.url }}" alt="{{ album.title }}">
{% else %}
    <div class="no-cover">No Cover</div>
{% endif %}
```

**Files Modified:**
- `album/templates/album/dashboard.html` - Line 63
- `album/templates/album/album_list.html` - Line 243

---

### 3. Upload Album Pre-selection

**Issue:**
- Clicking "Add Media" from album dashboard didn't pre-select the target album
- Users had to manually select album from dropdown after navigating

**Solution:**
- Read `?album=` query parameter from URL
- Validate user owns/can access the album
- Pre-populate form with selected album

**Implementation:**
```python
album_id = request.GET.get('album')
if album_id:
    album = Album.objects.get(pk=album_id)
    if request.user == album.owner or request.user.is_superuser:
        initial_data['album'] = album
```

**Files Modified:**
- `album/views/media_views.py` - Updated `minimal_upload` view (lines 1243-1256)

---

### 4. Upload Validation Before Spinner

**Issue:**
- Upload validation happened after loading spinner started
- Users saw spinner, then error about missing album selection
- Confusing UX - spinner implies processing started

**Solution:**
- Added client-side validation before showing spinner
- Check album selection first
- Show alert and prevent submission if invalid

**Implementation:**
```javascript
const albumSelect = document.querySelector('select[name="album"]');
if (!albumSelect || !albumSelect.value) {
    alert('Please select an album before uploading.');
    event.preventDefault();
    return false;
}
// Show spinner only after validation passes
```

**Files Modified:**
- `album/static/album/js/minimal_upload.js` - Updated `confirmUpload()` function

---

## 🛠️ Development Improvements

### Docker Development Workflow

**What Changed:**
- Added code volume mounts to docker-compose.yml
- Live code reloading without rebuilding Docker images
- Faster development iteration

**Volumes Mounted:**
```yaml
volumes:
  # Code volumes for development (remove for production)
  - ./album:/app/album
  - ./photo_album:/app/photo_album
  - ./manage.py:/app/manage.py
```

**Services Updated:**
- web
- celery-worker
- celery-beat

**Files Modified:**
- `docker-compose.yml` - Added volume mounts with production removal comments

---

## 📚 Documentation Updates

### Updated Documents:

1. **ADMIN_GUIDE_AI_SETTINGS.md**
   - Added "Album Admin Processing Limit" section
   - New scenarios for changing the limit
   - Updated shell command examples
   - Added recommendations by use case

2. **USER_MANUAL.md**
   - Updated permission model section
   - Documented album admin batch size limits
   - Explained configurability of limits

3. **AI_COMMANDS_REFERENCE.md**
   - Updated web interface alternatives section
   - Documented permission model with batch limits
   - Clarified site admin vs album admin permissions

4. **CHANGELOG.md**
   - Added [Unreleased] section with all recent changes
   - Organized by Added, Fixed, Changed, Documentation

5. **RECENT_UPDATES_OCT_21_2025.md** (this document)
   - Comprehensive summary of all changes
   - Implementation details and code examples

---

## 🧪 Testing Performed

### Database Migration
```bash
✅ Migration 0007_add_album_admin_processing_limit created
✅ Migration applied successfully
✅ Setting loads correctly with default value of 50
✅ Setting can be modified and persisted
```

### Code Volume Mounts
```bash
✅ Template changes reflect immediately
✅ Python code changes reflect without rebuild
✅ All containers restarted successfully
```

### Functionality Tests
```bash
✅ Bulk delete with "photo-383" format IDs works
✅ Bulk download with prefixed IDs works
✅ Video-only albums show cover images
✅ Album pre-selection from ?album= parameter works
✅ Upload validation before spinner works
✅ Album owner sees AI processing links
✅ AI processing respects configurable limit
```

---

## 🔄 Rollback Information

If you need to rollback these changes:

### Revert Migration
```bash
python manage.py migrate album 0006  # Or previous migration number
```

### Revert Code Changes
```bash
git revert <commit-hash>
# Or manually restore from backup
```

### Remove Volume Mounts (Production)
In `docker-compose.yml`, remove or comment out these lines:
```yaml
# Code volumes for development (remove for production)
- ./album:/app/album
- ./photo_album:/app/photo_album
- ./manage.py:/app/manage.py
```

---

## 📝 Notes for Deployment

### Production Considerations:

1. **Remove Development Volumes:**
   - Comment out code volume mounts in docker-compose.yml
   - Rebuild Docker image with `docker-compose build web`
   - Code will be baked into image (no live reloading)

2. **Set Album Admin Limit:**
   - Review and adjust `album_admin_processing_limit` for your environment
   - Consider server resources and user base
   - Default of 50 is conservative and safe

3. **Verify Permissions:**
   - Test album owner access to AI processing
   - Ensure site admins retain unlimited access
   - Check that album-scoped filtering works correctly

4. **Monitor Performance:**
   - Watch AI processing loads with new album owner access
   - Adjust limits if system becomes overloaded
   - GPU acceleration helps with higher limits

---

## 🎉 Summary

This update focused on improving user experience, fixing bugs, and making the system more configurable:

- ✅ **4 bug fixes** (bulk operations, album covers, upload UX)
- ✅ **2 new features** (configurable limits, album owner access)
- ✅ **1 development improvement** (live code reloading)
- ✅ **5 documentation updates** (admin guide, user manual, changelog, etc.)

All changes maintain backward compatibility and include proper migrations and documentation.
