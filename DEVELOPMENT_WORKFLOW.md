# Development Workflow Guide

## 🎯 Overview

You're currently on the **`dev`** branch - your primary development workspace.

**Main branch:** Production-ready code only (v1.3.0)  
**Dev branch:** Daily development work (commit freely!)

---

## 📋 Daily Workflow

### 1. Make Changes & Commit Freely

```bash
# You're on dev branch - work normally
vim album/views.py

# Commit as often as you want
git add album/views.py
git commit -m "WIP: Trying new photo editor approach"

# Or use quick aliases:
git wip              # Quick "WIP" commit of tracked files
git save             # Save all changes with timestamp
```

### 2. Push to Dev Branch (Optional)

```bash
# Push to dev branch for backup (not required every time)
git push origin dev

# This won't affect main branch!
```

### 3. When Feature is Complete

```bash
# Switch to main
git checkout main

# Merge dev into main
git merge dev --no-ff -m "Release v1.4.0: Photo Editor Feature"

# Tag the release (optional)
git tag v1.4.0

# Push to GitHub (this updates production)
git push origin main --tags

# Back to dev for more work
git checkout dev
```

---

## 🔧 Quick Command Reference

### Git Aliases (Already Configured!)

```bash
git wip              # Quick commit: "WIP"
git save             # Commit all changes: "WIP: Save progress"
git undo             # Undo last commit (keeps changes)
git overview         # See branch history graph
```

### Common Tasks

```bash
# Check which branch you're on
git branch

# See what's changed
git status

# View recent commits
git log --oneline -5

# Compare dev vs main
git diff main..dev

# See all branches
git branch -a
```

---

## 📊 Branch Status

### Current Setup

```
main branch:  Production-ready (v1.3.0) ✅
↓
dev branch:   Development (current) 🚧
↓
Your work:    Commit freely here! 💻
```

### On GitHub

- **main branch:** https://github.com/badspelr/Overly-Complicated-Photo-Album/tree/main
- **dev branch:** https://github.com/badspelr/Overly-Complicated-Photo-Album/tree/dev

---

## 🎨 Example Development Session

### Morning: Start New Feature

```bash
# Already on dev branch
git branch
# * dev

# Create a feature file
vim album/services/photo_editor.py

# Commit your progress
git add album/services/photo_editor.py
git commit -m "WIP: Photo editor service skeleton"
```

### Afternoon: Continue Development

```bash
# Add more functionality
vim album/services/photo_editor.py
vim album/views/photo_editor.py

# Quick commit
git wip

# Or commit with message
git commit -am "WIP: Add crop and rotate functions"
```

### Evening: Add Tests

```bash
# Add tests
vim album/tests/test_photo_editor.py

# Commit
git commit -am "Add photo editor tests"

# Optionally push to dev for backup
git push origin dev
```

### Next Day: Feature Complete

```bash
# Run tests
docker-compose exec web pytest

# Update documentation
vim docs/features/PHOTO_EDITOR.md
git commit -am "Add photo editor documentation"

# Update version
vim photo_album/__version__.py
# Change to 1.4.0

# Ready to release!
git checkout main
git merge dev --no-ff -m "Release v1.4.0: Photo Editor

- Add photo editor with crop, rotate, filters
- Add comprehensive tests
- Update documentation"

# Tag the release
git tag v1.4.0

# Push to production
git push origin main --tags

# Back to dev
git checkout dev
```

---

## 🚨 Important Rules

### ✅ DO:
- Commit frequently on dev branch
- Push to dev occasionally for backup
- Merge to main only when feature is complete
- Test before merging to main
- Update version numbers before release
- Tag releases on main branch

### ❌ DON'T:
- Don't commit directly to main
- Don't push incomplete features to main
- Don't merge to main without testing
- Don't forget to switch back to dev after merging

---

## 🔄 Syncing Changes

### If Main Gets Updates (from another source)

```bash
# On dev branch
git checkout dev

# Pull main changes
git fetch origin main
git merge origin/main

# Or rebase (keeps cleaner history)
git rebase origin/main
```

### If You Accidentally Committed to Main

```bash
# On main branch with uncommitted changes
git stash

# Switch to dev
git checkout dev

# Apply those changes
git stash pop
```

---

## 📈 Version Release Workflow

### When You're Ready to Release

1. **Ensure all tests pass**
   ```bash
   docker-compose exec web pytest
   ```

2. **Update version number**
   ```bash
   # Edit photo_album/__version__.py
   __version__ = "1.4.0"
   
   # Update VERSION file
   echo "1.4.0" > VERSION
   
   # Update CHANGELOG.md
   # Add new version section
   ```

3. **Commit version bump**
   ```bash
   git commit -am "Bump version to 1.4.0"
   ```

4. **Merge to main**
   ```bash
   git checkout main
   git merge dev --no-ff -m "Release v1.4.0: Feature name"
   ```

5. **Tag and push**
   ```bash
   git tag v1.4.0
   git push origin main --tags
   ```

6. **Back to dev**
   ```bash
   git checkout dev
   ```

---

## 🛠️ Troubleshooting

### "I'm on the wrong branch!"

```bash
# Save your work
git stash

# Switch to correct branch
git checkout dev

# Get your work back
git stash pop
```

### "I want to undo my last commit"

```bash
# Undo commit but keep changes
git undo  # (alias we set up)

# Or:
git reset HEAD~1 --mixed
```

### "I want to throw away all changes"

```bash
# ⚠️ WARNING: This deletes uncommitted changes!
git reset --hard HEAD
git clean -fd
```

### "I forgot which branch I'm on"

```bash
# Shows current branch with *
git branch

# Or check status
git status
```

### "How do I see what's different between dev and main?"

```bash
# List different files
git diff --name-only main..dev

# See actual changes
git diff main..dev

# See commits on dev not on main
git log main..dev --oneline
```

---

## 📚 Additional Resources

### Visual Branch Overview

```bash
# See branch graph
git overview  # (alias we set up)

# Or full version:
git log --oneline --graph --all
```

### Commit History

```bash
# Last 10 commits
git log --oneline -10

# Commits today
git log --since="midnight" --oneline

# Your commits
git log --author="$(git config user.name)" --oneline
```

---

## 🎯 Quick Start Checklist

```
✅ Currently on dev branch
✅ Dev branch pushed to GitHub
✅ Git aliases configured (wip, save, undo, overview)
✅ Main branch protected (v1.3.0 production ready)
✅ Ready to develop!
```

---

## 💡 Pro Tips

1. **Commit often on dev** - Don't worry about perfect commits
2. **Push dev occasionally** - For backup, not every commit
3. **Test before merging** - Always run tests before main merge
4. **Use descriptive messages** - Even "WIP: descriptive text" is better than "WIP"
5. **Tag releases** - Makes it easy to track versions
6. **Update CHANGELOG** - Before merging to main

---

## 🚀 Your Current Status

```
Current Branch:  dev ✅
Main Branch:     v1.3.0 (production ready) ✅
Dev Branch:      Synced with main ✅
Git Aliases:     Configured ✅
Ready to Code:   YES! 🎉
```

---

## Need Help?

```bash
# Show this guide
cat DEVELOPMENT_WORKFLOW.md

# Check current branch
git branch

# See recent activity
git log --oneline -5

# Get help on a command
git help <command>
```

---

**Happy Coding! 🎨**

Remember: You're on **dev** - commit freely and have fun! 🚀

---

**Version:** 1.3.0  
**Last Updated:** October 24, 2025  
**Workflow:** Development Branch Strategy
