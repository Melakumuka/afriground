from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from auth import get_current_user

app = FastAPI(
    title=settings.app_name,
    description="AfriGround GSaaS Platform API",
    version="0.2.0",
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.api_cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def tenant_context_middleware(request, call_next):
    """Stamp request state with the verified JWT subject (tenant resolution happens in deps)."""
    from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

    request.state.tenant_user_id = None
    request.state.tenant_org_id = None
    auth_header = request.headers.get("Authorization", "")
    if auth_header.lower().startswith("bearer "):
        token = auth_header[7:].strip()
        try:
            import jwt as pyjwt

            payload = pyjwt.decode(
                token,
                settings.supabase_jwt_secret,
                algorithms=["HS256"],
                audience="authenticated",
            )
            request.state.tenant_user_id = payload.get("sub")
            request.state.tenant_org_id = payload.get("org_id")
        except Exception:
            pass
    response = await call_next(request)
    return response

@app.get("/health")
async def health_check():
    return {"status": "ok", "app": settings.app_name, "env": settings.app_env}

@app.get("/api/v1/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return {"user_id": current_user.get("sub"), "email": current_user.get("email")}

from routes import commercial, operations, telemetry, data, support, routing, tenancy, missions, stations, contact, regulatory, orchestration, edge

app.include_router(commercial.router)
app.include_router(operations.router)
app.include_router(telemetry.router)
app.include_router(data.router)
app.include_router(support.router)
app.include_router(routing.router)
app.include_router(tenancy.router)
app.include_router(missions.router)
app.include_router(stations.router)
app.include_router(contact.router)
app.include_router(regulatory.router)
app.include_router(orchestration.router)
app.include_router(edge.router)
