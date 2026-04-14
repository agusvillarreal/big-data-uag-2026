"""
Generador de eventos sinteticos de gaming analytics.
Simula el origen de datos del slide 33 del modulo 11.

Endpoints:
  GET  /evento              -> 1 evento aleatorio
  GET  /eventos?n=100       -> N eventos en batch
  GET  /jugadores?n=10      -> dimension de jugadores
"""
from fastapi import FastAPI, Query
from pydantic import BaseModel
from faker import Faker
from datetime import datetime, timezone
import random
import uuid

app = FastAPI(title="Gaming Analytics Generator", version="1.0")
fake = Faker(["es_MX", "en_US"])

ARMAS = ["pistola", "rifle", "escopeta", "francotirador", "cuchillo", "granada"]
MAPAS = ["desierto_alpha", "ciudad_neon", "isla_tropico", "estacion_orbital", "bosque_oscuro"]
EVENTOS = ["kill", "death", "compra", "match_start", "match_end", "logout", "login"]
PLATAFORMAS = ["PC", "PS5", "Xbox", "Switch", "Mobile"]
PAISES = ["MX", "US", "BR", "AR", "CO", "ES", "CL", "PE"]


class Evento(BaseModel):
    evento_id: str
    timestamp: str
    jugador_id: str
    pais: str
    plataforma: str
    tipo_evento: str
    mapa: str
    arma: str | None
    duracion_ms: int
    monto_usd: float


def _generar_evento() -> Evento:
    tipo = random.choice(EVENTOS)
    es_compra = tipo == "compra"
    return Evento(
        evento_id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc).isoformat(),
        jugador_id=f"player_{random.randint(1, 5000):05d}",
        pais=random.choice(PAISES),
        plataforma=random.choice(PLATAFORMAS),
        tipo_evento=tipo,
        mapa=random.choice(MAPAS),
        arma=random.choice(ARMAS) if tipo in ("kill", "death", "compra") else None,
        duracion_ms=random.randint(50, 30_000),
        monto_usd=round(random.uniform(0.99, 49.99), 2) if es_compra else 0.0,
    )


@app.get("/evento", response_model=Evento)
def evento():
    return _generar_evento()


@app.get("/eventos", response_model=list[Evento])
def eventos(n: int = Query(100, ge=1, le=10_000)):
    return [_generar_evento() for _ in range(n)]


@app.get("/jugadores")
def jugadores(n: int = Query(10, ge=1, le=1000)):
    """Dimension de jugadores (datos relativamente estables)."""
    return [
        {
            "jugador_id": f"player_{i:05d}",
            "nickname": fake.user_name(),
            "pais_registro": random.choice(PAISES),
            "fecha_registro": fake.date_between("-3y", "today").isoformat(),
            "nivel": random.randint(1, 100),
            "es_premium": random.random() < 0.18,
        }
        for i in range(1, n + 1)
    ]


@app.get("/health")
def health():
    return {"status": "ok"}
