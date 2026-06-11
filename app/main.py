from fastapi import FastAPI
from app.api.endpoints import router as api_router

app = FastAPI(title="Academic Intelligence API", version="1.0.0")

app.include_router(api_router, prefix="/api/v1")

@app.get("/api/v1/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
