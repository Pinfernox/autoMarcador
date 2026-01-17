def parse_events(txt_path):
    events = []
    
    # Marcador inicial
    local_score = 0
    visitor_score = 0

    with open(txt_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # 1. Intentar leer el tiempo
            try:
                # Separamos tiempo (00:00) del texto
                if " " in line:
                    time_str, desc = line.split(" ", 1)
                else:
                    continue # Línea sin texto, la ignoramos

                min_, sec = map(int, time_str.split(":"))
                t = min_ * 60 + sec
            except ValueError:
                continue # Si la hora está mal escrita, saltamos la línea

            # 2. Analizar el texto (convertimos a minúsculas para evitar líos)
            desc_lower = desc.lower()

            # Solo procesamos si la línea empieza por "gol"
            if desc_lower.startswith("gol"):
                
                # A) DETECTAR VISITANTE
                if "(v)" in desc_lower or "visitante" in desc_lower:
                    visitor_score += 1
                
                # B) DETECTAR LOCAL EXPLÍCITO
                elif "(l)" in desc_lower or "local" in desc_lower:
                    local_score += 1
                
                # C) SI NO PONE NADA (Defecto)
                # Ej: "Gol Hugo" -> Asumimos que es Local
                else:
                    local_score += 1

                # Guardamos el evento con el marcador actualizado
                events.append({
                    "time": t,
                    "type": "GOAL",
                    "local": local_score,
                    "visitor": visitor_score
                })

    return events