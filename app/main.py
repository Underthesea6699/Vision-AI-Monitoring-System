from fastapi import FastAPI


app = FastAPI(
    title="Vision-AI Monitoring System",
    description="AI-Based Industrial Safety and Surveillance System",
    version="1.0.0"
)


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