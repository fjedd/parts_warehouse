from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database import init_db
from .routes.category_routes import router as CategoryRouter
from .routes.part_routes import router as PartsRouter
from .routes.search_routes import router as SearchRouter


@asynccontextmanager
async def lifespan(fastapi: FastAPI):
    print("Initializing database...")
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Parts warehouse"}


app.include_router(PartsRouter, tags=["Part"], prefix="/parts")
app.include_router(CategoryRouter, tags=["Category"], prefix="/categories")
app.include_router(SearchRouter, tags=["Search"], prefix="/search")
