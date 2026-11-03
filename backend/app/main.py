import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.db.session import engine, Base, SessionLocal
from app.services.seed_service import seed_database

# Import routers
from app.api.routes import (
    demo, documents, generation, questions,
    papers, attempts, grading, analytics, notifications
)

app = FastAPI(
    title="ExamForge API",
    version="1.0.0",
    description="AI-powered question-paper generation and college assessment platform",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for local development & preview
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup: initialize tables and seed data if clean
@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db, force=False)
    finally:
        db.close()

# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "detail": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": f"Internal server error: {str(exc)}",
            "status_code": 500
        }
    )

# Health checks
@app.get("/health")
@app.get(f"{settings.API_V1_STR}/health")
def health_check():
    return {
        "status": "ok",
        "app": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "gemini_configured": bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your_gemini_api_key_here")
    }

# Register API v1 Routers
api_v1 = settings.API_V1_STR
app.include_router(demo.router, prefix=api_v1)
app.include_router(demo.dash_router, prefix=api_v1)
app.include_router(documents.router, prefix=api_v1)
app.include_router(generation.router, prefix=api_v1)
app.include_router(questions.router, prefix=api_v1)
app.include_router(papers.router, prefix=api_v1)
app.include_router(attempts.router, prefix=api_v1)
app.include_router(grading.router, prefix=api_v1)
app.include_router(analytics.router, prefix=api_v1)
app.include_router(notifications.router, prefix=api_v1)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
