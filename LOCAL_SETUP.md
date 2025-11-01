# Local Development Setup

This project has two components:
1. **React Frontend** (Vite + TypeScript)
2. **Python Recommendation System** (Streamlit app)

## Running the React Frontend

### Prerequisites
- Node.js 18+ and npm installed

### Steps

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm run dev
   ```
   
   The app will be available at: **http://localhost:8080**

3. **Build for production:**
   ```bash
   npm run build
   ```

4. **Preview production build:**
   ```bash
   npm run preview
   ```

## Running the Python Recommendation System (Streamlit)

### Prerequisites
- Python 3.8+ installed
- pip or conda

### Steps

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Streamlit app:**
   ```bash
   streamlit run app.py
   ```
   
   Or use the provided script:
   ```bash
   ./run.sh
   ```

   The app will be available at: **http://localhost:8501**

3. **Test the recommendation system programmatically:**
   ```bash
   python example_usage.py
   ```

## Running Both Simultaneously

You can run both the React frontend and Streamlit app at the same time:

**Terminal 1 - React Frontend:**
```bash
npm run dev
# Runs on http://localhost:8080
```

**Terminal 2 - Streamlit App:**
```bash
streamlit run app.py
# Runs on http://localhost:8501
```

## Troubleshooting

### React App Issues

**If you get "Cannot find module" errors:**
- Make sure you've run `npm install`
- Check that the `src` directory exists with your React components

**If port 8080 is already in use:**
- Change the port in `vite.config.ts` or use `npm run dev -- --port 3000`

### Streamlit App Issues

**If you get "ModuleNotFoundError":**
- Make sure you've installed all dependencies: `pip install -r requirements.txt`
- Check that you're using the correct Python environment

**If port 8501 is already in use:**
- Streamlit will automatically try the next available port

## Quick Start (All-in-One)

```bash
# Install Node.js dependencies
npm install

# Install Python dependencies
pip install -r requirements.txt

# Run React frontend (Terminal 1)
npm run dev

# Run Streamlit app (Terminal 2)
streamlit run app.py
```

