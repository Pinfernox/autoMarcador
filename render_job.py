import ffmpeg
import os
import subprocess

# --- FUNCIÓN AUXILIAR PARA LEER EL TXT ---
def parse_txt_events(txt_path):
    events = []
    local_score = 0
    visitor_score = 0

    try:
        with open(txt_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line: continue

                # 1. Separar Tiempo y Descripción
                try:
                    if " " in line:
                        time_str, desc = line.split(" ", 1)
                    else:
                        continue 
                    
                    min_, sec = map(int, time_str.split(":"))
                    t = min_ * 60 + sec
                except ValueError:
                    continue

                # 2. Analizar Goles
                desc_lower = desc.lower()
                if desc_lower.startswith("gol"):
                    # Lógica de detección (L) / (V)
                    if "(v)" in desc_lower or "visitante" in desc_lower:
                        visitor_score += 1
                    elif "(l)" in desc_lower or "local" in desc_lower:
                        local_score += 1
                    else:
                        # Si no especifica, asumimos Local
                        local_score += 1
                    
                    # Añadimos el evento CON EL MARCADOR YA CALCULADO
                    events.append({
                        "time": t,
                        "local": local_score,
                        "visitor": visitor_score
                    })
    except Exception as e:
        print(f"Error parseando TXT: {e}")
        
    return events

# --- FUNCIÓN PRINCIPAL DE RENDER ---
def render(video_path, txt_path, output_path, l_name, v_name, l_color, v_color):
    print(f"--> Iniciando Render TXT: {video_path}")

    # 1. CONFIGURACIÓN VISUAL (IGUAL AL CSS)
    C_WHITE = "white"
    C_BLUE  = "dodgerblue"
    C_TEXT  = "black"
    C_BLUE_LOCAL = l_color  
    C_BLUE_VISIT = v_color
    
    Y_POS = 20
    X_START = 20
    H_BAR = 30
    
    W_LIGA  = 35
    W_TIME  = 60
    W_TEAM  = 100
    W_SCORE = 60
    LOGO_H  = 20
    FONT    = "Inter.ttf" 

    # 2. OBTENER EVENTOS DEL TXT
    events = parse_txt_events(txt_path)
    
    # Duración por defecto (si no podemos saberla, ponemos 1 hora)
    # Nota: FFmpeg cortará cuando acabe el video input
    duration = 3600 

    # 3. LAYOUT (COORDENADAS)
    x_liga  = X_START
    x_time  = x_liga + W_LIGA
    x_loc   = x_time + W_TIME
    x_score = x_loc  + W_TEAM
    x_vis   = x_score + W_SCORE
    y_logo  = Y_POS + (H_BAR - LOGO_H) / 2

    # 4. CONSTRUCCIÓN FFMPEG
    filters = []
    
    # Rutas de assets
    IMG_LIGA  = "static/assets/logo_liga.jpg"
    IMG_LOCAL = "static/assets/logo_local.png"
    IMG_VISIT = "static/assets/logo_visitante.png"

    inputs = ["-i", video_path]
    idx = 1
    
    # Cargar imágenes si existen
    for img in [IMG_LIGA, IMG_LOCAL, IMG_VISIT]:
        if os.path.exists(img):
            inputs.extend(["-i", img])
            filters.append(f"[{idx}:v]scale=-1:{LOGO_H}[img_{idx}]")
            idx += 1

    # Cajas de fondo
    boxes = [
        f"drawbox=x={x_liga}:y={Y_POS}:w={W_LIGA}:h={H_BAR}:color={C_WHITE}:t=fill",
        f"drawbox=x={x_time}:y={Y_POS}:w={W_TIME}:h={H_BAR}:color={C_WHITE}:t=fill",
        f"drawbox=x={x_loc}:y={Y_POS}:w={W_TEAM}:h={H_BAR}:color={C_BLUE}:t=fill",
        f"drawbox=x={x_score}:y={Y_POS}:w={W_SCORE}:h={H_BAR}:color={C_WHITE}:t=fill",
        f"drawbox=x={x_vis}:y={Y_POS}:w={W_TEAM}:h={H_BAR}:color={C_BLUE}:t=fill"
    ]
    filters.append(f"[0:v]{','.join(boxes)}[bg]")
    last_stream = "[bg]"

    # Overlays de logos
    if os.path.exists(IMG_LIGA):
        filters.append(f"{last_stream}[img_1]overlay=x={x_liga}+({W_LIGA}-w)/2:y={y_logo}[v_l]")
        last_stream = "[v_l]"
    if os.path.exists(IMG_LOCAL):
        filters.append(f"{last_stream}[img_2]overlay=x={x_loc}+5:y={y_logo}[v_loc]")
        last_stream = "[v_loc]"
    if os.path.exists(IMG_VISIT):
        filters.append(f"{last_stream}[img_3]overlay=x={x_vis}+{W_TEAM}-w-5:y={y_logo}[v_vis]")
        last_stream = "[v_vis]"

    # Textos Fijos
    timer_expr = r"%{eif\:t/60\:d\:2}\:%{eif\:mod(t,60)\:d\:2}"
    text_cmds = [
        f"drawtext=fontfile='{FONT}':text='{timer_expr}':x={x_time}+({W_TIME}-text_w)/2:y={Y_POS}+6:fontsize=16:fontcolor={C_TEXT}",
        f"drawtext=fontfile='{FONT}':text='LOCAL':x={x_loc}+25+({W_TEAM}-25-text_w)/2:y={Y_POS}+6:fontsize=16:fontcolor={C_TEXT}",
        f"drawtext=fontfile='{FONT}':text='VISIT':x={x_vis}+({W_TEAM}-25-text_w)/2:y={Y_POS}+6:fontsize=16:fontcolor={C_TEXT}"
    ]

    # Marcador Dinámico (Basado en el TXT parseado)
    last_t = 0
    curr_score = "0 - 0"
    events.sort(key=lambda x: x['time'])

    for e in events:
        t_end = e["time"]
        text_cmds.append(
            f"drawtext=fontfile='{FONT}':text='{curr_score}':"
            f"x={x_score}+({W_SCORE}-text_w)/2:y={Y_POS}+4:fontsize=20:fontcolor={C_TEXT}:"
            f"enable='between(t,{last_t},{t_end})'"
        )
        curr_score = f"{e['local']} - {e['visitor']}"
        last_t = t_end

    # Tramo final
    text_cmds.append(
        f"drawtext=fontfile='{FONT}':text='{curr_score}':"
        f"x={x_score}+({W_SCORE}-text_w)/2:y={Y_POS}+4:fontsize=20:fontcolor={C_TEXT}:"
        f"enable='between(t,{last_t},{duration})'"
    )

    filters.append(f"{last_stream}{','.join(text_cmds)}")
    
    # Ejecutar
    cmd = ["ffmpeg", "-y"]
    cmd.extend(inputs)
    cmd.extend(["-filter_complex", ";".join(filters)])
    cmd.extend(["-c:v", "libx264",
                "-preset", "veryfast",
                "-crf", "18",
                "-pix_fmt", "yuv420p",
                "-c:a", "copy",
                output_path])

    print("Ejecutando FFmpeg...")
    subprocess.run(cmd, check=True)
    print(f"Render completado: {output_path}")