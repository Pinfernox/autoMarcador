from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Form, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import shutil
import os
import uuid
import asyncio
from typing import List, Optional

import render_job 

app = FastAPI()

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

# ---------------------------------------------------------
# 2. PARSEO DE EVENTOS (CON SINCRONIZACIÓN DE SEGUNDAS PARTES)
# ---------------------------------------------------------
def parse_events(file_content: str, start_minute: int = 0, initial_local: int = 0, initial_visit: int = 0):
    events = []
    lines = file_content.split('\n')
    
    local_score = initial_local
    visit_score = initial_visit
    
    # Segundos que ya han transcurrido de partido antes de que empiece el video
    offset_seconds = start_minute * 60 
    
    for line in lines:
        line = line.strip()
        if not line: continue
        
        parts = line.split(' ')
        if len(parts) < 2: continue
        
        time_str = parts[0]
        raw_desc = line[len(time_str):].strip()
        desc_lower = raw_desc.lower()
        
        try:
            mm, ss = map(int, time_str.split(':'))
            
            # Calculamos el segundo ABSOLUTO del partido
            absolute_seconds = mm * 60 + ss
            
            # Calculamos el segundo RELATIVO al video subido
            video_seconds = absolute_seconds - offset_seconds
            
            short_minute = f"{mm}'"
            
            # Si el evento pasó antes del video (ej: gol en min 10, pero subes la segunda parte)
            # no se dibuja animación en el video nuevo, simplemente se cuenta en el inicial_score.
            if video_seconds < 0:
                continue 
                
        except:
            continue
            
        if "gol" in desc_lower:
            is_visitor = "(v)" in desc_lower or "visitante" in desc_lower
            
            if is_visitor:
                visit_score += 1
            else:
                local_score += 1
            
            clean_name = raw_desc
            words_to_remove = ["Gol", "gol", "GOL", "(v)", "(V)", "visitante", "local", "de", "-", ":"]
            
            for w in words_to_remove:
                clean_name = clean_name.replace(f" {w} ", " ")
                clean_name = clean_name.replace(f"{w} ", " ")
                clean_name = clean_name.replace(f" {w}", " ")
                
            clean_name = clean_name.strip()
            if not clean_name: clean_name = "GOL"
            
            if len(clean_name) > 15:
                clean_name = clean_name[:15] + "..."

            events.append({
                "time": video_seconds,  # El momento exacto del archivo MP4
                "local": local_score,
                "visitor": visit_score,
                "desc": desc_lower,
                "author": clean_name,
                "time_str": short_minute # El texto que ve el usuario
            })
            
    return events

# ---------------------------------------------------------
# 3. LIMPIEZA DE ARCHIVOS
# ---------------------------------------------------------
def cleanup_files(file_paths: List[str]):
    for path in file_paths:
        try:
            if path and os.path.exists(path):
                os.remove(path)
                print(f"🗑️ Eliminado: {path}")
        except Exception as e:
            print(f"⚠️ Error eliminando {path}: {e}")

# ---------------------------------------------------------
# 4. ENDPOINT DE RENDERIZADO
# ---------------------------------------------------------
@app.post("/render")
async def render_video(
    background_tasks: BackgroundTasks,
    video: UploadFile = File(...),
    events: UploadFile = File(...),
    
    logo_local: Optional[UploadFile] = File(None),
    logo_visit: Optional[UploadFile] = File(None),
    logo_liga: Optional[UploadFile] = File(None),

    main_bg: str = Form("#1E90FF"),
    info_bg: str = Form("#FFFFFF"),
    text_color: str = Form("#000000"),
    local_name: str = Form("LOCAL"),
    visit_name: str = Form("VISIT"),
    loc_s1: str = Form("#FFFFFF"),
    loc_s2: str = Form("#000000"),
    vis_s1: str = Form("#FFFFFF"),
    vis_s2: str = Form("#000000"),
    
    style_local: str = Form("stripes"),
    style_visit: str = Form("stripes"),
    show_liga: str = Form("true"), 

    output_quality: int = Form(1080),
    
    # Parámetros del marcador inicial
    start_minute: int = Form(0),
    start_score_local: int = Form(0),
    start_score_visit: int = Form(0)
):
    job_id = str(uuid.uuid4())
    temp_files_to_delete = []

    temp_video_path = os.path.join(UPLOAD_DIR, f"{job_id}_input.mp4")
    output_path = os.path.join(OUTPUT_DIR, f"Resumen_{job_id}.mp4")
    
    temp_files_to_delete.append(temp_video_path)
    temp_files_to_delete.append(output_path)

    try:
        with open(temp_video_path, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)
            
        path_logo_local = None
        if logo_local and logo_local.filename:
            path_logo_local = os.path.join(UPLOAD_DIR, f"{job_id}_logo_loc.png")
            with open(path_logo_local, "wb") as buffer:
                shutil.copyfileobj(logo_local.file, buffer)
            temp_files_to_delete.append(path_logo_local)

        path_logo_visit = None
        if logo_visit and logo_visit.filename:
            path_logo_visit = os.path.join(UPLOAD_DIR, f"{job_id}_logo_vis.png")
            with open(path_logo_visit, "wb") as buffer:
                shutil.copyfileobj(logo_visit.file, buffer)
            temp_files_to_delete.append(path_logo_visit)

        path_logo_liga = None
        if logo_liga and logo_liga.filename:
            path_logo_liga = os.path.join(UPLOAD_DIR, f"{job_id}_logo_liga.png")
            with open(path_logo_liga, "wb") as buffer:
                shutil.copyfileobj(logo_liga.file, buffer)
            temp_files_to_delete.append(path_logo_liga)

        events_content = (await events.read()).decode("utf-8")
        
        # Le pasamos los datos iniciales al parser
        match_events = parse_events(events_content, start_minute, start_score_local, start_score_visit)

        config = {
            "main_bg": main_bg,
            "info_bg": info_bg,
            "text_color": text_color,
            "local_name": local_name,
            "visit_name": visit_name,
            "loc_s1": loc_s1,
            "loc_s2": loc_s2,
            "vis_s1": vis_s1,
            "vis_s2": vis_s2,
            "style_local": style_local,
            "style_visit": style_visit,
            "show_liga": show_liga,
            "logo_local": os.path.abspath(path_logo_local) if path_logo_local else None,
            "logo_visit": os.path.abspath(path_logo_visit) if path_logo_visit else None,
            "logo_liga": os.path.abspath(path_logo_liga) if path_logo_liga else None,
            "output_quality": output_quality,
            
            # Enviamos variables al render_job.py
            "start_minute": start_minute,
            "start_score_local": start_score_local,
            "start_score_visit": start_score_visit
        }

        print(f"🎬 Iniciando Job {job_id} a {output_quality}p | Empieza: {start_minute}' ({start_score_local}-{start_score_visit})")
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, render_job.render, temp_video_path, match_events, config, output_path)
        
        background_tasks.add_task(cleanup_files, temp_files_to_delete)
        
        return FileResponse(
            output_path, 
            media_type="video/mp4", 
            filename=f"Resumen_{local_name}_vs_{visit_name}_{output_quality}p.mp4"
        )

    except Exception as e:
        cleanup_files(temp_files_to_delete) 
        print(f"❌ ERROR SERVER: {str(e)}")
        return Response(content=f"Error: {str(e)}", status_code=500)