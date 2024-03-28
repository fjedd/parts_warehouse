from contextlib import asynccontextmanager
from typing import List

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth.jwt_handler import AuthHandler
from .database import Database
from .routes.auth_routes import router as AuthRouter
from .routes.category_routes import router as CategoryRouter
from .routes.part_routes import router as PartsRouter
from .routes.search_routes import router as SearchRouter

db: Database = Database()
auth_handler: AuthHandler = AuthHandler()


@asynccontextmanager
async def lifespan(fastapi: FastAPI):
    print("Initializing database...")
    await db.init_db()
    yield
    print("Closing connection...")
    db.close_db()


app: FastAPI = FastAPI(title="Parts warehouse API", lifespan=lifespan)


origins: List[str] = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,  # type: ignore
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET, POST, PUT, DELETE"],
    allow_headers=["*"],
)

app.include_router(
    PartsRouter,
    tags=["Part"],
    prefix="/parts",
    dependencies=[Depends(auth_handler.verify_token)],
)
app.include_router(
    CategoryRouter,
    tags=["Category"],
    prefix="/categories",
    dependencies=[Depends(auth_handler.verify_token)],
)
app.include_router(
    SearchRouter,
    tags=["Search"],
    prefix="/search",
    dependencies=[Depends(auth_handler.verify_token)],
)
app.include_router(AuthRouter, tags=["Auth"], prefix="/auth")


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Parts warehouse API"}
