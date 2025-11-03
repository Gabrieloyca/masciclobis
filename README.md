# WebMap de análisis de accesibilidad urbana

Esta aplicación genera indicadores de accesibilidad y conectividad sobre la red de calles de OpenStreetMap y los expone en un visor web interactivo construido con HTML, CSS y JavaScript.

## Requisitos

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Ejecución

Inicia el servidor FastAPI (sirve la API y los archivos estáticos del visor):

```bash
uvicorn app.api:app --reload
```

Luego abre `http://127.0.0.1:8000/` en tu navegador para acceder al mapa. Desde la barra lateral podrás:

- Elegir cualquier ciudad o dirección (la descarga se realiza directamente vía Overpass / OpenStreetMap).
- Seleccionar el perfil de movilidad (peatonal, bicicleta o vehículo) y el radio de análisis.
- Activar indicadores de betweenness, closeness, grado, straightness y eigenvector para colorear la red.
- Generar la malla H3 agregada y descargar los GeoJSON/CSV resultantes.
- Habilitar un grafo sintético de respaldo si trabajas sin acceso a Overpass.

### Configuración de Overpass y ejecución sin conexión

El módulo `grafos.loader` intenta varios endpoints de Overpass. Puedes personalizar el comportamiento mediante variables de entorno:

- `OVERPASS_API_URL`: endpoint principal a utilizar.
- `OVERPASS_EXTRA_ENDPOINTS`: lista separada por comas de endpoints alternativos.
- `OVERPASS_TIMEOUT`: tiempo de espera en segundos (por defecto 180).
- `OSM_CACHE_DIR`: carpeta local para cachear descargas de OSMnx.
- `HTTP_PROXY` / `HTTPS_PROXY`: proxies a utilizar para las peticiones.
- `OSM_GRAPHML_PATH`: ruta a un archivo `.graphml` local que quieras reutilizar en lugar de descargar.

Si necesitas ejecutar el flujo sin conexión, activa la casilla *“Permitir red sintética si Overpass no responde”* en la interfaz web o establece la variable `ALLOW_SYNTHETIC_GRAPH=1` antes de arrancar el servidor.

## Tests

```bash
pytest
```

Las pruebas que requieren conexión con Overpass están marcadas con `@pytest.mark.network` y se omitirán automáticamente si el servicio no responde.
