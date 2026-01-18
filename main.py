from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Form, Response
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import shutil
import uuid
import tempfile
from render_job import render

app = FastAPI()

# --- 1. FUNCIÓN DE LIMPIEZA ---
def cleanup_files(file_paths):
    for path in file_paths:
        try:
            if os.path.exists(path):
                os.remove(path)
                print(f"🗑️ Archivo temporal eliminado: {path}")
        except Exception as e:
            print(f"Error borrando {path}: {e}")

# --- 2. RUTAS DE LA API (IMPORTANTE: VAN PRIMERO) ---
@app.post("/render")
async def render_video(
    background_tasks: BackgroundTasks,
    video: UploadFile = File(...), 
    events: UploadFile = File(...),
    team_local_name: str = Form("LOCAL"),
    team_visit_name: str = Form("VISIT"),
    team_local_color: str = Form("0x1E90FF"),
    team_visit_color: str = Form("0x1E90FF")
):
    unique_id = str(uuid.uuid4())
    temp_dir = tempfile.gettempdir()
    
    # Rutas temporales
    temp_video = os.path.join(temp_dir, f"{unique_id}_input.mp4")
    temp_txt = os.path.join(temp_dir, f"{unique_id}_events.txt")
    temp_output = os.path.join(temp_dir, f"PARTIDO_{unique_id}.mp4")

    try:
        # Guardar archivos
        with open(temp_video, "wb") as f:
            shutil.copyfileobj(video.file, f)
            
        with open(temp_txt, "wb") as f:
            shutil.copyfileobj(events.file, f)

        # Renderizar
        print("⏳ Renderizando en carpeta temporal...")
        render(temp_video, temp_txt, temp_output, 
           team_local_name, team_visit_name, 
           team_local_color, team_visit_color)

        # Programar borrado
        background_tasks.add_task(cleanup_files, [temp_video, temp_txt, temp_output])

        # Enviar descarga
        return FileResponse(
            path=temp_output, 
            filename="Resumen_Partido.mp4",
            media_type="video/mp4"
        )

    except Exception as e:
        print(f"ERROR EN RENDER: {e}")
        cleanup_files([temp_video, temp_txt])
        # Devolvemos un error 500 para que el JS sepa que falló
        return {"error": str(e)}


@app.head("/")
async def keep_alive():
    # Respondemos con un simple "OK" (200) sin contenido
    return Response(status_code=200)

# --- 3. SERVIR FRONTEND (IMPORTANTE: VA AL FINAL) ---
# Esto captura "todo lo demás" que no sea /render
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def read_root():
    # Asegúrate de que index.html está en backend/static/index.html
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())