# CinemaCompass - Hybrid Movie Recommendation System

A production-ready, cinematic movie discovery platform that combines advanced machine learning with a premium Netflix-inspired UI. CinemaCompass provides transparent, explainable recommendations through a hybrid model that blends content-based and collaborative filtering.

## 🎬 Features

### Core Recommendation Engine
- **Hybrid Model**: Combines content-based filtering with collaborative filtering using adaptive weights
- **Matrix Factorization**: SVD and ALS for collaborative filtering
- **Advanced Embeddings**: Genre embeddings, director/cast vectors, Word2Vec for text features
- **Cold-Start Handling**: Smart recommendations for new users and new movies
- **Explainability**: Detailed explanations with feature attribution
- **Comprehensive Evaluation**: Precision@K, Recall@K, NDCG, Diversity, Novelty, Coverage metrics

### Data Pipeline
- **MovieLens Integration**: Download and process MovieLens datasets
- **TMDb API**: Enrich movies with metadata, posters, cast information
- **Data Cleaning**: Automated cleaning and normalization pipeline

### Backend API
- **FastAPI**: High-performance async REST API
- **Authentication**: JWT-based user authentication
- **PostgreSQL**: Production-ready database schema
- **Redis Caching**: Fast recommendation caching

### Frontend
- **Next.js**: Modern React framework
- **Cinematic Design**: Netflix-inspired UI with dark theme
- **Interactive Components**: Recommendation slider, genre filters, movie cards
- **Responsive**: Mobile-friendly design

### Admin Dashboard
- **Streamlit Dashboard**: Model performance monitoring
- **User Analytics**: Engagement statistics and insights
- **System Metrics**: Real-time monitoring

## 📁 Project Structure

```
cinemaCompass/
├── backend/                    # FastAPI backend
│   ├── api/
│   │   ├── main.py            # FastAPI application
│   │   ├── routes/            # API endpoints
│   │   ├── models/            # Database models
│   │   ├── auth.py            # Authentication
│   │   └── cache.py           # Redis caching
│   └── database_schema.sql    # PostgreSQL schema
│
├── frontend/                   # Next.js frontend
│   ├── src/
│   │   ├── pages/             # Next.js pages
│   │   ├── components/        # React components
│   │   └── styles/            # Design system
│
├── recommendation_system/      # ML models
│   ├── hybrid_model.py        # Hybrid recommender
│   ├── content_based.py       # Content-based filtering
│   ├── collaborative_filtering.py
│   ├── matrix_factorization.py
│   ├── embeddings.py          # Feature engineering
│   ├── adaptive_weights.py    # Dynamic weights
│   ├── cold_start.py          # Cold-start handlers
│   ├── explainability.py      # Explanation generator
│   └── evaluation.py          # Metrics
│
├── data/                       # Data pipeline
│   ├── scripts/
│   │   ├── download_movielens.py
│   │   ├── fetch_tmdb.py
│   │   ├── merge_datasets.py
│   │   └── clean_data.py
│   └── README.md
│
├── admin_dashboard.py          # Streamlit admin
├── app.py                      # Streamlit user app
├── Dockerfile                  # Container config
├── docker-compose.yml          # Local deployment
└── requirements.txt            # Python dependencies
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend)
- PostgreSQL (or SQLite for development)
- Redis (optional, falls back to in-memory cache)
- TMDb API key (optional, for movie enrichment)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd cinemaCompass
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   export TMDB_API_KEY='your_tmdb_api_key'
   export DATABASE_URL='sqlite:///./cinemacompass.db'  # or PostgreSQL URL
   export REDIS_URL='redis://localhost:6379'  # optional
   export JWT_SECRET_KEY='your-secret-key'
   ```

4. **Run data pipeline** (optional)
   ```bash
   # Download MovieLens data
   python data/scripts/download_movielens.py
   
   # Enrich with TMDb (requires API key)
   export TMDB_API_KEY='your_key'
   python data/scripts/fetch_tmdb.py
   
   # Merge and clean
   python data/scripts/merge_datasets.py
   python data/scripts/clean_data.py
   ```

5. **Initialize database**
   ```bash
   # Using SQLite (development)
   python -c "from backend.api.models.database import init_db; init_db()"
   
   # Using PostgreSQL (production)
   psql -U postgres -f backend/database_schema.sql
   ```

### Running the Application

#### Option 1: Docker Compose (Recommended)

```bash
docker-compose up
```

This starts:
- Backend API on http://localhost:8000
- PostgreSQL on localhost:5432
- Redis on localhost:6379

#### Option 2: Manual Setup

**Backend:**
```bash
# Start FastAPI server
python backend/run_api.py
# Or with uvicorn
uvicorn backend.api.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
# Visit http://localhost:3000
```

**Streamlit App:**
```bash
streamlit run app.py
```

**Admin Dashboard:**
```bash
streamlit run admin_dashboard.py
```

## 📖 API Documentation

Once the backend is running, visit:
- **API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### Key Endpoints

#### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user

#### Recommendations
- `GET /api/recommendations/{user_id}?top_k=10` - Get recommendations
- `GET /api/recommendations/explain/{user_id}/{movie_id}` - Get explanation

#### Movies
- `GET /api/movies/{movie_id}` - Get movie details
- `GET /api/movies/search/list?q=query&genre=sci-fi` - Search movies
- `GET /api/movies/trending/list` - Get trending movies
- `POST /api/movies/{movie_id}/rate?rating=4.5&user_id=123` - Rate movie

#### User
- `GET /api/user/profile` - Get user profile
- `PUT /api/user/preferences` - Update preferences
- `GET /api/user/watchlist` - Get watchlist
- `POST /api/user/watchlist/add?movie_id=123` - Add to watchlist

## 🎨 Frontend Pages

- **Home** (`/`) - Netflix-style hero with recommendation rows
- **Discover** (`/discover`) - Advanced filtering and search
- **Movie Detail** (`/movie/{id}`) - Full movie information
- **Profile** (`/profile`) - User settings and watchlist

## 🧪 Testing the Recommendation System

```python
from recommendation_system.hybrid_model import HybridRecommender
from recommendation_system.data_loader import load_from_csv

# Load data
movies_df, ratings_df = load_from_csv()

# Initialize and fit model
recommender = HybridRecommender(use_adaptive_weights=True)
recommender.fit(movies_df, ratings_df)

# Get recommendations
recommendations = recommender.get_recommendations(
    user_id="1",
    liked_movies=["1", "2"],
    top_n=10
)

for rec in recommendations:
    print(f"{rec['title']}: {rec['score']:.3f} - {rec['reason']}")
```

## 📊 Evaluation Metrics

Run evaluation:
```python
from recommendation_system.evaluation import evaluate_recommender

# Prepare test data
# ... (split ratings into train/test)

results = evaluate_recommender(
    recommendations_dict,
    test_ratings,
    movies_df,
    k_values=[5, 10, 20]
)
```

Metrics include:
- **Accuracy**: Precision@K, Recall@K, NDCG@K, MAP@K
- **Diversity**: Intra-list diversity, genre diversity
- **Novelty**: Self-information, unexpectedness
- **Coverage**: Catalog coverage, user coverage

## 🔧 Configuration

### Environment Variables

- `DATABASE_URL` - Database connection string
- `REDIS_URL` - Redis connection string (optional)
- `JWT_SECRET_KEY` - Secret key for JWT tokens
- `TMDB_API_KEY` - TMDb API key for movie enrichment
- `PORT` - Backend server port (default: 8000)

### Model Configuration

Adjust hybrid model weights in `recommendation_system/hybrid_model.py`:
- `default_content_weight`: Default weight for content-based (0.5)
- `default_collaborative_weight`: Default weight for collaborative (0.5)
- `use_adaptive_weights`: Enable adaptive weight calculation (True)

## 🚀 Deployment

### Docker Deployment

```bash
docker build -t cinemacompass-backend .
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e REDIS_URL=redis://... \
  cinemacompass-backend
```

### Cloud Deployment

See deployment configurations:
- `docker-compose.yml` - Local development
- `.github/workflows/deploy.yml` - CI/CD pipeline
- `Dockerfile` - Container definition

Recommended platforms:
- **Backend**: Render, Railway, or AWS
- **Frontend**: Vercel or Netlify
- **Database**: Render PostgreSQL or AWS RDS
- **Redis**: Upstash or Redis Cloud

## 📝 Development

### Adding New Features

1. **New Recommendation Algorithm**: Add to `recommendation_system/`
2. **New API Endpoint**: Add route to `backend/api/routes/`
3. **New Frontend Page**: Add to `frontend/src/pages/`
4. **New Component**: Add to `frontend/src/components/`

### Running Tests

```bash
# Python tests
pytest tests/

# Frontend tests
cd frontend
npm test
```

## 📄 License

This project is part of the CinemaCompass system evolution plan.

## 🤝 Contributing

See the complete system plan in `cinemacompass-complete-system-plan.plan.md` for detailed architecture and development roadmap.

## 📞 Support

For issues and questions, please refer to the system plan document or create an issue in the repository.
