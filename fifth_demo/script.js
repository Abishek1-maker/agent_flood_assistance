// ============================================================================
// SECTION 1: SIDEBAR INTERACTION & RESIZE HANDLERS
// ============================================================================
const chatPanel = document.getElementById("chat_panel");
const toggleBtn = document.getElementById("toggle_btn");
const resizer = document.getElementById("resizer_handle");
const sendBtn = document.getElementById("send_btn");
const userInput = document.getElementById("user_input");
const chatHistory = document.getElementById("chat_history");
const langSelect = document.getElementById("lang_select");

let history = [];

// Sidebar visibility toggle
toggleBtn.addEventListener("click", () => {
  chatPanel.classList.toggle("hidden");
  if (typeof map !== 'undefined') {
    setTimeout(() => { map.invalidateSize(); }, 200);
  }
});

// Drag to resize sidebar
let isResizing = false;
resizer.addEventListener("mousedown", () => {
  isResizing = true;
  resizer.classList.add("dragging");
  document.body.style.cursor = "col-resize";
  document.body.style.userSelect = "none";
});

document.addEventListener("mousemove", (e) => {
  if (!isResizing) return;
  const newWidth = window.innerWidth - e.clientX;
  if (newWidth >= 240 && newWidth <= 600) {
    chatPanel.style.width = newWidth + "px";
    if (typeof map !== 'undefined') {
      map.invalidateSize();
    }
  }
});

document.addEventListener("mouseup", () => {
  if (isResizing) {
    isResizing = false;
    resizer.classList.remove("dragging");
    document.body.style.cursor = "default";
    document.body.style.userSelect = "auto";
  }
});

// ============================================================================
// SECTION 2: FASTAPI BACKEND CHAT INTEGRATION
// ============================================================================
let isGenerating = false;
async function sendMessage() {
  const message = userInput.value.trim();
  if (!message || isGenerating) return;

  isGenerating = true;
  sendBtn.disabled = true;
  sendBtn.style.opacity = "0.4";

  appendMessage(message, "user");
  userInput.value = "";

  const loadingDiv = document.createElement("div");
  loadingDiv.className = "msg loading";
  loadingDiv.textContent = "Pravah AI is responding...";
  chatHistory.appendChild(loadingDiv);
  chatHistory.scrollTop = chatHistory.scrollHeight;

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: message,
        history: history,
        language: langSelect.value,
      }),
    });

    const data = await res.json();
    if (chatHistory.contains(loadingDiv)) {
      chatHistory.removeChild(loadingDiv);
    }
    appendMessage(data.response, "bot");
    history.push([message, data.response]);
  } catch (err) {
    if (chatHistory.contains(loadingDiv)) {
      chatHistory.removeChild(loadingDiv);
    }
    appendMessage("Error communicating with AI engine.", "bot");
  } finally {
    isGenerating = false;
    sendBtn.disabled = false;
    sendBtn.style.opacity = "1";
  }
}

// Robust Multi-Layer Markdown & Bullet Point Formatter
function appendMessage(text, sender) {
  const msgDiv = document.createElement("div");
  msgDiv.className = `msg ${sender}`;

  let formattedText = text || "";

  // 1. Process Markdown Bold (**text** -> <strong>text</strong>)
  formattedText = formattedText.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

  // 2. Fix inline asterisk lists: convert any " * " or " *" or "* " into line break + bullet
  formattedText = formattedText.replace(/(\s*\*|\*\s*)/g, "<br>• ");

  // 3. Convert all standard system newlines (\n) to HTML line breaks (<br>)
  formattedText = formattedText.replace(/\n/g, "<br>");

  // 4. Cleanup double line breaks
  formattedText = formattedText.replace(/(<br>\s*){3,}/g, "<br><br>");

  msgDiv.innerHTML = formattedText;
  chatHistory.appendChild(msgDiv);
  chatHistory.scrollTop = chatHistory.scrollHeight;
}

sendBtn.addEventListener("click", sendMessage);
userInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendMessage();
});

// ============================================================================
// SECTION 3: BASE MAP INITIALIZATION & TILE LAYERS
// ============================================================================
const map = L.map('map').setView([28.3949, 84.1240], 7);

const googleStandard = L.tileLayer('https://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', {
  maxZoom: 20,
  subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
  attribution: '&copy; Google Maps'
});

const googleHybrid = L.tileLayer('https://{s}.google.com/vt/lyrs=s,h&x={x}&y={y}&z={z}', {
  maxZoom: 20,
  subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
  attribution: '&copy; Google Maps'
});

const enhancedTerrain = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}', {
  maxZoom: 19,
  attribution: 'Tiles &copy; Esri'
});

const detailedAQI = L.tileLayer('https://tiles.aqicn.org/tiles/usepa-aqi/{z}/{x}/{y}.png', {
  maxZoom: 18,
  opacity: 0.75,
  attribution: 'Air Quality &copy; WAQI'
});

googleStandard.addTo(map);

const baseMaps = {
  "🗺️ Standard": googleStandard,
  "🛰️ Satellite": googleHybrid,
  "⛰️ High-Res Terrain": enhancedTerrain
};

const overlayMaps = {
  "💨 Air Quality Overlay": detailedAQI
};

const layerControl = L.control.layers(baseMaps, overlayMaps, { position: 'topright' }).addTo(map);

// Default risk station markers
L.marker([27.7172, 85.3240]).addTo(map)
  .bindPopup('<b>Kathmandu</b><br>Flood Risk: Low (11.8%)');

L.marker([28.6833, 80.6000]).addTo(map)
  .bindPopup('<b>Kailali District</b><br>Flash Flood Risk: Moderate (23.7%)');

// ============================================================================
// 🚨 [TEAMMATE INSERTION POINT: CHHUCHE MAP POLYGONS & TELEMETRY LAYERS]
// ----------------------------------------------------------------------------
// YOUR FRIEND CAN ADD THEIR GEOJSON DATA OR CUSTOM VECTOR LAYERS HERE:
// ============================================================================