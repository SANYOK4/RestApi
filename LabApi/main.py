from fastapi import FastAPI
from api.router import router
from models.database import engine, Base
app = FastAPI()

# Автоматичне створення таблиць при запуску
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(router)