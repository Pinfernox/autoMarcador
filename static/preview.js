console.log("✅ preview.js cargado (Versión Final Corregida)");

document.addEventListener('DOMContentLoaded', () => {
    
    // --- 1. REFERENCIAS DOM ---
    const els = {
        // Contenedores
        scoreboardOverlay: document.getElementById('scoreboardOverlay'),
        videoPlayer: document.getElementById('video'),
        chkShowLiga: document.getElementById('chkShowLiga'),

        // Textos e Inputs
        localName: document.getElementById('local'),
        visitName: document.getElementById('visitor'),
        localNameInput: document.getElementById('inputLocalName'),
        visitNameInput: document.getElementById('inputVisitName'),
        
        // Colores
        mainBg: document.getElementById('cfgMainBg'),
        infoBg: document.getElementById('cfgInfoBg'),
        textColor: document.getElementById('cfgTextColor'),
        cfgLocStrip1: document.getElementById('cfgLocStrip1'),
        cfgLocStrip2: document.getElementById('cfgLocStrip2'),
        cfgVisStrip1: document.getElementById('cfgVisStrip1'),
        cfgVisStrip2: document.getElementById('cfgVisStrip2'),

        // Estilos
        styleLocalSelect: document.getElementById('styleLocal'),
        styleVisitSelect: document.getElementById('styleVisit'),
        stripsLocal: document.getElementById('stripsLocal'),
        stripsVisit: document.getElementById('stripsVisit'),

        // Archivos
        videoInput: document.getElementById('videoInput'),
        eventsInput: document.getElementById('eventsInput'),
        
        // Imágenes
        imgLocalInput: document.getElementById('imgLocal'),
        btnDelLocal: document.getElementById('btnDelLocal'),
        labelImgLocal: document.getElementById('labelImgLocal'),
        previewLogoLocal: document.getElementById('previewLogoLocal'),
        
        imgVisitInput: document.getElementById('imgVisit'),
        btnDelVisit: document.getElementById('btnDelVisit'),
        labelImgVisit: document.getElementById('labelImgVisit'),
        previewLogoVisit: document.getElementById('previewLogoVisit'),
        
        imgLigaInput: document.getElementById('imgLiga'),
        btnDelLiga: document.getElementById('btnDelLiga'),
        labelImgLiga: document.getElementById('labelImgLiga'),
        previewLogoLiga: document.getElementById('previewLogoLiga'),
        ligaPlaceholder: document.getElementById('ligaPlaceholder'),

        // Botones y Modal
        btnRender: document.getElementById('btnRender'),
        btnOpenConfig: document.getElementById('btnOpenConfig'),
        btnCloseConfig: document.getElementById('btnCloseConfig'),
        btnApplyConfig: document.getElementById('btnApplyConfig'),
        modal: document.getElementById('configModal'),

        // Progreso y Feedback
        progressContainer: document.getElementById('progressContainer'),
        progressBar: document.getElementById('progressBar'),
        progressText: document.getElementById('progressText'),
        progressStatus: document.getElementById('progressStatus'),
        toastContainer: document.getElementById('toast-container'),
        estimatedTimeLabel: document.getElementById('estimatedTimeLabel'),

        // Calidad
        resolutionSelect: document.getElementById('resolutionSelect')
    };

    // VARIABLE GLOBAL
    let videoDurationSeconds = 0;

    // --- FUNCIONES AUXILIARES ---
    const showToast = (message, type = 'info') => {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        let icon = type === 'error' ? '❌' : (type === 'success' ? '✅' : 'ℹ️');
        toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
        if (els.toastContainer) els.toastContainer.appendChild(toast);
        setTimeout(() => toast.remove(), 4500);
    };

    const markInputError = (inputElement) => {
        if(inputElement && inputElement.parentElement) {
            const wrapper = inputElement.parentElement;
            wrapper.classList.add('input-error');
            setTimeout(() => wrapper.classList.remove('input-error'), 500);
        }
    };

    const updateEstimatedTime = () => {
        if (videoDurationSeconds <= 0) return;

        const qualityFactors = {
            "1080": 0.6,
            "720": 0.4,
            "480": 0.25
        };

        const currentRes = els.resolutionSelect ? els.resolutionSelect.value : "1080";
        const factor = qualityFactors[currentRes] || 0.6;
        
        let estimatedSeconds = videoDurationSeconds * factor;
        
        let timeString = "";
        if (estimatedSeconds < 60) {
            timeString = `~${Math.ceil(estimatedSeconds)} seg`;
        } else {
            let mins = Math.ceil(estimatedSeconds / 60);
            timeString = `~${mins} min`;
        }

        if(els.estimatedTimeLabel) {
            els.estimatedTimeLabel.innerText = `⏱️ Tiempo estimado (${currentRes}p): ${timeString}`;
            els.estimatedTimeLabel.classList.remove('hidden');
        }
    };

    // --- 2. EVENTOS DE ESTILO (Colores y Textos) ---
    const root = document.documentElement;
    const updateCssVar = (variable, value) => root.style.setProperty(variable, value);
    updateCssVar('--strip-radius', '0px');

    if(els.mainBg) els.mainBg.addEventListener('input', (e) => updateCssVar('--sb-bg-main', e.target.value));
    if(els.infoBg) els.infoBg.addEventListener('input', (e) => updateCssVar('--sb-bg-info', e.target.value));
    if(els.textColor) els.textColor.addEventListener('input', (e) => updateCssVar('--sb-text', e.target.value));
    if(els.cfgLocStrip1) els.cfgLocStrip1.addEventListener('input', (e) => updateCssVar('--loc-s1', e.target.value));
    if(els.cfgLocStrip2) els.cfgLocStrip2.addEventListener('input', (e) => updateCssVar('--loc-s2', e.target.value));
    if(els.cfgVisStrip1) els.cfgVisStrip1.addEventListener('input', (e) => updateCssVar('--vis-s1', e.target.value));
    if(els.cfgVisStrip2) els.cfgVisStrip2.addEventListener('input', (e) => updateCssVar('--vis-s2', e.target.value));

    if(els.localNameInput) els.localNameInput.addEventListener('input', (e) => els.localName.innerText = e.target.value || "LOCAL");
    if(els.visitNameInput) els.visitNameInput.addEventListener('input', (e) => els.visitName.innerText = e.target.value || "VISIT");
    
    // --- 3. TOGGLE LIGA Y ESTILOS ESCUDO ---
    const updateBadgeStyle = (select, container) => {
        if (!select || !container) return;
        select.value === 'split' ? container.classList.add('style-split') : container.classList.remove('style-split');
    };
    if(els.styleLocalSelect) els.styleLocalSelect.addEventListener('change', () => updateBadgeStyle(els.styleLocalSelect, els.stripsLocal));
    if(els.styleVisitSelect) els.styleVisitSelect.addEventListener('change', () => updateBadgeStyle(els.styleVisitSelect, els.stripsVisit));

    function toggleLigaBox() {
        if (!els.chkShowLiga || !els.scoreboardOverlay) return;
        els.chkShowLiga.checked ? els.scoreboardOverlay.classList.remove('no-liga') : els.scoreboardOverlay.classList.add('no-liga');
    }
    if(els.chkShowLiga) els.chkShowLiga.addEventListener('change', toggleLigaBox);
    toggleLigaBox(); 

    // --- 4. GESTIÓN DE IMÁGENES ---
    const setupImageControl = (input, btnDelete, label, imgPreview, stripElement, defaultLabel, placeholderElement) => {
        if(!input) return;
        input.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                label.innerText = "✅ " + file.name.substring(0, 8) + "...";
                btnDelete.classList.add('visible');
                const reader = new FileReader();
                reader.onload = function(e) {
                    imgPreview.src = e.target.result;
                    imgPreview.classList.remove('hidden');
                    if(stripElement) stripElement.classList.add('hidden');
                    if(placeholderElement) placeholderElement.classList.add('hidden');
                }
                reader.readAsDataURL(file);
                showToast("Imagen cargada correctamente", "success");
            }
        });
        btnDelete.addEventListener('click', function() {
            input.value = "";
            label.innerText = defaultLabel;
            btnDelete.classList.remove('visible');
            imgPreview.src = "";
            imgPreview.classList.add('hidden');
            if(stripElement) stripElement.classList.remove('hidden');
            if(placeholderElement) placeholderElement.classList.remove('hidden');
        });
    };
    setupImageControl(els.imgLocalInput, els.btnDelLocal, els.labelImgLocal, els.previewLogoLocal, els.stripsLocal, "🛡️ Subir", null);
    setupImageControl(els.imgVisitInput, els.btnDelVisit, els.labelImgVisit, els.previewLogoVisit, els.stripsVisit, "🛡️ Subir", null);
    setupImageControl(els.imgLigaInput, els.btnDelLiga, els.labelImgLiga, els.previewLogoLiga, null, "🖼️ Imagen", els.ligaPlaceholder);


    // =========================================================
    // --- 5. LÓGICA DEL MODAL (ESTO ERA LO QUE FALTABA) ---
    // =========================================================
    const openModal = () => els.modal.classList.remove('hidden');
    const closeModal = () => els.modal.classList.add('hidden');

    if (els.btnOpenConfig) els.btnOpenConfig.addEventListener('click', openModal);
    if (els.btnCloseConfig) els.btnCloseConfig.addEventListener('click', closeModal);
    if (els.btnApplyConfig) els.btnApplyConfig.addEventListener('click', closeModal);
    if (els.modal) els.modal.addEventListener('click', (e) => {
        if (e.target === els.modal) closeModal();
    });
    // =========================================================


    // --- 6. CAMBIO DE RESOLUCIÓN ---
    if(els.resolutionSelect) {
        els.resolutionSelect.addEventListener('change', updateEstimatedTime);
    }

    // --- 7. CARGA DE VIDEO ---
    if(els.videoInput) {
        els.videoInput.addEventListener('change', function(){
            const file = this.files[0];
            if(file) {
                document.getElementById('videoStatusLabel').innerText = "✅ " + file.name;
                const fileUrl = URL.createObjectURL(file);
                els.videoPlayer.src = fileUrl;
                
                els.videoPlayer.onloadedmetadata = function() {
                    videoDurationSeconds = els.videoPlayer.duration;
                    showToast("Video cargado. Duración detectada.", "success");
                    updateEstimatedTime();
                };
                els.videoPlayer.load();
                if(this.parentElement) this.parentElement.classList.remove('input-error');
            }
        });
    }

    // --- 8. CARGA DE TXT ---
    if(els.eventsInput) {
        els.eventsInput.addEventListener('change', function(){
            const file = this.files[0];
            if(file) {
                document.getElementById('eventStatusLabel').innerText = "✅ " + file.name;
                showToast("Datos del partido cargados", "success");
                if(this.parentElement) this.parentElement.classList.remove('input-error');
            }
        });
    }

    // --- 9. RENDERIZADO ---
    if(els.btnRender) {
        els.btnRender.addEventListener('click', () => { 
            let hasError = false;

            if (!els.videoInput.files[0]) { 
                showToast("Falta subir el VIDEO (MP4)", "error");
                markInputError(els.videoInput);
                hasError = true; 
            }
            if (!els.eventsInput.files[0]) { 
                showToast("Falta subir los DATOS (TXT)", "error");
                markInputError(els.eventsInput);
                hasError = true; 
            }
            if (hasError) return;

            // Preparar UI
            const originalText = els.btnRender.innerText;
            els.btnRender.innerText = "⏳ Procesando...";
            els.btnRender.disabled = true;
            els.btnRender.style.cursor = "wait";
            els.btnRender.style.opacity = "0.7";

            els.progressContainer.classList.remove('hidden');
            els.progressBar.style.width = "0%";
            els.progressBar.classList.remove('processing');
            els.progressText.innerText = "0%";
            els.progressStatus.innerText = "Subiendo...";

            // Preparar Datos
            const formData = new FormData();
            formData.append('video', els.videoInput.files[0]);
            formData.append('events', els.eventsInput.files[0]);
            if (els.imgLocalInput.files[0]) formData.append('logo_local', els.imgLocalInput.files[0]);
            if (els.imgVisitInput.files[0]) formData.append('logo_visit', els.imgVisitInput.files[0]);
            if (els.imgLigaInput.files[0])  formData.append('logo_liga', els.imgLigaInput.files[0]);
            formData.append('main_bg', els.mainBg.value);
            formData.append('info_bg', els.infoBg.value);
            formData.append('text_color', els.textColor.value);
            formData.append('local_name', els.localNameInput.value || "LOCAL");
            formData.append('visit_name', els.visitNameInput.value || "VISIT");
            formData.append('loc_s1', els.cfgLocStrip1.value);
            formData.append('loc_s2', els.cfgLocStrip2.value);
            formData.append('vis_s1', els.cfgVisStrip1.value);
            formData.append('vis_s2', els.cfgVisStrip2.value);
            if(els.styleLocalSelect) formData.append('style_local', els.styleLocalSelect.value);
            if(els.styleVisitSelect) formData.append('style_visit', els.styleVisitSelect.value);
            if(els.chkShowLiga) formData.append('show_liga', els.chkShowLiga.checked);
            
            // Calidad
            formData.append('output_quality', els.resolutionSelect.value);

            // Enviar AJAX
            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/render', true);
            xhr.responseType = 'blob'; 

            xhr.upload.onprogress = function(e) {
                if (e.lengthComputable) {
                    const percentComplete = Math.round((e.loaded / e.total) * 100);
                    if (percentComplete < 100) {
                        els.progressBar.style.width = percentComplete + "%";
                        els.progressText.innerText = percentComplete + "%";
                        els.progressStatus.innerText = "Subiendo archivos...";
                    } else {
                        els.progressStatus.innerText = "🎥 Renderizando... No cierres la ventana.";
                        els.progressText.innerText = "";
                        requestAnimationFrame(() => {
                            els.progressBar.classList.add('processing');
                        });
                    }
                }
            };

            xhr.onload = function() {
                if (xhr.status === 200) {
                    const blob = xhr.response;
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `partido_marcador_${els.resolutionSelect.value}p.mp4`; 
                    document.body.appendChild(a);
                    a.click();
                    a.remove();
                    window.URL.revokeObjectURL(url);
                    
                    els.progressStatus.innerText = "✅ ¡Listo!";
                    els.progressBar.classList.remove('processing');
                    els.progressBar.style.width = "100%";
                    showToast("Renderizado completado con éxito", "success");
                } else {
                    showToast(`Error del servidor (${xhr.status})`, "error");
                    els.progressStatus.innerText = "Falló.";
                    els.progressBar.style.backgroundColor = "#ff4444";
                }
                resetButton();
            };

            xhr.onerror = function() {
                showToast("Error de conexión", "error");
                resetButton();
            };

            xhr.send(formData);

            function resetButton() {
                els.btnRender.innerText = originalText;
                els.btnRender.disabled = false;
                els.btnRender.style.cursor = "pointer";
                els.btnRender.style.opacity = "1";
            }
        });
    }
});