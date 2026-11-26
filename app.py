# ... existing code ...
DATA_VERSION = "2026-11-26-v18-jersey-zero-all-views"
OUR_TEAM = "New Virtus Basket Toritto"
# ... existing code ...
    ("C22_2328", "Girone C", 22, "Dom 25/04/2027 17:00", "ASD BELLFIKA MESAGNE", "ASD NEW BASKET CARMIANO", 0, 0, "Da giocare"),
]
def _to_safe_int(val: object, default: int = 0) -> int:
    """Converte in modo sicuro un valore generico in int senza sollevare eccezioni."""
    try:
        if val is None or isinstance(val, (bool, list, tuple, dict, set)):
            return int(default)
        if isinstance(val, float) and pd.isna(val):
            return int(default)
        if isinstance(val, str):
            s = val.strip()
            if not s or s.lower() in {"nan", "none", "null", "—", "-", "?"}:
                return int(default)
            parsed = pd.to_numeric(s, errors="coerce")
            return int(float(parsed)) if pd.notna(parsed) else int(default)
        parsed = pd.to_numeric(val, errors="coerce")
        return int(float(parsed)) if pd.notna(parsed) else int(default)
    except Exception:
        return int(default)
def _extract_jersey_number(name: object = "", explicit_num: object = None) -> int:
    """Estrae o valida un numero di maglia valido (0-99); restituisce 999 se assente o non valido."""
    try:
        if explicit_num is not None and not isinstance(explicit_num, (bool, list, tuple, dict, set)):
            if not (isinstance(explicit_num, float) and pd.isna(explicit_num)):
                raw_s = str(explicit_num).strip()
                if raw_s and raw_s.lower() not in {"nan", "none", "null", "—", "-", "?"}:
                    cleaned = raw_s.lstrip("#").strip()
                    parsed = pd.to_numeric(cleaned, errors="coerce")
                    if pd.notna(parsed):
                        num_i = int(float(parsed))
                        if 0 <= num_i <= 99:
                            return num_i
    except Exception:
        pass
    try:
        name_s = "" if name is None else str(name)
        match = re.match(r"^\s*#?(\d{1,2})\b", name_s)
        if match:
            num_i = int(match.group(1))
            if 0 <= num_i <= 99:
                return num_i
    except Exception:
        pass
    return 999
def _format_jersey_display(
    num_val: object = None,
    empty_placeholder: str = "—",
    prefix: str = "#",
) -> str:
    """Formatta un numero di maglia valido (0-99, incluso 0 -> '#0') o restituisce empty_placeholder."""
    placeholder = "" if empty_placeholder is None else str(empty_placeholder)
    pfx = "" if prefix is None else str(prefix)
    try:
        if num_val is None or isinstance(num_val, (bool, list, tuple, dict, set)):
            return placeholder
        if isinstance(num_val, float) and pd.isna(num_val):
            return placeholder
        if isinstance(num_val, str):
            raw_s = num_val.strip()
            if not raw_s or raw_s.lower() in {"nan", "none", "null", "—", "-", "?"}:
                return placeholder
            cleaned = raw_s.lstrip("#").strip()
            parsed = pd.to_numeric(cleaned, errors="coerce")
        else:
            parsed = pd.to_numeric(num_val, errors="coerce")
        if pd.isna(parsed):
            return placeholder
        num_i = int(float(parsed))
        if 0 <= num_i <= 99:
            return f"{pfx}{num_i}"
        return placeholder
    except Exception:
        return placeholder
def _format_jersey_badge(
    num_val: object = None,
    empty_placeholder: str = "—",
    css_class: str = "num-badge",
) -> str:
    """Restituisce l'HTML di un badge per il numero di maglia o stringa vuota se non disponibile."""
    disp = _format_jersey_display(num_val=num_val, empty_placeholder=empty_placeholder, prefix="#")
    if disp == "":
        return ""
    cls_safe = re.sub(r"[^A-Za-z0-9_-]", "", str(css_class or "num-badge")) or "num-badge"
    disp_safe = disp.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f'<span class="{cls_safe}">{disp_safe}</span>'
def _p_row(
# ... existing code ...
    resolved_num = _extract_jersey_number(str(giocatore), numero)
    return {
        "Giocatore": str(giocatore),
        "NUM": int(resolved_num),
        "PUN": _to_safe_int(pts, 0),
        "MIN": str(minuti),
        "SF": bool(sf),
        "F_C": _to_safe_int(falli_c, 0),
        "F_S": _to_safe_int(falli_s, 0),
        "2PT_R": _to_safe_int(t2_r, 0),
        "2PT_T": _to_safe_int(t2_t, 0),
        "SC": _to_safe_int(sc, 0),
        "3PT_R": _to_safe_int(t3_r, 0),
        "3PT_T": _to_safe_int(t3_t, 0),
        "TL_R": _to_safe_int(tl_r, 0),
        "TL_T": _to_safe_int(tl_t, 0),
        "RIM_O": _to_safe_int(rim_o, 0),
        "RIM_D": _to_safe_int(rim_d, 0),
        "ST_D": _to_safe_int(st_d, 0),
        "ST_S": _to_safe_int(st_s, 0),
        "PAL_P": _to_safe_int(pal_p, 0),
        "PAL_R": _to_safe_int(pal_r, 0),
        "ASS": _to_safe_int(ass, 0),
        "VAL": _to_safe_int(val_lega, 0),
        "OER": float(_to_safe_int(oer, 0)) if isinstance(oer, bool) else float(pd.to_numeric(oer, errors="coerce") or 0.0),
    }
DEFAULT_ROUND3_DETAILS: dict[str, dict] = {
# ... existing code ...
def _extract_surname(full_name: str) -> str:
    try:
        cleaned = re.sub(r"\s*\(N\.E\.\)\s*$", "", str(full_name or ""), flags=re.IGNORECASE).strip()
        cleaned = re.sub(r"^\s*#?\d{1,2}\s*[-–.]?\s*", "", cleaned).strip()
        if not cleaned:
            return ""
        parts = cleaned.split()
        if len(parts) == 1:
            return parts[0]
        if len(parts[-1]) <= 2 and len(parts[0]) > 2:
            return parts[0]
        return parts[-1]
    except Exception:
        return str(full_name or "").strip()
def _normalize_player_rows(rows: list | None) -> list[dict]:
    if not isinstance(rows, list):
        return []
    out: list[dict] = []
    for item in rows:
        if not isinstance(item, dict):
            continue
        name = str(item.get("Giocatore", "") or "").strip()
        if not name:
            continue
        try:
            pts_val = item.get("PUN", item.get("PTS", 0))
            t2_r_val = item.get("2PT_R", item.get("2PT", 0))
            t2_r_int = _to_safe_int(t2_r_val, 0)
            t2_t_val = item.get("2PT_T", max(t2_r_int, 0))
            t3_r_val = item.get("3PT_R", item.get("3PT", 0))
            t3_r_int = _to_safe_int(t3_r_val, 0)
            t3_t_val = item.get("3PT_T", max(t3_r_int, 0))
            tl_r_val = item.get("TL_R", 0)
            tl_r_int = _to_safe_int(tl_r_val, 0)
            tl_sbag_val = item.get("TL_SBAG", 0)
            tl_t_default = tl_r_int + _to_safe_int(tl_sbag_val, 0)
            tl_t_val = item.get("TL_T", tl_t_default)
            fc_val = item.get("F_C", item.get("FALLI", 0))
            sf_val = item.get("SF", item.get("QUINTETTO", False))
            raw_num_field = item.get("NUM", item.get("MAGLIA", None))
            num_val = _extract_jersey_number(name, raw_num_field)
            out.append(
                {
                    "Giocatore": name,
                    "NUM": int(num_val),
                    "PUN": _to_safe_int(pts_val, 0),
                    "MIN": str(item.get("MIN", "0") or "0").strip(),
                    "SF": bool(sf_val),
                    "F_C": _to_safe_int(fc_val, 0),
                    "F_S": _to_safe_int(item.get("F_S", 0), 0),
                    "2PT_R": t2_r_int,
                    "2PT_T": max(_to_safe_int(t2_t_val, 0), t2_r_int),
                    "SC": _to_safe_int(item.get("SC", 0), 0),
                    "3PT_R": t3_r_int,
                    "3PT_T": max(_to_safe_int(t3_t_val, 0), t3_r_int),
                    "TL_R": tl_r_int,
                    "TL_T": max(_to_safe_int(tl_t_val, 0), tl_r_int),
                    "RIM_O": _to_safe_int(item.get("RIM_O", 0), 0),
                    "RIM_D": _to_safe_int(item.get("RIM_D", 0), 0),
                    "ST_D": _to_safe_int(item.get("ST_D", 0), 0),
                    "ST_S": _to_safe_int(item.get("ST_S", 0), 0),
                    "PAL_P": _to_safe_int(item.get("PAL_P", 0), 0),
                    "PAL_R": _to_safe_int(item.get("PAL_R", 0), 0),
                    "ASS": _to_safe_int(item.get("ASS", 0), 0),
                    "VAL": _to_safe_int(item.get("VAL", 0), 0),
                    "OER": float(pd.to_numeric(item.get("OER", 0.0), errors="coerce") or 0.0),
                }
            )
        except Exception:
            continue
    return out
# ... existing code ...
def _players_to_editor_df(player_list: list[dict], full_stats: bool = True, min_rows: int = 8) -> pd.DataFrame:
    rows = _normalize_player_rows(player_list)
    while len(rows) < min_rows:
        rows.append(_p_row(""))
    df = pd.DataFrame(rows)
    if "NUM" in df.columns:
        df["NUM"] = df["NUM"].apply(lambda v: _to_safe_int(v, 999))
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
        try:
            name = str(getattr(r, "Giocatore", "") or "").strip()
            if not name:
                continue
            prev = existing_by_name.get(name.lower(), {})
            r2_val = _to_safe_int(getattr(r, "2PT_R", prev.get("2PT_R", 0)), 0)
            t2_val = max(_to_safe_int(getattr(r, "2PT_T", prev.get("2PT_T", r2_val)), r2_val), r2_val)
            r3_val = _to_safe_int(getattr(r, "3PT_R", prev.get("3PT_R", 0)), 0)
            t3_val = max(_to_safe_int(getattr(r, "3PT_T", prev.get("3PT_T", r3_val)), r3_val), r3_val)
            tl_r_val = _to_safe_int(getattr(r, "TL_R", prev.get("TL_R", 0)), 0)
            tl_t_val = max(_to_safe_int(getattr(r, "TL_T", prev.get("TL_T", tl_r_val)), tl_r_val), tl_r_val)
            raw_num = getattr(r, "NUM", None)
            resolved_num = _extract_jersey_number(name, raw_num)
            if resolved_num == 999 and prev:
                prev_num = _extract_jersey_number(name, prev.get("NUM", None))
                if prev_num != 999:
                    resolved_num = prev_num
            out.append(
                _p_row(
                    giocatore=name,
                    numero=resolved_num,
                    pts=_to_safe_int(getattr(r, "PUN", prev.get("PUN", 0)), 0),
                    minuti=str(getattr(r, "MIN", prev.get("MIN", "0")) or "0").strip(),
                    sf=bool(getattr(r, "SF", prev.get("SF", False))),
                    falli_c=_to_safe_int(getattr(r, "F_C", prev.get("F_C", 0)), 0),
                    falli_s=_to_safe_int(getattr(r, "F_S", prev.get("F_S", 0)), 0),
                    t2_r=r2_val,
                    t2_t=t2_val,
                    sc=_to_safe_int(getattr(r, "SC", prev.get("SC", 0)), 0),
                    t3_r=r3_val,
                    t3_t=t3_val,
                    tl_r=tl_r_val,
                    tl_t=tl_t_val,
                    rim_o=_to_safe_int(getattr(r, "RIM_O", prev.get("RIM_O", 0)), 0),
                    rim_d=_to_safe_int(getattr(r, "RIM_D", prev.get("RIM_D", 0)), 0),
                    st_d=_to_safe_int(getattr(r, "ST_D", prev.get("ST_D", 0)), 0),
                    st_s=_to_safe_int(getattr(r, "ST_S", prev.get("ST_S", 0)), 0),
                    pal_p=_to_safe_int(getattr(r, "PAL_P", prev.get("PAL_P", 0)), 0),
                    pal_r=_to_safe_int(getattr(r, "PAL_R", prev.get("PAL_R", 0)), 0),
                    ass=_to_safe_int(getattr(r, "ASS", prev.get("ASS", 0)), 0),
                    val_lega=_to_safe_int(getattr(r, "VAL", prev.get("VAL", 0)), 0),
                    oer=float(pd.to_numeric(getattr(r, "OER", prev.get("OER", 0.0)), errors="coerce") or 0.0),
                )
            )
        except Exception:
            continue
    return out
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
        '<div class="lba-team-logo" style="display:flex;align-items:center;justify-content:center;font-size:22px;">🏀</div>',
    )
    allenatore_txt = str(coach_name or "").strip() if str(coach_name or "").strip() else "—"
    badge_txt = "STATISTICHE DETTAGLIATE" if full_stats else "TABELLINO ESSENZIALE"
    table_cls = "lba-box full-stats" if full_stats else "lba-box compact-stats"
# ... existing code ...
    for p in norm_players:
        try:
            player_label = str(p.get("Giocatore", "") or "").strip()
            if not player_label:
                continue
            pun = _to_safe_int(p.get("PUN", 0), 0)
            min_str = str(p.get("MIN", "0") or "0").strip() or "0"
            sf_mark = "✓" if bool(p.get("SF", False)) else ""
            fc = _to_safe_int(p.get("F_C", 0), 0)
            fs = _to_safe_int(p.get("F_S", 0), 0)
            r2 = _to_safe_int(p.get("2PT_R", 0), 0)
            t2 = _to_safe_int(p.get("2PT_T", 0), 0)
            sc = _to_safe_int(p.get("SC", 0), 0)
            r3 = _to_safe_int(p.get("3PT_R", 0), 0)
            t3 = _to_safe_int(p.get("3PT_T", 0), 0)
            rtl = _to_safe_int(p.get("TL_R", 0), 0)
            ttl = _to_safe_int(p.get("TL_T", 0), 0)
            ro = _to_safe_int(p.get("RIM_O", 0), 0)
            rd = _to_safe_int(p.get("RIM_D", 0), 0)
            rt = ro + rd
            sd = _to_safe_int(p.get("ST_D", 0), 0)
            ss = _to_safe_int(p.get("ST_S", 0), 0)
            pp = _to_safe_int(p.get("PAL_P", 0), 0)
            pr = _to_safe_int(p.get("PAL_R", 0), 0)
            ass = _to_safe_int(p.get("ASS", 0), 0)
            val_l = _to_safe_int(p.get("VAL", 0), 0)
            oer_raw = float(pd.to_numeric(p.get("OER", 0.0), errors="coerce") or 0.0)
            oer_v = f"{oer_raw:.1f}" if oer_raw != 0 else "0"
            raw_num = p.get("NUM", None)
            num_badge = _format_jersey_badge(
                num_val=raw_num if raw_num is not None else _extract_jersey_number(player_label, None),
                empty_placeholder="",
                css_class="num-badge",
            )
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
            player_safe = player_label.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            if full_stats:
                html.append(
                    "<tr>"
                    f'<td class="player-name">{num_badge}{player_safe}</td>'
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
                    f'<td class="player-name">{num_badge}{player_safe}</td>'
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
        except Exception:
            continue
    if full_stats:
# ... existing code ...
def _render_court_formation(
    home_name: str,
    away_name: str,
    home_players: list[dict],
    away_players: list[dict],
    logo_html_map: dict[str, str],
) -> None:
    def _prepare_roster(plist: list[dict] | None) -> tuple[list[dict], list[dict]]:
        norm = sorted(
            _normalize_player_rows(plist),
            key=lambda x: (_extract_jersey_number(x.get("Giocatore", ""), x.get("NUM", 999)), str(x.get("Giocatore", ""))),
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
            key=lambda x: (_extract_jersey_number(x.get("Giocatore", ""), x.get("NUM", 999)), str(x.get("Giocatore", ""))),
        )
        five_ids = {id(p) for p in starters_five}
        bench = [p for p in norm if id(p) not in five_ids]
        return starters_five, bench
    h_starters, h_bench = _prepare_roster(home_players)
    a_starters, a_bench = _prepare_roster(away_players)
    def _roster_col_html(team_name: str, starters: list[dict], bench: list[dict], is_right: bool = False) -> str:
        logo_src = logo_html_map.get(f"raw_src::{team_name}", "")
        logo_img = f'<img src="{logo_src}" alt="" />' if logo_src else "🏀"
        align_style = ' style="justify-content:flex-end;text-align:right;"' if is_right else ""
        def _line(p: dict, is_st: bool) -> str:
            p_name = str(p.get("Giocatore", "") or "").strip()
            num_val = p.get("NUM", None)
            num_txt = _format_jersey_display(
                num_val=num_val if num_val is not None else _extract_jersey_number(p_name, None),
                empty_placeholder="?",
                prefix="",
            )
            cls_st = " starter" if is_st else ""
            p_name_safe = p_name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            return (
                f'<div class="roster-player-line{cls_st}">'
                f'<span class="roster-num-pill">{num_txt}</span>'
                f"<span>{p_name_safe}</span>"
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
        p_name = str(p.get("Giocatore", "") or "").strip()
        num_val = p.get("NUM", None)
        num_txt = _format_jersey_display(
            num_val=num_val if num_val is not None else _extract_jersey_number(p_name, None),
            empty_placeholder="?",
            prefix="",
        )
        cognome = _extract_surname(p_name) or p_name
        cognome_safe = cognome.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return (
            '<div class="jersey-card">'
            f'<div class="jersey-shape {team_cls}">{num_txt}</div>'
            f'<div class="jersey-name">{cognome_safe}</div>'
            "</div>"
        )
# ... existing code ...
def compute_team_player_stats(team_name: str, games_df: pd.DataFrame) -> pd.DataFrame:
    played_ids = set(
        games_df[
            ((games_df["Casa"] == team_name) | (games_df["Trasferta"] == team_name))
            & (games_df["Stato"].astype(str).str.strip().str.lower() == "giocata")
        ]["ID_Partita"].astype(str)
    )
    agg: dict[str, dict] = {}
    for g in games_df[(games_df["Casa"] == team_name) | (games_df["Trasferta"] == team_name)].itertuples(index=False):
        gid = str(g.ID_Partita)
        if gid not in played_ids:
            continue
        det = _get_match_detail(gid)
        plist = _normalize_player_rows(det.get("home_players") if str(g.Casa) == team_name else det.get("away_players"))
        for p in plist:
            raw_name = str(p.get("Giocatore", "") or "").strip()
            if not raw_name:
                continue
            key = raw_name.lower()
            num_val = _extract_jersey_number(raw_name, p.get("NUM", None))
            if key not in agg:
                agg[key] = {
                    "NUM": int(num_val),
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
            else:
                if num_val != 999:
                    agg[key]["NUM"] = int(num_val)
            agg[key]["G"] += 1
            agg[key]["PUN"] += _to_safe_int(p.get("PUN", 0), 0)
            agg[key]["2PT_R"] += _to_safe_int(p.get("2PT_R", 0), 0)
            agg[key]["2PT_T"] += _to_safe_int(p.get("2PT_T", 0), 0)
            agg[key]["3PT_R"] += _to_safe_int(p.get("3PT_R", 0), 0)
            agg[key]["3PT_T"] += _to_safe_int(p.get("3PT_T", 0), 0)
            agg[key]["TL_R"] += _to_safe_int(p.get("TL_R", 0), 0)
            agg[key]["TL_T"] += _to_safe_int(p.get("TL_T", 0), 0)
            agg[key]["RIM"] += _to_safe_int(p.get("RIM_O", 0), 0) + _to_safe_int(p.get("RIM_D", 0), 0)
            agg[key]["ASS"] += _to_safe_int(p.get("ASS", 0), 0)
            agg[key]["F_C"] += _to_safe_int(p.get("F_C", 0), 0)
            agg[key]["VAL"] += _to_safe_int(p.get("VAL", 0), 0)
    if not agg:
        return pd.DataFrame(
            columns=["NUM", "Giocatore", "G", "PUN", "PPG", "2PT_R", "2PT_T", "3PT_R", "3PT_T", "TL_R", "TL_T", "RIM", "ASS", "F_C", "VAL"]
        )
    rows = []
    for item in agg.values():
        g_cnt = max(_to_safe_int(item.get("G", 1), 1), 1)
        pun_tot = _to_safe_int(item.get("PUN", 0), 0)
        rows.append(
            {
                "NUM": _extract_jersey_number(item.get("Giocatore", ""), item.get("NUM", 999)),
                "Giocatore": str(item.get("Giocatore", "")),
                "G": g_cnt,
                "PUN": pun_tot,
                "PPG": round(pun_tot / g_cnt, 1),
                "2PT_R": _to_safe_int(item.get("2PT_R", 0), 0),
                "2PT_T": _to_safe_int(item.get("2PT_T", 0), 0),
                "3PT_R": _to_safe_int(item.get("3PT_R", 0), 0),
                "3PT_T": _to_safe_int(item.get("3PT_T", 0), 0),
                "TL_R": _to_safe_int(item.get("TL_R", 0), 0),
                "TL_T": _to_safe_int(item.get("TL_T", 0), 0),
                "RIM": _to_safe_int(item.get("RIM", 0), 0),
                "ASS": _to_safe_int(item.get("ASS", 0), 0),
                "F_C": _to_safe_int(item.get("F_C", 0), 0),
                "VAL": _to_safe_int(item.get("VAL", 0), 0),
            }
        )
    return pd.DataFrame(rows).sort_values(by=["PUN", "Giocatore"], ascending=[False, True]).reset_index(drop=True)
def _render_team_player_stats_html(team_name: str, p_df: pd.DataFrame | None = None) -> str:
    safe_team = str(team_name or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    html = [
        '<div class="tp-stats-card">',
        '<div class="tp-stats-head">'
        f"<span>STATISTICHE GIOCATORI — {safe_team}</span>"
        '<span style="color:#fbbf24;font-size:11px;">ORDINATO PER PUNTI</span>'
        "</div>",
        '<div class="tp-table-wrap"><table class="tp-stats-table"><thead><tr>'
        "<th>#</th>"
        '<th class="left-col">GIOCATORE</th>'
        "<th>G</th>"
        '<th class="hi-col">PUN</th>'
        '<th class="hi-col">PPG</th>'
        "<th>2PT R</th>"
        "<th>2PT T</th>"
        "<th>3PT R</th>"
        "<th>3PT T</th>"
        "<th>TL R</th>"
        "<th>TL T</th>"
        "<th>RIM</th>"
        "<th>ASS</th>"
        "<th>FALLI</th>"
        "<th>VAL</th>"
        "</tr></thead><tbody>",
    ]
    records = p_df.to_dict("records") if isinstance(p_df, pd.DataFrame) and not p_df.empty else []
    for row in records:
        if not isinstance(row, dict):
            continue
        try:
            p_name = str(row.get("Giocatore", "") or "").strip()
            if not p_name:
                continue
            raw_num = row.get("NUM", row.get("MAGLIA", None))
            num_disp = _format_jersey_display(
                num_val=raw_num if raw_num is not None else _extract_jersey_number(p_name, None),
                empty_placeholder="—",
                prefix="#",
            )
            num_safe = num_disp.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            name_safe = p_name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            ppg_val = float(pd.to_numeric(row.get("PPG", 0.0), errors="coerce") or 0.0)
            html.append(
                "<tr>"
                f'<td class="num-col">{num_safe}</td>'
                f'<td class="name-col">{name_safe}</td>'
                f"<td>{_to_safe_int(row.get('G', 0), 0)}</td>"
                f'<td class="pts-col">{_to_safe_int(row.get("PUN", 0), 0)}</td>'
                f'<td class="pts-col">{ppg_val:.1f}</td>'
                f"<td>{_to_safe_int(row.get('2PT_R', 0), 0)}</td>"
                f"<td>{_to_safe_int(row.get('2PT_T', 0), 0)}</td>"
                f"<td>{_to_safe_int(row.get('3PT_R', 0), 0)}</td>"
                f"<td>{_to_safe_int(row.get('3PT_T', 0), 0)}</td>"
                f"<td>{_to_safe_int(row.get('TL_R', 0), 0)}</td>"
                f"<td>{_to_safe_int(row.get('TL_T', 0), 0)}</td>"
                f"<td>{_to_safe_int(row.get('RIM', 0), 0)}</td>"
                f"<td>{_to_safe_int(row.get('ASS', 0), 0)}</td>"
                f"<td>{_to_safe_int(row.get('F_C', 0), 0)}</td>"
                f"<td>{_to_safe_int(row.get('VAL', 0), 0)}</td>"
                "</tr>"
            )
        except Exception:
            continue
    html.append("</tbody></table></div></div>")
    return "".join(html)
# ... existing code ...
    with st.expander("✏️ Modifica Numero di Maglia e Nome Cognome atleti", expanded=False):
        roster_edit_df = pd.DataFrame(
            [
                {
                    "_orig_key": str(r.get("Giocatore", "")).strip().lower(),
                    "NUM": _to_safe_int(r.get("NUM", 0), 0) if 0 <= _to_safe_int(r.get("NUM", 0), 0) <= 99 else 0,
                    "Giocatore": str(r.get("Giocatore", "")),
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
                parsed_n = pd.to_numeric(nr.get("NUM", None), errors="coerce")
                new_num = int(float(parsed_n)) if pd.notna(parsed_n) and 0 <= int(float(parsed_n)) <= 99 else 0
                if not new_name:
                    continue
                if idx_r < len(orig_rows) and orig_rows[idx_r].get("_orig_key"):
                    rename_map[str(orig_rows[idx_r]["_orig_key"])] = (new_name, new_num)
                rename_map[new_name.lower()] = (new_name, new_num)
# ... existing code ...
