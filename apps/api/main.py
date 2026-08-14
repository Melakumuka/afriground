from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from auth import get_current_user

app = FastAPI(
    title=settings.app_name,
    description="AfriGround GSaaS Platform API",
    version="0.1.0",
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.api_cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok", "app": settings.app_name, "env": settings.app_env}

@app.get("/api/v1/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return {"user_id": current_user.get("sub"), "email": current_user.get("email")}

from routes import commercial, operations, telemetry, data, support, routing

app.include_router(commercial.router)
app.include_router(operations.router)
app.include_router(telemetry.router)
app.include_router(data.router)
app.include_router(support.router)
app.include_router(routing.router)
