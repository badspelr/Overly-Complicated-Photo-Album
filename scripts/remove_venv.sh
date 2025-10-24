#!/bin/bash

# Photo Album - Virtual Environment Cleanup Script
# This script removes Python virtual environments (redundant in Docker)
# and updates documentation to emphasize Docker-first approach

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Virtual Environment Cleanup ===${NC}\n"

# Step 1: Check for virtual environment directories
echo -e "${YELLOW}Step 1: Checking for virtual environment directories...${NC}"

VENV_FOUND=0

if [ -d "venv" ]; then
    echo -e "  Found: ${YELLOW}venv/${NC}"
    VENV_FOUND=1
fi

if [ -d "env" ]; then
    echo -e "  Found: ${YELLOW}env/${NC}"
    VENV_FOUND=1
fi

if [ -d ".venv" ]; then
    echo -e "  Found: ${YELLOW}.venv/${NC}"
    VENV_FOUND=1
fi

if [ $VENV_FOUND -eq 0 ]; then
    echo -e "  ${GREEN}✓ No virtual environment directories found${NC}"
else
    read -p "Remove these virtual environment directories? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv/ env/ .venv/
        echo -e "  ${GREEN}✓ Virtual environment directories removed${NC}"
    else
        echo -e "  ${YELLOW}⚠ Skipped removal${NC}"
    fi
fi

echo ""

# Step 2: Check for venv-related files
echo -e "${YELLOW}Step 2: Checking for venv-related files...${NC}"

if [ -f "activate_venv.sh" ]; then
    echo -e "  Found: ${YELLOW}activate_venv.sh${NC}"
    rm -f activate_venv.sh
    echo -e "  ${GREEN}✓ Removed activate_venv.sh${NC}"
fi

if [ -f ".python-version" ]; then
    echo -e "  Found: ${YELLOW}.python-version${NC}"
    read -p "Remove .python-version? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -f .python-version
        echo -e "  ${GREEN}✓ Removed .python-version${NC}"
    else
        echo -e "  ${YELLOW}⚠ Kept .python-version${NC}"
    fi
fi

echo -e "  ${GREEN}✓ File cleanup complete${NC}\n"

# Step 3: Search for venv references in scripts
echo -e "${YELLOW}Step 3: Searching for venv references in scripts...${NC}"

VENV_REFS=$(grep -r "source.*venv" . --include="*.sh" 2>/dev/null || true)

if [ -n "$VENV_REFS" ]; then
    echo -e "${YELLOW}Found venv activation references in shell scripts:${NC}"
    echo "$VENV_REFS"
    echo ""
    echo -e "${YELLOW}Please review and update these scripts manually${NC}"
else
    echo -e "  ${GREEN}✓ No venv references in shell scripts${NC}"
fi

echo ""

# Step 4: Create backup of files we'll modify
echo -e "${YELLOW}Step 4: Creating backups of documentation...${NC}"

mkdir -p .cleanup_backups

FILES_TO_BACKUP=("README.md" "docs/getting-started/QUICK_START.md")

for file in "${FILES_TO_BACKUP[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" ".cleanup_backups/$(basename $file).backup"
        echo -e "  ${GREEN}✓ Backed up: $file${NC}"
    fi
done

echo ""

# Step 5: Summary
echo -e "${BLUE}=== Summary ===${NC}\n"

echo "Cleanup completed! Here's what was done:"
echo ""
echo "✓ Removed virtual environment directories (if found)"
echo "✓ Removed venv-related files"
echo "✓ Created backups in .cleanup_backups/"
echo ""
echo -e "${GREEN}Next steps:${NC}"
echo "1. Review changes with: git status"
echo "2. Update documentation to emphasize Docker (see suggestions below)"
echo "3. Test Docker setup: docker-compose -f docker-compose.light.yml up -d"
echo "4. Commit changes: git add . && git commit -m 'Remove redundant virtual environment'"
echo ""
echo -e "${YELLOW}Documentation Update Suggestions:${NC}"
echo ""
echo "Update README.md to say:"
echo "  'Quick Start (Docker - Recommended) - No virtual environment needed!'"
echo ""
echo "Update installation guides to emphasize:"
echo "  'Docker provides complete isolation - venv not required'"
echo ""
echo -e "${BLUE}Why Docker eliminates the need for venv:${NC}"
echo "  • Complete filesystem isolation"
echo "  • Separate Python installation per container"
echo "  • No dependency conflicts between projects"
echo "  • Matches production environment exactly"
echo ""
echo -e "${GREEN}Cleanup complete!${NC}"
