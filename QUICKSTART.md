# CinemaCompass Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Python 3.11+
- pip

### Installation

```bash
# Clone and navigate
cd cinemaCompass

# Install dependencies
pip install -r requirements.txt
```

### Run the Application

#### Option 1: Streamlit UI (Quick Demo)
```bash
streamlit run app.py
```
Visit http://localhost:8501

#### Option 2: FastAPI Backend
```bash
python backend/run_api.py
```
Visit http://localhost:8000/docs for API documentation

#### Option 3: Admin Dashboard
```bash
streamlit run admin_dashboard.py
```

### Run with Docker
```bash
docker-compose up
```

## 📊 Data Setup (Optional)

To use real MovieLens data:

```bash
# Download MovieLens dataset
python data/scripts/download_movielens.py

# Optional: Enrich with TMDb (requires API key)
export TMDB_API_KEY='your_key'
python data/scripts/fetch_tmdb.py

# Merge and clean
python data/scripts/merge_datasets.py
python data/scripts/clean_data.py
```

## 🎯 Quick Test

```python
from recommendation_system.hybrid_model import HybridRecommender
from recommendation_system.data_loader import load_from_csv

# Load sample data
movies_df, ratings_df = load_from_csv()

# Initialize recommender
recommender = HybridRecommender(use_adaptive_weights=True)
recommender.fit(movies_df, ratings_df)

# Get recommendations
recs = recommender.get_recommendations(
    user_id="1",
    liked_movies=["1", "2"],
    top_n=5
)

for rec in recs:
    print(f"{rec['title']}: {rec['score']:.2f} - {rec['reason']}")
```

## 📖 Next Steps

- Read [README.md](README.md) for full documentation
- Read [DEPLOYMENT.md](DEPLOYMENT.md) for production setup
- Explore API docs at http://localhost:8000/docs
- Check the plan: `cinemacompass-complete-system-plan.plan.md`

