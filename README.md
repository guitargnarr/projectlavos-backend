# Project Lavos Backend

**Status**: ✅ Live on Render.com

FastAPI backend powering [projectlavos.com](https://projectlavos.com) AI demos with Claude Haiku API integration.

![Python](https://img.shields.io/badge/Python-3.14-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green) ![Claude](https://img.shields.io/badge/Claude-Haiku-purple)

---

## 🚀 API Endpoints

### Health Check
```http
GET /health
```
Returns API status and version info.

**Response**:
```json
{
  "status": "healthy",
  "demos_available": 6,
  "version": "1.4.0"
}
```

---

### 1. Restaurant Analyzer
```http
POST /api/analyze-restaurant
Content-Type: application/json

{
  "restaurant_name": "Jack Fry's"
}
```

Analyzes Louisville restaurant reviews with Claude Haiku.

**Features**:
- 5 Louisville restaurants × 20 authentic reviews (100 reviews total)
- Overall sentiment score (0-5)
- Key themes with mention counts
- Sample positive/negative reviews
- 3-4 actionable recommendations

**Restaurants**:
- Jack Fry's (upscale Southern)
- Proof on Main (contemporary American)
- Hammerheads (gastropub)
- Bourbon Raw (seafood & sushi)
- Milkwood (modern American)

---

### 2. Email Scorer
```http
POST /api/score-email
Content-Type: application/json

{
  "email_subject": "Quick question about your AI needs",
  "email_body": "Hi [Name], I noticed..."
}
```

Scores B2B sales emails 1-10 with specific improvement suggestions.

**Output**: Score + 4-6 actionable improvements (subject line, personalization, CTA, etc.)

---

### 3. Sentiment Analysis
```http
POST /api/analyze-sentiment
Content-Type: application/json

{
  "text": "This product exceeded my expectations!"
}
```

Real-time emotion detection with confidence scores.

---

### 4. Lead Scoring
```http
POST /api/score-lead
Content-Type: application/json

{
  "company_size": "50-200",
  "industry": "Healthcare",
  "budget": "$50K+"
}
```

Sales lead qualification calculator.

---

### 5. Phishing Detection
```http
POST /api/detect-phishing
Content-Type: application/json

{
  "email_subject": "Urgent: Verify your account",
  "email_body": "Click here immediately..."
}
```

Email security scanner with threat level assessment.

---

### 6. Prompt Engineering (Showcase)
```http
POST /api/prompt-demo
Content-Type: application/json

{
  "technique": "chain-of-thought",
  "context": "Write a professional email..."
}
```

Demonstrates 5 advanced LLM prompting techniques:
- Zero-shot
- Few-shot
- Chain-of-thought
- Role-based
- Structured output

---

## 🛠️ Tech Stack

- **Framework**: FastAPI 0.115+
- **LLM Integration**: Anthropic SDK (Claude Haiku)
- **Python**: 3.14
- **Hosting**: Render.com ($7/month starter tier)
- **Deployment**: GitHub Actions webhook automation
- **CORS**: Configured for projectlavos.com subdomains

---

## ⚡ Quick Start

### Prerequisites
- Python 3.14+
- Anthropic API key

### Local Development

```bash
# Clone the repo
git clone https://github.com/guitargnarr/projectlavos-backend.git
cd projectlavos-backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variable
export ANTHROPIC_API_KEY="your-key-here"

# Run dev server
uvicorn main:app --reload --port 8000
```

**Dev server**: http://localhost:8000

**API docs**: http://localhost:8000/docs (Swagger UI)

---

## 🚢 Deployment

**Automatic**: Push to `main` triggers GitHub Actions → Render webhook

**Manual**:
1. Push to GitHub
2. Render auto-deploys from `main` branch
3. Live at: https://projectlavos-backend.onrender.com

**Environment Variables on Render**:
- `ANTHROPIC_API_KEY`: Your Claude API key

---

## 📊 Cost Analysis

**Claude Haiku Pricing**:
- $0.001 per demo analysis
- 98% cost savings vs Opus ($0.001 vs $0.05)
- 1,000 analyses = $1 (sustainable for demos)

**Hosting**:
- Render Starter: $7/month (30s cold start acceptable)
- Free tier alternative: $0/month (longer cold starts)

---

## 🎯 Data Strategy

**Week 2** (Current): Static JSON files
- 5 restaurants × 20 reviews = 100 reviews
- Fast, free, controlled demo experience
- No API rate limits

**Week 3** (Future): Google Places API integration
- IF restaurant owners respond to outreach
- Real-time review fetching
- Rationale: Validate demand before API investment

---

## 🏗️ Architecture

```
Frontend (Vercel)     Backend (Render)      LLM (Anthropic)
    ↓                      ↓                     ↓
demos.projectlavos.com → FastAPI Server → Claude Haiku API
                           ↓
                      Static JSON Data
                   (restaurant reviews)
```

**Flow**:
1. User selects demo on frontend
2. Frontend POSTs to `/api/*` endpoint
3. Backend constructs prompt with data
4. Claude Haiku analyzes (3-5s)
5. Backend returns structured JSON
6. Frontend displays results

---

## 📝 Why I Built This

Louisville SMBs need tangible AI value, not buzzwords. These demos prove capability with their actual use cases before consultation.

**"Show, Don't Tell" Strategy**: Let business owners try AI with familiar data (their restaurants, their emails).

---

## 📧 Contact

**Author**: Matthew David Scott
**Email**: matthewdscott7@gmail.com
**Website**: [projectlavos.com](https://projectlavos.com)
**GitHub**: [guitargnarr](https://github.com/guitargnarr)

---

## 📄 License

Proprietary - © 2025 Matthew David Scott
