from fastapi import FastAPI
from core.routes import item

app = FastAPI(
    title="API",
    description="A REST API app",
    version="1.0.0",
)

app.include_router(item.router, prefix="/api", tags=["Items"])
