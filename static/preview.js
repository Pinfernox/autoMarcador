console.log("✅ preview.js cargado (Versión Estética)");

document.addEventListener('DOMContentLoaded', () => {
    
    // --- 1. REFERENCIAS DOM ---
    const els = {
        // ... (Tus referencias anteriores se mantienen igual) ...
        scoreboardOverlay: document.getElementById('scoreboardOverlay'),
        videoPlayer: document.getElementById('video'),
        chkShowLiga: document.getElementById('chkShowLiga'),
        localName: document.getElementById('local'),
        visitName: document.getElementById('visitor'),
        localNameInput: document.getElementById('inputLocalName'),
        visitNameInput: document.getElementById('inputVisitName'),
        mainBg: document.getElementById('cfgMainBg'),
        infoBg: document.getElementById('cfgInfoBg'),
        textColor: document.getElementById('cfgTextColor'),
        cfgLocStrip1: document.getElementById('cfgLocStrip1'),
        cfgLocStrip2: document.getElementById('cfgLocStrip2'),
        cfgVisStrip1: document.getElementById('cfgVisStrip1'),
        cfgVisStrip2: document.getElementById('cfgVisStrip2'),
        styleLocalSelect: document.getElementById('styleLocal'),
        styleVisitSelect: document.getElementById('styleVisit'),
        stripsLocal: document.getElementById('stripsLocal'),
        stripsVisit: document.getElementById('stripsVisit'),
        videoInput: document.getElementById('videoInput'),
        eventsInput: document.getElementById('eventsInput'),
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
        btnRender: document.getElementById('btnRender'),
        btnOpenConfig: document.getElementById('btnOpenConfig'),
        btnCloseConfig: document.getElementById('btnCloseConfig'),
        btnApplyConfig: document.getElementById('btnApplyConfig'),
        modal: document.getElementById('configModal'),
        progressContainer: document.getElementById('progressContainer'),
        progressBar: document.getElementById('progressBar'),
        progressText: document.getElementById('progressText'),
        progressStatus: document.getElementById('progressStatus'),
        
        // NUEVAS REFERENCIAS
        toastContainer: document.getElementById('toast-container'),
        estimatedTimeLabel: document.getElementById('estimatedTimeLabel')
    };

    // VARIABLE GLOBAL PARA DURACIÓN DEL VIDEO
    let videoDurationSeconds = 0;

    // --- FUNCIONES AUXILIARES DE UI ---
    
    // 1. Mostrar Notificación (Toast)
    const showToast = (message, type = 'info') => {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        // Icono según tipo
        let icon = 'ℹ️';
        if (type === 'error') icon = '❌';
        if (type === 'success') icon = '✅';

        toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
        
        els.toastContainer.appendChild(toast);

        // Auto eliminar del DOM después de la animación (4.5s)
        setTimeout(() => {
            toast.remove();
        }, 4500);
    };

    // 2. Marcar input con error
    const markInputError = (elementWrapperId) => {
        const el = document.getElementById(elementWrapperId); // Usamos el ID del label contenedor
        if(el) {
            el.classList.add('input-error');
            setTimeout(() => el.classList.remove('input-error'), 500);
        }
    };

    // --- 2. LÓGICA DE COLORES ---
    const root = document.documentElement;
    const updateCssVar = (variable, value) => root.style.setProperty(variable, value);
    updateCssVar('--strip-radius', '0px'); // Forzar cuadrado

    if(els.mainBg) els.mainBg.addEventListener('input', (e) => updateCssVar('--sb-bg-main', e.target.value));
    if(els.infoBg) els.infoBg.addEventListener('input', (e) => updateCssVar('--sb-bg-info', e.target.value));
    if(els.textColor) els.textColor.addEventListener('input', (e) => updateCssVar('--sb-text', e.target.value));
    if(els.cfgLocStrip1) els.cfgLocStrip1.addEventListener('input', (e) => updateCssVar('--loc-s1', e.target.value));
    if(els.cfgLocStrip2) els.cfgLocStrip2.addEventListener('input', (e) => updateCssVar('--loc-s2', e.target.value));
    if(els.cfgVisStrip1) els.cfgVisStrip1.addEventListener('input', (e) => updateCssVar('--vis-s1', e.target.value));
    if(els.cfgVisStrip2) els.cfgVisStrip2.addEventListener('input', (e) => updateCssVar('--vis-s2', e.target.value));

    // --- 3. TEXTOS Y ESTILOS ---
    if(els.localNameInput) els.localNameInput.addEventListener('input', (e) => els.localName.innerText = e.target.value || "LOCAL");
    if(els.visitNameInput) els.visitNameInput.addEventListener('input', (e) => els.visitName.innerText = e.target.value || "VISIT");

    const updateBadgeStyle = (select, container) => {
        if (!select || !container) return;
        select.value === 'split' ? container.classList.add('style-split') : container.classList.remove('style-split');
    };
    if(els.styleLocalSelect) els.styleLocalSelect.addEventListener('change', () => updateBadgeStyle(els.styleLocalSelect, els.stripsLocal));
    if(els.styleVisitSelect) els.styleVisitSelect.addEventListener('change', () => updateBadgeStyle(els.styleVisitSelect, els.stripsVisit));

    // --- 4. TOGGLE LIGA ---
    function toggleLigaBox() {
        if (!els.chkShowLiga || !els.scoreboardOverlay) return;
        els.chkShowLiga.checked ? els.scoreboardOverlay.classList.remove('no-liga') : els.scoreboardOverlay.classList.add('no-liga');
    }
    if(els.chkShowLiga) els.chkShowLiga.addEventListener('change', toggleLigaBox);
    toggleLigaBox(); 

    // --- 5. IMÁGENES ---
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

    // --- 6. MODAL ---
    const openModal = () => els.modal.classList.remove('hidden');
    const closeModal = () => els.modal.classList.add('hidden');
    if(els.btnOpenConfig) els.btnOpenConfig.addEventListener('click', openModal);
    if(els.btnCloseConfig) els.btnCloseConfig.addEventListener('click', closeModal);
    if(els.btnApplyConfig) els.btnApplyConfig.addEventListener('click', closeModal); 
    if(els.modal) els.modal.addEventListener('click', (e) => { if (e.target === els.modal) closeModal(); });

    // --- 7. CARGA DE VIDEO Y STATUS ---
    if(els.videoInput) {
        els.videoInput.addEventListener('change', function(){
            const file = this.files[0];
            if(file) {
                document.getElementById('videoStatusLabel').innerText = "✅ " + file.name;
                const fileUrl = URL.createObjectURL(file);
                els.videoPlayer.src = fileUrl;
                
                // Cuando el video carga los metadatos, obtenemos la duración
                els.videoPlayer.onloadedmetadata = function() {
                    videoDurationSeconds = els.videoPlayer.duration;
                    console.log("Duración del video detectada:", videoDurationSeconds);
                    showToast("Video cargado.", "success");
                };
                
                els.videoPlayer.load();
            }
        });
    }
    if(els.eventsInput) {
        els.eventsInput.addEventListener('change', function(){
            if(this.files[0]) {
                document.getElementById('eventStatusLabel').innerText = "✅ " + this.files[0].name;
                showToast("Archivo de eventos cargado", "success");
            }
        });
    }

    // --- 8. RENDERIZADO CON PROGRESO Y ESTIMACIÓN ---
    if(els.btnRender) {
        els.btnRender.addEventListener('click', () => { 
            
            // A. VALIDACIÓN ESTÉTICA
            let hasError = false;
            
            if (!els.videoInput.files[0]) { 
                showToast("Falta el archivo de VIDEO", "error");
                // Buscamos el label padre para agitarlo
                els.videoInput.parentElement.classList.add('input-error');
                setTimeout(()=> els.videoInput.parentElement.classList.remove('input-error'), 500);
                hasError = true;
            }
            
            if (!els.eventsInput.files[0]) { 
                showToast("Falta el archivo de DATOS (TXT)", "error");
                els.eventsInput.parentElement.classList.add('input-error');
                setTimeout(()=> els.eventsInput.parentElement.classList.remove('input-error'), 500);
                hasError = true;
            }

            if(hasError) return;

            // B. CÁLCULO DE ESTIMACIÓN DE TIEMPO
            let estimatedSeconds = videoDurationSeconds * 0.3;
            
            // Mínimo 10 segundos, Máximo mostrar minutos
            let timeString = "";
            if (estimatedSeconds < 60) {
                timeString = `${Math.ceil(estimatedSeconds)} segundos`;
            } else {
                let mins = Math.ceil(estimatedSeconds / 60);
                timeString = `${mins} minuto${mins > 1 ? 's' : ''}`;
            }

            // Actualizar UI
            els.estimatedTimeLabel.innerText = `⏱️ Tiempo estimado: ~${timeString}`;
            els.estimatedTimeLabel.classList.remove('hidden');


            // C. PREPARAR UI
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

            // D. PREPARAR DATOS
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

            // E. INICIAR PETICIÓN AJAX (XHR)
            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/render', true);
            xhr.responseType = 'blob'; 

            xhr.upload.onprogress = function(e) {
                if (e.lengthComputable) {
                    const percentComplete = Math.round((e.loaded / e.total) * 100);
                    if (percentComplete < 100) {
                        els.progressBar.style.width = percentComplete + "%";
                        els.progressText.innerText = percentComplete + "%";
                        els.progressStatus.innerText = "Subiendo...";
                    } else {
                        els.progressStatus.innerText = "🎥 Renderizando...";
                        els.progressText.innerText = "Procesando";
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
                    a.download = "resumen_partido.mp4";
                    document.body.appendChild(a);
                    a.click();
                    a.remove();
                    window.URL.revokeObjectURL(url);
                    
                    els.progressStatus.innerText = "✅ ¡Listo!";
                    showToast("Renderizado completado con éxito", "success");
                    
                    els.progressBar.classList.remove('processing');
                    els.progressBar.style.width = "100%";
                } else {
                    showToast(`Error del servidor (${xhr.status})`, "error");
                    els.progressStatus.innerText = "Falló.";
                    els.progressBar.style.backgroundColor = "#ff4444";
                }
                resetButton();
            };

            xhr.onerror = function() {
                showToast("Error de conexión con el servidor", "error");
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