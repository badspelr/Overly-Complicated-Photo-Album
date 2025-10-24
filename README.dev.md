# 🚧 Development Branch

Welcome to the **development branch** of Django Photo Album!

---

## 📍 You Are Here

This is the **`dev`** branch - the active development workspace where new features are built and tested.

**Branch Purpose:**
- ✅ Daily development work
- ✅ Feature experimentation
- ✅ Commit freely without pushing to production
- ✅ Merge to `main` when features are complete

---

## 🎯 Quick Start

You're all set! Just start coding:

```bash
# Check you're on dev branch
git branch
# * dev  ← You should see this

# Make changes
vim album/views.py

# Quick commit
git wip

# Or commit with message
git commit -am "Add new feature"

# Continue working...
# No need to push every time!
```

---

## 📚 Documentation

- **Complete Guide:** [`DEVELOPMENT_WORKFLOW.md`](DEVELOPMENT_WORKFLOW.md)
- **Quick Reference:** [`.github/WORKFLOW_CHEATSHEET.md`](.github/WORKFLOW_CHEATSHEET.md)

---

## 🔄 Branch Relationship

```
main (production)  ← Merge to when feature complete
  ↑
  │ merge
  │
dev (you are here) ← Work here freely
  ↑
  │
your commits       ← Commit as often as you want
```

---

## 🚀 When to Merge to Main

Merge to `main` when:
- ✅ Feature is complete
- ✅ All tests pass
- ✅ Documentation updated
- ✅ Ready for production

```bash
git checkout main
git merge dev --no-ff -m "Release v1.4.0: Feature name"
git tag v1.4.0
git push origin main --tags
git checkout dev
```

---

## 💡 Quick Commands

```bash
git wip          # Quick commit
git save         # Save all changes
git undo         # Undo last commit
git overview     # View branch history
```

---

## 📊 Current Status

**Production (main):** v1.3.0 ✅  
**Development (dev):** Active 🚧  
**Your Branch:** dev ✅

---

## 🎨 Development Philosophy

On this branch:
- Commit early, commit often
- Experiment freely
- Don't worry about perfect commits
- Push to `origin/dev` for backup (optional)
- Have fun building features!

---

**Happy Coding! 🚀**

For help, see: [`DEVELOPMENT_WORKFLOW.md`](DEVELOPMENT_WORKFLOW.md)
