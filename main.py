from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Form, Response
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import shutil
import os
import uuid
import asyncio
from typing import List

# Importamos la función de renderizado
from render_job import render

app = FastAPI()

# Carpetas temporales
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------------------------------------------------
# 1. SOPORTE PARA UPTIMEROBOT (Evita que se duerma)
# ---------------------------------------------------------
@app.head("/")
async def keep_alive():
    return Response(status_code=200)

# ---------------------------------------------------------
# 2. RUTAS ESTÁTICAS Y FRONTEND
# ---------------------------------------------------------
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

# ---------------------------------------------------------
# 3. PARSEO DE EVENTOS TXT
# ---------------------------------------------------------
def parse_events(file_content: str):
    events = []
    lines = file_content.split('\n')
    
    local_score = 0
    visit_score = 0
    
    for line in lines:
        line = line.strip()
        if not line: continue
        
        parts = line.split(' ')
        if len(parts) < 2: continue
        
        time_str = parts[0]
        desc = line[len(time_str):].strip().lower()
        
        # Parsear tiempo MM:SS
        try:
            mm, ss = map(int, time_str.split(':'))
            seconds = mm * 60 + ss
        except:
            continue
            
        # Detección de Goles
        if "gol" in desc:
            if "(v)" in desc or "visitante" in desc:
                visit_score += 1
            else:
                local_score += 1
                
            events.append({
                "time": seconds,
                "local": local_score,
                "visitor": visit_score,
                "desc": desc
            })
            
    return events

# ---------------------------------------------------------
# 4. LIMPIEZA DE ARCHIVOS (Background Task)
# ---------------------------------------------------------
def cleanup_files(file_paths: List[str]):
    for path in file_paths:
        try:
            if os.path.exists(path):
                os.remove(path)
                print(f"🗑️ Archivo temporal eliminado: {path}")
        except Exception as e:
            print(f"⚠️ Error eliminando {path}: {e}")

# ---------------------------------------------------------
# 5. ENDPOINT DE RENDERIZADO
# ---------------------------------------------------------
@app.post("/render")
async def render_video(
    background_tasks: BackgroundTasks,
    video: UploadFile = File(...),
    events: UploadFile = File(...),
    # Recibimos los datos del formulario
    main_bg: str = Form(...),
    info_bg: str = Form(...),
    text_color: str = Form(...),
    local_name: str = Form(...),
    loc_s1: str = Form(...),
    loc_s2: str = Form(...),
    visit_name: str = Form(...),
    vis_s1: str = Form(...),
    vis_s2: str = Form(...)
):
    # Generar ID único para este trabajo
    job_id = str(uuid.uuid4())
    
    # Rutas de archivos temporales
    temp_video_path = os.path.join(UPLOAD_DIR, f"{job_id}_input.mp4")
    output_path = os.path.join(OUTPUT_DIR, f"Resumen_{job_id}.mp4")

    try:
        # 1. Guardar Video
        with open(temp_video_path, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)
            
        # 2. Leer y Parsear Eventos
        events_content = (await events.read()).decode("utf-8")
        match_events = parse_events(events_content)

        # 3. PREPARAR CONFIGURACIÓN (Aquí estaba el error antes)
        # Empaquetamos todo en un diccionario
        config = {
            "main_bg": main_bg,
            "info_bg": info_bg,
            "text_color": text_color,
            "local_name": local_name,
            "loc_s1": loc_s1,
            "loc_s2": loc_s2,
            "visit_name": visit_name,
            "vis_s1": vis_s1,
            "vis_s2": vis_s2
        }

        # 4. LLAMAR AL RENDER (Ahora pasamos 4 argumentos, como pide render_job.py)
        print("⏳ Renderizando en carpeta temporal...")
        
        # Ejecutar en un hilo aparte para no bloquear el servidor
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, render, temp_video_path, match_events, config, output_path)
        
        # 5. Programar limpieza y devolver archivo
        background_tasks.add_task(cleanup_files, [temp_video_path, output_path])
        
        return FileResponse(
            output_path, 
            media_type="video/mp4", 
            filename=f"Resumen_{local_name}_vs_{visit_name}.mp4"
        )

    except Exception as e:
        # Limpieza de emergencia si falla
        cleanup_files([temp_video_path])
        print(f"ERROR EN RENDER: {str(e)}")
        return Response(content=f"Error en el servidor: {str(e)}", status_code=500)