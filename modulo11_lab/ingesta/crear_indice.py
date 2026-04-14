"""
Crea el indice de eventos de gaming con mapeo explicito.
Equivalente AWS: definir el schema de un Glue Table.
"""
from opensearchpy import OpenSearch
import urllib3

urllib3.disable_warnings()

INDICE = "eventos-gaming"

cliente = OpenSearch(
    hosts=[{"host": "localhost", "port": 9200}],
    http_auth=("admin", "Uag2026!Strong"),
    use_ssl=True,
    verify_certs=False,
    ssl_show_warn=False,
)

mapeo = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "refresh_interval": "5s",
    },
    "mappings": {
        "properties": {
            "evento_id":    {"type": "keyword"},
            "timestamp":    {"type": "date"},
            "jugador_id":   {"type": "keyword"},
            "pais":         {"type": "keyword"},
            "plataforma":   {"type": "keyword"},
            "tipo_evento":  {"type": "keyword"},
            "mapa":         {"type": "keyword"},
            "arma":         {"type": "keyword"},
            "duracion_ms":  {"type": "integer"},
            "monto_usd":    {"type": "float"},
        }
    },
}

if cliente.indices.exists(INDICE):
    print(f"Indice {INDICE} ya existe. Borrando para recrear...")
    cliente.indices.delete(INDICE)

cliente.indices.create(INDICE, body=mapeo)
print(f"Indice {INDICE} creado correctamente")
print(cliente.indices.get_mapping(INDICE))
