# backend/app/api/chat_routes.py

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
import random
import uuid

router = APIRouter(tags=["AI Advisor"])

# ==========================
# Pydantic Models
# ==========================

class Message(BaseModel):
    role: str
    content: str
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    history: Optional[List[Message]] = Field(default_factory=list)
    language: Optional[str] = "english"
    farmer_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    suggestions: List[str] = []
    session_id: str
    confidence: float
    category: str
    timestamp: datetime
    follow_up_questions: List[str] = []
    action_items: List[str] = []


# ==========================
# Knowledge Base
# ==========================

KNOWLEDGE_BASE = {

    "crops": {
        "keywords": ["crop","plant","grow","seed","sow","harvest"],
        "responses": [
            {
                "pattern": ["wheat","gehu"],
                "response": "🌾 Wheat is a Rabi crop sown Oct–Dec and harvested Mar–Apr. Recommended varieties: HD-2967, PBW-343.",
                "follow_up": [
                    "When to irrigate wheat?",
                    "Fertilizer for wheat?",
                    "Wheat disease control?"
                ]
            },
            {
                "pattern": ["rice","paddy"],
                "response": "🌾 Rice is a Kharif crop grown during monsoon. Maintain 5cm standing water for best growth.",
                "follow_up": [
                    "Rice nursery preparation?",
                    "Paddy transplanting time?",
                    "Rice fertilizer schedule?"
                ]
            },
            {
                "pattern": ["tomato"],
                "response": "🍅 Tomato grows best in well-drained soil. Use staking and mulch for better yield.",
                "follow_up": [
                    "Tomato diseases?",
                    "Tomato pruning?",
                    "Best tomato varieties?"
                ]
            }
        ],
        "default": "Tell me your soil type, season, and region. I will recommend the best crops."
    },

    "fertilizer": {
        "keywords": ["fertilizer","urea","dap","npk","manure"],
        "responses": [
            {
                "pattern": ["urea"],
                "response": "🧪 Urea contains 46% Nitrogen. Apply in split doses during crop growth.",
                "follow_up": [
                    "Urea for paddy?",
                    "When to apply urea?",
                    "Urea alternatives?"
                ]
            },
            {
                "pattern": ["dap"],
                "response": "🧪 DAP fertilizer (18:46:0) supplies phosphorus and nitrogen. Usually applied at sowing.",
                "follow_up": [
                    "DAP vs SSP?",
                    "DAP for vegetables?",
                    "DAP application method?"
                ]
            }
        ],
        "default": "Tell me your crop and growth stage. I will suggest fertilizer schedule."
    },

    "pest": {
        "keywords": ["pest","disease","fungus","insect"],
        "responses": [
            {
                "pattern": ["aphid"],
                "response": "🐛 Aphids can be controlled using neem oil spray or imidacloprid.",
                "follow_up": [
                    "Aphids on wheat?",
                    "Organic aphid control?",
                    "Aphids on mustard?"
                ]
            },
            {
                "pattern": ["blight"],
                "response": "🍂 Blight disease can be controlled using Mancozeb fungicide.",
                "follow_up": [
                    "Early blight treatment?",
                    "Blight resistant varieties?",
                    "Blight in potato?"
                ]
            }
        ],
        "default": "Please describe the symptoms and crop affected. Photos help in accurate diagnosis."
    },

    "market": {
        "keywords": ["price","rate","market","sell"],
        "responses": [
            {
                "pattern": ["price","rate"],
                "response": "💰 Wheat approx ₹2100-2300/qtl, Rice ₹2200-2800/qtl, Tomato ₹1200-1800/qtl.",
                "follow_up": [
                    "Best time to sell?",
                    "Mandi near me?",
                    "Price trends?"
                ]
            }
        ],
        "default": "Tell me crop name and location. I will provide market guidance."
    }
}


# ==========================
# Helper Functions
# ==========================

def detect_intent(message: str):

    message_lower = message.lower()
    best_category = "general"
    best_confidence = 0.0
    matched_data = {}

    for category,data in KNOWLEDGE_BASE.items():

        for keyword in data["keywords"]:

            if keyword in message_lower:

                confidence = 0.6

                for response in data["responses"]:
                    for pattern in response["pattern"]:
                        if pattern in message_lower:
                            confidence += 0.2
                            matched_data = response

                if confidence > best_confidence:
                    best_confidence = confidence
                    best_category = category

    return best_category, min(best_confidence,0.95), matched_data


def generate_response(category,confidence,matched_data):

    if confidence > 0.7 and matched_data:
        response_text = matched_data["response"]
        follow_up = matched_data.get("follow_up",[])
    else:
        response_text = KNOWLEDGE_BASE[category]["default"]
        follow_up = []

    return response_text, follow_up


# ==========================
# API Endpoints
# ==========================

@router.get("/")
async def chat_info():
    return {
        "message": "KrishiMitra AI Advisor",
        "capabilities": list(KNOWLEDGE_BASE.keys())
    }


@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):

    category,confidence,matched_data = detect_intent(request.message)

    response_text,follow_up = generate_response(
        category,
        confidence,
        matched_data
    )

    return ChatResponse(
        response=response_text,
        suggestions=[
            "Crop advice",
            "Fertilizer help",
            "Pest control",
            "Market price"
        ],
        session_id=request.session_id,
        confidence=confidence,
        category=category,
        timestamp=datetime.now(),
        follow_up_questions=follow_up,
        action_items=[]
    )


@router.post("/feedback")
async def submit_feedback(
    session_id: str,
    rating: int = Query(..., ge=1, le=5),
    feedback_text: Optional[str] = None
):

    return {
        "status": "success",
        "message": "Thank you for your feedback!",
        "session_id": session_id,
        "rating": rating,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/session/{session_id}")
async def get_session_history(session_id: str):

    return {
        "session_id": session_id,
        "message_count": random.randint(3,15),
        "duration_minutes": random.randint(2,30),
        "topics_discussed": random.sample(
            list(KNOWLEDGE_BASE.keys()),
            k=min(3,len(KNOWLEDGE_BASE))
        )
    }