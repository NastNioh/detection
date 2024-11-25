from fastapi import FastAPI
from api.route import router as api_router

# Initialiser l'application FastAPI
app = FastAPI(
    title="API de Détection d'Images Truquées",
    description="Une API pour détecter et expliquer les images truquées.",
    version="1.0",
)

# Inclure les routes
app.include_router(api_router, prefix="/api", tags=["Images"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True)
