# Django Photo Album - User Manual

> **📌 Note**: This is the Markdown version of the user manual for reference and offline reading. 
> For the most up-to-date and visually enhanced version, please visit the **in-app user manual** at `/user-manual/` when logged into the application.
> The HTML version includes:
> - 15 comprehensive sections with quick navigation
> - Visual styling and feature cards
> - Step-by-step guides with screenshots
> - Mobile-optimized layout
> - Search functionality

## 📚 Table of Contents

1. [Getting Started](#getting-started)
2. [Account Management](#account-management)
3. [Creating and Managing Albums](#creating-and-managing-albums)
4. [Uploading and Organizing Photos](#uploading-and-organizing-photos)
5. [Search and Discovery](#search-and-discovery)
6. [AI Features](#ai-features)
7. [Sharing and Collaboration](#sharing-and-collaboration)
8. [Advanced Features](#advanced-features)
9. [Troubleshooting](#troubleshooting)

## 🚀 Getting Started

### First Login
1. Navigate to your Django Photo Album instance (e.g., `http://localhost:8000`)
2. Click **Login** or **Register** if you need to create an account
3. Enter your credentials and click **Sign In**
4. You'll be taken to your dashboard showing your albums

### Dashboard Overview
The dashboard displays:
- **Your Albums**: Grid view of all your albums
- **Recent Activity**: Recently updated albums
- **Quick Actions**: Create new album, upload photos
- **Search Bar**: Global search across all your albums

## 👤 Account Management

### Profile Settings
Access your profile by clicking your username in the top navigation:
- **Change Password**: Update your account password
- **Profile Information**: View account details
- **Privacy Settings**: Control album visibility defaults

### Password Management
To change your password:
1. Click your username → **Change Password**
2. Enter your current password
3. Enter and confirm your new password
4. Click **Update Password**

## 📁 Creating and Managing Albums

### Creating a New Album

#### Quick Create
1. Click **+ New Album** on the dashboard
2. Enter album title and description
3. Set privacy (Public/Private)
4. Click **Create Album**

#### Detailed Setup
1. Choose **+ New Album** → **Advanced Options**
2. Fill in album details:
   - **Title**: Album name (required)
   - **Description**: Detailed description (optional)
   - **Category**: Assign to category (optional)
   - **Visibility**: Public or Private
   - **Viewers**: Add specific users who can view (Private albums only)
3. Click **Create and Upload Photos** or **Create Album**

### Album Settings
Access album settings by clicking the **⋮** menu on any album:

#### Basic Information
- **Edit Title/Description**: Update album metadata
- **Change Visibility**: Switch between Public/Private
- **Category Assignment**: Organize albums by category

#### Sharing Options
- **Create Share Link**: Generate public sharing URLs
- **Manage Viewers**: Add/remove users with viewing access
- **Share Settings**: Set expiration dates for share links

#### Advanced Options
- **Download Album**: Download all photos as ZIP
- **Delete Album**: Permanently remove album and all contents
- **Transfer Ownership**: Change album owner (admin only)

## 📸 Uploading and Organizing Photos

### Uploading Photos

#### Single Upload
1. Open an album
2. Click **+ Upload Photos**
3. Select photos from your device
4. Photos upload automatically with progress indicators

#### Bulk Upload
1. Select multiple photos (Ctrl/Cmd + Click)
2. Drag and drop onto the album area
3. Monitor upload progress
4. AI analysis begins automatically after upload

#### Supported Formats
- **Photos**: JPEG, PNG, GIF, WebP
- **Videos**: MP4, MOV, AVI, WebM
- **Max Size**: 50MB per file (configurable)

### Photo Management

#### Individual Photo Actions
Click any photo to access:
- **View Full Size**: Modal viewer with zoom
- **Download**: Save photo to device
- **Edit Details**: Update title, description, category
- **Delete**: Remove from album
- **Copy Link**: Get direct photo URL

#### Bulk Operations
1. Select multiple photos using checkboxes
2. Choose bulk action:
   - **Download Selected**: ZIP download of selected photos
   - **Delete Selected**: Remove multiple photos
   - **Move to Category**: Assign category to multiple photos
   - **Add Tags**: Bulk tag assignment

### Organization Features

#### Categories
Create and manage photo categories:
1. Go to **Categories** in album settings
2. Click **+ New Category**
3. Enter category name and color
4. Assign photos to categories via bulk operations or individual editing

#### Custom Albums (Virtual Collections)
Custom Albums are like playlists for your photos and videos - they let you create virtual collections from photos across different regular albums without moving or duplicating files.

**Understanding the Difference:**
- **Regular Albums** = Physical photo albums (photos belong to one album)
- **Custom Albums** = Virtual playlists (photos can appear in multiple custom albums)

**Creating Custom Albums:**
1. Go to your dashboard or custom albums page
2. Click **+ New Custom Album**
3. Enter a title and description
4. Click **Create**

**Adding Photos to Custom Albums:**
1. Open any photo or video in edit mode
2. Find the **Custom Albums** dropdown field
3. Select one or more custom albums to add the media to
4. Click **Save**

**Use Cases:**
- Create a "Best of 2024" custom album with favorite photos from multiple regular albums
- Organize a "Family Memories" collection with family photos from vacation, holiday, and birthday albums
- Build a "Nature Photography" collection gathering nature shots from various trips
- Assemble a "Year in Review" showcasing highlights from the entire year

**Key Features:**
- Photos stay in their original albums
- One photo can appear in unlimited custom albums
- Each user can only see and manage their own custom albums
- Deleting from a custom album doesn't delete the original photo
- Perfect for creating themed collections without reorganizing your main albums

#### Sorting Options
Access via the sort dropdown in any album:
- **Date Taken** (Newest/Oldest)
- **Date Added** (Newest/Oldest)
- **Title** (A-Z, Z-A)
- **File Size** (Largest/Smallest)

#### Filtering
Use the filter bar to narrow your view:
- **Media Type**: Photos, Videos, or All
- **Category**: Filter by assigned categories
- **Date Range**: Show photos from specific time periods
- **AI Status**: Show only AI-processed photos

## 🔍 Search and Discovery

### Search Types

#### Text Search (Traditional)
- Searches photo titles, descriptions, and manual tags
- Supports partial matches and wildcards
- Best for finding photos with known names or descriptions
- Example: "vacation 2023", "birthday party", "beach"

#### AI Search (Intelligent)
- Uses artificial intelligence to understand photo and video content
- Searches AI-generated descriptions and tags
- Understands concepts and context
- Example: "people swimming", "sunset over water", "dogs playing"

### Using Search

#### Quick Search
1. Enter search terms in the search bar
2. Select **Text Search** or **AI Search**
3. Press Enter or click the search icon
4. Results appear with relevance scoring

#### Advanced Search
Access advanced search options:
1. Click the **🔍** icon next to search
2. Set additional filters:
   - **Date Range**: Specific time periods
   - **Album**: Search within specific albums
   - **Media Type**: Photos only, videos only
   - **Category**: Limit to categories
   - **AI Confidence**: Minimum AI confidence score

### Search Results

#### Understanding Results
- **Relevance Score**: How well the photo matches your search
- **Highlighted Matches**: Search terms highlighted in descriptions
- **Context Snippets**: Why the photo matched your search
- **Similarity Ranking**: Most relevant photos appear first

#### Result Actions
From search results you can:
- **View Photo**: Click to open full-size view
- **Go to Album**: Navigate to the photo's album
- **Quick Download**: Download without leaving search
- **Add to Collection**: Save to personal collections

### Search Tips

#### For Best Text Search Results
- Use specific keywords from photo titles or descriptions
- Try different variations of words
- Use quotes for exact phrases: `"family reunion"`
- Combine multiple terms: `vacation beach 2023`

#### For Best AI Search Results
- Describe what you see in the photo
- Use natural language: `children playing in a park`
- Try different descriptions: `dog` vs `puppy` vs `pet`
- Include context: `wedding ceremony` vs just `wedding`

## 🤖 AI Features

### Automatic AI Analysis

#### What AI Analyzes
The system uses local BLIP (Bootstrapping Language-Image Pre-training) models to analyze your media:
- **Generates Descriptions**: Natural language description of photo/video content
- **Extracts Tags**: Relevant keywords and categories automatically
- **Identifies Objects**: People, animals, vehicles, buildings, activities
- **Understands Scenes**: Indoor/outdoor settings, events, contexts
- **Processes Locally**: All analysis happens on your server with GPU acceleration

#### AI Processing Requirements
- **For Photos**: Valid image files (JPG, PNG, etc.) with existing file paths
- **For Videos**: Video thumbnails must be generated first using `python manage.py generate_video_thumbnails`
- **Permissions**: Album Admin access to the albums you want to process
- **Hardware**: GPU recommended for faster processing (~0.4 seconds per photo)

### Web-Based AI Processing

#### Photo AI Processing
Access photo AI processing at `/process-photos-ai/`:

1. **Navigate to Processing Page**: Visit the AI photo processing interface
2. **Review Statistics**: See counts of photos needing analysis by album
3. **Select Processing Options**:
   - **Album**: Choose specific album or process all accessible albums
   - **Force Regeneration**: Reprocess photos that already have AI descriptions
   - **Limit**: Set maximum number of photos to process (useful for testing)
4. **Start Processing**: Click "Start AI Analysis" button
5. **Monitor Progress**: Real-time progress modal shows processing status
6. **Review Results**: Success/error messages with processing statistics

#### Video AI Processing
Access video AI processing at `/process-videos-ai/`:

1. **Navigate to Processing Page**: Visit the AI video processing interface
2. **Review Statistics**: See counts of videos needing analysis by album  
3. **Select Processing Options**:
   - **Album**: Choose specific album or process all accessible albums
   - **Force Regeneration**: Reprocess videos that already have AI descriptions
   - **Limit**: Set maximum number of videos to process
4. **Start Processing**: Click "Start AI Analysis" button
5. **Monitor Progress**: Real-time progress modal with status updates
6. **Review Results**: Detailed feedback on processing completion

### Permission Model

#### Album Admin Access
- **Album Admins** can only process AI for albums they own or have viewer access to
- **Album Admins** are limited by a configurable batch size (default: 50 photos/videos per batch)
- **Site Admins** can process AI for any album system-wide with no batch limits
- **Regular Users** cannot access AI processing interfaces

**Note**: The album admin batch limit can be adjusted by site administrators in Django Admin → AI Processing Settings → Album admin processing limit.

#### Album-Scoped Processing
The system enforces strict album-level permissions:
- Album dropdown only shows albums you can access
- Statistics are filtered to your accessible albums
- Processing requests validate album ownership before execution
- Clear error messages for unauthorized access attempts

### AI-Generated Content

#### Viewing AI Data
For any photo or video, you can see:
- **AI Description**: Natural language description of content (e.g., "a little boy sitting in a car seat")
- **AI Tags**: Automatically extracted keywords (e.g., boy, people, car, sitting)
- **Processing Status**: Whether AI analysis has been completed
- **File Status**: Indicates if media file exists or is orphaned

#### Editing AI Content
You can modify AI-generated content:
1. Click **Edit** on any photo or video
2. Update AI description text
3. Modify or add to AI-generated tags
4. Add manual tags alongside AI tags
5. Save changes to preserve your customizations

### Advanced Features

#### Orphaned Record Handling
The system intelligently handles database inconsistencies:
- **Detection**: Automatically identifies records with missing media files
- **Statistics**: Excludes orphaned records from processing counts
- **Processing**: Skips orphaned records during AI analysis
- **User Feedback**: Clear messages about skipped files

#### Processing Progress
Enhanced user experience during AI operations:
- **Real-time Modals**: Processing progress with loading indicators
- **Status Updates**: Live feedback during analysis operations  
- **Completion Reports**: Detailed success/error statistics
- **Time Estimates**: Processing duration and average time per item

#### Performance Optimization
- **GPU Acceleration**: Local BLIP models utilize CUDA when available
- **Batch Processing**: Efficient handling of multiple media items
- **Smart Filtering**: Only processes items that need analysis
- **Background Processing**: Non-blocking user interface during operations

## 🔗 Sharing and Collaboration

### Album Sharing

#### Public Albums
Make albums publicly accessible:
1. Edit album settings
2. Set **Visibility** to **Public**
3. Share the album URL with anyone
4. Public albums appear in search engines (if enabled)

#### Private Sharing
Share private albums with specific people:
1. Keep album **Private**
2. Add **Viewers** by username or email
3. Viewers get access notifications
4. Manage viewer list anytime

### Share Links

#### Creating Share Links
Generate temporary sharing URLs:
1. Open album settings
2. Click **Create Share Link**
3. Set options:
   - **Expiration Date**: When link expires
   - **Password Protection**: Optional password
   - **Download Permissions**: Allow/disallow downloads
   - **View Count Limit**: Maximum number of views

#### Managing Share Links
Track and control your share links:
- **Active Links**: See all active sharing URLs
- **Usage Statistics**: View count and access logs
- **Revoke Access**: Immediately disable links
- **Update Settings**: Change expiration or permissions

### Collaboration Features

#### Viewer Permissions
Control what viewers can do:
- **View Only**: See photos but cannot download
- **Download**: Can save photos to their device
- **Comment**: Add comments to photos (if enabled)
- **Upload**: Add photos to shared albums (if enabled)

#### Team Albums
For collaborative photo management:
1. Create album with **Team** visibility
2. Add team members as **Collaborators**
3. Set permission levels per member
4. Enable notifications for new uploads

## ⚙️ Advanced Features

### Keyboard Shortcuts

#### Navigation
- **↑/↓**: Navigate between photos
- **←/→**: Previous/next page
- **Esc**: Close modal or cancel action
- **Ctrl+F**: Focus search bar

#### Actions
- **Ctrl+A**: Select all photos
- **Ctrl+D**: Download selected
- **Delete**: Remove selected photos
- **Ctrl+Upload**: Open upload dialog

### URL Patterns

#### Direct Access
- **Album**: `/albums/{album_id}/`
- **Photo**: `/photos/{photo_id}/`
- **Search**: `/search/?q={query}&type={ai|text}`
- **Share Link**: `/share/{share_token}/`

#### API Access
For developers and integrations:
- **REST API**: `/api/v1/`
- **Album API**: `/api/v1/albums/`
- **Photo API**: `/api/v1/photos/`
- **Search API**: `/api/v1/search/`

### Performance Optimization

#### Large Albums
For albums with 1000+ photos:
- **Enable Lazy Loading**: Photos load as you scroll
- **Reduce Page Size**: Use 20-40 photos per page
- **Use Filters**: Narrow view with categories or dates
- **Background Processing**: AI analysis happens in background

#### Search Performance
Optimize search experience:
- **Use Specific Terms**: More specific = faster results
- **Limit Date Ranges**: Narrow search timeframes
- **Category Filters**: Search within categories
- **Cache Results**: Recent searches are cached

### Data Management

#### Export Options
Export your data:
- **Album Export**: Download all photos + metadata
- **Search Export**: Export search results
- **AI Data Export**: Export AI analysis results
- **EXIF Export**: Export photo metadata

#### Backup Strategies
Protect your photos:
- **Regular Downloads**: Download albums periodically
- **External Sync**: Sync with cloud storage
- **Database Backup**: Admin can backup metadata
- **Incremental Backup**: Only new/changed photos

## 🔧 Troubleshooting

### Common Issues

#### Upload Problems
**Photos won't upload:**
- Check file size (max 50MB per file)
- Verify file format (JPEG, PNG, GIF supported)
- Ensure stable internet connection
- Try uploading one file at a time

**Upload is slow:**
- Large files take time to upload
- Multiple files upload in parallel (may appear slow)
- Check your internet upload speed
- Consider resizing very large photos

#### Search Issues
**AI search returns no results:**
- Wait for AI processing to complete
- Try different search terms
- Check AI processing status in photo details
- Use text search as fallback

**Search is slow:**
- Large albums may take longer to search
- AI search is slower than text search
- Use filters to narrow search scope
- Contact admin if consistently slow

#### Display Problems
**Photos not loading:**
- Refresh the page
- Check internet connection
- Clear browser cache
- Try a different browser

**Layout issues:**
- Refresh the page
- Check browser compatibility
- Disable browser extensions
- Try incognito/private mode

### Getting Help

#### Self-Service
- **Help Documentation**: This manual and online docs
- **FAQ Section**: Common questions and answers
- **Video Tutorials**: Step-by-step video guides
- **Community Forum**: User community discussions

#### Support Channels
- **Email Support**: Contact administrator
- **Bug Reports**: Report issues via admin panel
- **Feature Requests**: Suggest improvements
- **Documentation**: Contribute to user guides

### Error Messages

#### Understanding Errors
- **Upload Failed**: File format or size issue
- **Access Denied**: Permission problem
- **Search Error**: Search service unavailable
- **AI Processing Failed**: AI analysis error

#### Recovery Steps
1. **Refresh the page** - Often resolves temporary issues
2. **Check permissions** - Ensure you have access rights
3. **Try again later** - Service may be temporarily unavailable
4. **Contact support** - If problem persists

## 📱 Mobile Usage

### Mobile Interface
The mobile version provides:
- **Touch-Optimized**: Large touch targets
- **Responsive Design**: Adapts to screen size
- **Swipe Navigation**: Swipe between photos
- **Mobile Upload**: Camera integration

### Mobile-Specific Features
- **Camera Integration**: Upload directly from camera
- **GPS Location**: Automatic location tagging
- **Offline Viewing**: View recently accessed photos offline
- **Push Notifications**: Upload completion alerts

### Mobile Tips
- **Single File Downloads**: Mobile downloads one file at a time
- **Landscape Mode**: Better viewing for wide photos
- **Pinch to Zoom**: Zoom into photo details
- **Share Integration**: Use device sharing features

---

## 💡 Pro Tips

1. **Use AI Search for Discovery**: Find photos you forgot you had
2. **Organize with Categories**: Create meaningful photo groups
3. **Batch Upload**: Upload multiple photos at once for efficiency
4. **Regular Backups**: Download important albums periodically
5. **Share Strategically**: Use expiring links for temporary sharing
6. **Monitor AI Processing**: Check that new photos are being analyzed
7. **Use Keyboard Shortcuts**: Speed up navigation and actions
8. **Filter Before Search**: Narrow scope for faster results

This user manual covers all aspects of using Django Photo Album effectively. For technical support or advanced configuration, consult your system administrator.