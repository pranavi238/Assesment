from fastapi import FastAPI

from app.api.routes import router as api_router


def create_app() -> FastAPI:
    app = FastAPI(title="REST Thumbnail Creation Service")
    app.include_router(api_router)
    return app


app = create_app()

