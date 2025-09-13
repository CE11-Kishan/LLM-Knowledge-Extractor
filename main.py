import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routes import router
from app.database import init_db
from dotenv import load_dotenv

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()
    init_db()
    yield

app = FastAPI(title="LLM Knowledge Extractor", version="0.1.0", lifespan=lifespan)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    
    # For cloud deployment, bind to 0.0.0.0 to accept connections from all interfaces
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    uvicorn.run("main:app", host=host, port=port)
