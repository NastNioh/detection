from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.route import router as api_router
from database.db import engine, Base

app = FastAPI(
    title="API de Détection d'Images Truquées",
    description="Une API pour détecter et expliquer les images truquées.",
    version="1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 👈 Autoriser toutes les origines pour le test (change en ["http://localhost"] en prod)
    allow_credentials=True,
    allow_methods=["*"],  # 👈 Autoriser toutes les méthodes HTTP (GET, POST, OPTIONS...)
    allow_headers=["*"],  # 👈 Autoriser tous les headers
)

Base.metadata.create_all(bind=engine)

# Inclure les routes
app.include_router(api_router, prefix="/api", tags=["Images"])

@app.options("/{full_path:path}")
async def preflight(full_path: str):
    return {"message": "Preflight request handled"}

@app.get("/")
def read_root():
    return {"message": "Face Recognition API is running!"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
