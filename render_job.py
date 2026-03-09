import ffmpeg
import os

def render(video_path, events, config, output_path):
    print("🚀 Iniciando Renderizado (Versión Final: Controles de Diseño y Animación)...")

    # -------------------------------------------------------------------------
    # 1. EXTRACCIÓN DE CONFIGURACIÓN
    # -------------------------------------------------------------------------
    main_bg = config.get("main_bg", "#1E90FF")
    info_bg = config.get("info_bg", "#FFFFFF")
    text_color = config.get("text_color", "#000000")
    
    local_name = config.get("local_name", "LOCAL")
    loc_s1 = config.get("loc_s1", "#FFFFFF")
    loc_s2 = config.get("loc_s2", "#000000")
    style_local = config.get("style_local", "stripes")
    logo_local_path = config.get("logo_local", None)

    visit_name = config.get("visit_name", "VISIT")
    vis_s1 = config.get("vis_s1", "#FFFFFF")
    vis_s2 = config.get("vis_s2", "#000000")
    style_visit = config.get("style_visit", "stripes")
    logo_visit_path = config.get("logo_visit", None)

    logo_liga_path = config.get("logo_liga", None)
    show_liga_str = str(config.get("show_liga", "true")).lower()
    show_liga = show_liga_str == 'true'

    has_liga_logo = show_liga and logo_liga_path and os.path.exists(logo_liga_path)
    has_loc_logo  = logo_local_path and os.path.exists(logo_local_path)
    has_vis_logo  = logo_visit_path and os.path.exists(logo_visit_path)

    # -------------------------------------------------------------------------
    # HELPER: COLOR PARA OVERLAY
    # -------------------------------------------------------------------------
    def get_lavfi_color(hex_code):
        if not hex_code: return "white"
        if hex_code.lower() == "#ffffff" or hex_code.lower() == "white":
            return "white"
        if not hex_code.startswith("#"):
            return f"#{hex_code}"
        return hex_code

    banner_bg_color = get_lavfi_color(info_bg) 

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

    BASE_REF = 1100.0 
    S = width_final / BASE_REF 
    
    fs_main = int(13 * S)
    H_BAR = int(28 * S)
    Y_POS = int(25 * S)
    X_START = int(25 * S) 

    W_LIGA_BASE = int(30 * S)
    W_TIME  = int(60 * S)
    W_TEAM  = int(100 * S)
    W_SCORE = int(60 * S)

    # -------------------------------------------------------------------------
    # 3. CÁLCULO DE POSICIONES
    # -------------------------------------------------------------------------
    GAP_LIGA_TIME = 0 

    if show_liga:
        x_liga = X_START
        W_LIGA = W_LIGA_BASE
        x_time = int(x_liga + W_LIGA + GAP_LIGA_TIME)
    else:
        x_liga = 0
        W_LIGA = 0
        x_time = X_START

    x_loc   = int(x_time + W_TIME)
    x_score = int(x_loc + W_TEAM)
    x_vis   = int(x_score + W_SCORE)

    # -------------------------------------------------------------------------
    # 4. CONSTRUCCIÓN DE FLUJO FFMPEG
    # -------------------------------------------------------------------------
    input_file = ffmpeg.input(video_path)
    audio_stream = input_file.audio
    stream = input_file['v']

    # =========================================================================
    # CAPA 1: SOMBRA DEL MARCADOR (FONDO)
    # =========================================================================
    shadow_offset = int(4 * S)
    end_x = x_vis + W_TEAM
    start_shadow_x = x_liga if show_liga else x_time
    total_w = end_x - start_shadow_x
    
    stream = stream.filter('drawbox', x=start_shadow_x + shadow_offset, y=Y_POS + shadow_offset, 
                           w=total_w, h=H_BAR, color="black@0.4", t='fill')

    # =========================================================================
    # CAPA 2: BANNER DE GOLEADOR (CONTROLES DE DISEÑO)
    # =========================================================================
    sorted_events = sorted(events, key=lambda x: x['time'])
    
    # ---------------------------------------------------------
    # 🎛️ AJUSTES FINOS DEL BANNER (Modifica estos valores)
    # ---------------------------------------------------------
    BANNER_DURATION = 5.0     
    
    # ⏱️ VELOCIDAD DE ANIMACIÓN (Menor = Más rápido)
    ANIM_DURATION = 0.6
    
    # 📏 LONGITUD DEL BANNER (Aumenta el 140 para alargarlo)
    W_BANNER = int(100 * S) 
    
    # 📐 EL PÍXEL REBELDE (Alineación vertical perfecta)
    # Si asoma por arriba, cambia Y_POS + 0 a Y_POS + 1
    Y_BANNER = int(Y_POS + 0)
    # Si es muy gordo, cambia H_BAR - 0 a H_BAR - 1
    H_BANNER = int(H_BAR - 0)
    # ---------------------------------------------------------

    # Coordenadas horizontales
    X_VISIBLE = x_vis + W_TEAM          # Posición Final (derecha)
    X_HIDDEN = X_VISIBLE - W_BANNER     # Posición Inicial (escondido)

    for ev in sorted_events:
        author = ev.get('author', '')
        minute_txt = ev.get('time_str', '')
        t_event = float(ev['time'])
        
        if author and author != "GOL":
            t_start = t_event
            t_end = t_start + BANNER_DURATION
            t_anim_in_end = t_start + ANIM_DURATION
            t_anim_out_start = t_end - ANIM_DURATION
            
            # Fórmulas IDA Y VUELTA
            expr_in = f"{X_HIDDEN} + ({X_VISIBLE}-{X_HIDDEN}) * (t-{t_start})/{ANIM_DURATION}"
            expr_out = f"{X_VISIBLE} - ({X_VISIBLE}-{X_HIDDEN}) * (t-{t_anim_out_start})/{ANIM_DURATION}"
            slide_expr = f"if(lt(t, {t_anim_in_end}), {expr_in}, if(lt(t, {t_anim_out_start}), {X_VISIBLE}, {expr_out}))"

            # 1. Caja del Banner (Usando los valores ajustados Y_BANNER y H_BANNER)
            banner_src = ffmpeg.input(f"color=c={banner_bg_color}:s={W_BANNER}x{H_BANNER}", f='lavfi')
            stream = stream.overlay(
                banner_src,
                x=slide_expr,
                y=Y_BANNER, # <--- Alineación Y corregida
                enable=f"between(t,{t_start},{t_end})",
                shortest=1
            )
            
            # 2. Nombre del Jugador
            stream = stream.drawtext(
                fontfile=font_bold,
                text=author.upper(),
                x=f"{slide_expr} + (10*{S})", 
                y=f"{Y_BANNER}+({H_BANNER}-th)/2 - (4*{S})", # Centrado respecto a la nueva altura
                fontsize=int(fs_main * 0.95),
                fontcolor=text_color,
                enable=f"between(t,{t_start},{t_end})"
            )
            
            # 3. Minuto
            stream = stream.drawtext(
                fontfile=font_bold,
                text=minute_txt,
                x=f"{slide_expr} + (10*{S})", 
                y=f"{Y_BANNER}+({H_BANNER}-th)/2 + (6*{S})",
                fontsize=int(fs_main * 0.7),
                fontcolor="#666666",
                enable=f"between(t,{t_start},{t_end})"
            )

    # =========================================================================
    # CAPA 3: MARCADOR PRINCIPAL (Z-INDEX SUPERIOR)
    # =========================================================================

    if show_liga:
        stream = stream.filter('drawbox', x=x_liga, y=Y_POS, w=W_LIGA, h=H_BAR, color=f"{info_bg}@1", t='fill')

    stream = stream.filter('drawbox', x=x_time, y=Y_POS, w=W_TIME, h=H_BAR, color=f"{info_bg}@1", t='fill')
    stream = stream.filter('drawbox', x=x_loc, y=Y_POS, w=W_TEAM, h=H_BAR, color=f"{main_bg}@1", t='fill')
    stream = stream.filter('drawbox', x=x_score, y=Y_POS, w=W_SCORE, h=H_BAR, color=f"{info_bg}@1", t='fill')
    stream = stream.filter('drawbox', x=x_vis, y=Y_POS, w=W_TEAM, h=H_BAR, color=f"{main_bg}@1", t='fill')

    # D. INSIGNIAS / FRANJAS
    strip_h = int(16 * S)
    strip_y = int(Y_POS + (H_BAR - strip_h) / 2)
    space_WITH_logo = int(23 * S)
    space_NO_logo   = int(15 * S)

    # -- LOCAL --
    current_space_loc = space_WITH_logo if has_loc_logo else space_NO_logo
    x_strip_loc = int(x_loc + current_space_loc + (5 * S))
    strip_w_loc = 0
    if style_local == 'split':
        temp_w = int(4 * S)
        total_strip_w_loc = temp_w
    else:
        temp_w = int(5 * S)
        total_strip_w_loc = temp_w * 2 if style_local == 'stripes' else temp_w
    if not has_loc_logo:
        strip_w_loc = total_strip_w_loc
        if style_local == 'split':
            half_h = int(strip_h / 2)
            stream = stream.filter('drawbox', x=x_strip_loc, y=strip_y, w=temp_w, h=half_h, color=f"{loc_s1}@1", t='fill')
            stream = stream.filter('drawbox', x=x_strip_loc, y=strip_y+half_h, w=temp_w, h=half_h, color=f"{loc_s2}@1", t='fill')
        else:
            stream = stream.filter('drawbox', x=x_strip_loc, y=strip_y, w=temp_w, h=strip_h, color=f"{loc_s1}@1", t='fill')
            stream = stream.filter('drawbox', x=x_strip_loc+temp_w, y=strip_y, w=temp_w, h=strip_h, color=f"{loc_s2}@1", t='fill')
    else:
        strip_w_loc = 0

    # -- VISITANTE --
    current_space_vis = space_WITH_logo if has_vis_logo else space_NO_logo
    if style_visit == 'split':
        temp_w_vis = int(4 * S)
        total_strip_w_vis = temp_w_vis
    else:
        temp_w_vis = int(5 * S)
        total_strip_w_vis = temp_w_vis * 2
    x_strip_vis = int(x_vis + W_TEAM - current_space_vis - (5 * S) - total_strip_w_vis)
    strip_w_vis_actual = 0 
    if not has_vis_logo:
        strip_w_vis_actual = total_strip_w_vis
        if style_visit == 'split':
            half_h = int(strip_h / 2)
            stream = stream.filter('drawbox', x=x_strip_vis, y=strip_y, w=temp_w_vis, h=half_h, color=f"{vis_s1}@1", t='fill')
            stream = stream.filter('drawbox', x=x_strip_vis, y=strip_y+half_h, w=temp_w_vis, h=half_h, color=f"{vis_s2}@1", t='fill')
        else:
            stream = stream.filter('drawbox', x=x_strip_vis, y=strip_y, w=temp_w_vis, h=strip_h, color=f"{vis_s1}@1", t='fill')
            stream = stream.filter('drawbox', x=x_strip_vis+temp_w_vis, y=strip_y, w=temp_w_vis, h=strip_h, color=f"{vis_s2}@1", t='fill')
    else:
        strip_w_vis_actual = 0

    # E. TEXTOS Y RELOJ
    txt_x_loc = int(x_strip_loc + strip_w_loc + (6 * S))
    stream = stream.drawtext(fontfile=font_bold, text=local_name, x=txt_x_loc, 
                             y=f"{Y_POS}+({H_BAR}-th)/2", fontsize=fs_main, fontcolor=text_color)
    ref_right_vis = int(x_vis + W_TEAM - current_space_vis - (5 * S))
    if not has_vis_logo:
        txt_x_vis = int(x_strip_vis - (6 * S))
    else:
        txt_x_vis = int(ref_right_vis - (6 * S))
    stream = stream.drawtext(fontfile=font_bold, text=visit_name, x=f"{txt_x_vis}-tw", 
                             y=f"{Y_POS}+({H_BAR}-th)/2", fontsize=fs_main, fontcolor=text_color)

    time_str = "%{pts:gmtime:0:%M\\:%S}"
    stream = stream.drawtext(fontfile=font_bold, text=time_str, x=f"{x_time}+({W_TIME}-tw)/2", 
                             y=f"{Y_POS}+({H_BAR}-th)/2", fontsize=fs_main, fontcolor=text_color, escape_text=False)

    if show_liga and not has_liga_logo:
        stream = stream.drawtext(fontfile=font_bold, text="TV", x=f"{x_liga}+({W_LIGA}-tw)/2", 
                                 y=f"{Y_POS}+({H_BAR}-th)/2", fontsize=fs_main, fontcolor="#999999")

    # F. MARCADOR (GOLES)
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

    # G. LOGOS SUPERPUESTOS
    logo_target_h = int(20 * S) 
    logo_y = int(Y_POS + (H_BAR - logo_target_h) / 2)

    if has_loc_logo:
        logo_layer = ffmpeg.input(logo_local_path, loop=1)
        logo_layer = logo_layer.filter('scale', -2, logo_target_h)
        l_x = int(x_loc + (4 * S))
        stream = stream.overlay(logo_layer, x=l_x, y=logo_y, shortest=1)

    if has_vis_logo:
        logo_layer = ffmpeg.input(logo_visit_path, loop=1)
        logo_layer = logo_layer.filter('scale', -2, logo_target_h)
        l_x = int(x_vis + W_TEAM - logo_target_h - (4 * S))
        stream = stream.overlay(logo_layer, x=l_x, y=logo_y, shortest=1)

    if has_liga_logo:
        liga_target_h = int(21 * S)
        liga_y = int(Y_POS + (H_BAR - liga_target_h) / 2)
        logo_layer = ffmpeg.input(logo_liga_path, loop=1)
        logo_layer = logo_layer.filter('scale', -2, liga_target_h)
        l_x = int(x_liga + (W_LIGA - liga_target_h) / 2)
        stream = stream.overlay(logo_layer, x=l_x, y=liga_y, shortest=1)

    # -------------------------------------------------------------------------
    # 6. RENDER FINAL
    # -------------------------------------------------------------------------
    target_height = int(config.get("output_quality", 1080))
    print(f"🎥 Escalando salida a {target_height}p con Alta Calidad y Audio AAC...")
    stream = stream.filter('scale', -2, target_height)

    try:
        print("🎥 Ejecutando FFmpeg...")
        out = ffmpeg.output(stream, audio_stream, output_path, 
                            vcodec='libx264', 
                            preset='veryfast', 
                            crf=23, 
                            acodec='aac',          
                            audio_bitrate='192k') 
        out.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
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