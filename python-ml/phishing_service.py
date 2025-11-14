#!/usr/bin/env python3
"""
PhishGuard ML Ensemble Service
Enhances phishing detection with ML + heuristic ensemble
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import pickle
import numpy as np
import re
from pathlib import Path

app = FastAPI(title="PhishGuard ML Ensemble", version="1.0.0")

# Load models at startup
MODEL_DIR = Path("/app/models")  # Will be mounted in Docker
MODELS_LOADED = False
classifier = None
vectorizer = None
metadata = None

class PhishingRequest(BaseModel):
    features: List[float]  # 39 features from C++ extractor
    text: str = ""  # Optional raw text for additional analysis

class PhishingResponse(BaseModel):
    risk_level: str  # "Safe", "Suspicious", "Dangerous"
    confidence: float
    risk_score: int
    detection_methods: List[str]
    indicators: List[str]

def load_models():
    """Load the PhishGuard models"""
    global classifier, vectorizer, metadata, MODELS_LOADED

    try:
        # Try to load from mounted volume first
        if MODEL_DIR.exists():
            with open(MODEL_DIR / "phishing_clf.pkl", 'rb') as f:
                classifier = pickle.load(f)
            with open(MODEL_DIR / "tfidf_vec.pkl", 'rb') as f:
                vectorizer = pickle.load(f)
            with open(MODEL_DIR / "model_metadata.pkl", 'rb') as f:
                metadata = pickle.load(f)
            MODELS_LOADED = True
            print("✅ PhishGuard models loaded successfully")
        else:
            print("⚠️ Models directory not found, using heuristics only")

    except Exception as e:
        print(f"⚠️ Could not load ML models: {e}")
        print("   Falling back to heuristic detection only")

def heuristic_detection(features: List[float], text: str = "") -> Dict[str, Any]:
    """
    Enhanced heuristic phishing detection
    Uses the 39 features from C++ extractor
    """
    risk_score = 0
    indicators = []
    methods = ["heuristic_analysis"]

    # Feature indices (from PhishGuard feature set)
    # 0-9: URL features
    # 10-19: Domain features
    # 20-29: Content features
    # 30-38: Additional security features

    # Check URL features
    if len(features) >= 39:
        # Suspicious URL length (feature 0)
        if features[0] > 100:
            risk_score += 15
            indicators.append("excessive_url_length")

        # Too many dots in URL (feature 2)
        if features[2] > 5:
            risk_score += 10
            indicators.append("suspicious_dots_count")

        # Has @ symbol (feature 5)
        if features[5] > 0:
            risk_score += 25
            indicators.append("at_symbol_in_url")

        # Suspicious port (feature 8)
        if features[8] != 80 and features[8] != 443 and features[8] > 0:
            risk_score += 20
            indicators.append("non_standard_port")

        # IP address instead of domain (feature 10)
        if features[10] > 0:
            risk_score += 30
            indicators.append("ip_address_used")

        # Too many subdomains (feature 12)
        if features[12] > 3:
            risk_score += 15
            indicators.append("excessive_subdomains")

        # Shortened URL (feature 15)
        if features[15] > 0:
            risk_score += 25
            indicators.append("url_shortener_used")

        # No HTTPS (feature 18)
        if features[18] == 0:
            risk_score += 10
            indicators.append("no_https")

        # Suspicious keywords count (feature 25)
        if features[25] > 3:
            risk_score += 20
            indicators.append("phishing_keywords_detected")

        # Urgency indicators (feature 30)
        if features[30] > 2:
            risk_score += 15
            indicators.append("urgency_language")

    # Additional text analysis if provided
    if text:
        text_lower = text.lower()

        # Check for common phishing patterns (increased scores)
        phishing_patterns = [
            (r"verify.{0,20}account", 35, "verify_account_request"),
            (r"suspend", 30, "suspension_threat"),
            (r"click.{0,10}here|click.{0,10}now", 35, "click_bait"),
            (r"urgent|immediate|expire", 25, "urgency_words"),
            (r"congratulations|winner|won", 30, "prize_scam"),
            (r"refund|tax|invoice", 20, "financial_lure"),
            (r"security.{0,10}alert|breach", 30, "security_scare"),
            (r"limited.{0,10}time|act.{0,10}now", 25, "time_pressure"),
            (r"final.{0,10}warning|last.{0,10}chance", 30, "final_warning"),
            (r"bit\.ly|tinyurl|short\.link", 35, "url_shortener_bonus"),
        ]

        for pattern, points, indicator in phishing_patterns:
            if re.search(pattern, text_lower):
                risk_score += points
                indicators.append(indicator)
                if "pattern_matching" not in methods:
                    methods.append("pattern_matching")

    return {
        "risk_score": min(risk_score, 100),
        "indicators": indicators,
        "methods": methods
    }

def ml_detection(features: List[float]) -> Dict[str, Any]:
    """
    ML-based detection using PhishGuard classifier
    """
    if not MODELS_LOADED or classifier is None:
        return None

    try:
        # Reshape features for sklearn
        X = np.array(features).reshape(1, -1)

        # Get prediction and probability
        prediction = classifier.predict(X)[0]
        proba = classifier.predict_proba(X)[0]

        # Convert to risk score (0-100)
        risk_probability = proba[1] if len(proba) > 1 else proba[0]
        risk_score = int(risk_probability * 100)

        indicators = []
        if prediction == 1:
            indicators.append("ml_classifier_positive")

        return {
            "risk_score": risk_score,
            "confidence": float(max(proba)),
            "indicators": indicators,
            "methods": ["ml_classifier"]
        }
    except Exception as e:
        print(f"ML detection error: {e}")
        return None

def ensemble_voting(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Combine multiple detection methods into final verdict
    """
    if not results:
        return {
            "risk_level": "Unknown",
            "confidence": 0.0,
            "risk_score": 0,
            "indicators": [],
            "methods": []
        }

    # Aggregate scores and indicators
    total_score = 0
    all_indicators = []
    all_methods = []
    weights = []

    for result in results:
        if result:
            score = result.get("risk_score", 0)
            total_score += score
            weights.append(score)
            all_indicators.extend(result.get("indicators", []))
            all_methods.extend(result.get("methods", []))

    # Calculate weighted average
    avg_score = total_score / len(results) if results else 0

    # Boost score if multiple methods agree
    if len([r for r in results if r and r.get("risk_score", 0) > 50]) >= 1:
        avg_score = min(avg_score * 1.3, 100)

    # Determine risk level with adjusted thresholds
    if avg_score >= 60:  # Lowered from 70
        risk_level = "Dangerous"
    elif avg_score >= 35:  # Lowered from 40
        risk_level = "Suspicious"
    else:
        risk_level = "Safe"

    # Calculate confidence
    confidence = min(0.5 + (len(all_methods) * 0.25), 0.95)

    return {
        "risk_level": risk_level,
        "confidence": confidence,
        "risk_score": int(avg_score),
        "indicators": list(set(all_indicators)),
        "methods": list(set(all_methods))
    }

@app.on_event("startup")
async def startup_event():
    """Load models when service starts"""
    load_models()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "phishing-ml-ensemble",
        "models_loaded": MODELS_LOADED
    }

@app.post("/classify-ensemble", response_model=PhishingResponse)
async def classify_phishing(request: PhishingRequest):
    """
    Ensemble phishing classification
    Combines ML model with heuristic analysis
    """
    try:
        results = []

        # Run heuristic detection
        heuristic_result = heuristic_detection(request.features, request.text)
        results.append(heuristic_result)

        # Run ML detection if models are loaded
        if MODELS_LOADED:
            ml_result = ml_detection(request.features)
            if ml_result:
                results.append(ml_result)

        # Combine results
        final_result = ensemble_voting(results)

        return PhishingResponse(**final_result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9001)