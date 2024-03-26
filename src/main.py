import uvicorn

from core.config import settings

if __name__ == "__main__":
    uvicorn.run("core.app:app", host="0.0.0.0", port=settings.APP_PORT, reload=True)
