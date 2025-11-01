# Git Setup Guide for CinemaCompass

## Current Status
- ✅ Git repository initialized
- ✅ Remote configured: `origin` → `https://github.com/diaboliquepapillon/cinemaCompass.git`
- ✅ User configured: Aylin (vahabovaylin@gmail.com)
- ✅ Branch: `main` (3 commits ahead of origin/main)

## Sync Your Changes

### Push Local Commits to GitHub

```bash
# Check your status first
git status

# Push your commits to GitHub
git push origin main
```

### If Authentication is Required

**Option 1: Personal Access Token (Recommended)**
1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Generate a new token with `repo` permissions
3. When prompted for password, use the token instead

**Option 2: SSH Authentication**
```bash
# Check if you have SSH keys
ls -la ~/.ssh

# If not, generate SSH key
ssh-keygen -t ed25519 -C "vahabovaylin@gmail.com"

# Add to GitHub: Settings → SSH and GPG keys → New SSH key
# Then change remote URL
git remote set-url origin git@github.com:diaboliquepapillon/cinemaCompass.git
```

### Pull Latest Changes

```bash
# Fetch and merge latest changes
git pull origin main
```

### Resolve Conflicts (if any)

```bash
# If there are conflicts after pull
git status  # See conflicted files
# Edit conflicted files, then:
git add .
git commit -m "Resolve merge conflicts"
git push origin main
```

## Common Commands

```bash
# View commit history
git log --oneline -10

# See what files changed
git diff

# Add all changes
git add .

# Commit changes
git commit -m "Your commit message"

# Push to GitHub
git push origin main

# Pull latest changes
git pull origin main

# Check remote status
git remote -v
```

## Troubleshooting

### If push fails due to large files:
```bash
# Check for large files
find . -type f -size +50M -not -path "./.git/*"

# Remove large files from history (if needed)
git rm --cached large_file.csv
git commit -m "Remove large file"
```

### If you need to reset:
```bash
# Reset to last commit (discard local changes)
git reset --hard HEAD

# Reset to match remote
git reset --hard origin/main
```

## Next Steps

1. **Push your 3 local commits:**
   ```bash
   git push origin main
   ```

2. **If authentication fails:**
   - Use Personal Access Token or set up SSH (see above)

3. **Set up automatic syncing:**
   - Use GitHub Desktop app, or
   - Set up Git hooks for automatic backup

