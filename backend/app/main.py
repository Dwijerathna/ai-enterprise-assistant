from fastapi import FastAPI

app = FastAPI(
    title="Enterprise AI Assistant",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "status": "healthy",
        "message": "Enterprise AI Assistant API running"
    }