#!/bin/bash
# Safe File Cleanup Script
# Removes confirmed unused files with backup

set -e

BACKUP_DIR="/tmp/photo_album_cleanup_$(date +%Y%m%d_%H%M%S)"
PROJECT_DIR="photo_album"

echo "🧹 Photo Album Project Cleanup"
echo "=============================="
echo ""

# Create backup directory
mkdir -p "$BACKUP_DIR"
echo "📦 Created backup directory: $BACKUP_DIR"
echo ""

cd "$PROJECT_DIR"

# Files to delete (confirmed safe)
FILES_TO_DELETE=(
    "album/views_old.py"           # Old views file - not imported anywhere
    "test_messages.py"             # Root-level test file
    "console.txt"                  # Old console output
    "errors.txt"                   # Old error log
    "docker-build.log"             # Temporary build log
    "data.json"                    # Data dump (801 KB)
    "fix_photo.sql"                # One-time SQL fix
)

# Backup files before deletion
echo "📋 Files to be deleted:"
TOTAL_SIZE=0
for file in "${FILES_TO_DELETE[@]}"; do
    if [ -f "$file" ]; then
        SIZE=$(du -h "$file" | cut -f1)
        TOTAL_SIZE=$((TOTAL_SIZE + $(du -b "$file" | cut -f1)))
        echo "  ✓ $file ($SIZE)"
        
        # Create backup
        cp --parents "$file" "$BACKUP_DIR/" 2>/dev/null || true
    else
        echo "  ⊗ $file (not found - skipping)"
    fi
done

echo ""
echo "💾 Total size to free: $(numfmt --to=iec $TOTAL_SIZE)"
echo ""

# Ask for confirmation
read -p "❓ Proceed with deletion? (y/N) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🗑️  Deleting files..."
    
    for file in "${FILES_TO_DELETE[@]}"; do
        if [ -f "$file" ]; then
            rm "$file"
            echo "  ✓ Deleted: $file"
        fi
    done
    
    echo ""
    echo "✅ Cleanup complete!"
    echo ""
    echo "📦 Backup saved to: $BACKUP_DIR"
    echo "   (You can delete this backup folder after verifying everything works)"
    echo ""
    echo "🧪 Test your application:"
    echo "   docker-compose exec web python manage.py check"
    echo ""
else
    echo ""
    echo "❌ Cleanup cancelled - no files deleted"
    rm -rf "$BACKUP_DIR"
fi
