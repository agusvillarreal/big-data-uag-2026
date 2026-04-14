"""
Simulador de Amazon Data Firehose.
Politica: enviar lote cuando se acumulen MAX_RECORDS o pasen MAX_SECONDS,
lo que ocurra primero (politica clasica de buffer de Firehose).
"""
import time
import requests
import urllib3
from datetime import datetime
from opensearchpy import OpenSearch, helpers

urllib3.disable_warnings()

INDICE = "eventos-gaming"
GENERADOR_URL = "http://localhost:8000/evento"

MAX_RECORDS = 50
MAX_SECONDS = 5
EVENTOS_POR_SEGUNDO = 20

cliente = OpenSearch(
    hosts=[{"host": "localhost", "port": 9200}],
    http_auth=("admin", "Uag2026!Strong"),
    use_ssl=True, verify_certs=False, ssl_show_warn=False,
)


def flush(buffer):
    if not buffer:
        return 0
    acciones = [{"_index": INDICE, "_id": e["evento_id"], "_source": e} for e in buffer]
    exitos, _ = helpers.bulk(cliente, acciones, raise_on_error=False)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] flush: {exitos} eventos enviados")
    return exitos


def main():
    buffer = []
    ultimo_flush = time.time()
    intervalo_generacion = 1.0 / EVENTOS_POR_SEGUNDO
    total = 0

    print(f"Iniciando productor: {EVENTOS_POR_SEGUNDO} eventos/seg, "
          f"flush cada {MAX_RECORDS} registros o {MAX_SECONDS}s")
    print("Ctrl+C para detener\n")

    try:
        while True:
            evento = requests.get(GENERADOR_URL, timeout=2).json()
            buffer.append(evento)

            tiempo_transcurrido = time.time() - ultimo_flush
            if len(buffer) >= MAX_RECORDS or tiempo_transcurrido >= MAX_SECONDS:
                total += flush(buffer)
                buffer = []
                ultimo_flush = time.time()

            time.sleep(intervalo_generacion)

    except KeyboardInterrupt:
        print(f"\nDeteniendo... Flush final del buffer ({len(buffer)} eventos)")
        total += flush(buffer)
        print(f"Total enviado en esta sesion: {total}")


if __name__ == "__main__":
    main()
