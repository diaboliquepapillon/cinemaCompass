# GitHub Pages Branch Deployment Setup

## ✅ Changes Made

Switched from GitHub Actions Pages deployment to **branch-based deployment** using `gh-pages` branch.

## 📋 Setup Instructions

After pushing this commit, follow these steps:

### Step 1: Go to Repository Settings
1. Navigate to: **Settings** → **Pages**

### Step 2: Configure Source
1. Under **"Source"**, select: **"Deploy from a branch"**
2. Select branch: **`gh-pages`**
3. Select folder: **`/ (root)`**
4. Click **Save**

### Step 3: Wait for First Deployment
1. Go to **Actions** tab
2. Wait for "Build and Deploy to Branch" workflow to complete
3. It will create the `gh-pages` branch automatically
4. Once complete, GitHub Pages will be live

### Step 4: Verify Deployment
- Visit: `https://diaboliquepapillon.github.io/cinemaCompass/`
- Clear browser cache if needed

## 🔄 How It Works

1. **On every push to `main`:**
   - GitHub Actions builds the project
   - Creates/updates the `gh-pages` branch with `dist/` contents
   - GitHub Pages serves from `gh-pages` branch

2. **Automatic Updates:**
   - Every time you push to `main`, the site auto-updates
   - No manual deployment needed

## ✅ Benefits

- ✅ Simpler deployment (branch-based)
- ✅ Works with GitHub's built-in Pages
- ✅ Automatic updates on every push
- ✅ No special permissions needed

## 🐛 Troubleshooting

If deployment fails:
1. Check **Actions** tab for errors
2. Verify **Settings → Pages** is set to `gh-pages` branch
3. Make sure workflow completed successfully
4. Wait 1-2 minutes after workflow completes for Pages to update

The app will be available at:
**https://diaboliquepapillon.github.io/cinemaCompass/**

