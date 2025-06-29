from fastapi import FastAPI
from core.routes import characters, films, integrations, starships

app = FastAPI(
    title="SWAPI",
    description="A Start Wars REST API app",
    version="1.0.0",
)

app.include_router(characters.router, prefix="/api", tags=["Characters"])
app.include_router(films.router, prefix="/api", tags=["Films"])
app.include_router(starships.router, prefix="/api", tags=["Starships"])
app.include_router(integrations.router, prefix="/api", tags=["Integration"])
