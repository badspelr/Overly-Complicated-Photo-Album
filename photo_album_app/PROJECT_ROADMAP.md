# Photo Album Flutter App - Project Roadmap

## 📱 Overview
Flutter mobile application for the Django Photo Album project. Provides photo/video browsing, management, and AI-powered search capabilities.

---

## ✅ Phase 1: Core Features (COMPLETED)

### Authentication & Navigation
- [x] Token-based login
- [x] Logout functionality
- [x] Token persistence (SharedPreferences)
- [x] Navigation between screens

### Albums
- [x] List all albums (grid view)
- [x] Display album cover photos
- [x] Show album metadata (title, description, privacy status)
- [x] Navigate to album contents

### Media Viewing
- [x] Display photos and videos in grid
- [x] Photo detail view with pinch-to-zoom
- [x] Video thumbnail display with play icon
- [x] Video detail screen (placeholder for playback)
- [x] Swipe between photos/videos
- [x] Hero animations for smooth transitions
- [x] Image caching (CachedNetworkImage)

### Upload
- [x] Multi-photo upload UI
- [x] Camera integration
- [x] Gallery picker
- [x] File picker support
- [x] Upload progress indicator

### API Integration
- [x] `/api/auth/login/` - Authentication
- [x] `/api/albums/` - List albums with cover photos
- [x] `/api/albums/{id}/media/` - Get photos/videos
- [x] `/api/upload/` - Upload media
- [x] Pagination handling
- [x] Error handling

---

## 🔄 Phase 2: Essential Features (IN PROGRESS)

### Priority: HIGH - Album Management
- [ ] **Create Album** 
  - Endpoint: `POST /api/albums/`
  - Fields: title, description, is_public, category
  - UI: FAB button on albums screen → bottom sheet form
  
- [ ] **Edit Album**
  - Endpoint: `PUT /api/albums/{id}/`
  - Fields: title, description, is_public, category
  - UI: Long-press album → edit option in menu
  
- [ ] **Delete Album**
  - Endpoint: `DELETE /api/albums/{id}/`
  - UI: Long-press → delete with confirmation dialog
  
- [ ] **Set Album Cover**
  - Endpoint: Custom action or update album
  - UI: Long-press photo in album → "Set as cover"

### Priority: HIGH - Media Management
- [ ] **Delete Photo/Video**
  - Endpoint: `DELETE /api/photos/{id}/` or `/api/videos/{id}/`
  - UI: Long-press in grid → delete option
  
- [ ] **Edit Photo Metadata**
  - Endpoint: `PUT /api/photos/{id}/`
  - Fields: title, description, tags
  - UI: Info button in detail view → edit mode
  
- [ ] **Download Photo**
  - Use image URL from API
  - Save to device gallery/downloads
  - UI: Download button in detail view
  
- [ ] **Bulk Operations**
  - Multi-select mode (checkbox overlay on grid)
  - Bulk delete, bulk move to album
  - UI: Long-press to enter select mode

### Priority: MEDIUM - Search & Discovery
- [ ] **Search Photos**
  - Endpoint: `/api/albums/` with search params
  - Search by title, description, AI description
  - UI: Search bar in app bar
  
- [ ] **Filter Albums**
  - Filter by: public/private, category, shared
  - UI: Filter button → bottom sheet with options
  
- [ ] **Sort Options**
  - Sort by: date, title, custom order
  - UI: Sort button in app bar

### Priority: MEDIUM - Categories
- [ ] **View Categories**
  - Endpoint: `/api/categories/`
  - Display category list
  
- [ ] **Create Category**
  - Endpoint: `POST /api/categories/`
  - UI: In album create/edit form
  
- [ ] **Filter by Category**
  - Show albums in specific category
  - UI: Category chips/tabs

---

## 📋 Phase 3: Advanced Features (PLANNED)

### AI Features
- [ ] Display AI-generated descriptions on photos
- [ ] Search by AI content
- [ ] View AI confidence scores
- [ ] Trigger AI analysis on demand

### User Profile
- [ ] View user profile
- [ ] Edit profile (name, email)
- [ ] Change password
- [ ] Account settings
- [ ] Storage usage statistics

### Sharing & Collaboration
- [ ] Share album with specific users
  - Endpoint: `/api/albums/{id}/toggle_viewer/`
- [ ] Manage album viewers list
- [ ] Generate share links
- [ ] View "Shared with me" albums separately

### Enhanced Viewing
- [ ] Slideshow mode
- [ ] Adjustable grid size (2/3/4 columns)
- [ ] Group photos by date
- [ ] Timeline view
- [ ] Map view (if GPS metadata available)

---

## 📋 Phase 4: Polish & Extras (FUTURE)

### Media Features
- [ ] Video player integration (video_player package)
- [ ] Video playback controls
- [ ] Video trimming/editing
- [ ] Photo editing (crop, rotate, filters)

### Offline & Performance
- [ ] Offline album caching
- [ ] Download entire albums
- [ ] Background sync
- [ ] Progressive image loading
- [ ] Lazy loading optimization

### UI/UX Enhancements
- [ ] Dark mode toggle
- [ ] Custom themes
- [ ] Smooth animations
- [ ] Pull-to-refresh everywhere
- [ ] Better empty states with illustrations
- [ ] Skeleton loading screens
- [ ] Haptic feedback

### Additional Features
- [ ] Favorites/starred photos
- [ ] Recently viewed
- [ ] Photo metadata viewer (EXIF)
- [ ] QR code album sharing
- [ ] Print/export options

---

## 🎨 UI/UX Design Guidelines

### Navigation Pattern
```
Bottom Navigation (4 tabs):
├── Albums (Home)
├── Search
├── Upload (or FAB)
└── Profile
```

### Screen Organization
- **Albums Screen**: Grid + FAB for create
- **Album Detail**: Grid + FAB for upload
- **Photo Detail**: Full screen + bottom app bar
- **Search**: Search bar + filter chips + results grid

### Interaction Patterns
- **Tap**: View/open
- **Long-press**: Enter selection mode or show context menu
- **Swipe**: Navigate between items
- **Pull-down**: Refresh
- **FAB**: Primary action for current screen
- **Bottom Sheet**: Secondary options/forms

### Component Guidelines
- Max 2 icons in top app bar (avoid clutter)
- Use chips for filters/tags
- Use cards for list items
- Use dialogs for confirmations
- Use snackbars for feedback

---

## 🔧 Technical Considerations

### State Management
- Current: StatefulWidget with setState
- Future: Consider Provider/Riverpod for complex state

### API Service
- Centralized in `api_service.dart`
- Token management via SharedPreferences
- Error handling with try/catch

### Models
- `Album` - album data with cover photo
- `Photo` - handles both photos and videos (has `isVideo` flag)
- `Owner` - user data for album owner

### Dependencies
```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0                    # API calls
  provider: ^6.1.0                # State management (if needed)
  shared_preferences: ^2.2.0      # Token storage
  cached_network_image: ^3.3.0    # Image caching
  photo_view: ^0.14.0             # Photo zoom
  image_picker: ^1.0.4            # Camera/gallery
  file_picker: ^6.0.0             # File selection
  video_player: ^2.8.0            # For Phase 4
```

---

## 📊 Progress Tracking

### Sprint 1: Album CRUD (Next Up)
**Goal**: Complete album management features
**Timeline**: 1 week
**Tasks**:
1. Create album UI + API integration
2. Edit album UI + API integration  
3. Delete album with confirmation
4. Set album cover photo

### Sprint 2: Media Management
**Goal**: Complete photo/video management
**Timeline**: 1 week
**Tasks**:
1. Delete media items
2. Edit photo metadata
3. Download functionality
4. Bulk selection mode

### Sprint 3: Search & Organization
**Goal**: Search, filter, and categorize
**Timeline**: 1 week
**Tasks**:
1. Search implementation
2. Filters and sorting
3. Category management
4. Tags display

---

## 🐛 Known Issues

- [ ] Sleep commands in terminal cause app crashes (not critical)
- [ ] Video playback not implemented (shows placeholder)
- [ ] No offline support
- [ ] No error retry mechanism for failed uploads

---

## 📝 Notes

### API Endpoints Reference
```
Authentication:
POST   /api/auth/login/          - Login with username/password
POST   /api/auth/register/       - Register new user
POST   /api/auth/token/          - Get auth token

Albums:
GET    /api/albums/              - List albums (with cover_photo)
POST   /api/albums/              - Create album
GET    /api/albums/{id}/         - Get album details
PUT    /api/albums/{id}/         - Update album
DELETE /api/albums/{id}/         - Delete album
GET    /api/albums/{id}/media/   - Get photos/videos (paginated)
POST   /api/albums/{id}/toggle_viewer/  - Add/remove viewer

Media:
POST   /api/upload/              - Upload photo/video (fields: file, album_id)
GET    /api/photos/{id}/         - Get photo details
PUT    /api/photos/{id}/         - Update photo
DELETE /api/photos/{id}/         - Delete photo

Categories:
GET    /api/categories/          - List categories
POST   /api/categories/          - Create category

User:
GET    /api/user/me/             - Current user info
```

### Response Format
- Paginated: `{"count": int, "next": url, "previous": url, "results": []}`
- Single item: `{...item fields...}`
- Error: `{"error": "message"}`

---

**Last Updated**: 2025-11-19
**Version**: 0.1.0
**Status**: Phase 1 Complete, Phase 2 Planning
