from fastapi import FastAPI, Request, Response, Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from lib.cors import get_cors_origins
from routes.auth import router as auth_router
from routes.protected import router as protected_router
from routes.cards import router as cards_router
from routes.links import router as links_router
from routes.collections import router as collections_router
from routes.profile import router as profile_router


from fastapi.staticfiles import StaticFiles
import os

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

os.makedirs("uploads", exist_ok=True)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.on_event("startup")
async def startup_event():
    import logging
    logger = logging.getLogger("uvicorn")
    if not os.getenv("SECRET_KEY"):
        raise RuntimeError("SECRET_KEY environment variable is not set")
    if not os.getenv("CLOUDFLARE_R2_API"):
        logger.warning("CLOUDFLARE_R2_API environment variable is missing. Avatar uploads will fail.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(protected_router)
app.include_router(cards_router)
app.include_router(links_router)
app.include_router(collections_router)
app.include_router(profile_router)

from sqlalchemy import text
from lib.database import get_db

@app.get("/health")
def check_health(response: Response, db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        response.status_code = 200
        return {"status": "healthy", "database": "connected"}
    except Exception:
        response.status_code = 503
        return {"status": "unhealthy", "database": "unreachable"}
