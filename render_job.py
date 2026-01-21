import ffmpeg
import os

def render(video_path, events, config, output_path):
    print("🚀 Iniciando Renderizado (Versión Final: Espaciado Dinámico)...")

    # -------------------------------------------------------------------------
    # 1. EXTRACCIÓN DE CONFIGURACIÓN
    # -------------------------------------------------------------------------
    main_bg = config.get("main_bg", "#1E90FF")
    info_bg = config.get("info_bg", "#FFFFFF")
    text_color = config.get("text_color", "#000000")
    
    # Local
    local_name = config.get("local_name", "LOCAL")
    loc_s1 = config.get("loc_s1", "#FFFFFF")
    loc_s2 = config.get("loc_s2", "#000000")
    style_local = config.get("style_local", "stripes")
    logo_local_path = config.get("logo_local", None)

    # Visitante
    visit_name = config.get("visit_name", "VISIT")
    vis_s1 = config.get("vis_s1", "#FFFFFF")
    vis_s2 = config.get("vis_s2", "#000000")
    style_visit = config.get("style_visit", "stripes")
    logo_visit_path = config.get("logo_visit", None)

    # Liga / TV
    logo_liga_path = config.get("logo_liga", None)
    show_liga_str = str(config.get("show_liga", "true")).lower()
    show_liga = show_liga_str == 'true'

    # Validación de Logos
    has_liga_logo = show_liga and logo_liga_path and os.path.exists(logo_liga_path)
    has_loc_logo  = logo_local_path and os.path.exists(logo_local_path)
    has_vis_logo  = logo_visit_path and os.path.exists(logo_visit_path)

    # -------------------------------------------------------------------------
    # 2. FUENTES Y GEOMETRÍA
    # -------------------------------------------------------------------------
    font_bold = "arial.ttf"
    possible_fonts = ["Inter-ExtraBold.ttf", "Inter-Bold.ttf", "Inter.ttf", "arial.ttf", 
                      "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
    for f in possible_fonts:
        if os.path.exists(f):
            font_bold = f
            break

    # Detección de ancho
    width_final = 1280 
    try:
        probe = ffmpeg.probe(video_path)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        width_raw = int(video_stream['width'])
        height_raw = int(video_stream['height'])
        
        tags = video_stream.get('tags', {})
        rotate = tags.get('rotate', '0')
        if str(rotate) in ['90', '-90', '270', '-270']:
            width_final = height_raw 
        else:
            width_final = width_raw
    except:
        pass

    BASE_REF = 680.0 
    S = width_final / BASE_REF 
    
    fs_main = int(13 * S)
    H_BAR = 28 * S
    Y_POS = 25 * S
    X_START = 25 * S 

    W_LIGA_BASE = 30 * S
    W_TIME  = 60 * S
    W_TEAM  = 100 * S
    W_SCORE = 60 * S

    # -------------------------------------------------------------------------
    # 3. CÁLCULO DE POSICIONES
    # -------------------------------------------------------------------------
    if show_liga:
        x_liga = X_START
        W_LIGA = W_LIGA_BASE
        x_time = x_liga + W_LIGA
    else:
        x_liga = 0
        W_LIGA = 0
        x_time = X_START

    x_loc   = x_time + W_TIME
    x_score = x_loc + W_TEAM
    x_vis   = x_score + W_SCORE

    # -------------------------------------------------------------------------
    # 4. CONSTRUCCIÓN DE FLUJO FFMPEG
    # -------------------------------------------------------------------------
    stream = ffmpeg.input(video_path)

    # A. CAJAS DE FONDO
    shadow_offset = 4 * S
    total_w = W_LIGA + W_TIME + W_TEAM + W_SCORE + W_TEAM
    start_shadow_x = x_liga if show_liga else x_time
    
    stream = stream.filter('drawbox', x=start_shadow_x + shadow_offset, y=Y_POS + shadow_offset, 
                           w=total_w, h=H_BAR, color="black@0.4", t='fill')

    if show_liga:
        stream = stream.filter('drawbox', x=x_liga, y=Y_POS, w=W_LIGA, h=H_BAR, color=f"{info_bg}@1", t='fill')

    stream = stream.filter('drawbox', x=x_time, y=Y_POS, w=W_TIME, h=H_BAR, color=f"{info_bg}@1", t='fill')
    stream = stream.filter('drawbox', x=x_loc, y=Y_POS, w=W_TEAM, h=H_BAR, color=f"{main_bg}@1", t='fill')
    stream = stream.filter('drawbox', x=x_score, y=Y_POS, w=W_SCORE, h=H_BAR, color=f"{info_bg}@1", t='fill')
    stream = stream.filter('drawbox', x=x_vis, y=Y_POS, w=W_TEAM, h=H_BAR, color=f"{main_bg}@1", t='fill')

    # B. INSIGNIAS / FRANJAS
    # --------------------------------------------------------
    strip_h = 16 * S
    strip_y = Y_POS + (H_BAR - strip_h) / 2
    
    # === [NUEVO] DEFINICIÓN DE ESPACIOS ===
    # Aquí definimos los dos tamaños que quieres:
    space_WITH_logo = 24 * S  # Espacio grande para cuando hay imagen
    space_NO_logo   = 15 * S  # Espacio ajustado (el que te gusta) para cuando son solo franjas

    # -- LOCAL --
    # Decidimos qué espacio usar dependiendo de si hay logo o no
    current_space_loc = space_WITH_logo if has_loc_logo else space_NO_logo
    
    x_strip_loc = x_loc + current_space_loc + (5 * S)
    strip_w_loc = 0

    if style_local == 'split':
        temp_w = 4 * S
        total_strip_w_loc = temp_w
    else:
        temp_w = 5 * S
        total_strip_w_loc = temp_w * 2 if style_local == 'stripes' else temp_w

    if not has_loc_logo:
        strip_w_loc = total_strip_w_loc
        if style_local == 'split':
            stream = stream.filter('drawbox', x=x_strip_loc, y=strip_y, w=temp_w, h=strip_h/2, color=f"{loc_s1}@1", t='fill')
            stream = stream.filter('drawbox', x=x_strip_loc, y=strip_y+(strip_h/2), w=temp_w, h=strip_h/2, color=f"{loc_s2}@1", t='fill')
        else:
            stream = stream.filter('drawbox', x=x_strip_loc, y=strip_y, w=temp_w, h=strip_h, color=f"{loc_s1}@1", t='fill')
            stream = stream.filter('drawbox', x=x_strip_loc+temp_w, y=strip_y, w=temp_w, h=strip_h, color=f"{loc_s2}@1", t='fill')
    else:
        strip_w_loc = 0

    # -- VISITANTE --
    # Decidimos espacio visitante
    current_space_vis = space_WITH_logo if has_vis_logo else space_NO_logo

    if style_visit == 'split':
        temp_w_vis = 4 * S
        total_strip_w_vis = temp_w_vis
    else:
        temp_w_vis = 5 * S
        total_strip_w_vis = temp_w_vis * 2

    # Usamos current_space_vis aquí
    x_strip_vis = x_vis + W_TEAM - current_space_vis - (5 * S) - total_strip_w_vis
    strip_w_vis_actual = 0 

    if not has_vis_logo:
        strip_w_vis_actual = total_strip_w_vis
        if style_visit == 'split':
            stream = stream.filter('drawbox', x=x_strip_vis, y=strip_y, w=temp_w_vis, h=strip_h/2, color=f"{vis_s1}@1", t='fill')
            stream = stream.filter('drawbox', x=x_strip_vis, y=strip_y+(strip_h/2), w=temp_w_vis, h=strip_h/2, color=f"{vis_s2}@1", t='fill')
        else:
            stream = stream.filter('drawbox', x=x_strip_vis, y=strip_y, w=temp_w_vis, h=strip_h, color=f"{vis_s1}@1", t='fill')
            stream = stream.filter('drawbox', x=x_strip_vis+temp_w_vis, y=strip_y, w=temp_w_vis, h=strip_h, color=f"{vis_s2}@1", t='fill')
    else:
        strip_w_vis_actual = 0

    # C. TEXTOS
    # ---------
    txt_x_loc = x_strip_loc + strip_w_loc + (6 * S)
    stream = stream.drawtext(fontfile=font_bold, text=local_name, x=txt_x_loc, 
                             y=f"{Y_POS}+({H_BAR}-th)/2", fontsize=fs_main, fontcolor=text_color)

    # Para el texto visitante, recalculamos la referencia derecha usando el espacio dinámico
    ref_right_vis = x_vis + W_TEAM - current_space_vis - (5 * S)
    
    if not has_vis_logo:
        txt_x_vis = x_strip_vis - (6 * S)
    else:
        txt_x_vis = ref_right_vis - (6 * S)

    stream = stream.drawtext(fontfile=font_bold, text=visit_name, x=f"{txt_x_vis}-tw", 
                             y=f"{Y_POS}+({H_BAR}-th)/2", fontsize=fs_main, fontcolor=text_color)

    # Cronómetro
    time_str = "%{pts:gmtime:0:%M\\:%S}"
    stream = stream.drawtext(
        fontfile=font_bold, 
        text=time_str, 
        x=f"{x_time}+({W_TIME}-tw)/2", 
        y=f"{Y_POS}+({H_BAR}-th)/2", 
        fontsize=fs_main, 
        fontcolor=text_color,
        escape_text=False
    )

    if show_liga and not has_liga_logo:
        stream = stream.drawtext(
            fontfile=font_bold, text="TV", 
            x=f"{x_liga}+({W_LIGA}-tw)/2", y=f"{Y_POS}+({H_BAR}-th)/2", 
            fontsize=fs_main, fontcolor="#999999"
        )

    # D. MARCADOR DINÁMICO
    sorted_events = sorted(events, key=lambda x: x['time'])
    current_loc = 0
    current_vis = 0
    last_time = 0
    
    if not sorted_events:
        stream = stream.drawtext(fontfile=font_bold, text="0 - 0", x=f"{x_score}+({W_SCORE}-tw)/2", y=f"{Y_POS}+({H_BAR}-th)/2", fontsize=fs_main, fontcolor=text_color)
    else:
        for ev in sorted_events:
            t_event = ev['time']
            score_txt = f"{current_loc} - {current_vis}"
            stream = stream.drawtext(fontfile=font_bold, text=score_txt, enable=f"between(t,{last_time},{t_event})", 
                                     x=f"{x_score}+({W_SCORE}-tw)/2", y=f"{Y_POS}+({H_BAR}-th)/2", fontsize=fs_main, fontcolor=text_color)
            current_loc = ev['local']
            current_vis = ev['visitor']
            last_time = t_event
        
        final_score = f"{current_loc} - {current_vis}"
        stream = stream.drawtext(fontfile=font_bold, text=final_score, enable=f"gte(t,{last_time})", 
                                 x=f"{x_score}+({W_SCORE}-tw)/2", y=f"{Y_POS}+({H_BAR}-th)/2", fontsize=fs_main, fontcolor=text_color)

    # -------------------------------------------------------------------------
    # 5. SUPERPOSICIÓN DE LOGOS
    # -------------------------------------------------------------------------
    logo_target_h = 20 * S 
    logo_y = Y_POS + (H_BAR - logo_target_h) / 2

    if has_loc_logo:
        logo_layer = ffmpeg.input(logo_local_path, loop=1)
        logo_layer = logo_layer.filter('scale', -2, int(logo_target_h))
        l_x = x_loc + (4 * S)
        stream = stream.overlay(logo_layer, x=l_x, y=logo_y, shortest=1)

    if has_vis_logo:
        logo_layer = ffmpeg.input(logo_visit_path, loop=1)
        logo_layer = logo_layer.filter('scale', -2, int(logo_target_h))
        l_x = x_vis + W_TEAM - logo_target_h - (4 * S)
        stream = stream.overlay(logo_layer, x=l_x, y=logo_y, shortest=1)

    if has_liga_logo:
        liga_target_h = 21 * S
        liga_y = Y_POS + (H_BAR - liga_target_h) / 2
        logo_layer = ffmpeg.input(logo_liga_path, loop=1)
        logo_layer = logo_layer.filter('scale', -2, int(liga_target_h))
        l_x = x_liga + (W_LIGA - liga_target_h) / 2
        stream = stream.overlay(logo_layer, x=l_x, y=liga_y, shortest=1)

    # -------------------------------------------------------------------------
    # 6. RENDER FINAL
    # -------------------------------------------------------------------------
    stream = stream.filter('scale', -2, 1080)

    try:
        print("🎥 Ejecutando FFmpeg...")
        stream.output(output_path, vcodec='libx264', preset='ultrafast', crf=28, acodec='copy').run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
    except ffmpeg.Error as e:
        error_log = e.stderr.decode('utf8')
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            print("⚠️ Advertencia FFmpeg (Proceso interrumpido pero video generado).")
            return output_path
        else:
            print("❌ Error Fatal FFmpeg:")
            print(error_log[-500:]) 
            raise e

    return output_path