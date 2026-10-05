from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.video import router as video_router
from app.api.routes.zone import router as zone_router

from app.api.routes.incidents import router as incident_router


app = FastAPI(
    title="Vision-AI Monitoring System",
    description="AI-Based Industrial Safety and Surveillance System",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


app.include_router(video_router)
app.include_router(zone_router)
app.include_router(incident_router)


@app.get("/")
def root():
    return {
        "message": "Vision-AI Monitoring System API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }