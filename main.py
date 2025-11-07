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
import os
import json
from pathlib import Path
from anthropic import Anthropic

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Project Lavos - AI Demos",
    description="Practical AI tools for Louisville businesses - Matthew Scott",
    version="1.2.1",
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


class PromptRequest(BaseModel):
    technique: str  # zero-shot, few-shot, chain-of-thought, role-based, structured
    use_case: str  # email, blog, summary, custom
    context: str = Field(..., min_length=10, max_length=2000)
    tone: str  # professional, technical, casual, persuasive


class PromptResponse(BaseModel):
    generated_content: str
    prompt_used: Dict[str, str]  # {"system": "...", "user": "..."}
    technique_name: str
    explanation: str


class ContactRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=3, max_length=200)
    businessType: str = Field(..., min_length=1, max_length=100)
    challenge: str = Field(..., min_length=10, max_length=2000)


class ContactResponse(BaseModel):
    success: bool
    message: str


class RestaurantRequest(BaseModel):
    restaurant_name: str = Field(..., min_length=1, max_length=200, description="Restaurant name to analyze")
    location: Optional[str] = Field("Louisville, KY", max_length=100)


class Theme(BaseModel):
    theme: str
    mentions: int
    sentiment: str  # positive, negative, mixed


class RestaurantResponse(BaseModel):
    restaurant: str
    location: str
    overall_sentiment: float  # 0-5
    total_reviews_analyzed: int
    themes: List[Theme]
    sample_positive: str
    sample_negative: str
    recommendations: List[str]

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
# DEMO 4: PROMPT ENGINEERING PLAYGROUND
# ============================================================================

# Initialize Anthropic client
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))


def build_zero_shot_prompt(use_case: str, context: str, tone: str) -> tuple:
    """
    Zero-shot: Direct request with role definition, no examples
    Best for: Simple tasks, general knowledge, straightforward generation
    """
    system_prompt = f"You are a professional {use_case} writer with expertise in creating clear, compelling content."

    user_prompt = f"""Write a {use_case} with the following specifications:

Context: {context}
Tone: {tone}
Length: Appropriate for a {use_case}

Requirements:
- Be clear and concise
- Match the requested tone
- Make it actionable and engaging"""

    explanation = """**Zero-Shot Prompting**

What it is: Direct instruction without examples. The model uses its training to understand the task.

Why it works: Modern LLMs are trained on vast amounts of text and can generalize well to new tasks without explicit examples.

When to use: Simple, well-defined tasks where the model's general knowledge is sufficient. Fastest and most token-efficient approach.

Strengths: Fast, token-efficient, works for most common tasks
Limitations: May struggle with highly specific formats or uncommon tasks"""

    return system_prompt, user_prompt, explanation


def build_few_shot_prompt(use_case: str, context: str, tone: str) -> tuple:
    """
    Few-shot: Include 2-3 examples to guide the model's output
    Best for: Specific formats, style consistency, pattern replication
    """
    # Define examples based on use case
    examples = {
        "email": [
            {"input": "Meeting reschedule",
             "output": "Subject: Rescheduling Our Meeting - New Time Proposed\n\nHi [Name],\n\nI hope this email finds you well. Unfortunately, I need to reschedule our meeting originally planned for [date/time]. Would [new date/time] work for your schedule?\n\nI apologize for any inconvenience and look forward to connecting soon.\n\nBest regards,\n[Your name]"},
            {"input": "Project update",
             "output": "Subject: Weekly Project Update - On Track\n\nHi Team,\n\nQuick update on Project X: We've completed Phase 1 (design) and are moving into Phase 2 (development) as planned. Timeline remains on schedule for Q2 delivery.\n\nNext steps: Engineering kick-off meeting this Thursday.\n\nLet me know if you have questions.\n\nBest,\n[Your name]"}
        ],
        "blog": [
            {"input": "AI in healthcare", "output": "# The AI Revolution in Healthcare: What Doctors and Patients Need to Know\n\nArtificial intelligence is transforming healthcare at an unprecedented pace. From diagnostic imaging to treatment planning, AI systems are augmenting—not replacing—the expertise of medical professionals.\n\nHere's what you need to know about this revolution..."},
        ]
    }

    example_text = ""
    if use_case.lower() in examples:
        for i, ex in enumerate(examples[use_case.lower()][:2], 1):
            example_text += f"\nExample {i}:\nContext: {ex['input']}\nOutput:\n{ex['output']}\n"

    system_prompt = f"You are an expert {use_case} writer. Follow the style and format shown in the examples below."

    user_prompt = f"""You will write content following the patterns shown in these examples:
{example_text if example_text else 'Follow professional standards for ' + use_case + ' writing.'}

Now write a {use_case} with these specifications:
Context: {context}
Tone: {tone}

Match the format and style from the examples above."""

    explanation = """**Few-Shot Prompting**

What it is: Provide 2-5 examples of the desired output format before the actual request. The model learns the pattern from examples.

Why it works: LLMs excel at pattern recognition. Concrete examples clarify expectations better than abstract instructions.

When to use: When you need specific formatting, consistent style across outputs, or the task is unusual/specialized.

Strengths: Better accuracy for specific formats, style consistency, handles edge cases
Limitations: Uses more tokens (costs more), examples must be high-quality"""

    return system_prompt, user_prompt, explanation


def build_chain_of_thought_prompt(use_case: str, context: str, tone: str) -> tuple:
    """
    Chain-of-thought: Request step-by-step reasoning before the final output
    Best for: Complex tasks, ensuring quality, transparent decision-making
    """
    system_prompt = f"You are an expert {use_case} writer who thinks carefully through each aspect before writing."

    user_prompt = f"""I need you to write a {use_case}. Before writing the final version, please think through this step-by-step:

Context: {context}
Tone: {tone}

Please follow this thought process:
1. First, identify the key message and goal
2. Consider the audience and what they need to know
3. Outline the main points to cover
4. Choose the most effective structure
5. Write the final version

Show your reasoning for steps 1-4, then provide the final polished {use_case}."""

    explanation = """**Chain-of-Thought Prompting**

What it is: Ask the model to "think out loud" and show its reasoning process before generating the final output.

Why it works: Breaking complex tasks into steps improves accuracy. The model's intermediate reasoning helps it avoid errors and produce better final outputs.

When to use: Complex tasks requiring planning, quality-critical outputs, when you want to verify the reasoning behind the output.

Strengths: Higher accuracy on complex tasks, transparent reasoning, catches logical errors
Limitations: Much longer responses (higher cost/latency), verbose output"""

    return system_prompt, user_prompt, explanation


def build_role_based_prompt(use_case: str, context: str, tone: str) -> tuple:
    """
    Role-based: Assign expert persona with specific expertise and perspective
    Best for: Specialized content, authoritative voice, technical accuracy
    """
    roles = {
        "email": "senior business communications expert with 15 years of experience in professional correspondence",
        "blog": "professional content strategist and storyteller who creates engaging, SEO-optimized articles",
        "summary": "executive briefing specialist who distills complex information into clear, actionable insights",
        "custom": "versatile professional writer with expertise across multiple domains"
    }

    role = roles.get(use_case.lower(), roles["custom"])

    system_prompt = f"""You are a {role}.

Your expertise includes:
- Understanding audience needs and context
- Crafting messages that achieve specific goals
- Maintaining appropriate tone and professionalism
- Delivering clear, actionable content

Apply your professional judgment and experience to this task."""

    user_prompt = f"""As an expert in your field, please create a {use_case} for this situation:

Context: {context}
Desired tone: {tone}

Use your expertise to determine:
- The most effective structure
- Key points to emphasize
- Appropriate level of detail
- Best practices for this type of communication

Deliver a polished, professional result."""

    explanation = """**Role-Based Prompting**

What it is: Assign the model a specific expert role/persona with defined expertise, perspective, and professional standards.

Why it works: Activating a "role" in the model's training data helps it access relevant knowledge and writing styles. The model generates content consistent with that expert's perspective.

When to use: Specialized or technical content, when you need authoritative voice, industry-specific terminology, professional standards.

Strengths: Access to specialized knowledge, appropriate professional tone, industry-standard formats
Limitations: May be overly formal, could include unnecessary technical jargon if not balanced"""

    return system_prompt, user_prompt, explanation


def build_structured_output_prompt(use_case: str, context: str, tone: str) -> tuple:
    """
    Structured output: Specify exact format (JSON, Markdown, etc.) with schema
    Best for: Programmatic use, consistent parsing, integration with other systems
    """
    system_prompt = f"You are a {use_case} writing assistant that produces well-structured, formatted content."

    user_prompt = f"""Create a {use_case} with the following requirements:

Context: {context}
Tone: {tone}

Format your response as structured content with clear sections:

## Main Content
[Your primary {use_case} content here]

## Key Points
- [Bullet point 1]
- [Bullet point 2]
- [Bullet point 3]

## Metadata
- Word count: [count]
- Tone achieved: {tone}
- Target audience: [describe]

Ensure each section is clearly marked and formatted consistently."""

    explanation = """**Structured Output Prompting**

What it is: Specify exact output format with clear schema, sections, or data structure (JSON, Markdown, XML, etc.).

Why it works: Explicit formatting instructions ensure consistent, parseable outputs. Reduces post-processing and enables programmatic use.

When to use: When outputs need to be parsed by other systems, consistency is critical, or you need to extract specific fields reliably.

Strengths: Perfect for automation, consistent format, easy to parse programmatically, no post-processing
Limitations: Less natural/conversational output, may feel rigid, requires careful schema design"""

    return system_prompt, user_prompt, explanation


async def generate_with_claude(system_prompt: str, user_prompt: str) -> str:
    """Call Claude API with the engineered prompts"""
    try:
        message = client.messages.create(
            model="claude-3-5-haiku-20241022",  # Fast, cost-efficient for demos
            max_tokens=1000,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        return message.content[0].text
    except Exception as e:
        logger.error(f"Claude API error: {e}")
        raise HTTPException(status_code=500, detail=f"LLM generation failed: {str(e)}")


@app.post("/api/prompt-engineering", response_model=PromptResponse)
async def prompt_engineering_demo(request: PromptRequest):
    """
    Demonstrate advanced prompt engineering techniques with real LLM calls.
    Techniques: zero-shot, few-shot, chain-of-thought, role-based, structured output
    """
    try:
        # Select technique and build prompts
        technique_builders = {
            "zero-shot": build_zero_shot_prompt,
            "few-shot": build_few_shot_prompt,
            "chain-of-thought": build_chain_of_thought_prompt,
            "role-based": build_role_based_prompt,
            "structured": build_structured_output_prompt
        }

        if request.technique not in technique_builders:
            raise HTTPException(status_code=400, detail=f"Unknown technique: {request.technique}")

        # Build prompts for selected technique
        builder = technique_builders[request.technique]
        system_prompt, user_prompt, explanation = builder(
            request.use_case,
            request.context,
            request.tone
        )

        # Generate content with Claude
        generated_content = await generate_with_claude(system_prompt, user_prompt)

        # Return comprehensive response
        return PromptResponse(
            generated_content=generated_content,
            prompt_used={
                "system": system_prompt,
                "user": user_prompt
            },
            technique_name=request.technique.replace("-", " ").title(),
            explanation=explanation
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prompt engineering error: {e}")
        raise HTTPException(status_code=500, detail="Demo failed")

# ============================================================================
# CONTACT FORM
# ============================================================================


@app.post("/api/contact", response_model=ContactResponse)
async def submit_contact_form(request: ContactRequest):
    """
    Handle contact form submissions from projectlavos.com
    Logs inquiries and sends notification email (future: integrate SendGrid/SMTP)
    """
    try:
        # Log the contact request (visible in Render.com logs)
        logger.info(f"""
        ========================================
        NEW CONTACT FORM SUBMISSION
        ========================================
        Name: {request.name}
        Email: {request.email}
        Business Type: {request.businessType}
        Challenge: {request.challenge}
        ========================================
        """)

        # TODO: Send email notification via SendGrid/SMTP
        # For now, logging is sufficient - user can check Render logs

        return ContactResponse(
            success=True,
            message="Thank you! Your message has been received. I'll respond within 24 hours."
        )

    except Exception as e:
        logger.error(f"Contact form error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to submit contact form. Please email matthewdscott7@gmail.com directly."
        )

# ============================================================================
# DEMO 5: RESTAURANT REVIEW ANALYZER
# ============================================================================


@app.post("/api/analyze-restaurant", response_model=RestaurantResponse)
async def analyze_restaurant(request: RestaurantRequest):
    """
    Analyze restaurant reviews to extract sentiment, themes, and recommendations.
    Uses static Louisville restaurant data with Claude API for analysis.
    """
    try:
        # Normalize restaurant name for file lookup
        restaurant_slug = request.restaurant_name.lower().replace(" ", "-").replace("'", "")
        data_path = Path(__file__).parent / "data" / "restaurants" / f"{restaurant_slug}.json"

        # Load restaurant data
        if not data_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Restaurant '{
                    request.restaurant_name}' not found. Available: Jack Fry's, Proof on Main, Hammerheads, Bourbon Raw, Milkwood"
            )

        with open(data_path, "r") as f:
            restaurant_data = json.load(f)

        reviews = restaurant_data["reviews"]

        # Prepare reviews text for Claude analysis
        reviews_text = "\n\n".join([
            f"Rating: {r['rating']}/5\nReview: {r['text']}"
            for r in reviews[:20]  # Analyze first 20 reviews to stay within token limits
        ])

        # Build Claude prompt for analysis
        system_prompt = """You are an expert restaurant consultant analyzing customer reviews.
Your task is to:
1. Identify the overall sentiment (average rating 0-5)
2. Extract 3-5 key themes mentioned frequently (e.g., atmosphere, service, food quality, wait times, pricing)
3. For each theme, count how many times it's mentioned and whether sentiment is positive, negative, or mixed
4. Find one representative positive review excerpt (1-2 sentences)
5. Find one representative negative review excerpt (1-2 sentences)
6. Provide 3-4 actionable recommendations for the restaurant owner

Return your analysis in this exact JSON format:
{
  "overall_sentiment": 4.2,
  "themes": [
    {"theme": "Atmosphere", "mentions": 15, "sentiment": "positive"},
    {"theme": "Service", "mentions": 12, "sentiment": "positive"},
    {"theme": "Wait times", "mentions": 8, "sentiment": "negative"}
  ],
  "sample_positive": "One sentence positive review excerpt",
  "sample_negative": "One sentence negative review excerpt",
  "recommendations": [
    "Specific actionable recommendation 1",
    "Specific actionable recommendation 2",
    "Specific actionable recommendation 3"
  ]
}"""

        user_prompt = f"""Analyze these reviews for {restaurant_data['restaurant']} ({restaurant_data['cuisine']} cuisine) in {restaurant_data['location']}:

{reviews_text}

Provide your analysis in the JSON format specified."""

        # Get analysis from Claude
        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        message = client.messages.create(
            model="claude-haiku-4-20250514",
            max_tokens=2000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )

        # Parse Claude's JSON response
        analysis_text = message.content[0].text

        # Extract JSON from response (handle markdown code blocks if present)
        if "```json" in analysis_text:
            json_start = analysis_text.find("```json") + 7
            json_end = analysis_text.find("```", json_start)
            analysis_text = analysis_text[json_start:json_end].strip()
        elif "```" in analysis_text:
            json_start = analysis_text.find("```") + 3
            json_end = analysis_text.find("```", json_start)
            analysis_text = analysis_text[json_start:json_end].strip()

        analysis = json.loads(analysis_text)

        # Build response
        return RestaurantResponse(
            restaurant=restaurant_data["restaurant"],
            location=restaurant_data["location"],
            overall_sentiment=analysis["overall_sentiment"],
            total_reviews_analyzed=len(reviews),
            themes=[Theme(**theme) for theme in analysis["themes"]],
            sample_positive=analysis["sample_positive"],
            sample_negative=analysis["sample_negative"],
            recommendations=analysis["recommendations"]
        )

    except HTTPException:
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Claude response: {e}")
        raise HTTPException(status_code=500, detail="Failed to parse analysis results")
    except Exception as e:
        logger.error(f"Restaurant analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

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
            "phishing": "/api/phishing - Detect phishing emails",
            "prompt-engineering": "/api/prompt-engineering - Advanced LLM prompt techniques",
            "restaurant-analyzer": "/api/analyze-restaurant - Analyze Louisville restaurant reviews"
        },
        "contact": "/api/contact - Submit contact form",
        "website": "https://projectlavos.com",
        "portfolio": "https://jaspermatters.com",
        "github": "https://github.com/guitargnarr"
    }


@app.get("/health")
def health_check():
    """Health check endpoint with restaurant analyzer and contact form support"""
    return {
        "status": "healthy",
        "demos_available": 5,
        "version": "1.3.0",
        "contact_form": "enabled",
        "restaurant_analyzer": "enabled"
    }

# ============================================================================
# RUN
# ============================================================================


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
