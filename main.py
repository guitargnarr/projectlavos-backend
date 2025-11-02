"""
Project Lavos - AI Demos Backend
Matthew Scott - Louisville AI Consultant

Consolidated API for business demonstrations:
- Sentiment Analysis (customer feedback)
- Lead Scoring (sales prioritization)
- Phishing Detection (email security)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Project Lavos - AI Demos",
    description="Practical AI tools for Louisville businesses - Matthew Scott",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS - allow frontend to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# MODELS (Request/Response schemas)
# ============================================================================

class SentimentRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="Text to analyze")

class SentimentResponse(BaseModel):
    sentiment: str
    confidence: float
    explanation: str

class LeadRequest(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    company: Optional[str] = None
    budget: Optional[str] = None
    timeline: Optional[str] = None

class LeadResponse(BaseModel):
    score: int  # 0-100
    priority: str  # High, Medium, Low
    reasoning: str
    next_action: str

class PhishingRequest(BaseModel):
    sender: str
    subject: str
    body: str

class PhishingResponse(BaseModel):
    is_phishing: bool
    confidence: float
    risk_level: str  # Safe, Suspicious, Dangerous
    indicators: List[str]
    recommendation: str

# ============================================================================
# DEMO 1: SENTIMENT ANALYSIS
# ============================================================================

def analyze_sentiment_simple(text: str) -> Dict:
    """
    Simple sentiment analysis using keyword-based approach
    In production, use transformers model from sentiment-analysis-api
    For demo: Fast, reliable, good enough
    """
    text_lower = text.lower()

    # Positive indicators
    positive_words = ['great', 'excellent', 'amazing', 'love', 'fantastic',
                     'wonderful', 'best', 'awesome', 'perfect', 'outstanding']
    # Negative indicators
    negative_words = ['terrible', 'awful', 'horrible', 'hate', 'worst',
                     'disgusting', 'disappointing', 'poor', 'bad', 'never']

    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)

    if positive_count > negative_count:
        sentiment = "positive"
        confidence = min(0.6 + (positive_count * 0.1), 0.95)
        explanation = f"Detected {positive_count} positive indicators. Text expresses satisfaction."
    elif negative_count > positive_count:
        sentiment = "negative"
        confidence = min(0.6 + (negative_count * 0.1), 0.95)
        explanation = f"Detected {negative_count} negative indicators. Text expresses dissatisfaction."
    else:
        sentiment = "neutral"
        confidence = 0.6
        explanation = "No strong sentiment indicators detected. Text is balanced."

    return {
        "sentiment": sentiment,
        "confidence": round(confidence, 2),
        "explanation": explanation
    }

@app.post("/api/sentiment", response_model=SentimentResponse)
async def sentiment_analysis(request: SentimentRequest):
    """
    Analyze sentiment of customer reviews, feedback, or any text.
    Returns: positive/negative/neutral with confidence score
    """
    try:
        result = analyze_sentiment_simple(request.text)
        return SentimentResponse(**result)
    except Exception as e:
        logger.error(f"Sentiment analysis error: {e}")
        raise HTTPException(status_code=500, detail="Analysis failed")

# ============================================================================
# DEMO 2: LEAD SCORING
# ============================================================================

def score_lead_simple(lead: LeadRequest) -> Dict:
    """
    Score sales leads based on qualification criteria
    In production: Use ML model from apartment-leasing-demo
    For demo: Rule-based scoring
    """
    score = 0
    indicators = []

    # Email provided
    if lead.email and '@' in lead.email:
        score += 20
        indicators.append("Valid email provided")

    # Phone provided
    if lead.phone:
        score += 15
        indicators.append("Phone contact available")

    # Company provided (B2B indicator)
    if lead.company:
        score += 20
        indicators.append("Business inquiry")

    # Budget indicated
    if lead.budget:
        budget_lower = lead.budget.lower()
        if any(term in budget_lower for term in ['50k', '100k', 'enterprise', 'unlimited']):
            score += 25
            indicators.append("High budget potential")
        elif any(term in budget_lower for term in ['10k', '20k', '30k']):
            score += 15
            indicators.append("Medium budget")
        else:
            score += 5
            indicators.append("Budget mentioned")

    # Timeline indicated (urgency)
    if lead.timeline:
        timeline_lower = lead.timeline.lower()
        if any(term in timeline_lower for term in ['asap', 'urgent', 'immediately', 'this week']):
            score += 20
            indicators.append("Urgent timeline - high priority")
        elif any(term in timeline_lower for term in ['month', '30 days']):
            score += 10
            indicators.append("Near-term timeline")
        else:
            score += 5
            indicators.append("Timeline provided")

    # Determine priority
    if score >= 70:
        priority = "High"
        next_action = "Contact within 24 hours - strong qualified lead"
    elif score >= 40:
        priority = "Medium"
        next_action = "Contact within 48-72 hours - needs qualification"
    else:
        priority = "Low"
        next_action = "Add to nurture campaign - incomplete information"

    reasoning = f"Lead scored {score}/100 based on: {', '.join(indicators) if indicators else 'minimal information provided'}"

    return {
        "score": score,
        "priority": priority,
        "reasoning": reasoning,
        "next_action": next_action
    }

@app.post("/api/leads", response_model=LeadResponse)
async def lead_scoring(request: LeadRequest):
    """
    Score and prioritize sales leads based on qualification criteria.
    Returns: Priority score, suggested action, reasoning
    """
    try:
        result = score_lead_simple(request)
        return LeadResponse(**result)
    except Exception as e:
        logger.error(f"Lead scoring error: {e}")
        raise HTTPException(status_code=500, detail="Scoring failed")

# ============================================================================
# DEMO 3: PHISHING DETECTION
# ============================================================================

def detect_phishing_simple(sender: str, subject: str, body: str) -> Dict:
    """
    Detect potential phishing emails using pattern matching
    In production: Use 7-model ensemble from phishguard-ml
    For demo: Rule-based detection
    """
    risk_indicators = []
    risk_score = 0

    # Suspicious sender patterns
    suspicious_domains = ['@gmail.com', '@yahoo.com', '@outlook.com', '@hotmail.com']
    if any(domain in sender.lower() for domain in suspicious_domains):
        risk_score += 20
        risk_indicators.append("Personal email domain (not business)")

    # Urgent language in subject
    urgent_terms = ['urgent', 'immediate', 'action required', 'verify', 'suspended', 'expires']
    if any(term in subject.lower() for term in urgent_terms):
        risk_score += 25
        risk_indicators.append(f"Urgent language in subject: '{subject}'")

    # Suspicious body content
    phishing_keywords = ['click here', 'verify account', 'confirm identity', 'reset password',
                        'wire transfer', 'bank account', 'social security', 'gift card']
    body_lower = body.lower()
    found_keywords = [kw for kw in phishing_keywords if kw in body_lower]
    if found_keywords:
        risk_score += len(found_keywords) * 15
        risk_indicators.append(f"Phishing keywords: {', '.join(found_keywords)}")

    # Links with mismatched domains
    if 'http' in body_lower and ('<a' in body_lower or 'href' in body_lower):
        risk_score += 20
        risk_indicators.append("Contains links (verify before clicking)")

    # Spelling/grammar issues (simple check)
    if any(term in body_lower for term in ['dear customer', 'dear user', 'dear member']):
        risk_score += 15
        risk_indicators.append("Generic greeting (not personalized)")

    # Determine risk level
    if risk_score >= 60:
        is_phishing = True
        risk_level = "Dangerous"
        recommendation = "DO NOT RESPOND. Delete immediately. Likely phishing attempt."
        confidence = min(risk_score / 100, 0.95)
    elif risk_score >= 30:
        is_phishing = False
        risk_level = "Suspicious"
        recommendation = "CAUTION. Verify sender authenticity before responding or clicking links."
        confidence = risk_score / 100
    else:
        is_phishing = False
        risk_level = "Safe"
        recommendation = "Email appears legitimate, but always verify before sharing sensitive information."
        confidence = 0.85

    return {
        "is_phishing": is_phishing,
        "confidence": round(confidence, 2),
        "risk_level": risk_level,
        "indicators": risk_indicators if risk_indicators else ["No significant risk indicators found"],
        "recommendation": recommendation
    }

@app.post("/api/phishing", response_model=PhishingResponse)
async def phishing_detection(request: PhishingRequest):
    """
    Detect potential phishing emails based on sender, subject, and content.
    Returns: Risk assessment, indicators, and recommended action
    """
    try:
        result = detect_phishing_simple(request.sender, request.subject, request.body)
        return PhishingResponse(**result)
    except Exception as e:
        logger.error(f"Phishing detection error: {e}")
        raise HTTPException(status_code=500, detail="Detection failed")

# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@app.get("/")
def root():
    """API information and available endpoints"""
    return {
        "name": "Project Lavos - AI Demos API",
        "consultant": "Matthew Scott",
        "location": "Louisville, KY",
        "demos": {
            "sentiment": "/api/sentiment - Analyze text sentiment",
            "leads": "/api/leads - Score sales leads",
            "phishing": "/api/phishing - Detect phishing emails"
        },
        "website": "https://projectlavos.com",
        "portfolio": "https://jaspermatters.com",
        "github": "https://github.com/guitargnarr"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "demos_available": 3,
        "version": "1.0.0"
    }

# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
