# Viewer Permission Security Fix

## Issue Discovered

**Date:** October 22, 2025  
**Reported by:** User  
**Severity:** HIGH - Permission Escalation Vulnerability

### Problem Description

Album **viewers** were incorrectly given **full edit and delete permissions** on photos and videos, equivalent to album owners. This is a serious security issue.

**Expected Behavior:**
- Viewers should only have **VIEW** access to albums shared with them
- Only album **owners** should be able to edit or delete photos/videos

**Actual Behavior:**
- Viewers could edit photo/video metadata
- Viewers could delete photos/videos from albums they don't own
- This allowed guests to modify or destroy content

### Example Scenario

1. User "Amanda" owns album "Evan Photos"
2. User "Guest" is added as a viewer to "Evan Photos"
3. **Bug:** Guest could click "Edit Metadata" and "Delete Photo" buttons
4. **Bug:** Guest could successfully edit or delete Amanda's photos

This completely violated the owner/viewer permission model!

## Root Cause Analysis

### 1. Obsolete `is_album_admin()` Function

**File:** `album/views/media_views.py` (line 30-31)

```python
def is_album_admin(user, album):
    return user.is_superuser or album.owner == user or user in album.viewers.all()
```

**Problem:** This function treated viewers as admins, giving them full permissions.

### 2. Insufficient Permission Checks

**File:** `album/views/base_views.py` (lines 15-37)

The `check_object_permission()` function had no separate handling for 'edit' action:

```python
elif obj_type in ['photo', 'video']:
    if action == 'delete':
        return obj.album and (obj.album.owner == user or user.is_superuser)
    else:  # This 'else' handles BOTH view AND edit!
        return obj.album and (user.is_superuser or obj.album.owner == user or 
                             obj.album.viewers.filter(pk=user.pk).exists() or 
                             obj.album.is_public)
```

When `action='edit'` was passed, it fell through to the `else` clause, which allowed viewers!

### 3. Template Permission Checks

**Files:** `album/templates/album/photo_detail.html` and `video_detail.html`

Templates showed Edit/Delete buttons to viewers:

```django
{% if user.is_superuser or photo.album.owner == user or user in photo.album.viewers.all %}
    <a href="{% url 'album:photo_edit' ... %}">Edit Metadata</a>
    <a href="{% url 'album:delete_photo' ... %}">Delete Photo</a>
{% endif %}
```

This displayed the buttons to viewers, encouraging them to attempt unauthorized actions.

## Security Fix Implementation

### 1. Updated `check_object_permission()` Function

**File:** `album/views/base_views.py`

Added explicit handling for 'edit' action:

```python
elif obj_type in ['photo', 'video']:
    if action == 'delete':
        # Only album owner can delete photos/videos
        return obj.album and obj.album.owner == user
    elif action == 'edit':
        # Only album owner can edit photos/videos
        return obj.album and obj.album.owner == user
    else:  # view
        # Check if user can view the album containing the media
        return obj.album and (obj.album.owner == user or 
                             obj.album.viewers.filter(pk=user.pk).exists() or 
                             obj.album.is_public)
```

**Changes:**
- ✅ Separated 'edit' from 'view' permission
- ✅ Only album owners can edit (plus superusers via line 18)
- ✅ Only album owners can delete (plus superusers via line 18)
- ✅ Viewers can still view content

### 2. Fixed Photo and Video Edit Views

**File:** `album/views/media_views.py`

Replaced obsolete `is_album_admin()` with proper permission check:

```python
@login_required
def photo_edit(request, pk):
    """Edit photo metadata, tags, and custom albums for album owners only."""
    photo = get_object_or_404(Photo, pk=pk)
    
    # Check permissions - only album owner or superuser can edit
    if not check_object_permission(request.user, photo, 'photo', action='edit'):
        messages.error(request, 'You do not have permission to edit this photo. Only the album owner can edit photos.')
        log_security_event('unauthorized_photo_edit', request.user, f'Photo ID: {pk}')
        return redirect('album:photo_detail', pk=pk)
    
    # ... rest of view
```

Same fix applied to `video_edit()`.

**Changes:**
- ✅ Uses `check_object_permission()` with `action='edit'`
- ✅ Logs security events for unauthorized attempts
- ✅ Shows clear error message to users
- ✅ Redirects to detail page instead of dashboard

### 3. Removed Obsolete Function

**File:** `album/views/media_views.py`

Deleted the dangerous `is_album_admin()` function entirely to prevent future misuse.

### 4. Fixed Template Permission Checks

**Files:** `photo_detail.html` and `video_detail.html`

Updated button visibility logic:

```django
{# Show edit/delete buttons only to album owner or superuser #}
{% if user.is_superuser or photo.album.owner == user %}
    <a href="{% url 'album:photo_edit' photo.pk %}" class="btn btn-warning mt-2">Edit Metadata</a>
    <a href="{% url 'album:delete_photo' photo.pk %}" class="btn btn-danger mt-2">Delete Photo</a>
{% endif %}
```

**Changes:**
- ✅ Removed `or user in photo.album.viewers.all` condition
- ✅ Buttons now hidden from viewers
- ✅ Updated comments to reflect correct permissions

## Testing the Fix

### Test as Album Owner (Should Work)

1. Log in as album owner
2. Navigate to a photo in your album
3. ✅ Should see "Edit Metadata" and "Delete Photo" buttons
4. ✅ Click "Edit Metadata" - should open edit form
5. ✅ Make changes and save - should succeed

### Test as Viewer (Should Be Restricted)

1. Log in as a user who is a viewer (not owner) of an album
2. Navigate to a photo in that shared album
3. ✅ Should NOT see "Edit Metadata" or "Delete Photo" buttons
4. ✅ Try to access `/photos/<id>/edit/` directly in URL
5. ✅ Should see error: "You do not have permission to edit this photo. Only the album owner can edit photos."
6. ✅ Should be redirected to photo detail page
7. ✅ Security event should be logged

### Test as Superuser (Should Work)

1. Log in as superuser
2. Navigate to any photo
3. ✅ Should see edit/delete buttons regardless of ownership
4. ✅ Should be able to edit/delete any photo

## Permission Matrix

| User Type | View Photos | Edit Photos | Delete Photos |
|-----------|-------------|-------------|---------------|
| **Album Owner** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Viewer** | ✅ Yes | ❌ No | ❌ No |
| **Superuser** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Public (is_public=True)** | ✅ Yes | ❌ No | ❌ No |
| **Unauthorized User** | ❌ No | ❌ No | ❌ No |

## Files Modified

1. ✅ `album/views/base_views.py` - Added 'edit' action handling to `check_object_permission()`
2. ✅ `album/views/media_views.py` - Updated `photo_edit()` and `video_edit()` permission checks
3. ✅ `album/views/media_views.py` - Removed obsolete `is_album_admin()` function
4. ✅ `album/templates/album/photo_detail.html` - Fixed button visibility
5. ✅ `album/templates/album/video_detail.html` - Fixed button visibility

## Security Considerations

### What This Fixes
- ✅ Viewers can no longer edit photos/videos they don't own
- ✅ Viewers can no longer delete content from shared albums
- ✅ Unauthorized edit attempts are logged for security monitoring
- ✅ Clear error messages inform users of permission restrictions

### What Viewers Can Still Do
- ✅ View photos/videos in shared albums
- ✅ Download photos/videos (if that's desired behavior)
- ✅ Browse album contents
- ✅ Use slideshow feature

### Future Enhancements

Consider adding:
1. **Granular permissions** - Different viewer levels (read-only vs. contributor)
2. **Audit log** - Track all edit/delete operations with timestamps
3. **Permission groups** - "Editors" group with edit-but-not-delete rights
4. **Ownership transfer** - Allow transferring album ownership
5. **Shared editing** - Optional collaborative mode for specific albums

## Related Security

This fix is part of a larger security overhaul that previously addressed:
- ✅ Global "Album Admin" privilege escalation (eliminated global admin group)
- ✅ Account deletion with proper data cleanup
- ✅ CSRF protection on all forms
- ✅ XSS prevention in user inputs
- ✅ SQL injection protection via ORM

## Recommendations

1. **Review other permissions** - Check if similar issues exist in album-level permissions
2. **Add permission tests** - Create automated tests for all permission scenarios
3. **Security audit** - Consider a full security review of all permission checks
4. **Documentation** - Update user manual with clear explanation of viewer rights

## Date
October 22, 2025
