from fastapi import FastAPI
from api.router import router

app = FastAPI(title="Library API")
app.include_router(router)