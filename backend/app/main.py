from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .model_service import FEATURES, predict
from .schemas import PredictionResponse, ProjectInput

BASE_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(
    title="Land Acquisition Delay Prediction API",
    version="1.0.0",
    description="Random Forest based delay-risk prediction with SHAP explanations.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "model": "loaded", "features": FEATURES}


@app.post("/api/predict", response_model=PredictionResponse)
def prediction(project: ProjectInput):
    return predict(project.model_dump())


@app.get("/", include_in_schema=False)
def frontend():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/{path:path}", include_in_schema=False)
def static_files(path: str):
    requested = FRONTEND_DIR / path
    if requested.is_file():
        return FileResponse(requested)
    return FileResponse(FRONTEND_DIR / "index.html")
