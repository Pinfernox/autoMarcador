document.addEventListener("DOMContentLoaded", () => {
    // ==========================================
    // 1. REFERENCIAS AL DOM
    // ==========================================
    
    // --- Archivos y Reproductor ---
    const videoInput = document.getElementById("videoInput");
    const eventsInput = document.getElementById("eventsInput");
    const videoPlayer = document.getElementById("video");
    const btnRender = document.getElementById("btnRender");

    // --- Elementos del Marcador (Visualización) ---
    const timeDisplay = document.getElementById('time');
    const scoreDisplay = document.getElementById('score');
    const localDisplay = document.getElementById('local');
    const visitDisplay = document.getElementById('visitor');

    // --- Elementos del Modal de Configuración ---
    const modal = document.getElementById("configModal");
    const btnOpenConfig = document.getElementById("btnOpenConfig");
    const btnCloseConfig = document.getElementById("btnCloseConfig");
    const btnApplyConfig = document.getElementById("btnApplyConfig");

    // --- Inputs del Modal ---
    const cfgMainBg = document.getElementById("cfgMainBg");
    const cfgInfoBg = document.getElementById("cfgInfoBg");
    const cfgTextColor = document.getElementById("cfgTextColor");
    
    const inputLocalName = document.getElementById("inputLocalName");
    const cfgLocStrip1 = document.getElementById("cfgLocStrip1");
    const cfgLocStrip2 = document.getElementById("cfgLocStrip2");
    
    const inputVisitName = document.getElementById("inputVisitName");
    const cfgVisStrip1 = document.getElementById("cfgVisStrip1");
    const cfgVisStrip2 = document.getElementById("cfgVisStrip2");


    // ==========================================
    // 2. LÓGICA DEL REPRODUCTOR (Video y TXT)
    // ==========================================
    let matchEvents = []; // Aquí guardamos los goles

    // A) Cargar Video
    videoInput.addEventListener("change", e => {
        const file = e.target.files[0];
        if (file) {
            videoPlayer.src = URL.createObjectURL(file);
            // videoPlayer.hidden = false; // Ya no es necesario ocultarlo
        }
    });

    // B) Cargar y Parsear TXT
    eventsInput.addEventListener("change", async e => {
        const file = e.target.files[0];
        if (!file) return;

        const text = await file.text();
        matchEvents = parseTxtEvents(text);
        console.log("Eventos cargados:", matchEvents);
    });

    // Función para leer el archivo de texto
    function parseTxtEvents(text) {
        const lines = text.split("\n");
        const events = [];
        let localScore = 0;
        let visitorScore = 0;

        lines.forEach(line => {
            line = line.trim();
            if (!line) return;

            // Separar tiempo (00:00) del resto
            const parts = line.split(" ");
            if (parts.length < 2) return;

            const timeParts = parts[0].split(":");
            if (timeParts.length !== 2) return;

            const seconds = parseInt(timeParts[0]) * 60 + parseInt(timeParts[1]);
            const desc = line.substring(parts[0].length).toLowerCase();

            if (desc.includes("gol")) {
                // Detectar si es visitante o local
                if (desc.includes("(v)") || desc.includes("visitante")) {
                    visitorScore++;
                } else {
                    localScore++; // Por defecto local
                }

                events.push({
                    time: seconds,
                    local: localScore,
                    visitor: visitorScore
                });
            }
        });
        return events;
    }

    // C) Actualizar Marcador en Tiempo Real
    videoPlayer.addEventListener("timeupdate", () => {
        const t = Math.floor(videoPlayer.currentTime);
        
        // 1. Reloj
        const m = Math.floor(t / 60).toString().padStart(2, "0");
        const s = (t % 60).toString().padStart(2, "0");
        timeDisplay.innerText = `${m}:${s}`;

        // 2. Goles
        let currentLocal = 0;
        let currentVisitor = 0;

        // Buscamos el último evento que haya ocurrido antes del segundo actual
        for (let event of matchEvents) {
            if (event.time <= t) {
                currentLocal = event.local;
                currentVisitor = event.visitor;
            }
        }
        scoreDisplay.innerText = `${currentLocal} - ${currentVisitor}`;
    });


    // ==========================================
    // 3. LÓGICA DE PERSONALIZACIÓN (Modal)
    // ==========================================

    // Abrir/Cerrar Modal
    btnOpenConfig.addEventListener("click", () => modal.classList.remove("hidden"));
    btnCloseConfig.addEventListener("click", () => modal.classList.add("hidden"));
    btnApplyConfig.addEventListener("click", () => modal.classList.add("hidden"));

    // Función auxiliar para actualizar variables CSS
    const setCSS = (varName, value) => document.documentElement.style.setProperty(varName, value);

    // --- Actualización en tiempo real ---

    // Estilos Generales
    cfgMainBg.addEventListener("input", (e) => setCSS("--sb-bg-main", e.target.value));
    cfgInfoBg.addEventListener("input", (e) => setCSS("--sb-bg-info", e.target.value));
    cfgTextColor.addEventListener("input", (e) => setCSS("--sb-text", e.target.value));

    // Estilos Local
    cfgLocStrip1.addEventListener("input", (e) => setCSS("--loc-s1", e.target.value));
    cfgLocStrip2.addEventListener("input", (e) => setCSS("--loc-s2", e.target.value));

    // Estilos Visitante
    cfgVisStrip1.addEventListener("input", (e) => setCSS("--vis-s1", e.target.value));
    cfgVisStrip2.addEventListener("input", (e) => setCSS("--vis-s2", e.target.value));

    // Validación y cambio de Nombres
    function cleanName(text) {
        // Solo mayúsculas, A-Z, máx 6 chars
        return text.toUpperCase().replace(/[^A-Z]/g, '').substring(0, 6);
    }

    inputLocalName.addEventListener("input", (e) => {
        const val = cleanName(e.target.value);
        e.target.value = val;
        localDisplay.innerText = val || "LOCAL";
    });

    inputVisitName.addEventListener("input", (e) => {
        const val = cleanName(e.target.value);
        e.target.value = val;
        visitDisplay.innerText = val || "VISIT";
    });


    // ==========================================
    // 4. ENVÍO AL SERVIDOR (Renderizar)
    // ==========================================
    btnRender.addEventListener("click", async () => {
        const videoFile = videoInput.files[0];
        const txtFile = eventsInput.files[0];

        if (!videoFile || !txtFile) {
            alert("⚠️ Por favor sube el VIDEO y el archivo TXT.");
            return;
        }

        const btnText = btnRender.innerText;
        btnRender.innerText = "⏳ Procesando... (Esto puede tardar)";
        btnRender.disabled = true;

        const formData = new FormData();
        formData.append("video", videoFile);
        formData.append("events", txtFile);

        // -- Convertimos datos del modal para enviarlos a Python --
        // Función para quitar el '#' y poner '0x' (Formato FFmpeg)
        const hex = (h) => "0x" + h.substring(1);

        formData.append("main_bg", hex(cfgMainBg.value));
        formData.append("info_bg", hex(cfgInfoBg.value));
        formData.append("text_color", hex(cfgTextColor.value));

        formData.append("local_name", inputLocalName.value || "LOCAL");
        formData.append("loc_s1", hex(cfgLocStrip1.value));
        formData.append("loc_s2", hex(cfgLocStrip2.value));

        formData.append("visit_name", inputVisitName.value || "VISIT");
        formData.append("vis_s1", hex(cfgVisStrip1.value));
        formData.append("vis_s2", hex(cfgVisStrip2.value));

        try {
            const response = await fetch("/render", { method: "POST", body: formData });
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                // Nombre del archivo de descarga
                a.download = `Resumen_${inputLocalName.value || 'Local'}_vs_${inputVisitName.value || 'Visit'}.mp4`;
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);
                alert("✅ ¡Video generado y descargado con éxito!");
            } else {
                alert("❌ Error en el servidor. Revisa la consola para más detalles.");
            }
        } catch (e) {
            console.error(e);
            alert("❌ Error de conexión con el servidor.");
        } finally {
            btnRender.innerText = btnText;
            btnRender.disabled = false;
        }
    });
});