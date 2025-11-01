# GitHub Pages Setup Instructions

## Enabling GitHub Pages

To enable GitHub Pages for this repository:

1. Go to your repository on GitHub: `https://github.com/diaboliquepapillon/cinemaCompass`

2. Click on **Settings** tab

3. Scroll down to **Pages** in the left sidebar

4. Under **Source**, select:
   - **Source**: `GitHub Actions`
   - This will use the workflow file in `.github/workflows/deploy.yml`

5. Click **Save**

## How It Works

The GitHub Actions workflow (`.github/workflows/deploy.yml`) will:
- Automatically build your React app when you push to the `main` branch
- Configure the base URL for GitHub Pages (`/cinemaCompass/`)
- Deploy the built files to GitHub Pages

## After Deployment

Once deployed, your site will be available at:
`https://diaboliquepapillon.github.io/cinemaCompass/`

## Troubleshooting

### If the page shows a blank screen or 404:
1. Make sure GitHub Actions workflow completed successfully
2. Check that the base URL matches your repository name
3. Verify that the `dist` folder contains the built files

### If assets (CSS, JS) aren't loading:
- The `vite.config.ts` has been configured to use the correct base path
- Make sure you're accessing the site via the GitHub Pages URL, not locally

### To manually trigger deployment:
1. Go to **Actions** tab in your repository
2. Select **Deploy to GitHub Pages** workflow
3. Click **Run workflow**

## Local Development

For local development, the base URL will be `/` so everything works normally.

For local testing with GitHub Pages base path:
```bash
npm run build
npx serve -s dist -l 3000
# Then visit http://localhost:3000/cinemaCompass/
```

