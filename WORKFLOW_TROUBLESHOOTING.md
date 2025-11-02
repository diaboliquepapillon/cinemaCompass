# GitHub Actions Workflow Troubleshooting

## Current Status
The workflow should now work with these improvements:
- ✅ Added explicit `NODE_ENV=production`
- ✅ Improved verification script (handles whitespace in counts)
- ✅ Better error messages
- ✅ `.nojekyll` file added to prevent Jekyll processing

## If Workflow Still Fails

### Step 1: Check GitHub Pages Settings
1. Go to: Settings → Pages
2. **Source** should be: **"GitHub Actions"** (NOT "Deploy from a branch")
3. Save if changed

### Step 2: Check Workflow Permissions
1. Go to: Settings → Actions → General
2. Under "Workflow permissions":
   - Select: **"Read and write permissions"**
   - Check: **"Allow GitHub Actions to create and approve pull requests"**
3. Save

### Step 3: Check Latest Workflow Run
1. Go to: Actions tab
2. Click on the latest failed run
3. Look at which step failed:
   - **Build step**: Check if npm install or build failed
   - **Verify step**: Check if files are missing
   - **Deploy step**: Check if permissions are correct

### Step 4: Common Issues

#### Issue: "Permission denied" in deploy step
**Fix**: Ensure GitHub Pages environment is set up:
1. Settings → Environments
2. Ensure "github-pages" environment exists
3. If not, the workflow will create it on first run

#### Issue: "Build failed"
**Possible causes**:
- Missing dependencies
- TypeScript errors
- Missing files

**Fix**: Check the build logs in the Actions tab

#### Issue: "Upload artifact failed"
**Fix**: This usually indicates the dist folder doesn't exist or is empty. Check the verify step output.

### Step 5: Manual Testing
To test the build locally (matches CI):
```bash
rm -rf node_modules dist
npm ci
NODE_ENV=production npm run build
ls -la dist/
ls -la dist/assets/
```

### Step 6: Force Re-run
1. Go to: Actions tab
2. Find the latest workflow run
3. Click "Re-run jobs" → "Re-run all jobs"

## Verification Checklist

After workflow succeeds:
- [ ] Build step completed
- [ ] Verify step shows "✅ Build verification passed"
- [ ] Upload artifact completed
- [ ] Deploy step completed
- [ ] Site accessible at: https://diaboliquepapillon.github.io/cinemaCompass/

## Expected Workflow Output

```
✓ Build step: npm ci → npm run build → Success
✓ Verify step: Files exist → ✅ Build verification passed
✓ Upload artifact: Uploaded dist/ folder
✓ Deploy: Deployed to GitHub Pages
```

