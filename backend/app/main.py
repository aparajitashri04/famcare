from app.routes import slots
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app.models import Base
from app.routes import checkout

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="FamCare Booking Engine",
    description="Multi-service bulk scheduler with atomic checkout",
    version="1.0.0",
)

# Add CORS middleware for Flutter client
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(slots.router)
app.include_router(checkout.router)


@app.get("/")
def root():
    return {
        "message": "FamCare Booking Engine API",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}
