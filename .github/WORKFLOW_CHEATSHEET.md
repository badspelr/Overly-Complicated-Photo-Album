# Git Workflow Cheat Sheet

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                                                                ┃
┃  🚀 DEVELOPMENT BRANCH WORKFLOW                                ┃
┃                                                                ┃
┃  Current Setup:                                                ┃
┃  • main branch = Production (v1.3.0) ✅                        ┃
┃  • dev branch = Development 🚧                                 ┃
┃                                                                ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

## Daily Commands

```bash
# Check which branch you're on
git branch
# * dev  ← You should see this!

# Quick commit (tracked files only)
git wip

# Save everything
git save

# Undo last commit (keep changes)
git undo

# See history
git overview
```

## Development Cycle

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  1. DEVELOP on 'dev' branch                     │
│     ↓                                           │
│     • Make changes                              │
│     • Commit frequently (git wip / git commit)  │
│     • No need to push every time!               │
│                                                 │
│  2. BACKUP (optional)                           │
│     ↓                                           │
│     • git push origin dev                       │
│     • Only when you want backup                 │
│                                                 │
│  3. RELEASE when feature complete               │
│     ↓                                           │
│     • git checkout main                         │
│     • git merge dev --no-ff                     │
│     • git tag v1.4.0                            │
│     • git push origin main --tags               │
│     • git checkout dev                          │
│                                                 │
└─────────────────────────────────────────────────┘
```

## Branch Diagram

```
main:   v1.3.0 ──────────────────────────> v1.4.0 ────────> v1.5.0
                                              ↑                 ↑
                                              │                 │
                                           MERGE            MERGE
                                              │                 │
dev:    ──── commit ─ commit ─ commit ───────┘ commit ────────┘
        │           │         │                      │
     Feature A   Feature B  Feature C            Feature D
     
     ↑
     YOU ARE HERE
     (work freely, commit often)
```

## Quick Commands

| Task | Command |
|------|---------|
| **See branch** | `git branch` |
| **Quick commit** | `git wip` |
| **Save all** | `git save` |
| **Undo commit** | `git undo` |
| **View history** | `git overview` |
| **Push backup** | `git push origin dev` |
| **Merge to main** | `git checkout main && git merge dev` |
| **Tag version** | `git tag v1.4.0` |
| **Push main** | `git push origin main --tags` |
| **Back to dev** | `git checkout dev` |

## Rules

```
✅ DO:
  • Commit often on dev
  • Push dev for backup (optional)
  • Merge to main when complete
  • Test before merging
  • Tag releases

❌ DON'T:
  • Don't commit to main directly
  • Don't push incomplete work to main
  • Don't forget to test first
```

## Example Session

```bash
# Morning: Start work
vim album/views.py
git commit -am "WIP: New feature"

# Afternoon: Continue
vim album/models.py
git wip

# Evening: More work
vim album/tests.py
git commit -am "Add tests"

# Optional: Backup
git push origin dev

# Next day: Feature complete!
git checkout main
git merge dev --no-ff -m "Release v1.4.0: New feature"
git tag v1.4.0
git push origin main --tags
git checkout dev
```

## Aliases (Already Set Up!)

```bash
git wip       # = git commit -am "WIP"
git save      # = git add -A && git commit -m "WIP: Save progress"
git undo      # = git reset HEAD~1 --mixed
git overview  # = git log --oneline --graph --all -10
```

## Help

```bash
# Which branch?
git branch

# What changed?
git status

# Recent commits
git log --oneline -5

# Full guide
cat DEVELOPMENT_WORKFLOW.md
```

---

**Current Status:** ✅ You're on `dev` - Code freely! 🎨

**Remember:** Commit as often as you want on dev. Only push to main when ready for production!
