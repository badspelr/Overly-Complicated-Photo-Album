# Slideshow Fix - Load All Photos from Album

## Issue
The slideshow feature was only showing 20 photos, which was the number of photos visible on the current page due to pagination.

## Root Cause
The slideshow JavaScript was loading photos from the DOM using `document.querySelectorAll()`, which only captured the photos rendered on the current page (default 20 items per page).

## Solution

### 1. Created Custom Pagination Class
**File:** `album/api/views.py`

Added `FlexiblePageNumberPagination` class that allows clients to override the page size via the `page_size` query parameter:

```python
class FlexiblePageNumberPagination(PageNumberPagination):
    """Pagination class that allows clients to control page size via query parameter."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 10000
```

### 2. Applied Custom Pagination to AlbumViewSet
**File:** `album/api/views.py`

Added the pagination class to the `AlbumViewSet`:

```python
class AlbumViewSet(viewsets.ModelViewSet):
    # ... other settings ...
    pagination_class = FlexiblePageNumberPagination
```

### 3. Updated Slideshow JavaScript
**File:** `album/static/album/js/slideshow.js`

**Changes:**
- Added `albumId` property extracted from the `data-album-id` attribute on the media container
- Created new `loadPhotosFromAlbum()` method that fetches ALL photos via the API:
  - Makes API call to `/api/albums/{album_id}/media/?media_type=photos&page_size=1000`
  - Processes the paginated response
  - Builds photo array with full album data
- Updated `start()` method to call `loadPhotosFromAlbum()` before starting the slideshow
- Kept `loadPhotosFromPage()` as a fallback if the API call fails

## Result
The slideshow now loads ALL photos from the album (up to 10,000) via the API, not just the 20 visible on the current page.

## Testing
1. Navigate to an album with more than 20 photos
2. Click the "Slideshow" button
3. Verify that all photos from the album are included in the slideshow
4. Check the browser console - should see a message like "Loaded X photos from album API"

## Files Modified
- `album/api/views.py` - Added `FlexiblePageNumberPagination` class and applied to `AlbumViewSet`
- `album/static/album/js/slideshow.js` - Updated to fetch all photos via API instead of DOM

## Date
October 22, 2025
