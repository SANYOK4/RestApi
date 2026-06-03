from contextlib import asynccontextmanager
from fastapi import FastAPI
from models.database import engine, Base
from api.router import router as books_router
from api.auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Library API - Load Testing", lifespan=lifespan)
app.include_router(auth_router)
app.include_router(books_router)