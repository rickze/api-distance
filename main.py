# Comentar código : CRT + K + C
# Descomentar código : CRT + K + U
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Tuple, Dict
import requests
import re
import os
import logging
from contextlib import asynccontextmanager
# IMPORTAR FUNÇÕES DA CACHE SQLITE
from inspect_cache import init_db, get_from_cache, save_to_cache
# ==========================================================
# Configuração
# ==========================================================
# Logging básico
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)
# Se quiseres, podes manter a leitura da env var e pôr um fallback
API_KEY_TOMTOM = os.getenv("TOMTOM_API_KEY")
if not API_KEY_TOMTOM:
    raise RuntimeError("TomTom API key not configured")
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})
# Caches em memória
coord_cache: Dict[str, Tuple[Optional[float], Optional[float]]] = {}
route_cache: Dict[str, Tuple[Optional[float], Optional[float]]] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: garantir que a base de dados e tabela existem
    init_db()
    yield
app = FastAPI(
    title="API Distâncias CEP",
    description="Calcula distâncias e tempos entre dois CEP usando codigo-postal.pt + TomTom.",
    version="1.1.0",
    lifespan=lifespan,
)
# ==========================================================
# Healthcheck
# ==========================================================


@app.get("/ping")
def ping():
    return {"status": "ok"}
# ==========================================================
# MODELOS
# ==========================================================


class CEPRequest(BaseModel):
    cep_origem: str
    cep_destino: str
    vehicle_type: str   # Ex: ligeiro, pesado, van, truck, car, ...
# ==========================================================
# FUNÇÕES UTILITÁRIAS
# ==========================================================


def safe_val_dbl(s: str) -> Optional[float]:
    if s is None:
        return None
    s = str(s).replace("\xa0", " ").strip().replace(",", ".")
    match = re.findall(r"[-+]?\d*\.\d+|\d+", s)
    if not match:
        return None
    try:
        return float(match[0])
    except (ValueError, IndexError):
        return None


def normalize_cep(cep: str) -> str:
    """Normaliza CEP para 'XXXX-XXX' se tiver 7 dígitos."""
    if cep is None:
        return ""
    s = str(cep)
    digits = re.findall(r"\d+", s)
    if not digits:
        return s.strip()
    all_digits = "".join(digits)
    if len(all_digits) == 7:
        return f"{all_digits[:4]}-{all_digits[4:]}"
    return all_digits


def validate_cep_format(cep: str) -> bool:
    """Valida formatos: '1234-567' ou '1234567'."""
    if not isinstance(cep, str):
        return False
    cep = cep.strip()
    return bool(re.match(r"^\d{4}-\d{3}$", cep) or re.match(r"^\d{7}$", cep))


def fetch_coordinates_from_site(cep: str) -> Tuple[Optional[float], Optional[float]]:
    """Busca coordenadas no codigo-postal.pt (igual à lógica do teu colega, com média)."""
    try:
        url = f"https://www.codigo-postal.pt/?rua={cep}"
        r = session.get(url, timeout=8)
        if r.status_code != 200:
            return None, None
        html = r.text
        pattern = re.compile(
            r"pull-right\s+gps[\s\S]*?([+-]?\d+\.\d+)[\s,]+([+-]?\d+\.\d+)"
        )
        matches = pattern.findall(html)
        if not matches:
            return None, None
        latitudes = [safe_val_dbl(lat) for lat, _ in matches if safe_val_dbl(lat) is not None]
        longitudes = [safe_val_dbl(lon) for _, lon in matches if safe_val_dbl(lon) is not None]
        if not latitudes or not longitudes:
            return None, None
        avg_lat = sum(latitudes) / len(latitudes)
        avg_lon = sum(longitudes) / len(longitudes)
        return avg_lat, avg_lon
    except Exception as e:
        logger.exception("Erro ao buscar CEP %s: %s", cep, e)
        return None, None


def get_coordinates_for_cep(cep: str) -> Tuple[Optional[float], Optional[float]]:
    """Usa cache em memória + scraping para devolver coordenadas médias por CEP."""
    cep_norm = normalize_cep(cep)
    if cep_norm in coord_cache:
        logger.info("[COORD CACHE HIT] %s -> %s", cep_norm, coord_cache[cep_norm])
        return coord_cache[cep_norm]
    logger.info("[COORD CACHE MISS] %s -> a obter coordenadas...", cep_norm)
    lat, lon = fetch_coordinates_from_site(cep_norm)
    coord_cache[cep_norm] = (lat, lon)
    logger.info("[COORD CACHE STORE] %s -> %s, %s", cep_norm, lat, lon)
    return lat, lon


def map_vehicle_to_travel_mode(vehicle_type: str) -> str:
    """Mapeia o tipo de viatura interno para o travelMode do TomTom."""
    if not vehicle_type:
        raise HTTPException(status_code=400, detail="Tipo de viatura em branco.")
    vt = vehicle_type.strip().lower()
    mapping = {
        "ligeiro": "car",
        "carro": "car",
        "car": "car",
        "c": "car",
        "pesado": "truck",
        "camião": "truck",
        "camiao": "truck",
        "truck": "truck",
        "t": "truck",
        "van": "van",
        "furgão": "van",
        "furgao": "van",
        "v": "van",
    }
    if vt not in mapping:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de viatura inválido: '{vehicle_type}'. Use por ex.: ligeiro, pesado, van."
        )
    return mapping[vt]


def calculate_route_tomtom(
    lat_orig: float,
    lon_orig: float,
    lat_dest: float,
    lon_dest: float,
    travel_mode: str
) -> Tuple[Optional[float], Optional[float]]:
    """Chama TomTom e devolve distância (km) e tempo (min), com cache em memória."""
    key = f"{lat_orig},{lon_orig}:{lat_dest},{lon_dest}:{travel_mode}"
    if key in route_cache:
        logger.info("[ROUTE CACHE HIT] %s -> %s", key, route_cache[key])
        return route_cache[key]
    logger.info("[ROUTE CACHE MISS] %s -> a chamar TomTom...", key)
    api_url = (
        f"https://api.tomtom.com/routing/1/calculateRoute/"
        f"{lat_orig},{lon_orig}:{lat_dest},{lon_dest}/json"
        f"?key={API_KEY_TOMTOM}&travelMode={travel_mode}"
    )
    try:
        r = session.get(api_url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if "routes" in data and data["routes"]:
                summary = data["routes"][0]["summary"]
                distance_km = round(summary.get("lengthInMeters", 0) / 1000, 2)
                time_minutes = round(summary.get("travelTimeInSeconds", 0) / 60, 2)
                route_cache[key] = (distance_km, time_minutes)
                logger.info("[ROUTE CACHE STORE] %s -> %s km, %s min", key, distance_km, time_minutes)
                return distance_km, time_minutes
    except Exception as e:
        logger.exception("Erro ao chamar TomTom: %s", e)
    route_cache[key] = (None, None)
    logger.warning("[ROUTE CACHE STORE FAIL] %s -> (None, None)", key)
    return None, None
# ==========================================================
# ENDPOINT PRINCIPAL PARA SAP
# ==========================================================


@app.post("/gps/distance")
async def calcular_distancia_post(req: CEPRequest):
    """
    Entrada:
      - cep_origem
      - cep_destino
      - vehicle_type (ligeiro, pesado, van, truck, ...)
    Saída:
      - distance + distance_unit
      - travel_time + time_unit
      - ecos dos CEPs e tipo de viatura
      - campo 'source' a indicar se veio da cache ou da TomTom
    """
    cep_o = normalize_cep(req.cep_origem)
    cep_d = normalize_cep(req.cep_destino)
    if not validate_cep_format(cep_o) or not validate_cep_format(cep_d):
        raise HTTPException(
            status_code=400,
            detail=f"CEPs inválidos: origem='{req.cep_origem}', destino='{req.cep_destino}'"
        )
    # Mapear tipo viatura para travelMode TomTom (e usar isto como chave na cache)
    travel_mode = map_vehicle_to_travel_mode(req.vehicle_type)
    # 1) CASO TRIVIAL: CEP origem = CEP destino
    if cep_o == cep_d:
        return {
            "origin_cep": cep_o,
            "destination_cep": cep_d,
            "vehicle_type": req.vehicle_type,
            "tomtom_travel_mode": travel_mode,
            "distance": 0.0,
            "distance_unit": "km",
            "travel_time": 0.0,
            "time_unit": "min",
            "source": "trivial"
        }
    # 2) TENTAR CACHE PERSISTENTE (SQLite)
    cached = get_from_cache(cep_o, cep_d, travel_mode)
    if cached:
        logger.info("[DB CACHE HIT] %s -> %s (%s)", cep_o, cep_d, travel_mode)
        return {
            "origin_cep": cep_o,
            "destination_cep": cep_d,
            "vehicle_type": req.vehicle_type,
            "tomtom_travel_mode": travel_mode,
            "distance": cached["distance_km"],
            "distance_unit": cached["distance_unit"],
            "travel_time": cached["time_min"],
            "time_unit": cached["time_unit"],
            "source": "db_cache"
        }
    logger.info("[DB CACHE MISS] %s -> %s (%s)", cep_o, cep_d, travel_mode)
    # 3) Coordenadas por CEP (com cache em memória)
    lat_o, lon_o = get_coordinates_for_cep(cep_o)
    lat_d, lon_d = get_coordinates_for_cep(cep_d)
    if None in (lat_o, lon_o, lat_d, lon_d):
        raise HTTPException(
            status_code=404,
            detail=f"Não foi possível obter coordenadas para origem='{cep_o}', destino='{cep_d}'."
        )
    # 4) Calcular rota via TomTom (com cache em memória por coordenadas)
    distancia_km, tempo_min = calculate_route_tomtom(lat_o, lon_o, lat_d, lon_d, travel_mode)
    if distancia_km is None or tempo_min is None:
        raise HTTPException(
            status_code=502,
            detail="Falha no cálculo de rota via TomTom."
        )
    # 5) GUARDAR NA CACHE PERSISTENTE (SQLite)
    save_to_cache(
        cep_origem=cep_o,
        cep_destino=cep_d,
        vehicle_type=travel_mode,   # importante: guardamos por travelMode
        distance_km=distancia_km,
        time_min=tempo_min,
        distance_unit="km",
        time_unit="min"
    )
    return {
        "origin_cep": cep_o,
        "destination_cep": cep_d,
        "vehicle_type": req.vehicle_type,
        "tomtom_travel_mode": travel_mode,
        "distance": distancia_km,
        "distance_unit": "km",
        "travel_time": tempo_min,
        "time_unit": "min",
        "source": "tomtom"
    }
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8010, reload=False)
