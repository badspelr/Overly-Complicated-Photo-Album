# 🔒 Dev Branch Security Guide

## ⚠️ CRITICAL: Never Push Sensitive Information

This guide ensures you **never accidentally commit sensitive data** to the dev branch.

---

## ✅ Already Protected (via .gitignore)

Your `.gitignore` is already protecting:

```
✅ .env files (all variants)
✅ Database files (*.sql, *.dump, db.sqlite3)
✅ Log files (*.log, logs/)
✅ SSL certificates (*.pem, *.key, *.crt)
✅ Media uploads (photos, videos, user data)
✅ Python cache (__pycache__, *.pyc)
✅ IDE files (.vscode, .idea)
✅ Backup files (*.bak, *.backup)
✅ Temporary files (*.tmp, temp.py)
```

---

## 🚨 What NEVER to Commit

### **1. Environment Files**
```
❌ .env
❌ .env.local
❌ .env.production
❌ Any file with real passwords/keys
```

### **2. Database Files**
```
❌ db.sqlite3
❌ *.sql dumps
❌ Database backups
❌ User data exports
```

### **3. User Data**
```
❌ Uploaded photos
❌ Uploaded videos
❌ User profile pictures
❌ Any personal information
```

### **4. Secrets & Credentials**
```
❌ API keys
❌ Secret keys
❌ Passwords
❌ OAuth tokens
❌ SSL certificates
❌ Private keys
```

### **5. Log Files**
```
❌ *.log files
❌ Error logs with stack traces
❌ Security audit logs
❌ Access logs with IP addresses
```

---

## ✅ Pre-Commit Checklist

**Before committing ANYTHING to dev branch:**

```bash
# 1. Check what you're about to commit
git status

# 2. Review actual changes
git diff

# 3. Look for sensitive patterns
git diff | grep -i "password\|secret\|key\|token"

# 4. If you see ANY secrets, DON'T COMMIT!
```

---

## 🛡️ Additional Protections (Recommended)

### **1. Pre-Commit Hooks**

I'll set this up for you - it automatically scans for secrets before commit.

### **2. Git Secrets Tool**

Prevents committing credentials:
```bash
git secrets --install
git secrets --register-aws
```

### **3. Regular Audits**

Check what's tracked:
```bash
# See all tracked files
git ls-files

# Check for accidentally committed secrets
git log -S "password" --all
git log -S "SECRET_KEY" --all
```

---

## 🔍 How to Check Before Pushing

### **Quick Check**
```bash
# What am I about to push?
git diff main..dev

# List changed files
git diff --name-only main..dev

# Search for secrets in changes
git diff main..dev | grep -E "(password|secret|key|token|api_key)" -i
```

### **Thorough Check**
```bash
# Review each commit on dev
git log main..dev --oneline

# Check specific commit
git show <commit-hash>

# Search commit messages for warnings
git log --grep="TODO\|FIXME\|TEMP\|DEBUG"
```

---

## 🚀 Safe Development Workflow

### **Development with Sensitive Data**

```bash
# 1. Use environment variables (already set up ✅)
#    Sensitive data in .env (which is .gitignored)

# 2. Use placeholders in code
SECRET_KEY = config('SECRET_KEY')  # ✅ Good
SECRET_KEY = 'hardcoded-value'     # ❌ Never do this

# 3. Document what needs configuration
# See: .env.example for required variables

# 4. Test with dummy data
# Don't test with real user photos/videos
```

### **Before Pushing to Dev Branch**

```bash
# Step 1: Review changes
git diff main..dev

# Step 2: Check for secrets (automated - see below)
./scripts/check-secrets.sh

# Step 3: If clean, push
git push origin dev
```

---

## 🤖 Automated Secret Detection

Let me create a script to check for secrets automatically.

---

## 📋 Safe Files to Commit

These are **SAFE** to commit to dev branch:

```
✅ Python code (.py files)
✅ Templates (.html files)
✅ Static files (CSS, JS, images)
✅ Configuration templates (.env.example)
✅ Documentation (.md files)
✅ Tests (test_*.py)
✅ Requirements (requirements.txt)
✅ Docker configs (Dockerfile, docker-compose.yml)
✅ Scripts (.sh files - if no secrets)
```

---

## ⚠️ Files to Review Carefully

These **CAN** contain secrets - review before commit:

```
⚠️ settings.py - Check for hardcoded values
⚠️ .sh scripts - Check for credentials
⚠️ docker-compose.yml - Check for passwords
⚠️ nginx.conf - Check for domain names
⚠️ Any new config files
```

---

## 🆘 If You Accidentally Commit Secrets

### **If Not Pushed Yet**

```bash
# Remove from commit, keep changes
git reset HEAD~1

# Edit file to remove secret
vim file_with_secret.py

# Commit again (without secret)
git add file_with_secret.py
git commit -m "Fix: Remove secret"
```

### **If Already Pushed to Dev**

```bash
# ⚠️ WARNING: This rewrites history
# Only do this if dev branch is just yours

# Remove last commit from dev
git reset --hard HEAD~1

# Force push (overwrites remote)
git push origin dev --force

# Then commit properly without secret
```

### **If Secret Was in Main Branch**

**🚨 CRITICAL: Immediate Action Required**

1. **Rotate the secret immediately** (change password/key)
2. **Remove from Git history** (use BFG Repo-Cleaner)
3. **Notify users if applicable**
4. **Update all deployment configs**

---

## 🔧 Example Safe vs Unsafe

### ❌ UNSAFE (Never Do This)

```python
# DON'T hardcode secrets
SECRET_KEY = 'django-insecure-hardcoded-key-12345'
DATABASE_PASSWORD = 'mypassword123'
API_KEY = 'sk-1234567890abcdef'

# DON'T commit real data
user_email = 'real.user@example.com'
credit_card = '4111-1111-1111-1111'
```

### ✅ SAFE (Always Do This)

```python
# DO use environment variables
SECRET_KEY = config('SECRET_KEY')
DATABASE_PASSWORD = config('DB_PASSWORD')
API_KEY = config('OPENAI_API_KEY')

# DO use placeholders
user_email = 'test@example.com'
user_data = {'email': 'placeholder@example.com'}
```

---

## 📊 What's Currently Safe

```
✅ .env is .gitignored (secrets protected)
✅ .env.example has placeholders (safe to commit)
✅ settings.py uses config() (reads from env)
✅ media/ uploads are .gitignored (user data protected)
✅ *.log files are .gitignored (logs protected)
✅ db.sqlite3 is .gitignored (database protected)
```

---

## 🎯 Daily Workflow (Secure)

```bash
# 1. Make changes
vim album/views.py

# 2. Before committing, check what changed
git diff

# 3. Look for any secrets (manual review)
#    - No passwords
#    - No API keys
#    - No real emails
#    - No sensitive data

# 4. If clean, commit
git wip  # or git commit -m "message"

# 5. Before pushing to dev, final check
git diff main..dev | grep -iE "password|secret|key|token"

# 6. If no matches, safe to push
git push origin dev
```

---

## 🔍 Verification Commands

### **Check Current Branch for Secrets**

```bash
# Search for common secret patterns
git grep -E "password.*=|secret.*=|key.*=" | grep -v ".env.example"

# Search for email addresses (might be sensitive)
git grep -E "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

# Search for URLs with credentials
git grep -E "https?://[^:]+:[^@]+@"

# Search for potential API keys
git grep -E "['\"][0-9a-zA-Z]{32,}['\"]"
```

### **Check What's Tracked**

```bash
# List all tracked files
git ls-files

# Check if .env is tracked (should NOT be)
git ls-files | grep "^.env$"
# (Should return nothing)

# Check for tracked logs
git ls-files | grep ".log"
# (Should return nothing)
```

---

## 🛠️ Tools to Install (Optional)

### **1. git-secrets**
```bash
brew install git-secrets  # macOS
# or
sudo apt install git-secrets  # Linux

git secrets --install
git secrets --register-aws
```

### **2. detect-secrets**
```bash
pip install detect-secrets

detect-secrets scan > .secrets.baseline
detect-secrets audit .secrets.baseline
```

### **3. gitleaks**
```bash
# Install
brew install gitleaks

# Scan repository
gitleaks detect
```

---

## 📝 Summary: Your Protection Layers

```
Layer 1: .gitignore           ✅ Already configured
Layer 2: .env files           ✅ Excluded from git
Layer 3: settings.py          ✅ Uses environment variables
Layer 4: Pre-commit checks    ⚠️ Can add (see below)
Layer 5: Manual review        ✅ You (always review git diff)
Layer 6: Automated scanning   ⚠️ Optional tools available
```

---

## ✅ You're Already Protected!

**Good news:** Your setup is already secure because:

1. ✅ `.env` files are gitignored
2. ✅ `settings.py` reads from environment (not hardcoded)
3. ✅ User uploads are gitignored
4. ✅ Database files are gitignored
5. ✅ Log files are gitignored

**Just remember:**
- Always review `git diff` before committing
- Never hardcode secrets in Python files
- Use `.env.example` for documentation, `.env` for real values
- When in doubt, don't commit - ask first!

---

## 🚀 Next Steps

Would you like me to:

1. **Create an automated pre-commit hook** to check for secrets?
2. **Add a `check-secrets.sh` script** you can run manually?
3. **Install git-secrets** or similar tools?
4. **Keep current setup** (already secure with manual review)?

Let me know and I'll set it up! 🔒

---

**Remember:** When you run `git diff` before committing, you're your own best security check! 🛡️
