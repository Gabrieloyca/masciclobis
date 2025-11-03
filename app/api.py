from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import analysis, map as map_mod

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "web"

app = FastAPI(title="Accessibilité urbaine", version="2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter()


class AnalysisRequest(BaseModel):
    city: str = Field(..., description="Nom de la ville ou coordonnées supportées par OSM")
    mode: str = Field("walk", description="Profil OSM à utiliser (walk, bike, drive…)")
    radius_km: float = Field(1.0, gt=0, description="Rayon en kilomètres")
    do_centrality: bool = True
    do_closeness: bool = False
    do_degree: bool = False
    do_straightness: bool = False
    do_eigenvector: bool = False
    do_h3: bool = True
    h3_res: int = Field(7, ge=1, le=15)
    color_by: str = "length"
    allow_synthetic: bool = Field(
        False,
        description=(
            "Autoriser une grille synthétique de secours si Overpass est indisponible."
        ),
    )


def _to_native(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _to_native(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_to_native(v) for v in obj]
    try:
        import numpy as np
        if isinstance(obj, (np.generic,)):
            return obj.item()
    except ModuleNotFoundError:
        pass
    if hasattr(obj, "isoformat"):
        try:
            return obj.isoformat()
        except Exception:  # pragma: no cover - fallback for unexpected types
            return str(obj)
    return obj


@router.get("/health")
async def healthcheck():
    return {"status": "ok"}


@router.post("/analyze")
async def analyze(req: AnalysisRequest):
    result = analysis.run(
        city=req.city,
        mode=req.mode,
        radius_km=req.radius_km,
        do_centrality=req.do_centrality,
        do_closeness=req.do_closeness,
        do_degree=req.do_degree,
        do_straightness=req.do_straightness,
        do_eigenvector=req.do_eigenvector,
        do_h3=req.do_h3,
        h3_res=req.h3_res,
        color_by=req.color_by,
        allow_synthetic=req.allow_synthetic,
    )

    if result.get("error"):
        raise HTTPException(status_code=400, detail=result)

    map_payload = map_mod.build_map_payload(result, color_by=req.color_by)
    h3_payload = map_mod.h3_payload(result)

    metrics_df = result.get("metrics_df")
    metrics_table = []
    if metrics_df is not None and not metrics_df.empty:
        metrics_table = metrics_df.to_dict(orient="records")

    response: Dict[str, Any] = {
        "metrics": _to_native(result.get("metrics", {})),
        "map": map_payload,
        "metricsTable": metrics_table,
        "downloads": {
            "edgesGeoJSON": result.get("edges_geojson"),
            "metricsCSV": result.get("metrics_csv"),
            "h3GeoJSON": result.get("h3_geojson"),
        },
        "colorBy": map_payload.get("colorBy"),
    }

    if h3_payload:
        response["h3"] = h3_payload

    return response


app.include_router(router, prefix="/api")

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def serve_index() -> FileResponse:
    if STATIC_DIR.exists():
        return FileResponse(STATIC_DIR / "index.html")
    raise HTTPException(status_code=404, detail="Interface web non disponible")


def create_app() -> FastAPI:
    """Expose a factory for ASGI servers."""
    return app
