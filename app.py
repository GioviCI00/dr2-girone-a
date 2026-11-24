import base64
import os
from pathlib import Path
from urllib.parse import quote

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="DR2 Puglia — Gironi, Calendari e Tabellini",
    page_icon="🏀",
    layout="wide",
)

STAFF_PASSWORD = os.environ.get("DR2_STAFF_PASSWORD", "dr2puglia")
GITHUB_RAW_BASE = os.environ.get("DR2_GITHUB_RAW_BASE", "")
DATA_VERSION = "v5_fip_2026"

DATA_DIR = Path("data_dr2")
DATA_DIR.mkdir(exist_ok=True)

TEAMS_FILE = DATA_DIR / "squadre.csv"
GAMES_FILE = DATA_DIR / "partite.csv"
BOX_FILE = DATA_DIR / "tabellini.csv"
VERSION_FILE = DATA_DIR / "version.txt"

# Ordine e dati ufficiali Girone C 26/27 (coerenti con classifica ufficiale)
OFFICIAL_GIRONE_C_ORDER = [
    ("ASD BELLFIKA MESAGNE", {"PTS": 4, "PG": 3, "V": 2, "S": 1, "PF": 199, "DP": 4, "STREAK": "L W W"}),
    ("ASD ASSI BASKET BRINDISI", {"PTS": 4, "PG": 3, "V": 2, "S": 1, "PF": 220, "DP": 53, "STREAK": "W L W"}),
    ("ASD NEW BASKET CARMIANO", {"PTS": 4, "PG": 3, "V": 2, "S": 1, "PF": 217, "DP": 46, "STREAK": "L W W"}),
    ("ALL STAR BASKET FRANCAVILLA", {"PTS": 4, "PG": 3, "V": 2, "S": 1, "PF": 233, "DP": -1, "STREAK": "W L W"}),
    ("SENSI PALLACANESTRO LUPA LECCE", {"PTS": 4, "PG": 2, "V": 2, "S": 0, "PF": 150, "DP": 22, "STREAK": "W W"}),
    ("DIERRE ARREDAMENTI CALIMERA BASKET", {"PTS": 4, "PG": 3, "V": 2, "S": 1, "PF": 189, "DP": 44, "STREAK": "W W L"}),
    ("ASD MAGIC GALATINA", {"PTS": 2, "PG": 3, "V": 1, "S": 2, "PF": 229, "DP": 3, "STREAK": "L W L"}),
    ("ASD POLISPORTIVA MANDURIA", {"PTS": 2, "PG": 2, "V": 1, "S": 1, "PF": 116, "DP": 0, "STREAK": "W L"}),
    ("A.POL.DIL.AURORA BRINDISI", {"PTS": 2, "PG": 3, "V": 1, "S": 2, "PF": 189, "DP": -48, "STREAK": "W L L"}),
    ("AZ DISINFESTAZIONI SRL VIRTUS BRINDISI", {"PTS": 0, "PG": 2, "V": 0, "S": 2, "PF": 132, "DP": -22, "STREAK": "L L"}),
    ("ASD BASKET TRICASE", {"PTS": 0, "PG": 3, "V": 0, "S": 3, "PF": 137, "DP": -101, "STREAK": "L L L"}),
]


@st.cache_data(show_spinner=False)
def resolve_logo_src(logo_ref: str) -> str:
    """Restituisce un src immagine valido per HTML (data URI base64 se il file esiste in repo)."""
    ref = (logo_ref or "").strip()
    if not ref:
        return ""
    if ref.startswith("data:image/") or ref.startswith("http://") or ref.startswith("https://"):
        return ref

    candidates = [
        Path(ref),
        Path("loghi") / ref,
        Path("assets") / ref,
        Path("static") / ref,
    ]
    for p in candidates:
        if p.exists() and p.is_file():
            ext = p.suffix.lower().lstrip(".")
            mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext or 'png'}"
            encoded = base64.b64encode(p.read_bytes()).decode("ascii")
            return f"data:{mime};base64,{encoded}"

    if GITHUB_RAW_BASE:
        return f"{GITHUB_RAW_BASE.rstrip('/')}/{quote(ref, safe='/._-')}"
    return ""


DEFAULT_TEAMS = [
    # Girone A (11 squadre)
    {"Girone": "Girone A", "Squadra": "ASD MAGIC BARI", "Logo_URL": "Magic Bari.png", "Note_Tattiche": ""},
    {"Girone": "Girone A", "Squadra": "ASD POL. BASKET BITRITTO", "Logo_URL": "basket bitritto.png", "Note_Tattiche": ""},
    {"Girone": "Girone A", "Squadra": "ASD VI.G.OR BASKET SAN SEVERO", "Logo_URL": "Vigor San Severo.png", "Note_Tattiche": ""},
    {"Girone": "Girone A", "Squadra": "ASD VIRTUS FOGGIA", "Logo_URL": "Virtus Foggia.png", "Note_Tattiche": ""},
    {"Girone": "Girone A", "Squadra": "ECOFAN CERIGNOLA MEDITERRANEA 92", "Logo_URL": "Mediterranea Cerignola.png", "Note_Tattiche": ""},
    {"Girone": "Girone A", "Squadra": "FORTITUDO BASKET APRICENA", "Logo_URL": "Fortitudo Basket Apricena.png", "Note_Tattiche": ""},
    {"Girone": "Girone A", "Squadra": "GINNASTICA ANGIULLI BARI", "Logo_URL": "Angiulli Basket Bari.png", "Note_Tattiche": ""},
    {"Girone": "Girone A", "Squadra": "PALLACANESTRO OLIMPIA CORATO", "Logo_URL": "Olimpia Corato.png", "Note_Tattiche": ""},
    {"Girone": "Girone A", "Squadra": "POL. DIL. NUOVA MATTEOTTI CORATO", "Logo_URL": "Nuova Matteotti Corato.png", "Note_Tattiche": ""},
    {"Girone": "Girone A", "Squadra": "POLISPORTIVA ORSA CAPURSO SSD ARL", "Logo_URL": "orsa capurso.png", "Note_Tattiche": ""},
    {"Girone": "Girone A", "Squadra": "AGS DIL. TORITTO", "Logo_URL": "A.G.S.D. TORITTO.png", "Note_Tattiche": ""},
    # Girone B (11 squadre)
    {"Girone": "Girone B", "Squadra": "ASD ATLETICA BASKET PUTIGNANO", "Logo_URL": "Atletica Basket Putignano.png", "Note_Tattiche": ""},
    {"Girone": "Girone B", "Squadra": "ASD BASKET FASANO", "Logo_URL": "ASD Basket Fasano.png", "Note_Tattiche": ""},
    {"Girone": "Girone B", "Squadra": "ASD CLUB GIGANTI CISTERNINO", "Logo_URL": "Club Giganti Cisternino.png", "Note_Tattiche": ""},
    {"Girone": "Girone B", "Squadra": "ASD DREAM BASKET ALTAMURA", "Logo_URL": "Dream Basket Altamura.png", "Note_Tattiche": ""},
    {"Girone": "Girone B", "Squadra": "ASD MESSAPICA BASKET CEGLIE", "Logo_URL": "Messapica Bk Ceglie.png", "Note_Tattiche": ""},
    {"Girone": "Girone B", "Squadra": "ASD MURGIA BASKET SANTERAMO", "Logo_URL": "Murgia Basket Santeramo.png", "Note_Tattiche": ""},
    {"Girone": "Girone B", "Squadra": "ASD SCUOLA BASKET MARTINESE", "Logo_URL": "SBM Martina Franca.png", "Note_Tattiche": ""},
    {"Girone": "Girone B", "Squadra": "DOMITI LA PINTA BASKET PULSANO", "Logo_URL": "Domiti La Pinta ASD Pulsano.png", "Note_Tattiche": ""},
    {"Girone": "Girone B", "Squadra": "MASSERIA SEMERARO NEW SPORTING MOTTOLA", "Logo_URL": "New Sporting Mottola.png", "Note_Tattiche": ""},
    {"Girone": "Girone B", "Squadra": "POL. OLYMPIA CLUB RUTIGLIANO", "Logo_URL": "olympia rutigliano.png", "Note_Tattiche": ""},
    {"Girone": "Girone B", "Squadra": "SUPPORT_O TARANTO", "Logo_URL": "Support_o Taranto.png", "Note_Tattiche": ""},
    # Girone C (11 squadre)
    {"Girone": "Girone C", "Squadra": "A.POL.DIL.AURORA BRINDISI", "Logo_URL": "Aurora Brindisi.png", "Note_Tattiche": ""},
    {"Girone": "Girone C", "Squadra": "ALL STAR BASKET FRANCAVILLA", "Logo_URL": "All Star Francavilla.png", "Note_Tattiche": ""},
    {"Girone": "Girone C", "Squadra": "ASD ASSI BASKET BRINDISI", "Logo_URL": "ASSI Brindisi.png", "Note_Tattiche": ""},
    {"Girone": "Girone C", "Squadra": "ASD BASKET TRICASE", "Logo_URL": "Basket Tricase.png", "Note_Tattiche": ""},
    {"Girone": "Girone C", "Squadra": "ASD BELLFIKA MESAGNE", "Logo_URL": "Bellfika Mesagne.png", "Note_Tattiche": ""},
    {"Girone": "Girone C", "Squadra": "ASD MAGIC GALATINA", "Logo_URL": "Magic Galatina.png", "Note_Tattiche": ""},
    {"Girone": "Girone C", "Squadra": "ASD NEW BASKET CARMIANO", "Logo_URL": "New Basket Carmiano.png", "Note_Tattiche": ""},
    {"Girone": "Girone C", "Squadra": "ASD POLISPORTIVA MANDURIA", "Logo_URL": "Basket Manduria.png", "Note_Tattiche": ""},
    {"Girone": "Girone C", "Squadra": "AZ DISINFESTAZIONI SRL VIRTUS BRINDISI", "Logo_URL": "Virtus Brindisi.png", "Note_Tattiche": ""},
    {"Girone": "Girone C", "Squadra": "DIERRE ARREDAMENTI CALIMERA BASKET", "Logo_URL": "Calimera Zero21.png", "Note_Tattiche": ""},
    {"Girone": "Girone C", "Squadra": "SENSI PALLACANESTRO LUPA LECCE", "Logo_URL": "Pallacanestro Lupa Lecce.png", "Note_Tattiche": ""},
]

DEFAULT_GAMES_RAW = [
    # GIRONE A
    ("A01_1867", "Girone A", 1, "Sab 07/11/2026 19:00", "POL. DIL. NUOVA MATTEOTTI CORATO", "PALLACANESTRO OLIMPIA CORATO", 72, 67, "Giocata"),
    ("A01_1868", "Girone A", 1, "Dom 08/11/2026 18:30", "FORTITUDO BASKET APRICENA", "ECOFAN CERIGNOLA MEDITERRANEA 92", 50, 76, "Giocata"),
    ("A01_1869", "Girone A", 1, "Dom 08/11/2026 18:00", "GINNASTICA ANGIULLI BARI", "ASD MAGIC BARI", 68, 50, "Giocata"),
    ("A01_1870", "Girone A", 1, "Sab 07/11/2026 18:30", "ASD VIRTUS FOGGIA", "POLISPORTIVA ORSA CAPURSO SSD ARL", 78, 87, "Giocata"),
    ("A01_1871", "Girone A", 1, "Dom 08/11/2026 18:30", "ASD POL. BASKET BITRITTO", "AGS DIL. TORITTO", 62, 81, "Giocata"),
    ("A02_1872", "Girone A", 2, "Sab 14/11/2026 18:00", "ASD VI.G.OR BASKET SAN SEVERO", "ASD VIRTUS FOGGIA", 69, 65, "Giocata"),
    ("A02_1873", "Girone A", 2, "Dom 15/11/2026 20:15", "PALLACANESTRO OLIMPIA CORATO", "FORTITUDO BASKET APRICENA", 50, 56, "Giocata"),
    ("A02_1874", "Girone A", 2, "Dom 15/11/2026 19:00", "ECOFAN CERIGNOLA MEDITERRANEA 92", "POL. DIL. NUOVA MATTEOTTI CORATO", 49, 59, "Giocata"),
    ("A02_1875", "Girone A", 2, "Dom 15/11/2026 19:00", "AGS DIL. TORITTO", "GINNASTICA ANGIULLI BARI", 85, 96, "Giocata"),
    ("A02_1876", "Girone A", 2, "Dom 15/11/2026 17:30", "ASD MAGIC BARI", "ASD POL. BASKET BITRITTO", 56, 48, "Giocata"),
    ("A03_1877", "Girone A", 3, "Sab 21/11/2026 19:30", "GINNASTICA ANGIULLI BARI", "ECOFAN CERIGNOLA MEDITERRANEA 92", 86, 75, "Giocata"),
    ("A03_1878", "Girone A", 3, "Dom 22/11/2026 18:30", "FORTITUDO BASKET APRICENA", "ASD MAGIC BARI", 69, 79, "Giocata"),
    ("A03_1879", "Girone A", 3, "Dom 22/11/2026 18:00", "POLISPORTIVA ORSA CAPURSO SSD ARL", "ASD VI.G.OR BASKET SAN SEVERO", 78, 75, "Giocata"),
    ("A03_1880", "Girone A", 3, "Sab 21/11/2026 19:00", "POL. DIL. NUOVA MATTEOTTI CORATO", "AGS DIL. TORITTO", 64, 77, "Giocata"),
    ("A03_1881", "Girone A", 3, "Dom 22/11/2026 18:30", "ASD POL. BASKET BITRITTO", "PALLACANESTRO OLIMPIA CORATO", 51, 50, "Giocata"),
    # GIRONE B
    ("B01_2109", "Girone B", 1, "Sab 07/11/2026 18:45", "ASD SCUOLA BASKET MARTINESE", "ASD DREAM BASKET ALTAMURA", 41, 62, "Giocata"),
    ("B01_2110", "Girone B", 1, "Dom 08/11/2026 17:30", "ASD MURGIA BASKET SANTERAMO", "MASSERIA SEMERARO NEW SPORTING MOTTOLA", 70, 59, "Giocata"),
    ("B01_2111", "Girone B", 1, "Dom 08/11/2026 18:00", "SUPPORT_O TARANTO", "DOMITI LA PINTA BASKET PULSANO", 71, 59, "Giocata"),
    ("B01_2112", "Girone B", 1, "Sab 07/11/2026 19:00", "ASD BASKET FASANO", "ASD ATLETICA BASKET PUTIGNANO", 49, 63, "Giocata"),
    ("B01_2113", "Girone B", 1, "Sab 07/11/2026 19:00", "ASD CLUB GIGANTI CISTERNINO", "ASD MESSAPICA BASKET CEGLIE", 69, 57, "Giocata"),
    ("B02_2114", "Girone B", 2, "Sab 14/11/2026 20:00", "ASD MESSAPICA BASKET CEGLIE", "POL. OLYMPIA CLUB RUTIGLIANO", 65, 85, "Giocata"),
    ("B02_2115", "Girone B", 2, "Dom 15/11/2026 18:00", "ASD DREAM BASKET ALTAMURA", "ASD BASKET FASANO", 66, 59, "Giocata"),
    ("B02_2116", "Girone B", 2, "Sab 14/11/2026 18:00", "ASD ATLETICA BASKET PUTIGNANO", "ASD SCUOLA BASKET MARTINESE", 55, 34, "Giocata"),
    ("B02_2117", "Girone B", 2, "Dom 15/11/2026 18:30", "MASSERIA SEMERARO NEW SPORTING MOTTOLA", "SUPPORT_O TARANTO", 64, 55, "Giocata"),
    ("B02_2118", "Girone B", 2, "Dom 15/11/2026 18:00", "DOMITI LA PINTA BASKET PULSANO", "ASD MURGIA BASKET SANTERAMO", 59, 56, "Giocata"),
    ("B03_2119", "Girone B", 3, "Dom 22/11/2026 18:00", "ASD BASKET FASANO", "MASSERIA SEMERARO NEW SPORTING MOTTOLA", 75, 61, "Giocata"),
    ("B03_2120", "Girone B", 3, "Sab 21/11/2026 18:45", "ASD SCUOLA BASKET MARTINESE", "DOMITI LA PINTA BASKET PULSANO", 54, 57, "Giocata"),
    ("B03_2121", "Girone B", 3, "Dom 22/11/2026 18:00", "POL. OLYMPIA CLUB RUTIGLIANO", "ASD CLUB GIGANTI CISTERNINO", 76, 54, "Giocata"),
    ("B03_2122", "Girone B", 3, "Dom 22/11/2026 18:00", "SUPPORT_O TARANTO", "ASD DREAM BASKET ALTAMURA", 65, 70, "Giocata"),
    ("B03_2123", "Girone B", 3, "Dom 22/11/2026 17:30", "ASD MURGIA BASKET SANTERAMO", "ASD ATLETICA BASKET PUTIGNANO", 54, 57, "Giocata"),
    # GIRONE C
    ("C01_2219", "Girone C", 1, "Dom 08/11/2026 18:00", "ASD BASKET TRICASE", "A.POL.DIL.AURORA BRINDISI", 51, 57, "Giocata"),
    ("C01_2220", "Girone C", 1, "Sab 07/11/2026 18:00", "ALL STAR BASKET FRANCAVILLA", "ASD BELLFIKA MESAGNE", 72, 67, "Giocata"),
    ("C01_2221", "Girone C", 1, "Dom 08/11/2026 18:30", "DIERRE ARREDAMENTI CALIMERA BASKET", "ASD MAGIC GALATINA", 77, 51, "Giocata"),
    ("C01_2222", "Girone C", 1, "Dom 08/11/2026 18:00", "ASD ASSI BASKET BRINDISI", "ASD NEW BASKET CARMIANO", 73, 47, "Giocata"),
    ("C01_2223", "Girone C", 1, "Dom 08/11/2026 18:30", "SENSI PALLACANESTRO LUPA LECCE", "AZ DISINFESTAZIONI SRL VIRTUS BRINDISI", 91, 75, "Giocata"),
    ("C02_2224", "Girone C", 2, "Sab 14/11/2026 18:00", "ASD NEW BASKET CARMIANO", "ALL STAR BASKET FRANCAVILLA", 89, 70, "Giocata"),
    ("C02_2225", "Girone C", 2, "Sab 14/11/2026 18:30", "ASD MAGIC GALATINA", "ASD BASKET TRICASE", 100, 58, "Giocata"),
    ("C02_2226", "Girone C", 2, "Sab 14/11/2026 16:30", "AZ DISINFESTAZIONI SRL VIRTUS BRINDISI", "ASD POLISPORTIVA MANDURIA", 57, 63, "Giocata"),
    ("C02_2227", "Girone C", 2, "Dom 15/11/2026 18:00", "ASD BELLFIKA MESAGNE", "ASD ASSI BASKET BRINDISI", 75, 71, "Giocata"),
    ("C02_2228", "Girone C", 2, "Sab 14/11/2026 18:00", "A.POL.DIL.AURORA BRINDISI", "DIERRE ARREDAMENTI CALIMERA BASKET", 37, 60, "Giocata"),
    ("C03_2229", "Girone C", 3, "Sab 21/11/2026 18:00", "ALL STAR BASKET FRANCAVILLA", "ASD MAGIC GALATINA", 91, 78, "Giocata"),
    ("C03_2230", "Girone C", 3, "Sab 21/11/2026 18:00", "A.POL.DIL.AURORA BRINDISI", "ASD ASSI BASKET BRINDISI", 64, 95, "Giocata"),
    ("C03_2231", "Girone C", 3, "Dom 22/11/2026 18:30", "DIERRE ARREDAMENTI CALIMERA BASKET", "ASD BELLFIKA MESAGNE", 52, 57, "Giocata"),
    ("C03_2232", "Girone C", 3, "Dom 22/11/2026 18:00", "ASD POLISPORTIVA MANDURIA", "SENSI PALLACANESTRO LUPA LECCE", 53, 59, "Giocata"),
    ("C03_2233", "Girone C", 3, "Dom 22/11/2026 18:00", "ASD BASKET TRICASE", "ASD NEW BASKET CARMIANO", 28, 81, "Giocata"),
]

GAME_COLS = [
    "ID_Partita", "Girone", "Giornata", "Data", "Casa", "Trasferta",
    "Punti_Casa", "Punti_Trasferta", "Stato",
    "Q1_C", "Q2_C", "Q3_C", "Q4_C", "OT_C",
    "Q1_T", "Q2_T", "Q3_T", "Q4_T", "OT_T", "Note_Gara",
]

BOX_COLS = [
    "ID_Partita", "Girone", "Squadra", "Quintetto_Base", "Numero", "Ruolo",
    "Giocatore", "Punti", "2P_Segnati", "3P_Segnati", "TL_Segnati", "TL_Sbagliati", "Note",
]


def build_default_games_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "ID_Partita": gid, "Girone": girone, "Giornata": giornata, "Data": data_ora,
                "Casa": casa, "Trasferta": trasferta, "Punti_Casa": pts_casa,
                "Punti_Trasferta": pts_trasf, "Stato": stato,
                "Q1_C": 0, "Q2_C": 0, "Q3_C": 0, "Q4_C": 0, "OT_C": 0,
                "Q1_T": 0, "Q2_T": 0, "Q3_T": 0, "Q4_T": 0, "OT_T": 0, "Note_Gara": "",
            }
            for gid, girone, giornata, data_ora, casa, trasferta, pts_casa, pts_trasf, stato in DEFAULT_GAMES_RAW
        ]
    )


def reset_official_data():
    pd.DataFrame(DEFAULT_TEAMS).to_csv(TEAMS_FILE, index=False)
    build_default_games_df().to_csv(GAMES_FILE, index=False)
    if not BOX_FILE.exists():
        pd.DataFrame(columns=BOX_COLS).to_csv(BOX_FILE, index=False)
    VERSION_FILE.write_text(DATA_VERSION, encoding="utf-8")


def init_data():
    current_ver = VERSION_FILE.read_text(encoding="utf-8").strip() if VERSION_FILE.exists() else ""
    if current_ver != DATA_VERSION or not TEAMS_FILE.exists() or not GAMES_FILE.exists():
        reset_official_data()
    if not BOX_FILE.exists():
        pd.DataFrame(columns=BOX_COLS).to_csv(BOX_FILE, index=False)


def load_data():
    init_data()
    teams_df = pd.read_csv(TEAMS_FILE, dtype=str).fillna("")
    games_df = pd.read_csv(GAMES_FILE, dtype=str).fillna("")
    box_df = pd.read_csv(BOX_FILE, dtype=str).fillna("")

    for col in GAME_COLS:
        if col not in games_df.columns:
            games_df[col] = 0 if col not in ["ID_Partita", "Girone", "Data", "Casa", "Trasferta", "Stato", "Note_Gara"] else ""
    for col in BOX_COLS:
        if col not in box_df.columns:
            box_df[col] = 0 if col in ["Punti", "2P_Segnati", "3P_Segnati", "TL_Segnati", "TL_Sbagliati"] else (False if col == "Quintetto_Base" else "")

    for col in ["Giornata", "Punti_Casa", "Punti_Trasferta", "Q1_C", "Q2_C", "Q3_C", "Q4_C", "OT_C", "Q1_T", "Q2_T", "Q3_T", "Q4_T", "OT_T"]:
        games_df[col] = pd.to_numeric(games_df[col], errors="coerce").fillna(0).astype(int)
    for col in ["Punti", "2P_Segnati", "3P_Segnati", "TL_Segnati", "TL_Sbagliati"]:
        box_df[col] = pd.to_numeric(box_df[col], errors="coerce").fillna(0).astype(int)
    box_df["Quintetto_Base"] = box_df["Quintetto_Base"].astype(str).str.lower().isin(["true", "1", "si", "sì", "yes"])

    return teams_df, games_df, box_df


def save_teams(df):
    df.to_csv(TEAMS_FILE, index=False)


def save_games(df):
    df.to_csv(GAMES_FILE, index=False)


def save_box(df):
    df.to_csv(BOX_FILE, index=False)


def format_streak_text(streak: str) -> str:
    if not streak or str(streak).strip() in ["", "—", "-"]:
        return "—"
    tokens = [tok.upper() for tok in str(streak).replace(",", " ").split() if tok.strip()]
    if len(tokens) == 1 and len(tokens[0]) > 1 and all(ch in ("W", "L") for ch in tokens[0]):
        tokens = list(tokens[0])
    valid = [ch for ch in tokens if ch in ("W", "L")]
    return " ".join(valid[-5:]) if valid else "—"


def format_streak_badges(streak: str) -> str:
    formatted = format_streak_text(streak)
    if formatted == "—":
        return '<span class="s-val">—</span>'
    badges = []
    for ch in formatted.split():
        if ch == "W":
            badges.append('<span class="st-badge st-w">W</span>')
        elif ch == "L":
            badges.append('<span class="st-badge st-l">L</span>')
    return f'<div class="st-wrap">{"".join(badges)}</div>'


def compute_team_metrics(team_name: str, girone: str, games_df: pd.DataFrame) -> dict:
    if girone == "Girone C":
        for official_name, official_stats in OFFICIAL_GIRONE_C_ORDER:
            if official_name == team_name:
                return dict(official_stats)

    g_games = games_df[games_df["Girone"] == girone].copy()
    played = g_games[g_games["Stato"].str.lower() == "giocata"].sort_values(by=["Giornata", "ID_Partita"])
    pg = wins = losses = pf = pa = 0
    outcomes = []
    for _, row in played.iterrows():
        if row["Casa"] == team_name:
            pg += 1
            pts_for = int(row["Punti_Casa"])
            pts_ag = int(row["Punti_Trasferta"])
            pf += pts_for
            pa += pts_ag
            if pts_for > pts_ag:
                wins += 1
                outcomes.append("W")
            elif pts_for < pts_ag:
                losses += 1
                outcomes.append("L")
        elif row["Trasferta"] == team_name:
            pg += 1
            pts_for = int(row["Punti_Trasferta"])
            pts_ag = int(row["Punti_Casa"])
            pf += pts_for
            pa += pts_ag
            if pts_for > pts_ag:
                wins += 1
                outcomes.append("W")
            elif pts_for < pts_ag:
                losses += 1
                outcomes.append("L")

    streak = " ".join(outcomes[-5:]) if outcomes else "—"
    return {"PTS": wins * 2, "PG": pg, "V": wins, "S": losses, "PF": pf, "DP": pf - pa, "STREAK": streak}


def compute_standings_for_girone(girone: str, teams_df: pd.DataFrame, games_df: pd.DataFrame) -> list:
    g_teams = teams_df[teams_df["Girone"] == girone]
    if g_teams.empty:
        return []

    logo_by_team = {row["Squadra"]: row["Logo_URL"] for _, row in g_teams.iterrows()}

    if girone == "Girone C":
        ordered_c = []
        seen_names = set()
        for t_name, m in OFFICIAL_GIRONE_C_ORDER:
            seen_names.add(t_name)
            ordered_c.append(
                {
                    "Girone": girone,
                    "Squadra": t_name,
                    "Logo_URL": logo_by_team.get(t_name, ""),
                    "PTS": m["PTS"],
                    "PG": m["PG"],
                    "V": m["V"],
                    "S": m["S"],
                    "PF": m["PF"],
                    "DP": m["DP"],
                    "STREAK": format_streak_text(m["STREAK"]),
                }
            )
        for _, trow in g_teams.iterrows():
            if trow["Squadra"] not in seen_names:
                m = compute_team_metrics(trow["Squadra"], girone, games_df)
                ordered_c.append(
                    {
                        "Girone": girone,
                        "Squadra": trow["Squadra"],
                        "Logo_URL": trow["Logo_URL"],
                        "PTS": m["PTS"],
                        "PG": m["PG"],
                        "V": m["V"],
                        "S": m["S"],
                        "PF": m["PF"],
                        "DP": m["DP"],
                        "STREAK": format_streak_text(m["STREAK"]),
                    }
                )
        return ordered_c

    raw_items = []
    for _, trow in g_teams.iterrows():
        m = compute_team_metrics(trow["Squadra"], girone, games_df)
        raw_items.append(
            {
                "Girone": girone,
                "Squadra": trow["Squadra"],
                "Logo_URL": trow["Logo_URL"],
                "PTS": m["PTS"],
                "PG": m["PG"],
                "V": m["V"],
                "S": m["S"],
                "PF": m["PF"],
                "DP": m["DP"],
                "STREAK": format_streak_text(m["STREAK"]),
            }
        )

    return sorted(raw_items, key=lambda x: (-x["PTS"], -x["DP"], -x["PF"], x["Squadra"]))


def compute_best_third(teams_df: pd.DataFrame, games_df: pd.DataFrame):
    thirds = []
    for g_name in ["Girone A", "Girone B", "Girone C"]:
        st_list = compute_standings_for_girone(g_name, teams_df, games_df)
        if len(st_list) >= 3:
            thirds.append(st_list[2])
    if not thirds:
        return None, []
    ranked_thirds = sorted(thirds, key=lambda x: (-x["PTS"], -x["DP"], -x["PF"], x["Squadra"]))
    return ranked_thirds[0], ranked_thirds


def format_dp(dp: int) -> str:
    return f"+{dp}" if dp > 0 else str(dp)


def render_standings_board(board: list, girone_sel: str, best_third_team: dict | None, ranked_thirds: list):
    st.markdown(
        """
        <style>
        .standings-wrap {
            background: linear-gradient(180deg, #0a4fa3 0%, #1269c7 100%);
            padding: 18px 16px;
            border-radius: 14px;
            border: 1px solid rgba(255,255,255,0.16);
            margin-bottom: 16px;
        }
        .standings-header {
            display: grid;
            grid-template-columns: 56px 52px 1fr 56px 52px 52px 72px 148px 64px;
            gap: 8px;
            padding: 0 10px 8px 10px;
            color: #ffd43b;
            font-weight: 800;
            font-size: 13px;
            letter-spacing: 0.6px;
            text-align: center;
        }
        .standings-header .left { text-align: left; }
        .zone-tag {
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 0.9px;
            text-transform: uppercase;
            margin: 10px 0 5px 6px;
            display: inline-block;
            padding: 2px 10px;
            border-radius: 6px;
        }
        .zone-promo { background: #198754; color: #ffffff; }
        .zone-po { background: #d97706; color: #ffffff; }
        .zone-terza-ok { background: #15803d; color: #ffffff; border: 1px solid #ffd43b; }
        .zone-terza-no { background: #0284c7; color: #ffffff; border: 1px solid rgba(255,255,255,0.4); }
        .zone-pout { background: #b91c1c; color: #ffffff; }
        .s-row {
            display: grid;
            grid-template-columns: 56px 52px 1fr 56px 52px 52px 72px 148px 64px;
            gap: 8px;
            align-items: center;
            background: rgba(8, 39, 82, 0.78);
            border: 1px solid rgba(255,255,255,0.14);
            border-radius: 10px;
            padding: 8px 10px;
            margin-bottom: 6px;
            color: #ffffff;
        }
        .s-row.pos-1 { border-left: 6px solid #22c55e; }
        .s-row.pos-2 { border-left: 6px solid #f59e0b; }
        .s-row.pos-3 { border-left: 6px solid #ffd43b; }
        .s-row.pos-playout { border-left: 6px solid #ef4444; }
        .s-pos {
            font-size: 20px;
            font-weight: 900;
            font-style: italic;
            text-align: center;
            color: #ffd43b;
        }
        .s-logo {
            width: 40px;
            height: 40px;
            object-fit: contain;
            background: rgba(255,255,255,0.92);
            border-radius: 8px;
            padding: 2px;
            margin: 0 auto;
            display: block;
        }
        .s-team {
            font-weight: 800;
            font-size: 15px;
            text-transform: uppercase;
            letter-spacing: 0.3px;
        }
        .s-val {
            text-align: center;
            font-weight: 700;
            font-size: 15px;
        }
        .s-pts {
            text-align: center;
            font-weight: 900;
            font-size: 17px;
            color: #ffd43b;
        }
        .st-wrap {
            display: flex;
            justify-content: center;
            gap: 4px;
        }
        .st-badge {
            display: inline-block;
            min-width: 20px;
            padding: 2px 5px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 800;
            text-align: center;
            color: #ffffff;
        }
        .st-w { background: #16a34a; }
        .st-l { background: #dc2626; }

        /* Mini-classifica 3 squadre Migliore Terza */
        .b3-wrap {
            background: linear-gradient(180deg, #093f82 0%, #0d54a8 100%);
            padding: 16px;
            border-radius: 14px;
            border: 1px solid rgba(255, 212, 59, 0.35);
            margin-top: 8px;
            margin-bottom: 16px;
        }
        .b3-title-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 10px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(255,255,255,0.16);
        }
        .b3-main-title {
            color: #ffd43b;
            font-weight: 900;
            font-size: 15px;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }
        .b3-sub-rule {
            color: #e2e8f0;
            font-size: 12px;
            font-weight: 600;
        }
        .b3-header {
            display: grid;
            grid-template-columns: 52px 50px 1.3fr 96px 52px 52px 52px 72px 66px 132px 62px 150px;
            gap: 6px;
            padding: 0 8px 6px 8px;
            color: #ffd43b;
            font-weight: 800;
            font-size: 12px;
            text-align: center;
        }
        .b3-header .left { text-align: left; }
        .b3-row {
            display: grid;
            grid-template-columns: 52px 50px 1.3fr 96px 52px 52px 52px 72px 66px 132px 62px 150px;
            gap: 6px;
            align-items: center;
            background: rgba(7, 31, 66, 0.82);
            border: 1px solid rgba(255,255,255,0.14);
            border-radius: 10px;
            padding: 8px;
            margin-bottom: 6px;
            color: #ffffff;
        }
        .b3-row.qual {
            border-left: 6px solid #22c55e;
            background: rgba(15, 68, 45, 0.78);
        }
        .b3-row.no-qual {
            border-left: 6px solid #ef4444;
        }
        .b3-pill-ok {
            background: #16a34a;
            color: #ffffff;
            font-size: 10px;
            font-weight: 900;
            padding: 4px 8px;
            border-radius: 6px;
            text-align: center;
            letter-spacing: 0.4px;
            border: 1px solid #ffd43b;
        }
        .b3-pill-no {
            background: rgba(185, 28, 28, 0.85);
            color: #f8fafc;
            font-size: 10px;
            font-weight: 800;
            padding: 4px 8px;
            border-radius: 6px;
            text-align: center;
            letter-spacing: 0.4px;
        }
        .b3-gir-badge {
            background: rgba(255, 212, 59, 0.16);
            color: #ffd43b;
            font-size: 11px;
            font-weight: 800;
            padding: 3px 6px;
            border-radius: 5px;
            text-align: center;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    total_teams = len(board)
    playout_start_pos = max(total_teams - 3, 5)

    html_parts = [
        '<div class="standings-wrap">',
        '<div class="standings-header">'
        '<div>POS</div><div>LOGO</div><div class="left">SQUADRA</div>'
        '<div>P</div><div>W</div><div>L</div><div>DIFF</div><div>STREAK</div><div>PTS</div>'
        '</div>',
    ]

    for idx, item in enumerate(board, start=1):
        row_class = ""
        if idx == 1:
            html_parts.append('<div class="zone-tag zone-promo">PROMOZIONE DR1 (1° POSTO)</div>')
            row_class = "pos-1"
        elif idx == 2:
            html_parts.append('<div class="zone-tag zone-po">PLAY-OFF (2° POSTO)</div>')
            row_class = "pos-2"
        elif idx == 3:
            is_best = best_third_team is not None and best_third_team["Girone"] == girone_sel
            if len(ranked_thirds) <= 1:
                label_3 = "3° POSTO — MIGLIORE TERZA (IN ATTESA DATI ALTRI GIRONI)"
                tag_cls = "zone-terza-no"
            elif is_best:
                label_3 = "3° POSTO — ATTUALE MIGLIORE TERZA (PLAY-OFF)"
                tag_cls = "zone-terza-ok"
            else:
                label_3 = f"3° POSTO — NON MIGLIORE TERZA (ATTUALE: {best_third_team['Squadra']} - {best_third_team['Girone']})"
                tag_cls = "zone-terza-no"
            html_parts.append(f'<div class="zone-tag {tag_cls}">{label_3}</div>')
            row_class = "pos-3"
        elif idx == playout_start_pos:
            html_parts.append('<div class="zone-tag zone-pout">PLAY-OUT (ULTIME 4)</div>')

        if idx >= playout_start_pos:
            row_class = "pos-playout"

        logo_src = resolve_logo_src(item["Logo_URL"])
        logo_html = (
            f'<img class="s-logo" src="{logo_src}" alt="{item["Squadra"]}" />'
            if logo_src
            else '<div class="s-pos">🏀</div>'
        )
        dp_str = format_dp(item["DP"])
        streak_str = format_streak_text(item["STREAK"])
        streak_html = format_streak_badges(streak_str)

        html_parts.append(
            f'<div class="s-row {row_class}">'
            f'<div class="s-pos">{idx}</div>'
            f'<div>{logo_html}</div>'
            f'<div><div class="s-team">{item["Squadra"]}</div></div>'
            f'<div class="s-val">{item["PG"]}</div>'
            f'<div class="s-val">{item["V"]}</div>'
            f'<div class="s-val">{item["S"]}</div>'
            f'<div class="s-val">{dp_str}</div>'
            f'<div title="{streak_str}">{streak_html}</div>'
            f'<div class="s-pts">{item["PTS"]}</div>'
            f'</div>'
        )

    html_parts.append("</div>")
    st.markdown("".join(html_parts), unsafe_allow_html=True)

    if ranked_thirds:
        b3_parts = [
            '<div class="b3-wrap">',
            '<div class="b3-title-bar">'
            '<div class="b3-main-title">🏆 MINI-CLASSIFICA MIGLIORE TERZA (3° POSTO GIRONI A · B · C)</div>'
            '<div class="b3-sub-rule">Criteri: PTS → DIFF → PF</div>'
            '</div>',
            '<div class="b3-header">'
            '<div>#</div><div>LOGO</div><div class="left">SQUADRA</div>'
            '<div>GIRONE</div><div>P</div><div>W</div><div>L</div><div>DIFF</div><div>PF</div>'
            '<div>STREAK</div><div>PTS</div><div>ESITO</div>'
            '</div>',
        ]
        for rank_i, t_item in enumerate(ranked_thirds, start=1):
            is_qual = rank_i == 1
            row_cls = "qual" if is_qual else "no-qual"
            logo_src = resolve_logo_src(t_item["Logo_URL"])
            logo_html = (
                f'<img class="s-logo" src="{logo_src}" alt="{t_item["Squadra"]}" />'
                if logo_src
                else '<div class="s-pos">🏀</div>'
            )
            streak_str = format_streak_text(t_item["STREAK"])
            streak_html = format_streak_badges(streak_str)
            esito_html = (
                '<div class="b3-pill-ok">QUALIFICATA PLAY-OFF</div>'
                if is_qual
                else '<div class="b3-pill-no">FUORI PLAY-OFF</div>'
            )

            b3_parts.append(
                f'<div class="b3-row {row_cls}">'
                f'<div class="s-pos">{rank_i}</div>'
                f'<div>{logo_html}</div>'
                f'<div><div class="s-team">{t_item["Squadra"]}</div></div>'
                f'<div><div class="b3-gir-badge">{t_item["Girone"]}</div></div>'
                f'<div class="s-val">{t_item["PG"]}</div>'
                f'<div class="s-val">{t_item["V"]}</div>'
                f'<div class="s-val">{t_item["S"]}</div>'
                f'<div class="s-val">{format_dp(t_item["DP"])}</div>'
                f'<div class="s-val">{t_item["PF"]}</div>'
                f'<div title="{streak_str}">{streak_html}</div>'
                f'<div class="s-pts">{t_item["PTS"]}</div>'
                f'<div>{esito_html}</div>'
                f'</div>'
            )
        b3_parts.append("</div>")
        st.markdown("".join(b3_parts), unsafe_allow_html=True)


if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🏀 DR2 Puglia — Area Riservata Staff")
    pwd = st.text_input("Password", type="password")
    if st.button("Accedi"):
        if pwd == STAFF_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Password non valida.")
    st.stop()

teams_df, games_df, box_df = load_data()

st.sidebar.title("🏀 DR2 Puglia")
page = st.sidebar.radio("Navigazione", ["Gironi", "Gestione Squadre"])

if page == "Gironi":
    st.title("Gironi — Divisione Regionale 2 Puglia")
    girone_sel = st.selectbox("Seleziona Girone", ["Girone A", "Girone B", "Girone C"])
    board = compute_standings_for_girone(girone_sel, teams_df, games_df)
    best_third_team, ranked_thirds = compute_best_third(teams_df, games_df)
    render_standings_board(board, girone_sel, best_third_team, ranked_thirds)

elif page == "Gestione Squadre":
    st.title("Gestione Squadre e Dati")
    if st.button("🔄 Ripristina Tutti i Gironi e Calendari Ufficiali (A, B, C)"):
        reset_official_data()
        resolve_logo_src.clear()
        st.success("Dati ufficiali ripristinati.")
        st.rerun()
