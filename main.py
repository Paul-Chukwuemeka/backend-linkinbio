from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from routes.auth import router as auth_router
from routes.protected import router as protected_router
from routes.cards import router as cards_router
from routes.links import router as links_router
from routes.collections import router as collections_router
from routes.profile import router as profile_router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(protected_router)
app.include_router(cards_router)
app.include_router(links_router)
app.include_router(collections_router)
app.include_router(profile_router)

@app.get("/health")
def check_health(response: Response):
    response.status_code = 200
    return {"message": "Healthy and running"}
