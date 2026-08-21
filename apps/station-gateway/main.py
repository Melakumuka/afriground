from contextlib import asynccontextmanager
from fastapi import FastAPI

from local_db import init_db
from routes.operator import router as operator_router
from worker import BackgroundWorker

worker = BackgroundWorker()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await worker.start()
    yield
    await worker.stop()

app = FastAPI(title="AfriGround Station Gateway", lifespan=lifespan)
app.include_router(operator_router)
