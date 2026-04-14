"""
Pide N eventos al generador FastAPI y los envia a OpenSearch via Bulk API.
Equivalente AWS: una Lambda activada por trigger, que recibe registros
y los empuja a OpenSearch Service.
"""
import requests
import urllib3
from opensearchpy import OpenSearch, helpers

urllib3.disable_warnings()

INDICE = "eventos-gaming"
GENERADOR_URL = "http://localhost:8000/eventos"
TOTAL_EVENTOS = 5000
BATCH_SIZE = 500

cliente = OpenSearch(
    hosts=[{"host": "localhost", "port": 9200}],
    http_auth=("admin", "Uag2026!Strong"),
    use_ssl=True,
    verify_certs=False,
    ssl_show_warn=False,
)


def generar_acciones(eventos):
    """Convierte eventos en el formato que espera la Bulk API."""
    for evento in eventos:
        yield {
            "_index": INDICE,
            "_id": evento["evento_id"],
            "_source": evento,
        }


def main():
    enviados = 0
    while enviados < TOTAL_EVENTOS:
        n = min(BATCH_SIZE, TOTAL_EVENTOS - enviados)
        eventos = requests.get(GENERADOR_URL, params={"n": n}).json()

        exitos, errores = helpers.bulk(
            cliente,
            generar_acciones(eventos),
            raise_on_error=False,
        )
        enviados += exitos
        print(f"Lote enviado: {exitos} ok, {len(errores) if errores else 0} errores. Total: {enviados}")

    cliente.indices.refresh(INDICE)
    stats = cliente.count(index=INDICE)
    print(f"\nDocumentos en el indice: {stats['count']}")


if __name__ == "__main__":
    main()
