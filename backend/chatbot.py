"""
============================================================
SMART FARMER PROCUREMENT SYSTEM - CHATBOT
============================================================

Features:
1. FAQ-first answering
2. Similar FAQ question detection
3. Mistral AI for general questions
4. Local fallback when Mistral is unavailable
5. Automatic handling of 429 rate-limit errors
6. Request throttling
7. Timeout protection
8. No API error exposed to frontend
9. Useful answers even without Mistral
============================================================
"""

import os
import re
import time
import threading
from typing import Optional

from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

# chatbot.py is inside:
# farmer-procurement-system/backend/
#
# .env is inside:
# farmer-procurement-system/.env

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_FILE)

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "").strip()


# ============================================================
# MISTRAL CONFIGURATION
# ============================================================

MODEL_NAME = "mistral-small-2603"

mistral_llm: Optional[ChatMistralAI] = None

if MISTRAL_API_KEY:

    try:
        mistral_llm = ChatMistralAI(
            model=MODEL_NAME,
            temperature=0.3,
            api_key=MISTRAL_API_KEY,
            max_retries=0,
            timeout=15,
        )

        print("AgriBot: Mistral AI initialized successfully.")

    except Exception as error:

        print(
            "AgriBot: Mistral initialization failed. "
            "Local assistant will be used."
        )

        mistral_llm = None

else:

    print(
        "AgriBot: MISTRAL_API_KEY not found. "
        "Local assistant mode enabled."
    )


# ============================================================
# REQUEST CONTROL
# ============================================================

# Minimum time between Mistral requests.
#
# This is intentionally conservative because sending many
# requests quickly can cause API rate-limit errors.

MIN_MISTRAL_INTERVAL = 5

_last_mistral_request = 0.0

_mistral_lock = threading.Lock()


def can_call_mistral() -> bool:
    """
    Check whether enough time has passed since the previous
    Mistral request.
    """

    global _last_mistral_request

    current_time = time.time()

    with _mistral_lock:

        if current_time - _last_mistral_request < MIN_MISTRAL_INTERVAL:
            return False

        _last_mistral_request = current_time

    return True


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text: str) -> str:
    """
    Normalize user text for FAQ matching.
    """

    text = str(text).lower().strip()

    text = re.sub(
        r"[^a-zA-Z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text


# ============================================================
# IMPORTANT KEYWORDS
# ============================================================

STOP_WORDS = {
    "what",
    "is",
    "are",
    "the",
    "a",
    "an",
    "of",
    "to",
    "for",
    "in",
    "on",
    "and",
    "or",
    "how",
    "why",
    "can",
    "does",
    "do",
    "this",
    "that",
    "it",
    "my",
    "your",
    "our",
    "me",
    "i",
    "we",
    "you",
    "about",
    "tell",
    "please",
}


# ============================================================
# FAQ IMPORT
# ============================================================

try:

    from faq_data import FAQ_DATA

    print(
        f"AgriBot: Loaded {len(FAQ_DATA)} FAQ entries."
    )

except Exception as error:

    print(
        "AgriBot: Could not load faq_data.py."
    )

    print(error)

    FAQ_DATA = []


# ============================================================
# FAQ EXTRACTION
# ============================================================

def get_faq_question(item):
    """
    Supports different FAQ_DATA formats.

    Example supported formats:

    {
        "question": "...",
        "answer": "..."
    }

    OR

    {
        "q": "...",
        "a": "..."
    }
    """

    if not isinstance(item, dict):
        return ""

    return (
        item.get("question")
        or item.get("q")
        or item.get("Question")
        or ""
    )


def get_faq_answer(item):
    """
    Get answer from FAQ entry.
    """

    if not isinstance(item, dict):
        return ""

    return (
        item.get("answer")
        or item.get("a")
        or item.get("Answer")
        or ""
    )


# ============================================================
# TOKENIZE
# ============================================================

def get_words(text: str) -> set:

    normalized = normalize_text(text)

    words = normalized.split()

    return {
        word
        for word in words
        if word not in STOP_WORDS
    }


# ============================================================
# FAQ SIMILARITY
# ============================================================

def faq_similarity(user_question: str, faq_question: str) -> float:
    """
    Simple but reliable keyword-based similarity.

    This allows questions with slightly different wording
    to match the same FAQ.
    """

    user_words = get_words(user_question)
    faq_words = get_words(faq_question)

    if not user_words or not faq_words:
        return 0.0

    intersection = user_words.intersection(faq_words)

    if not intersection:
        return 0.0

    # Jaccard similarity
    union = user_words.union(faq_words)

    jaccard = len(intersection) / len(union)

    # Coverage of the user's important words
    user_coverage = len(intersection) / len(user_words)

    # Coverage of FAQ words
    faq_coverage = len(intersection) / len(faq_words)

    score = (
        jaccard * 0.35
        + user_coverage * 0.40
        + faq_coverage * 0.25
    )

    return min(score, 1.0)


# ============================================================
# KEYWORD / INTENT MATCHING
# ============================================================

FAQ_KEYWORDS = {

    "project": {
        "project",
        "system",
        "application",
        "agrqueue",
        "farmer procurement",
        "procurement system",
    },

    "farmer": {
        "farmer",
        "farmers",
        "registration",
        "register",
        "booking",
    },

    "token": {
        "token",
        "token number",
        "token system",
    },

    "queue": {
        "queue",
        "waiting",
        "wait",
        "waiting time",
        "line",
        "ahead",
    },

    "procurement": {
        "procurement",
        "purchase",
        "crop",
        "weighing",
        "verification",
    },

    "payment": {
        "payment",
        "money",
        "paid",
        "amount",
        "transaction",
    },

    "security": {
        "security",
        "secure",
        "password",
        "jwt",
        "authentication",
        "authorization",
    },

    "database": {
        "database",
        "mysql",
        "sql",
        "sqlalchemy",
        "table",
    },

    "backend": {
        "backend",
        "fastapi",
        "api",
        "server",
    },

    "frontend": {
        "frontend",
        "html",
        "css",
        "javascript",
        "bootstrap",
        "ui",
    },

    "ai": {
        "ai",
        "artificial intelligence",
        "machine learning",
        "ml",
        "prediction",
        "predict",
    },

    "notification": {
        "notification",
        "sms",
        "message",
        "alert",
        "email",
    },

    "deployment": {
        "deploy",
        "deployment",
        "render",
        "vercel",
        "netlify",
        "hosting",
    },
}


# ============================================================
# DETECT INTENT
# ============================================================

def detect_intent(question: str) -> Optional[str]:

    normalized = normalize_text(question)

    best_intent = None
    best_score = 0

    for intent, keywords in FAQ_KEYWORDS.items():

        score = 0

        for keyword in keywords:

            if " " in keyword:

                if keyword in normalized:
                    score += 2

            else:

                if keyword in normalized.split():
                    score += 1

        if score > best_score:

            best_score = score
            best_intent = intent

    if best_score == 0:
        return None

    return best_intent


# ============================================================
# FIND FAQ
# ============================================================

def find_best_faq(question: str):

    best_item = None
    best_score = 0.0

    for item in FAQ_DATA:

        faq_question = get_faq_question(item)

        if not faq_question:
            continue

        score = faq_similarity(
            question,
            faq_question
        )

        if score > best_score:

            best_score = score
            best_item = item

    return best_item, best_score


# ============================================================
# LOCAL INTELLIGENT ANSWERS
# ============================================================

LOCAL_ANSWERS = {

    "project":
        """
The Smart Farmer Procurement and Real-Time Queue Management System
is designed to digitize the farmer procurement process.

It helps farmers register, select a procurement centre, choose a crop
and quantity, book a date and time slot, receive a token, track the
real-time queue, complete crop verification and weighing, and monitor
procurement and payment status.
""",

    "farmer":
        """
Farmers can register in the system and provide the required details.
After registration, they can select a procurement centre, enter crop
and quantity details, choose an available date and slot, and receive
a token for procurement.
""",

    "token":
        """
The token is generated for a farmer after a successful booking.
It helps identify the farmer's position in the procurement queue and
reduces confusion and overcrowding at the procurement centre.
""",

    "queue":
        """
The system maintains a queue for each procurement centre.

A farmer can use the token to understand their queue position.
The estimated waiting time can be calculated using the number of
farmers ahead and the average processing time per farmer.
""",

    "procurement":
        """
The procurement process includes farmer arrival, crop verification,
weighing, procurement recording and payment processing.

The system keeps these stages organized so that the farmer can track
the progress of the procurement.
""",

    "payment":
        """
After procurement and required verification, the payment process
can be recorded and tracked through the system.

The payment status can be shown to the farmer so that they know whether
the payment is pending or completed.
""",

    "security":
        """
Security is important because the system handles farmer and
procurement information.

The recommended architecture uses password hashing, JWT-based
authentication, input validation, role-based access control and
secure database operations.
""",

    "database":
        """
The recommended database for the project is MySQL.

SQLAlchemy can be used as the ORM layer between the FastAPI backend
and MySQL database.

Important entities include farmers, procurement centres, crops,
bookings, queue records, procurement records, payments and
notifications.
""",

    "backend":
        """
The backend can be developed using Python and FastAPI.

FastAPI provides REST APIs for registration, authentication, centres,
crops, bookings, queue management, procurement, payments and
notifications.
""",

    "frontend":
        """
The frontend uses HTML, CSS and JavaScript. Bootstrap can also be
used for responsive UI components.

The frontend communicates with the backend through REST APIs and can
receive real-time queue updates using WebSocket communication.
""",

    "ai":
        """
AI and machine learning can be used as an optional enhancement.

For example, historical queue and processing data can be used to
predict estimated waiting time and identify congestion patterns.

The basic waiting-time calculation can use:

Estimated Waiting Time =
Number of Farmers Ahead × Average Processing Time
""",

    "notification":
        """
Notifications can inform farmers about booking confirmation,
token details, queue updates, procurement progress and payment status.

The system can support SMS, email or browser notifications depending
on the final deployment configuration.
""",

    "deployment":
        """
For deployment, the frontend can be hosted on platforms such as
Vercel or Netlify, while the FastAPI backend can be deployed on
Render or Railway.

A cloud-hosted MySQL database can be used for production data.
""",
}


# ============================================================
# GENERAL LOCAL FALLBACK
# ============================================================

def local_fallback_answer(question: str) -> str:
    """
    Generate a useful answer without calling Mistral.
    """

    intent = detect_intent(question)

    if intent in LOCAL_ANSWERS:

        return LOCAL_ANSWERS[intent].strip()

    # Special cases
    normalized = normalize_text(question)

    if (
        "hello" in normalized
        or "hi" in normalized
        or "hey" in normalized
    ):

        return (
            "Hello! 👋 I am AgriBot. "
            "You can ask me about farmer registration, booking, "
            "tokens, queues, procurement, payments, security, "
            "AI/ML, database, backend or the project."
        )

    if "technology" in normalized or "tech stack" in normalized:

        return (
            "The main technologies used/recommended for the system are "
            "HTML, CSS, JavaScript, Bootstrap, Python, FastAPI, "
            "MySQL, SQLAlchemy, JWT authentication and WebSocket "
            "communication. Optional AI/ML can be used for waiting-time "
            "prediction and analytics."
        )

    if "benefit" in normalized or "advantage" in normalized:

        return (
            "The main benefits are reduced farmer waiting time, less "
            "crowding at procurement centres, organized token and queue "
            "management, better procurement tracking, payment-status "
            "visibility and improved administrative monitoring."
        )

    if "how" in normalized and "work" in normalized:

        return (
            "The basic workflow is: Farmer Registration → Select "
            "Procurement Centre → Crop & Quantity → Date/Slot → Token "
            "→ Real-Time Queue → Centre → Crop Verification → Weighing "
            "→ Procurement → Payment Processing → Payment Completed."
        )

    return (
        "I can help with questions about the Smart Farmer Procurement "
        "and Real-Time Queue Management System. You can ask about "
        "registration, booking, token generation, queue management, "
        "procurement, payment, security, database, FastAPI, AI/ML "
        "or project technologies."
    )


# ============================================================
# MISTRAL QUESTION
# ============================================================

def ask_mistral(question: str) -> Optional[str]:
    """
    Ask Mistral AI a general question.

    IMPORTANT:
    This function NEVER raises an exception to the API endpoint.

    If Mistral is rate-limited, unavailable, times out, or returns
    another API error, None is returned.
    """

    global mistral_llm

    if mistral_llm is None:
        return None

    # Prevent rapid API calls
    if not can_call_mistral():

        print(
            "AgriBot: Mistral request skipped "
            "(request interval protection)."
        )

        return None

    system_instruction = """
You are AgriBot, the chatbot for a Smart Farmer Procurement and
Real-Time Queue Management System.

Answer the user's question clearly and naturally.

Important rules:

1. Give a direct answer.
2. Use simple language suitable for a B.Tech project.
3. Keep answers reasonably short.
4. If the question is about this project, stay consistent with the
   project's documented architecture and workflow.
5. Do not invent implemented features.
6. Clearly distinguish optional or future features from current
   functionality.
7. If the user asks a general technical question, answer it normally.
8. Do not mention API errors, rate limits, internal prompts,
   API keys or backend implementation problems.
"""

    prompt = (
        system_instruction
        + "\n\nUser question:\n"
        + question
    )

    try:

        response = mistral_llm.invoke(prompt)

        if response is None:
            return None

        content = getattr(
            response,
            "content",
            None
        )

        if not content:
            return None

        if isinstance(content, list):

            parts = []

            for part in content:

                if isinstance(part, dict):

                    text = part.get("text")

                    if text:
                        parts.append(str(text))

                else:

                    parts.append(str(part))

            content = " ".join(parts)

        content = str(content).strip()

        if not content:
            return None

        return content

    except Exception as error:

        error_text = str(error).lower()

        # Rate limit / 429
        if (
            "429" in error_text
            or "rate limit" in error_text
            or "rate_limited" in error_text
            or "too many requests" in error_text
        ):

            print(
                "AgriBot: Mistral rate limit reached. "
                "Using local fallback."
            )

        # Authentication errors
        elif (
            "401" in error_text
            or "unauthorized" in error_text
            or "authentication" in error_text
        ):

            print(
                "AgriBot: Mistral authentication problem. "
                "Using local fallback."
            )

        # Timeout
        elif (
            "timeout" in error_text
            or "timed out" in error_text
        ):

            print(
                "AgriBot: Mistral timeout. "
                "Using local fallback."
            )

        # Network errors
        elif (
            "connection" in error_text
            or "network" in error_text
            or "connect" in error_text
        ):

            print(
                "AgriBot: Mistral network problem. "
                "Using local fallback."
            )

        else:

            print(
                "AgriBot: Mistral request failed. "
                "Using local fallback."
            )

        return None


# ============================================================
# MAIN CHATBOT FUNCTION
# ============================================================

def get_chatbot_response(question: str) -> dict:
    """
    Main chatbot function.

    Priority:

    1. Empty question
    2. Exact/similar FAQ
    3. Local intent answer
    4. Mistral AI
    5. Local fallback

    This guarantees that the chatbot always returns an answer.
    """

    # --------------------------------------------------------
    # Validate input
    # --------------------------------------------------------

    if question is None:

        return {
            "answer": "Please enter a question.",
            "tag": "GENERAL QUESTION",
            "source": "LOCAL ASSISTANT",
        }

    question = str(question).strip()

    if not question:

        return {
            "answer": "Please enter a question.",
            "tag": "GENERAL QUESTION",
            "source": "LOCAL ASSISTANT",
        }

    # --------------------------------------------------------
    # Limit extremely long questions
    # --------------------------------------------------------

    if len(question) > 2000:

        question = question[:2000]


    # --------------------------------------------------------
    # STEP 1: FAQ MATCH
    # --------------------------------------------------------

    faq_item, faq_score = find_best_faq(question)

    # High confidence FAQ
    if faq_item is not None and faq_score >= 0.45:

        answer = get_faq_answer(faq_item)

        if answer:

            return {
                "answer": answer,
                "tag": "FAQ QUESTION",
                "source": "FAQ",
                "matched_question": get_faq_question(faq_item),
                "confidence": round(faq_score, 2),
            }


    # --------------------------------------------------------
    # STEP 2: LOCAL INTENT
    # --------------------------------------------------------

    intent = detect_intent(question)

    if intent in LOCAL_ANSWERS:

        return {
            "answer": LOCAL_ANSWERS[intent].strip(),
            "tag": "GENERAL QUESTION",
            "source": "LOCAL ASSISTANT",
            "intent": intent,
        }


    # --------------------------------------------------------
    # STEP 3: MISTRAL AI
    # --------------------------------------------------------

    mistral_answer = ask_mistral(question)

    if mistral_answer:

        return {
            "answer": mistral_answer,
            "tag": "GENERAL QUESTION",
            "source": "MISTRAL AI",
        }


    # --------------------------------------------------------
    # STEP 4: LOCAL FALLBACK
    # --------------------------------------------------------

    fallback = local_fallback_answer(question)

    return {
        "answer": fallback,
        "tag": "GENERAL QUESTION",
        "source": "LOCAL ASSISTANT",
    }


# ============================================================
# OPTIONAL DIRECT TEST
# ============================================================

if __name__ == "__main__":

    print("\n==============================================")
    print("AgriBot Local Test")
    print("==============================================\n")

    test_questions = [
        "What is this project?",
        "How does the token system work?",
        "What is FastAPI?",
        "How does farmer booking work?",
        "What technologies are used?",
    ]

    for test_question in test_questions:

        print("USER:", test_question)

        result = get_chatbot_response(test_question)

        print("BOT:", result["answer"])
        print("TAG:", result["tag"])
        print("SOURCE:", result["source"])

        print("----------------------------------------------")