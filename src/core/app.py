from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from .auth.jwt_handler import AuthHandler
from .database import init_db
from .routes.auth_routes import router as AuthRouter
from .routes.category_routes import router as CategoryRouter
from .routes.part_routes import router as PartsRouter
from .routes.search_routes import router as SearchRouter


@asynccontextmanager
async def lifespan(fastapi: FastAPI):
    print("Initializing database...")
    await init_db()
    yield
    print("Closing connection...")
    # add


auth_handler: AuthHandler = AuthHandler()
app: FastAPI = FastAPI(lifespan=lifespan)


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Parts warehouse"}


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
