from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from routers import auth, profile, friends, messages, stats, leaderboard
from routers import auth, profile, friends, messages, stats, leaderboard, match



app = FastAPI(title="FootUP Connect API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(profile.router, prefix="/api")
app.include_router(friends.router, prefix="/api")
app.include_router(messages.router, prefix="/api")  # ✅ Déjà là normalement
app.include_router(stats.router, prefix="/api")
app.include_router(leaderboard.router, prefix="/api")
app.include_router(match.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)