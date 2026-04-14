# Modulo 11 Lab - OpenSearch + Dashboards + FastAPI

Implementacion local del lab del Modulo 11 (AWS Academy Data Engineering - UAG 2026).

## Estructura

```
modulo11_lab/
├── docker-compose.yml        # Stack: opensearch + dashboards + generator
├── .env                      # Password admin OpenSearch
├── generator/                # FastAPI generador de eventos sinteticos
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py
├── ingesta/                  # Scripts Python de ingesta
│   ├── requirements.txt
│   ├── crear_indice.py       # Crea indice con mapeo explicito
│   ├── ingesta_batch.py      # Bulk API: 5000 eventos
│   └── streaming_producer.py # Simulador de Firehose
└── datos/
```

## Puesta en marcha

```bash
cd modulo11_lab
docker compose up -d opensearch dashboards
docker compose up -d --build generator

# Verificar
curl -k -u admin:'Uag2026!Strong' https://localhost:9200/_cluster/health
curl http://localhost:8000/evento
# Dashboards: http://localhost:5601 (admin / Uag2026!Strong)
```

## Ejecutar ingesta

```bash
cd ingesta
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

python crear_indice.py        # crea indice 'eventos-gaming'
python ingesta_batch.py       # ingresa 5000 docs via Bulk API
python streaming_producer.py  # streaming continuo (Ctrl+C para detener)
```

## Resultados verificados

- Cluster health: `yellow` (single-node, normal sin replicas)
- Generator `/evento` y `/eventos?n=N` responden JSON valido
- Indice `eventos-gaming` con mapeo explicito (keyword para categoricos)
- Ingesta batch: 5000/5000 docs OK, 10 lotes de 500
- Streaming producer: generando ~20 eventos/seg, flush cada 50 docs o 5s
- Query DSL aggregations: ingresos por plataforma funcionando
- SQL plugin: consultas tipo Athena funcionando (usar `DATE_SUB(NOW(), INTERVAL 1 DAY)` para filtros temporales — `NOW() - INTERVAL` no es soportado directamente)

## Nota sobre ejercicio 4.4

La sintaxis del texto original `WHERE timestamp > NOW() - INTERVAL 1 DAY` falla
en el SQL plugin. Usar:

```sql
SELECT plataforma, arma, COUNT(*) AS kills
FROM `eventos-gaming`
WHERE tipo_evento='kill'
  AND timestamp > DATE_SUB(NOW(), INTERVAL 1 DAY)
GROUP BY plataforma, arma
ORDER BY kills DESC LIMIT 15
```

## Visualizar la data en OpenSearch Dashboards

### 1. Login

Abrir **http://localhost:5601** → usuario `admin`, password `Uag2026!Strong`.
Si aparece el tenant selector, elegir **Global**. Si pide "Add sample data" o
"Explore on my own", elegir **Explore on my own**.

### 2. Crear el Index Pattern

El index pattern es el "puente" entre Dashboards y el indice de OpenSearch.

1. Menu lateral (☰) → **Management → Dashboards Management** → **Index patterns**
2. Click **Create index pattern**
3. Index pattern name: `eventos-gaming` → **Next step**
4. Time field: seleccionar `timestamp` → **Create index pattern**

> Si no aparece el indice en el paso 3, verificar que `ingesta_batch.py` ya se
> ejecuto y que `_count` devuelve > 0.

### 3. Explorar datos crudos (Discover)

Menu lateral → **Discover**.

1. Seleccionar el index pattern `eventos-gaming`
2. Arriba a la derecha, abrir el **time picker** y elegir `Last 24 hours`
   (o `Last 15 minutes` si estas corriendo el streaming)
3. Se ven los documentos con todos sus campos
4. En la columna izquierda, click `+` al lado de `plataforma`, `pais`,
   `tipo_evento` para agregarlos como columnas de la tabla
5. Filtros rapidos: click sobre cualquier valor → `Filter for value (+)` o
   `Filter out value (-)`

### 4. Crear las 3 visualizaciones

Menu lateral → **Visualize** → **Create visualization**.

#### 4.1 Pie chart de plataformas

1. Tipo: **Pie**
2. Source: `eventos-gaming`
3. **Metrics → Slice size**: `Count`
4. **Buckets → Add → Split slices**:
   - Aggregation: `Terms`
   - Field: `plataforma`
   - Size: `5`
5. Click el triangulo ▶ (Update) arriba a la derecha
6. **Save** → nombre: `pie_plataformas`

#### 4.2 Heat map pais × plataforma

1. Tipo: **Heat Map**
2. Source: `eventos-gaming`
3. **Metrics**: `Count`
4. **Buckets → Add → Y-axis**: Terms, field `pais`, size `8`
5. **Buckets → Add → X-axis**: Terms, field `plataforma`, size `5`
6. Update → **Save** → `heatmap_pais_plataforma`

#### 4.3 Histograma temporal de eventos

1. Tipo: **Vertical Bar**
2. Source: `eventos-gaming`
3. **Metrics → Y-axis**: `Count`
4. **Buckets → Add → X-axis**:
   - Aggregation: `Date Histogram`
   - Field: `timestamp`
   - Interval: `Auto`
5. **Buckets → Add → Split series**: Terms, field `tipo_evento`, size `7`
6. Update → **Save** → `histograma_eventos`

### 5. Armar el Dashboard

Menu lateral → **Dashboard** → **Create new dashboard**.

1. Click **Add** (arriba)
2. Seleccionar las 3 visualizaciones creadas
3. Arrastrar/redimensionar los paneles
4. **Save** → nombre: `gaming_analytics_overview`

### 6. Auto-refresh en vivo (con streaming_producer corriendo)

Con el dashboard abierto:

1. Arriba a la derecha, click el icono del reloj ⏱
2. **Refresh every**: `10 seconds` → **Start**
3. Cambiar time picker a `Last 15 minutes`
4. En otra terminal: `python streaming_producer.py`
5. Los graficos se actualizan solos

### 7. Dev Tools para consultas ad-hoc

Menu lateral → **Management → Dev Tools**. Permite ejecutar Query DSL y SQL
plugin con autocompletado (mas comodo que `curl`).

Ejemplo SQL plugin:

```
POST /_plugins/_sql
{
  "query": "SELECT plataforma, SUM(monto_usd) AS ingresos FROM `eventos-gaming` WHERE tipo_evento='compra' GROUP BY plataforma ORDER BY ingresos DESC"
}
```

### Troubleshooting Dashboards

| Sintoma | Causa | Solucion |
|---|---|---|
| "No results found" en Discover | Time picker fuera de rango | Cambiar a `Last 24 hours` |
| Index pattern no encuentra `eventos-gaming` | Indice vacio o no creado | Correr `crear_indice.py` + `ingesta_batch.py` |
| No se puede agrupar por `plataforma` (aparece `.keyword`) | Campo mapeado como `text` | El mapeo ya es `keyword`; recargar index pattern con el boton de refresh |
| Dashboard no se refresca en vivo | Auto-refresh apagado | Icono del reloj → Start |

## Generar mas datos (recargar el lab)

```bash
cd ingesta && source venv/bin/activate

# Opcion 1: batch adicional (5000 docs mas, con IDs nuevos no se duplican)
python ingesta_batch.py

# Opcion 2: streaming continuo (Ctrl+C para parar)
python streaming_producer.py

# Opcion 3: reset total del indice
python crear_indice.py        # borra y recrea el indice vacio
python ingesta_batch.py       # lo repuebla
```

## Apagar

```bash
docker compose down       # mantiene volumen (datos persisten)
docker compose down -v    # reset total
```
