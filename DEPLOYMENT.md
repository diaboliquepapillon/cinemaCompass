# CinemaCompass Deployment Guide

Complete guide for deploying CinemaCompass to production.

## Prerequisites

- Docker and Docker Compose installed
- PostgreSQL database (managed or self-hosted)
- Redis instance (optional but recommended)
- TMDb API key
- Domain name (for production)

## Local Development Setup

### Using Docker Compose

1. **Clone and navigate to project**
   ```bash
   cd cinemaCompass
   ```

2. **Set environment variables**
   Create `.env` file:
   ```env
   DATABASE_URL=postgresql://cinemacompass:password@postgres:5432/cinemacompass
   REDIS_URL=redis://redis:6379
   JWT_SECRET_KEY=your-secret-key-change-in-production
   TMDB_API_KEY=your_tmdb_api_key
   ```

3. **Start services**
   ```bash
   docker-compose up -d
   ```

4. **Initialize database**
   ```bash
   docker-compose exec backend python -c "from backend.api.models.database import init_db; init_db()"
   ```

5. **Access services**
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - PostgreSQL: localhost:5432
   - Redis: localhost:6379

### Manual Setup

**Backend:**
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL=sqlite:///./cinemacompass.db
export JWT_SECRET_KEY=dev-secret-key

# Run migrations
python -c "from backend.api.models.database import init_db; init_db()"

# Start server
python backend/run_api.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Production Deployment

### Option 1: Render (Recommended for MVP)

**Backend Deployment:**

1. Create new Web Service on Render
2. Connect your GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn backend.api.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables:
   - `DATABASE_URL` (from PostgreSQL service)
   - `REDIS_URL` (from Redis service)
   - `JWT_SECRET_KEY`
   - `TMDB_API_KEY`

**PostgreSQL Database:**

1. Create new PostgreSQL service on Render
2. Copy connection string to `DATABASE_URL`
3. Run migrations:
   ```bash
   psql $DATABASE_URL -f backend/database_schema.sql
   ```

**Redis:**

1. Use Upstash (serverless Redis)
2. Copy connection string to `REDIS_URL`

**Frontend Deployment:**

1. Create new Static Site on Render
2. Build command: `cd frontend && npm install && npm run build`
3. Publish directory: `frontend/.next`
4. Set environment variable:
   - `NEXT_PUBLIC_API_URL=https://your-backend.onrender.com`

### Option 2: Railway

**Backend:**

1. Create new project on Railway
2. Connect GitHub repository
3. Add PostgreSQL service
4. Add Redis service
5. Set environment variables
6. Deploy

**Frontend:**

1. Use Vercel for Next.js deployment
2. Connect GitHub repository
3. Set build settings:
   - Framework: Next.js
   - Root directory: `frontend`
4. Add environment variables

### Option 3: AWS (Scalable)

**Architecture:**
- EC2 or ECS for backend
- RDS PostgreSQL
- ElastiCache Redis
- S3 for static assets
- CloudFront CDN
- ALB for load balancing

**Deployment Steps:**

1. Build Docker image:
   ```bash
   docker build -t cinemacompass-backend .
   docker tag cinemacompass-backend:latest your-ecr-repo/cinemacompass:latest
   docker push your-ecr-repo/cinemacompass:latest
   ```

2. Create ECS service or EC2 instance
3. Configure RDS PostgreSQL
4. Set up ElastiCache Redis
5. Configure environment variables
6. Set up CloudFront for CDN

## Environment Variables

### Required
```env
DATABASE_URL=postgresql://user:password@host:5432/dbname
JWT_SECRET_KEY=your-secure-random-secret-key
```

### Optional but Recommended
```env
REDIS_URL=redis://host:6379
TMDB_API_KEY=your_tmdb_api_key
PORT=8000
LOG_LEVEL=INFO
```

### Frontend
```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

## Database Migrations

### Initial Setup

```bash
# Using SQLAlchemy
python -c "from backend.api.models.database import init_db; init_db()"

# Or using SQL script
psql $DATABASE_URL -f backend/database_schema.sql
```

### Alembic (Future)

```bash
# Initialize
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head
```

## Monitoring & Logging

### Health Checks

Backend health endpoint:
```bash
curl http://localhost:8000/api/health
```

### Logging

Configure logging in `backend/api/main.py`:
```python
import logging
logging.basicConfig(level=logging.INFO)
```

### Monitoring Tools

- **Application**: Use Streamlit admin dashboard
- **Infrastructure**: CloudWatch (AWS), Datadog, or Prometheus
- **Error Tracking**: Sentry

## Scaling Considerations

### Horizontal Scaling

- Use load balancer (ALB, NLB) for multiple backend instances
- Ensure Redis is shared across instances
- Use connection pooling for PostgreSQL

### Caching Strategy

- Cache recommendations for active users (TTL: 1 hour)
- Cache movie metadata (TTL: 24 hours)
- Pre-compute popular recommendations (daily batch)

### Database Optimization

- Add indexes on frequently queried columns
- Use read replicas for read-heavy workloads
- Implement connection pooling

## Security Checklist

- [ ] Use HTTPS for all endpoints
- [ ] Set strong `JWT_SECRET_KEY`
- [ ] Enable CORS only for allowed origins
- [ ] Use environment variables for secrets
- [ ] Implement rate limiting
- [ ] Use parameterized queries (SQLAlchemy handles this)
- [ ] Regular security updates
- [ ] Enable database backups

## Troubleshooting

### Backend won't start

1. Check environment variables
2. Verify database connection
3. Check port availability
4. Review logs: `docker-compose logs backend`

### Database connection errors

1. Verify `DATABASE_URL` format
2. Check database is running
3. Verify credentials
4. Check network connectivity

### Redis connection errors

1. Redis is optional - will fallback to in-memory cache
2. Check `REDIS_URL` format
3. Verify Redis is running

### Frontend can't connect to API

1. Check `NEXT_PUBLIC_API_URL` environment variable
2. Verify CORS settings in backend
3. Check network/firewall rules

## CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/deploy.yml`):

- Runs tests on push
- Builds Docker image
- Deploys to staging on merge to `develop`
- Deploys to production on merge to `main`

Configure secrets in GitHub:
- `RENDER_API_KEY`
- `RENDER_SERVICE_ID`
- Deployment credentials

## Performance Optimization

1. **Enable Gzip compression**
2. **Use CDN for static assets**
3. **Implement request caching**
4. **Optimize database queries**
5. **Use Redis for session storage**
6. **Enable async/await throughout**

## Backup Strategy

### Database Backups

```bash
# PostgreSQL dump
pg_dump $DATABASE_URL > backup.sql

# Restore
psql $DATABASE_URL < backup.sql
```

### Automated Backups

- Use managed database service with automatic backups
- Or schedule cron job for regular dumps

## Support

For deployment issues, refer to:
- Docker documentation
- Platform-specific documentation (Render, Railway, AWS)
- GitHub Issues

