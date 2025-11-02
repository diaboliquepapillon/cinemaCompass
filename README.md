# CinemaCompass - Hybrid Movie Recommendation System

A production-ready movie recommendation system that combines **content-based filtering** and **collaborative filtering** with rich metadata and personalized explanations.

## 🎯 Features

### Hybrid Recommendation Engine
- **Content-Based Filtering**: Uses TF-IDF on rich metadata (genres, director, cast, tags, overview)
- **Collaborative Filtering**: Matrix factorization (SVD) to find similar users
- **Hybrid Combination**: Weighted blend of both approaches for optimal recommendations

### Rich Metadata
- **Genres**: Movie genres and categories
- **Director**: Director information
- **Cast**: Top 5 cast members
- **Tags/Keywords**: Movie tags and keywords
- **Overview**: Movie descriptions

### Evaluation Metrics
- **Precision@K**: Fraction of recommended items that are relevant
- **Recall@K**: Fraction of relevant items that are retrieved
- **NDCG@K**: Normalized Discounted Cumulative Gain at K
- **MAP**: Mean Average Precision

### Personalized Explanations
- **"Because you liked X, try Y"** - Personalized recommendations with explanations
- **Similarity Reasoning**: Explains why movies are recommended
- **User Taste Matching**: Shows how recommendations match user preferences

## 🏗️ Architecture

```
CinemaCompass/
├── recommendation_system/
│   ├── content_based.py          # Content-based filtering with rich metadata
│   ├── collaborative_filtering.py # Collaborative filtering (SVD)
│   ├── hybrid_recommender.py     # Hybrid combination
│   └── evaluation.py             # Precision@K, Recall@K, NDCG@K
├── backend_api.py                # FastAPI backend
├── src/
│   ├── services/
│   │   ├── movieService.ts       # TMDb API integration
│   │   └── recommendationService.ts # Hybrid recommendations API
│   └── pages/
│       └── Index.tsx              # Main UI (kept original design)
└── requirements.txt
```

## 🚀 Quick Start

### Backend Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Start the FastAPI server**:
```bash
python backend_api.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Install dependencies**:
```bash
npm install
```

2. **Start development server**:
```bash
npm run dev
```

3. **Set API URL** (optional):
```bash
# Create .env file
VITE_API_URL=http://localhost:8000
```

## 📡 API Endpoints

### Get Recommendations
```http
POST /api/recommendations
Content-Type: application/json

{
  "user_id": "user123",
  "liked_movie_ids": ["12345", "67890"],
  "top_n": 10
}
```

**Response**:
```json
[
  {
    "movie_id": "12345",
    "title": "Inception",
    "score": 0.85,
    "reason": "Because you liked The Matrix, you might enjoy Inception - they share similar genres, cast, and storyline.",
    "genres": "Action, Sci-Fi",
    "poster_path": "/poster.jpg",
    "vote_average": 8.5
  }
]
```

### Evaluate Recommendations
```http
POST /api/evaluate
Content-Type: application/json

{
  "user_id": "user123",
  "liked_movies": ["12345", "67890"],
  "relevant_movies": ["11111", "22222", "33333"],
  "k": 10
}
```

**Response**:
```json
{
  "precision_at_k": 0.75,
  "recall_at_k": 0.60,
  "ndcg_at_k": 0.82,
  "k": 10
}
```

## 🔧 Configuration

### Hybrid Weights
Adjust the balance between content-based and collaborative filtering:

```python
recommender = HybridRecommender(
    content_weight=0.5,      # 50% content-based
    collaborative_weight=0.5  # 50% collaborative
)
```

### Evaluation Metrics
Calculate metrics at different K values:

```python
from recommendation_system.evaluation import evaluate_model

results = evaluate_model(
    model=recommender,
    test_data=[...],
    k_values=[5, 10, 20]
)
```

## 📊 How It Works

### Content-Based Filtering
1. Extract rich metadata (genres, director, cast, tags, overview)
2. Combine into feature strings
3. Apply TF-IDF vectorization
4. Compute cosine similarity
5. Recommend similar movies

### Collaborative Filtering
1. Build user-item rating matrix
2. Apply SVD matrix factorization
3. Find similar users
4. Recommend movies liked by similar users

### Hybrid Combination
1. Get recommendations from both approaches
2. Weight and combine scores
3. Generate personalized explanations
4. Return top N recommendations

## 🎨 UI/UX

The original React UI is preserved with:
- Search functionality
- Movie selection
- Mood-based filtering
- Genre blending
- Watch list management

## 📈 Evaluation

The system includes comprehensive evaluation metrics:
- **Precision@K**: Measures recommendation accuracy
- **Recall@K**: Measures recommendation coverage
- **NDCG@K**: Measures ranking quality
- **MAP**: Overall recommendation quality

## 🔮 Future Enhancements

- [ ] Real-time user preference learning
- [ ] Advanced deep learning models
- [ ] Multi-modal features (images, trailers)
- [ ] Explainable AI visualizations
- [ ] A/B testing framework

## 📝 License

MIT License

## 👤 Author

Aylin Vahabova
