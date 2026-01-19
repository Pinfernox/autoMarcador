import ffmpeg
import os
import sys

def render(video_path, events, config, output_path):
    # 1. EXTRACCIÓN DE CONFIGURACIÓN
    main_bg = config.get("main_bg", "0x1E90FF")
    info_bg = config.get("info_bg", "0xFFFFFF")
    text_color = config.get("text_color", "0x000000")
    local_name = config.get("local_name", "LOCAL")
    loc_s1 = config.get("loc_s1", "0xFFFFFF")
    loc_s2 = config.get("loc_s2", "0x000000")
    visit_name = config.get("visit_name", "VISIT")
    vis_s1 = config.get("vis_s1", "0xFFFFFF")
    vis_s2 = config.get("vis_s2", "0x000000")

    # 2. CONFIGURACIÓN DE FUENTES
    if os.path.exists("Inter-ExtraBold.ttf"):
        font_bold = "Inter-ExtraBold.ttf"
    elif os.path.exists("Inter-Bold.ttf"):
        font_bold = "Inter-Bold.ttf"
    elif os.path.exists("Inter.ttf"):
        font_bold = "Inter.ttf"
    elif os.path.exists("arial.ttf"):
        font_bold = "arial.ttf"
    else:
        font_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

    # 3. DETECCIÓN INTELIGENTE DE ROTACIÓN
    # Esto asegura que en Local y en Web se vea igual de tamaño
    width_final = 1280 
    try:
        probe = ffmpeg.probe(video_path)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        
        width_raw = int(video_stream['width'])
        height_raw = int(video_stream['height'])
        
        tags = video_stream.get('tags', {})
        rotate = tags.get('rotate', '0')
        
        # Si está rotado 90 grados, usamos la altura como ancho
        if str(rotate) in ['90', '-90', '270', '-270']:
            width_final = height_raw 
            print(f"🔄 Rotación detectada. Ajustando ancho a: {width_final}")
        else:
            width_final = width_raw
            
    except Exception as e:
        print(f"⚠️ No se pudo detectar rotación: {e}")
        width_final = 1280 

    # -------------------------------------------------------------------------
    # 4. TAMAÑO DEL MARCADOR (ZOOM)
    # -------------------------------------------------------------------------
    # ANTES: 780.0
    # AHORA: 680.0 (Al bajar el número, el marcador se hace MÁS GRANDE)
    BASE_REF = 680.0 
    
    S = width_final / BASE_REF 
    
    fs_main = int(14 * S)
    H_BAR = 28 * S
    Y_POS = 25 * S
    X_START = 25 * S 
    W_TIME  = 60 * S
    W_TEAM  = 100 * S
    W_SCORE = 60 * S

    x_time  = X_START
    x_loc   = x_time + W_TIME
    x_score = x_loc  + W_TEAM
    x_vis   = x_score + W_SCORE

    strip_w = 6 * S
    strip_h = 16 * S
    strip_y = Y_POS + (H_BAR - strip_h) / 2
    x_strip_loc = x_loc + (10 * S)
    x_strip_vis = x_vis + W_TEAM - (10 * S) - (strip_w * 2) - 2 

    # 5. CONSTRUCCIÓN FFMPEG
    overlay_args = []

    # SOMBRA UNIFICADA
    shadow_offset = 4 * S
    shadow_y = Y_POS + shadow_offset
    total_width = W_TIME + W_TEAM + W_SCORE + W_TEAM
    overlay_args.append(f"drawbox=x={x_time+shadow_offset}:y={shadow_y}:w={total_width}:h={H_BAR}:color=black@0.4:t=fill")

    # CAJAS
    overlay_args.append(f"drawbox=x={x_time}:y={Y_POS}:w={W_TIME}:h={H_BAR}:color={info_bg}@1:t=fill")
    overlay_args.append(f"drawbox=x={x_loc}:y={Y_POS}:w={W_TEAM}:h={H_BAR}:color={main_bg}@1:t=fill")
    overlay_args.append(f"drawbox=x={x_score}:y={Y_POS}:w={W_SCORE}:h={H_BAR}:color={info_bg}@1:t=fill")
    overlay_args.append(f"drawbox=x={x_vis}:y={Y_POS}:w={W_TEAM}:h={H_BAR}:color={main_bg}@1:t=fill")

    # INSIGNIAS
    overlay_args.append(f"drawbox=x={x_strip_loc}:y={strip_y}:w={strip_w}:h={strip_h}:color={loc_s1}@1:t=fill")
    overlay_args.append(f"drawbox=x={x_strip_loc+strip_w+2}:y={strip_y}:w={strip_w}:h={strip_h}:color={loc_s2}@1:t=fill")
    overlay_args.append(f"drawbox=x={x_strip_vis}:y={strip_y}:w={strip_w}:h={strip_h}:color={vis_s1}@1:t=fill")
    overlay_args.append(f"drawbox=x={x_strip_vis+strip_w+2}:y={strip_y}:w={strip_w}:h={strip_h}:color={vis_s2}@1:t=fill")

    # TEXTOS
    text_offset_loc = x_strip_loc + (strip_w * 2) + (8 * S)
    overlay_args.append(f"drawtext=fontfile='{font_bold}':text='{local_name}':x={text_offset_loc}:y={Y_POS}+({H_BAR}-th)/2:fontsize={fs_main}:fontcolor={text_color}")
    
    text_offset_vis = x_strip_vis - (8 * S)
    overlay_args.append(f"drawtext=fontfile='{font_bold}':text='{visit_name}':x={text_offset_vis}-tw:y={Y_POS}+({H_BAR}-th)/2:fontsize={fs_main}:fontcolor={text_color}")

    # Reloj
    overlay_args.append(f"drawtext=fontfile='{font_bold}':text='%{{pts\\:gmtime\\:0\\:%M\\\\\\:%S}}':x={x_time}+({W_TIME}-tw)/2:y={Y_POS}+({H_BAR}-th)/2:fontsize={fs_main}:fontcolor={text_color}")

    # Marcador Dinámico
    current_loc = 0
    current_vis = 0
    sorted_events = sorted(events, key=lambda x: x['time'])
    last_time = 0
    
    if not sorted_events:
        overlay_args.append(f"drawtext=fontfile='{font_bold}':text='0 - 0':x={x_score}+({W_SCORE}-tw)/2:y={Y_POS}+({H_BAR}-th)/2:fontsize={fs_main}:fontcolor={text_color}")
    else:
        for i, ev in enumerate(sorted_events):
            t_event = ev['time']
            score_text = f"{current_loc} - {current_vis}"
            overlay_args.append(f"drawtext=fontfile='{font_bold}':text='{score_text}':enable='between(t,{last_time},{t_event})':x={x_score}+({W_SCORE}-tw)/2:y={Y_POS}+({H_BAR}-th)/2:fontsize={fs_main}:fontcolor={text_color}")
            current_loc = ev['local']
            current_vis = ev['visitor']
            last_time = t_event
        
        final_score = f"{current_loc} - {current_vis}"
        overlay_args.append(f"drawtext=fontfile='{font_bold}':text='{final_score}':enable='gte(t,{last_time})':x={x_score}+({W_SCORE}-tw)/2:y={Y_POS}+({H_BAR}-th)/2:fontsize={fs_main}:fontcolor={text_color}")

    # -------------------------------------------------------------------------
    # 6. CALIDAD MEJORADA (720p)
    # -------------------------------------------------------------------------
    # - scale=-2:720 -> Calidad HD (Se verá bien, ya no borroso)
    # - crf=28       -> Buena compresión para no saturar la CPU
    # - ultrafast    -> Obligatorio para que no tarde 20 minutos
    filter_complex = ",".join(overlay_args) + ",scale=-2:1080"

    try:
        (
            ffmpeg
            .input(video_path)
            .output(
                output_path, 
                vf=filter_complex, 
                vcodec='libx264', 
                preset='ultrafast', 
                crf=28,             
                acodec='copy',
                threads=1            
            )
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        error_msg = e.stderr.decode('utf8')
        print("❌ CRITICAL FFMPEG ERROR:", error_msg)
        raise Exception(error_msg)

    return output_path