const map = L.map("map", { preferCanvas: true }).setView([48.8566, 2.3522], 12);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "&copy; OpenStreetMap contributors",
  maxZoom: 19,
}).addTo(map);

let edgesLayer = null;
let h3Layer = null;
let legendControl = null;

const form = document.getElementById("analysis-form");
const statusEl = document.getElementById("form-status");
const submitBtn = document.getElementById("submit-btn");
const downloadsSection = document.getElementById("downloads");
const downloadEdges = document.getElementById("download-edges");
const downloadMetrics = document.getElementById("download-metrics");
const downloadH3 = document.getElementById("download-h3");
const metricsPanel = document.getElementById("metrics-panel");
const metricsSummary = document.getElementById("metrics-summary");
const metricsTableBody = document.querySelector("#metrics-table tbody");

function formatNumber(value) {
  if (value === null || value === undefined) {
    return "—";
  }
  if (typeof value === "number" && !Number.isInteger(value)) {
    return value.toLocaleString(undefined, { maximumFractionDigits: 3 });
  }
  if (typeof value === "number") {
    return value.toLocaleString();
  }
  return String(value);
}

function buildPopup(properties) {
  const entries = [];
  const names = [
    ["name", "Nombre"],
    ["highway", "Tipo"],
    ["length", "Longitud (m)"],
    ["betweenness", "Betweenness"],
    ["closeness", "Closeness"],
    ["degree", "Grado"],
    ["straightness", "Straightness"],
    ["eigenvector", "Eigenvector"],
  ];
  for (const [key, label] of names) {
    if (properties[key] !== undefined && properties[key] !== null) {
      entries.push(`<strong>${label}:</strong> ${formatNumber(properties[key])}`);
    }
  }
  return entries.join("<br/>");
}

function updateLegend(mapInfo) {
  if (legendControl) {
    map.removeControl(legendControl);
    legendControl = null;
  }
  if (!mapInfo || !mapInfo.legend) {
    return;
  }
  legendControl = L.control({ position: "bottomleft" });
  legendControl.onAdd = () => {
    const container = L.DomUtil.create("div", "map-legend");
    container.innerHTML = `
      <h3>${mapInfo.colorBy ?? "Leyenda"}</h3>
      <ul>
        ${mapInfo.legend
          .map((item, idx) => {
            const label = item.label || `Clase ${idx + 1}`;
            return `<li><span style="background:${item.color}"></span>${label}</li>`;
          })
          .join("")}
      </ul>
    `;
    return container;
  };
  legendControl.addTo(map);
}

function updateMetrics(metrics, table) {
  metricsSummary.replaceChildren();
  metricsPanel.hidden = !metrics || Object.keys(metrics).length === 0;
  if (!metrics || Object.keys(metrics).length === 0) {
    return;
  }

  Object.entries(metrics).forEach(([key, value]) => {
    const item = document.createElement("div");
    item.className = "metric";
    const label = document.createElement("span");
    label.className = "label";
    label.textContent = key;
    const val = document.createElement("span");
    val.className = "value";
    val.textContent = formatNumber(value);
    item.append(label, val);
    metricsSummary.appendChild(item);
  });

  metricsTableBody.replaceChildren();
  if (Array.isArray(table)) {
    table.forEach((row) => {
      const tr = document.createElement("tr");
      const tdIndicator = document.createElement("td");
      tdIndicator.textContent = row.indicateur ?? row.indicador ?? row.index ?? "";
      const tdValue = document.createElement("td");
      tdValue.textContent = formatNumber(row.valeur ?? row.valor ?? row.value ?? Object.values(row)[1]);
      tr.append(tdIndicator, tdValue);
      metricsTableBody.appendChild(tr);
    });
  }
}

function updateDownloads(downloads) {
  if (!downloads) {
    downloadsSection.hidden = true;
    return;
  }
  const { edgesGeoJSON, metricsCSV, h3GeoJSON } = downloads;
  if (edgesGeoJSON) {
    downloadEdges.href = `data:application/geo+json;charset=utf-8,${encodeURIComponent(edgesGeoJSON)}`;
  }
  if (metricsCSV) {
    downloadMetrics.href = `data:text/csv;charset=utf-8,${encodeURIComponent(metricsCSV)}`;
  }
  if (h3GeoJSON) {
    downloadH3.href = `data:application/geo+json;charset=utf-8,${encodeURIComponent(h3GeoJSON)}`;
    downloadH3.hidden = false;
  } else {
    downloadH3.hidden = true;
  }
  downloadsSection.hidden = !(edgesGeoJSON || metricsCSV || h3GeoJSON);
}

async function submitAnalysis(event) {
  event.preventDefault();
  const payload = {
    city: document.getElementById("city").value,
    mode: document.getElementById("mode").value,
    radius_km: parseFloat(document.getElementById("radius_km").value),
    do_centrality: document.getElementById("do_centrality").checked,
    do_closeness: document.getElementById("do_closeness").checked,
    do_degree: document.getElementById("do_degree").checked,
    do_straightness: document.getElementById("do_straightness").checked,
    do_eigenvector: document.getElementById("do_eigenvector").checked,
    do_h3: document.getElementById("do_h3").checked,
    h3_res: parseInt(document.getElementById("h3_res").value, 10),
    color_by: document.getElementById("color_by").value,
    allow_synthetic: document.getElementById("allow_synthetic").checked,
  };

  submitBtn.disabled = true;
  statusEl.textContent = "Calculando… Esta operación puede tardar unos minutos";

  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      let message = error.detail?.error || error.detail || "No se pudo completar el análisis";
      if (error.detail?.code === "osm_unavailable" || error.code === "osm_unavailable") {
        message +=
          ". Verifica tu conexión a Overpass (puedes configurar OVERPASS_API_URL o activar la red sintética en Opciones avanzadas).";
      }
      throw new Error(message);
    }

    const result = await response.json();
    renderResult(result);
    statusEl.textContent = "Análisis completado";
  } catch (error) {
    console.error(error);
    statusEl.textContent = error.message;
  } finally {
    submitBtn.disabled = false;
  }
}

function renderResult(result) {
  if (!result || !result.map) {
    return;
  }

  const { map: mapInfo, h3, metrics, metricsTable, downloads } = result;

  if (mapInfo.center) {
    map.setView([mapInfo.center.lat, mapInfo.center.lng], mapInfo.zoom || 13);
  }

  if (edgesLayer) {
    edgesLayer.remove();
  }
  edgesLayer = L.geoJSON(mapInfo.geojson, {
    style: (feature) => feature?.properties?.__style || { color: "#1976d2", weight: 2, opacity: 0.85 },
    onEachFeature: (feature, layer) => {
      const popup = buildPopup(feature.properties || {});
      if (popup) {
        layer.bindPopup(popup);
      }
    },
  }).addTo(map);

  if (h3Layer) {
    h3Layer.remove();
  }
  if (h3 && h3.geojson) {
    h3Layer = L.geoJSON(h3.geojson, {
      style: () => ({ color: "#f59e0b", weight: 1, fillOpacity: 0.35 }),
      onEachFeature: (feature, layer) => {
        const props = feature.properties || {};
        const popup = Object.entries(props)
          .map(([key, value]) => `<strong>${key}:</strong> ${formatNumber(value)}`)
          .join("<br/>");
        if (popup) {
          layer.bindPopup(popup);
        }
      },
    }).addTo(map);
  }

  updateLegend(mapInfo);
  updateMetrics(metrics, metricsTable);
  updateDownloads(downloads);
}

form.addEventListener("submit", submitAnalysis);

// Lanzar una petición inicial en segundo plano para precalentar el backend
submitAnalysis(new Event("submit", { cancelable: true }));
