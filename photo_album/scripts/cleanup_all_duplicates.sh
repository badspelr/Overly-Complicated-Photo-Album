#!/bin/bash
# Script to remove duplicate photos and videos from all albums on production server
# This script should be run on the production server after pulling latest code from GitHub
#
# Usage:
#   ./scripts/cleanup_all_duplicates.sh --dry-run    # Preview what would be deleted
#   ./scripts/cleanup_all_duplicates.sh              # Actually delete duplicates

set -e  # Exit on error

echo "=================================="
echo "Duplicate Photo/Video Cleanup"
echo "=================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo -e "${RED}Error: manage.py not found. Please run this script from the Django project root.${NC}"
    exit 1
fi

# Detect if running in Docker or direct Python
if command -v docker &> /dev/null && docker ps | grep -q photo_album_web; then
    PYTHON_CMD="docker exec photo_album_web python"
    echo "Using Docker container: photo_album_web"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    echo "Using local Python"
else
    echo -e "${RED}Error: Neither Docker container nor Python found.${NC}"
    exit 1
fi
echo ""

# Check if dry-run mode
DRY_RUN=""
if [ "$1" == "--dry-run" ] || [ "$1" == "-d" ]; then
    DRY_RUN="--dry-run"
    echo -e "${YELLOW}Running in DRY-RUN mode (no changes will be made)${NC}"
    echo ""
fi

# Get all users and their albums
echo "Finding all users and albums..."
echo ""

# Run Python code to get albums
USER_ALBUMS=$($PYTHON_CMD manage.py shell -c "
from album.models import Album
from django.db.models import Count

albums = Album.objects.annotate(photo_count=Count('photos')).filter(photo_count__gte=2).select_related('owner')
for album in albums:
    print(f'{album.owner.username}|{album.title}|{album.photo_count}')
" 2>&1 | grep '|' || true)

if [ -z "$USER_ALBUMS" ]; then
    echo -e "${YELLOW}No albums found with 2 or more photos.${NC}"
    echo ""
    echo "Either:"
    echo "  - All albums have been cleaned already"
    echo "  - Albums only have 1 photo (no possibility of duplicates)"
    echo "  - No albums exist in the system"
    echo ""
    exit 0
fi

echo -e "${GREEN}Found albums to process:${NC}"
echo "$USER_ALBUMS" | while IFS='|' read -r username album_title photo_count; do
    echo "  - $album_title (Owner: $username, Photos: $photo_count)"
done
echo ""

# Ask for confirmation if not in dry-run mode
if [ -z "$DRY_RUN" ]; then
    echo -e "${YELLOW}WARNING: This will permanently delete duplicate photos!${NC}"
    echo -e "${YELLOW}It is recommended to run with --dry-run first to see what would be deleted.${NC}"
    echo ""
    read -p "Are you sure you want to continue? (yes/no): " -r confirm
    if [ "$confirm" != "yes" ]; then
        echo "Cancelled."
        exit 0
    fi
    echo ""
fi

# Process each album
echo "Processing albums..."
echo ""

echo "$USER_ALBUMS" | while IFS='|' read -r username album_title photo_count; do
    echo "=================================="
    echo "Album: $album_title"
    echo "Owner: $username"
    echo "Photos: $photo_count"
    echo "=================================="
    
    # Run the remove_duplicates command
    if [ -n "$DRY_RUN" ]; then
        $PYTHON_CMD manage.py remove_duplicates --username "$username" --album "$album_title" --dry-run 2>&1 | head -n 100
    else
        $PYTHON_CMD manage.py remove_duplicates --username "$username" --album "$album_title" 2>&1 | tail -n 20
    fi
    
    echo ""
done

echo "=================================="
echo "Cleanup Complete!"
echo "=================================="

if [ -n "$DRY_RUN" ]; then
    echo -e "${YELLOW}This was a DRY-RUN. No changes were made.${NC}"
    echo -e "${YELLOW}Run without --dry-run to actually delete duplicates.${NC}"
fi
