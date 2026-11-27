# app.py — DR2 Puglia: Classifiche, Calendario e Scouting
import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
import json
import os
import uuid
import re

# ─── Configurazione Pagina ───────────────────────────────────────────────────
st.set_page_config(
    page_title="DR2 Puglia — Classifiche e Calendario",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── CSS Globale ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Oswald:wght@500;600;700&display=swap');

:root {
    --bg-primary: #0f1117;
    --bg-card: #161923;
    --bg-card-hover: #1d2130;
    --border-subtle: #252a3a;
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --accent-orange: #f97316;
    --accent-orange-dim: rgba(249, 115, 22, 0.15);
    --green: #22c55e;
    --green-dim: rgba(34, 197, 94, 0.15);
    --red: #ef4444;
    --red-dim: rgba(239, 68, 68, 0.15);
    --yellow: #eab308;
    --yellow-dim: rgba(234, 179, 8, 0.15);
    --blue: #3b82f6;
}

.stApp {
    background-color: var(--bg-primary);
    color: var(--text-primary);
    font-family: 'Inter', sans-serif;
}

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 3rem;
    max-width: 1280px;
}

h1, h2, h3 {
    font-family: 'Oswald', sans-serif;
    letter-spacing: 0.02em;
}

/* Header Banner */
.hero-banner {
    background: linear-gradient(135deg, #161923 0%, #1e2436 60%, rgba(249,115,22,0.18) 100%);
    border: 1px solid var(--border-subtle);
    border-left: 4px solid var(--accent-orange);
    border-radius: 10px;
    padding: 18px 24px;
    margin-bottom: 16px;
}
.hero-title {
    font-family: 'Oswald', sans-serif;
    font-size: 1.85rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0;
    line-height: 1.15;
    text-transform: uppercase;
}
.hero-sub {
    color: var(--text-secondary);
    font-size: 0.88rem;
    margin-top: 4px;
}

/* Metric Cards */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 10px;
    margin-bottom: 18px;
}
.metric-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 8px;
    padding: 12px 14px;
    text-align: center;
}
.metric-val {
    font-family: 'Oswald', sans-serif;
    font-size: 1.65rem;
    font-weight: 700;
    color: var(--accent-orange);
    line-height: 1.1;
}
.metric-lbl {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-secondary);
    margin-top: 4px;
}

/* Tabella Classifica Custom */
.standings-wrapper {
    background-color: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 10px;
    overflow-x: auto;
    margin-bottom: 18px;
}
table.standings-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.86rem;
}
table.standings-table th {
    background-color: #12151e;
    color: var(--text-secondary);
    font-weight: 600;
    text-transform: uppercase;
    font-size: 0.73rem;
    letter-spacing: 0.05em;
    padding: 11px 8px;
    text-align: center;
    border-bottom: 1px solid var(--border-subtle);
    white-space: nowrap;
}
table.standings-table th.col-team {
    text-align: left;
    padding-left: 14px;
}
table.standings-table td {
    padding: 9px 8px;
    text-align: center;
    border-bottom: 1px solid rgba(37, 42, 58, 0.6);
    color: var(--text-primary);
    white-space: nowrap;
}
table.standings-table tr:hover td {
    background-color: var(--bg-card-hover);
}
table.standings-table tr.row-highlight td {
    background-color: rgba(249, 115, 22, 0.10);
}
table.standings-table tr.row-highlight:hover td {
    background-color: rgba(249, 115, 22, 0.17);
}
td.col-pos {
    font-family: 'Oswald', sans-serif;
    font-weight: 700;
    font-size: 0.95rem;
    width: 38px;
}
td.col-team-name {
    text-align: left !important;
    padding-left: 14px !important;
    font-weight: 600;
}
td.col-pts {
    font-family: 'Oswald', sans-serif;
    font-weight: 700;
    font-size: 1.02rem;
    color: var(--accent-orange) !important;
}

/* Zone Playoff / Playout */
.zone-playoff { border-left: 3px solid var(--green) !important; }
.zone-playin  { border-left: 3px solid var(--yellow) !important; }
.zone-playout { border-left: 3px solid var(--red) !important; }
.zone-none    { border-left: 3px solid transparent !important; }

/* Forma Recente Badges */
.form-badge {
    display: inline-block;
    width: 19px;
    height: 19px;
    line-height: 19px;
    border-radius: 4px;
    font-size: 0.68rem;
    font-weight: 700;
    text-align: center;
    margin: 0 1px;
}
.form-w { background-color: var(--green-dim); color: var(--green); border: 1px solid rgba(34,197,94,0.35); }
.form-l { background-color: var(--red-dim); color: var(--red); border: 1px solid rgba(239,68,68,0.35); }

/* Match Card */
.match-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 9px;
    padding: 12px 16px;
    margin-bottom: 9px;
    transition: border-color 0.15s ease;
}
.match-card:hover {
    border-color: #384158;
}
.match-card-toritto {
    border-left: 3px solid var(--accent-orange);
    background: linear-gradient(90deg, rgba(249,115,22,0.08) 0%, var(--bg-card) 35%);
}
.match-meta {
    display: flex;
    justify-content: space-between;
    font-size: 0.74rem;
    color: var(--text-secondary);
    margin-bottom: 8px;
}
.match-body {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
}
.match-team {
    flex: 1;
    font-weight: 600;
    font-size: 0.94rem;
}
.match-team-home { text-align: right; }
.match-team-away { text-align: left; }
.team-winner { color: #ffffff; font-weight: 700; }
.team-loser { color: var(--text-secondary); font-weight: 500; }

.score-pill {
    font-family: 'Oswald', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    background-color: #10131b;
    border: 1px solid var(--border-subtle);
    border-radius: 6px;
    padding: 4px 12px;
    min-width: 96px;
    text-align: center;
    color: #ffffff;
    letter-spacing: 0.03em;
}
.score-pill-upcoming {
    font-family: 'Inter', sans-serif;
    font-size: 0.78rem;
    font-weight: 600;
    color: var(--accent-orange);
    background-color: var(--accent-orange-dim);
    border: 1px solid rgba(249,115,22,0.3);
}
.match-quarters {
    margin-top: 7px;
    padding-top: 6px;
    border-top: 1px dashed rgba(37, 42, 58, 0.8);
    font-size: 0.73rem;
    color: var(--text-muted);
    text-align: center;
}

/* Scouting Comparison Bars */
.comp-row {
    background-color: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 8px;
}
.comp-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.86rem;
    margin-bottom: 6px;
}
.comp-val {
    font-family: 'Oswald', sans-serif;
    font-size: 1.05rem;
    font-weight: 700;
}
.comp-label {
    font-size: 0.74rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-secondary);
}
.comp-bar-bg {
    display: flex;
    height: 7px;
    border-radius: 4px;
    overflow: hidden;
    background-color: #10131b;
}
.comp-bar-a { background-color: var(--accent-orange); }
.comp-bar-b { background-color: var(--blue); }

/* Legenda */
.legend-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
    font-size: 0.76rem;
    color: var(--text-secondary);
    padding: 8px 4px;
}
.legend-item {
    display: flex;
    align-items: center;
    gap: 6px;
}
.legend-dot {
    width: 10px;
    height: 10px;
    border-radius: 2px;
}

/* Nascondi menu standard Streamlit */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ─── Costanti & Dati Iniziali ────────────────────────────────────────────────
DATA_FILE = "dr2_puglia_data.json"
DEFAULT_FAVORITE_TEAM = "C.U.S. Bari"

LOGOS = {
    "Bitritto Basket": "🏀",
    "C.U.S. Bari": "🐺",
    "Basket Calimera": "🦅",
    "Fortitudo Grottaglie": "⚔️",
    "A.S.D. Duma": "🦁",
    "AP Monopoli": "⚓",
    "Fortitudo Basket Trani": "🏰",
    "Basket Noicattaro": "🍇",
    "BASKET CALIMERA": "🦅",
    "TORITTO": "🐂",
}

ALL_TEAMS = [
    "Bitritto Basket",
    "C.U.S. Bari",
    "Basket Calimera",
    "Fortitudo Grottaglie",
    "A.S.D. Duma",
    "AP Monopoli",
    "Fortitudo Basket Trani",
    "Basket Noicattaro",
    "TORITTO",
]

# Tabellini di esempio pre-caricati per test immediato
SAMPLE_PLAYER_STATS = {
    "girone_a_g1_m2": {
        "home": [
            {"Giocatore": "G. Rossi", "N°": 7, "MIN": 31, "PTS": 18, "2P R": 5, "2P T": 9, "3P R": 2, "3P T": 5, "TL R": 2, "TL T": 2, "RO": 1, "RD": 5, "ASS": 4, "PR": 2, "PP": 1, "ST": 0, "FF": 2, "FS": 3, "Q": True},
            {"Giocatore": "M. Bianchi", "N°": 11, "MIN": 28, "PTS": 14, "2P R": 6, "2P T": 10, "3P R": 0, "3P T": 1, "TL R": 2, "TL T": 4, "RO": 4, "RD": 6, "ASS": 1, "PR": 1, "PP": 2, "ST": 2, "FF": 3, "FS": 3, "Q": True},
            {"Giocatore": "L. Verdi", "N°": 4, "MIN": 26, "PTS": 11, "2P R": 2, "2P T": 5, "3P R": 2, "3P T": 6, "TL R": 1, "TL T": 2, "RO": 0, "RD": 3, "ASS": 5, "PR": 3, "PP": 3, "ST": 0, "FF": 1, "FS": 2, "Q": True},
            {"Giocatore": "A. Russo", "N°": 15, "MIN": 24, "PTS": 9, "2P R": 4, "2P T": 7, "3P R": 0, "3P T": 0, "TL R": 1, "TL T": 2, "RO": 2, "RD": 4, "ASS": 0, "PR": 0, "PP": 1, "ST": 1, "FF": 4, "FS": 2, "Q": True},
            {"Giocatore": "D. Conti", "N°": 9, "MIN": 22, "PTS": 8, "2P R": 1, "2P T": 3, "3P R": 2, "3P T": 4, "TL R": 0, "TL T": 0, "RO": 1, "RD": 2, "ASS": 2, "PR": 1, "PP": 1, "ST": 0, "FF": 2, "FS": 1, "Q": True},
            {"Giocatore": "F. Gallo", "N°": 23, "MIN": 18, "PTS": 6, "2P R": 3, "2P T": 5, "3P R": 0, "3P T": 1, "TL R": 0, "TL T": 0, "RO": 1, "RD": 2, "ASS": 1, "PR": 0, "PP": 2, "ST": 0, "FF": 1, "FS": 0, "Q": False},
            {"Giocatore": "S. Costa", "N°": 12, "MIN": 16, "PTS": 5, "2P R": 1, "2P T": 2, "3P R": 1, "3P T": 3, "TL R": 0, "TL T": 0, "RO": 0, "RD": 1, "ASS": 2, "PR": 1, "PP": 0, "ST": 0, "FF": 2, "FS": 1, "Q": False},
            {"Giocatore": "P. Moretti", "N°": 8, "MIN": 15, "PTS": 3, "2P R": 1, "2P T": 3, "3P R": 0, "3P T": 0, "TL R": 1, "TL T": 2, "RO": 2, "RD": 2, "ASS": 0, "PR": 0, "PP": 1, "ST": 0, "FF": 1, "FS": 1, "Q": False},
        ],
        "away": [
            {"Giocatore": "N. Marini", "N°": 10, "MIN": 33, "PTS": 20, "2P R": 4, "2P T": 8, "3P R": 3, "3P T": 7, "TL R": 3, "TL T": 4, "RO": 1, "RD": 4, "ASS": 3, "PR": 2, "PP": 3, "ST": 0, "FF": 3, "FS": 4, "Q": True},
            {"Giocatore": "E. Rinaldi", "N°": 14, "MIN": 29, "PTS": 15, "2P R": 6, "2P T": 11, "3P R": 0, "3P T": 0, "TL R": 3, "TL T": 5, "RO": 3, "RD": 7, "ASS": 1, "PR": 0, "PP": 2, "ST": 1, "FF": 4, "FS": 4, "Q": True},
            {"Giocatore": "T. Caruso", "N°": 6, "MIN": 27, "PTS": 12, "2P R": 3, "2P T": 6, "3P R": 2, "3P T": 5, "TL R": 0, "TL T": 0, "RO": 0, "RD": 2, "ASS": 4, "PR": 2, "PP": 2, "ST": 0, "FF": 2, "FS": 1, "Q": True},
            {"Giocatore": "R. Leone", "N°": 21, "MIN": 25, "PTS": 9, "2P R": 4, "2P T": 8, "3P R": 0, "3P T": 1, "TL R": 1, "TL T": 2, "RO": 2, "RD": 3, "ASS": 1, "PR": 1, "PP": 1, "ST": 1, "FF": 2, "FS": 2, "Q": True},
            {"Giocatore": "C. Serra", "N°": 5, "MIN": 21, "PTS": 6, "2P R": 0, "2P T": 2, "3P R": 2, "3P T": 4, "TL R": 0, "TL T": 0, "RO": 0, "RD": 2, "ASS": 2, "PR": 1, "PP": 1, "ST": 0, "FF": 1, "FS": 0, "Q": True},
            {"Giocatore": "V. Longo", "N°": 18, "MIN": 17, "PTS": 4, "2P R": 2, "2P T": 4, "3P R": 0, "3P T": 0, "TL R": 0, "TL T": 0, "RO": 1, "RD": 2, "ASS": 0, "PR": 0, "PP": 1, "ST": 0, "FF": 2, "FS": 1, "Q": False},
            {"Giocatore": "M. Greco", "N°": 13, "MIN": 13, "PTS": 2, "2P R": 1, "2P T": 3, "3P R": 0, "3P T": 1, "TL R": 0, "TL T": 0, "RO": 1, "RD": 1, "ASS": 1, "PR": 0, "PP": 0, "ST": 0, "FF": 1, "FS": 0, "Q": False},
        ]
    }
}

INITIAL_DATA = {
    "girone_a": {
        "nome": "Girone A",
        "descrizione": "Fase Regionale — Girone A (9 Squadre)",
        "squadre": ALL_TEAMS,
        "partite": [
            {"id": "girone_a_g1_m1", "giornata": 1, "data": "2025-10-18", "ora": "18:30", "casa": "Bitritto Basket", "trasferta": "Basket Noicattaro", "pt_casa": 78, "pt_trasferta": 64, "quarti": "21-15, 19-16, 20-17, 18-16", "giocata": True},
            {"id": "girone_a_g1_m2", "giornata": 1, "data": "2025-10-18", "ora": "19:00", "casa": "C.U.S. Bari", "trasferta": "Fortitudo Basket Trani", "pt_casa": 74, "pt_trasferta": 68, "quarti": "18-17, 20-16, 17-19, 19-16", "giocata": True},
            {"id": "girone_a_g1_m3", "giornata": 1, "data": "2025-10-19", "ora": "18:00", "casa": "Basket Calimera", "trasferta": "AP Monopoli", "pt_casa": 69, "pt_trasferta": 72, "quarti": "16-18, 18-17, 17-20, 18-17", "giocata": True},
            {"id": "girone_a_g1_m4", "giornata": 1, "data": "2025-10-19", "ora": "18:30", "casa": "Fortitudo Grottaglie", "trasferta": "A.S.D. Duma", "pt_casa": 81, "pt_trasferta": 75, "quarti": "22-18, 19-20, 21-18, 19-19", "giocata": True},
            {"id": "girone_a_g1_m5", "giornata": 1, "data": "2025-10-19", "ora": "19:00", "casa": "TORITTO", "trasferta": "Riposo", "pt_casa": None, "pt_trasferta": None, "quarti": "", "giocata": False},
            {"id": "girone_a_g2_m1", "giornata": 2, "data": "2025-10-25", "ora": "18:30", "casa": "AP Monopoli", "trasferta": "C.U.S. Bari", "pt_casa": 66, "pt_trasferta": 71, "quarti": "15-19, 18-16, 16-18, 17-18", "giocata": True},
            {"id": "girone_a_g2_m2", "giornata": 2, "data": "2025-10-25", "ora": "19:00", "casa": "Fortitudo Basket Trani", "trasferta": "Bitritto Basket", "pt_casa": 70, "pt_trasferta": 75, "quarti": "17-20, 18-18, 16-19, 19-18", "giocata": True},
            {"id": "girone_a_g2_m3", "giornata": 2, "data": "2025-10-26", "ora": "18:00", "casa": "A.S.D. Duma", "trasferta": "Basket Calimera", "pt_casa": 77, "pt_trasferta": 65, "quarti": "20-14, 19-17, 21-16, 17-18", "giocata": True},
            {"id": "girone_a_g2_m4", "giornata": 2, "data": "2025-10-26", "ora": "18:30", "casa": "Basket Noicattaro", "trasferta": "TORITTO", "pt_casa": 68, "pt_trasferta": 73, "quarti": "16-18, 17-19, 18-17, 17-19", "giocata": True},
            {"id": "girone_a_g3_m1", "giornata": 3, "data": "2025-11-01", "ora": "18:30", "casa": "Bitritto Basket", "trasferta": "AP Monopoli", "pt_casa": 82, "pt_trasferta": 70, "quarti": "22-16, 20-18, 21-17, 19-19", "giocata": True},
            {"id": "girone_a_g3_m2", "giornata": 3, "data": "2025-11-01", "ora": "19:00", "casa": "C.U.S. Bari", "trasferta": "A.S.D. Duma", "pt_casa": 79, "pt_trasferta": 73, "quarti": "21-17, 18-19, 20-18, 20-19", "giocata": True},
            {"id": "girone_a_g3_m3", "giornata": 3, "data": "2025-11-02", "ora": "18:00", "casa": "TORITTO", "trasferta": "Fortitudo Grottaglie", "pt_casa": 76, "pt_trasferta": 72, "quarti": "19-18, 20-17, 18-20, 19-17", "giocata": True},
            {"id": "girone_a_g3_m4", "giornata": 3, "data": "2025-11-02", "ora": "18:30", "casa": "Basket Calimera", "trasferta": "Fortitudo Basket Trani", "pt_casa": 74, "pt_trasferta": 69, "quarti": "18-16, 19-18, 17-18, 20-17", "giocata": True},
            {"id": "girone_a_g4_m1", "giornata": 4, "data": "2025-11-08", "ora": "18:30", "casa": "A.S.D. Duma", "trasferta": "Bitritto Basket", "pt_casa": None, "pt_trasferta": None, "quarti": "", "giocata": False},
            {"id": "girone_a_g4_m2", "giornata": 4, "data": "2025-11-08", "ora": "19:00", "casa": "Fortitudo Grottaglie", "trasferta": "C.U.S. Bari", "pt_casa": None, "pt_trasferta": None, "quarti": "", "giocata": False},
            {"id": "girone_a_g4_m3", "giornata": 4, "data": "2025-11-09", "ora": "18:00", "casa": "AP Monopoli", "trasferta": "TORITTO", "pt_casa": None, "pt_trasferta": None, "quarti": "", "giocata": False},
            {"id": "girone_a_g4_m4", "giornata": 4, "data": "2025-11-09", "ora": "18:30", "casa": "Fortitudo Basket Trani", "trasferta": "Basket Noicattaro", "pt_casa": None, "pt_trasferta": None, "quarti": "", "giocata": False},
        ]
    }
}

# ─── Persistenza Dati JSON ───────────────────────────────────────────────────
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "player_stats" not in data:
                    data["player_stats"] = SAMPLE_PLAYER_STATS
                if "rosters" not in data:
                    data["rosters"] = {}
                if "girone_a" not in data:
                    data["girone_a"] = INITIAL_DATA["girone_a"]
                return data
        except Exception:
            pass
    default = {
        "girone_a": INITIAL_DATA["girone_a"],
        "player_stats": SAMPLE_PLAYER_STATS,
        "rosters": {}
    }
    save_data(default)
    return default

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if "league_data" not in st.session_state:
    st.session_state.league_data = load_data()

if "fav_team" not in st.session_state:
    st.session_state.fav_team = "TORITTO"

if "selected_team_page" not in st.session_state:
    st.session_state.selected_team_page = None

# ─── Calcolo Classifica & Metriche Avanzate ──────────────────────────────────
def compute_standings(girone_data):
    teams = girone_data.get("squadre", [])
    partite = [p for p in girone_data.get("partite", []) if p.get("giocata") and p.get("casa") != "Riposo" and p.get("trasferta") != "Riposo"]

    stats = {
        t: {
            "Squadra": t, "G": 0, "V": 0, "P": 0, "PTI": 0,
            "PF": 0, "PS": 0, "DIFF": 0,
            "Casa_V": 0, "Casa_P": 0, "Casa_PF": 0, "Casa_PS": 0,
            "Trasf_V": 0, "Trasf_P": 0, "Trasf_PF": 0, "Trasf_PS": 0,
            "Forma": [],
            "Q1_F": 0, "Q1_S": 0, "Q2_F": 0, "Q2_S": 0,
            "Q3_F": 0, "Q3_S": 0, "Q4_F": 0, "Q4_S": 0,
            "Q_Gare": 0
        }
        for t in teams
    }

    partite_sorted = sorted(partite, key=lambda x: (x.get("giornata", 0), x.get("data", "")))

    for p in partite_sorted:
        c, tr = p["casa"], p["trasferta"]
        pt_c, pt_t = p["pt_casa"], p["pt_trasferta"]
        if pt_c is None or pt_t is None:
            continue

        for sq in (c, tr):
            if sq not in stats:
                stats[sq] = {
                    "Squadra": sq, "G": 0, "V": 0, "P": 0, "PTI": 0,
                    "PF": 0, "PS": 0, "DIFF": 0,
                    "Casa_V": 0, "Casa_P": 0, "Casa_PF": 0, "Casa_PS": 0,
                    "Trasf_V": 0, "Trasf_P": 0, "Trasf_PF": 0, "Trasf_PS": 0,
                    "Forma": [],
                    "Q1_F": 0, "Q1_S": 0, "Q2_F": 0, "Q2_S": 0,
                    "Q3_F": 0, "Q3_S": 0, "Q4_F": 0, "Q4_S": 0,
                    "Q_Gare": 0
                }

        stats[c]["G"] += 1
        stats[tr]["G"] += 1
        stats[c]["PF"] += pt_c
        stats[c]["PS"] += pt_t
        stats[tr]["PF"] += pt_t
        stats[tr]["PS"] += pt_c

        stats[c]["Casa_PF"] += pt_c
        stats[c]["Casa_PS"] += pt_t
        stats[tr]["Trasf_PF"] += pt_t
        stats[tr]["Trasf_PS"] += pt_c

        if pt_c > pt_t:
            stats[c]["V"] += 1
            stats[c]["PTI"] += 2
            stats[c]["Casa_V"] += 1
            stats[c]["Forma"].append("W")

            stats[tr]["P"] += 1
            stats[tr]["Trasf_P"] += 1
            stats[tr]["Forma"].append("L")
        else:
            stats[tr]["V"] += 1
            stats[tr]["PTI"] += 2
            stats[tr]["Trasf_V"] += 1
            stats[tr]["Forma"].append("W")

            stats[c]["P"] += 1
            stats[c]["Casa_P"] += 1
            stats[c]["Forma"].append("L")

        # Parsing dei quarti se disponibili
        q_str = p.get("quarti", "")
        if q_str:
            parts = [x.strip() for x in q_str.split(",") if "-" in x]
            if len(parts) >= 4:
                try:
                    q_vals = []
                    for q_item in parts[:4]:
                        qc, qt = map(int, q_item.split("-"))
                        q_vals.append((qc, qt))
                    for idx, (qc, qt) in enumerate(q_vals, start=1):
                        stats[c][f"Q{idx}_F"] += qc
                        stats[c][f"Q{idx}_S"] += qt
                        stats[tr][f"Q{idx}_F"] += qt
                        stats[tr][f"Q{idx}_S"] += qc
                    stats[c]["Q_Gare"] += 1
                    stats[tr]["Q_Gare"] += 1
                except ValueError:
                    pass

    rows = list(stats.values())
    for r in rows:
        r["DIFF"] = r["PF"] - r["PS"]
        r["PF_G"] = round(r["PF"] / r["G"], 1) if r["G"] > 0 else 0.0
        r["PS_G"] = round(r["PS"] / r["G"], 1) if r["G"] > 0 else 0.0
        r["DIFF_G"] = round(r["DIFF"] / r["G"], 1) if r["G"] > 0 else 0.0
        r["WIN_PCT"] = round((r["V"] / r["G"]) * 100, 1) if r["G"] > 0 else 0.0

        g_casa = r["Casa_V"] + r["Casa_P"]
        g_trasf = r["Trasf_V"] + r["Trasf_P"]
        r["Casa_PF_G"] = round(r["Casa_PF"] / g_casa, 1) if g_casa > 0 else 0.0
        r["Casa_PS_G"] = round(r["Casa_PS"] / g_casa, 1) if g_casa > 0 else 0.0
        r["Trasf_PF_G"] = round(r["Trasf_PF"] / g_trasf, 1) if g_trasf > 0 else 0.0
        r["Trasf_PS_G"] = round(r["Trasf_PS"] / g_trasf, 1) if g_trasf > 0 else 0.0

    rows.sort(key=lambda x: (-x["PTI"], -x["DIFF"], -x["PF"], x["Squadra"]))

    # Calcolo Strength of Schedule / Record contro squadre >= 50% vittorie
    team_win_pct = {r["Squadra"]: r["WIN_PCT"] for r in rows}
    top_record = {t: {"V": 0, "P": 0} for t in stats}
    for p in partite_sorted:
        c, tr = p["casa"], p["trasferta"]
        pt_c, pt_t = p["pt_casa"], p["pt_trasferta"]
        if pt_c is None or pt_t is None:
            continue
        if team_win_pct.get(tr, 0) >= 50.0:
            if pt_c > pt_t:
                top_record[c]["V"] += 1
            else:
                top_record[c]["P"] += 1
        if team_win_pct.get(c, 0) >= 50.0:
            if pt_t > pt_c:
                top_record[tr]["V"] += 1
            else:
                top_record[tr]["P"] += 1

    for i, r in enumerate(rows, start=1):
        r["Pos"] = i
        sq = r["Squadra"]
        r["vs_Top50"] = f"{top_record[sq]['V']}-{top_record[sq]['P']}"

    return rows

def get_zone_class(pos, total_teams):
    if pos <= 4:
        return "zone-playoff"
    elif pos <= 6:
        return "zone-playin"
    elif pos >= total_teams - 1:
        return "zone-playout"
    return "zone-none"

def format_form_badges(forma_list):
    if not forma_list:
        return "<span style='color:#64748b;font-size:0.75rem;'>-</span>"
    last5 = forma_list[-5:]
    html = ""
    for res in last5:
        cls = "form-w" if res == "W" else "form-l"
        lbl = "V" if res == "W" else "P"
        html += f"<span class='form-badge {cls}'>{lbl}</span>"
    return html

def format_date_it(date_str):
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        mesi = ["Gen", "Feb", "Mar", "Apr", "Mag", "Giu", "Lug", "Ago", "Set", "Ott", "Nov", "Dic"]
        return f"{dt.day:02d} {mesi[dt.month-1]} {dt.year}"
    except Exception:
        return date_str

def calc_pir(row):
    pts = row.get("PTS", 0)
    reb = row.get("RO", 0) + row.get("RD", 0)
    ast = row.get("ASS", 0)
    stl = row.get("PR", 0)
    blk = row.get("ST", 0)
    fs = row.get("FS", 0)
    miss_2 = max(0, row.get("2P T", 0) - row.get("2P R", 0))
    miss_3 = max(0, row.get("3P T", 0) - row.get("3P R", 0))
    miss_ft = max(0, row.get("TL T", 0) - row.get("TL R", 0))
    to = row.get("PP", 0)
    ff = row.get("FF", 0)
    return (pts + reb + ast + stl + blk + fs) - (miss_2 + miss_3 + miss_ft + to + ff)

def is_toritto_team(team_name):
    return "toritto" in team_name.strip().lower()

def get_team_roster(team_name):
    rosters = st.session_state.league_data.get("rosters", {})
    return rosters.get(team_name, [])

def save_team_roster(team_name, roster_list):
    if "rosters" not in st.session_state.league_data:
        st.session_state.league_data["rosters"] = {}
    cleaned = []
    seen = set()
    for item in roster_list:
        nome = str(item.get("Giocatore", "")).strip()
        if not nome or nome in seen:
            continue
        seen.add(nome)
        cleaned.append({
            "Giocatore": nome,
            "N°": int(item.get("N°", 0) or 0)
        })
    st.session_state.league_data["rosters"][team_name] = cleaned
    save_data(st.session_state.league_data)

def sanitize_opponent_rows(df_edited):
    rows = []
    for _, r in df_edited.iterrows():
        nome = str(r.get("Giocatore", "")).strip()
        if not nome:
            continue
        p2r = int(r.get("2P R", 0) or 0)
        p3r = int(r.get("3P R", 0) or 0)
        tlr = int(r.get("TL R", 0) or 0)
        tlt = max(tlr, int(r.get("TL T", 0) or 0))
        pts = (p2r * 2) + (p3r * 3) + tlr
        rows.append({
            "Giocatore": nome,
            "N°": int(r.get("N°", 0) or 0),
            "Q": bool(r.get("Q", False)),
            "MIN": int(r.get("MIN", 0) or 0),
            "FF": int(r.get("FF", 0) or 0),
            "2P R": p2r,
            "3P R": p3r,
            "TL R": tlr,
            "TL T": tlt,
            "PTS": pts,
        })
    return rows

def sanitize_toritto_rows(df_edited):
    rows = []
    for _, r in df_edited.iterrows():
        nome = str(r.get("Giocatore", "")).strip()
        if not nome:
            continue
        p2r = int(r.get("2P R", 0) or 0)
        p2t = max(p2r, int(r.get("2P T", 0) or 0))
        p3r = int(r.get("3P R", 0) or 0)
        p3t = max(p3r, int(r.get("3P T", 0) or 0))
        tlr = int(r.get("TL R", 0) or 0)
        tlt = max(tlr, int(r.get("TL T", 0) or 0))
        pts = (p2r * 2) + (p3r * 3) + tlr
        rows.append({
            "Giocatore": nome,
            "N°": int(r.get("N°", 0) or 0),
            "Q": bool(r.get("Q", False)),
            "MIN": int(r.get("MIN", 0) or 0),
            "PTS": pts,
            "2P R": p2r, "2P T": p2t,
            "3P R": p3r, "3P T": p3t,
            "TL R": tlr, "TL T": tlt,
            "RO": int(r.get("RO", 0) or 0),
            "RD": int(r.get("RD", 0) or 0),
            "ASS": int(r.get("ASS", 0) or 0),
            "PR": int(r.get("PR", 0) or 0),
            "PP": int(r.get("PP", 0) or 0),
            "ST": int(r.get("ST", 0) or 0),
            "FF": int(r.get("FF", 0) or 0),
            "FS": int(r.get("FS", 0) or 0),
        })
    return rows

def get_all_players_stats_summary(girone_data, player_stats_db):
    """Aggrega le statistiche di tutti i giocatori del campionato con incidenza sui punti squadra."""
    partite_map = {p["id"]: p for p in girone_data.get("partite", [])}
    agg = {}

    for match_id, sides in player_stats_db.items():
        match = partite_map.get(match_id)
        if not match or not match.get("giocata"):
            continue
        for side_key, team_key in [("home", "casa"), ("away", "trasferta")]:
            team_name = match.get(team_key)
            team_pts_match = match.get("pt_casa") if side_key == "home" else match.get("pt_trasferta")
            if not team_name or team_pts_match is None:
                continue
            rows = sides.get(side_key, [])
            for r in rows:
                g_name = str(r.get("Giocatore", "")).strip()
                if not g_name:
                    continue
                key = (team_name, g_name)
                if key not in agg:
                    agg[key] = {
                        "Squadra": team_name,
                        "Giocatore": g_name,
                        "N°": int(r.get("N°", 0) or 0),
                        "G": 0, "Q_G": 0, "MIN": 0, "PTS": 0, "High": 0,
                        "2P_R": 0, "3P_R": 0, "TL_R": 0, "TL_T": 0,
                        "FF": 0, "Team_PTS_Played": 0,
                        "Games_15plus": 0, "Games_20plus": 0
                    }
                pts = int(r.get("PTS", 0) or 0)
                agg[key]["G"] += 1
                if r.get("Q"):
                    agg[key]["Q_G"] += 1
                agg[key]["MIN"] += int(r.get("MIN", 0) or 0)
                agg[key]["PTS"] += pts
                agg[key]["High"] = max(agg[key]["High"], pts)
                agg[key]["2P_R"] += int(r.get("2P R", 0) or 0)
                agg[key]["3P_R"] += int(r.get("3P R", 0) or 0)
                agg[key]["TL_R"] += int(r.get("TL R", 0) or 0)
                agg[key]["TL_T"] += int(r.get("TL T", 0) or 0)
                agg[key]["FF"] += int(r.get("FF", 0) or 0)
                agg[key]["Team_PTS_Played"] += int(team_pts_match)
                if pts >= 15:
                    agg[key]["Games_15plus"] += 1
                if pts >= 20:
                    agg[key]["Games_20plus"] += 1

    result = []
    for item in agg.values():
        g = item["G"]
        item["PPG"] = round(item["PTS"] / g, 1) if g > 0 else 0.0
        item["MPG"] = round(item["MIN"] / g, 1) if g > 0 else 0.0
        item["FPG"] = round(item["FF"] / g, 1) if g > 0 else 0.0
        item["3PG"] = round(item["3P_R"] / g, 1) if g > 0 else 0.0
        item["TL_PCT"] = round((item["TL_R"] / item["TL_T"]) * 100, 1) if item["TL_T"] > 0 else 0.0
        item["Share_PTS"] = round((item["PTS"] / item["Team_PTS_Played"]) * 100, 1) if item["Team_PTS_Played"] > 0 else 0.0

        # Profilo offensivo sintetico
        pts_tot = max(1, item["PTS"])
        pct_from_3 = ((item["3P_R"] * 3) / pts_tot) * 100
        pct_from_ft = (item["TL_R"] / pts_tot) * 100
        if pct_from_3 >= 40:
            item["Profilo"] = "🎯 Tiratore 3PT"
        elif pct_from_ft >= 28:
            item["Profilo"] = "⚡ Penetratore / Falli"
        elif item["2P_R"] * 2 / pts_tot >= 65:
            item["Profilo"] = "🏀 Finalizzatore Area"
        else:
            item["Profilo"] = "🔄 Realizzatore Completo"

        result.append(item)

    result.sort(key=lambda x: (-x["PPG"], -x["PTS"]))
    return result

# ─── Componenti UI ───────────────────────────────────────────────────────────
def render_header():
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">🏀 DR2 Puglia — Classifiche, Calendario & Scouting</div>
        <div class="hero-sub">FIP Puglia • Divisione Regionale 2 • Girone A • Analisi Pre-Gara, Minacce Offensive e Statistiche</div>
    </div>
    """, unsafe_allow_html=True)

def render_match_card(match, fav_team, show_boxscore_btn=False, key_prefix=""):
    casa = match["casa"]
    trasf = match["trasferta"]
    giocata = match.get("giocata", False)
    pt_c = match.get("pt_casa")
    pt_t = match.get("pt_trasferta")

    is_fav = (casa == fav_team or trasf == fav_team)
    card_cls = "match-card match-card-toritto" if is_fav else "match-card"

    logo_c = LOGOS.get(casa, "🏀")
    logo_t = LOGOS.get(trasf, "🏀")

    if trasf == "Riposo":
        st.markdown(f"""
        <div class="{card_cls}">
            <div class="match-meta">
                <span>Giornata {match['giornata']} • {format_date_it(match['data'])}</span>
                <span>Turno di Riposo</span>
            </div>
            <div class="match-body">
                <div class="match-team" style="text-align:center;color:#94a3b8;">
                    {logo_c} <strong>{casa}</strong> — Riposa in questo turno
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    if giocata and pt_c is not None and pt_t is not None:
        c_cls = "team-winner" if pt_c > pt_t else "team-loser"
        t_cls = "team-winner" if pt_t > pt_c else "team-loser"
        score_html = f"<div class='score-pill'>{pt_c} - {pt_t}</div>"
        status_lbl = "<span style='color:#22c55e;font-weight:600;'>FINALE</span>"
    else:
        c_cls = ""
        t_cls = ""
        score_html = f"<div class='score-pill score-pill-upcoming'>{match.get('ora', '18:30')}</div>"
        status_lbl = "<span style='color:#f97316;font-weight:600;'>DA GIOCARE</span>"

    quarti_html = ""
    if giocata and match.get("quarti"):
        quarti_html = f"<div class='match-quarters'>Parziali: {match['quarti']}</div>"

    has_stats = match["id"] in st.session_state.league_data.get("player_stats", {})
    badge_stats = " • 📊 Tabellino" if has_stats else ""

    st.markdown(f"""
    <div class="{card_cls}">
        <div class="match-meta">
            <span>Giornata {match['giornata']} • {format_date_it(match['data'])} • Ore {match.get('ora', '-')}{badge_stats}</span>
            <span>{status_lbl}</span>
        </div>
        <div class="match-body">
            <div class="match-team match-team-home {c_cls}">{casa} {logo_c}</div>
            {score_html}
            <div class="match-team match-team-away {t_cls}">{logo_t} {trasf}</div>
        </div>
        {quarti_html}
    </div>
    """, unsafe_allow_html=True)

    if show_boxscore_btn and giocata:
        if st.button(f"📊 Tabellino: {casa} vs {trasf}", key=f"{key_prefix}_btn_{match['id']}", use_container_width=True):
            st.session_state[f"open_box_{match['id']}"] = not st.session_state.get(f"open_box_{match['id']}", False)

        if st.session_state.get(f"open_box_{match['id']}", False):
            render_boxscore_panel(match)

def render_boxscore_panel(match):
    match_id = match["id"]
    p_stats = st.session_state.league_data.get("player_stats", {}).get(match_id)

    with st.container(border=True):
        st.markdown(f"#### 📋 Tabellino Partita — {match['casa']} vs {match['trasferta']}")
        if not p_stats:
            st.info("Nessun tabellino individuale inserito per questa partita. Puoi aggiungerlo dalla sezione **⚙️ Gestione Dati & Tabellini**.")
            return

        tab_c, tab_t = st.tabs([f"{LOGOS.get(match['casa'], '🏀')} {match['casa']}", f"{LOGOS.get(match['trasferta'], '🏀')} {match['trasferta']}"])

        for tab, side_key, team_name in [(tab_c, "home", match["casa"]), (tab_t, "away", match["trasferta"])]:
            with tab:
                rows = p_stats.get(side_key, [])
                if not rows:
                    st.caption("Dati giocatori non disponibili per questa squadra.")
                    continue
                df = pd.DataFrame(rows)
                if is_toritto_team(team_name):
                    if "RO" in df.columns and "RD" in df.columns:
                        df["RT"] = df["RO"] + df["RD"]
                    df["VAL"] = df.apply(calc_pir, axis=1)
                    cols_order = ["N°", "Giocatore", "Q", "MIN", "PTS", "2P R", "2P T", "3P R", "3P T", "TL R", "TL T", "RO", "RD", "RT", "ASS", "PR", "PP", "ST", "FF", "FS", "VAL"]
                    cols_present = [c for c in cols_order if c in df.columns]
                    st.dataframe(df[cols_present], use_container_width=True, hide_index=True)
                else:
                    df["TL %"] = df.apply(
                        lambda r: round((r.get("TL R", 0) / r.get("TL T", 0)) * 100, 1) if r.get("TL T", 0) > 0 else 0.0,
                        axis=1
                    )
                    cols_order = ["N°", "Giocatore", "Q", "MIN", "PTS", "FF", "2P R", "3P R", "TL R", "TL T", "TL %"]
                    cols_present = [c for c in cols_order if c in df.columns]
                    st.dataframe(df[cols_present], use_container_width=True, hide_index=True)

# ─── Viste Principali ────────────────────────────────────────────────────────
def view_classifica(girone_data, standings):
    st.markdown(f"### 🏆 Classifica — {girone_data['nome']}")

    tot_giocate = sum(1 for p in girone_data["partite"] if p.get("giocata") and p.get("trasferta") != "Riposo")
    tot_partite = sum(1 for p in girone_data["partite"] if p.get("trasferta") != "Riposo")
    punti_tot = sum((p.get("pt_casa") or 0) + (p.get("pt_trasferta") or 0) for p in girone_data["partite"] if p.get("giocata"))
    media_pt = round(punti_tot / (tot_giocate * 2), 1) if tot_giocate > 0 else 0.0

    # Miglior attacco e miglior difesa
    active_teams = [r for r in standings if r["G"] > 0]
    best_off = max(active_teams, key=lambda x: x["PF_G"]) if active_teams else None
    best_def = min(active_teams, key=lambda x: x["PS_G"]) if active_teams else None

    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-card"><div class="metric-val">{len(standings)}</div><div class="metric-lbl">Squadre</div></div>
        <div class="metric-card"><div class="metric-val">{tot_giocate}/{tot_partite}</div><div class="metric-lbl">Gare Giocate</div></div>
        <div class="metric-card"><div class="metric-val">{media_pt}</div><div class="metric-lbl">Media Punti / Squadra</div></div>
        <div class="metric-card"><div class="metric-val" style="font-size:1.15rem;">{best_off['Squadra'] if best_off else '-'} ({best_off['PF_G'] if best_off else 0})</div><div class="metric-lbl">Miglior Attacco (PPG)</div></div>
        <div class="metric-card"><div class="metric-val" style="font-size:1.15rem;">{best_def['Squadra'] if best_def else '-'} ({best_def['PS_G'] if best_def else 0})</div><div class="metric-lbl">Miglior Difesa (PPG)</div></div>
    </div>
    """, unsafe_allow_html=True)

    fav_team = st.session_state.fav_team
    total_teams = len(standings)

    rows_html = ""
    for r in standings:
        sq = r["Squadra"]
        zone_cls = get_zone_class(r["Pos"], total_teams)
        row_cls = "row-highlight" if sq == fav_team else ""
        logo = LOGOS.get(sq, "🏀")
        diff_str = f"+{r['DIFF']}" if r["DIFF"] > 0 else str(r["DIFF"])
        diff_color = "#22c55e" if r["DIFF"] > 0 else ("#ef4444" if r["DIFF"] < 0 else "#94a3b8")
        forma_html = format_form_badges(r["Forma"])
        casa_rec = f"{r['Casa_V']}-{r['Casa_P']}"
        trasf_rec = f"{r['Trasf_V']}-{r['Trasf_P']}"

        rows_html += f"""
        <tr class="{row_cls}">
            <td class="col-pos {zone_cls}">{r['Pos']}</td>
            <td class="col-team-name">{logo} {sq}</td>
            <td class="col-pts">{r['PTI']}</td>
            <td>{r['G']}</td>
            <td>{r['V']}</td>
            <td>{r['P']}</td>
            <td>{r['PF_G']}</td>
            <td>{r['PS_G']}</td>
            <td style="color:{diff_color};font-weight:600;">{diff_str}</td>
            <td>{casa_rec}</td>
            <td>{trasf_rec}</td>
            <td>{r['vs_Top50']}</td>
            <td>{forma_html}</td>
        </tr>
        """

    st.markdown(f"""
    <div class="standings-wrapper">
        <table class="standings-table">
            <thead>
                <tr>
                    <th>#</th>
                    <th class="col-team">Squadra</th>
                    <th>PTI</th>
                    <th>G</th>
                    <th>V</th>
                    <th>P</th>
                    <th>PF/G</th>
                    <th>PS/G</th>
                    <th>DIFF</th>
                    <th>CASA</th>
                    <th>TRASF</th>
                    <th>vs ≥50%</th>
                    <th>FORMA (ULT. 5)</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    <div class="legend-bar">
        <div class="legend-item"><div class="legend-dot" style="background:#22c55e;"></div> Playoff (1ª - 4ª)</div>
        <div class="legend-item"><div class="legend-dot" style="background:#eab308;"></div> Play-In (5ª - 6ª)</div>
        <div class="legend-item"><div class="legend-dot" style="background:#ef4444;"></div> Playout / Retrocessione</div>
        <div class="legend-item"><span>• <strong>vs ≥50%</strong>: Record contro squadre con almeno il 50% di vittorie</span></div>
    </div>
    """, unsafe_allow_html=True)

    # Analisi Avanzata del Livello del Girone
    with st.expander("📈 Analisi Livello del Girone — Attacco vs Difesa, Fattore Campo e Quarti"):
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown("#### 🎯 Efficienza Offensiva vs Difensiva (PPG)")
            if active_teams:
                df_eff = pd.DataFrame(active_teams)
                chart = alt.Chart(df_eff).mark_circle(size=140).encode(
                    x=alt.X("PF_G:Q", title="Punti Segnati a Partita (Attacco)", scale=alt.Scale(zero=False)),
                    y=alt.Y("PS_G:Q", title="Punti Subiti a Partita (Difesa - più basso è meglio)", scale=alt.Scale(zero=False, reverse=True)),
                    color=alt.condition(
                        alt.datum.Squadra == fav_team,
                        alt.value("#f97316"),
                        alt.value("#3b82f6")
                    ),
                    tooltip=["Squadra", "PTI", "V", "P", "PF_G", "PS_G", "DIFF_G"]
                ).properties(height=300)
                text = chart.mark_text(align="left", baseline="middle", dx=8, color="#e2e8f0", fontSize=11).encode(
                    text="Squadra"
                )
                st.altair_chart(chart + text, use_container_width=True)
            else:
                st.info("Dati insufficienti per il grafico.")

        with col_g2:
            st.markdown("#### 🏠 Impatto Fattore Campo & Ritmo")
            partite_giocate = [p for p in girone_data["partite"] if p.get("giocata") and p.get("trasferta") != "Riposo"]
            if partite_giocate:
                vitt_casa = sum(1 for p in partite_giocate if (p["pt_casa"] or 0) > (p["pt_trasferta"] or 0))
                pct_casa = round((vitt_casa / len(partite_giocate)) * 100, 1)
                scarto_medio = round(sum(abs((p["pt_casa"] or 0) - (p["pt_trasferta"] or 0)) for p in partite_giocate) / len(partite_giocate), 1)
                gare_punto_a_punto = sum(1 for p in partite_giocate if abs((p["pt_casa"] or 0) - (p["pt_trasferta"] or 0)) <= 6)

                st.metric("Vittorie in Casa nel Girone", f"{vitt_casa}/{len(partite_giocate)} ({pct_casa}%)")
                st.metric("Scarto Medio a Partita", f"{scarto_medio} punti")
                st.metric("Gare Punto a Punto (≤ 6 pt)", f"{gare_punto_a_punto} su {len(partite_giocate)}")
            else:
                st.info("Nessuna partita giocata.")

        st.markdown("#### ⏱️ Rendimento per Quarto di Gioco (Differenziale Medio)")
        q_rows = []
        for r in standings:
            qg = r["Q_Gare"]
            if qg > 0:
                q_rows.append({
                    "Squadra": r["Squadra"],
                    "Gare con Parziali": qg,
                    "1° Quarto": round((r["Q1_F"] - r["Q1_S"]) / qg, 1),
                    "2° Quarto": round((r["Q2_F"] - r["Q2_S"]) / qg, 1),
                    "3° Quarto": round((r["Q3_F"] - r["Q3_S"]) / qg, 1),
                    "4° Quarto": round((r["Q4_F"] - r["Q4_S"]) / qg, 1),
                })
        if q_rows:
            st.dataframe(pd.DataFrame(q_rows), use_container_width=True, hide_index=True)

def view_scouting_pre_gara(girone_data, standings):
    st.markdown("### 🎯 Scouting Pre-Gara & Confronto Avversari")
    st.caption("Seleziona la tua squadra e l'avversaria da affrontare per analizzare punti di forza, rendimento casa/trasferta, quarti critici e giocatori più pericolosi.")

    teams = girone_data["squadre"]
    default_a_idx = teams.index(st.session_state.fav_team) if st.session_state.fav_team in teams else 0

    # Trova automaticamente la prossima avversaria di fav_team se disponibile
    next_opp = None
    upcoming_fav = sorted(
        [p for p in girone_data["partite"] if not p.get("giocata") and p.get("trasferta") != "Riposo" and (p["casa"] == st.session_state.fav_team or p["trasferta"] == st.session_state.fav_team)],
        key=lambda x: x.get("giornata", 99)
    )
    if upcoming_fav:
        m_next = upcoming_fav[0]
        next_opp = m_next["trasferta"] if m_next["casa"] == st.session_state.fav_team else m_next["casa"]

    default_b_idx = teams.index(next_opp) if (next_opp and next_opp in teams) else (1 if default_a_idx == 0 else 0)

    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        team_a = st.selectbox("🟠 La Tua Squadra", teams, index=default_a_idx, key="scout_team_a")
    with col_sel2:
        team_b = st.selectbox("🔵 Prossima Avversaria", teams, index=default_b_idx, key="scout_team_b")

    if upcoming_fav and team_a == st.session_state.fav_team and team_b == next_opp:
        m_next = upcoming_fav[0]
        dove = "IN CASA 🏠" if m_next["casa"] == team_a else "IN TRASFERTA ✈️"
        st.info(f"📅 **Prossimo Impegno Ufficiale (Giornata {m_next['giornata']}):** {m_next['casa']} vs {m_next['trasferta']} — {format_date_it(m_next['data'])} ore {m_next.get('ora', '-')} (**{dove}**)")

    standings_map = {r["Squadra"]: r for r in standings}
    sa = standings_map.get(team_a, {})
    sb = standings_map.get(team_b, {})

    # Confronto Diretto
    st.markdown("#### ⚔️ Confronto Statistico Diretto")

    def render_comp_bar(label, val_a, val_b, higher_is_better=True, suffix=""):
        tot = abs(val_a) + abs(val_b)
        pct_a = 50 if tot == 0 else max(15, min(85, round((abs(val_a) / tot) * 100)))
        pct_b = 100 - pct_a
        color_a = "#22c55e" if (val_a > val_b and higher_is_better) or (val_a < val_b and not higher_is_better) else "#f1f5f9"
        color_b = "#22c55e" if (val_b > val_a and higher_is_better) or (val_b < val_a and not higher_is_better) else "#f1f5f9"
        st.markdown(f"""
        <div class="comp-row">
            <div class="comp-header">
                <span class="comp-val" style="color:{color_a};">{val_a}{suffix}</span>
                <span class="comp-label">{label}</span>
                <span class="comp-val" style="color:{color_b};">{val_b}{suffix}</span>
            </div>
            <div class="comp-bar-bg">
                <div class="comp-bar-a" style="width:{pct_a}%;"></div>
                <div class="comp-bar-b" style="width:{pct_b}%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    c_left, c_mid, c_right = st.columns([1.2, 2, 1.2])
    with c_left:
        st.markdown(f"""
        <div class="metric-card" style="border-top:3px solid #f97316;">
            <div style="font-size:1.5rem;">{LOGOS.get(team_a, '🏀')}</div>
            <div style="font-weight:700;font-size:1.05rem;">{team_a}</div>
            <div style="color:#94a3b8;font-size:0.8rem;">Posizione: <strong>#{sa.get('Pos', '-')}</strong> ({sa.get('V', 0)}V - {sa.get('P', 0)}P)</div>
            <div style="margin-top:6px;">{format_form_badges(sa.get('Forma', []))}</div>
        </div>
        """, unsafe_allow_html=True)

    with c_mid:
        render_comp_bar("Punti Segnati / Partita (Attacco)", sa.get("PF_G", 0), sb.get("PF_G", 0), higher_is_better=True)
        render_comp_bar("Punti Subiti / Partita (Difesa)", sa.get("PS_G", 0), sb.get("PS_G", 0), higher_is_better=False)
        render_comp_bar("Differenza Canestri Media", sa.get("DIFF_G", 0), sb.get("DIFF_G", 0), higher_is_better=True)
        render_comp_bar("Rendimento in Casa (PF/G)", sa.get("Casa_PF_G", 0), sb.get("Casa_PF_G", 0), higher_is_better=True)
        render_comp_bar("Rendimento in Trasferta (PF/G)", sa.get("Trasf_PF_G", 0), sb.get("Trasf_PF_G", 0), higher_is_better=True)

    with c_right:
        st.markdown(f"""
        <div class="metric-card" style="border-top:3px solid #3b82f6;">
            <div style="font-size:1.5rem;">{LOGOS.get(team_b, '🏀')}</div>
            <div style="font-weight:700;font-size:1.05rem;">{team_b}</div>
            <div style="color:#94a3b8;font-size:0.8rem;">Posizione: <strong>#{sb.get('Pos', '-')}</strong> ({sb.get('V', 0)}V - {sb.get('P', 0)}P)</div>
            <div style="margin-top:6px;">{format_form_badges(sb.get('Forma', []))}</div>
        </div>
        """, unsafe_allow_html=True)

    # Spaccato Quarti & Trend Punti dell'Avversaria
    st.markdown("---")
    col_q, col_trend = st.columns(2)
    with col_q:
        st.markdown(f"#### ⏱️ Analisi Quarti — {team_b}")
        qg_b = sb.get("Q_Gare", 0)
        if qg_b > 0:
            q_df = pd.DataFrame([
                {"Quarto": "1° Quarto", "Segnati": round(sb["Q1_F"]/qg_b, 1), "Subiti": round(sb["Q1_S"]/qg_b, 1), "Diff": round((sb["Q1_F"]-sb["Q1_S"])/qg_b, 1)},
                {"Quarto": "2° Quarto", "Segnati": round(sb["Q2_F"]/qg_b, 1), "Subiti": round(sb["Q2_S"]/qg_b, 1), "Diff": round((sb["Q2_F"]-sb["Q2_S"])/qg_b, 1)},
                {"Quarto": "3° Quarto", "Segnati": round(sb["Q3_F"]/qg_b, 1), "Subiti": round(sb["Q3_S"]/qg_b, 1), "Diff": round((sb["Q3_F"]-sb["Q3_S"])/qg_b, 1)},
                {"Quarto": "4° Quarto", "Segnati": round(sb["Q4_F"]/qg_b, 1), "Subiti": round(sb["Q4_S"]/qg_b, 1), "Diff": round((sb["Q4_F"]-sb["Q4_S"])/qg_b, 1)},
            ])
            best_q = q_df.loc[q_df["Diff"].idxmax()]
            worst_q = q_df.loc[q_df["Diff"].idxmin()]
            st.caption(f"🔥 Quarto migliore: **{best_q['Quarto']}** ({best_q['Diff']:+.1f}) • ❄️ Quarto debole: **{worst_q['Quarto']}** ({worst_q['Diff']:+.1f})")
            st.dataframe(q_df, use_container_width=True, hide_index=True)
        else:
            st.info("Nessun parziale quarto disponibile per questa squadra.")

    with col_trend:
        st.markdown(f"#### 📈 Andamento Gara per Gara — {team_b}")
        b_matches = sorted(
            [p for p in girone_data["partite"] if p.get("giocata") and p.get("trasferta") != "Riposo" and (p["casa"] == team_b or p["trasferta"] == team_b)],
            key=lambda x: x.get("giornata", 0)
        )
        if b_matches:
            trend_rows = []
            for m in b_matches:
                is_home = (m["casa"] == team_b)
                pf = m["pt_casa"] if is_home else m["pt_trasferta"]
                ps = m["pt_trasferta"] if is_home else m["pt_casa"]
                opp = m["trasferta"] if is_home else m["casa"]
                trend_rows.append({
                    "Giornata": f"G{m['giornata']} ({'C' if is_home else 'T'} vs {opp[:10]})",
                    "Punti Segnati": pf,
                    "Punti Subiti": ps
                })
            df_tr = pd.DataFrame(trend_rows)
            st.line_chart(df_tr.set_index("Giornata")[["Punti Segnati", "Punti Subiti"]], height=210)
        else:
            st.info("Nessuna gara giocata da visualizzare.")

    # Giocatori più pericolosi dell'avversaria
    st.markdown("---")
    st.markdown(f"#### 🚨 Giocatori Più Pericolosi — {team_b}")
    all_players = get_all_players_stats_summary(girone_data, st.session_state.league_data.get("player_stats", {}))
    opp_players = [p for p in all_players if p["Squadra"] == team_b]

    if opp_players:
        top3 = opp_players[:3]
        cols_t3 = st.columns(len(top3))
        for idx, pl in enumerate(top3):
            with cols_t3[idx]:
                st.markdown(f"""
                <div class="metric-card" style="text-align:left;border-left:3px solid #ef4444;">
                    <div style="font-size:0.75rem;color:#ef4444;font-weight:700;">MINACCIA #{idx+1} • {pl['Profilo']}</div>
                    <div style="font-size:1.1rem;font-weight:700;margin:2px 0;">#{pl['N°']} {pl['Giocatore']}</div>
                    <div style="font-family:'Oswald',sans-serif;font-size:1.45rem;color:#f97316;">{pl['PPG']} PPG <span style="font-size:0.8rem;color:#94a3b8;">({pl['Share_PTS']}% pt squadra)</span></div>
                    <div style="font-size:0.76rem;color:#cbd5e1;margin-top:4px;">High: <strong>{pl['High']}</strong> • 3PT/G: <strong>{pl['3PG']}</strong> • TL: <strong>{pl['TL_PCT']}%</strong> • Falli/G: <strong>{pl['FPG']}</strong></div>
                </div>
                """, unsafe_allow_html=True)

        df_opp = pd.DataFrame(opp_players)[["N°", "Giocatore", "Profilo", "G", "MPG", "PPG", "High", "Share_PTS", "3PG", "TL_PCT", "FPG"]]
        df_opp = df_opp.rename(columns={"Share_PTS": "% PT Sq.", "TL_PCT": "TL %"})
        st.dataframe(df_opp, use_container_width=True, hide_index=True)
    else:
        st.warning(f"Nessun tabellino individuale caricato finora per **{team_b}**. Inserisci i tabellini delle sue partite in **⚙️ Gestione Dati & Tabellini** per sbloccare l'analisi dei giocatori pericolosi.")

    # Ultime Gare delle due squadre
    st.markdown("---")
    c_hist_a, c_hist_b = st.columns(2)
    with c_hist_a:
        st.markdown(f"#### 📋 Ultime Gare — {team_a}")
        matches_a = sorted([p for p in girone_data["partite"] if p.get("giocata") and (p["casa"] == team_a or p["trasferta"] == team_a)], key=lambda x: -x.get("giornata", 0))
        for m in matches_a[:4]:
            render_match_card(m, team_a, show_boxscore_btn=True, key_prefix="scout_a")
    with c_hist_b:
        st.markdown(f"#### 📋 Ultime Gare — {team_b}")
        matches_b = sorted([p for p in girone_data["partite"] if p.get("giocata") and (p["casa"] == team_b or p["trasferta"] == team_b)], key=lambda x: -x.get("giornata", 0))
        for m in matches_b[:4]:
            render_match_card(m, team_b, show_boxscore_btn=True, key_prefix="scout_b")

def view_giocatori_pericolosi(girone_data):
    st.markdown("### 🔥 Classifica Marcatori & Giocatori Più Pericolosi del Girone")
    st.caption("Analisi individuale su tutte le partite con tabellino inserito: media punti, peso sull'attacco della squadra (% PT Sq.), pericolosità perimetrale e falli.")

    all_players = get_all_players_stats_summary(girone_data, st.session_state.league_data.get("player_stats", {}))
    if not all_players:
        st.info("Nessun tabellino individuale disponibile nel girone. Vai su **⚙️ Gestione Dati & Tabellini** per inserire le statistiche delle partite.")
        return

    col_f1, col_f2, col_f3 = st.columns([2, 1.5, 1.5])
    with col_f1:
        team_filter = st.selectbox("Filtra per Squadra", ["Tutte le Squadre"] + girone_data["squadre"], key="top_pl_team")
    with col_f2:
        prof_filter = st.selectbox("Filtra per Profilo Tattico", ["Tutti i Profili", "🎯 Tiratore 3PT", "⚡ Penetratore / Falli", "🏀 Finalizzatore Area", "🔄 Realizzatore Completo"], key="top_pl_prof")
    with col_f3:
        sort_by = st.selectbox("Ordina per", ["Media Punti (PPG)", "Incidenza Squadra (% PT)", "Massimo in una gara (High)", "Triple a Partita (3PG)", "Falli a Partita (FPG)"], key="top_pl_sort")

    filtered = all_players
    if team_filter != "Tutte le Squadre":
        filtered = [p for p in filtered if p["Squadra"] == team_filter]
    if prof_filter != "Tutti i Profili":
        filtered = [p for p in filtered if p["Profilo"] == prof_filter]

    sort_map = {
        "Media Punti (PPG)": lambda x: (-x["PPG"], -x["PTS"]),
        "Incidenza Squadra (% PT)": lambda x: (-x["Share_PTS"], -x["PPG"]),
        "Massimo in una gara (High)": lambda x: (-x["High"], -x["PPG"]),
        "Triple a Partita (3PG)": lambda x: (-x["3PG"], -x["PPG"]),
        "Falli a Partita (FPG)": lambda x: (-x["FPG"], -x["PPG"]),
    }
    filtered = sorted(filtered, key=sort_map[sort_by])

    if not filtered:
        st.warning("Nessun giocatore corrisponde ai filtri selezionati.")
        return

    # Podio Top 3
    top3 = filtered[:3]
    cols_p = st.columns(len(top3))
    for i, pl in enumerate(top3):
        with cols_p[i]:
            st.markdown(f"""
            <div class="metric-card" style="text-align:left;border-top:3px solid #f97316;">
                <div style="font-size:0.74rem;color:#94a3b8;">#{i+1} • {LOGOS.get(pl['Squadra'], '🏀')} {pl['Squadra']}</div>
                <div style="font-size:1.08rem;font-weight:700;margin:2px 0;">{pl['Giocatore']} <span style="color:#64748b;font-size:0.85rem;">(#{pl['N°']})</span></div>
                <div style="font-family:'Oswald',sans-serif;font-size:1.5rem;color:#f97316;">{pl['PPG']} PPG <span style="font-size:0.8rem;color:#22c55e;">({pl['Share_PTS']}% pt sq.)</span></div>
                <div style="font-size:0.75rem;color:#cbd5e1;margin-top:4px;">{pl['Profilo']} • High: <strong>{pl['High']}</strong> • 3PT/G: <strong>{pl['3PG']}</strong></div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("#### 📊 Tabella Completa Giocatori")
    df_players = pd.DataFrame(filtered)[
        ["Squadra", "N°", "Giocatore", "Profilo", "G", "MPG", "PTS", "PPG", "High", "Share_PTS", "3PG", "TL_PCT", "Games_15plus", "FPG"]
    ].rename(columns={
        "Share_PTS": "% PT Sq.",
        "TL_PCT": "TL %",
        "Games_15plus": "Gare ≥15pt"
    })
    st.dataframe(df_players, use_container_width=True, hide_index=True)

def view_calendario(girone_data):
    st.markdown(f"### 📅 Calendario & Risultati — {girone_data['nome']}")

    partite = girone_data["partite"]
    giornate = sorted(list({p["giornata"] for p in partite}))
    squadre = ["Tutte le Squadre"] + girone_data["squadre"]

    col_f1, col_f2, col_f3 = st.columns([1.2, 1.8, 1.2])
    with col_f1:
        sel_giornata = st.selectbox("Giornata", ["Tutte le Giornate"] + [f"Giornata {g}" for g in giornate], key="cal_giornata")
    with col_f2:
        sel_squadra = st.selectbox("Filtra per Squadra", squadre, key="cal_squadra")
    with col_f3:
        sel_stato = st.selectbox("Stato", ["Tutte", "Giocate", "Da Giocare"], key="cal_stato")

    filtered = partite
    if sel_giornata != "Tutte le Giornate":
        g_num = int(sel_giornata.replace("Giornata ", ""))
        filtered = [p for p in filtered if p["giornata"] == g_num]
    if sel_squadra != "Tutte le Squadre":
        filtered = [p for p in filtered if p["casa"] == sel_squadra or p["trasferta"] == sel_squadra]
    if sel_stato == "Giocate":
        filtered = [p for p in filtered if p.get("giocata")]
    elif sel_stato == "Da Giocare":
        filtered = [p for p in filtered if not p.get("giocata")]

    if not filtered:
        st.info("Nessuna partita trovata con i filtri selezionati.")
        return

    by_round = {}
    for p in sorted(filtered, key=lambda x: (x["giornata"], x.get("data", ""))):
        by_round.setdefault(p["giornata"], []).append(p)

    for g_num, matches in by_round.items():
        st.markdown(f"#### Giornata {g_num}")
        for m in matches:
            render_match_card(m, st.session_state.fav_team, show_boxscore_btn=True, key_prefix=f"cal_{g_num}")

def view_squadra(girone_data, standings):
    teams = girone_data["squadre"]
    default_idx = teams.index(st.session_state.fav_team) if st.session_state.fav_team in teams else 0
    sel_team = st.selectbox("Seleziona Squadra da Analizzare", teams, index=default_idx, key="team_page_select")

    team_row = next((r for r in standings if r["Squadra"] == sel_team), None)
    logo = LOGOS.get(sel_team, "🏀")

    st.markdown(f"### {logo} Scheda Squadra — {sel_team}")

    if team_row:
        st.markdown(f"""
        <div class="metric-grid">
            <div class="metric-card"><div class="metric-val">#{team_row['Pos']}</div><div class="metric-lbl">Posizione</div></div>
            <div class="metric-card"><div class="metric-val">{team_row['PTI']}</div><div class="metric-lbl">Punti Classifica</div></div>
            <div class="metric-card"><div class="metric-val">{team_row['V']}-{team_row['P']}</div><div class="metric-lbl">Record V-P ({team_row['WIN_PCT']}%)</div></div>
            <div class="metric-card"><div class="metric-val">{team_row['PF_G']}</div><div class="metric-lbl">Punti Segnati / G</div></div>
            <div class="metric-card"><div class="metric-val">{team_row['PS_G']}</div><div class="metric-lbl">Punti Subiti / G</div></div>
            <div class="metric-card"><div class="metric-val">{team_row['Casa_V']}-{team_row['Casa_P']} / {team_row['Trasf_V']}-{team_row['Trasf_P']}</div><div class="metric-lbl">Casa / Trasferta</div></div>
        </div>
        """, unsafe_allow_html=True)

    tab_gioc, tab_part = st.tabs(["👥 Roster & Statistiche Giocatori", "📅 Partite della Squadra"])

    with tab_gioc:
        player_stats_db = st.session_state.league_data.get("player_stats", {})
        partite_map = {p["id"]: p for p in girone_data["partite"]}
        agg = {}
        is_toritto = is_toritto_team(sel_team)

        for match_id, sides in player_stats_db.items():
            match = partite_map.get(match_id)
            if not match or not match.get("giocata"):
                continue
            side_key = None
            if match["casa"] == sel_team:
                side_key = "home"
            elif match["trasferta"] == sel_team:
                side_key = "away"
            if not side_key:
                continue

            team_pts_match = match["pt_casa"] if side_key == "home" else match["pt_trasferta"]
            rows = sides.get(side_key, [])
            for r in rows:
                g_name = str(r.get("Giocatore", "")).strip()
                if not g_name:
                    continue
                if g_name not in agg:
                    agg[g_name] = {
                        "Giocatore": g_name,
                        "N°": int(r.get("N°", 0) or 0),
                        "G": 0, "Q_G": 0, "MIN": 0, "PTS": 0, "High": 0,
                        "2P_R": 0, "2P_T": 0, "3P_R": 0, "3P_T": 0,
                        "TL_R": 0, "TL_T": 0, "RO": 0, "RD": 0,
                        "ASS": 0, "PR": 0, "PP": 0, "ST": 0, "FF": 0, "FS": 0, "VAL": 0,
                        "Team_PTS": 0
                    }
                pts = int(r.get("PTS", 0) or 0)
                agg[g_name]["G"] += 1
                if r.get("Q"):
                    agg[g_name]["Q_G"] += 1
                agg[g_name]["MIN"] += int(r.get("MIN", 0) or 0)
                agg[g_name]["PTS"] += pts
                agg[g_name]["High"] = max(agg[g_name]["High"], pts)
                agg[g_name]["2P_R"] += int(r.get("2P R", 0) or 0)
                agg[g_name]["2P_T"] += int(r.get("2P T", 0) or 0)
                agg[g_name]["3P_R"] += int(r.get("3P R", 0) or 0)
                agg[g_name]["3P_T"] += int(r.get("3P T", 0) or 0)
                agg[g_name]["TL_R"] += int(r.get("TL R", 0) or 0)
                agg[g_name]["TL_T"] += int(r.get("TL T", 0) or 0)
                agg[g_name]["RO"] += int(r.get("RO", 0) or 0)
                agg[g_name]["RD"] += int(r.get("RD", 0) or 0)
                agg[g_name]["ASS"] += int(r.get("ASS", 0) or 0)
                agg[g_name]["PR"] += int(r.get("PR", 0) or 0)
                agg[g_name]["PP"] += int(r.get("PP", 0) or 0)
                agg[g_name]["ST"] += int(r.get("ST", 0) or 0)
                agg[g_name]["FF"] += int(r.get("FF", 0) or 0)
                agg[g_name]["FS"] += int(r.get("FS", 0) or 0)
                agg[g_name]["VAL"] += calc_pir(r)
                agg[g_name]["Team_PTS"] += int(team_pts_match or 0)

        if not agg:
            st.info(f"Nessuna statistica individuale registrata finora per **{sel_team}**.")
        else:
            summary_rows = []
            for g in agg.values():
                gp = g["G"]
                share_pt = round((g["PTS"] / g["Team_PTS"]) * 100, 1) if g["Team_PTS"] > 0 else 0.0
                if is_toritto:
                    reb_tot = g["RO"] + g["RD"]
                    p2_pct = round((g["2P_R"] / g["2P_T"]) * 100, 1) if g["2P_T"] > 0 else 0.0
                    p3_pct = round((g["3P_R"] / g["3P_T"]) * 100, 1) if g["3P_T"] > 0 else 0.0
                    tl_pct = round((g["TL_R"] / g["TL_T"]) * 100, 1) if g["TL_T"] > 0 else 0.0
                    summary_rows.append({
                        "N°": g["N°"],
                        "Giocatore": g["Giocatore"],
                        "G": gp,
                        "Q": g["Q_G"],
                        "MPG": round(g["MIN"] / gp, 1),
                        "PTS": g["PTS"],
                        "PPG": round(g["PTS"] / gp, 1),
                        "High": g["High"],
                        "% PT Sq.": share_pt,
                        "2P %": p2_pct,
                        "3P %": p3_pct,
                        "TL %": tl_pct,
                        "RPG": round(reb_tot / gp, 1),
                        "APG": round(g["ASS"] / gp, 1),
                        "SPG": round(g["PR"] / gp, 1),
                        "FPG": round(g["FF"] / gp, 1),
                        "VAL/G": round(g["VAL"] / gp, 1),
                    })
                else:
                    tl_pct = round((g["TL_R"] / g["TL_T"]) * 100, 1) if g["TL_T"] > 0 else 0.0
                    summary_rows.append({
                        "N°": g["N°"],
                        "Giocatore": g["Giocatore"],
                        "G": gp,
                        "Q": g["Q_G"],
                        "MPG": round(g["MIN"] / gp, 1),
                        "PTS": g["PTS"],
                        "PPG": round(g["PTS"] / gp, 1),
                        "High": g["High"],
                        "% PT Sq.": share_pt,
                        "2P R": g["2P_R"],
                        "3P R": g["3P_R"],
                        "TL R": g["TL_R"],
                        "TL T": g["TL_T"],
                        "TL %": tl_pct,
                        "FF": g["FF"],
                        "FPG": round(g["FF"] / gp, 1),
                    })
            df_sum = pd.DataFrame(summary_rows).sort_values(by=["PPG", "PTS"], ascending=False)
            st.dataframe(df_sum, use_container_width=True, hide_index=True)

    with tab_part:
        team_matches = [p for p in girone_data["partite"] if p["casa"] == sel_team or p["trasferta"] == sel_team]
        team_matches.sort(key=lambda x: x["giornata"])
        for m in team_matches:
            render_match_card(m, sel_team, show_boxscore_btn=True, key_prefix=f"sq_{sel_team}")

def view_gestione_dati(girone_data):
    st.markdown("### ⚙️ Gestione Dati, Roster & Tabellini")
    st.caption("Aggiorna risultati, inserisci tabellini (con auto-caricamento del roster della squadra) o gestisci i roster delle squadre.")

    tab_ris, tab_box, tab_ros, tab_new = st.tabs([
        "📝 Aggiorna Risultati",
        "📊 Inserisci / Modifica Tabellini",
        "👥 Gestione Roster Squadre",
        "➕ Aggiungi Nuova Partita"
    ])

    # 1. Aggiorna Risultati
    with tab_ris:
        partite = sorted(girone_data["partite"], key=lambda x: (x["giornata"], x.get("data", "")))
        match_labels = {
            f"G{p['giornata']} • {p['casa']} vs {p['trasferta']} ({'Giocata: ' + str(p['pt_casa']) + '-' + str(p['pt_trasferta']) if p.get('giocata') else 'Da giocare'})": p
            for p in partite if p["trasferta"] != "Riposo"
        }
        sel_lbl = st.selectbox("Seleziona Partita", list(match_labels.keys()), key="edit_match_sel")
        m = match_labels[sel_lbl]

        with st.form("form_edit_match"):
            c1, c2, c3 = st.columns(3)
            with c1:
                new_pt_c = st.number_input(f"Punti {m['casa']}", min_value=0, max_value=200, value=int(m["pt_casa"] or 0))
            with c2:
                new_pt_t = st.number_input(f"Punti {m['trasferta']}", min_value=0, max_value=200, value=int(m["pt_trasferta"] or 0))
            with c3:
                new_giocata = st.checkbox("Partita Giocata (Ufficiale)", value=bool(m.get("giocata", False)))

            c4, c5, c6 = st.columns(3)
            with c4:
                new_data = st.text_input("Data (YYYY-MM-DD)", value=m.get("data", ""))
            with c5:
                new_ora = st.text_input("Ora", value=m.get("ora", "18:30"))
            with c6:
                new_quarti = st.text_input("Parziali Quarti (es. 20-15, 18-19, 21-17, 19-16)", value=m.get("quarti", ""))

            if st.form_submit_button("💾 Salva Risultato", type="primary"):
                m["pt_casa"] = int(new_pt_c) if new_giocata else None
                m["pt_trasferta"] = int(new_pt_t) if new_giocata else None
                m["giocata"] = new_giocata
                m["data"] = new_data.strip()
                m["ora"] = new_ora.strip()
                m["quarti"] = new_quarti.strip()
                save_data(st.session_state.league_data)
                st.success("Risultato aggiornato e salvato con successo!")
                st.rerun()

    # 2. Inserisci / Modifica Tabellini (con caricamento automatico del roster della squadra)
    with tab_box:
        partite_giocate = [p for p in girone_data["partite"] if p.get("giocata") and p["trasferta"] != "Riposo"]
        if not partite_giocate:
            st.info("Segna prima almeno una partita come 'Giocata' per inserirne il tabellino.")
        else:
            box_labels = {
                f"G{p['giornata']} • {p['casa']} {p['pt_casa']} - {p['pt_trasferta']} {p['trasferta']}": p
                for p in sorted(partite_giocate, key=lambda x: (x["giornata"], x.get("data", "")))
            }
            sel_box_lbl = st.selectbox("Seleziona Partita Giocata", list(box_labels.keys()), key="box_match_sel")
            bm = box_labels[sel_box_lbl]
            bm_id = bm["id"]

            side_choice = st.radio(
                "Squadra del Tabellino",
                [f"Casa: {bm['casa']}", f"Trasferta: {bm['trasferta']}"],
                horizontal=True,
                key="box_side_radio"
            )
            side_key = "home" if side_choice.startswith("Casa:") else "away"
            team_name_editing = bm["casa"] if side_key == "home" else bm["trasferta"]
            is_toritto_editing = is_toritto_team(team_name_editing)

            existing_rows = st.session_state.league_data.get("player_stats", {}).get(bm_id, {}).get(side_key, [])
            if not existing_rows:
                saved_roster = get_team_roster(team_name_editing)
                if saved_roster:
                    st.info(f"📋 Caricato automaticamente il roster salvato di **{team_name_editing}** ({len(saved_roster)} giocatori). Compila solo i numeri della partita!")
                    if is_toritto_editing:
                        existing_rows = [
                            {
                                "Giocatore": p["Giocatore"], "N°": p["N°"], "Q": False, "MIN": 0, "PTS": 0,
                                "2P R": 0, "2P T": 0, "3P R": 0, "3P T": 0,
                                "TL R": 0, "TL T": 0, "RO": 0, "RD": 0,
                                "ASS": 0, "PR": 0, "PP": 0, "ST": 0, "FF": 0, "FS": 0
                            }
                            for p in saved_roster
                        ]
                    else:
                        existing_rows = [
                            {
                                "Giocatore": p["Giocatore"], "N°": p["N°"], "Q": False, "MIN": 0,
                                "FF": 0, "2P R": 0, "3P R": 0, "TL R": 0, "TL T": 0, "PTS": 0
                            }
                            for p in saved_roster
                        ]
                else:
                    if is_toritto_editing:
                        existing_rows = [
                            {
                                "Giocatore": "", "N°": 0, "Q": False, "MIN": 0, "PTS": 0,
                                "2P R": 0, "2P T": 0, "3P R": 0, "3P T": 0,
                                "TL R": 0, "TL T": 0, "RO": 0, "RD": 0,
                                "ASS": 0, "PR": 0, "PP": 0, "ST": 0, "FF": 0, "FS": 0
                            }
                        ]
                    else:
                        existing_rows = [
                            {
                                "Giocatore": "", "N°": 0, "Q": False, "MIN": 0,
                                "FF": 0, "2P R": 0, "3P R": 0, "TL R": 0, "TL T": 0, "PTS": 0
                            }
                        ]

            if is_toritto_editing:
                st.caption(f"Tabellino completo attivo per **{team_name_editing}**. I punti (PTS) vengono ricalcolati in automatico da 2P R, 3P R e TL R al salvataggio.")
                toritto_cols = ["Giocatore", "N°", "Q", "MIN", "PTS", "2P R", "2P T", "3P R", "3P T", "TL R", "TL T", "RO", "RD", "ASS", "PR", "PP", "ST", "FF", "FS"]
                df_editor = pd.DataFrame(existing_rows)
                for col in toritto_cols:
                    if col not in df_editor.columns:
                        df_editor[col] = False if col == "Q" else ("" if col == "Giocatore" else 0)
                df_editor = df_editor[toritto_cols]

                edited_df = st.data_editor(
                    df_editor,
                    num_rows="dynamic",
                    use_container_width=True,
                    key=f"editor_{bm_id}_{side_key}_toritto",
                    column_config={
                        "Q": st.column_config.CheckboxColumn("Q (Quintetto)", default=False),
                        "PTS": st.column_config.NumberColumn("PTS (Auto)", disabled=True),
                    }
                )
            else:
                st.caption(f"Scheda essenziale per **{team_name_editing}**: Giocatore, N°, Quintetto (Q), Minuti (MIN), Falli (FF), 2PT segnati, 3PT segnati, Tiri Liberi segnati (TL R) e tentati (TL T). I punti (PTS) vengono calcolati in automatico.")
                opp_cols = ["Giocatore", "N°", "Q", "MIN", "FF", "2P R", "3P R", "TL R", "TL T", "PTS"]
                df_editor = pd.DataFrame(existing_rows)
                for col in opp_cols:
                    if col not in df_editor.columns:
                        df_editor[col] = False if col == "Q" else ("" if col == "Giocatore" else 0)
                df_editor = df_editor[opp_cols]

                edited_df = st.data_editor(
                    df_editor,
                    num_rows="dynamic",
                    use_container_width=True,
                    key=f"editor_{bm_id}_{side_key}_opp",
                    column_config={
                        "Q": st.column_config.CheckboxColumn("Q (Quintetto)", default=False),
                        "PTS": st.column_config.NumberColumn("PTS (Auto)", disabled=True),
                    }
                )

            c_save1, c_save2 = st.columns([1.2, 1.5])
            with c_save1:
                also_update_roster = st.checkbox("Aggiorna anche il roster salvato della squadra con questi giocatori", value=True)
            with c_save2:
                if st.button("💾 Salva Tabellino Giocatori", type="primary", use_container_width=True):
                    if "player_stats" not in st.session_state.league_data:
                        st.session_state.league_data["player_stats"] = {}
                    if bm_id not in st.session_state.league_data["player_stats"]:
                        st.session_state.league_data["player_stats"][bm_id] = {}

                    clean_rows = sanitize_toritto_rows(edited_df) if is_toritto_editing else sanitize_opponent_rows(edited_df)
                    st.session_state.league_data["player_stats"][bm_id][side_key] = clean_rows

                    if also_update_roster and clean_rows:
                        existing_roster = get_team_roster(team_name_editing)
                        roster_map = {r["Giocatore"]: r["N°"] for r in existing_roster}
                        for r in clean_rows:
                            roster_map[r["Giocatore"]] = r["N°"]
                        merged_roster = [{"Giocatore": k, "N°": v} for k, v in roster_map.items()]
                        save_team_roster(team_name_editing, merged_roster)
                    else:
                        save_data(st.session_state.league_data)

                    tot_pts_calc = sum(r["PTS"] for r in clean_rows)
                    st.success(f"Tabellino salvato per {team_name_editing} ({len(clean_rows)} giocatori, totale {tot_pts_calc} punti)!")
                    st.rerun()

    # 3. Gestione Roster Squadre
    with tab_ros:
        st.markdown("#### 👥 Roster Ufficiali delle Squadre")
        st.caption("Salva una volta i giocatori e i numeri di maglia di una squadra: ogni volta che inserirai un nuovo tabellino per quella squadra, i nomi verranno caricati automaticamente.")
        sel_ros_team = st.selectbox("Seleziona Squadra", girone_data["squadre"], key="ros_team_sel")
        current_roster = get_team_roster(sel_ros_team)

        if not current_roster:
            df_ros = pd.DataFrame([{"N°": 0, "Giocatore": ""}])
        else:
            df_ros = pd.DataFrame(current_roster)[["N°", "Giocatore"]]

        edited_ros = st.data_editor(
            df_ros,
            num_rows="dynamic",
            use_container_width=True,
            key=f"ros_editor_{sel_ros_team}"
        )

        if st.button("💾 Salva Roster Squadra", type="primary"):
            ros_rows = []
            for _, r in edited_ros.iterrows():
                nome = str(r.get("Giocatore", "")).strip()
                if nome:
                    ros_rows.append({"N°": int(r.get("N°", 0) or 0), "Giocatore": nome})
            save_team_roster(sel_ros_team, ros_rows)
            st.success(f"Roster salvato per {sel_ros_team} ({len(ros_rows)} giocatori)!")
            st.rerun()

    # 4. Aggiungi Nuova Partita
    with tab_new:
        with st.form("form_new_match"):
            c1, c2, c3 = st.columns(3)
            with c1:
                n_giornata = st.number_input("Giornata", min_value=1, max_value=40, value=5)
            with c2:
                n_data = st.text_input("Data (YYYY-MM-DD)", value="2025-11-15")
            with c3:
                n_ora = st.text_input("Ora", value="18:30")

            c4, c5 = st.columns(2)
            with c4:
                n_casa = st.selectbox("Squadra Casa", girone_data["squadre"], index=0)
            with c5:
                n_trasf = st.selectbox("Squadra Trasferta", girone_data["squadre"] + ["Riposo"], index=1)

            c6, c7, c8 = st.columns(3)
            with c6:
                n_giocata = st.checkbox("Già Giocata?", value=False)
            with c7:
                n_pt_c = st.number_input("Punti Casa", min_value=0, max_value=200, value=0)
            with c8:
                n_pt_t = st.number_input("Punti Trasferta", min_value=0, max_value=200, value=0)

            n_quarti = st.text_input("Parziali Quarti (opzionale)", value="")

            if st.form_submit_button("➕ Aggiungi Partita al Calendario", type="primary"):
                if n_casa == n_trasf:
                    st.error("La squadra di casa e quella in trasferta non possono coincidere.")
                else:
                    new_match = {
                        "id": f"girone_a_g{n_giornata}_{uuid.uuid4().hex[:6]}",
                        "giornata": int(n_giornata),
                        "data": n_data.strip(),
                        "ora": n_ora.strip(),
                        "casa": n_casa,
                        "trasferta": n_trasf,
                        "pt_casa": int(n_pt_c) if (n_giocata and n_trasf != "Riposo") else None,
                        "pt_trasferta": int(n_pt_t) if (n_giocata and n_trasf != "Riposo") else None,
                        "quarti": n_quarti.strip(),
                        "giocata": bool(n_giocata and n_trasf != "Riposo")
                    }
                    girone_data["partite"].append(new_match)
                    save_data(st.session_state.league_data)
                    st.success("Partita aggiunta al calendario!")
                    st.rerun()

# ─── Main App Flow ───────────────────────────────────────────────────────────
def main():
    render_header()
    girone_data = st.session_state.league_data["girone_a"]
    standings = compute_standings(girone_data)

    # Barra Navigazione + Selettore Squadra Preferita
    col_nav, col_fav = st.columns([3.8, 1.2])
    with col_nav:
        page = st.radio(
            "Navigazione",
            [
                "🏆 Classifica",
                "🎯 Scouting Pre-Gara",
                "🔥 Top Marcatori & Minacce",
                "📅 Calendario",
                "🏀 Squadra",
                "⚙️ Gestione Dati"
            ],
            horizontal=True,
            label_visibility="collapsed"
        )
    with col_fav:
        teams = girone_data["squadre"]
        fav_idx = teams.index(st.session_state.fav_team) if st.session_state.fav_team in teams else 0
        st.session_state.fav_team = st.selectbox(
            "Squadra Evidenziata",
            teams,
            index=fav_idx,
            label_visibility="collapsed",
            help="Evidenzia la tua squadra in classifica, nel calendario e nello scouting pre-gara"
        )

    st.markdown("---")

    if page == "🏆 Classifica":
        view_classifica(girone_data, standings)
    elif page == "🎯 Scouting Pre-Gara":
        view_scouting_pre_gara(girone_data, standings)
    elif page == "🔥 Top Marcatori & Minacce":
        view_giocatori_pericolosi(girone_data)
    elif page == "📅 Calendario":
        view_calendario(girone_data)
    elif page == "🏀 Squadra":
        view_squadra(girone_data, standings)
    elif page == "⚙️ Gestione Dati":
        view_gestione_dati(girone_data)

if __name__ == "__main__":
    main()
