import base64
import os
from pathlib import Path
from urllib.parse import quote

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="DR2 Puglia — Classifiche e Calendario",
    page_icon="🏀",
    layout="wide",
)

# ==========================================
# CONFIGURAZIONE
# ==========================================
STAFF_PASSWORD = os.environ.get("DR2_STAFF_PASSWORD", "dr2puglia")
GITHUB_RAW_BASE = os.environ.get("DR2_GITHUB_RAW_BASE", "").strip()

GIRONI_TEAMS: dict[str, list[dict[str, str]]] = {
    "Girone A": [
        {"squadra": "ASD MAGIC BARI", "logo": "Magic Bari.png"},
        {"squadra": "ASD POL. BASKET BITRITTO", "logo": "basket bitritto.png"},
        {"squadra": "ASD VI.G.OR BASKET SAN SEVERO", "logo": "Vigor San Severo.png"},
        {"squadra": "ASD VIRTUS FOGGIA", "logo": "Virtus Foggia.png"},
        {"squadra": "ECOFAN CERIGNOLA MEDITERRANEA 92", "logo": "Mediterranea Cerignola.png"},
        {"squadra": "FORTITUDO BASKET APRICENA", "logo": "Fortitudo Basket Apricena.png"},
        {"squadra": "GINNASTICA ANGIULLI BARI", "logo": "Angiulli Basket Bari.png"},
        {"squadra": "PALLACANESTRO OLIMPIA CORATO", "logo": "Olimpia Corato.png"},
        {"squadra": "POL. DIL. NUOVA MATTEOTTI CORATO", "logo": "Nuova Matteotti Corato.png"},
        {"squadra": "POLISPORTIVA ORSA CAPURSO SSD ARL", "logo": "orsa capurso.png"},
        {"squadra": "AGS DIL. TORITTO", "logo": "A.G.S.D. TORITTO.png"},
    ],
    "Girone B": [
        {"squadra": "ASD ATLETICA BASKET PUTIGNANO", "logo": "Atletica Basket Putignano.png"},
        {"squadra": "ASD BASKET FASANO", "logo": "ASD Basket Fasano.png"},
        {"squadra": "ASD CLUB GIGANTI CISTERNINO", "logo": "Club Giganti Cisternino.png"},
        {"squadra": "ASD DREAM BASKET ALTAMURA", "logo": "Dream Basket Altamura.png"},
        {"squadra": "ASD MESSAPICA BASKET CEGLIE", "logo": "Messapica Bk Ceglie.png"},
        {"squadra": "ASD MURGIA BASKET SANTERAMO", "logo": "Murgia Basket Santeramo.png"},
        {"squadra": "ASD SCUOLA BASKET MARTINESE", "logo": "SBM Martina Franca.png"},
        {"squadra": "DOMITI LA PINTA BASKET PULSANO", "logo": "Domiti La Pinta ASD Pulsano.png"},
        {"squadra": "MASSERIA SEMERARO NEW SPORTING MOTTOLA", "logo": "New Sporting Mottola.png"},
        {"squadra": "POL. OLYMPIA CLUB RUTIGLIANO", "logo": "olympia rutigliano.png"},
        {"squadra": "SUPPORT_O TARANTO", "logo": "Support_o Taranto.png"},
    ],
    "Girone C": [
        {"squadra": "A.POL.DIL.AURORA BRINDISI", "logo": "Aurora Brindisi.png"},
        {"squadra": "ALL STAR BASKET FRANCAVILLA", "logo": "All Star Francavilla.png"},
        {"squadra": "ASD ASSI BASKET BRINDISI", "logo": "ASSI Brindisi.png"},
        {"squadra": "ASD BASKET TRICASE", "logo": "Basket Tricase.png"},
        {"squadra": "ASD BELLFIKA MESAGNE", "logo": "Bellfika Mesagne.png"},
        {"squadra": "ASD MAGIC GALATINA", "logo": "Magic Galatina.png"},
        {"squadra": "ASD NEW BASKET CARMIANO", "logo": "New Basket Carmiano.png"},
        {"squadra": "ASD POLISPORTIVA MANDURIA", "logo": "Basket Manduria.png"},
        {"squadra": "AZ DISINFESTAZIONI SRL VIRTUS BRINDISI", "logo": "Virtus Brindisi.png"},
        {"squadra": "DIERRE ARREDAMENTI CALIMERA BASKET", "logo": "Calimera Zero21.png"},
        {"squadra": "SENSI PALLACANESTRO LUPA LECCE", "logo": "Pallacanestro Lupa Lecce.png"},
    ],
}

DEFAULT_GAMES_RAW = [
    # GIRONE A
    ("A01_1867", "Girone A", 1, "Sab 07/11/2026 19:00", "POL. DIL. NUOVA MATTEOTTI CORATO", "PALLACANESTRO OLIMPIA CORATO", 72, 67, "Giocata"),
    ("A01_1868", "Girone A", 1, "Dom 08/11/2026 18:30", "FORTITUDO BASKET APRICENA", "ECOFAN CERIGNOLA MEDITERRANEA 92", 50, 76, "Giocata"),
    ("A01_1869", "Girone A", 1, "Dom 08/11/2026 18:00", "GINNASTICA ANGIULLI BARI", "ASD MAGIC BARI", 68, 50, "Giocata"),
    ("A01_1870", "Girone A", 1, "Sab 07/11/2026 18:30", "ASD VIRTUS FOGGIA", "POLISPORTIVA ORSA CAPURSO SSD ARL", 78, 87, "Giocata"),
    ("A01_1871", "Girone A", 1, "Dom 08/11/2026 18:30", "ASD POL. BASKET BITRITTO", "AGS DIL. TORITTO", 62, 81, "Giocata"),

    ("A02_1872", "Girone A", 2, "Sab 14/11/2026 18:00", "ASD VI.G.OR BASKET SAN SEVERO", "ASD VIRTUS FOGGIA", 0, 0, "Da giocare"),
    ("A02_1873", "Girone A", 2, "Dom 15/11/2026 20:15", "PALLACANESTRO OLIMPIA CORATO", "FORTITUDO BASKET APRICENA", 50, 56, "Giocata"),
    ("A02_1874", "Girone A", 2, "Dom 15/11/2026 19:00", "ECOFAN CERIGNOLA MEDITERRANEA 92", "POL. DIL. NUOVA MATTEOTTI CORATO", 49, 59, "Giocata"),
    ("A02_1875", "Girone A", 2, "Dom 15/11/2026 19:00", "AGS DIL. TORITTO", "GINNASTICA ANGIULLI BARI", 85, 96, "Giocata"),
    ("A02_1876", "Girone A", 2, "Dom 15/11/2026 17:30", "ASD MAGIC BARI", "ASD POL. BASKET BITRITTO", 56, 48, "Giocata"),

    ("A03_1877", "Girone A", 3, "Sab 21/11/2026 19:30", "GINNASTICA ANGIULLI BARI", "ECOFAN CERIGNOLA MEDITERRANEA 92", 86, 75, "Giocata"),
    ("A03_1878", "Girone A", 3, "Dom 22/11/2026 18:30", "FORTITUDO BASKET APRICENA", "ASD MAGIC BARI", 69, 79, "Giocata"),
    ("A03_1879", "Girone A", 3, "Dom 22/11/2026 18:00", "POLISPORTIVA ORSA CAPURSO SSD ARL", "ASD VI.G.OR BASKET SAN SEVERO", 75, 74, "Giocata"),
    ("A03_1880", "Girone A", 3, "Sab 21/11/2026 19:00", "POL. DIL. NUOVA MATTEOTTI CORATO", "AGS DIL. TORITTO", 64, 77, "Giocata"),
    ("A03_1881", "Girone A", 3, "Dom 22/11/2026 18:30", "ASD POL. BASKET BITRITTO", "PALLACANESTRO OLIMPIA CORATO", 51, 50, "Giocata"),

    ("A04_1882", "Girone A", 4, "Dom 29/11/2026 17:30", "ASD MAGIC BARI", "POL. DIL. NUOVA MATTEOTTI CORATO", 0, 0, "Da giocare"),
    ("A04_1883", "Girone A", 4, "Dom 29/11/2026 19:00", "AGS DIL. TORITTO", "FORTITUDO BASKET APRICENA", 0, 0, "Da giocare"),
    ("A04_1884", "Girone A", 4, "Sab 28/11/2026 18:30", "ASD VIRTUS FOGGIA", "GINNASTICA ANGIULLI BARI", 0, 0, "Da giocare"),
    ("A04_1885", "Girone A", 4, "Dom 29/11/2026 18:00", "POLISPORTIVA ORSA CAPURSO SSD ARL", "PALLACANESTRO OLIMPIA CORATO", 0, 0, "Da giocare"),
    ("A04_1886", "Girone A", 4, "Sab 28/11/2026 19:45", "ASD VI.G.OR BASKET SAN SEVERO", "ASD POL. BASKET BITRITTO", 0, 0, "Da giocare"),

    # GIRONE B
    ("B01_2109", "Girone B", 1, "Sab 07/11/2026 18:45", "ASD SCUOLA BASKET MARTINESE", "ASD DREAM BASKET ALTAMURA", 41, 62, "Giocata"),
    ("B01_2110", "Girone B", 1, "Dom 08/11/2026 17:30", "ASD MURGIA BASKET SANTERAMO", "MASSERIA SEMERARO NEW SPORTING MOTTOLA", 70, 59, "Giocata"),
    ("B01_2111", "Girone B", 1, "Dom 08/11/2026 18:00", "SUPPORT_O TARANTO", "DOMITI LA PINTA BASKET PULSANO", 71, 59, "Giocata"),
    ("B01_2112", "Girone B", 1, "Sab 07/11/2026 19:00", "ASD BASKET FASANO", "ASD ATLETICA BASKET PUTIGNANO", 49, 63, "Giocata"),
    ("B01_2113", "Girone B", 1, "Sab 07/11/2026 19:00", "ASD CLUB GIGANTI CISTERNINO", "ASD MESSAPICA BASKET CEGLIE", 69, 57, "Giocata"),

    ("B02_2114", "Girone B", 2, "Sab 14/11/2026 20:00", "ASD MESSAPICA BASKET CEGLIE", "POL. OLYMPIA CLUB RUTIGLIANO", 0, 0, "Da giocare"),
    ("B02_2115", "Girone B", 2, "Dom 15/11/2026 18:00", "ASD DREAM BASKET ALTAMURA", "ASD BASKET FASANO", 66, 59, "Giocata"),
    ("B02_2116", "Girone B", 2, "Sab 14/11/2026 18:00", "ASD ATLETICA BASKET PUTIGNANO", "ASD SCUOLA BASKET MARTINESE", 55, 34, "Giocata"),
    ("B02_2117", "Girone B", 2, "Dom 15/11/2026 18:30", "MASSERIA SEMERARO NEW SPORTING MOTTOLA", "SUPPORT_O TARANTO", 64, 55, "Giocata"),
    ("B02_2118", "Girone B", 2, "Dom 15/11/2026 18:00", "DOMITI LA PINTA BASKET PULSANO", "ASD MURGIA BASKET SANTERAMO", 59, 56, "Giocata"),

    ("B03_2119", "Girone B", 3, "Dom 22/11/2026 18:00", "ASD BASKET FASANO", "MASSERIA SEMERARO NEW SPORTING MOTTOLA", 75, 61, "Giocata"),
    ("B03_2120", "Girone B", 3, "Sab 21/11/2026 18:45", "ASD SCUOLA BASKET MARTINESE", "DOMITI LA PINTA BASKET PULSANO", 54, 57, "Giocata"),
    ("B03_2121", "Girone B", 3, "Dom 22/11/2026 18:00", "POL. OLYMPIA CLUB RUTIGLIANO", "ASD CLUB GIGANTI CISTERNINO", 76, 54, "Giocata"),
    ("B03_2122", "Girone B", 3, "Dom 22/11/2026 18:00", "SUPPORT_O TARANTO", "ASD DREAM BASKET ALTAMURA", 65, 70, "Giocata"),
    ("B03_2123", "Girone B", 3, "Dom 22/11/2026 17:30", "ASD MURGIA BASKET SANTERAMO", "ASD ATLETICA BASKET PUTIGNANO", 54, 57, "Giocata"),

    ("B04_2124", "Girone B", 4, "Sab 28/11/2026 19:00", "ASD CLUB GIGANTI CISTERNINO", "ASD DREAM BASKET ALTAMURA", 0, 0, "Da giocare"),
    ("B04_2125", "Girone B", 4, "Sab 28/11/2026 20:00", "ASD MESSAPICA BASKET CEGLIE", "ASD MURGIA BASKET SANTERAMO", 0, 0, "Da giocare"),
    ("B04_2126", "Girone B", 4, "Dom 29/11/2026 18:00", "DOMITI LA PINTA BASKET PULSANO", "ASD BASKET FASANO", 0, 0, "Da giocare"),
    ("B04_2127", "Girone B", 4, "Dom 29/11/2026 18:30", "MASSERIA SEMERARO NEW SPORTING MOTTOLA", "ASD SCUOLA BASKET MARTINESE", 0, 0, "Da giocare"),
    ("B04_2128", "Girone B", 4, "Dom 29/11/2026 18:00", "POL. OLYMPIA CLUB RUTIGLIANO", "SUPPORT_O TARANTO", 0, 0, "Da giocare"),

    # GIRONE C
    ("C01_2219", "Girone C", 1, "Dom 08/11/2026 18:00", "ASD BASKET TRICASE", "A.POL.DIL.AURORA BRINDISI", 51, 57, "Giocata"),
    ("C01_2220", "Girone C", 1, "Sab 07/11/2026 18:00", "ALL STAR BASKET FRANCAVILLA", "ASD BELLFIKA MESAGNE", 72, 66, "Giocata"),
    ("C01_2221", "Girone C", 1, "Dom 08/11/2026 18:30", "DIERRE ARREDAMENTI CALIMERA BASKET", "ASD MAGIC GALATINA", 77, 51, "Giocata"),
    ("C01_2222", "Girone C", 1, "Dom 08/11/2026 18:00", "ASD ASSI BASKET BRINDISI", "ASD NEW BASKET CARMIANO", 73, 47, "Giocata"),
    ("C01_2223", "Girone C", 1, "Dom 08/11/2026 18:30", "SENSI PALLACANESTRO LUPA LECCE", "AZ DISINFESTAZIONI SRL VIRTUS BRINDISI", 91, 75, "Giocata"),

    ("C02_2224", "Girone C", 2, "Sab 14/11/2026 18:00", "ASD NEW BASKET CARMIANO", "ALL STAR BASKET FRANCAVILLA", 89, 70, "Giocata"),
    ("C02_2225", "Girone C", 2, "Sab 14/11/2026 18:30", "ASD MAGIC GALATINA", "ASD BASKET TRICASE", 100, 58, "Giocata"),
    ("C02_2226", "Girone C", 2, "Sab 14/11/2026 16:30", "AZ DISINFESTAZIONI SRL VIRTUS BRINDISI", "ASD POLISPORTIVA MANDURIA", 0, 0, "Da giocare"),
    ("C02_2227", "Girone C", 2, "Dom 15/11/2026 18:00", "ASD BELLFIKA MESAGNE", "ASD ASSI BASKET BRINDISI", 75, 71, "Giocata"),
    ("C02_2228", "Girone C", 2, "Sab 14/11/2026 18:00", "A.POL.DIL.AURORA BRINDISI", "DIERRE ARREDAMENTI CALIMERA BASKET", 37, 60, "Giocata"),

    ("C03_2229", "Girone C", 3, "Sab 21/11/2026 18:00", "ALL STAR BASKET FRANCAVILLA", "ASD MAGIC GALATINA", 90, 77, "Giocata"),
    ("C03_2230", "Girone C", 3, "Sab 21/11/2026 18:00", "A.POL.DIL.AURORA BRINDISI", "ASD ASSI BASKET BRINDISI", 64, 95, "Giocata"),
    ("C03_2231", "Girone C", 3, "Dom 22/11/2026 18:30", "DIERRE ARREDAMENTI CALIMERA BASKET", "ASD BELLFIKA MESAGNE", 52, 58, "Giocata"),
    ("C03_2232", "Girone C", 3, "Dom 22/11/2026 18:00", "ASD POLISPORTIVA MANDURIA", "SENSI PALLACANESTRO LUPA LECCE", 0, 0, "Da giocare"),
    ("C03_2233", "Girone C", 3, "Dom 22/11/2026 18:00", "ASD BASKET TRICASE", "ASD NEW BASKET CARMIANO", 28, 81, "Giocata"),

    ("C04_2234", "Girone C", 4, "Dom 29/11/2026 17:00", "ASD BELLFIKA MESAGNE", "ASD BASKET TRICASE", 0, 0, "Da giocare"),
    ("C04_2235", "Girone C", 4, "Dom 29/11/2026 18:00", "ASD POLISPORTIVA MANDURIA", "ALL STAR BASKET FRANCAVILLA", 0, 0, "Da giocare"),
    ("C04_2236", "Girone C", 4, "Sab 28/11/2026 18:00", "ASD NEW BASKET CARMIANO", "DIERRE ARREDAMENTI CALIMERA BASKET", 0, 0, "Da giocare"),
    ("C04_2237", "Girone C", 4, "Sab 28/11/2026 16:30", "AZ DISINFESTAZIONI SRL VIRTUS BRINDISI", "ASD ASSI BASKET BRINDISI", 0, 0, "Da giocare"),
    ("C04_2238", "Girone C", 4, "Sab 28/11/2026 16:30", "SENSI PALLACANESTRO LUPA LECCE", "ASD MAGIC GALATINA", 0, 0, "Da giocare"),
]

STANDINGS_CSS = """
<style>
.board-box {
    background: linear-gradient(180deg, #0a4fa3 0%, #1269c7 100%);
    padding: 16px;
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.16);
    margin-bottom: 18px;
}
.board-head {
    display: grid;
    grid-template-columns: 54px 52px 1fr 52px 52px 52px 68px 132px 64px;
    gap: 8px;
    padding: 0 10px 8px 10px;
    color: #ffd43b;
    font-weight: 800;
    font-size: 13px;
    text-align: center;
}
.board-head .left { text-align: left; }
.zone-tag {
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.7px;
    text-transform: uppercase;
    margin: 10px 0 5px 4px;
    display: inline-block;
    padding: 2px 10px;
    border-radius: 6px;
}
.zone-promo { background: #16a34a; color: #ffffff; }
.zone-po { background: #d97706; color: #ffffff; }
.zone-pout { background: #dc2626; color: #ffffff; }
.board-row {
    display: grid;
    grid-template-columns: 54px 52px 1fr 52px 52px 52px 68px 132px 64px;
    gap: 8px;
    align-items: center;
    background: rgba(8, 39, 82, 0.78);
    border: 1px solid rgba(255,255,255,0.14);
    border-radius: 10px;
    padding: 8px 10px;
    margin-bottom: 6px;
    color: #ffffff;
}
.board-row.row-promo { border-left: 6px solid #22c55e; }
.board-row.row-po { border-left: 6px solid #f59e0b; }
.board-row.row-pout { border-left: 6px solid #ef4444; }
.board-row.row-qual { border-left: 6px solid #22c55e; }
.board-row.row-out { border-left: 6px solid #ef4444; }
.b-pos {
    font-size: 18px;
    font-weight: 900;
    text-align: center;
    color: #ffd43b;
}
.b-logo {
    width: 38px;
    height: 38px;
    object-fit: contain;
    background: rgba(255,255,255,0.92);
    border-radius: 8px;
    padding: 2px;
    margin: 0 auto;
    display: block;
}
.b-team {
    font-weight: 800;
    font-size: 14px;
    text-transform: uppercase;
}
.b-sub {
    font-size: 11px;
    font-weight: 700;
    color: #bae6fd;
}
.b-val {
    text-align: center;
    font-weight: 700;
    font-size: 14px;
}
.streak-wrap {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 5px;
}
.streak-box {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 22px;
    height: 22px;
    border-radius: 5px;
    font-size: 11px;
    font-weight: 900;
    color: #ffffff;
    line-height: 1;
}
.streak-w {
    background: #16a34a;
    border: 1px solid #22c55e;
}
.streak-l {
    background: #dc2626;
    border: 1px solid #ef4444;
}
.streak-empty {
    color: #cbd5e1;
    font-size: 13px;
    font-weight: 700;
}
.b-pts {
    text-align: center;
    font-weight: 900;
    font-size: 16px;
    color: #ffd43b;
}
.badge-ok {
    display: inline-block;
    background: #16a34a;
    color: #ffffff;
    font-size: 10px;
    font-weight: 800;
    padding: 2px 7px;
    border-radius: 5px;
    margin-left: 6px;
}
.badge-no {
    display: inline-block;
    background: rgba(239,68,68,0.25);
    border: 1px solid #ef4444;
    color: #fecaca;
    font-size: 10px;
    font-weight: 800;
    padding: 2px 7px;
    border-radius: 5px;
    margin-left: 6px;
}
</style>
"""

CALENDAR_CSS = """
<style>
.cal-card {
    background: #14171c;
    border: 1px solid #262b34;
    border-radius: 8px;
    margin-bottom: 14px;
    overflow: hidden;
}
.cal-card-head {
    background: #1b2028;
    color: #e2e8f0;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 0.6px;
    padding: 8px 14px;
    border-bottom: 1px solid #262b34;
    text-transform: uppercase;
}
.cal-match {
    display: grid;
    grid-template-columns: 96px 1fr 48px;
    gap: 10px;
    align-items: center;
    padding: 9px 14px;
    border-bottom: 1px solid #20252e;
}
.cal-match:last-child { border-bottom: none; }
.cal-meta { text-align: center; line-height: 1.35; }
.cal-date { font-size: 11px; font-weight: 700; color: #cbd5e1; }
.cal-ft { font-size: 11px; font-weight: 700; color: #94a3b8; }
.cal-time { font-size: 11px; font-weight: 600; color: #94a3b8; }
.cal-teams { display: flex; flex-direction: column; gap: 5px; min-width: 0; }
.cal-team {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    font-weight: 700;
    color: #cbd5e1;
    text-transform: uppercase;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.cal-team.win { color: #ffffff; font-weight: 800; }
.cal-logo {
    width: 18px;
    height: 18px;
    object-fit: contain;
    background: rgba(255,255,255,0.92);
    border-radius: 4px;
    padding: 1px;
    flex-shrink: 0;
}
.cal-scores {
    display: flex;
    flex-direction: column;
    gap: 5px;
    text-align: right;
    font-size: 13px;
    font-weight: 700;
    color: #94a3b8;
}
.cal-score-win { color: #ffffff; font-weight: 800; }
</style>
"""


@st.cache_data(show_spinner=False)
def build_games_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "ID_Partita": gid,
                "Girone": girone,
                "Giornata": int(giornata),
                "Data": data_ora,
                "Casa": casa,
                "Trasferta": trasferta,
                "Punti_Casa": int(pts_casa),
                "Punti_Trasferta": int(pts_trasf),
                "Stato": stato,
            }
            for gid, girone, giornata, data_ora, casa, trasferta, pts_casa, pts_trasf, stato in DEFAULT_GAMES_RAW
        ]
    )


@st.cache_data(show_spinner=False)
def resolve_logo_src(logo_filename: str, github_base: str) -> str:
    clean_name = (logo_filename or "").strip()
    if not clean_name:
        return ""

    if github_base:
        return f"{github_base.rstrip('/')}/{quote(clean_name, safe='._-')}"

    for candidate in (Path(clean_name), Path("loghi") / clean_name, Path("assets") / clean_name):
        if candidate.is_file():
            ext = candidate.suffix.lower().lstrip(".")
            mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext or 'png'}"
            encoded = base64.b64encode(candidate.read_bytes()).decode("ascii")
            return f"data:{mime};base64,{encoded}"

    return ""


@st.cache_data(show_spinner=False)
def build_team_logo_html_map(github_base: str) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for teams in GIRONI_TEAMS.values():
        for t in teams:
            src = resolve_logo_src(t["logo"], github_base)
            squadra = t["squadra"]
            mapping[f"board::{squadra}"] = (
                f'<img class="b-logo" src="{src}" alt="{squadra}" loading="lazy" />'
                if src
                else '<div class="b-pos">🏀</div>'
            )
            mapping[f"cal::{squadra}"] = (
                f'<img class="cal-logo" src="{src}" alt="" loading="lazy" />'
                if src
                else "🏀"
            )
    return mapping


def _render_streak_html(outcomes: list[str], max_items: int = 5) -> str:
    recent = outcomes[-max_items:]
    if not recent:
        return '<div class="streak-wrap"><span class="streak-empty">—</span></div>'
    boxes = []
    for res in recent:
        if res == "W":
            boxes.append('<span class="streak-box streak-w">W</span>')
        elif res == "L":
            boxes.append('<span class="streak-box streak-l">L</span>')
    return f'<div class="streak-wrap">{"".join(boxes)}</div>'


def _h2h_points_for_group(group_teams: list[str], played_games: list[tuple]) -> dict[str, int]:
    """Punti (2 a vittoria) negli scontri diretti tra le squadre a pari punti."""
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
    """Ordina squadre a pari punti: 1) Scontri diretti, 2) Differenza canestri, 3) Squadra."""
    if len(group_rows) <= 1:
        return group_rows

    group_names = [r["squadra"] for r in group_rows]
    h2h_pts = _h2h_points_for_group(group_names, played_games)

    return sorted(
        group_rows,
        key=lambda r: (-h2h_pts.get(r["squadra"], 0), -r["diff"], r["squadra"]),
    )


def compute_standings(girone: str, games_df: pd.DataFrame) -> list[dict]:
    """Calcola la classifica del girone dalle gare concluse ('Giocata'), 2 punti a vittoria."""
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
            "outcomes": [],
            "pts": 0,
        }
        for item in teams
    }

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
            stats[home]["outcomes"].append("W")
            stats[away]["outcomes"].append("L")
        elif p_away > p_home:
            stats[away]["w"] += 1
            stats[home]["l"] += 1
            stats[away]["pts"] += 2
            stats[away]["outcomes"].append("W")
            stats[home]["outcomes"].append("L")

    for r in stats.values():
        r["diff"] = r["pf"] - r["ps"]

    by_pts: dict[int, list[dict]] = {}
    for r in stats.values():
        by_pts.setdefault(r["pts"], []).append(r)

    ordered_rows: list[dict] = []
    for pts_val in sorted(by_pts.keys(), reverse=True):
        ordered_rows.extend(_rank_tied_group(by_pts[pts_val], played_tuples))

    return ordered_rows


def compute_thirds_standings(games_df: pd.DataFrame) -> list[dict]:
    thirds = []
    for g_name in ("Girone A", "Girone B", "Girone C"):
        board = compute_standings(g_name, games_df)
        if len(board) >= 3:
            thirds.append(board[2])
    return sorted(thirds, key=lambda r: (-r["pts"], -r["diff"], r["squadra"]))


def render_standings(girone: str, rows: list[dict], thirds_board: list[dict], logo_html_map: dict[str, str]) -> None:
    st.markdown(STANDINGS_CSS, unsafe_allow_html=True)

    playout_start = max(len(rows) - 3, 5)
    best_third = thirds_board[0] if thirds_board else None

    st.subheader(f"Classifica — {girone}")
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
        streak_html = _render_streak_html(r.get("outcomes", []))

        logo_tag = logo_html_map.get(f"board::{r['squadra']}", '<div class="b-pos">🏀</div>')
        html.append(
            f'<div class="board-row {row_cls}">'
            f'<div class="b-pos">{pos}</div>'
            f'<div>{logo_tag}</div>'
            f'<div><div class="b-team">{r["squadra"]}</div></div>'
            f'<div class="b-val">{r["p"]}</div>'
            f'<div class="b-val">{r["w"]}</div>'
            f'<div class="b-val">{r["l"]}</div>'
            f'<div class="b-val">{diff_str}</div>'
            f'<div>{streak_html}</div>'
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
            streak_html = _render_streak_html(t.get("outcomes", []))
            logo_tag = logo_html_map.get(f"board::{t['squadra']}", '<div class="b-pos">🏀</div>')
            t_html.append(
                f'<div class="board-row {r_cls}">'
                f'<div class="b-pos">{idx}</div>'
                f'<div>{logo_tag}</div>'
                f'<div>'
                f'<div class="b-team">{t["squadra"]}</div>'
                f'<div class="b-sub">{t["girone"]}{badge}</div>'
                f'</div>'
                f'<div class="b-val">{t["p"]}</div>'
                f'<div class="b-val">{t["w"]}</div>'
                f'<div class="b-val">{t["l"]}</div>'
                f'<div class="b-val">{diff_str}</div>'
                f'<div>{streak_html}</div>'
                f'<div class="b-pts">{t["pts"]}</div>'
                '</div>'
            )
        t_html.append("</div>")
        st.markdown("".join(t_html), unsafe_allow_html=True)


def build_round_html(round_num: int, round_games: pd.DataFrame, logo_html_map: dict[str, str], is_ritorno: bool = False) -> str:
    display_num = round_num - 11 if is_ritorno and round_num > 11 else round_num
    phase_label = "RITORNO" if is_ritorno else "ANDATA"
    parts = [f'<div class="cal-card"><div class="cal-card-head">GIORNATA {display_num} ({phase_label})</div>']

    if round_games.empty:
        parts.append(
            '<div class="cal-match"><div class="cal-meta">—</div>'
            '<div class="cal-teams"><div class="cal-team">Nessuna gara</div></div>'
            '<div class="cal-scores"></div></div>'
        )
    else:
        for g in round_games.itertuples(index=False):
            is_played = str(g.Stato).strip().lower() == "giocata"
            tokens = str(g.Data).strip().split()
            if len(tokens) >= 3:
                date_str, time_str = tokens[1], tokens[2]
            elif len(tokens) == 2:
                date_str, time_str = tokens[0], tokens[1]
            else:
                date_str, time_str = str(g.Data).strip(), ""

            meta_sub = '<div class="cal-ft">FT</div>' if is_played else f'<div class="cal-time">{time_str}</div>'

            home_name = str(g.Casa)
            away_name = str(g.Trasferta)
            home_pts = int(g.Punti_Casa)
            away_pts = int(g.Punti_Trasferta)
            home_win = is_played and home_pts > away_pts
            away_win = is_played and away_pts > home_pts

            h_logo = logo_html_map.get(f"cal::{home_name}", "🏀")
            a_logo = logo_html_map.get(f"cal::{away_name}", "🏀")

            s1 = str(home_pts) if is_played else ""
            s2 = str(away_pts) if is_played else ""

            parts.append(
                f'<div class="cal-match">'
                f'<div class="cal-meta"><div class="cal-date">{date_str}</div>{meta_sub}</div>'
                f'<div class="cal-teams">'
                f'<div class="cal-team {"win" if home_win else ""}">{h_logo}<span>{home_name}</span></div>'
                f'<div class="cal-team {"win" if away_win else ""}">{a_logo}<span>{away_name}</span></div>'
                f'</div>'
                f'<div class="cal-scores">'
                f'<div class="{"cal-score-win" if home_win else ""}">{s1}</div>'
                f'<div class="{"cal-score-win" if away_win else ""}">{s2}</div>'
                f'</div>'
                f'</div>'
            )

    parts.append("</div>")
    return "".join(parts)


def render_calendar_page(games_df: pd.DataFrame, logo_html_map: dict[str, str]) -> pd.DataFrame:
    st.markdown(CALENDAR_CSS, unsafe_allow_html=True)
    st.title("Calendario e Risultati")
    st.caption("Seleziona il girone e il turno per visualizzare o aggiungere gare di Andata e Ritorno.")

    gironi_list = ("Girone A", "Girone B", "Girone C")
    current_idx = gironi_list.index(st.session_state["calendar_girone"])
    girone = st.selectbox("Filtra per Girone", gironi_list, index=current_idx, key="cal_girone_select")
    st.session_state["calendar_girone"] = girone

    teams_in_girone = [t["squadra"] for t in GIRONI_TEAMS.get(girone, [])]

    with st.expander("➕ Aggiungi nuova partita al calendario"):
        with st.form(f"add_game_{girone}"):
            c1, c2, c3 = st.columns(3)
            giornata = c1.number_input("Giornata (1-11 Andata, 12-22 Ritorno)", min_value=1, max_value=22, value=1, step=1)
            data_gara = c2.text_input("Data e Ora (es. Dom 29/11/2026 18:00)", value="")
            stato = c3.selectbox("Stato", ("Da giocare", "Giocata"))

            c4, c5, c6, c7 = st.columns([3, 1, 1, 3])
            casa = c4.selectbox("Squadra Casa", teams_in_girone, index=0)
            trasferta = c7.selectbox("Squadra Trasferta", teams_in_girone, index=1 if len(teams_in_girone) > 1 else 0)
            pts_casa = c5.number_input("Pti Casa", min_value=0, max_value=200, value=0, step=1)
            pts_trasf = c6.number_input("Pti Trasf", min_value=0, max_value=200, value=0, step=1)

            if st.form_submit_button("Salva Partita"):
                if casa == trasferta:
                    st.error("Seleziona due squadre differenti per Casa e Trasferta.")
                else:
                    new_game = pd.DataFrame(
                        [
                            {
                                "ID_Partita": f"{girone.replace(' ', '')}_G{int(giornata)}_{len(games_df) + 1}",
                                "Girone": girone,
                                "Giornata": int(giornata),
                                "Data": data_gara.strip(),
                                "Casa": casa,
                                "Trasferta": trasferta,
                                "Punti_Casa": int(pts_casa),
                                "Punti_Trasferta": int(pts_trasf),
                                "Stato": stato,
                            }
                        ]
                    )
                    games_df = pd.concat([games_df, new_game], ignore_index=True)
                    st.session_state["games_df"] = games_df
                    st.success("Partita aggiunta al calendario.")
                    st.rerun()

    g_games = games_df[games_df["Girone"] == girone]
    if g_games.empty:
        st.info(f"Nessuna partita disponibile per **{girone}**.")
        return games_df

    g_games = g_games.sort_values(by=["Giornata", "ID_Partita"])
    by_round = {int(r_num): grp for r_num, grp in g_games.groupby("Giornata", sort=False)}
    turns = list(range(1, 12))

    turn_choice = st.selectbox(
        "Visualizza Turno (Andata a sinistra / Ritorno a destra)",
        ["Turno 1 (Giornata 1 Andata / Ritorno)"]
        + [f"Turno {t} (Giornata {t} Andata / Ritorno)" for t in turns[1:]]
        + ["Tutti i turni (1ª–11ª)"],
    )
    selected_turns = turns if turn_choice.startswith("Tutti") else [int(turn_choice.split()[1])]

    h_left, h_right = st.columns(2)
    h_left.markdown("### GIRONE DI ANDATA")
    h_right.markdown("### GIRONE DI RITORNO")

    empty_df = g_games.iloc[0:0]
    for t_num in selected_turns:
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown(
                build_round_html(t_num, by_round.get(t_num, empty_df), logo_html_map, is_ritorno=False),
                unsafe_allow_html=True,
            )
        with col_r:
            st.markdown(
                build_round_html(t_num + 11, by_round.get(t_num + 11, empty_df), logo_html_map, is_ritorno=True),
                unsafe_allow_html=True,
            )

    return games_df


# ==========================================
# LOGIN E NAVIGAZIONE
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "games_df" not in st.session_state:
    st.session_state["games_df"] = build_games_df()

if "calendar_girone" not in st.session_state:
    st.session_state["calendar_girone"] = "Girone A"

if not st.session_state.authenticated:
    st.title("🏀 DR2 Puglia — Login Staff")
    pwd = st.text_input("Password", type="password")
    if st.button("Accedi"):
        if pwd == STAFF_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Password non valida.")
    st.stop()

with st.sidebar:
    st.title("🏀 DR2 Puglia")
    sezione = st.radio("Sezione", ("Classifiche", "Calendario e Risultati"))
    if st.button("Esci"):
        st.session_state.authenticated = False
        st.rerun()

if not GITHUB_RAW_BASE:
    st.info(
        "Suggerimento: imposta la variabile d'ambiente `DR2_GITHUB_RAW_BASE` "
        "(es. `https://raw.githubusercontent.com/<utente>/<repo>/main/loghi`) per caricare i loghi direttamente da GitHub."
    )

logo_html_map = build_team_logo_html_map(GITHUB_RAW_BASE)

if sezione == "Classifiche":
    girone_classifica = st.selectbox("Seleziona Girone", ("Girone A", "Girone B", "Girone C"))
    classifica = compute_standings(girone_classifica, st.session_state["games_df"])
    terze_classificate = compute_thirds_standings(st.session_state["games_df"])
    render_standings(girone_classifica, classifica, terze_classificate, logo_html_map)
else:
    render_calendar_page(st.session_state["games_df"], logo_html_map)
