# Django Photo Album - AI Analysis Commands Reference

## 🤖 **AI Analysis Commands**

### **📸 Analyze Photos** 
**Command:** `python manage.py analyze_photos`

**Purpose:** Analyzes photos using local BLIP models to generate descriptions and searchable tags

**AI Technology:** 
- **Local Processing**: Uses BLIP (Bootstrapping Language-Image Pre-training) models
- **GPU Acceleration**: CUDA support for faster processing (~0.4 seconds per photo)
- **No External APIs**: All analysis happens locally on your server

**Options:**
- `--force` - Force regeneration for photos that already have AI descriptions
- `--album "Album Name"` - Process only photos from a specific album
- `--limit N` - Limit processing to N number of photos (useful for testing)

**Examples:**
```bash
# Analyze all unprocessed photos
python manage.py analyze_photos

# Analyze all photos (including already processed ones)
python manage.py analyze_photos --force

# Analyze only photos from "Family" album
python manage.py analyze_photos --album "Family"

# Test with just 10 photos
python manage.py analyze_photos --limit 10

# Reprocess photos in "Vacation" album
python manage.py analyze_photos --force --album "Vacation"
```

**What it does:**
- Generates AI descriptions (e.g., "a little boy sitting in a car seat")
- Extracts searchable tags (e.g., boy, people, car, sitting, water)
- Creates vector embeddings for semantic search
- Updates database with AI analysis results
- Skips orphaned records (database entries with missing files)

**Web Interface Alternative:**
- Access user-friendly processing at `/process-photos-ai/`
- Real-time progress indicators and album-scoped processing
- Requires Album Admin or Site Admin permissions
- Album admins have a configurable batch limit (default: 50 photos)
- Site admins have unlimited batch processing

---

### **🎬 Analyze Videos**
**Command:** `python manage.py analyze_videos`

**Purpose:** Analyzes video thumbnails using local BLIP models to generate descriptions and tags

**AI Technology:** 
- **Local Processing**: Uses same BLIP models as photo analysis
- **Thumbnail Analysis**: Processes video thumbnail images (not video frames)
- **GPU Acceleration**: CUDA support for faster processing

**Options:**
- `--force` - Force regeneration for videos that already have AI descriptions
- `--album "Album Name"` - Process only videos from a specific album
- `--limit N` - Limit processing to N number of videos

**Examples:**
```bash
# Analyze all unprocessed videos
python manage.py analyze_videos

# Analyze all videos (including already processed ones)
python manage.py analyze_videos --force

# Analyze only videos from "Events" album
python manage.py analyze_videos --album "Events"

# Test with just 5 videos
python manage.py analyze_videos --limit 5
```

**Prerequisites:**
- Videos must have thumbnails generated first
- Run `python manage.py generate_video_thumbnails` if needed
- Thumbnail files must exist in the media directory

**What it does:**
- Analyzes video thumbnail images using BLIP model
- Generates descriptive text based on thumbnail content
- Extracts relevant tags for video searchability
- Skips videos with missing thumbnail files
- Updates database with AI analysis results

**Web Interface Alternative:**
- Access user-friendly processing at `/process-videos-ai/`
- Real-time progress indicators and album-scoped processing  
- Requires Album Admin permissions

---

## 🌐 **Web-Based AI Processing Interfaces**

### **📸 Photo AI Processing Interface**
**URL:** `/process-photos-ai/`

**Purpose:** User-friendly web interface for AI photo processing with real-time feedback

**Features:**
- **Album-Scoped Processing**: Only shows albums you can access
- **Real-time Statistics**: Live counts of photos needing analysis
- **Processing Options**: Force regeneration, album selection, limits
- **Progress Modals**: Real-time feedback during processing operations
- **Orphaned Record Detection**: Automatically excludes records with missing files

**Access Requirements:**
- Must be logged in as Album Admin or Site Admin
- Album Admins can only process their own albums
- Site Admins can process any album system-wide

**Interface Elements:**
- **Statistics Cards**: Show processable photos by album with modern dark theme
- **Album Dropdown**: Filtered list of albums you can access  
- **Processing Options**: Force regeneration checkbox, limit input field
- **Progress Modal**: Loading indicators and real-time status updates

### **🎬 Video AI Processing Interface** 
**URL:** `/process-videos-ai/`

**Purpose:** User-friendly web interface for AI video processing with consistent design

**Features:**
- **Matching Design**: Consistent with photo processing interface
- **Album-Scoped Processing**: Same permission model as photos
- **Thumbnail Validation**: Checks for existing video thumbnails
- **Progress Feedback**: Real-time processing status and completion reports

**Prerequisites:**
- Video thumbnails must exist (run `python manage.py generate_video_thumbnails`)
- Album Admin or Site Admin permissions required

**Permission Model:**
- **Album Admins**: Can only process albums they own or have viewer access to
  - Limited by configurable batch size (default: 50 photos per request)
  - Limit can be adjusted in Django Admin → AI Processing Settings
- **Site Admins**: Can process any album in the system
  - No batch size limits
- **Validation**: POST requests verify album ownership before processing
- **Error Handling**: Clear messages for permission violations

---

### **🔍 Generate Embeddings**
**Command:** `python manage.py generate_embeddings`

**Purpose:** Generates vector embeddings for semantic search functionality

**Options:**
- `--force` - Force regeneration of embeddings for all photos

**Examples:**
```bash
# Generate embeddings for photos without them
python manage.py generate_embeddings

# Regenerate all embeddings
python manage.py generate_embeddings --force
```

**What it does:**
- Creates vector representations of images for similarity search
- Enables "find similar photos" functionality
- Required for advanced semantic search features

---

## 🖼️ **Media Processing Commands**

### **📷 Generate Photo Thumbnails**
**Command:** `python manage.py generate_thumbnails`

**Purpose:** Creates thumbnail images for photos

**Examples:**
```bash
# Generate missing thumbnails
python manage.py generate_thumbnails

# Regenerate all thumbnails
python manage.py regenerate_thumbnails
```

---

### **🎥 Generate Video Thumbnails**
**Command:** `python manage.py generate_video_thumbnails`

**Purpose:** Creates thumbnail images from video files

**Examples:**
```bash
# Generate missing video thumbnails
python manage.py generate_video_thumbnails
```

**Note:** Required before running `analyze_videos`

---

## 🚀 **Recommended Workflow**

### **For New Photo Album Setup:**
```bash
# 1. Generate photo thumbnails (if needed)
python manage.py generate_thumbnails

# 2. Generate video thumbnails (if needed)
python manage.py generate_video_thumbnails

# 3. Analyze photos with AI
python manage.py analyze_photos

# 4. Analyze videos with AI
python manage.py analyze_videos

# 5. Generate embeddings for semantic search
python manage.py generate_embeddings
```

### **For Testing AI Features:**
```bash
# Test with small batches first
python manage.py analyze_photos --limit 5
python manage.py analyze_videos --limit 3
```

### **For Specific Albums:**
```bash
# Process only specific albums
python manage.py analyze_photos --album "Family Photos"
python manage.py analyze_videos --album "Vacation Videos"
```

### **For Reprocessing Everything:**
```bash
# Force reanalysis of all media
python manage.py analyze_photos --force
python manage.py analyze_videos --force
python manage.py generate_embeddings --force
```

---

## 🔍 **Search Features Enabled**

After running AI analysis, you can search for:

**People & Objects:**
- "dog", "cat", "person", "child", "car", "tree"

**Activities:**
- "playing", "eating", "sitting", "running", "swimming"

**Locations & Scenes:**
- "outdoor", "indoor", "beach", "garden", "room", "kitchen"

**Emotions & Situations:**
- "happy", "group", "family", "party", "celebration"

---

## ⚡ **Performance Tips**

**For Large Photo Collections:**
1. **Start small**: Use `--limit 10` to test first
2. **Process during off-hours**: AI analysis can be CPU-intensive
3. **Album-by-album**: Use `--album` to process specific collections
4. **Monitor progress**: Commands show real-time progress and timing

**Time Estimates:**
- **Photos**: ~1-3 seconds per photo (after initial model loading)
- **Videos**: ~2-5 seconds per video (analyzing thumbnails)
- **Embeddings**: ~0.5-1 second per photo

**First Run Note:**
- Initial AI model download may take time (~500MB-1GB)
- Models are cached locally for faster subsequent runs

---

## 🐛 **Troubleshooting**

**If analysis fails:**
```bash
# Check AI service availability
python manage.py shell -c "from album.services.ai_analysis_service import is_ai_analysis_available; print(is_ai_analysis_available())"

# Check for missing thumbnails
python manage.py generate_thumbnails
python manage.py generate_video_thumbnails
```

**Common Issues:**
- **Missing thumbnails**: Run thumbnail generation commands first
- **Memory issues**: Use `--limit` for smaller batches
- **No results**: Check that files exist and aren't corrupted

---

## 🎯 **Web Interface Alternative**

For videos, you can also use the web interface:
- **URL**: `/process-videos-ai/` (admin access required)
- **Features**: Same options as command line but with GUI
- **Benefits**: Progress feedback, statistics, easier parameter selection

---

This documentation covers all the AI analysis and media processing commands available in your Django Photo Album application. The AI features will make your photos and videos much more searchable and organized!