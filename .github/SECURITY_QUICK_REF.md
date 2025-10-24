# 🔒 Dev Branch Security - Quick Reference

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  YOUR SECURITY STATUS: ✅ PROTECTED                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Before Every Push

```bash
# Run this command:
./scripts/check-secrets.sh

# Expected output:
✅ All checks passed!
✅ Safe to commit/push
```

## What's Protected

| Type | Status | How |
|------|--------|-----|
| .env files | ✅ Protected | .gitignore |
| Passwords | ✅ Protected | Environment vars |
| API keys | ✅ Protected | Environment vars |
| Database files | ✅ Protected | .gitignore |
| Log files | ✅ Protected | .gitignore |
| User uploads | ✅ Protected | .gitignore |

## Safe Workflow

```
1. Make changes
   ↓
2. git diff (review)
   ↓
3. ./scripts/check-secrets.sh (scan)
   ↓
4. git commit (if clean)
   ↓
5. git push origin dev (backup)
```

## Quick Commands

```bash
# Check for secrets
./scripts/check-secrets.sh

# Review changes
git diff

# Check what's tracked
git ls-files | grep -E "\.env$|\.log$|\.sqlite3$"
# (Should return nothing or only .env.example/.env.production)

# Verify .env is not tracked
git ls-files | grep "^\.env$"
# (Should return nothing)
```

## Emergency: If You Commit a Secret

### Not Pushed Yet
```bash
git reset HEAD~1        # Undo commit
# Remove secret from file
git commit -am "Fix"    # Commit again
```

### Already Pushed to Dev
```bash
git reset --hard HEAD~1        # Remove commit
git push origin dev --force    # Force update
# Then rotate the secret immediately!
```

## Documentation

- **Full Guide:** `docs/development/DEV_BRANCH_SECURITY.md`
- **Scanner Script:** `scripts/check-secrets.sh`

---

**Remember:** When in doubt, DON'T commit. Review first! 🛡️
