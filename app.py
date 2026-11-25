logo" style="display:flex;align-items:center;justify-content:center;font-size:22px;">🏀'
)
return mapping

def _find_team_girone(team_name: str) -> str | None:
for g_name, items in GIRONI_TEAMS.items():
for item in items:
if item["squadra"] == team_name:
return g_name
return None

def _format_tooltip_data(g) -> dict[str, str]:
tokens = str(g.Data).strip().split()
date_part = tokens[1] if len(tokens) >= 3 else (tokens[0] if len(tokens) >= 1 else "")
return {
"date": date_part,
"home": str(g.Casa),
"away": str(g.Trasferta),
"score": f"{int(g.Punti_Casa)} - {int(g.Punti_Trasferta)}",
}

def _render_streak_html(events: list[dict], max_items: int = 5) -> str:
recent = events[-max_items:]
if not recent:
return '—'

```
items = []
for ev in recent:
    res = ev["res"]
    gid = quote(str(ev["game_id"]), safe="")
    tip = ev.get("tooltip_data", {})
    date_str = str(tip.get("date", "")).replace("<", "&lt;").replace(">", "&gt;")
    home_str = str(tip.get("home", "")).replace("<", "&lt;").replace(">", "&gt;")
    away_str = str(tip.get("away", "")).replace("<", "&lt;").replace(">", "&gt;")
    score_str = str(tip.get("score", "")).replace("<", "&lt;").replace(">", "&gt;")

    cls = "streak-w" if res == "W" else "streak-l"
    badge_cls = "tt-badge-w" if res == "W" else "tt-badge-l"
    esito_txt = "VITTORIA" if res == "W" else "SCONFITTA"

    items.append(
        f'<div class="streak-item">'
        f'<div class="streak-tooltip">'
        f'<div class="tt-top"><span>{date_str}</span><span class="{badge_cls}">{esito_txt}</span></div>'
        f'<div class="tt-match">{home_str}<span class="tt-score">{score_str}</span>{away_str}</div>'
        f'</div>'
        f'<a class="streak-link" href="?match={gid}" target="_self">'
        f'<span class="streak-box {cls}">{res}</span>'
        f'</a>'
        f'</div>'
    )
return f'<div class="streak-track">{"".join(items)}</div>'

```

def _h2h_points_for_group(group_teams: list[str], played_games: list[tuple]) -> dict[str, int]:
h2h_pts = {team: 0 for team in group_teams}
team_set = set(group_teams)
for g in played_games:
home = str(g.Casa)
away = str(g.Trasferta)
if home in team_set and away in team_set:
p_home = int(g.Punti_Casa)
p_away = int(g.Punti_Trasferta)
if p_home > p_away:
h2h_pts[home] += 2
elif p_away > p_home:
h2h_pts[away] += 2
return h2h_pts

def _rank_tied_group(group_rows: list[dict], played_games: list[tuple]) -> list[dict]:
if len(group_rows) <= 1:
return group_rows

```
group_names = [r["squadra"] for r in group_rows]
h2h_pts = _h2h_points_for_group(group_names, played_games)

return sorted(
    group_rows,
    key=lambda r: (-h2h_pts.get(r["squadra"], 0), -r["diff"], r["squadra"]),
)

```

def compute_standings(girone: str, games_df: pd.DataFrame) -> list[dict]:
teams = GIRONI_TEAMS.get(girone, [])
stats: dict[str, dict] = {
item["squadra"]: {
"girone": girone,
"squadra": item["squadra"],
"p": 0,
"w": 0,
"l": 0,
"pf": 0,
"ps": 0,
"diff": 0,
"streak_events": [],
"pts": 0,
}
for item in teams
}

```
g_played = games_df[
    (games_df["Girone"] == girone)
    & (games_df["Stato"].astype(str).str.strip().str.lower() == "giocata")
].sort_values(by=["Giornata", "ID_Partita"])

played_tuples = list(g_played.itertuples(index=False))

for g in played_tuples:
    home = str(g.Casa)
    away = str(g.Trasferta)
    p_home = int(g.Punti_Casa)
    p_away = int(g.Punti_Trasferta)
    gid = str(g.ID_Partita)
    tip_data = _format_tooltip_data(g)

    if home not in stats or away not in stats:
        continue

    stats[home]["p"] += 1
    stats[away]["p"] += 1
    stats[home]["pf"] += p_home
    stats[home]["ps"] += p_away
    stats[away]["pf"] += p_away
    stats[away]["ps"] += p_home

    if p_home > p_away:
        stats[home]["w"] += 1
        stats[away]["l"] += 1
        stats[home]["pts"] += 2
        stats[home]["streak_events"].append({"res": "W", "game_id": gid, "tooltip_data": tip_data})
        stats[away]["streak_events"].append({"res": "L", "game_id": gid, "tooltip_data": tip_data})
    elif p_away > p_home:
        stats[away]["w"] += 1
        stats[home]["l"] += 1
        stats[away]["pts"] += 2
        stats[away]["streak_events"].append({"res": "W", "game_id": gid, "tooltip_data": tip_data})
        stats[home]["streak_events"].append({"res": "L", "game_id": gid, "tooltip_data": tip_data})

for r in stats.values():
    r["diff"] = r["pf"] - r["ps"]

by_pts: dict[int, list[dict]] = {}
for r in stats.values():
    by_pts.setdefault(r["pts"], []).append(r)

ordered_rows: list[dict] = []
for pts_val in sorted(by_pts.keys(), reverse=True):
    ordered_rows.extend(_rank_tied_group(by_pts[pts_val], played_tuples))

return ordered_rows

```

def compute_thirds_standings(games_df: pd.DataFrame) -> list[dict]:
thirds = []
for g_name in ("Girone A", "Girone B", "Girone C"):
board = compute_standings(g_name, games_df)
if len(board) >= 3:
thirds.append(board[2])
return sorted(thirds, key=lambda r: (-r["pts"], -r["diff"], r["squadra"]))

def render_standings(girone: str, rows: list[dict], thirds_board: list[dict], logo_html_map: dict[str, str]) -> None:
st.markdown(STANDINGS_CSS, unsafe_allow_html=True)

```
playout_start = max(len(rows) - 3, 5)
best_third = thirds_board[0] if thirds_board else None

st.subheader(f"Classifica — {girone}")
st.caption("Clicca sul nome di una squadra per aprire la scheda squadra oppure passa sul quadratino W/L per i dettagli gara.")
html = [
    '<div class="board-box">',
    '<div class="board-head">'
    '<div>POS</div><div>LOGO</div><div class="left">SQUADRA</div>'
    '<div>P</div><div>W</div><div>L</div><div>DIFF</div><div>STREAK</div><div>PTS</div>'
    '</div>',
]

for pos, r in enumerate(rows, start=1):
    row_cls = ""
    is_best_third = (
        pos == 3
        and best_third is not None
        and best_third["squadra"] == r["squadra"]
        and best_third["girone"] == girone
    )

    if pos == 1:
        html.append('<div class="zone-tag zone-promo">Promozione Diretta (1° Posto)</div>')
        row_cls = "row-promo"
    elif pos == 2 or is_best_third:
        label_po = "Play-off (Migliore Terza)" if is_best_third else "Play-off (2° Posto)"
        html.append(f'<div class="zone-tag zone-po">{label_po}</div>')
        row_cls = "row-po"
    elif pos == playout_start:
        html.append('<div class="zone-tag zone-pout">Play-out (Ultime 4)</div>')

    if pos >= playout_start:
        row_cls = "row-pout"

    diff_val = r["diff"]
    diff_str = f"+{diff_val}" if diff_val > 0 else str(diff_val)
    streak_html = _render_streak_html(r.get("streak_events", []))

    team_encoded = quote(str(r["squadra"]), safe="")
    logo_tag = logo_html_map.get(f"board::{r['squadra']}", '<div class="b-pos">🏀</div>')
    html.append(
        f'<div class="board-row {row_cls}">'
        f'<div class="b-pos">{pos}</div>'
        f'<div><a href="?team={team_encoded}" target="_self">{logo_tag}</a></div>'
        f'<div><a class="team-link" href="?team={team_encoded}" target="_self">{r["squadra"]}</a></div>'
        f'<div class="b-val">{r["p"]}</div>'
        f'<div class="b-val">{r["w"]}</div>'
        f'<div class="b-val">{r["l"]}</div>'
        f'<div class="b-val">{diff_str}</div>'
        f'<div style="text-align:center;">{streak_html}</div>'
        f'<div class="b-pts">{r["pts"]}</div>'
        f'</div>'
    )

html.append("</div>")
st.markdown("".join(html), unsafe_allow_html=True)

if thirds_board:
    st.subheader("Mini-Classifica Terze Classificate (Migliore Terza ai Play-off)")
    t_html = [
        '<div class="board-box">',
        '<div class="board-head">'
        '<div>#</div><div>LOGO</div><div class="left">TERZA CLASSIFICATA</div>'
        '<div>P</div><div>W</div><div>L</div><div>DIFF</div><div>STREAK</div><div>PTS</div>'
        '</div>',
    ]
    for idx, t in enumerate(thirds_board, start=1):
        qual = idx == 1
        r_cls = "row-qual" if qual else "row-out"
        badge = '<span class="badge-ok">PLAY-OFF</span>' if qual else '<span class="badge-no">FUORI</span>'
        diff_val = t["diff"]
        diff_str = f"+{diff_val}" if diff_val > 0 else str(diff_val)
        streak_html = _render_streak_html(t.get("streak_events", []))
        team_encoded = quote(str(t["squadra"]), safe="")
        logo_tag = logo_html_map.get(f"board::{t['squadra']}", '<div class="b-pos">🏀</div>')
        t_html.append(
            f'<div class="board-row {r_cls}">'
            f'<div class="b-pos">{idx}</div>'
            f'<div><a href="?team={team_encoded}" target="_self">{logo_tag}</a></div>'
            f'<div>'
            f'<a class="team-link" href="?team={team_encoded}" target="_self">{t["squadra"]}</a>'
            f'<div class="b-sub">{t["girone"]}{badge}</div>'
            f'</div>'
            f'<div class="b-val">{t["p"]}</div>'
            f'<div class="b-val">{t["w"]}</div>'
            f'<div class="b-val">{t["l"]}</div>'
            f'<div class="b-val">{diff_str}</div>'
            f'<div style="text-align:center;">{streak_html}</div>'
            f'<div class="b-pts">{t["pts"]}</div>'
            '</div>'
        )
    t_html.append("</div>")
    st.markdown("".join(t_html), unsafe_allow_html=True)

```

def build_round_html(
round_num: int,
round_games: pd.DataFrame,
logo_html_map: dict[str, str],
is_ritorno: bool = False,
girone_label: str = "DR2 Puglia",
) -> str:
display_num = round_num - 11 if is_ritorno and round_num > 11 else round_num
phase_label = "RITORNO" if is_ritorno else "ANDATA"

```
parts = [
    '<div class="cal-board">',
    '<div class="cal-board-head">'
    '<div class="c-left">GIORNATA</div>'
    '<div class="c-right">SQUADRA DI CASA</div>'
    '<div class="c-center">RISULTATO</div>'
    '<div class="c-left">SQUADRA OSPITE</div>'
    "</div>",
]

if round_games.empty:
    parts.append(
        '<div class="cal-row-card">'
        f'<div class="cal-round-col"><div class="cal-round-num">{display_num}ª Giornata • {phase_label}</div><div class="cal-round-date">—</div></div>'
        '<div class="cal-side-home"><span class="cal-side-name">Nessuna gara</span></div>'
        '<div class="cal-score-box"><div class="cal-score-line cal-pts-vs">-</div></div>'
        '<div class="cal-side-away"><span class="cal-side-name">in programma</span></div>'
        "</div>"
    )
else:
    for g in round_games.itertuples(index=False):
        gid_encoded = quote(str(g.ID_Partita), safe="")
        is_played = str(g.Stato).strip().lower() == "giocata"
        tokens = str(g.Data).strip().split()
        if len(tokens) >= 3:
            date_str, time_str = tokens[1], tokens[2]
        elif len(tokens) == 2:
            date_str, time_str = tokens[0], tokens[1]
        else:
            date_str, time_str = str(g.Data).strip(), ""

        home_name = str(g.Casa)
        away_name = str(g.Trasferta)
        home_pts = int(g.Punti_Casa)
        away_pts = int(g.Punti_Trasferta)

        h_logo_src = logo_html_map.get(f"raw_src::{home_name}", "")
        a_logo_src = logo_html_map.get(f"raw_src::{away_name}", "")
        h_logo = f'<img class="cal-side-logo" src="{h_logo_src}" alt="" loading="lazy" />' if h_logo_src else "🏀"
        a_logo = f'<img class="cal-side-logo" src="{a_logo_src}" alt="" loading="lazy" />' if a_logo_src else "🏀"

        if is_played:
            h_win = home_pts > away_pts
            a_win = away_pts > home_pts
            h_cls = "cal-pts-win" if h_win else "cal-pts-lose"
            a_cls = "cal-pts-win" if a_win else "cal-pts-lose"
            score_html = (
                f'<div class="cal-score-line">'
                f'<span class="{h_cls}">{home_pts}</span>'
                f'<span style="color:#64748b;margin:0 3px;">-</span>'
                f'<span class="{a_cls}">{away_pts}</span>'
                f"</div>"
                f'<div class="cal-state-sub done">CONCLUSA</div>'
            )
        else:
            h_win = False
            a_win = False
            sub_txt = time_str if time_str else "DA GIOCARE"
            score_html = (
                '<div class="cal-score-line cal-pts-vs">VS</div>'
                f'<div class="cal-state-sub todo">{sub_txt}</div>'
            )

        parts.append(
            f'<a class="cal-row-link" href="?match={gid_encoded}" target="_self">'
            '<div class="cal-row-card">'
            '<div class="cal-round-col">'
            f'<div class="cal-round-league">{girone_label}</div>'
            f'<div class="cal-round-num">{display_num}ª Giornata • {phase_label}</div>'
            f'<div class="cal-round-date">{date_str}</div>'
            "</div>"
            '<div class="cal-side-home">'
            f'<span class="cal-side-name {"win" if h_win else ""}">{home_name}</span>'
            f"{h_logo}"
            "</div>"
            f'<div class="cal-score-box">{score_html}</div>'
            '<div class="cal-side-away">'
            f"{a_logo}"
            f'<span class="cal-side-name {"win" if a_win else ""}">{away_name}</span>'
            "</div>"
            "</div>"
            "</a>"
        )

parts.append("</div>")
return "".join(parts)

```

def _fmt_pct(made: int, att: int) -> str:
if att <= 0:
return "0"
val = (made / att) * 100.0
if abs(val - round(val)) < 1e-6:
return str(int(round(val)))
return f"{val:.1f}"

def _parse_minutes_to_int(min_str: str) -> int:
s = str(min_str or "").strip()
if not s or s == "-":
return 0
if ":" in s:
try:
m_part, s_part = s.split(":", 1)
return int(float(m_part)) + (1 if int(float(s_part)) >= 30 else 0)
except Exception:
return 0
try:
return int(float(s))
except Exception:
return 0

def _extract_jersey_number(name: str, explicit_num: object = None) -> int:
if explicit_num is not None and str(explicit_num).strip() != "":
parsed = pd.to_numeric(explicit_num, errors="coerce")
if pd.notna(parsed):
val = int(parsed)
if 0 <= val <= 99:
return val
m = re.match(r"^\s*#?(\d{1,2})\b", str(name or ""))
if m:
return int(m.group(1))
return 999

def _extract_surname(full_name: str) -> str:
cleaned = re.sub(r"\s*$N\.E\.$\s*$", "", str(full_name or ""), flags=re.IGNORECASE).strip()
cleaned = re.sub(r"^\s*#?\d+\s*[-–.]?\s*", "", cleaned).strip()
if not cleaned:
return ""
parts = cleaned.split()
if len(parts) == 1:
return parts[0]
if len(parts[-1]) <= 2 and len(parts[0]) > 2:
return parts[0]
return parts[-1]

def _normalize_player_rows(rows: list | None) -> list[dict]:
if not isinstance(rows, list):
return []
out: list[dict] = []
for item in rows:
if not isinstance(item, dict):
continue
name = str(item.get("Giocatore", "")).strip()
if not name:
continue

```
    pts_val = item.get("PUN", item.get("PTS", 0))
    t2_r_val = item.get("2PT_R", item.get("2PT", 0))
    t2_t_val = item.get("2PT_T", max(int(pd.to_numeric(t2_r_val, errors="coerce") or 0), 0))
    t3_r_val = item.get("3PT_R", item.get("3PT", 0))
    t3_t_val = item.get("3PT_T", max(int(pd.to_numeric(t3_r_val, errors="coerce") or 0), 0))
    tl_r_val = item.get("TL_R", 0)
    tl_sbag_val = item.get("TL_SBAG", 0)
    tl_t_val = item.get(
        "TL_T",
        int(pd.to_numeric(tl_r_val, errors="coerce") or 0) + int(pd.to_numeric(tl_sbag_val, errors="coerce") or 0),
    )
    fc_val = item.get("F_C", item.get("FALLI", 0))
    sf_val = item.get("SF", item.get("QUINTETTO", False))
    num_val = _extract_jersey_number(name, item.get("NUM", None))

    out.append(
        {
            "Giocatore": name,
            "NUM": num_val,
            "PUN": int(pd.to_numeric(pts_val, errors="coerce") or 0),
            "MIN": str(item.get("MIN", "0") or "0").strip(),
            "SF": bool(sf_val),
            "F_C": int(pd.to_numeric(fc_val, errors="coerce") or 0),
            "F_S": int(pd.to_numeric(item.get("F_S", 0), errors="coerce") or 0),
            "2PT_R": int(pd.to_numeric(t2_r_val, errors="coerce") or 0),
            "2PT_T": int(pd.to_numeric(t2_t_val, errors="coerce") or 0),
            "SC": int(pd.to_numeric(item.get("SC", 0), errors="coerce") or 0),
            "3PT_R": int(pd.to_numeric(t3_r_val, errors="coerce") or 0),
            "3PT_T": int(pd.to_numeric(t3_t_val, errors="coerce") or 0),
            "TL_R": int(pd.to_numeric(tl_r_val, errors="coerce") or 0),
            "TL_T": int(pd.to_numeric(tl_t_val, errors="coerce") or 0),
            "RIM_O": int(pd.to_numeric(item.get("RIM_O", 0), errors="coerce") or 0),
            "RIM_D": int(pd.to_numeric(item.get("RIM_D", 0), errors="coerce") or 0),
            "ST_D": int(pd.to_numeric(item.get("ST_D", 0), errors="coerce") or 0),
            "ST_S": int(pd.to_numeric(item.get("ST_S", 0), errors="coerce") or 0),
            "PAL_P": int(pd.to_numeric(item.get("PAL_P", 0), errors="coerce") or 0),
            "PAL_R": int(pd.to_numeric(item.get("PAL_R", 0), errors="coerce") or 0),
            "ASS": int(pd.to_numeric(item.get("ASS", 0), errors="coerce") or 0),
            "VAL": int(pd.to_numeric(item.get("VAL", 0), errors="coerce") or 0),
            "OER": float(pd.to_numeric(item.get("OER", 0.0), errors="coerce") or 0.0),
        }
    )
return out

```

def _get_match_detail(match_id: str) -> dict:
store = st.session_state.setdefault("match_details_store", {})
raw = store.get(match_id)
if isinstance(raw, dict):
qh = list(raw.get("quarters_home", [0, 0, 0, 0]))[:4]
qa = list(raw.get("quarters_away", [0, 0, 0, 0]))[:4]
while len(qh) < 4:
qh.append(0)
while len(qa) < 4:
qa.append(0)
return {
"coach_home": str(raw.get("coach_home", "") or ""),
"coach_away": str(raw.get("coach_away", "") or ""),
"quarters_home": [int(x) for x in qh],
"quarters_away": [int(x) for x in qa],
"ot_home": int(raw.get("ot_home", 0) or 0),
"ot_away": int(raw.get("ot_away", 0) or 0),
"home_players": _normalize_player_rows(raw.get("home_players")),
"away_players": _normalize_player_rows(raw.get("away_players")),
"notes": str(raw.get("notes", "") or ""),
}

```
return {
    "coach_home": "",
    "coach_away": "",
    "quarters_home": [0, 0, 0, 0],
    "quarters_away": [0, 0, 0, 0],
    "ot_home": 0,
    "ot_away": 0,
    "home_players": [],
    "away_players": [],
    "notes": "",
}

```

def _players_to_editor_df(player_list: list[dict], full_stats: bool = True, min_rows: int = 8) -> pd.DataFrame:
rows = _normalize_player_rows(player_list)
while len(rows) < min_rows:
rows.append(_p_row(""))
df = pd.DataFrame(rows)
if full_stats:
front_cols = ["NUM", "Giocatore"]
rest_cols = [c for c in df.columns if c not in front_cols]
return df[front_cols + rest_cols]
compact_cols = ["NUM", "Giocatore", "PUN", "MIN", "SF", "F_C", "2PT_R", "SC", "3PT_R", "TL_R", "TL_T", "ASS"]
return df[compact_cols]

def _editor_df_to_players(df: pd.DataFrame, existing_players: list[dict] | None = None) -> list[dict]:
if df is None or df.empty:
return []
existing_by_name = {
str(p.get("Giocatore", "")).strip().lower(): p
for p in _normalize_player_rows(existing_players)
}
out: list[dict] = []
for r in df.itertuples(index=False):
name = str(getattr(r, "Giocatore", "") or "").strip()
if not name:
continue
prev = existing_by_name.get(name.lower(), {})
r2_val = int(pd.to_numeric(getattr(r, "2PT_R", prev.get("2PT_R", 0)), errors="coerce") or 0)
t2_val = int(pd.to_numeric(getattr(r, "2PT_T", prev.get("2PT_T", r2_val)), errors="coerce") or 0)
if t2_val < r2_val:
t2_val = r2_val
r3_val = int(pd.to_numeric(getattr(r, "3PT_R", prev.get("3PT_R", 0)), errors="coerce") or 0)
t3_val = int(pd.to_numeric(getattr(r, "3PT_T", prev.get("3PT_T", r3_val)), errors="coerce") or 0)
if t3_val < r3_val:
t3_val = r3_val
tl_r_val = int(pd.to_numeric(getattr(r, "TL_R", prev.get("TL_R", 0)), errors="coerce") or 0)
tl_t_val = int(pd.to_numeric(getattr(r, "TL_T", prev.get("TL_T", tl_r_val)), errors="coerce") or 0)
if tl_t_val < tl_r_val:
tl_t_val = tl_r_val

```
    out.append(
        _p_row(
            giocatore=name,
            numero=_extract_jersey_number(name, getattr(r, "NUM", prev.get("NUM", None))),
            pts=int(pd.to_numeric(getattr(r, "PUN", prev.get("PUN", 0)), errors="coerce") or 0),
            minuti=str(getattr(r, "MIN", prev.get("MIN", "0")) or "0").strip(),
            sf=bool(getattr(r, "SF", prev.get("SF", False))),
            falli_c=int(pd.to_numeric(getattr(r, "F_C", prev.get("F_C", 0)), errors="coerce") or 0),
            falli_s=int(pd.to_numeric(getattr(r, "F_S", prev.get("F_S", 0)), errors="coerce") or 0),
            t2_r=r2_val,
            t2_t=t2_val,
            sc=int(pd.to_numeric(getattr(r, "SC", prev.get("SC", 0)), errors="coerce") or 0),
            t3_r=r3_val,
            t3_t=t3_val,
            tl_r=tl_r_val,
            tl_t=tl_t_val,
            rim_o=int(pd.to_numeric(getattr(r, "RIM_O", prev.get("RIM_O", 0)), errors="coerce") or 0),
            rim_d=int(pd.to_numeric(getattr(r, "RIM_D", prev.get("RIM_D", 0)), errors="coerce") or 0),
            st_d=int(pd.to_numeric(getattr(r, "ST_D", prev.get("ST_D", 0)), errors="coerce") or 0),
            st_s=int(pd.to_numeric(getattr(r, "ST_S", prev.get("ST_S", 0)), errors="coerce") or 0),
            pal_p=int(pd.to_numeric(getattr(r, "PAL_P", prev.get("PAL_P", 0)), errors="coerce") or 0),
            pal_r=int(pd.to_numeric(getattr(r, "PAL_R", prev.get("PAL_R", 0)), errors="coerce") or 0),
            ass=int(pd.to_numeric(getattr(r, "ASS", prev.get("ASS", 0)), errors="coerce") or 0),
            val_lega=int(pd.to_numeric(getattr(r, "VAL", prev.get("VAL", 0)), errors="coerce") or 0),
            oer=float(pd.to_numeric(getattr(r, "OER", prev.get("OER", 0.0)), errors="coerce") or 0.0),
        )
    )
return out

```

def render_lba_boxscore(
team_name: str,
coach_name: str,
players: list[dict],
logo_html_map: dict[str, str],
full_stats: bool = True,
) -> None:
norm_players = _normalize_player_rows(players)
logo_tag = logo_html_map.get(
f"lba::{team_name}",
'🏀',
)
allenatore_txt = coach_name.strip() if coach_name.strip() else "—"
badge_txt = "STATISTICHE DETTAGLIATE" if full_stats else "TABELLINO ESSENZIALE"

```
table_cls = "lba-box full-stats" if full_stats else "lba-box compact-stats"

if full_stats:
    header_html = (
        "<tr>"
        '<th class="grp-empty" colspan="4"></th>'
        '<th class="grp-hdr" colspan="2">FALLI</th>'
        '<th class="grp-hdr" colspan="3">TIRI DA 2</th>'
        '<th class="grp-empty" colspan="1"></th>'
        '<th class="grp-hdr" colspan="3">TIRI DA 3</th>'
        '<th class="grp-hdr" colspan="3">TIRI LIBERI</th>'
        '<th class="grp-hdr" colspan="3">RIMBALZI</th>'
        '<th class="grp-hdr" colspan="2">STOPPATE</th>'
        '<th class="grp-hdr" colspan="2">PALLE</th>'
        '<th class="grp-empty" colspan="1"></th>'
        '<th class="grp-hdr" colspan="2">VALUTAZIONE</th>'
        "</tr>"
        "<tr>"
        '<th class="sub-hdr left-col">GIOCATORE</th>'
        '<th class="sub-hdr pts-col">PUN</th>'
        '<th class="sub-hdr">MIN</th>'
        '<th class="sub-hdr">SF</th>'
        '<th class="sub-hdr">C</th>'
        '<th class="sub-hdr">S</th>'
        '<th class="sub-hdr">R</th>'
        '<th class="sub-hdr">T</th>'
        '<th class="sub-hdr pts-col">%</th>'
        '<th class="sub-hdr">SC</th>'
        '<th class="sub-hdr">R</th>'
        '<th class="sub-hdr">T</th>'
        '<th class="sub-hdr pts-col">%</th>'
        '<th class="sub-hdr">R</th>'
        '<th class="sub-hdr">T</th>'
        '<th class="sub-hdr pts-col">%</th>'
        '<th class="sub-hdr">O</th>'
        '<th class="sub-hdr">D</th>'
        '<th class="sub-hdr">T</th>'
        '<th class="sub-hdr">D</th>'
        '<th class="sub-hdr">S</th>'
        '<th class="sub-hdr">P</th>'
        '<th class="sub-hdr">R</th>'
        '<th class="sub-hdr">ASS</th>'
        '<th class="sub-hdr">LEGA</th>'
        '<th class="sub-hdr">OER</th>'
        "</tr>"
    )
else:
    header_html = (
        "<tr>"
        '<th class="grp-empty" colspan="4"></th>'
        '<th class="grp-hdr" colspan="1">FALLI</th>'
        '<th class="grp-hdr" colspan="1">TIRI DA 2</th>'
        '<th class="grp-empty" colspan="1"></th>'
        '<th class="grp-hdr" colspan="1">TIRI DA 3</th>'
        '<th class="grp-hdr" colspan="3">TIRI LIBERI</th>'
        '<th class="grp-empty" colspan="1"></th>'
        "</tr>"
        "<tr>"
        '<th class="sub-hdr left-col">GIOCATORE</th>'
        '<th class="sub-hdr pts-col">PUN</th>'
        '<th class="sub-hdr">MIN</th>'
        '<th class="sub-hdr">SF</th>'
        '<th class="sub-hdr">C</th>'
        '<th class="sub-hdr">R</th>'
        '<th class="sub-hdr">SC</th>'
        '<th class="sub-hdr">R</th>'
        '<th class="sub-hdr">R</th>'
        '<th class="sub-hdr">T</th>'
        '<th class="sub-hdr pts-col">%</th>'
        '<th class="sub-hdr">ASS</th>'
        "</tr>"
    )

html = [
    '<div class="lba-box-card">',
    '<div class="lba-team-banner">',
    f'<div class="lba-banner-left">{logo_tag}<div>'
    f'<div class="lba-team-title">{team_name}</div>'
    f'<div class="lba-team-coach">Allenatore: {allenatore_txt}</div>'
    f"</div></div>",
    f'<div class="lba-tag-pill">{badge_txt}</div>',
    "</div>",
    f'<div class="lba-table-wrap"><table class="{table_cls}"><thead>',
    header_html,
    "</thead><tbody>",
]

tot_pun = tot_min_num = 0
tot_fc = tot_fs = 0
tot_2r = tot_2t = tot_sc = 0
tot_3r = tot_3t = 0
tot_tlr = tot_tlt = 0
tot_rimo = tot_rimd = tot_rimt = 0
tot_std = tot_sts = 0
tot_palp = tot_palr = tot_ass = 0
tot_val = 0

for p in norm_players:
    pun = int(p["PUN"])
    min_str = str(p["MIN"]) if str(p["MIN"]).strip() else "0"
    sf_mark = "✓" if p["SF"] else ""
    fc = int(p["F_C"])
    fs = int(p["F_S"])
    r2 = int(p["2PT_R"])
    t2 = int(p["2PT_T"])
    sc = int(p["SC"])
    r3 = int(p["3PT_R"])
    t3 = int(p["3PT_T"])
    rtl = int(p["TL_R"])
    ttl = int(p["TL_T"])
    ro = int(p["RIM_O"])
    rd = int(p["RIM_D"])
    rt = ro + rd
    sd = int(p["ST_D"])
    ss = int(p["ST_S"])
    pp = int(p["PAL_P"])
    pr = int(p["PAL_R"])
    ass = int(p["ASS"])
    val_l = int(p["VAL"])
    oer_v = f"{float(p['OER']):.1f}" if float(p["OER"]) != 0 else "0"
    num_badge = f'<span class="num-badge">#{int(p["NUM"])}</span>' if int(p["NUM"]) < 999 else ""

    tot_pun += pun
    tot_min_num += _parse_minutes_to_int(min_str)
    tot_fc += fc
    tot_fs += fs
    tot_2r += r2
    tot_2t += t2
    tot_sc += sc
    tot_3r += r3
    tot_3t += t3
    tot_tlr += rtl
    tot_tlt += ttl
    tot_rimo += ro
    tot_rimd += rd
    tot_rimt += rt
    tot_std += sd
    tot_sts += ss
    tot_palp += pp
    tot_palr += pr
    tot_ass += ass
    tot_val += val_l

    if full_stats:
        html.append(
            "<tr>"
            f'<td class="player-name">{num_badge}{p["Giocatore"]}</td>'
            f'<td class="pts-val">{pun}</td>'
            f"<td>{min_str}</td>"
            f'<td class="sf-check">{sf_mark}</td>'
            f"<td>{fc}</td>"
            f"<td>{fs}</td>"
            f"<td>{r2}</td>"
            f"<td>{t2}</td>"
            f'<td class="pct-val">{_fmt_pct(r2, t2)}</td>'
            f"<td>{sc}</td>"
            f"<td>{r3}</td>"
            f"<td>{t3}</td>"
            f'<td class="pct-val">{_fmt_pct(r3, t3)}</td>'
            f"<td>{rtl}</td>"
            f"<td>{ttl}</td>"
            f'<td class="pct-val">{_fmt_pct(rtl, ttl)}</td>'
            f"<td>{ro}</td>"
            f"<td>{rd}</td>"
            f"<td>{rt}</td>"
            f"<td>{sd}</td>"
            f"<td>{ss}</td>"
            f"<td>{pp}</td>"
            f"<td>{pr}</td>"
            f"<td>{ass}</td>"
            f"<td>{val_l}</td>"
            f"<td>{oer_v}</td>"
            "</tr>"
        )
    else:
        html.append(
            "<tr>"
            f'<td class="player-name">{num_badge}{p["Giocatore"]}</td>'
            f'<td class="pts-val">{pun}</td>'
            f"<td>{min_str}</td>"
            f'<td class="sf-check">{sf_mark}</td>'
            f"<td>{fc}</td>"
            f"<td>{r2}</td>"
            f"<td>{sc}</td>"
            f"<td>{r3}</td>"
            f"<td>{rtl}</td>"
            f"<td>{ttl}</td>"
            f'<td class="pct-val">{_fmt_pct(rtl, ttl)}</td>'
            f"<td>{ass}</td>"
            "</tr>"
        )

if full_stats:
    tot_oer = f"{(tot_pun / max(tot_2t + tot_3t + tot_palp, 1)):.1f}" if (tot_2t + tot_3t + tot_palp) > 0 else "0"
    html.append(
        '<tr class="total-row">'
        '<td class="player-name">TOTALI</td>'
        f'<td class="pts-val">{tot_pun}</td>'
        f"<td>{tot_min_num}</td>"
        "<td>-</td>"
        f"<td>{tot_fc}</td><td>{tot_fs}</td>"
        f"<td>{tot_2r}</td><td>{tot_2t}</td><td class=\"pct-val\">{_fmt_pct(tot_2r, tot_2t)}</td>"
        f"<td>{tot_sc}</td>"
        f"<td>{tot_3r}</td><td>{tot_3t}</td><td class=\"pct-val\">{_fmt_pct(tot_3r, tot_3t)}</td>"
        f"<td>{tot_tlr}</td><td>{tot_tlt}</td><td class=\"pct-val\">{_fmt_pct(tot_tlr, tot_tlt)}</td>"
        f"<td>{tot_rimo}</td><td>{tot_rimd}</td><td>{tot_rimt}</td>"
        f"<td>{tot_std}</td><td>{tot_sts}</td>"
        f"<td>{tot_palp}</td><td>{tot_palr}</td>"
        f"<td>{tot_ass}</td>"
        f"<td>{tot_val}</td>"
        f"<td>{tot_oer}</td>"
        "</tr>"
    )
else:
    html.append(
        '<tr class="total-row">'
        '<td class="player-name">TOTALI</td>'
        f'<td class="pts-val">{tot_pun}</td>'
        f"<td>{tot_min_num}</td>"
        "<td>-</td>"
        f"<td>{tot_fc}</td>"
        f"<td>{tot_2r}</td>"
        f"<td>{tot_sc}</td>"
        f"<td>{tot_3r}</td>"
        f"<td>{tot_tlr}</td>"
        f"<td>{tot_tlt}</td>"
        f'<td class="pct-val">{_fmt_pct(tot_tlr, tot_tlt)}</td>'
        f"<td>{tot_ass}</td>"
        "</tr>"
    )

html.append("</tbody></table></div></div>")
st.markdown("".join(html), unsafe_allow_html=True)

```

def _render_court_formation(
home_name: str,
away_name: str,
home_players: list[dict],
away_players: list[dict],
logo_html_map: dict[str, str],
) -> None:
def _prepare_roster(plist: list[dict]) -> tuple[list[dict], list[dict]]:
norm = sorted(
_normalize_player_rows(plist),
key=lambda x: (int(x.get("NUM", 999)), str(x.get("Giocatore", ""))),
)
starters = [p for p in norm if bool(p.get("SF"))]
starter_ids = {id(p) for p in starters}
if len(starters) < 5:
for p in norm:
if id(p) not in starter_ids:
starters.append(p)
starter_ids.add(id(p))
if len(starters) == 5:
break
starters_five = sorted(
starters[:5],
key=lambda x: (int(x.get("NUM", 999)), str(x.get("Giocatore", ""))),
)
five_ids = {id(p) for p in starters_five}
bench = [p for p in norm if id(p) not in five_ids]
return starters_five, bench

```
h_starters, h_bench = _prepare_roster(home_players)
a_starters, a_bench = _prepare_roster(away_players)

def _roster_col_html(team_name: str, starters: list[dict], bench: list[dict], is_right: bool = False) -> str:
    logo_src = logo_html_map.get(f"raw_src::{team_name}", "")
    logo_img = f'<img src="{logo_src}" alt="" />' if logo_src else "🏀"
    align_style = ' style="justify-content:flex-end;text-align:right;"' if is_right else ""

    def _line(p: dict, is_st: bool) -> str:
        num_txt = str(int(p.get("NUM", 0))) if int(p.get("NUM", 0)) < 999 else "?"
        cls_st = " starter" if is_st else ""
        return (
            f'<div class="roster-player-line{cls_st}">'
            f'<span class="roster-num-pill">#{num_txt}</span>'
            f'<span>{p["Giocatore"]}</span>'
            f"</div>"
        )

    st_html = "".join(_line(p, True) for p in starters) or '<div style="color:#94a3b8;font-size:11.5px;">Nessun quintetto</div>'
    bn_html = "".join(_line(p, False) for p in bench) or '<div style="color:#94a3b8;font-size:11.5px;">Nessun altro atleta</div>'

    return (
        '<div class="roster-side-card">'
        f'<div class="roster-side-head"{align_style}>{logo_img}<span>{team_name}</span></div>'
        '<div class="roster-group-lbl">Quintetto Base (Primi 5)</div>'
        f"{st_html}"
        '<hr class="roster-divider" />'
        '<div class="roster-group-lbl">Altri Atleti</div>'
        f"{bn_html}"
        "</div>"
    )

def _jersey_html(p: dict, team_cls: str) -> str:
    num_txt = str(int(p.get("NUM", 0))) if int(p.get("NUM", 0)) < 999 else "?"
    cognome = _extract_surname(str(p.get("Giocatore", ""))) or str(p.get("Giocatore", ""))
    return (
        '<div class="jersey-card">'
        f'<div class="jersey-shape {team_cls}">{num_txt}</div>'
        f'<div class="jersey-name">{cognome}</div>'
        "</div>"
    )

def _half_court_col_html(starters: list[dict], team_cls: str) -> str:
    top_html = "".join(_jersey_html(p, team_cls) for p in starters[:2])
    mid_html = "".join(_jersey_html(p, team_cls) for p in starters[2:3])
    bot_html = "".join(_jersey_html(p, team_cls) for p in starters[3:5])
    return (
        '<div class="half-court-col">'
        f'<div class="half-row-top">{top_html}</div>'
        f'<div class="half-row-mid">{mid_html}</div>'
        f'<div class="half-row-bot">{bot_html}</div>'
        "</div>"
    )

court_svg = (
    '<svg class="court-svg-bg" viewBox="0 0 1000 520" preserveAspectRatio="none" xmlns="[http://www.w3.org/2000/svg](http://www.w3.org/2000/svg)">'
    '<rect x="0" y="0" width="1000" height="520" fill="#c86d3b"/>'
    '<line x1="500" y1="0" x2="500" y2="520" stroke="#ffffff" stroke-width="4"/>'
    '<circle cx="500" cy="260" r="68" fill="none" stroke="#ffffff" stroke-width="4"/>'
    '<rect x="0" y="165" width="180" height="190" fill="rgba(15, 23, 42, 0.22)" stroke="#ffffff" stroke-width="4"/>'
    '<circle cx="180" cy="260" r="56" fill="none" stroke="#ffffff" stroke-width="3.5"/>'
    '<path d="M 0 62 L 155 62 A 230 230 0 0 1 155 458 L 0 458" fill="none" stroke="#ffffff" stroke-width="4"/>'
    '<circle cx="54" cy="260" r="9" fill="none" stroke="#f59e0b" stroke-width="3.5"/>'
    '<line x1="42" y1="220" x2="42" y2="300" stroke="#ffffff" stroke-width="4"/>'
    '<rect x="820" y="165" width="180" height="190" fill="rgba(15, 23, 42, 0.22)" stroke="#ffffff" stroke-width="4"/>'
    '<circle cx="820" cy="260" r="56" fill="none" stroke="#ffffff" stroke-width="3.5"/>'
    '<path d="M 1000 62 L 845 62 A 230 230 0 0 0 845 458 L 1000 458" fill="none" stroke="#ffffff" stroke-width="4"/>'
    '<circle cx="946" cy="260" r="9" fill="none" stroke="#f59e0b" stroke-width="3.5"/>'
    '<line x1="958" y1="220" x2="958" y2="300" stroke="#ffffff" stroke-width="4"/>'
    "</svg>"
)

center_court_html = (
    '<div class="court-compact-wrap">'
    '<div class="court-stage">'
    f"{court_svg}"
    '<div class="court-players-layer">'
    f'{_half_court_col_html(h_starters, "jersey-home")}'
    f'{_half_court_col_html(a_starters, "jersey-away")}'
    "</div>"
    "</div>"
    "</div>"
)

full_html = (
    '<div class="formation-3col">'
    f"{_roster_col_html(home_name, h_starters, h_bench, is_right=False)}"
    f"{center_court_html}"
    f"{_roster_col_html(away_name, a_starters, a_bench, is_right=True)}"
    "</div>"
)
st.markdown(full_html, unsafe_allow_html=True)

```

def _render_team_history_column(
team_name: str,
label_side: str,
current_match_id: str,
current_round: int,
games_df: pd.DataFrame,
logo_html_map: dict[str, str],
) -> str:
logo_src = logo_html_map.get(f"raw_src::{team_name}", "")
logo_img = f'' if logo_src else "🏀"

```
prev_games = games_df[
    (games_df["ID_Partita"] != current_match_id)
    & ((games_df["Casa"] == team_name) | (games_df["Trasferta"] == team_name))
    & (games_df["Stato"].astype(str).str.strip().str.lower() == "giocata")
    & (games_df["Giornata"].astype(int) <= int(current_round))
].sort_values(by=["Giornata", "ID_Partita"])

items_html = []
for g in prev_games.itertuples(index=False):
    is_home = str(g.Casa) == team_name
    opp = str(g.Trasferta) if is_home else str(g.Casa)
    t_pts = int(g.Punti_Casa) if is_home else int(g.Punti_Trasferta)
    o_pts = int(g.Punti_Trasferta) if is_home else int(g.Punti_Casa)
    won = t_pts > o_pts
    badge_cls = "hist-badge-w" if won else "hist-badge-l"
    badge_txt = "V" if won else "P"
    place_tag = "Casa" if is_home else "Trasf."
    items_html.append(
        '<div class="hist-item">'
        f'<div class="{badge_cls}">{badge_txt} • G{int(g.Giornata)}</div>'
        f"<div><strong>{place_tag}</strong> vs {opp}</div>"
        f'<div class="hist-score">{int(g.Punti_Casa)} - {int(g.Punti_Trasferta)}</div>'
        "</div>"
    )

body_html = (
    "".join(items_html)
    if items_html
    else '<div style="color:#94a3b8;font-size:12.5px;">Nessuna partita disputata in precedenza.</div>'
)

return (
    '<div class="hist-col">'
    f'<div class="hist-col-head">{logo_img}<div>{label_side}: {team_name}</div></div>'
    f"{body_html}"
    "</div>"
)

```

def compute_team_player_stats(team_name: str, games_df: pd.DataFrame) -> pd.DataFrame:
played_ids = set(
games_df[
((games_df["Casa"] == team_name) | (games_df["Trasferta"] == team_name))
& (games_df["Stato"].astype(str).str.strip().str.lower() == "giocata")
]["ID_Partita"].astype(str)
)

```
agg: dict[str, dict] = {}
for g in games_df[(games_df["Casa"] == team_name) | (games_df["Trasferta"] == team_name)].itertuples(index=False):
    gid = str(g.ID_Partita)
    if gid not in played_ids:
        continue
    det = _get_match_detail(gid)
    plist = det["home_players"] if str(g.Casa) == team_name else det["away_players"]
    for p in plist:
        raw_name = str(p.get("Giocatore", "")).strip()
        if not raw_name:
            continue
        key = raw_name.lower()
        num_val = _extract_jersey_number(raw_name, p.get("NUM", None))
        if key not in agg:
            agg[key] = {
                "NUM": num_val,
                "Giocatore": raw_name,
                "G": 0,
                "PUN": 0,
                "2PT_R": 0,
                "2PT_T": 0,
                "3PT_R": 0,
                "3PT_T": 0,
                "TL_R": 0,
                "TL_T": 0,
                "RIM": 0,
                "ASS": 0,
                "F_C": 0,
                "VAL": 0,
            }
        elif agg[key]["NUM"] == 999 and num_val < 999:
            agg[key]["NUM"] = num_val

        agg[key]["G"] += 1
        agg[key]["PUN"] += int(p.get("PUN", 0))
        agg[key]["2PT_R"] += int(p.get("2PT_R", 0))
        agg[key]["2PT_T"] += int(p.get("2PT_T", 0))
        agg[key]["3PT_R"] += int(p.get("3PT_R", 0))
        agg[key]["3PT_T"] += int(p.get("3PT_T", 0))
        agg[key]["TL_R"] += int(p.get("TL_R", 0))
        agg[key]["TL_T"] += int(p.get("TL_T", 0))
        agg[key]["RIM"] += int(p.get("RIM_O", 0)) + int(p.get("RIM_D", 0))
        agg[key]["ASS"] += int(p.get("ASS", 0))
        agg[key]["F_C"] += int(p.get("F_C", 0))
        agg[key]["VAL"] += int(p.get("VAL", 0))

if not agg:
    return pd.DataFrame(
        columns=["NUM", "Giocatore", "G", "PUN", "PPG", "2PT_R", "2PT_T", "3PT_R", "3PT_T", "TL_R", "TL_T", "RIM", "ASS", "F_C", "VAL"]
    )

rows = []
for item in agg.values():
    g_cnt = max(int(item["G"]), 1)
    rows.append(
        {
            "NUM": int(item["NUM"]),
            "Giocatore": item["Giocatore"],
            "G": item["G"],
            "PUN": item["PUN"],
            "PPG": round(item["PUN"] / g_cnt, 1),
            "2PT_R": item["2PT_R"],
            "2PT_T": item["2PT_T"],
            "3PT_R": item["3PT_R"],
            "3PT_T": item["3PT_T"],
            "TL_R": item["TL_R"],
            "TL_T": item["TL_T"],
            "RIM": item["RIM"],
            "ASS": item["ASS"],
            "F_C": item["F_C"],
            "VAL": item["VAL"],
        }
    )
return pd.DataFrame(rows).sort_values(by=["PUN", "Giocatore"], ascending=[False, True]).reset_index(drop=True)

```

def _render_team_player_stats_html(team_name: str, p_df: pd.DataFrame) -> str:
html = [
'',
''
f"STATISTICHE GIOCATORI — {team_name}"
'ORDINATO PER PUNTI'
"",
''
"#"
'GIOCATORE'
"G"
'PUN'
'PPG'
"2PT R"
"2PT T"
"3PT R"
"3PT T"
"TL R"
"TL T"
"RIM"
"ASS"
"FALLI"
"VAL"
"",
]

```
for row in p_df.to_dict("records"):
    num_int = int(row.get("NUM", 999))
    num_disp = f"#{num_int}" if num_int < 999 else "—"
    html.append(
        "<tr>"
        f'<td class="num-col">{num_disp}</td>'
        f'<td class="name-col">{row.get("Giocatore", "")}</td>'
        f"<td>{int(row.get('G', 0))}</td>"
        f'<td class="pts-col">{int(row.get("PUN", 0))}</td>'
        f'<td class="pts-col">{float(row.get("PPG", 0.0)):.1f}</td>'
        f"<td>{int(row.get('2PT_R', 0))}</td>"
        f"<td>{int(row.get('2PT_T', 0))}</td>"
        f"<td>{int(row.get('3PT_R', 0))}</td>"
        f"<td>{int(row.get('3PT_T', 0))}</td>"
        f"<td>{int(row.get('TL_R', 0))}</td>"
        f"<td>{int(row.get('TL_T', 0))}</td>"
        f"<td>{int(row.get('RIM', 0))}</td>"
        f"<td>{int(row.get('ASS', 0))}</td>"
        f"<td>{int(row.get('F_C', 0))}</td>"
        f"<td>{int(row.get('VAL', 0))}</td>"
        "</tr>"
    )

html.append("</tbody></table></div></div>")
return "".join(html)

```

def _render_team_games_interactive_html(team_name: str, games_df: pd.DataFrame, logo_html_map: dict[str, str]) -> str:
team_games = games_df[(games_df["Casa"] == team_name) | (games_df["Trasferta"] == team_name)].sort_values(
by=["Giornata", "ID_Partita"]
)
parts = [
'',
''
'GIORNATA'
'SQUADRA DI CASA'
'RISULTATO'
'SQUADRA OSPITE'
"",
]

```
for g in team_games.itertuples(index=False):
    gid_encoded = quote(str(g.ID_Partita), safe="")
    is_played = str(g.Stato).strip().lower() == "giocata"
    r_num = int(g.Giornata)
    phase_txt = "Ritorno" if r_num > 11 else "Andata"
    disp_r = r_num - 11 if r_num > 11 else r_num

    tokens = str(g.Data).strip().split()
    if len(tokens) >= 3:
        date_str, time_str = tokens[1], tokens[2]
    elif len(tokens) == 2:
        date_str, time_str = tokens[0], tokens[1]
    else:
        date_str, time_str = str(g.Data).strip(), ""

    home_name = str(g.Casa)
    away_name = str(g.Trasferta)
    home_pts = int(g.Punti_Casa)
    away_pts = int(g.Punti_Trasferta)

    h_logo_src = logo_html_map.get(f"raw_src::{home_name}", "")
    a_logo_src = logo_html_map.get(f"raw_src::{away_name}", "")
    h_logo = f'<img class="cal-side-logo" src="{h_logo_src}" alt="" loading="lazy" />' if h_logo_src else "🏀"
    a_logo = f'<img class="cal-side-logo" src="{a_logo_src}" alt="" loading="lazy" />' if a_logo_src else "🏀"

    if is_played:
        h_win = home_pts > away_pts
        a_win = away_pts > home_pts
        h_cls = "cal-pts-win" if h_win else "cal-pts-lose"
        a_cls = "cal-pts-win" if a_win else "cal-pts-lose"
        score_html = (
            f'<div class="cal-score-line">'
            f'<span class="{h_cls}">{home_pts}</span>'
            f'<span style="color:#64748b;margin:0 3px;">-</span>'
            f'<span class="{a_cls}">{away_pts}</span>'
            f"</div>"
            f'<div class="cal-state-sub done">CONCLUSA</div>'
        )
    else:
        h_win = False
        a_win = False
        sub_txt = time_str if time_str else "DA GIOCARE"
        score_html = (
            '<div class="cal-score-line cal-pts-vs">VS</div>'
            f'<div class="cal-state-sub todo">{sub_txt}</div>'
        )

    parts.append(
        f'<a class="cal-row-link" href="?match={gid_encoded}" target="_self">'
        '<div class="cal-row-card">'
        '<div class="cal-round-col">'
        f'<div class="cal-round-league">{g.Girone}</div>'
        f'<div class="cal-round-num">{disp_r}ª Giornata • {phase_txt}</div>'
        f'<div class="cal-round-date">{date_str}</div>'
        "</div>"
        '<div class="cal-side-home">'
        f'<span class="cal-side-name {"win" if h_win else ""}">{home_name}</span>'
        f"{h_logo}"
        "</div>"
        f'<div class="cal-score-box">{score_html}</div>'
        '<div class="cal-side-away">'
        f"{a_logo}"
        f'<span class="cal-side-name {"win" if a_win else ""}">{away_name}</span>'
        "</div>"
        "</div>"
        "</a>"
    )

parts.append("</div>")
return "".join(parts)

```

def render_team_page(team_name: str, games_df: pd.DataFrame, logo_html_map: dict[str, str]) -> None:
st.markdown(MATCH_DETAIL_CSS, unsafe_allow_html=True)
st.markdown(STANDINGS_CSS, unsafe_allow_html=True)
st.markdown(CALENDAR_CSS, unsafe_allow_html=True)
st.markdown(TEAM_PAGE_CSS, unsafe_allow_html=True)

```
if st.button("← Torna alla classifica"):
    st.session_state["selected_team_name"] = None
    if "team" in st.query_params:
        del st.query_params["team"]
    st.rerun()

girone = _find_team_girone(team_name)
if not girone:
    st.warning(f"Squadra `{team_name}` non trovata.")
    return

board = compute_standings(girone, games_df)
pos = next((idx for idx, r in enumerate(board, start=1) if r["squadra"] == team_name), 0)
t_row = next((r for r in board if r["squadra"] == team_name), None)

hero_logo = logo_html_map.get(f"hero::{team_name}", '<div class="md-logo-box">🏀</div>')
diff_val = int(t_row["diff"]) if t_row else 0
diff_str = f"+{diff_val}" if diff_val > 0 else str(diff_val)

st.markdown(
    '<div class="team-hero">'
    f"{hero_logo}"
    "<div>"
    f'<div class="team-hero-title">{team_name}</div>'
    f'<div class="team-hero-sub">{girone} • Posizione attuale: #{pos}</div>'
    "</div>"
    "</div>",
    unsafe_allow_html=True,
)

if t_row:
    st.markdown(
        '<div class="kpi-grid">'
        f'<div class="kpi-card"><div class="kpi-label">Punti</div><div class="kpi-val">{t_row["pts"]}</div></div>'
        f'<div class="kpi-card"><div class="kpi-label">Giocate</div><div class="kpi-val">{t_row["p"]}</div></div>'
        f'<div class="kpi-card"><div class="kpi-label">Vittorie</div><div class="kpi-val">{t_row["w"]}</div></div>'
        f'<div class="kpi-card"><div class="kpi-label">Sconfitte</div><div class="kpi-val">{t_row["l"]}</div></div>'
        f'<div class="kpi-card"><div class="kpi-label">PF / PS</div><div class="kpi-val">{t_row["pf"]}/{t_row["ps"]}</div></div>'
        f'<div class="kpi-card"><div class="kpi-label">Diff</div><div class="kpi-val">{diff_str}</div></div>'
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown("**Forma recente (Streak):**")
    st.markdown(_render_streak_html(t_row.get("streak_events", [])), unsafe_allow_html=True)

if "team_flash_msg" in st.session_state:
    f_kind, f_txt = st.session_state.pop("team_flash_msg")
    if f_kind == "success":
        st.success(f_txt)
    else:
        st.warning(f_txt)

st.subheader("Statistiche Giocatori (da tabellini partita)")
p_df = compute_team_player_stats(team_name, games_df)
if p_df.empty:
    st.info("Nessun tabellino inserito ancora per questa squadra.")
else:
    st.markdown(_render_team_player_stats_html(team_name, p_df), unsafe_allow_html=True)

with st.expander("✏️ Modifica Numero di Maglia e Nome Cognome atleti", expanded=False):
    roster_edit_df = pd.DataFrame(
        [
            {
                "_orig_key": str(r["Giocatore"]).strip().lower(),
                "NUM": int(r["NUM"]) if int(r["NUM"]) < 999 else 0,
                "Giocatore": str(r["Giocatore"]),
            }
            for r in p_df.to_dict("records")
        ]
    )
    if roster_edit_df.empty:
        roster_edit_df = pd.DataFrame([{"_orig_key": "", "NUM": 0, "Giocatore": ""}])

    edited_roster = st.data_editor(
        roster_edit_df[["NUM", "Giocatore"]],
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "NUM": st.column_config.NumberColumn("# Maglia", min_value=0, max_value=99, step=1),
            "Giocatore": st.column_config.TextColumn("Nome Cognome"),
        },
        key=f"edit_roster_{team_name}",
    )

    if st.button("💾 Salva Nome e Numero su GitHub", key=f"save_roster_{team_name}"):
        orig_rows = roster_edit_df.to_dict("records")
        new_rows = edited_roster.to_dict("records")
        rename_map: dict[str, tuple[str, int]] = {}
        for idx_r, nr in enumerate(new_rows):
            new_name = str(nr.get("Giocatore", "") or "").strip()
            new_num = int(pd.to_numeric(nr.get("NUM", 0), errors="coerce") or 0)
            if not new_name:
                continue
            if idx_r < len(orig_rows) and orig_rows[idx_r].get("_orig_key"):
                rename_map[str(orig_rows[idx_r]["_orig_key"])] = (new_name, new_num)
            rename_map[new_name.lower()] = (new_name, new_num)

        store = st.session_state.get("match_details_store", {})
        team_gids = set(
            games_df[(games_df["Casa"] == team_name) | (games_df["Trasferta"] == team_name)]["ID_Partita"].astype(str)
        )
        last_ok = True
        last_msg = "Aggiornamento completato."

        for g in games_df[games_df["ID_Partita"].astype(str).isin(team_gids)].itertuples(index=False):
            gid = str(g.ID_Partita)
            if gid not in store or not isinstance(store[gid], dict):
                continue
            side_key = "home_players" if str(g.Casa) == team_name else "away_players"
            plist = _normalize_player_rows(store[gid].get(side_key))
            if not plist:
                continue
            changed = False
            for p in plist:
                pkey = str(p.get("Giocatore", "")).strip().lower()
                if pkey in rename_map:
                    upd_name, upd_num = rename_map[pkey]
                    p["Giocatore"] = upd_name
                    p["NUM"] = upd_num
                    changed = True
            if changed:
                updated_det = dict(store[gid])
                updated_det[side_key] = plist
                ok_s, msg_s, store = save_match_detail_persistent(gid, updated_det)
                last_ok = last_ok and ok_s
                last_msg = msg_s

        st.session_state["match_details_store"] = store
        st.session_state["team_flash_msg"] = ("success" if last_ok else "warning", last_msg)
        st.rerun()

st.subheader("Calendario e Risultati Squadra")
st.caption("Clicca su una partita per aprire direttamente tabellino, parziali e dettagli gara.")
st.markdown(_render_team_games_interactive_html(team_name, games_df, logo_html_map), unsafe_allow_html=True)

```

def render_match_detail(match_id: str, games_df: pd.DataFrame, logo_html_map: dict[str, str]) -> None:
st.markdown(MATCH_DETAIL_CSS, unsafe_allow_html=True)

```
if st.button("← Torna indietro"):
    st.session_state["selected_match_id"] = None
    if "match" in st.query_params:
        del st.query_params["match"]
    st.rerun()

rows = games_df[games_df["ID_Partita"] == match_id]
if rows.empty:
    st.warning(f"Partita `{match_id}` non trovata.")
    return

g = rows.iloc[0]
home_name = str(g["Casa"])
away_name = str(g["Trasferta"])
home_pts = int(g["Punti_Casa"])
away_pts = int(g["Punti_Trasferta"])
round_num = int(g["Giornata"])
is_played = str(g["Stato"]).strip().lower() == "giocata"
status_label = "FINALE" if is_played else str(g["Stato"]).upper()
is_our_game = OUR_TEAM in (home_name.strip(), away_name.strip())

h_hero_logo = logo_html_map.get(f"hero::{home_name}", '<div class="md-logo-box">🏀</div>')
a_hero_logo = logo_html_map.get(f"hero::{away_name}", '<div class="md-logo-box">🏀</div>')

score_text = f"{home_pts} - {away_pts}" if is_played else "VS"

st.markdown(
    '<div class="md-hero">'
    '<div class="md-grid">'
    f'<div class="md-team-block">{h_hero_logo}<div class="md-team-name">{home_name}</div></div>'
    '<div class="md-center">'
    f'<div class="md-date">{g["Data"]} • {g["Girone"]} (Giornata {round_num})</div>'
    f'<div class="md-score">{score_text}</div>'
    f'<div class="md-status">{status_label}</div>'
    "</div>"
    f'<div class="md-team-block">{a_hero_logo}<div class="md-team-name">{away_name}</div></div>'
    "</div>"
    "</div>",
    unsafe_allow_html=True,
)

with st.expander("✏️ Modifica data, ora e risultato partita (salvataggio permanente)", expanded=False):
    with st.form(f"edit_game_form_{match_id}"):
        c1, c2 = st.columns([2, 1])
        new_date = c1.text_input(
            "Data e Ora (es. Dom 29/11/2026 18:00)",
            value=str(g["Data"]),
        )
        stati_opts = ("Da giocare", "Giocata")
        curr_stato = str(g["Stato"]).strip()
        stato_idx = stati_opts.index(curr_stato) if curr_stato in stati_opts else 0
        new_stato = c2.selectbox("Stato gara", stati_opts, index=stato_idx)

        c3, c4 = st.columns(2)
        new_pts_h = c3.number_input(
            f"Punti {home_name}",
            min_value=0,
            max_value=250,
            value=home_pts,
            step=1,
        )
        new_pts_a = c4.number_input(
            f"Punti {away_name}",
            min_value=0,
            max_value=250,
            value=away_pts,
            step=1,
        )

        if st.form_submit_button("💾 Salva modifiche per sempre"):
            if new_stato == "Giocata" and int(new_pts_h) == int(new_pts_a):
                st.error("Nel basket una partita 'Giocata' non può terminare in parità.")
            else:
                payload = {
                    "Data": new_date.strip(),
                    "Stato": new_stato,
                    "Punti_Casa": int(new_pts_h),
                    "Punti_Trasferta": int(new_pts_a),
                }
                with st.spinner("Salvataggio su GitHub in corso..."):
                    ok, msg, updated_overrides = save_game_override_persistent(match_id, payload)
                st.session_state["game_overrides"] = updated_overrides
                st.session_state["games_df"] = apply_overrides_to_df(
                    build_games_df(DATA_VERSION).copy(), updated_overrides
                )
                if ok:
                    st.session_state["flash_msg"] = ("success", msg)
                else:
                    st.session_state["flash_msg"] = ("warning", msg)
                st.rerun()

if "flash_msg" in st.session_state:
    kind, text = st.session_state.pop("flash_msg")
    if kind == "success":
        st.success(text)
    else:
        st.warning(text)

detail = _get_match_detail(match_id)

sezioni_gara = st.radio(
    "Sezione partita",
    ("RIASSUNTO", "STATS GIOCATORE", "FORMAZIONI", "STORICO"),
    horizontal=True,
    label_visibility="collapsed",
    key=f"md_tab_{match_id}",
)

if sezioni_gara == "RIASSUNTO":
    q_h = detail["quarters_home"]
    q_a = detail["quarters_away"]
    ot_h = int(detail.get("ot_home", 0))
    ot_a = int(detail.get("ot_away", 0))
    has_ot = (ot_h > 0 or ot_a > 0)
    ot_th = "<th>OT</th>" if has_ot else ""
    ot_td_h = f"<td>{ot_h}</td>" if has_ot else ""
    ot_td_a = f"<td>{ot_a}</td>" if has_ot else ""

    st.markdown(
        '<div class="md-sec-card">'
        '<div class="md-sec-title">RISULTATO PARZIALE QUARTI</div>'
        '<table class="md-res-table">'
        f'<thead><tr><th class="team-col">SQUADRA</th><th>TOT</th><th>Q1</th><th>Q2</th><th>Q3</th><th>Q4</th>{ot_th}</tr></thead>'
        "<tbody>"
        f'<tr><td class="team-col">{home_name}</td><td class="tot-col">{home_pts}</td><td>{q_h[0]}</td><td>{q_h[1]}</td><td>{q_h[2]}</td><td>{q_h[3]}</td>{ot_td_h}</tr>'
        f'<tr><td class="team-col">{away_name}</td><td class="tot-col">{away_pts}</td><td>{q_a[0]}</td><td>{q_a[1]}</td><td>{q_a[2]}</td><td>{q_a[3]}</td>{ot_td_a}</tr>'
        "</tbody></table></div>",
        unsafe_allow_html=True,
    )
    with st.expander("✏️ Modifica parziali quarti"):
        qc = st.columns(5)
        nh = [qc[i].number_input(f"{home_name[:10]} Q{i+1}", min_value=0, max_value=80, value=int(q_h[i]), key=f"qh_{match_id}_{i}") for i in range(4)]
        not_h = qc[4].number_input("OT Casa", min_value=0, max_value=40, value=ot_h, key=f"oth_{match_id}")
        qc2 = st.columns(5)
        na = [qc2[i].number_input(f"{away_name[:10]} Q{i+1}", min_value=0, max_value=80, value=int(q_a[i]), key=f"qa_{match_id}_{i}") for i in range(4)]
        not_a = qc2[4].number_input("OT Trasf", min_value=0, max_value=40, value=ot_a, key=f"ota_{match_id}")
        if st.button("💾 Salva parziali su GitHub", key=f"save_q_{match_id}"):
            new_detail = dict(detail)
            new_detail["quarters_home"] = [int(x) for x in nh]
            new_detail["quarters_away"] = [int(x) for x in na]
            new_detail["ot_home"] = int(not_h)
            new_detail["ot_away"] = int(not_a)
            with st.spinner("Salvataggio parziali su GitHub..."):
                ok, msg, store = save_match_detail_persistent(match_id, new_detail)
            st.session_state["match_details_store"] = store
            st.session_state["flash_msg"] = ("success" if ok else "warning", msg)
            st.rerun()

    hp = _normalize_player_rows(detail["home_players"])
    ap = _normalize_player_rows(detail["away_players"])

    pts_tab_h = sum(int(p["PUN"]) for p in hp)
    pts_tab_a = sum(int(p["PUN"]) for p in ap)
    disp_pts_h = pts_tab_h if (is_our_game and hp) else home_pts
    disp_pts_a = pts_tab_a if (is_our_game and ap) else away_pts

    tl_r_h = sum(int(p["TL_R"]) for p in hp)
    tl_r_a = sum(int(p["TL_R"]) for p in ap)
    tl_t_h = sum(int(p["TL_T"]) for p in hp)
    tl_t_a = sum(int(p["TL_T"]) for p in ap)
    tl_sbag_h = max(tl_t_h - tl_r_h, 0)
    tl_sbag_a = max(tl_t_a - tl_r_a, 0)

    t2_r_h = sum(int(p["2PT_R"]) for p in hp)
    t2_r_a = sum(int(p["2PT_R"]) for p in ap)
    t3_r_h = sum(int(p["3PT_R"]) for p in hp)
    t3_r_a = sum(int(p["3PT_R"]) for p in ap)
    fc_h = sum(int(p["F_C"]) for p in hp)
    fc_a = sum(int(p["F_C"]) for p in ap)

    stat_rows = [
        {"Statistica": "Punti", home_name: disp_pts_h, away_name: disp_pts_a},
        {"Statistica": "Tiri liberi segnati", home_name: tl_r_h, away_name: tl_r_a},
        {"Statistica": "Tiri liberi sbagliati", home_name: tl_sbag_h, away_name: tl_sbag_a},
        {"Statistica": "2PT segnati", home_name: t2_r_h, away_name: t2_r_a},
        {"Statistica": "3PT segnati", home_name: t3_r_h, away_name: t3_r_a},
        {"Statistica": "Falli fatti", home_name: fc_h, away_name: fc_a},
    ]
    if is_our_game:
        rim_h = sum(int(p["RIM_O"]) + int(p["RIM_D"]) for p in hp)
        rim_a = sum(int(p["RIM_O"]) + int(p["RIM_D"]) for p in ap)
        ass_h = sum(int(p["ASS"]) for p in hp)
        ass_a = sum(int(p["ASS"]) for p in ap)
        stat_rows.extend([
            {"Statistica": "Rimbalzi totali", home_name: rim_h, away_name: rim_a},
            {"Statistica": "Assist", home_name: ass_h, away_name: ass_a},
        ])

    st.markdown('<div class="md-sec-card"><div class="md-sec-title">STATISTICHE DI SQUADRA</div>', unsafe_allow_html=True)
    st.table(pd.DataFrame(stat_rows))
    st.markdown("</div>", unsafe_allow_html=True)

elif sezioni_gara == "STATS GIOCATORE":
    if not is_our_game:
        st.caption(
            f"Tabellino essenziale per le gare senza {OUR_TEAM} (mantenuta solo la % dei tiri liberi; "
            "nascoste falli subiti, tentativi 2PT/3PT, % da 2, rimbalzi, stoppate, palle perse/recuperate e valutazione)."
        )

    render_lba_boxscore(home_name, detail["coach_home"], detail["home_players"], logo_html_map, full_stats=is_our_game)
    render_lba_boxscore(away_name, detail["coach_away"], detail["away_players"], logo_html_map, full_stats=is_our_game)

    with st.expander("✏️ Modifica tabellini giocatori e allenatori (salvataggio permanente)", expanded=False):
        c_ch, c_ca = st.columns(2)
        new_coach_h = c_ch.text_input(f"Allenatore {home_name}", value=detail["coach_home"], key=f"coach_h_{match_id}")
        new_coach_a = c_ca.text_input(f"Allenatore {away_name}", value=detail["coach_away"], key=f"coach_a_{match_id}")

        tab_h, tab_a = st.tabs([home_name, away_name])
        with tab_h:
            edited_h = st.data_editor(
                _players_to_editor_df(detail["home_players"], full_stats=is_our_game),
                num_rows="dynamic",
                use_container_width=True,
                key=f"editor_h_{match_id}",
            )
        with tab_a:
            edited_a = st.data_editor(
                _players_to_editor_df(detail["away_players"], full_stats=is_our_game),
                num_rows="dynamic",
                use_container_width=True,
                key=f"editor_a_{match_id}",
            )

        if st.button("💾 Salva tabellini su GitHub", key=f"save_box_{match_id}"):
            new_detail = dict(detail)
            new_detail["coach_home"] = new_coach_h.strip()
            new_detail["coach_away"] = new_coach_a.strip()
            new_detail["home_players"] = _editor_df_to_players(edited_h, detail["home_players"])
            new_detail["away_players"] = _editor_df_to_players(edited_a, detail["away_players"])

            if is_our_game:
                sum_h = sum(int(p["PUN"]) for p in new_detail["home_players"])
                sum_a = sum(int(p["PUN"]) for p in new_detail["away_players"])
                if sum_h > 0 or sum_a > 0:
                    ov_payload = {
                        "Data": str(g["Data"]),
                        "Stato": "Giocata" if sum_h != sum_a else str(g["Stato"]),
                        "Punti_Casa": int(sum_h),
                        "Punti_Trasferta": int(sum_a),
                    }
                    _, _, updated_ov = save_game_override_persistent(match_id, ov_payload)
                    st.session_state["game_overrides"] = updated_ov
                    st.session_state["games_df"] = apply_overrides_to_df(
                        build_games_df(DATA_VERSION).copy(), updated_ov
                    )

            with st.spinner("Salvataggio tabellini su GitHub..."):
                ok, msg, store = save_match_detail_persistent(match_id, new_detail)
            st.session_state["match_details_store"] = store
            st.session_state["flash_msg"] = ("success" if ok else "warning", msg)
            st.rerun()

elif sezioni_gara == "FORMAZIONI":
    st.markdown('<div class="md-sec-card"><div class="md-sec-title">FORMAZIONI IN CAMPO</div>', unsafe_allow_html=True)
    _render_court_formation(
        home_name=home_name,
        away_name=away_name,
        home_players=detail["home_players"],
        away_players=detail["away_players"],
        logo_html_map=logo_html_map,
    )
    st.markdown("</div>", unsafe_allow_html=True)

elif sezioni_gara == "STORICO":
    st.markdown('<div class="md-sec-card"><div class="md-sec-title">STORICO PARTITE PRECEDENTI</div>', unsafe_allow_html=True)
    hist_html = (
        '<div class="hist-grid">'
        f'{_render_team_history_column(home_name, "CASA", match_id, round_num, games_df, logo_html_map)}'
        f'{_render_team_history_column(away_name, "TRASFERTA", match_id, round_num, games_df, logo_html_map)}'
        "</div>"
    )
    st.markdown(hist_html, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

```

def render_calendar_page(girone: str, games_df: pd.DataFrame, logo_html_map: dict[str, str]) -> None:
st.markdown(CALENDAR_CSS, unsafe_allow_html=True)

```
g_games = games_df[games_df["Girone"] == girone].copy()
if g_games.empty:
    st.info(f"Nessuna partita disponibile per {girone}.")
    return

all_rounds = sorted(g_games["Giornata"].astype(int).unique().tolist())
andata_rounds = [r for r in all_rounds if r <= 11]
ritorno_rounds = [r for r in all_rounds if r > 11]

round_options = ["Tutte le giornate"] + [f"{r}ª Giornata" for r in all_rounds]
selected_round = st.selectbox(
    "Filtra per giornata",
    round_options,
    index=0,
    key=f"cal_round_{girone}",
)

if selected_round == "Tutte le giornate":
    col_andata, col_ritorno = st.columns(2, gap="medium")

    with col_andata:
        st.markdown('<div class="cal-phase-hdr">⬆️ GIRONE DI ANDATA (SINISTRA)</div>', unsafe_allow_html=True)
        for r in andata_rounds:
            r_df = g_games[g_games["Giornata"].astype(int) == r].sort_values(by=["Data", "ID_Partita"])
            st.markdown(
                build_round_html(r, r_df, logo_html_map, is_ritorno=False, girone_label=girone),
                unsafe_allow_html=True,
            )

    with col_ritorno:
        st.markdown('<div class="cal-phase-hdr">⬇️ GIRONE DI RITORNO (DESTRA)</div>', unsafe_allow_html=True)
        for r in ritorno_rounds:
            r_df = g_games[g_games["Giornata"].astype(int) == r].sort_values(by=["Data", "ID_Partita"])
            st.markdown(
                build_round_html(r, r_df, logo_html_map, is_ritorno=True, girone_label=girone),
                unsafe_allow_html=True,
            )
else:
    r_num = int(selected_round.split("ª")[0])
    is_rit = r_num > 11
    r_df = g_games[g_games["Giornata"].astype(int) == r_num].sort_values(by=["Data", "ID_Partita"])
    col_andata, col_ritorno = st.columns(2, gap="medium")
    if not is_rit:
        with col_andata:
            st.markdown('<div class="cal-phase-hdr">⬆️ GIRONE DI ANDATA</div>', unsafe_allow_html=True)
            st.markdown(build_round_html(r_num, r_df, logo_html_map, is_ritorno=False, girone_label=girone), unsafe_allow_html=True)
        with col_ritorno:
            st.markdown('<div class="cal-phase-hdr">⬇️ GIRONE DI RITORNO</div>', unsafe_allow_html=True)
            st.info("Giornata di ritorno non selezionata.")
    else:
        with col_andata:
            st.markdown('<div class="cal-phase-hdr">⬆️ GIRONE DI ANDATA</div>', unsafe_allow_html=True)
            st.info("Giornata di andata non selezionata.")
        with col_ritorno:
            st.markdown('<div class="cal-phase-hdr">⬇️ GIRONE DI RITORNO</div>', unsafe_allow_html=True)
            st.markdown(build_round_html(r_num, r_df, logo_html_map, is_ritorno=True, girone_label=girone), unsafe_allow_html=True)

```

# ==========================================

# APPLICAZIONE PRINCIPALE

# ==========================================

def main() -> None:
st.markdown(GLOBAL_UI_CSS, unsafe_allow_html=True)

```
if "match_details_store" not in st.session_state:
    st.session_state["match_details_store"] = load_match_details_store()

if "games_df" not in st.session_state:
    st.session_state["games_df"] = load_full_games_df()

games_df: pd.DataFrame = st.session_state["games_df"]
logo_html_map = build_team_logo_html_map(GITHUB_RAW_BASE)

qp = st.query_params
match_param = qp.get("match")
team_param = qp.get("team")

if match_param:
    st.session_state["selected_match_id"] = str(match_param)
if team_param and not match_param:
    st.session_state["selected_team_name"] = str(team_param)

st.markdown(
    '<div class="topbar-card">'
    '<div class="topbar-title">🏀 DR2 Puglia — Classifiche e Calendario</div>'
    '<div class="topbar-sub">Stagione 2026/2027 • Gironi A, B e C • Clicca su una gara o una squadra per i dettagli</div>'
    "</div>",
    unsafe_allow_html=True,
)

selected_match = st.session_state.get("selected_match_id")
if selected_match:
    render_match_detail(str(selected_match), games_df, logo_html_map)
    return

selected_team = st.session_state.get("selected_team_name")
if selected_team:
    render_team_page(str(selected_team), games_df, logo_html_map)
    return

with st.sidebar:
    st.header("Navigazione")
    girone = st.selectbox(
        "Seleziona Girone",
        ("Girone A", "Girone B", "Girone C"),
        index=0,
    )
    sezione = st.radio(
        "Sezione",
        ("Classifica", "Calendario"),
        index=0,
    )
    st.divider()
    cfg = _get_github_config()
    if cfg["token"]:
        st.caption(f"Persistenza GitHub attiva ({cfg['owner']}/{cfg['repo']}@{cfg['branch']}).")
    else:
        st.caption("Modalità locale / sessione (imposta GITHUB_TOKEN per salvare su GitHub).")

if sezione == "Classifica":
    board_rows = compute_standings(girone, games_df)
    thirds_board = compute_thirds_standings(games_df)
    render_standings(girone, board_rows, thirds_board, logo_html_map)
else:
    render_calendar_page(girone, games_df, logo_html_map)

```

if **name** == "**main**":
main()
