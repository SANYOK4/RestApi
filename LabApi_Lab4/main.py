from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.router import router
from models.database import connect_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()


app = FastAPI(lifespan=lifespan)
app.include_router(router)