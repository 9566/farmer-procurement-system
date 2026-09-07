"""
Smart Farmer Procurement System
Main FastAPI application
"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import models

from database import (
    Base,
    engine,
)

from routers import (
    admin,
    booking,
    farmer,
    payment,
    procurement,
    queue,
)

from chatbot import get_chatbot_response


# ============================================================
# DATABASE TABLES
# ============================================================

Base.metadata.create_all(
    bind=engine
)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(

    title="Smart Farmer Procurement System",

    description=(
        "Backend API for Farmer Booking, "
        "Queue, Procurement and Payment Management"
    ),

    version="2.0.0",
)


# ============================================================
# CORS
# ============================================================

allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    ""
).strip()


if allowed_origins:

    origins = [
        origin.strip()
        for origin in allowed_origins.split(",")
        if origin.strip()
    ]

    allow_credentials = True

else:

    origins = ["*"]

    allow_credentials = False


app.add_middleware(

    CORSMiddleware,

    allow_origins=origins,

    allow_credentials=allow_credentials,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ============================================================
# EXISTING PROJECT ROUTERS
# ============================================================

app.include_router(
    admin.auth_router
)

app.include_router(
    admin.router
)

app.include_router(
    farmer.router
)

app.include_router(
    booking.router
)

app.include_router(
    queue.router
)

app.include_router(
    procurement.router
)

app.include_router(
    payment.router
)


# ============================================================
# ROOT API
# ============================================================

@app.get("/")
def root():

    return {

        "message":
            "Smart Farmer Procurement System API is running",

        "status":
            "success",

        "version":
            "2.0.0",
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {

        "status":
            "healthy",

        "database":
            "connected",
    }


# ============================================================
# CHATBOT
# ============================================================

class ChatRequest(BaseModel):

    question: str


# ============================================================
# CHATBOT API
# ============================================================

@app.post("/chatbot")
def chatbot(
    request: ChatRequest
):

    result = get_chatbot_response(
        request.question
    )

    return result