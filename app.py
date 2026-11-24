import base64
import os
from pathlib import Path
from urllib.parse import quote

import streamlit as st

st.set_page_config(
    page_title="DR2 Puglia — Classifiche",
    page_icon="🏀",
    layout="wide",
)

# ==========================================
# CONFIGURAZIONE
# ==========================================
STAFF_PASSWORD = os.environ.get("DR2_STAFF_PASSWORD", "dr2puglia")
# Esempio: https://raw.githubusercontent.com/<utente>/<repo>/<branch>/loghi
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


# ==========================================
# GESTIONE LOGHI (GITHUB RAW / LOCALE)
# ==========================================
@st.cache_data(show_spinner=False)
def get_logo_src(logo_filename: str) -> str:
    """Restituisce URL raw su GitHub se configurato, oppure data URI se presente in locale."""
    clean_name = (logo_filename or "").strip()
    if not clean_name:
        return ""

    if GITHUB_RAW_BASE:
        return f"{GITHUB_RAW_BASE.rstrip('/')}/{quote(clean_name, safe='._-')}"

    local_candidates = [
        Path(clean_name),
        Path("loghi") / clean_name,
        Path("assets") / clean_name,
    ]
    for path in local_candidates:
        if path.exists() and path.is_file():
            ext = path.suffix.lower().lstrip(".")
            mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext or 'png'}"
            encoded = base64.b64encode(path.read_bytes()).decode("ascii")
            return f"data:{mime};base64,{encoded}"

    return ""


# ==========================================
# CALCOLO CLASSIFICA SENZA PARTITE
# ==========================================
def compute_standings(girone: str) -> list[dict]:
    """Calcola la classifica iniziale (0 partite giocate) ordinata per punti, diff e nome."""
    teams = GIRONI_TEAMS.get(girone, [])
    rows = [
        {
            "squadra": item["squadra"],
            "logo": item["logo"],
            "p": 0,
            "w": 0,
            "l": 0,
            "diff": 0,
            "streak": "—",
            "pts": 0,
        }
        for item in teams
    ]
    return sorted(rows, key=lambda r: (-r["pts"], -r["diff"], r["squadra"]))


# ==========================================
# RENDER CLASSIFICA
# ==========================================
def render_standings(girone: str, rows: list[dict]) -> None:
    st.markdown(
        """
        <style>
        .board-box {
            background: linear-gradient(180deg, #0a4fa3 0%, #1269c7 100%);
            padding: 16px;
            border-radius: 14px;
            border: 1px solid rgba(255,255,255,0.16);
        }
        .board-head {
            display: grid;
            grid-template-columns: 54px 52px 1fr 52px 52px 52px 68px 110px 64px;
            gap: 8px;
            padding: 0 10px 8px 10px;
            color: #ffd43b;
            font-weight: 800;
            font-size: 13px;
            text-align: center;
        }
        .board-head .left { text-align: left; }
        .board-row {
            display: grid;
            grid-template-columns: 54px 52px 1fr 52px 52px 52px 68px 110px 64px;
            gap: 8px;
            align-items: center;
            background: rgba(8, 39, 82, 0.78);
            border: 1px solid rgba(255,255,255,0.14);
            border-radius: 10px;
            padding: 8px 10px;
            margin-bottom: 6px;
            color: #ffffff;
        }
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
        .b-val {
            text-align: center;
            font-weight: 700;
            font-size: 14px;
        }
        .b-pts {
            text-align: center;
            font-weight: 900;
            font-size: 16px;
            color: #ffd43b;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.subheader(f"Classifica — {girone}")
    html = [
        '<div class="board-box">',
        '<div class="board-head">'
        '<div>POS</div><div>LOGO</div><div class="left">SQUADRA</div>'
        '<div>P</div><div>W</div><div>L</div><div>DIFF</div><div>STREAK</div><div>PTS</div>'
        '</div>',
    ]

    for pos, r in enumerate(rows, start=1):
        src = get_logo_src(r["logo"])
        logo_tag = f'<img class="b-logo" src="{src}" alt="{r["squadra"]}" />' if src else '<div class="b-pos">🏀</div>'
        html.append(
            f'<div class="board-row">'
            f'<div class="b-pos">{pos}</div>'
            f'<div>{logo_tag}</div>'
            f'<div><div class="b-team">{r["squadra"]}</div></div>'
            f'<div class="b-val">{r["p"]}</div>'
            f'<div class="b-val">{r["w"]}</div>'
            f'<div class="b-val">{r["l"]}</div>'
            f'<div class="b-val">{r["diff"]}</div>'
            f'<div class="b-val">{r["streak"]}</div>'
            f'<div class="b-pts">{r["pts"]}</div>'
            f'</div>'
        )

    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)


# ==========================================
# LOGIN
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

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


# ==========================================
# VISTA CLASSIFICHE
# ==========================================
top_col1, top_col2 = st.columns([6, 1])
with top_col1:
    st.title("🏀 DR2 Puglia — Classifiche")
with top_col2:
    if st.button("Esci"):
        st.session_state.authenticated = False
        st.rerun()

if not GITHUB_RAW_BASE:
    st.info(
        "Suggerimento: imposta la variabile d'ambiente `DR2_GITHUB_RAW_BASE` "
        "(es. `https://raw.githubusercontent.com/<utente>/<repo>/main/loghi`) per caricare i loghi direttamente da GitHub."
    )

girone_selezionato = st.selectbox("Seleziona Girone", ["Girone A", "Girone B", "Girone C"])
classifica = compute_standings(girone_selezionato)
render_standings(girone_selezionato, classifica)
