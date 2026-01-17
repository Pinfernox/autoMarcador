def build_score_filters(events, x=20, y=20, size=36):
    filters = []
    local = 0
    visit = 0
    last_time = 0

    for e in events:
        if e["type"] == "GOAL":
            if e["team"] == "LOCAL":
                local += 1
            else:
                visit += 1

            score = f"{local} - {visit}"

            filters.append(
                f"drawtext=text='{score}':"
                f"x={x}:y={y}:fontsize={size}:"
                f"fontcolor=white:box=1:boxcolor=black@0.6:"
                f"enable='between(t,{last_time},{e['time']})'"
            )

            last_time = e["time"]

    return filters
