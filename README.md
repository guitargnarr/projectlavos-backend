# Project Lavos - AI Demos Backend

Backend API for [projectlavos.com](https://projectlavos.com)

**Consultant:** Matthew Scott - Louisville, KY
**Portfolio:** [jaspermatters.com](https://jaspermatters.com)
**GitHub:** [guitargnarr](https://github.com/guitargnarr)

## Demos

- **POST /api/sentiment** - Sentiment analysis for customer reviews
- **POST /api/leads** - Lead scoring for sales prioritization
- **POST /api/phishing** - Phishing detection for email security

## Quick Start

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Visit http://localhost:8000/docs for interactive API documentation.

## Deployment

Deployed on Render.com:
- Production URL: https://projectlavos-api.onrender.com
- Health check: https://projectlavos-api.onrender.com/health

## Tech Stack

- FastAPI 0.104+
- Python 3.11+
- Pydantic for validation
- CORS enabled for frontend integration
