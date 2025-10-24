#!/bin/bash

# =============================================================================
# Security Check Script for Dev Branch
# =============================================================================
# This script checks for potential secrets before pushing to GitHub
# Usage: ./scripts/check-secrets.sh
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}  Security Check for Dev Branch${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}❌ Not a git repository${NC}"
    exit 1
fi

# Check current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo -e "${BLUE}📍 Current branch: ${YELLOW}${CURRENT_BRANCH}${NC}"
echo ""

# Initialize counters
WARNINGS=0
ERRORS=0

# =============================================================================
# 1. Check if .env files are tracked
# =============================================================================
echo -e "${BLUE}🔍 Checking for tracked .env files...${NC}"
# .env.production and .env.example are safe (templates with placeholders)
# .env and .env.local should NEVER be tracked (contain real secrets)
TRACKED_ENV=$(git ls-files | grep -E "^\.env$|^\.env\.local$" || true)

if [ -n "$TRACKED_ENV" ]; then
    echo -e "${RED}❌ ERROR: Real .env files are tracked in git!${NC}"
    echo "$TRACKED_ENV"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ No real .env files tracked${NC}"
fi

# Check if templates exist (these are safe)
TRACKED_TEMPLATES=$(git ls-files | grep -E "^\.env\.(production|example)$" || true)
if [ -n "$TRACKED_TEMPLATES" ]; then
    echo -e "${GREEN}✅ Template files tracked (safe): .env.production, .env.example${NC}"
fi
echo ""

# =============================================================================
# 2. Check for common secret patterns in staged files
# =============================================================================
echo -e "${BLUE}🔍 Checking staged files for secrets...${NC}"

# Get staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(py|sh|yml|yaml|conf|cfg|ini|json)$' || true)

if [ -n "$STAGED_FILES" ]; then
    for file in $STAGED_FILES; do
        # Check for password patterns
        if git diff --cached "$file" | grep -iE "(password|passwd|pwd).*=.*['\"].*['\"]" | grep -v ".env.example" | grep -v "# Example:" | grep -v "your-password" > /dev/null 2>&1; then
            echo -e "${RED}⚠️  WARNING: Possible password in $file${NC}"
            WARNINGS=$((WARNINGS + 1))
        fi
        
        # Check for secret key patterns
        if git diff --cached "$file" | grep -iE "secret_key.*=.*['\"][^'\"]{20,}['\"]" | grep -v ".env.example" > /dev/null 2>&1; then
            echo -e "${RED}⚠️  WARNING: Possible secret key in $file${NC}"
            WARNINGS=$((WARNINGS + 1))
        fi
        
        # Check for API key patterns
        if git diff --cached "$file" | grep -E "(api[_-]?key|apikey).*['\"][a-zA-Z0-9]{20,}['\"]" > /dev/null 2>&1; then
            echo -e "${RED}⚠️  WARNING: Possible API key in $file${NC}"
            WARNINGS=$((WARNINGS + 1))
        fi
        
        # Check for AWS keys
        if git diff --cached "$file" | grep -E "AKIA[0-9A-Z]{16}" > /dev/null 2>&1; then
            echo -e "${RED}❌ ERROR: AWS Access Key found in $file${NC}"
            ERRORS=$((ERRORS + 1))
        fi
        
        # Check for private keys
        if git diff --cached "$file" | grep -E "BEGIN.*PRIVATE KEY" > /dev/null 2>&1; then
            echo -e "${RED}❌ ERROR: Private key found in $file${NC}"
            ERRORS=$((ERRORS + 1))
        fi
    done
fi

if [ $WARNINGS -eq 0 ] && [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ No obvious secrets found in staged files${NC}"
fi
echo ""

# =============================================================================
# 3. Check for hardcoded IPs or domains
# =============================================================================
echo -e "${BLUE}🔍 Checking for hardcoded IPs/domains...${NC}"

if [ -n "$STAGED_FILES" ]; then
    for file in $STAGED_FILES; do
        # Skip checks for certain files
        if [[ "$file" == *"test"* ]] || [[ "$file" == *".example"* ]]; then
            continue
        fi
        
        # Check for IP addresses (excluding common safe ones)
        if git diff --cached "$file" | grep -oE "\b([0-9]{1,3}\.){3}[0-9]{1,3}\b" | grep -vE "^(127\.0\.0\.1|0\.0\.0\.0|localhost)$" > /dev/null 2>&1; then
            echo -e "${YELLOW}⚠️  INFO: IP address found in $file (may be okay for config)${NC}"
        fi
    done
fi
echo -e "${GREEN}✅ IP check complete${NC}"
echo ""

# =============================================================================
# 4. Check for database files
# =============================================================================
echo -e "${BLUE}🔍 Checking for tracked database files...${NC}"
TRACKED_DB=$(git ls-files | grep -E "\.sqlite3$|\.db$|\.sql$|\.dump$" || true)

if [ -n "$TRACKED_DB" ]; then
    echo -e "${RED}❌ ERROR: Database files are tracked!${NC}"
    echo "$TRACKED_DB"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ No database files tracked${NC}"
fi
echo ""

# =============================================================================
# 5. Check for log files
# =============================================================================
echo -e "${BLUE}🔍 Checking for tracked log files...${NC}"
TRACKED_LOGS=$(git ls-files | grep -E "\.log$|logs/.*\.log" || true)

if [ -n "$TRACKED_LOGS" ]; then
    echo -e "${YELLOW}⚠️  WARNING: Log files are tracked${NC}"
    echo "$TRACKED_LOGS"
    WARNINGS=$((WARNINGS + 1))
else
    echo -e "${GREEN}✅ No log files tracked${NC}"
fi
echo ""

# =============================================================================
# 6. Check for media files (user uploads)
# =============================================================================
echo -e "${BLUE}🔍 Checking for tracked media files...${NC}"
TRACKED_MEDIA=$(git ls-files | grep -E "media/photos/|media/videos/|media/uploads/" || true)

if [ -n "$TRACKED_MEDIA" ]; then
    echo -e "${YELLOW}⚠️  WARNING: User media files are tracked${NC}"
    echo "$TRACKED_MEDIA"
    WARNINGS=$((WARNINGS + 1))
else
    echo -e "${GREEN}✅ No user media files tracked${NC}"
fi
echo ""

# =============================================================================
# 7. Check changes between main and dev (if on dev branch)
# =============================================================================
if [ "$CURRENT_BRANCH" = "dev" ]; then
    echo -e "${BLUE}🔍 Checking changes between main and dev...${NC}"
    
    # Check if there are differences
    if git diff --quiet main..dev; then
        echo -e "${GREEN}✅ No changes between main and dev${NC}"
    else
        # Check for secrets in the diff
        DIFF_SECRETS=$(git diff main..dev | grep -iE "(password|secret|api_key|token).*=.*['\"]" | grep -v ".env.example" || true)
        
        if [ -n "$DIFF_SECRETS" ]; then
            echo -e "${RED}⚠️  WARNING: Potential secrets in changes:${NC}"
            echo "$DIFF_SECRETS"
            WARNINGS=$((WARNINGS + 1))
        else
            echo -e "${GREEN}✅ No obvious secrets in changes between branches${NC}"
        fi
    fi
    echo ""
fi

# =============================================================================
# Summary
# =============================================================================
echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}  Security Check Summary${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed!${NC}"
    echo -e "${GREEN}✅ Safe to commit/push${NC}"
    echo ""
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  ${WARNINGS} warning(s) found${NC}"
    echo -e "${YELLOW}⚠️  Please review the warnings above${NC}"
    echo -e "${YELLOW}⚠️  If warnings are acceptable, you can proceed${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}❌ ${ERRORS} error(s) found${NC}"
    echo -e "${RED}❌ ${WARNINGS} warning(s) found${NC}"
    echo -e "${RED}❌ DO NOT commit/push until errors are fixed!${NC}"
    echo ""
    echo -e "${YELLOW}💡 Tips:${NC}"
    echo -e "   • Remove secrets from files"
    echo -e "   • Use environment variables instead"
    echo -e "   • Check .gitignore is configured"
    echo -e "   • Review: docs/development/DEV_BRANCH_SECURITY.md"
    echo ""
    exit 1
fi
