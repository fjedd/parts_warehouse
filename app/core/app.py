from core.routes.category_routes import router as CategoryRouter
from core.routes.part_routes import router as PartsRouter
from core.routes.search_routes import router as SearchRouter
from fastapi import FastAPI

app = FastAPI()


app.include_router(PartsRouter, tags=["Parts"], prefix="/parts")
app.include_router(CategoryRouter, tags=["Categories"], prefix="/categories")
app.include_router(SearchRouter, tags=["Search"], prefix="/search")
