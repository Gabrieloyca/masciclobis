# WebMap de análisis de accesibilidad urbana

Esta aplicación genera indicadores de accesibilidad y conectividad sobre la red de calles de OpenStreetMap y los expone en un visor web interactivo construido con HTML, CSS y JavaScript.

## Requisitos

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Ejecución

### 1. Preparar el entorno

1. **Abrir una terminal** (en Windows puedes usar PowerShell, en macOS/Linux la app “Terminal”).
2. **Moverte a la carpeta del proyecto**. Si acabas de clonar el repositorio, ejecuta:
   ```bash
   cd masciclobis
   ```
3. **Activar el entorno virtual** donde instalaste las dependencias. Si seguiste los pasos de la sección anterior, usa:
   ```bash
   source .venv/bin/activate      # En Windows: .venv\Scripts\activate
   ```
   Verás que en la terminal aparece el prefijo `(.venv)` indicando que está activo.

### 2. Encender el servidor paso a paso

1. **Escribir el comando** que inicia el backend (API + archivos estáticos):
   ```bash
   uvicorn app.api:app --reload
   ```
2. **Presionar la tecla Enter**. La terminal mostrará mensajes como `Uvicorn running on http://127.0.0.1:8000`. No cierres esta ventana mientras uses la app: el servidor necesita seguir encendido.

### 3. Abrir el visor en el navegador

1. **Abrir tu navegador favorito** (Chrome, Firefox, Edge, Safari, etc.).
2. **Escribir la dirección** `http://127.0.0.1:8000/` en la barra superior y pulsar Enter. Se cargará una página con un mapa al centro y una barra lateral gris oscuro.

### 4. Usar la barra lateral (instrucciones ultra detalladas)

1. **Buscar un territorio**:
   - Haz clic dentro del campo que dice *“Buscar ciudad o dirección”*.
   - Escribe el nombre del lugar, por ejemplo `Rouen, France`.
   - Pulsa el botón azul *“Descargar desde OpenStreetMap”*. El mapa se moverá al área elegida y verás un mensaje de progreso en la parte inferior de la barra lateral.
2. **Elegir el modo de viaje**:
   - En la sección *“Modo de red”*, haz clic en el icono correspondiente: peatón (persona caminando), bicicleta o automóvil.
   - El icono seleccionado queda resaltado con un borde azul.
3. **Configurar el radio de análisis**:
   - Arrastra el control deslizante bajo *“Radio (metros)”* o escribe un número en la casilla para indicar la distancia máxima que se utilizará en los cálculos de accesibilidad.
4. **Calcular indicadores de conectividad**:
   - En *“Indicadores de red”* encontrarás interruptores (switches) para Betweenness, Closeness, Degree, Straightness y Eigenvector.
   - Activa uno o varios moviendo el interruptor hacia la derecha (se pondrá de color azul). Después presiona el botón *“Calcular indicadores”* que está justo debajo.
   - Tras unos segundos el mapa coloreará las calles según el indicador elegido y aparecerá una leyenda explicando los valores.
5. **Analizar accesibilidad y hexágonos H3**:
   - En la sección *“Accesibilidad”*, define el tamaño de las celdas H3 con el control desplegable.
   - Activa el interruptor *“Calcular cobertura H3”* si quieres ver la agregación hexagonal.
   - Pulsa *“Calcular accesibilidad”*. Se agregarán capas adicionales con los resultados.
6. **Descargar resultados**:
   - Bajo *“Descargas”* encontrarás botones para obtener el GeoJSON de la red, el GeoJSON/CSV de hexágonos y un archivo ZIP con todos los datos.
   - Haz clic en cada botón y el navegador descargará los archivos a tu carpeta de descargas.
7. **Trabajar sin conexión a Overpass** (opcional):
   - Si tu conexión a Internet falla, desplázate a la sección *“Opciones avanzadas”*.
   - Activa el interruptor *“Permitir red sintética si Overpass no responde”*. Esto genera una cuadrícula artificial para seguir probando la interfaz, aunque los resultados no representen una ciudad real.

### 5. Apagar el servidor cuando termines

1. Vuelve a la terminal donde corre Uvicorn.
2. Presiona `Ctrl + C` (o `Cmd + C` en macOS) una vez. El servidor se detendrá y verás nuevamente el prompt de la terminal.

Con estos pasos tendrás la aplicación funcionando y sabrás exactamente qué hacer en cada pantalla aunque no tengas experiencia previa.

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
