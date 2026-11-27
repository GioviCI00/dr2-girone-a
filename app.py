import base64

import html as html_lib

import json

import os

import re

from pathlib import Path

from urllib.error import HTTPError

from urllib.parse import quote

from urllib.request import Request, urlopen



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

DATA_VERSION = "2026-11-26-v21-player-modal-fixed"

OUR_TEAM = "New Virtus Basket Toritto"

HIGHLIGHT_TEAM = "AGS DIL. TORITTO"

STAFF_PASSWORD = os.environ.get("DR2_STAFF_PASSWORD", "dr2puglia")



DEFAULT_GITHUB_OWNER = "GioviCI00"

DEFAULT_GITHUB_REPO = "dr2-girone-a"

DEFAULT_GITHUB_BRANCH = "main"



GITHUB_RAW_BASE = os.environ.get(

    "DR2_GITHUB_RAW_BASE",

    f"https://raw.githubusercontent.com/{DEFAULT_GITHUB_OWNER}/{DEFAULT_GITHUB_REPO}/{DEFAULT_GITHUB_BRANCH}",

).strip()



OVERRIDES_PATH = "modifiche_partita.json"

DETAILS_PATH = "dettagli_partite.json"

LOCAL_OVERRIDES_FILE = Path(OVERRIDES_PATH)

LOCAL_DETAILS_FILE = Path(DETAILS_PATH)



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



TEAM_COLORS: dict[str, dict[str, str]] = {

    # Girone A

    "AGS DIL. TORITTO": {"label": "Bianco - Blu", "primary": "#f8fafc", "secondary": "#1d4ed8", "text": "#0f172a"},

    "ASD VI.G.OR BASKET SAN SEVERO": {"label": "Bianco - Rosso", "primary": "#f8fafc", "secondary": "#dc2626", "text": "#0f172a"},

    "POLISPORTIVA ORSA CAPURSO SSD ARL": {"label": "Nero - Arancione", "primary": "#111827", "secondary": "#f97316", "text": "#ffffff"},

    "ASD POL. BASKET BITRITTO": {"label": "Bianco - Verde", "primary": "#f8fafc", "secondary": "#16a34a", "text": "#0f172a"},

    "GINNASTICA ANGIULLI BARI": {"label": "Azzurro - Bianco", "primary": "#0284c7", "secondary": "#f8fafc", "text": "#ffffff"},

    "ASD MAGIC BARI": {"label": "Bianco", "primary": "#f8fafc", "secondary": "#334155", "text": "#0f172a"},

    "ECOFAN CERIGNOLA MEDITERRANEA 92": {"label": "Bianco - Azzurro", "primary": "#f8fafc", "secondary": "#0284c7", "text": "#0f172a"},

    "POL. DIL. NUOVA MATTEOTTI CORATO": {"label": "Bianco - Blu", "primary": "#f8fafc", "secondary": "#1d4ed8", "text": "#0f172a"},

    "FORTITUDO BASKET APRICENA": {"label": "Bianco - Blu", "primary": "#f8fafc", "secondary": "#1d4ed8", "text": "#0f172a"},

    "PALLACANESTRO OLIMPIA CORATO": {"label": "Bianco - Rosso", "primary": "#f8fafc", "secondary": "#dc2626", "text": "#0f172a"},

    "ASD VIRTUS FOGGIA": {"label": "Bianco - Azzurro", "primary": "#f8fafc", "secondary": "#0284c7", "text": "#0f172a"},

    # Girone B

    "ASD SCUOLA BASKET MARTINESE": {"label": "Bianco - Verde", "primary": "#f8fafc", "secondary": "#16a34a", "text": "#0f172a"},

    "POL. OLYMPIA CLUB RUTIGLIANO": {"label": "Granata - Bianco", "primary": "#881337", "secondary": "#f8fafc", "text": "#ffffff"},

    "ASD DREAM BASKET ALTAMURA": {"label": "Bianco", "primary": "#f8fafc", "secondary": "#334155", "text": "#0f172a"},

    "ASD MESSAPICA BASKET CEGLIE": {"label": "Giallo - Blu", "primary": "#facc15", "secondary": "#1d4ed8", "text": "#0f172a"},

    "ASD MURGIA BASKET SANTERAMO": {"label": "Bianco - Azzurro", "primary": "#f8fafc", "secondary": "#0284c7", "text": "#0f172a"},

    "ASD ATLETICA BASKET PUTIGNANO": {"label": "Arancione - Nero", "primary": "#ea580c", "secondary": "#111827", "text": "#ffffff"},

    "MASSERIA SEMERARO NEW SPORTING MOTTOLA": {"label": "Blu - Giallo", "primary": "#1d4ed8", "secondary": "#facc15", "text": "#ffffff"},

    "SUPPORT_O TARANTO": {"label": "Bianco - Blu", "primary": "#f8fafc", "secondary": "#1d4ed8", "text": "#0f172a"},

    "ASD CLUB GIGANTI CISTERNINO": {"label": "Giallo - Blu", "primary": "#facc15", "secondary": "#1d4ed8", "text": "#0f172a"},

    "DOMITI LA PINTA BASKET PULSANO": {"label": "Blu - Bianco", "primary": "#1d4ed8", "secondary": "#f8fafc", "text": "#ffffff"},

    "ASD BASKET FASANO": {"label": "Bianco - Azzurro", "primary": "#f8fafc", "secondary": "#0284c7", "text": "#0f172a"},

    # Girone C

    "ASD ASSI BASKET BRINDISI": {"label": "Rosso - Bianco", "primary": "#dc2626", "secondary": "#f8fafc", "text": "#ffffff"},

    "ALL STAR BASKET FRANCAVILLA": {"label": "Bianco - Arancione", "primary": "#f8fafc", "secondary": "#ea580c", "text": "#0f172a"},

    "ASD NEW BASKET CARMIANO": {"label": "Rosso - Blu", "primary": "#dc2626", "secondary": "#1d4ed8", "text": "#ffffff"},

    "ASD BASKET TRICASE": {"label": "Verde - Bianco", "primary": "#16a34a", "secondary": "#f8fafc", "text": "#ffffff"},

    "A.POL.DIL.AURORA BRINDISI": {"label": "Giallo - Blu", "primary": "#facc15", "secondary": "#1d4ed8", "text": "#0f172a"},

    "AZ DISINFESTAZIONI SRL VIRTUS BRINDISI": {"label": "Giallo - Nero", "primary": "#facc15", "secondary": "#111827", "text": "#0f172a"},

    "ASD MAGIC GALATINA": {"label": "Bianco", "primary": "#f8fafc", "secondary": "#334155", "text": "#0f172a"},

    "ASD BELLFIKA MESAGNE": {"label": "Blu - Bianco", "primary": "#1d4ed8", "secondary": "#f8fafc", "text": "#ffffff"},

    "DIERRE ARREDAMENTI CALIMERA BASKET": {"label": "Giallo - Blu", "primary": "#facc15", "secondary": "#1d4ed8", "text": "#0f172a"},

    "ASD POLISPORTIVA MANDURIA": {"label": "Verde - Nero", "primary": "#16a34a", "secondary": "#111827", "text": "#ffffff"},

    "SENSI PALLACANESTRO LUPA LECCE": {"label": "Rosso - Giallo", "primary": "#dc2626", "secondary": "#facc15", "text": "#ffffff"},

}





def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:

    h = hex_color.strip().lstrip("#")

    if len(h) == 3:

        h = "".join(c * 2 for c in h)

    if len(h) != 6:

        return (29, 78, 216)

    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))





def _rgba(hex_color: str, alpha: float) -> str:

    r, g, b = _hex_to_rgb(hex_color)

    return f"rgba({r}, {g}, {b}, {alpha:.2f})"





def _get_team_palette(team_name: str) -> dict[str, str]:

    clean = str(team_name or "").strip()

    base = TEAM_COLORS.get(

        clean,

        {"label": "Blu - Oro", "primary": "#1d4ed8", "secondary": "#fbbf24", "text": "#ffffff"},

    )

    prim = base["primary"]

    sec = base["secondary"]

    txt = base["text"]

    # Colore saturo principale per sfondi scuri/bordo (evita che il bianco bruci i testi chiari su card scure)

    is_white_prim = prim.lower() in ("#f8fafc", "#ffffff")

    rich_main = sec if is_white_prim else prim

    rich_accent = prim if is_white_prim else sec

    # Colore vivo garantito visibile su sfondo scuro

    visible_accent = "#f8fafc" if rich_accent.lower() in ("#111827", "#334155") else rich_accent

    visible_main = "#38bdf8" if rich_main.lower() in ("#111827", "#334155") else rich_main

    return {

        "label": base["label"],

        "primary": prim,

        "secondary": sec,

        "text": txt,

        "rich_main": rich_main,

        "rich_accent": rich_accent,

        "visible_main": visible_main,

        "visible_accent": visible_accent,

    }



DEFAULT_GAMES_RAW = [

    # ==========================================

    # GIRONE A (Giornate 1-22 + Risultati G1-G3)

    # ==========================================

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

    ("A04_1882", "Girone A", 4, "Dom 29/11/2026 17:30", "POL. DIL. NUOVA MATTEOTTI CORATO", "ASD MAGIC BARI", 0, 0, "Da giocare"),

    ("A04_1883", "Girone A", 4, "Dom 29/11/2026 19:00", "AGS DIL. TORITTO", "FORTITUDO BASKET APRICENA", 0, 0, "Da giocare"),

    ("A04_1884", "Girone A", 4, "Sab 28/11/2026 18:30", "ASD VIRTUS FOGGIA", "GINNASTICA ANGIULLI BARI", 0, 0, "Da giocare"),

    ("A04_1885", "Girone A", 4, "Dom 29/11/2026 18:00", "POLISPORTIVA ORSA CAPURSO SSD ARL", "PALLACANESTRO OLIMPIA CORATO", 0, 0, "Da giocare"),

    ("A04_1886", "Girone A", 4, "Sab 28/11/2026 19:45", "ASD VI.G.OR BASKET SAN SEVERO", "ASD POL. BASKET BITRITTO", 0, 0, "Da giocare"),

    ("A05_1887", "Girone A", 5, "Dom 06/12/2026 17:30", "ASD MAGIC BARI", "POLISPORTIVA ORSA CAPURSO SSD ARL", 0, 0, "Da giocare"),

    ("A05_1888", "Girone A", 5, "Dom 06/12/2026 19:00", "ECOFAN CERIGNOLA MEDITERRANEA 92", "AGS DIL. TORITTO", 0, 0, "Da giocare"),

    ("A05_1889", "Girone A", 5, "Dom 06/12/2026 20:15", "PALLACANESTRO OLIMPIA CORATO", "ASD VI.G.OR BASKET SAN SEVERO", 0, 0, "Da giocare"),

    ("A05_1890", "Girone A", 5, "Dom 06/12/2026 18:30", "ASD POL. BASKET BITRITTO", "ASD VIRTUS FOGGIA", 0, 0, "Da giocare"),

    ("A05_1891", "Girone A", 5, "Sab 05/12/2026 19:30", "GINNASTICA ANGIULLI BARI", "POL. DIL. NUOVA MATTEOTTI CORATO", 0, 0, "Da giocare"),

    ("A06_1892", "Girone A", 6, "Dom 13/12/2026 18:30", "FORTITUDO BASKET APRICENA", "ASD POL. BASKET BITRITTO", 0, 0, "Da giocare"),

    ("A06_1893", "Girone A", 6, "Dom 13/12/2026 20:15", "PALLACANESTRO OLIMPIA CORATO", "ASD MAGIC BARI", 0, 0, "Da giocare"),

    ("A06_1894", "Girone A", 6, "Sab 12/12/2026 19:00", "POL. DIL. NUOVA MATTEOTTI CORATO", "ASD VI.G.OR BASKET SAN SEVERO", 0, 0, "Da giocare"),

    ("A06_1895", "Girone A", 6, "Dom 13/12/2026 18:00", "POLISPORTIVA ORSA CAPURSO SSD ARL", "GINNASTICA ANGIULLI BARI", 0, 0, "Da giocare"),

    ("A06_1896", "Girone A", 6, "Gio 17/12/2026 20:00", "ASD VIRTUS FOGGIA", "ECOFAN CERIGNOLA MEDITERRANEA 92", 0, 0, "Da giocare"),

    ("A07_1897", "Girone A", 7, "Sab 19/12/2026 18:00", "ASD VI.G.OR BASKET SAN SEVERO", "FORTITUDO BASKET APRICENA", 0, 0, "Da giocare"),

    ("A07_1898", "Girone A", 7, "Dom 20/12/2026 19:00", "ECOFAN CERIGNOLA MEDITERRANEA 92", "PALLACANESTRO OLIMPIA CORATO", 0, 0, "Da giocare"),

    ("A07_1899", "Girone A", 7, "Dom 20/12/2026 18:30", "ASD POL. BASKET BITRITTO", "POL. DIL. NUOVA MATTEOTTI CORATO", 0, 0, "Da giocare"),

    ("A07_1900", "Girone A", 7, "Dom 20/12/2026 19:00", "AGS DIL. TORITTO", "POLISPORTIVA ORSA CAPURSO SSD ARL", 0, 0, "Da giocare"),

    ("A07_1901", "Girone A", 7, "Dom 20/12/2026 17:30", "ASD MAGIC BARI", "ASD VIRTUS FOGGIA", 0, 0, "Da giocare"),

    ("A08_1902", "Girone A", 8, "Dom 10/01/2027 18:30", "FORTITUDO BASKET APRICENA", "GINNASTICA ANGIULLI BARI", 0, 0, "Da giocare"),

    ("A08_1903", "Girone A", 8, "Dom 10/01/2027 19:00", "AGS DIL. TORITTO", "ASD VI.G.OR BASKET SAN SEVERO", 0, 0, "Da giocare"),

    ("A08_1904", "Girone A", 8, "Dom 10/01/2027 19:00", "ECOFAN CERIGNOLA MEDITERRANEA 92", "ASD MAGIC BARI", 0, 0, "Da giocare"),

    ("A08_1905", "Girone A", 8, "Sab 09/01/2027 19:00", "POL. DIL. NUOVA MATTEOTTI CORATO", "POLISPORTIVA ORSA CAPURSO SSD ARL", 0, 0, "Da giocare"),

    ("A08_1906", "Girone A", 8, "Dom 10/01/2027 20:15", "PALLACANESTRO OLIMPIA CORATO", "ASD VIRTUS FOGGIA", 0, 0, "Da giocare"),

    ("A09_1907", "Girone A", 9, "Sab 16/01/2027 18:00", "ASD VI.G.OR BASKET SAN SEVERO", "ASD MAGIC BARI", 0, 0, "Da giocare"),

    ("A09_1908", "Girone A", 9, "Sab 16/01/2027 18:30", "ASD VIRTUS FOGGIA", "AGS DIL. TORITTO", 0, 0, "Da giocare"),

    ("A09_1909", "Girone A", 9, "Dom 17/01/2027 18:00", "POLISPORTIVA ORSA CAPURSO SSD ARL", "ECOFAN CERIGNOLA MEDITERRANEA 92", 0, 0, "Da giocare"),

    ("A09_1910", "Girone A", 9, "Sab 16/01/2027 19:30", "GINNASTICA ANGIULLI BARI", "ASD POL. BASKET BITRITTO", 0, 0, "Da giocare"),

    ("A09_1911", "Girone A", 9, "Sab 16/01/2027 17:00", "POL. DIL. NUOVA MATTEOTTI CORATO", "FORTITUDO BASKET APRICENA", 0, 0, "Da giocare"),

    ("A10_1912", "Girone A", 10, "Dom 24/01/2027 19:00", "AGS DIL. TORITTO", "PALLACANESTRO OLIMPIA CORATO", 0, 0, "Da giocare"),

    ("A10_1913", "Girone A", 10, "Dom 24/01/2027 19:00", "ECOFAN CERIGNOLA MEDITERRANEA 92", "ASD POL. BASKET BITRITTO", 0, 0, "Da giocare"),

    ("A10_1914", "Girone A", 10, "Dom 24/01/2027 18:00", "POLISPORTIVA ORSA CAPURSO SSD ARL", "FORTITUDO BASKET APRICENA", 0, 0, "Da giocare"),

    ("A10_1915", "Girone A", 10, "Sab 23/01/2027 19:30", "GINNASTICA ANGIULLI BARI", "ASD VI.G.OR BASKET SAN SEVERO", 0, 0, "Da giocare"),

    ("A10_1916", "Girone A", 10, "Sab 23/01/2027 18:30", "ASD VIRTUS FOGGIA", "POL. DIL. NUOVA MATTEOTTI CORATO", 0, 0, "Da giocare"),

    ("A11_1917", "Girone A", 11, "Dom 31/01/2027 17:30", "ASD MAGIC BARI", "AGS DIL. TORITTO", 0, 0, "Da giocare"),

    ("A11_1918", "Girone A", 11, "Dom 31/01/2027 18:30", "ASD POL. BASKET BITRITTO", "POLISPORTIVA ORSA CAPURSO SSD ARL", 0, 0, "Da giocare"),

    ("A11_1919", "Girone A", 11, "Dom 31/01/2027 18:30", "FORTITUDO BASKET APRICENA", "ASD VIRTUS FOGGIA", 0, 0, "Da giocare"),

    ("A11_1920", "Girone A", 11, "Dom 31/01/2027 20:15", "PALLACANESTRO OLIMPIA CORATO", "GINNASTICA ANGIULLI BARI", 0, 0, "Da giocare"),

    ("A11_1921", "Girone A", 11, "Sab 30/01/2027 18:00", "ASD VI.G.OR BASKET SAN SEVERO", "ECOFAN CERIGNOLA MEDITERRANEA 92", 0, 0, "Da giocare"),

    ("A12_1922", "Girone A", 12, "Dom 07/02/2027 18:00", "POLISPORTIVA ORSA CAPURSO SSD ARL", "ASD VIRTUS FOGGIA", 0, 0, "Da giocare"),

    ("A12_1923", "Girone A", 12, "Dom 07/02/2027 19:00", "ECOFAN CERIGNOLA MEDITERRANEA 92", "FORTITUDO BASKET APRICENA", 0, 0, "Da giocare"),

    ("A12_1924", "Girone A", 12, "Dom 07/02/2027 17:30", "ASD MAGIC BARI", "GINNASTICA ANGIULLI BARI", 0, 0, "Da giocare"),

    ("A12_1925", "Girone A", 12, "Sab 06/02/2027 19:00", "AGS DIL. TORITTO", "ASD POL. BASKET BITRITTO", 0, 0, "Da giocare"),

    ("A12_1926", "Girone A", 12, "Dom 07/02/2027 20:15", "PALLACANESTRO OLIMPIA CORATO", "POL. DIL. NUOVA MATTEOTTI CORATO", 0, 0, "Da giocare"),

    ("A13_1927", "Girone A", 13, "Sab 13/02/2027 18:30", "ASD VIRTUS FOGGIA", "ASD VI.G.OR BASKET SAN SEVERO", 0, 0, "Da giocare"),

    ("A13_1928", "Girone A", 13, "Sab 13/02/2027 19:30", "GINNASTICA ANGIULLI BARI", "AGS DIL. TORITTO", 0, 0, "Da giocare"),

    ("A13_1929", "Girone A", 13, "Sab 13/02/2027 19:00", "POL. DIL. NUOVA MATTEOTTI CORATO", "ECOFAN CERIGNOLA MEDITERRANEA 92", 0, 0, "Da giocare"),

    ("A13_1930", "Girone A", 13, "Dom 14/02/2027 20:15", "ASD POL. BASKET BITRITTO", "ASD MAGIC BARI", 0, 0, "Da giocare"),

    ("A13_1931", "Girone A", 13, "Dom 14/02/2027 18:30", "FORTITUDO BASKET APRICENA", "PALLACANESTRO OLIMPIA CORATO", 0, 0, "Da giocare"),

    ("A14_1932", "Girone A", 14, "Sab 20/02/2027 18:00", "ASD VI.G.OR BASKET SAN SEVERO", "POLISPORTIVA ORSA CAPURSO SSD ARL", 0, 0, "Da giocare"),

    ("A14_1933", "Girone A", 14, "Dom 21/02/2027 19:00", "AGS DIL. TORITTO", "POL. DIL. NUOVA MATTEOTTI CORATO", 0, 0, "Da giocare"),

    ("A14_1934", "Girone A", 14, "Dom 21/02/2027 20:15", "PALLACANESTRO OLIMPIA CORATO", "ASD POL. BASKET BITRITTO", 0, 0, "Da giocare"),

    ("A14_1935", "Girone A", 14, "Dom 21/02/2027 19:00", "ECOFAN CERIGNOLA MEDITERRANEA 92", "GINNASTICA ANGIULLI BARI", 0, 0, "Da giocare"),

    ("A14_1936", "Girone A", 14, "Dom 21/02/2027 17:30", "ASD MAGIC BARI", "FORTITUDO BASKET APRICENA", 0, 0, "Da giocare"),

    ("A15_1937", "Girone A", 15, "Sab 27/02/2027 20:00", "POL. DIL. NUOVA MATTEOTTI CORATO", "ASD MAGIC BARI", 0, 0, "Da giocare"),

    ("A15_1938", "Girone A", 15, "Dom 28/02/2027 18:30", "FORTITUDO BASKET APRICENA", "AGS DIL. TORITTO", 0, 0, "Da giocare"),

    ("A15_1939", "Girone A", 15, "Dom 28/02/2027 20:15", "ASD POL. BASKET BITRITTO", "ASD VI.G.OR BASKET SAN SEVERO", 0, 0, "Da giocare"),

    ("A15_1940", "Girone A", 15, "Dom 28/02/2027 20:15", "PALLACANESTRO OLIMPIA CORATO", "POLISPORTIVA ORSA CAPURSO SSD ARL", 0, 0, "Da giocare"),

    ("A15_1941", "Girone A", 15, "Sab 27/02/2027 19:30", "GINNASTICA ANGIULLI BARI", "ASD VIRTUS FOGGIA", 0, 0, "Da giocare"),

    ("A16_1942", "Girone A", 16, "Sab 06/03/2027 18:00", "ASD VI.G.OR BASKET SAN SEVERO", "PALLACANESTRO OLIMPIA CORATO", 0, 0, "Da giocare"),

    ("A16_1943", "Girone A", 16, "Dom 07/03/2027 18:00", "POLISPORTIVA ORSA CAPURSO SSD ARL", "ASD MAGIC BARI", 0, 0, "Da giocare"),

    ("A16_1944", "Girone A", 16, "Dom 07/03/2027 19:00", "AGS DIL. TORITTO", "ECOFAN CERIGNOLA MEDITERRANEA 92", 0, 0, "Da giocare"),

    ("A16_1945", "Girone A", 16, "Sab 06/03/2027 17:00", "POL. DIL. NUOVA MATTEOTTI CORATO", "GINNASTICA ANGIULLI BARI", 0, 0, "Da giocare"),

    ("A16_1946", "Girone A", 16, "Sab 06/03/2027 18:30", "ASD VIRTUS FOGGIA", "ASD POL. BASKET BITRITTO", 0, 0, "Da giocare"),

    ("A17_1947", "Girone A", 17, "Sab 13/03/2027 19:30", "GINNASTICA ANGIULLI BARI", "POLISPORTIVA ORSA CAPURSO SSD ARL", 0, 0, "Da giocare"),

    ("A17_1948", "Girone A", 17, "Dom 14/03/2027 19:00", "ECOFAN CERIGNOLA MEDITERRANEA 92", "ASD VIRTUS FOGGIA", 0, 0, "Da giocare"),

    ("A17_1949", "Girone A", 17, "Sab 13/03/2027 18:00", "ASD VI.G.OR BASKET SAN SEVERO", "POL. DIL. NUOVA MATTEOTTI CORATO", 0, 0, "Da giocare"),

    ("A17_1950", "Girone A", 17, "Dom 14/03/2027 17:30", "ASD MAGIC BARI", "PALLACANESTRO OLIMPIA CORATO", 0, 0, "Da giocare"),

    ("A17_1951", "Girone A", 17, "Dom 14/03/2027 18:30", "ASD POL. BASKET BITRITTO", "FORTITUDO BASKET APRICENA", 0, 0, "Da giocare"),

    ("A18_1952", "Girone A", 18, "Dom 21/03/2027 18:30", "ASD VIRTUS FOGGIA", "ASD MAGIC BARI", 0, 0, "Da giocare"),

    ("A18_1953", "Girone A", 18, "Dom 21/03/2027 18:00", "POLISPORTIVA ORSA CAPURSO SSD ARL", "AGS DIL. TORITTO", 0, 0, "Da giocare"),

    ("A18_1954", "Girone A", 18, "Dom 21/03/2027 18:30", "FORTITUDO BASKET APRICENA", "ASD VI.G.OR BASKET SAN SEVERO", 0, 0, "Da giocare"),

    ("A18_1955", "Girone A", 18, "Sab 20/03/2027 19:00", "POL. DIL. NUOVA MATTEOTTI CORATO", "ASD POL. BASKET BITRITTO", 0, 0, "Da giocare"),

    ("A18_1956", "Girone A", 18, "Dom 21/03/2027 20:15", "PALLACANESTRO OLIMPIA CORATO", "ECOFAN CERIGNOLA MEDITERRANEA 92", 0, 0, "Da giocare"),

    ("A19_1957", "Girone A", 19, "Sab 03/04/2027 18:30", "ASD VIRTUS FOGGIA", "PALLACANESTRO OLIMPIA CORATO", 0, 0, "Da giocare"),

    ("A19_1958", "Girone A", 19, "Sab 03/04/2027 18:00", "ASD VI.G.OR BASKET SAN SEVERO", "AGS DIL. TORITTO", 0, 0, "Da giocare"),

    ("A19_1959", "Girone A", 19, "Dom 04/04/2027 17:30", "ASD MAGIC BARI", "ECOFAN CERIGNOLA MEDITERRANEA 92", 0, 0, "Da giocare"),

    ("A19_1960", "Girone A", 19, "Sab 03/04/2027 19:30", "GINNASTICA ANGIULLI BARI", "FORTITUDO BASKET APRICENA", 0, 0, "Da giocare"),

    ("A19_1961", "Girone A", 19, "Dom 04/04/2027 18:00", "POLISPORTIVA ORSA CAPURSO SSD ARL", "POL. DIL. NUOVA MATTEOTTI CORATO", 0, 0, "Da giocare"),

    ("A20_1962", "Girone A", 20, "Dom 11/04/2027 19:00", "ECOFAN CERIGNOLA MEDITERRANEA 92", "POLISPORTIVA ORSA CAPURSO SSD ARL", 0, 0, "Da giocare"),

    ("A20_1963", "Girone A", 20, "Dom 11/04/2027 17:30", "ASD MAGIC BARI", "ASD VI.G.OR BASKET SAN SEVERO", 0, 0, "Da giocare"),

    ("A20_1964", "Girone A", 20, "Dom 11/04/2027 18:30", "FORTITUDO BASKET APRICENA", "POL. DIL. NUOVA MATTEOTTI CORATO", 0, 0, "Da giocare"),

    ("A20_1965", "Girone A", 20, "Dom 11/04/2027 19:00", "AGS DIL. TORITTO", "ASD VIRTUS FOGGIA", 0, 0, "Da giocare"),

    ("A20_1966", "Girone A", 20, "Dom 11/04/2027 18:30", "ASD POL. BASKET BITRITTO", "GINNASTICA ANGIULLI BARI", 0, 0, "Da giocare"),

    ("A21_1967", "Girone A", 21, "Dom 18/04/2027 20:15", "PALLACANESTRO OLIMPIA CORATO", "AGS DIL. TORITTO", 0, 0, "Da giocare"),

    ("A21_1968", "Girone A", 21, "Dom 18/04/2027 18:30", "ASD POL. BASKET BITRITTO", "ECOFAN CERIGNOLA MEDITERRANEA 92", 0, 0, "Da giocare"),

    ("A21_1969", "Girone A", 21, "Sab 17/04/2027 18:00", "ASD VI.G.OR BASKET SAN SEVERO", "GINNASTICA ANGIULLI BARI", 0, 0, "Da giocare"),

    ("A21_1970", "Girone A", 21, "Dom 18/04/2027 18:30", "FORTITUDO BASKET APRICENA", "POLISPORTIVA ORSA CAPURSO SSD ARL", 0, 0, "Da giocare"),

    ("A21_1971", "Girone A", 21, "Sab 17/04/2027 19:00", "POL. DIL. NUOVA MATTEOTTI CORATO", "ASD VIRTUS FOGGIA", 0, 0, "Da giocare"),

    ("A22_1972", "Girone A", 22, "Sab 24/04/2027 18:00", "POLISPORTIVA ORSA CAPURSO SSD ARL", "ASD POL. BASKET BITRITTO", 0, 0, "Da giocare"),

    ("A22_1973", "Girone A", 22, "Dom 25/04/2027 19:00", "AGS DIL. TORITTO", "ASD MAGIC BARI", 0, 0, "Da giocare"),

    ("A22_1974", "Girone A", 22, "Dom 25/04/2027 19:00", "ECOFAN CERIGNOLA MEDITERRANEA 92", "ASD VI.G.OR BASKET SAN SEVERO", 0, 0, "Da giocare"),

    ("A22_1975", "Girone A", 22, "Sab 24/04/2027 18:30", "ASD VIRTUS FOGGIA", "FORTITUDO BASKET APRICENA", 0, 0, "Da giocare"),

    ("A22_1976", "Girone A", 22, "Sab 24/04/2027 19:30", "GINNASTICA ANGIULLI BARI", "PALLACANESTRO OLIMPIA CORATO", 0, 0, "Da giocare"),



    # ==========================================

    # GIRONE B (Giornate 1-22 + Risultati G1-G3)

    # ==========================================

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

    ("B04_2124", "Girone B", 4, "Sab 28/11/2026 19:00", "ASD CLUB GIGANTI CISTERNINO", "ASD DREAM BASKET ALTAMURA", 0, 0, "Da giocare"),

    ("B04_2125", "Girone B", 4, "Sab 28/11/2026 20:00", "ASD MESSAPICA BASKET CEGLIE", "ASD MURGIA BASKET SANTERAMO", 0, 0, "Da giocare"),

    ("B04_2126", "Girone B", 4, "Dom 29/11/2026 18:00", "DOMITI LA PINTA BASKET PULSANO", "ASD BASKET FASANO", 0, 0, "Da giocare"),

    ("B04_2127", "Girone B", 4, "Dom 29/11/2026 18:30", "MASSERIA SEMERARO NEW SPORTING MOTTOLA", "ASD SCUOLA BASKET MARTINESE", 0, 0, "Da giocare"),

    ("B04_2128", "Girone B", 4, "Dom 29/11/2026 18:00", "POL. OLYMPIA CLUB RUTIGLIANO", "SUPPORT_O TARANTO", 0, 0, "Da giocare"),

    ("B05_2129", "Girone B", 5, "Dom 06/12/2026 17:30", "ASD MURGIA BASKET SANTERAMO", "ASD SCUOLA BASKET MARTINESE", 0, 0, "Da giocare"),

    ("B05_2130", "Girone B", 5, "Gio 03/12/2026 20:30", "ASD DREAM BASKET ALTAMURA", "POL. OLYMPIA CLUB RUTIGLIANO", 0, 0, "Da giocare"),

    ("B05_2131", "Girone B", 5, "Dom 06/12/2026 18:00", "SUPPORT_O TARANTO", "ASD MESSAPICA BASKET CEGLIE", 0, 0, "Da giocare"),

    ("B05_2132", "Girone B", 5, "Dom 06/12/2026 18:30", "MASSERIA SEMERARO NEW SPORTING MOTTOLA", "ASD CLUB GIGANTI CISTERNINO", 0, 0, "Da giocare"),

    ("B05_2133", "Girone B", 5, "Sab 05/12/2026 18:00", "ASD ATLETICA BASKET PUTIGNANO", "DOMITI LA PINTA BASKET PULSANO", 0, 0, "Da giocare"),

    ("B06_2134", "Girone B", 6, "Sab 12/12/2026 18:45", "ASD SCUOLA BASKET MARTINESE", "POL. OLYMPIA CLUB RUTIGLIANO", 0, 0, "Da giocare"),

    ("B06_2135", "Girone B", 6, "Sab 12/12/2026 19:00", "ASD BASKET FASANO", "SUPPORT_O TARANTO", 0, 0, "Da giocare"),

    ("B06_2136", "Girone B", 6, "Dom 13/12/2026 18:00", "ASD DREAM BASKET ALTAMURA", "MASSERIA SEMERARO NEW SPORTING MOTTOLA", 0, 0, "Da giocare"),

    ("B06_2137", "Girone B", 6, "Sab 12/12/2026 20:00", "ASD MESSAPICA BASKET CEGLIE", "ASD ATLETICA BASKET PUTIGNANO", 0, 0, "Da giocare"),

    ("B06_2138", "Girone B", 6, "Sab 12/12/2026 19:00", "ASD CLUB GIGANTI CISTERNINO", "ASD MURGIA BASKET SANTERAMO", 0, 0, "Da giocare"),

    ("B07_2139", "Girone B", 7, "Sab 19/12/2026 18:00", "ASD ATLETICA BASKET PUTIGNANO", "ASD DREAM BASKET ALTAMURA", 0, 0, "Da giocare"),

    ("B07_2140", "Girone B", 7, "Dom 20/12/2026 18:30", "MASSERIA SEMERARO NEW SPORTING MOTTOLA", "ASD MESSAPICA BASKET CEGLIE", 0, 0, "Da giocare"),

    ("B07_2141", "Girone B", 7, "Sab 19/12/2026 19:30", "DOMITI LA PINTA BASKET PULSANO", "ASD CLUB GIGANTI CISTERNINO", 0, 0, "Da giocare"),

    ("B07_2142", "Girone B", 7, "Dom 20/12/2026 18:00", "SUPPORT_O TARANTO", "ASD SCUOLA BASKET MARTINESE", 0, 0, "Da giocare"),

    ("B07_2143", "Girone B", 7, "Dom 20/12/2026 18:00", "POL. OLYMPIA CLUB RUTIGLIANO", "ASD BASKET FASANO", 0, 0, "Da giocare"),

    ("B08_2144", "Girone B", 8, "Sab 09/01/2027 19:00", "ASD BASKET FASANO", "ASD MURGIA BASKET SANTERAMO", 0, 0, "Da giocare"),

    ("B08_2145", "Girone B", 8, "Sab 09/01/2027 18:00", "ASD ATLETICA BASKET PUTIGNANO", "MASSERIA SEMERARO NEW SPORTING MOTTOLA", 0, 0, "Da giocare"),

    ("B08_2146", "Girone B", 8, "Sab 09/01/2027 18:45", "ASD SCUOLA BASKET MARTINESE", "ASD CLUB GIGANTI CISTERNINO", 0, 0, "Da giocare"),

    ("B08_2147", "Girone B", 8, "Dom 10/01/2027 18:00", "DOMITI LA PINTA BASKET PULSANO", "POL. OLYMPIA CLUB RUTIGLIANO", 0, 0, "Da giocare"),

    ("B08_2148", "Girone B", 8, "Dom 10/01/2027 18:00", "ASD DREAM BASKET ALTAMURA", "ASD MESSAPICA BASKET CEGLIE", 0, 0, "Da giocare"),

    ("B09_2149", "Girone B", 9, "Sab 16/01/2027 20:00", "ASD MESSAPICA BASKET CEGLIE", "DOMITI LA PINTA BASKET PULSANO", 0, 0, "Da giocare"),

    ("B09_2150", "Girone B", 9, "Dom 17/01/2027 18:00", "POL. OLYMPIA CLUB RUTIGLIANO", "MASSERIA SEMERARO NEW SPORTING MOTTOLA", 0, 0, "Da giocare"),

    ("B09_2151", "Girone B", 9, "Sab 16/01/2027 19:00", "ASD CLUB GIGANTI CISTERNINO", "ASD ATLETICA BASKET PUTIGNANO", 0, 0, "Da giocare"),

    ("B09_2152", "Girone B", 9, "Dom 17/01/2027 18:30", "ASD MURGIA BASKET SANTERAMO", "SUPPORT_O TARANTO", 0, 0, "Da giocare"),

    ("B09_2153", "Girone B", 9, "Sab 16/01/2027 18:45", "ASD SCUOLA BASKET MARTINESE", "ASD BASKET FASANO", 0, 0, "Da giocare"),

    ("B10_2154", "Girone B", 10, "Sab 23/01/2027 19:00", "ASD CLUB GIGANTI CISTERNINO", "ASD BASKET FASANO", 0, 0, "Da giocare"),

    ("B10_2155", "Girone B", 10, "Dom 24/01/2027 18:00", "DOMITI LA PINTA BASKET PULSANO", "ASD DREAM BASKET ALTAMURA", 0, 0, "Da giocare"),

    ("B10_2156", "Girone B", 10, "Sab 23/01/2027 19:30", "ASD ATLETICA BASKET PUTIGNANO", "SUPPORT_O TARANTO", 0, 0, "Da giocare"),

    ("B10_2157", "Girone B", 10, "Ven 22/01/2027 21:00", "ASD MESSAPICA BASKET CEGLIE", "ASD SCUOLA BASKET MARTINESE", 0, 0, "Da giocare"),

    ("B10_2158", "Girone B", 10, "Dom 24/01/2027 18:30", "ASD MURGIA BASKET SANTERAMO", "POL. OLYMPIA CLUB RUTIGLIANO", 0, 0, "Da giocare"),

    ("B11_2159", "Girone B", 11, "Dom 31/01/2027 18:00", "ASD DREAM BASKET ALTAMURA", "ASD MURGIA BASKET SANTERAMO", 0, 0, "Da giocare"),

    ("B11_2160", "Girone B", 11, "Dom 31/01/2027 18:00", "SUPPORT_O TARANTO", "ASD CLUB GIGANTI CISTERNINO", 0, 0, "Da giocare"),

    ("B11_2161", "Girone B", 11, "Dom 31/01/2027 18:00", "ASD BASKET FASANO", "ASD MESSAPICA BASKET CEGLIE", 0, 0, "Da giocare"),

    ("B11_2162", "Girone B", 11, "Dom 31/01/2027 18:00", "POL. OLYMPIA CLUB RUTIGLIANO", "ASD ATLETICA BASKET PUTIGNANO", 0, 0, "Da giocare"),

    ("B11_2163", "Girone B", 11, "Dom 31/01/2027 18:30", "MASSERIA SEMERARO NEW SPORTING MOTTOLA", "DOMITI LA PINTA BASKET PULSANO", 0, 0, "Da giocare"),

    ("B12_2164", "Girone B", 12, "Sab 06/02/2027 20:00", "ASD MESSAPICA BASKET CEGLIE", "ASD CLUB GIGANTI CISTERNINO", 0, 0, "Da giocare"),

    ("B12_2165", "Girone B", 12, "Dom 07/02/2027 18:00", "DOMITI LA PINTA BASKET PULSANO", "SUPPORT_O TARANTO", 0, 0, "Da giocare"),

    ("B12_2166", "Girone B", 12, "Sab 06/02/2027 18:00", "ASD ATLETICA BASKET PUTIGNANO", "ASD BASKET FASANO", 0, 0, "Da giocare"),

    ("B12_2167", "Girone B", 12, "Dom 07/02/2027 18:30", "MASSERIA SEMERARO NEW SPORTING MOTTOLA", "ASD MURGIA BASKET SANTERAMO", 0, 0, "Da giocare"),

    ("B12_2168", "Girone B", 12, "Dom 07/02/2027 18:00", "ASD DREAM BASKET ALTAMURA", "ASD SCUOLA BASKET MARTINESE", 0, 0, "Da giocare"),

    ("B13_2169", "Girone B", 13, "Sab 13/02/2027 19:00", "ASD BASKET FASANO", "ASD DREAM BASKET ALTAMURA", 0, 0, "Da giocare"),

    ("B13_2170", "Girone B", 13, "Dom 14/02/2027 18:30", "ASD MURGIA BASKET SANTERAMO", "DOMITI LA PINTA BASKET PULSANO", 0, 0, "Da giocare"),

    ("B13_2171", "Girone B", 13, "Sab 13/02/2027 18:45", "ASD SCUOLA BASKET MARTINESE", "ASD ATLETICA BASKET PUTIGNANO", 0, 0, "Da giocare"),

    ("B13_2172", "Girone B", 13, "Dom 14/02/2027 18:00", "POL. OLYMPIA CLUB RUTIGLIANO", "ASD MESSAPICA BASKET CEGLIE", 0, 0, "Da giocare"),

    ("B13_2173", "Girone B", 13, "Dom 14/02/2027 18:00", "SUPPORT_O TARANTO", "MASSERIA SEMERARO NEW SPORTING MOTTOLA", 0, 0, "Da giocare"),

    ("B14_2174", "Girone B", 14, "Dom 21/02/2027 18:00", "ASD DREAM BASKET ALTAMURA", "SUPPORT_O TARANTO", 0, 0, "Da giocare"),

    ("B14_2175", "Girone B", 14, "Dom 21/02/2027 18:00", "DOMITI LA PINTA BASKET PULSANO", "ASD SCUOLA BASKET MARTINESE", 0, 0, "Da giocare"),

    ("B14_2176", "Girone B", 14, "Sab 20/02/2027 18:00", "ASD ATLETICA BASKET PUTIGNANO", "ASD MURGIA BASKET SANTERAMO", 0, 0, "Da giocare"),

    ("B14_2177", "Girone B", 14, "Sab 20/02/2027 19:00", "ASD CLUB GIGANTI CISTERNINO", "POL. OLYMPIA CLUB RUTIGLIANO", 0, 0, "Da giocare"),

    ("B14_2178", "Girone B", 14, "Dom 21/02/2027 18:30", "MASSERIA SEMERARO NEW SPORTING MOTTOLA", "ASD BASKET FASANO", 0, 0, "Da giocare"),

    ("B15_2179", "Girone B", 15, "Dom 28/02/2027 18:30", "ASD MURGIA BASKET SANTERAMO", "ASD MESSAPICA BASKET CEGLIE", 0, 0, "Da giocare"),

    ("B15_2180", "Girone B", 15, "Sab 27/02/2027 18:45", "ASD SCUOLA BASKET MARTINESE", "MASSERIA SEMERARO NEW SPORTING MOTTOLA", 0, 0, "Da giocare"),

    ("B15_2181", "Girone B", 15, "Dom 28/02/2027 18:00", "ASD DREAM BASKET ALTAMURA", "ASD CLUB GIGANTI CISTERNINO", 0, 0, "Da giocare"),

    ("B15_2182", "Girone B", 15, "Dom 28/02/2027 18:00", "SUPPORT_O TARANTO", "POL. OLYMPIA CLUB RUTIGLIANO", 0, 0, "Da giocare"),

    ("B15_2183", "Girone B", 15, "Dom 28/02/2027 18:00", "ASD BASKET FASANO", "DOMITI LA PINTA BASKET PULSANO", 0, 0, "Da giocare"),

    ("B16_2184", "Girone B", 16, "Dom 07/03/2027 18:00", "POL. OLYMPIA CLUB RUTIGLIANO", "ASD DREAM BASKET ALTAMURA", 0, 0, "Da giocare"),

    ("B16_2185", "Girone B", 16, "Sab 06/03/2027 18:45", "ASD SCUOLA BASKET MARTINESE", "ASD MURGIA BASKET SANTERAMO", 0, 0, "Da giocare"),

    ("B16_2186", "Girone B", 16, "Ven 05/03/2027 19:00", "ASD MESSAPICA BASKET CEGLIE", "SUPPORT_O TARANTO", 0, 0, "Da giocare"),

    ("B16_2187", "Girone B", 16, "Dom 07/03/2027 18:00", "DOMITI LA PINTA BASKET PULSANO", "ASD ATLETICA BASKET PUTIGNANO", 0, 0, "Da giocare"),

    ("B16_2188", "Girone B", 16, "Sab 06/03/2027 19:00", "ASD CLUB GIGANTI CISTERNINO", "MASSERIA SEMERARO NEW SPORTING MOTTOLA", 0, 0, "Da giocare"),

    ("B17_2189", "Girone B", 17, "Dom 14/03/2027 18:00", "POL. OLYMPIA CLUB RUTIGLIANO", "ASD SCUOLA BASKET MARTINESE", 0, 0, "Da giocare"),

    ("B17_2190", "Girone B", 17, "Dom 14/03/2027 18:30", "ASD MURGIA BASKET SANTERAMO", "ASD CLUB GIGANTI CISTERNINO", 0, 0, "Da giocare"),

    ("B17_2191", "Girone B", 17, "Dom 14/03/2027 18:00", "SUPPORT_O TARANTO", "ASD BASKET FASANO", 0, 0, "Da giocare"),

    ("B17_2192", "Girone B", 17, "Gio 11/03/2027 21:00", "MASSERIA SEMERARO NEW SPORTING MOTTOLA", "ASD DREAM BASKET ALTAMURA", 0, 0, "Da giocare"),

    ("B17_2193", "Girone B", 17, "Sab 13/03/2027 18:00", "ASD ATLETICA BASKET PUTIGNANO", "ASD MESSAPICA BASKET CEGLIE", 0, 0, "Da giocare"),

    ("B18_2194", "Girone B", 18, "Sab 20/03/2027 19:00", "ASD CLUB GIGANTI CISTERNINO", "DOMITI LA PINTA BASKET PULSANO", 0, 0, "Da giocare"),

    ("B18_2195", "Girone B", 18, "Sab 20/03/2027 18:45", "ASD SCUOLA BASKET MARTINESE", "SUPPORT_O TARANTO", 0, 0, "Da giocare"),

    ("B18_2196", "Girone B", 18, "Ven 19/03/2027 21:00", "ASD MESSAPICA BASKET CEGLIE", "MASSERIA SEMERARO NEW SPORTING MOTTOLA", 0, 0, "Da giocare"),

    ("B18_2197", "Girone B", 18, "Dom 21/03/2027 18:00", "ASD BASKET FASANO", "POL. OLYMPIA CLUB RUTIGLIANO", 0, 0, "Da giocare"),

    ("B18_2198", "Girone B", 18, "Dom 21/03/2027 18:00", "ASD DREAM BASKET ALTAMURA", "ASD ATLETICA BASKET PUTIGNANO", 0, 0, "Da giocare"),

    ("B19_2199", "Girone B", 19, "Dom 04/04/2027 18:30", "MASSERIA SEMERARO NEW SPORTING MOTTOLA", "ASD ATLETICA BASKET PUTIGNANO", 0, 0, "Da giocare"),

    ("B19_2200", "Girone B", 19, "Dom 04/04/2027 18:30", "ASD MURGIA BASKET SANTERAMO", "ASD BASKET FASANO", 0, 0, "Da giocare"),

    ("B19_2201", "Girone B", 19, "Dom 04/04/2027 18:00", "POL. OLYMPIA CLUB RUTIGLIANO", "DOMITI LA PINTA BASKET PULSANO", 0, 0, "Da giocare"),

    ("B19_2202", "Girone B", 19, "Sab 03/04/2027 20:00", "ASD MESSAPICA BASKET CEGLIE", "ASD DREAM BASKET ALTAMURA", 0, 0, "Da giocare"),

    ("B19_2203", "Girone B", 19, "Sab 03/04/2027 19:00", "ASD CLUB GIGANTI CISTERNINO", "ASD SCUOLA BASKET MARTINESE", 0, 0, "Da giocare"),

    ("B20_2204", "Girone B", 20, "Dom 11/04/2027 18:00", "DOMITI LA PINTA BASKET PULSANO", "ASD MESSAPICA BASKET CEGLIE", 0, 0, "Da giocare"),

    ("B20_2205", "Girone B", 20, "Dom 11/04/2027 18:00", "SUPPORT_O TARANTO", "ASD MURGIA BASKET SANTERAMO", 0, 0, "Da giocare"),

    ("B20_2206", "Girone B", 20, "Sab 10/04/2027 19:00", "ASD BASKET FASANO", "ASD SCUOLA BASKET MARTINESE", 0, 0, "Da giocare"),

    ("B20_2207", "Girone B", 20, "Dom 11/04/2027 18:30", "MASSERIA SEMERARO NEW SPORTING MOTTOLA", "POL. OLYMPIA CLUB RUTIGLIANO", 0, 0, "Da giocare"),

    ("B20_2208", "Girone B", 20, "Sab 10/04/2027 18:00", "ASD ATLETICA BASKET PUTIGNANO", "ASD CLUB GIGANTI CISTERNINO", 0, 0, "Da giocare"),

    ("B21_2209", "Girone B", 21, "Dom 18/04/2027 18:00", "DOMITI LA PINTA BASKET PULSANO", "ASD DREAM BASKET ALTAMURA", 0, 0, "Da giocare"),

    ("B21_2210", "Girone B", 21, "Dom 18/04/2027 18:00", "POL. OLYMPIA CLUB RUTIGLIANO", "ASD MURGIA BASKET SANTERAMO", 0, 0, "Da giocare"),

    ("B21_2211", "Girone B", 21, "Sab 17/04/2027 18:45", "ASD SCUOLA BASKET MARTINESE", "ASD MESSAPICA BASKET CEGLIE", 0, 0, "Da giocare"),

    ("B21_2212", "Girone B", 21, "Sab 17/04/2027 19:00", "ASD CLUB GIGANTI CISTERNINO", "ASD BASKET FASANO", 0, 0, "Da giocare"),

    ("B21_2213", "Girone B", 21, "Dom 18/04/2027 18:00", "SUPPORT_O TARANTO", "ASD ATLETICA BASKET PUTIGNANO", 0, 0, "Da giocare"),

    ("B22_2214", "Girone B", 22, "Dom 25/04/2027 18:00", "DOMITI LA PINTA BASKET PULSANO", "MASSERIA SEMERARO NEW SPORTING MOTTOLA", 0, 0, "Da giocare"),

    ("B22_2215", "Girone B", 22, "Dom 25/04/2027 18:30", "ASD MURGIA BASKET SANTERAMO", "ASD DREAM BASKET ALTAMURA", 0, 0, "Da giocare"),

    ("B22_2216", "Girone B", 22, "Sab 24/04/2027 20:00", "ASD MESSAPICA BASKET CEGLIE", "ASD BASKET FASANO", 0, 0, "Da giocare"),

    ("B22_2217", "Girone B", 22, "Sab 24/04/2027 18:00", "ASD ATLETICA BASKET PUTIGNANO", "POL. OLYMPIA CLUB RUTIGLIANO", 0, 0, "Da giocare"),

    ("B22_2218", "Girone B", 22, "Sab 24/04/2027 19:00", "ASD CLUB GIGANTI CISTERNINO", "SUPPORT_O TARANTO", 0, 0, "Da giocare"),



    # ==========================================

    # GIRONE C (Giornate 1-22 + Risultati G1-G3)

    # ==========================================

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

    ("C04_2234", "Girone C", 4, "Dom 29/11/2026 17:00", "ASD BELLFIKA MESAGNE", "ASD BASKET TRICASE", 0, 0, "Da giocare"),

    ("C04_2235", "Girone C", 4, "Dom 29/11/2026 18:00", "ASD POLISPORTIVA MANDURIA", "ALL STAR BASKET FRANCAVILLA", 0, 0, "Da giocare"),

    ("C04_2236", "Girone C", 4, "Sab 28/11/2026 18:00", "ASD NEW BASKET CARMIANO", "DIERRE ARREDAMENTI CALIMERA BASKET", 0, 0, "Da giocare"),

    ("C04_2237", "Girone C", 4, "Sab 28/11/2026 16:30", "AZ DISINFESTAZIONI SRL VIRTUS BRINDISI", "ASD ASSI BASKET BRINDISI", 0, 0, "Da giocare"),

    ("C04_2238", "Girone C", 4, "Sab 28/11/2026 16:30", "SENSI PALLACANESTRO LUPA LECCE", "ASD MAGIC GALATINA", 0, 0, "Da giocare"),

    ("C05_2239", "Girone C", 5, "Dom 06/12/2026 18:30", "DIERRE ARREDAMENTI CALIMERA BASKET", "ASD ASSI BASKET BRINDISI", 0, 0, "Da giocare"),

    ("C05_2240", "Girone C", 5, "Sab 05/12/2026 18:30", "ASD MAGIC GALATINA", "ASD POLISPORTIVA MANDURIA", 0, 0, "Da giocare"),

    ("C05_2241", "Girone C", 5, "Sab 05/12/2026 18:00", "A.POL.DIL.AURORA BRINDISI", "ASD BELLFIKA MESAGNE", 0, 0, "Da giocare"),

    ("C05_2242", "Girone C", 5, "Sab 05/12/2026 18:30", "SENSI PALLACANESTRO LUPA LECCE", "ASD NEW BASKET CARMIANO", 0, 0, "Da giocare"),

    ("C05_2243", "Girone C", 5, "Sab 05/12/2026 18:00", "ALL STAR BASKET FRANCAVILLA", "AZ DISINFESTAZIONI SRL VIRTUS BRINDISI", 0, 0, "Da giocare"),

    ("C06_2244", "Girone C", 6, "Sab 12/12/2026 16:30", "AZ DISINFESTAZIONI SRL VIRTUS BRINDISI", "A.POL.DIL.AURORA BRINDISI", 0, 0, "Da giocare"),

    ("C06_2245", "Girone C", 6, "Dom 13/12/2026 18:30", "DIERRE ARREDAMENTI CALIMERA BASKET", "ASD POLISPORTIVA MANDURIA", 0, 0, "Da giocare"),

    ("C06_2246", "Girone C", 6, "Dom 13/12/2026 18:00", "ASD MAGIC GALATINA", "ASD NEW BASKET CARMIANO", 0, 0, "Da giocare"),

    ("C06_2247", "Girone C", 6, "Dom 13/12/2026 18:00", "ASD BASKET TRICASE", "ALL STAR BASKET FRANCAVILLA", 0, 0, "Da giocare"),

    ("C06_2248", "Girone C", 6, "Sab 12/12/2026 18:00", "ASD ASSI BASKET BRINDISI", "SENSI PALLACANESTRO LUPA LECCE", 0, 0, "Da giocare"),

    ("C07_2249", "Girone C", 7, "Sab 19/12/2026 18:00", "ALL STAR BASKET FRANCAVILLA", "DIERRE ARREDAMENTI CALIMERA BASKET", 0, 0, "Da giocare"),

    ("C07_2250", "Girone C", 7, "Dom 20/12/2026 20:00", "ASD NEW BASKET CARMIANO", "AZ DISINFESTAZIONI SRL VIRTUS BRINDISI", 0, 0, "Da giocare"),

    ("C07_2251", "Girone C", 7, "Ven 18/12/2026 20:30", "ASD POLISPORTIVA MANDURIA", "ASD BASKET TRICASE", 0, 0, "Da giocare"),

    ("C07_2252", "Girone C", 7, "Sab 19/12/2026 18:30", "SENSI PALLACANESTRO LUPA LECCE", "ASD BELLFIKA MESAGNE", 0, 0, "Da giocare"),

    ("C07_2253", "Girone C", 7, "Sab 19/12/2026 18:00", "A.POL.DIL.AURORA BRINDISI", "ASD MAGIC GALATINA", 0, 0, "Da giocare"),

    ("C08_2254", "Girone C", 8, "Dom 10/01/2027 18:00", "ASD POLISPORTIVA MANDURIA", "ASD BELLFIKA MESAGNE", 0, 0, "Da giocare"),

    ("C08_2255", "Girone C", 8, "Sab 09/01/2027 18:00", "A.POL.DIL.AURORA BRINDISI", "ASD NEW BASKET CARMIANO", 0, 0, "Da giocare"),

    ("C08_2256", "Girone C", 8, "Dom 10/01/2027 18:00", "ASD BASKET TRICASE", "ASD ASSI BASKET BRINDISI", 0, 0, "Da giocare"),

    ("C08_2257", "Girone C", 8, "Dom 10/01/2027 18:30", "DIERRE ARREDAMENTI CALIMERA BASKET", "SENSI PALLACANESTRO LUPA LECCE", 0, 0, "Da giocare"),

    ("C08_2258", "Girone C", 8, "Sab 09/01/2027 18:30", "ASD MAGIC GALATINA", "AZ DISINFESTAZIONI SRL VIRTUS BRINDISI", 0, 0, "Da giocare"),

    ("C09_2259", "Girone C", 9, "Sab 16/01/2027 18:30", "SENSI PALLACANESTRO LUPA LECCE", "A.POL.DIL.AURORA BRINDISI", 0, 0, "Da giocare"),

    ("C09_2260", "Girone C", 9, "Sab 16/01/2027 16:30", "AZ DISINFESTAZIONI SRL VIRTUS BRINDISI", "ASD BELLFIKA MESAGNE", 0, 0, "Da giocare"),

    ("C09_2261", "Girone C", 9, "Dom 17/01/2027 18:00", "ASD POLISPORTIVA MANDURIA", "ASD NEW BASKET CARMIANO", 0, 0, "Da giocare"),

    ("C09_2262", "Girone C", 9, "Sab 16/01/2027 18:00", "ASD ASSI BASKET BRINDISI", "ALL STAR BASKET FRANCAVILLA", 0, 0, "Da giocare"),

    ("C09_2263", "Girone C", 9, "Dom 17/01/2027 18:30", "DIERRE ARREDAMENTI CALIMERA BASKET", "ASD BASKET TRICASE", 0, 0, "Da giocare"),

    ("C10_2264", "Girone C", 10, "Sab 23/01/2027 16:30", "SENSI PALLACANESTRO LUPA LECCE", "ASD BASKET TRICASE", 0, 0, "Da giocare"),

    ("C10_2265", "Girone C", 10, "Sab 23/01/2027 18:00", "ASD ASSI BASKET BRINDISI", "ASD POLISPORTIVA MANDURIA", 0, 0, "Da giocare"),

    ("C10_2266", "Girone C", 10, "Dom 24/01/2027 17:00", "ASD BELLFIKA MESAGNE", "ASD MAGIC GALATINA", 0, 0, "Da giocare"),

    ("C10_2267", "Girone C", 10, "Sab 23/01/2027 18:00", "A.POL.DIL.AURORA BRINDISI", "ALL STAR BASKET FRANCAVILLA", 0, 0, "Da giocare"),

    ("C10_2268", "Girone C", 10, "Sab 23/01/2027 16:30", "AZ DISINFESTAZIONI SRL VIRTUS BRINDISI", "DIERRE ARREDAMENTI CALIMERA BASKET", 0, 0, "Da giocare"),

    ("C11_2269", "Girone C", 11, "Dom 31/01/2027 20:00", "ASD NEW BASKET CARMIANO", "ASD BELLFIKA MESAGNE", 0, 0, "Da giocare"),

    ("C11_2270", "Girone C", 11, "Sab 30/01/2027 18:00", "ALL STAR BASKET FRANCAVILLA", "SENSI PALLACANESTRO LUPA LECCE", 0, 0, "Da giocare"),

    ("C11_2271", "Girone C", 11, "Dom 31/01/2027 18:00", "ASD POLISPORTIVA MANDURIA", "A.POL.DIL.AURORA BRINDISI", 0, 0, "Da giocare"),

    ("C11_2272", "Girone C", 11, "Dom 31/01/2027 18:00", "ASD MAGIC GALATINA", "ASD ASSI BASKET BRINDISI", 0, 0, "Da giocare"),

    ("C11_2273", "Girone C", 11, "Dom 31/01/2027 18:00", "ASD BASKET TRICASE", "AZ DISINFESTAZIONI SRL VIRTUS BRINDISI", 0, 0, "Da giocare"),

    ("C12_2274", "Girone C", 12, "Sab 06/02/2027 18:00", "A.POL.DIL.AURORA BRINDISI", "ASD BASKET TRICASE", 0, 0, "Da giocare"),

    ("C12_2275", "Girone C", 12, "Sab 06/02/2027 16:30", "AZ DISINFESTAZIONI SRL VIRTUS BRINDISI", "SENSI PALLACANESTRO LUPA LECCE", 0, 0, "Da giocare"),

    ("C12_2276", "Girone C", 12, "Dom 07/02/2027 18:00", "ASD NEW BASKET CARMIANO", "ASD ASSI BASKET BRINDISI", 0, 0, "Da giocare"),

    ("C12_2277", "Girone C", 12, "Dom 07/02/2027 18:00", "ASD BELLFIKA MESAGNE", "ALL STAR BASKET FRANCAVILLA", 0, 0, "Da giocare"),

    ("C12_2278", "Girone C", 12, "Sab 06/02/2027 18:30", "ASD MAGIC GALATINA", "DIERRE ARREDAMENTI CALIMERA BASKET", 0, 0, "Da giocare"),

    ("C13_2279", "Girone C", 13, "Sab 13/02/2027 18:00", "ALL STAR BASKET FRANCAVILLA", "ASD NEW BASKET CARMIANO", 0, 0, "Da giocare"),

    ("C13_2280", "Girone C", 13, "Dom 14/02/2027 18:00", "ASD BASKET TRICASE", "ASD MAGIC GALATINA", 0, 0, "Da giocare"),

    ("C13_2281", "Girone C", 13, "Dom 14/02/2027 18:30", "DIERRE ARREDAMENTI CALIMERA BASKET", "A.POL.DIL.AURORA BRINDISI", 0, 0, "Da giocare"),

    ("C13_2282", "Girone C", 13, "Sab 13/02/2027 18:00", "ASD ASSI BASKET BRINDISI", "ASD BELLFIKA MESAGNE", 0, 0, "Da giocare"),

    ("C13_2283", "Girone C", 13, "Dom 14/02/2027 18:00", "ASD POLISPORTIVA MANDURIA", "AZ DISINFESTAZIONI SRL VIRTUS BRINDISI", 0, 0, "Da giocare"),

    ("C14_2284", "Girone C", 14, "Dom 21/02/2027 18:00", "ASD NEW BASKET CARMIANO", "ASD BASKET TRICASE", 0, 0, "Da giocare"),

    ("C14_2285", "Girone C", 14, "Sab 20/02/2027 18:00", "A.POL.DIL.AURORA BRINDISI", "ASD ASSI BASKET BRINDISI", 0, 0, "Da giocare"),

    ("C14_2286", "Girone C", 14, "Dom 21/02/2027 17:00", "ASD BELLFIKA MESAGNE", "DIERRE ARREDAMENTI CALIMERA BASKET", 0, 0, "Da giocare"),

    ("C14_2287", "Girone C", 14, "Sab 20/02/2027 18:30", "ASD MAGIC GALATINA", "ALL STAR BASKET FRANCAVILLA", 0, 0, "Da giocare"),

    ("C14_2288", "Girone C", 14, "Sab 20/02/2027 18:30", "SENSI PALLACANESTRO LUPA LECCE", "ASD POLISPORTIVA MANDURIA", 0, 0, "Da giocare"),

    ("C15_2289", "Girone C", 15, "Dom 28/02/2027 18:00", "ASD ASSI BASKET BRINDISI", "AZ DISINFESTAZIONI SRL VIRTUS BRINDISI", 0, 0, "Da giocare"),

    ("C15_2290", "Girone C", 15, "Dom 28/02/2027 18:00", "ASD BASKET TRICASE", "ASD BELLFIKA MESAGNE", 0, 0, "Da giocare"),

    ("C15_2291", "Girone C", 15, "Dom 28/02/2027 18:00", "ASD MAGIC GALATINA", "SENSI PALLACANESTRO LUPA LECCE", 0, 0, "Da giocare"),

    ("C15_2292", "Girone C", 15, "Sab 27/02/2027 18:00", "ALL STAR BASKET FRANCAVILLA", "ASD POLISPORTIVA MANDURIA", 0, 0, "Da giocare"),

    ("C15_2293", "Girone C", 15, "Sab 27/02/2027 18:30", "DIERRE ARREDAMENTI CALIMERA BASKET", "ASD NEW BASKET CARMIANO", 0, 0, "Da giocare"),

    ("C16_2294", "Girone C", 16, "Dom 07/03/2027 18:00", "ASD POLISPORTIVA MANDURIA", "ASD MAGIC GALATINA", 0, 0, "Da giocare"),

    ("C16_2295", "Girone C", 16, "Dom 07/03/2027 17:00", "ASD BELLFIKA MESAGNE", "A.POL.DIL.AURORA BRINDISI", 0, 0, "Da giocare"),

    ("C16_2296", "Girone C", 16, "Dom 07/03/2027 18:00", "ASD NEW BASKET CARMIANO", "SENSI PALLACANESTRO LUPA LECCE", 0, 0, "Da giocare"),

    ("C16_2297", "Girone C", 16, "Sab 06/03/2027 16:30", "AZ DISINFESTAZIONI SRL VIRTUS BRINDISI", "ALL STAR BASKET FRANCAVILLA", 0, 0, "Da giocare"),

    ("C16_2298", "Girone C", 16, "Sab 06/03/2027 18:00", "ASD ASSI BASKET BRINDISI", "DIERRE ARREDAMENTI CALIMERA BASKET", 0, 0, "Da giocare"),

    ("C17_2299", "Girone C", 17, "Sab 13/03/2027 18:00", "ALL STAR BASKET FRANCAVILLA", "ASD BASKET TRICASE", 0, 0, "Da giocare"),

    ("C17_2300", "Girone C", 17, "Dom 14/03/2027 18:30", "SENSI PALLACANESTRO LUPA LECCE", "ASD ASSI BASKET BRINDISI", 0, 0, "Da giocare"),

    ("C17_2301", "Girone C", 17, "Dom 14/03/2027 18:00", "ASD POLISPORTIVA MANDURIA", "DIERRE ARREDAMENTI CALIMERA BASKET", 0, 0, "Da giocare"),

    ("C17_2302", "Girone C", 17, "Sab 13/03/2027 18:00", "A.POL.DIL.AURORA BRINDISI", "AZ DISINFESTAZIONI SRL VIRTUS BRINDISI", 0, 0, "Da giocare"),

    ("C17_2303", "Girone C", 17, "Sab 13/03/2027 18:00", "ASD NEW BASKET CARMIANO", "ASD MAGIC GALATINA", 0, 0, "Da giocare"),

    ("C18_2304", "Girone C", 18, "Dom 21/03/2027 17:00", "ASD BELLFIKA MESAGNE", "SENSI PALLACANESTRO LUPA LECCE", 0, 0, "Da giocare"),

    ("C18_2305", "Girone C", 18, "Dom 21/03/2027 18:30", "DIERRE ARREDAMENTI CALIMERA BASKET", "ALL STAR BASKET FRANCAVILLA", 0, 0, "Da giocare"),

    ("C18_2306", "Girone C", 18, "Sab 20/03/2027 16:30", "AZ DISINFESTAZIONI SRL VIRTUS BRINDISI", "ASD NEW BASKET CARMIANO", 0, 0, "Da giocare"),

    ("C18_2307", "Girone C", 18, "Dom 21/03/2027 18:00", "ASD BASKET TRICASE", "ASD POLISPORTIVA MANDURIA", 0, 0, "Da giocare"),

    ("C18_2308", "Girone C", 18, "Sab 20/03/2027 18:30", "ASD MAGIC GALATINA", "A.POL.DIL.AURORA BRINDISI", 0, 0, "Da giocare"),

    ("C19_2309", "Girone C", 19, "Dom 04/04/2027 18:30", "SENSI PALLACANESTRO LUPA LECCE", "DIERRE ARREDAMENTI CALIMERA BASKET", 0, 0, "Da giocare"),

    ("C19_2310", "Girone C", 19, "Sab 03/04/2027 18:00", "A.POL.DIL.AURORA BRINDISI", "ASD NEW BASKET CARMIANO", 0, 0, "Da giocare"),

    ("C19_2311", "Girone C", 19, "Sab 03/04/2027 16:30", "AZ DISINFESTAZIONI SRL VIRTUS BRINDISI", "ASD MAGIC GALATINA", 0, 0, "Da giocare"),

    ("C19_2312", "Girone C", 19, "Sab 03/04/2027 16:30", "ASD BELLFIKA MESAGNE", "ASD POLISPORTIVA MANDURIA", 0, 0, "Da giocare"),

    ("C19_2313", "Girone C", 19, "Sab 03/04/2027 18:00", "ASD ASSI BASKET BRINDISI", "ASD BASKET TRICASE", 0, 0, "Da giocare"),

    ("C20_2314", "Girone C", 20, "Sab 10/04/2027 18:00", "A.POL.DIL.AURORA BRINDISI", "SENSI PALLACANESTRO LUPA LECCE", 0, 0, "Da giocare"),

    ("C20_2315", "Girone C", 20, "Dom 11/04/2027 18:00", "DIERRE ARREDAMENTI CALIMERA BASKET", "ASD BASKET TRICASE", 0, 0, "Da giocare"),

    ("C20_2316", "Girone C", 20, "Dom 11/04/2027 17:00", "ASD BELLFIKA MESAGNE", "AZ DISINFESTAZIONI SRL VIRTUS BRINDISI", 0, 0, "Da giocare"),

    ("C20_2317", "Girone C", 20, "Sab 10/04/2027 18:00", "ASD NEW BASKET CARMIANO", "ASD POLISPORTIVA MANDURIA", 0, 0, "Da giocare"),

    ("C20_2318", "Girone C", 20, "Sab 10/04/2027 18:00", "ALL STAR BASKET FRANCAVILLA", "ASD ASSI BASKET BRINDISI", 0, 0, "Da giocare"),

    ("C21_2319", "Girone C", 21, "Sab 17/04/2027 18:30", "ASD MAGIC GALATINA", "ASD BELLFIKA MESAGNE", 0, 0, "Da giocare"),

    ("C21_2320", "Girone C", 21, "Dom 18/04/2027 18:30", "DIERRE ARREDAMENTI CALIMERA BASKET", "AZ DISINFESTAZIONI SRL VIRTUS BRINDISI", 0, 0, "Da giocare"),

    ("C21_2321", "Girone C", 21, "Dom 18/04/2027 18:00", "SENSI PALLACANESTRO LUPA LECCE", "ASD BASKET TRICASE", 0, 0, "Da giocare"),

    ("C21_2322", "Girone C", 21, "Dom 18/04/2027 18:00", "ASD POLISPORTIVA MANDURIA", "ASD ASSI BASKET BRINDISI", 0, 0, "Da giocare"),

    ("C21_2323", "Girone C", 21, "Sab 17/04/2027 18:00", "ALL STAR BASKET FRANCAVILLA", "A.POL.DIL.AURORA BRINDISI", 0, 0, "Da giocare"),

    ("C22_2324", "Girone C", 22, "Sab 24/04/2027 18:00", "ASD MAGIC GALATINA", "ASD ASSI BASKET BRINDISI", 0, 0, "Da giocare"),

    ("C22_2325", "Girone C", 22, "Sab 24/04/2027 16:30", "AZ DISINFESTAZIONI SRL VIRTUS BRINDISI", "ASD BASKET TRICASE", 0, 0, "Da giocare"),

    ("C22_2326", "Girone C", 22, "Sab 24/04/2027 18:00", "A.POL.DIL.AURORA BRINDISI", "ASD POLISPORTIVA MANDURIA", 0, 0, "Da giocare"),

    ("C22_2327", "Girone C", 22, "Sab 24/04/2027 18:30", "SENSI PALLACANESTRO LUPA LECCE", "ALL STAR BASKET FRANCAVILLA", 0, 0, "Da giocare"),

    ("C22_2328", "Girone C", 22, "Dom 25/04/2027 17:00", "ASD BELLFIKA MESAGNE", "ASD NEW BASKET CARMIANO", 0, 0, "Da giocare"),

]





def _extract_jersey_number(name: str, explicit_num: object = None) -> int:

    """Estrae o valida un numero di maglia valido (0-99); restituisce 999 se assente o non valido."""

    try:

        if explicit_num is not None:

            if isinstance(explicit_num, (list, tuple, dict, set)):

                explicit_num = None

            elif not (isinstance(explicit_num, float) and pd.isna(explicit_num)):

                num_str = str(explicit_num).strip().lstrip("#")

                if num_str != "":

                    parsed = pd.to_numeric(num_str, errors="coerce")

                    if pd.notna(parsed):

                        val = int(float(parsed))

                        if 0 <= val <= 99:

                            return val

    except Exception:

        pass



    try:

        m = re.match(r"^\s*#?(\d{1,2})\b", str(name or ""))

        if m:

            val = int(m.group(1))

            if 0 <= val <= 99:

                return val

    except Exception:

        pass



    return 999





def _format_jersey_display(num_val: object, empty_placeholder: str = "—") -> str:

    """Formatta in modo sicuro un numero di maglia (incluso '0' -> '#0') o restituisce empty_placeholder."""

    placeholder = str(empty_placeholder) if empty_placeholder is not None else "—"

    try:

        if num_val is None or isinstance(num_val, (list, tuple, dict, set)):

            return placeholder

        if isinstance(num_val, bool):

            return placeholder

        if isinstance(num_val, str):

            cleaned = num_val.strip()

            if not cleaned or cleaned in {"—", "-", "?", "None", "nan", "NaN"}:

                return placeholder

            cleaned = cleaned.lstrip("#").strip()

            parsed = pd.to_numeric(cleaned, errors="coerce")

        else:

            if pd.isna(num_val):

                return placeholder

            parsed = pd.to_numeric(num_val, errors="coerce")



        if pd.isna(parsed):

            return placeholder

        n = int(float(parsed))

        if 0 <= n <= 99:

            return f"#{n}"

        return placeholder

    except Exception:

        return placeholder





def _p_row(

    giocatore: str,

    numero: int | None = None,

    pts: int = 0,

    minuti: str = "0",

    sf: bool = False,

    falli_c: int = 0,

    falli_s: int = 0,

    t2_r: int = 0,

    t2_t: int = 0,

    sc: int = 0,

    t3_r: int = 0,

    t3_t: int = 0,

    tl_r: int = 0,

    tl_t: int = 0,

    rim_o: int = 0,

    rim_d: int = 0,

    st_d: int = 0,

    st_s: int = 0,

    pal_p: int = 0,

    pal_r: int = 0,

    ass: int = 0,

    val_lega: int = 0,

    oer: float = 0.0,

) -> dict:

    resolved_num = _extract_jersey_number(str(giocatore), numero)

    return {

        "Giocatore": str(giocatore),

        "NUM": resolved_num,

        "PUN": int(pts),

        "MIN": str(minuti),

        "SF": bool(sf),

        "F_C": int(falli_c),

        "F_S": int(falli_s),

        "2PT_R": int(t2_r),

        "2PT_T": int(t2_t),

        "SC": int(sc),

        "3PT_R": int(t3_r),

        "3PT_T": int(t3_t),

        "TL_R": int(tl_r),

        "TL_T": int(tl_t),

        "RIM_O": int(rim_o),

        "RIM_D": int(rim_d),

        "ST_D": int(st_d),

        "ST_S": int(st_s),

        "PAL_P": int(pal_p),

        "PAL_R": int(pal_r),

        "ASS": int(ass),

        "VAL": int(val_lega),

        "OER": float(oer),

    }





DEFAULT_ROUND3_DETAILS: dict[str, dict] = {

    "A03_1880": {

        "coach_home": "",

        "coach_away": "",

        "quarters_home": [19, 15, 15, 15],

        "quarters_away": [29, 14, 11, 23],

        "ot_home": 0,

        "ot_away": 0,

        "home_players": [

            _p_row("Maldera N.", pts=6),

            _p_row("D'Imperio M.", pts=14),

            _p_row("Turturo J.", pts=6),

            _p_row("Lavacca G.", pts=12),

            _p_row("Eremita A.", pts=10),

            _p_row("Ricci R.", pts=6),

            _p_row("Lovero L.", pts=10),

        ],

        "away_players": [

            _p_row("Provaroni F.", numero=0, pts=3, minuti="13:03", sf=True, falli_c=1, t3_r=1, t3_t=1),

            _p_row("Derosa L.", pts=23, minuti="35:42", sf=True, falli_c=4, t2_r=7, t2_t=10, tl_r=9, tl_t=12),

            _p_row("Desiante V.", pts=5, minuti="15:24", sf=True, falli_c=3, t2_r=1, t2_t=1, t3_r=1, t3_t=1),

            _p_row("D'Erasmo F.", pts=15, minuti="30:18", sf=True, falli_c=4, t2_r=4, t2_t=4, tl_r=7, tl_t=10),

            _p_row("Housni Z.", pts=9, minuti="36:17", sf=True, falli_c=2, t2_r=4, t2_t=6, tl_r=1, tl_t=3),

            _p_row("Silletti D.", pts=8, minuti="30:33", sf=True, falli_c=3, t3_r=2, t3_t=2, tl_r=2, tl_t=2),

            _p_row("Micunco M.", pts=2, minuti="02:27", sf=True, falli_c=2, t2_r=1, t2_t=1),

            _p_row("Colangelo A.", pts=12, minuti="29:52", sf=True, falli_c=4, t2_r=3, t2_t=3, t3_r=1, t3_t=1, tl_r=3, tl_t=3),

            _p_row("Dario Iacobone", pts=0, minuti="03:53", falli_c=1),

            _p_row("Fraccalvieri A.", pts=0, minuti="02:31", falli_c=1),

            _p_row("Antonio Vero (N.E.)", pts=0),

            _p_row("Gianpiero Calabrese (N.E.)", pts=0),

        ],

    },

    "A03_1877": {

        "coach_home": "",

        "coach_away": "",

        "quarters_home": [21, 13, 28, 24],

        "quarters_away": [17, 23, 14, 21],

        "ot_home": 0,

        "ot_away": 0,

        "home_players": [

            _p_row("Ruotolo A.", pts=15),

            _p_row("Mastromarco P.", pts=2),

            _p_row("Mariani G.", pts=25, t3_r=4),

            _p_row("Natali F.", pts=1),

            _p_row("Ruotolo L.", pts=19, t3_r=3),

            _p_row("Riganti A.", pts=18),

            _p_row("Germanà A.", pts=6),

        ],

        "away_players": [

            _p_row("Daniello M. G.", pts=2),

            _p_row("Tricarico F.", pts=9),

            _p_row("Russo R.", pts=2),

            _p_row("Khelfat N.", pts=8),

            _p_row("Rinaldi P.", pts=21),

            _p_row("Marano A.", pts=12),

            _p_row("Pepe S.", pts=14),

            _p_row("Kharebava N.", pts=5),

            _p_row("Russo W.", pts=2),

        ],

    },

    "A03_1879": {

        "coach_home": "",

        "coach_away": "",

        "quarters_home": [19, 23, 24, 12],

        "quarters_away": [20, 12, 23, 20],

        "ot_home": 0,

        "ot_away": 0,

        "home_players": [

            _p_row("Centrone L.", pts=10),

            _p_row("Iacovelli A.", pts=15),

            _p_row("Panessa A.", pts=6),

            _p_row("Rutigliano A.", pts=3),

            _p_row("Maietta G.", pts=17, t3_r=5),

            _p_row("De Meo N.", pts=6),

            _p_row("Larocchia A.", pts=16),

            _p_row("Mazzarano M.", pts=3),

            _p_row("Pastore A.", pts=2),

        ],

        "away_players": [

            _p_row("Barletta F.", pts=5),

            _p_row("Fuiano M.", pts=7),

            _p_row("Miale A. M.", pts=6),

            _p_row("Santagata C. A.", pts=2),

            _p_row("Miglio E.", pts=8),

            _p_row("Cicculli V.", pts=2),

            _p_row("Mazzeo R.", pts=22),

            _p_row("Scarponi I.", pts=23, t3_r=6),

        ],

    },

    "A03_1878": {

        "coach_home": "",

        "coach_away": "",

        "quarters_home": [13, 22, 24, 10],

        "quarters_away": [15, 22, 18, 24],

        "ot_home": 0,

        "ot_away": 0,

        "home_players": [

            _p_row("Di Gennaro D.", pts=9),

            _p_row("Ferrara A.", pts=11),

            _p_row("Guida M.", pts=7),

            _p_row("Tarantella E.", pts=16),

            _p_row("De Capua A.", pts=9),

            _p_row("Tartaglione R.", pts=8),

            _p_row("Di Santo F.", pts=5),

            _p_row("Conte A.", pts=4),

        ],

        "away_players": [

            _p_row("Antonio Carlucci", pts=9),

            _p_row("Marco D'Errico", pts=9),

            _p_row("Dadahon Mohamed Montemurro", pts=4),

            _p_row("Davide Lorusso", pts=6),

            _p_row("Angelo Manigrasso", pts=25),

            _p_row("Nicola Merlo", pts=12),

            _p_row("Roberto Gaeta", pts=2),

            _p_row("Giulio Grittani", pts=3),

            _p_row("Roberto Genchi", pts=3),

            _p_row("Stefano Stamerra", pts=3),

            _p_row("Mattia Emiliano", pts=1),

            _p_row("Vito Antonio Vaccaro", pts=2),

        ],

    },

    "A03_1881": {

        "coach_home": "",

        "coach_away": "",

        "quarters_home": [7, 16, 13, 15],

        "quarters_away": [16, 11, 10, 13],

        "ot_home": 0,

        "ot_away": 0,

        "home_players": [

            _p_row("Cannarella R.", pts=16),

            _p_row("Chieco S.", pts=2),

            _p_row("Bozzi G.", pts=9),

            _p_row("Sicolo M.", pts=8),

            _p_row("Santeramo M.", pts=2),

            _p_row("Panebianco S.", pts=4),

            _p_row("Piccaluga R.", pts=3),

            _p_row("Urso M.", pts=7),

        ],

        "away_players": [

            _p_row("De Marco G.", pts=4),

            _p_row("Colonna F.", pts=6),

            _p_row("Sciscioli P.", pts=2),

            _p_row("Catano K.", pts=5),

            _p_row("Ferrante D.", pts=2),

            _p_row("Cantatore E.", pts=9),

            _p_row("Di Vittorio S.", pts=6),

            _p_row("Mangione N.", pts=7),

            _p_row("Lasorsa C.", pts=9),

        ],

    },

}





# ==========================================

# PERSISTENZA SU GITHUB

# ==========================================

def _get_github_config() -> dict[str, str]:

    token = ""

    owner = DEFAULT_GITHUB_OWNER

    repo = DEFAULT_GITHUB_REPO

    branch = DEFAULT_GITHUB_BRANCH



    try:

        if "GITHUB_TOKEN" in st.secrets:

            token = str(st.secrets["GITHUB_TOKEN"]).strip()

        if "GITHUB_OWNER" in st.secrets and str(st.secrets["GITHUB_OWNER"]).strip():

            owner = str(st.secrets["GITHUB_OWNER"]).strip()

        if "GITHUB_REPO" in st.secrets and str(st.secrets["GITHUB_REPO"]).strip():

            repo = str(st.secrets["GITHUB_REPO"]).strip()

        if "GITHUB_BRANCH" in st.secrets and str(st.secrets["GITHUB_BRANCH"]).strip():

            branch = str(st.secrets["GITHUB_BRANCH"]).strip()

    except Exception:

        pass



    token = token or os.environ.get("GITHUB_TOKEN", "").strip()

    owner = os.environ.get("GITHUB_OWNER", owner).strip() or DEFAULT_GITHUB_OWNER

    repo = os.environ.get("GITHUB_REPO", repo).strip() or DEFAULT_GITHUB_REPO

    branch = os.environ.get("GITHUB_BRANCH", branch).strip() or DEFAULT_GITHUB_BRANCH



    if "/" in repo:

        parts = [p for p in repo.split("/") if p]

        if len(parts) >= 2:

            owner, repo = parts[0], parts[1]



    return {"token": token, "owner": owner, "repo": repo, "branch": branch}





def _github_get_json_file(cfg: dict[str, str], file_path: str) -> tuple[dict, str | None]:

    if not cfg["token"]:

        return {}, None



    url = (

        f"https://api.github.com/repos/{cfg['owner']}/{cfg['repo']}/contents/{file_path}"

        f"?ref={quote(cfg['branch'], safe='')}"

    )

    req = Request(

        url,

        headers={

            "Authorization": f"Bearer {cfg['token']}",

            "Accept": "application/vnd.github+json",

            "X-GitHub-Api-Version": "2022-11-28",

            "User-Agent": "dr2-puglia-app",

        },

        method="GET",

    )

    try:

        with urlopen(req, timeout=10) as resp:

            payload = json.loads(resp.read().decode("utf-8"))

            sha = payload.get("sha")

            raw_b64 = payload.get("content", "")

            decoded = base64.b64decode(raw_b64).decode("utf-8") if raw_b64 else "{}"

            parsed = json.loads(decoded)

            return (parsed if isinstance(parsed, dict) else {}), sha

    except HTTPError as err:

        if err.code == 404:

            return {}, None

        raise





def _github_put_json_file(cfg: dict[str, str], file_path: str, data: dict, commit_msg: str) -> tuple[bool, str]:

    content_str = json.dumps(data, indent=2, ensure_ascii=False) + "\n"

    if not cfg["token"]:

        return (

            False,

            "GITHUB_TOKEN non trovato nei Secrets: modifica salvata solo temporaneamente in sessione.",

        )



    try:

        _, current_sha = _github_get_json_file(cfg, file_path)

        content_b64 = base64.b64encode(content_str.encode("utf-8")).decode("ascii")

        body: dict[str, str] = {

            "message": commit_msg,

            "content": content_b64,

            "branch": cfg["branch"],

        }

        if current_sha:

            body["sha"] = current_sha



        url = f"https://api.github.com/repos/{cfg['owner']}/{cfg['repo']}/contents/{file_path}"

        req = Request(

            url,

            data=json.dumps(body).encode("utf-8"),

            headers={

                "Authorization": f"Bearer {cfg['token']}",

                "Accept": "application/vnd.github+json",

                "Content-Type": "application/json",

                "X-GitHub-Api-Version": "2022-11-28",

                "User-Agent": "dr2-puglia-app",

            },

            method="PUT",

        )

        with urlopen(req, timeout=12) as resp:

            _ = resp.read()

        return True, "Modifica salvata in modo permanente su GitHub!"

    except HTTPError as err:

        detail = ""

        try:

            detail = err.read().decode("utf-8")

        except Exception:

            pass

        return (

            False,

            f"Errore GitHub ({err.code}): verifica che GITHUB_REPO sia 'dr2-girone-a' e che il token abbia permesso Contents: Read and write. {detail}",

        )

    except Exception as exc:

        return False, f"Errore durante il salvataggio su GitHub: {exc}"





def load_game_overrides() -> dict[str, dict]:

    cfg = _get_github_config()

    if cfg["token"]:

        try:

            data, _ = _github_get_json_file(cfg, OVERRIDES_PATH)

            LOCAL_OVERRIDES_FILE.write_text(

                json.dumps(data, indent=2, ensure_ascii=False),

                encoding="utf-8",

            )

            return data

        except Exception:

            pass



    if LOCAL_OVERRIDES_FILE.is_file():

        try:

            data = json.loads(LOCAL_OVERRIDES_FILE.read_text(encoding="utf-8"))

            return data if isinstance(data, dict) else {}

        except Exception:

            return {}

    return {}





def save_game_override_persistent(match_id: str, values: dict) -> tuple[bool, str, dict[str, dict]]:

    cfg = _get_github_config()

    overrides = load_game_overrides()

    overrides[str(match_id)] = values



    LOCAL_OVERRIDES_FILE.write_text(

        json.dumps(overrides, indent=2, ensure_ascii=False) + "\n",

        encoding="utf-8",

    )

    ok, msg = _github_put_json_file(cfg, OVERRIDES_PATH, overrides, f"Aggiorna partita {match_id}")

    return ok, msg, overrides





def load_match_details_store() -> dict[str, dict]:

    merged: dict[str, dict] = {k: json.loads(json.dumps(v)) for k, v in DEFAULT_ROUND3_DETAILS.items()}

    cfg = _get_github_config()

    remote_data: dict[str, dict] = {}



    if cfg["token"]:

        try:

            data, _ = _github_get_json_file(cfg, DETAILS_PATH)

            if isinstance(data, dict):

                remote_data = data

                LOCAL_DETAILS_FILE.write_text(

                    json.dumps(data, indent=2, ensure_ascii=False) + "\n",

                    encoding="utf-8",

                )

        except Exception:

            pass



    if not remote_data and LOCAL_DETAILS_FILE.is_file():

        try:

            data = json.loads(LOCAL_DETAILS_FILE.read_text(encoding="utf-8"))

            if isinstance(data, dict):

                remote_data = data

        except Exception:

            remote_data = {}



    for mid, mdata in remote_data.items():

        if isinstance(mdata, dict):

            merged[str(mid)] = mdata



    return merged





def save_match_detail_persistent(match_id: str, detail_payload: dict) -> tuple[bool, str, dict[str, dict]]:

    cfg = _get_github_config()

    store = st.session_state.get("match_details_store")

    if not isinstance(store, dict):

        store = load_match_details_store()

    store[str(match_id)] = detail_payload



    LOCAL_DETAILS_FILE.write_text(

        json.dumps(store, indent=2, ensure_ascii=False) + "\n",

        encoding="utf-8",

    )

    ok, msg = _github_put_json_file(cfg, DETAILS_PATH, store, f"Aggiorna dettagli partita {match_id}")

    return ok, msg, store





def apply_overrides_to_df(df: pd.DataFrame, overrides: dict[str, dict]) -> pd.DataFrame:

    out = df.copy()

    if not overrides:

        return out

    for idx, row in out.iterrows():

        gid = str(row["ID_Partita"])

        if gid in overrides:

            ov = overrides[gid]

            if "Data" in ov:

                out.loc[idx, "Data"] = str(ov["Data"])

            if "Stato" in ov:

                out.loc[idx, "Stato"] = str(ov["Stato"])

            if "Punti_Casa" in ov:

                out.loc[idx, "Punti_Casa"] = int(ov["Punti_Casa"])

            if "Punti_Trasferta" in ov:

                out.loc[idx, "Punti_Trasferta"] = int(ov["Punti_Trasferta"])

    return out





# ==========================================

# STILI GRAFICI

# ==========================================

GLOBAL_UI_CSS = """

<style>

.stApp {

    background-color: #070d16;

    color: #f1f5f9;

}

section[data-testid="stSidebar"] {

    background-color: #0b1320;

    border-right: 1px solid rgba(148, 163, 184, 0.14);

}

.topbar-card {

    background: linear-gradient(120deg, #0d2240 0%, #133b6e 55%, #194d8c 100%);

    border: 1px solid rgba(255, 255, 255, 0.14);

    border-radius: 14px;

    padding: 18px 22px;

    margin-bottom: 18px;

    box-shadow: 0 10px 26px rgba(0, 0, 0, 0.35);

}

.topbar-title {

    font-size: 24px;

    font-weight: 900;

    color: #ffffff;

    letter-spacing: -0.3px;

    margin: 0;

}

.topbar-sub {

    font-size: 13px;

    color: #bae6fd;

    margin-top: 4px;

    font-weight: 600;

}

</style>

"""



STANDINGS_CSS = """

<style>

.board-box {

    background: linear-gradient(180deg, #0b192c 0%, #0f2440 100%);

    padding: 16px;

    border-radius: 14px;

    border: 1px solid rgba(148, 163, 184, 0.2);

    margin-bottom: 18px;

    box-shadow: 0 8px 22px rgba(0, 0, 0, 0.28);

}

.board-head {

    display: grid;

    grid-template-columns: 44px 44px minmax(170px, 1.35fr) 36px 36px 36px 52px 52px 54px 54px 54px 60px 134px 48px;

    gap: 8px;

    padding: 0 10px 10px 10px;

    border-bottom: 1px solid rgba(255, 255, 255, 0.12);

    margin-bottom: 8px;

    color: #fbbf24;

    font-weight: 800;

    font-size: 12px;

    letter-spacing: 0.4px;

    text-align: center;

}

.board-head .left { text-align: left; }

.zone-tag {

    font-size: 10.5px;

    font-weight: 800;

    letter-spacing: 0.6px;

    text-transform: uppercase;

    margin: 10px 0 5px 4px;

    display: inline-block;

    padding: 2px 10px;

    border-radius: 6px;

}

.zone-promo { background: #15803d; color: #ffffff; }

.zone-po { background: #b45309; color: #ffffff; }

.zone-pout { background: #b91c1c; color: #ffffff; }



.board-row {

    display: grid;

    grid-template-columns: 44px 44px minmax(170px, 1.35fr) 36px 36px 36px 52px 52px 54px 54px 54px 60px 134px 48px;

    gap: 8px;

    align-items: center;

    background: rgba(15, 28, 48, 0.88);

    border: 1px solid rgba(255, 255, 255, 0.1);

    border-radius: 10px;

    padding: 8px 10px;

    margin-bottom: 6px;

    color: #ffffff;

    transition: transform 0.12s ease, border-color 0.12s ease, background 0.12s ease;

}

.board-row:hover {

    background: rgba(23, 43, 74, 0.96);

    border-color: rgba(251, 191, 36, 0.45);

    transform: translateY(-1px);

}

.board-row.row-promo { border-left: 5px solid #22c55e; }

.board-row.row-po { border-left: 5px solid #f59e0b; }

.board-row.row-pout { border-left: 5px solid #ef4444; }

.board-row.row-qual { border-left: 5px solid #22c55e; }

.board-row.row-out { border-left: 5px solid #ef4444; }



.b-pos {

    font-size: 17px;

    font-weight: 900;

    text-align: center;

    color: #fbbf24;

}

.b-logo {

    width: 36px;

    height: 36px;

    object-fit: contain;

    background: #ffffff;

    border-radius: 8px;

    padding: 2px;

    margin: 0 auto;

    display: block;

}

a.team-link {

    color: #ffffff !important;

    text-decoration: none !important;

    font-weight: 800;

    font-size: 13.5px;

    text-transform: uppercase;

}

a.team-link:hover {

    color: #fbbf24 !important;

    text-decoration: underline !important;

}

.b-sub {

    font-size: 11px;

    font-weight: 700;

    color: #93c5fd;

    margin-top: 2px;

}

.b-val {

    text-align: center;

    font-weight: 700;

    font-size: 13.5px;

    color: #e2e8f0;

}

.streak-track {

    display: inline-flex;

    align-items: center;

    gap: 4px;

    background: #090e17;

    border: 1px solid rgba(255, 255, 255, 0.12);

    border-radius: 8px;

    padding: 4px 10px 4px 6px;

    min-width: 118px;

    justify-content: flex-start;

}

.streak-item {

    position: relative;

    display: inline-flex;

    align-items: center;

    justify-content: center;

}

a.streak-link {

    text-decoration: none !important;

    display: inline-flex;

}

.streak-box {

    display: inline-flex;

    align-items: center;

    justify-content: center;

    width: 20px;

    height: 20px;

    border-radius: 4px;

    font-size: 11px;

    font-weight: 900;

    color: #ffffff;

    line-height: 1;

    cursor: pointer;

    transition: transform 0.12s ease, filter 0.12s ease;

}

.streak-item:hover .streak-box {

    transform: translateY(-2px);

    filter: brightness(1.15);

}

.streak-w {

    background: #16a34a;

    border: 1px solid #22c55e;

}

.streak-l {

    background: #dc2626;

    border: 1px solid #ef4444;

}

.streak-tooltip {

    visibility: hidden;

    opacity: 0;

    pointer-events: none;

    position: absolute;

    bottom: calc(100% + 8px);

    left: 50%;

    transform: translateX(-50%);

    z-index: 9999;

    min-width: 210px;

    max-width: 290px;

    background: #0f172a;

    border: 1px solid rgba(255, 255, 255, 0.2);

    border-radius: 9px;

    padding: 7px 10px;

    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.5);

    text-align: center;

    white-space: normal;

    transition: opacity 0.14s ease, visibility 0.14s ease;

}

.streak-tooltip::after {

    content: "";

    position: absolute;

    top: 100%;

    left: 50%;

    transform: translateX(-50%);

    border-width: 6px;

    border-style: solid;

    border-color: #0f172a transparent transparent transparent;

}

.streak-item:hover .streak-tooltip {

    visibility: visible;

    opacity: 1;

}

.tt-top {

    display: flex;

    align-items: center;

    justify-content: center;

    gap: 6px;

    font-size: 11px;

    font-weight: 700;

    color: #94a3b8;

    margin-bottom: 3px;

}

.tt-badge-w {

    background: rgba(22, 163, 74, 0.25);

    color: #4ade80;

    border-radius: 4px;

    padding: 1px 5px;

    font-size: 10px;

    font-weight: 900;

}

.tt-badge-l {

    background: rgba(220, 38, 38, 0.25);

    color: #f87171;

    border-radius: 4px;

    padding: 1px 5px;

    font-size: 10px;

    font-weight: 900;

}

.tt-match {

    font-size: 11.5px;

    font-weight: 800;

    color: #f8fafc;

    line-height: 1.3;

}

.tt-score {

    color: #fbbf24;

    font-weight: 900;

    margin: 0 4px;

}

.streak-empty {

    color: #64748b;

    font-size: 12px;

    font-weight: 700;

    padding: 0 4px;

}

.b-pts {

    text-align: center;

    font-weight: 900;

    font-size: 16px;

    color: #fbbf24;

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

    background: rgba(239, 68, 68, 0.22);

    border: 1px solid #ef4444;

    color: #fecaca;

    font-size: 10px;

    font-weight: 800;

    padding: 2px 7px;

    border-radius: 5px;

    margin-left: 6px;

}



.board-head-thirds, .board-row-thirds {

    grid-template-columns: 52px 52px 1fr 50px 50px 50px 66px 156px 62px !important;

}

.board-row.row-highlight-team {

    background: linear-gradient(90deg, rgba(29, 78, 216, 0.34) 0%, rgba(15, 28, 48, 0.94) 100%);

    border-color: rgba(96, 165, 250, 0.75);

    box-shadow: 0 0 0 1px rgba(96, 165, 250, 0.35);

}

</style>

"""



CALENDAR_CSS = """

<style>

.cal-filter-banner {

    background: linear-gradient(135deg, #0c192d 0%, #132746 100%);

    border: 1px solid rgba(148, 163, 184, 0.26);

    border-left: 4px solid #fbbf24;

    border-radius: 14px;

    padding: 13px 16px;

    margin-bottom: 12px;

    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.26);

    display: flex;

    align-items: center;

    justify-content: space-between;

    flex-wrap: wrap;

    gap: 10px;

}

.cal-filter-title {

    font-size: 13px;

    font-weight: 900;

    letter-spacing: 0.6px;

    text-transform: uppercase;

    color: #fbbf24;

}

.cal-filter-sub {

    font-size: 11.5px;

    font-weight: 600;

    color: #cbd5e1;

    margin-top: 2px;

}

.cal-filter-pills {

    display: flex;

    align-items: center;

    gap: 8px;

    flex-wrap: wrap;

}

.cal-pill {

    background: rgba(15, 23, 42, 0.85);

    border: 1px solid rgba(251, 191, 36, 0.35);

    color: #f8fafc;

    border-radius: 999px;

    padding: 4px 11px;

    font-size: 11px;

    font-weight: 800;

}

.cal-pill span {

    color: #fbbf24;

    font-weight: 900;

}

div[data-testid="stMultiSelect"] > label {

    font-size: 12px !important;

    font-weight: 800 !important;

    text-transform: uppercase !important;

    letter-spacing: 0.5px !important;

    color: #93c5fd !important;

    margin-bottom: 4px !important;

}

div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div {

    background-color: #0e1a2e !important;

    border: 1px solid rgba(148, 163, 184, 0.35) !important;

    border-radius: 11px !important;

    min-height: 44px !important;

    box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.3) !important;

}

div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div:focus-within {

    border-color: #fbbf24 !important;

    box-shadow: 0 0 0 1px #fbbf24 !important;

}

div[data-testid="stMultiSelect"] span[data-baseweb="tag"] {

    background: linear-gradient(90deg, #1d4ed8 0%, #1e40af 100%) !important;

    border: 1px solid rgba(147, 197, 253, 0.45) !important;

    border-radius: 7px !important;

    color: #ffffff !important;

    font-weight: 700 !important;

}

.cal-phase-hdr {

    background: linear-gradient(90deg, #10243e 0%, #193861 100%);

    border: 1px solid rgba(148, 163, 184, 0.25);

    border-left: 4px solid #fbbf24;

    border-radius: 10px;

    padding: 9px 14px;

    margin-top: 8px;

    margin-bottom: 12px;

    font-size: 12.5px;

    font-weight: 900;

    letter-spacing: 0.6px;

    color: #f8fafc;

    text-transform: uppercase;

}

.cal-board {

    background: #0d1624;

    border: 1px solid rgba(148, 163, 184, 0.22);

    border-radius: 12px;

    overflow: hidden;

    margin-bottom: 16px;

    box-shadow: 0 8px 22px rgba(0, 0, 0, 0.28);

}

.cal-board-head {

    display: grid;

    grid-template-columns: 128px 1fr 94px 1fr;

    gap: 8px;

    align-items: center;

    padding: 9px 12px;

    background: linear-gradient(90deg, #13243b 0%, #1a3150 100%);

    border-bottom: 1px solid rgba(148, 163, 184, 0.22);

    color: #cbd5e1;

    font-size: 10.5px;

    font-weight: 800;

    letter-spacing: 0.5px;

    text-transform: uppercase;

}

.cal-board-head .c-center { text-align: center; color: #fbbf24; }

.cal-board-head .c-right { text-align: right; }

.cal-board-head .c-left { text-align: left; }



a.cal-row-link {

    text-decoration: none !important;

    color: inherit !important;

    display: block;

}

.cal-row-card {

    display: grid;

    grid-template-columns: 128px 1fr 94px 1fr;

    gap: 8px;

    align-items: center;

    padding: 11px 12px;

    background: #0e1726;

    border-bottom: 1px solid rgba(148, 163, 184, 0.12);

    transition: background 0.14s ease, transform 0.12s ease;

    cursor: pointer;

}

.cal-row-card:nth-child(even) {

    background: #111c2e;

}

.cal-row-card:hover {

    background: #182942;

}

.cal-row-card:last-child {

    border-bottom: none;

}

.cal-round-col {

    line-height: 1.25;

}

.cal-round-league {

    font-size: 10px;

    font-weight: 700;

    color: #94a3b8;

}

.cal-round-num {

    font-size: 11px;

    font-weight: 900;

    color: #fbbf24;

}

.cal-round-date {

    font-size: 11px;

    font-weight: 800;

    color: #f8fafc;

    margin-top: 1px;

}

.cal-side-home {

    display: flex;

    align-items: center;

    justify-content: flex-end;

    gap: 7px;

    text-align: right;

    min-width: 0;

}

.cal-side-away {

    display: flex;

    align-items: center;

    justify-content: flex-start;

    gap: 7px;

    text-align: left;

    min-width: 0;

}

.cal-side-name {

    font-size: 12px;

    font-weight: 700;

    color: #cbd5e1;

    line-height: 1.18;

}

.cal-side-name.win {

    color: #ffffff;

    font-weight: 900;

}

.cal-side-logo {

    width: 30px;

    height: 30px;

    object-fit: contain;

    background: #ffffff;

    border-radius: 50%;

    padding: 2px;

    border: 1px solid rgba(148, 163, 184, 0.35);

    flex-shrink: 0;

}

.cal-score-box {

    text-align: center;

    line-height: 1.15;

}

.cal-score-line {

    font-size: 17px;

    font-weight: 900;

    letter-spacing: 0.4px;

    white-space: nowrap;

}

.cal-pts-win { color: #f8fafc; }

.cal-pts-lose { color: #94a3b8; }

.cal-pts-vs { color: #fbbf24; font-size: 14px; }

.cal-state-sub {

    font-size: 9px;

    font-weight: 800;

    letter-spacing: 0.6px;

    color: #94a3b8;

    margin-top: 2px;

    text-transform: uppercase;

}

.cal-state-sub.done { color: #4ade80; }

.cal-state-sub.todo { color: #7dd3fc; }



@media (max-width: 820px) {

    .cal-board-head { display: none; }

    .cal-row-card {

        grid-template-columns: 1fr auto 1fr;

        gap: 8px;

        padding: 12px;

    }

    .cal-round-col {

        grid-column: 1 / -1;

        display: flex;

        justify-content: space-between;

        align-items: center;

        padding-bottom: 6px;

        border-bottom: 1px solid rgba(148, 163, 184, 0.12);

    }

    .cal-side-name { font-size: 11.5px; }

    .cal-side-logo { width: 28px; height: 28px; }

    .cal-score-line { font-size: 16px; }

}

</style>

"""



TEAMS_GRID_CSS = """

<style>

.teams-row-4 {

    display: grid;

    grid-template-columns: repeat(4, minmax(0, 1fr));

    gap: 20px;

    margin-bottom: 24px;

}

.teams-row-3 {

    display: grid;

    grid-template-columns: repeat(3, minmax(0, 1fr));

    gap: 20px;

    max-width: 76%;

    margin: 0 auto 26px auto;

}

@media (max-width: 1100px) {

    .teams-row-4, .teams-row-3 {

        grid-template-columns: repeat(2, minmax(0, 1fr));

        max-width: 100%;

    }

}

@media (max-width: 580px) {

    .teams-row-4, .teams-row-3 {

        grid-template-columns: 1fr;

        max-width: 100%;

    }

}

a.team-tile-link {

    text-decoration: none !important;

    color: inherit !important;

    display: flex;

    flex-direction: column;

    align-items: center;

}

.team-square-card {

    width: 100%;

    aspect-ratio: 1 / 1;

    background: radial-gradient(circle at 50% 34%, rgba(37, 99, 235, 0.34) 0%, rgba(13, 29, 52, 0.96) 58%, #091323 100%);

    border: 1.5px solid rgba(148, 163, 184, 0.3);

    border-radius: 20px;

    padding: 14px;

    display: flex;

    flex-direction: column;

    align-items: center;

    justify-content: space-between;

    text-align: center;

    box-shadow: 0 12px 28px rgba(0, 0, 0, 0.42);

    transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease, background 0.18s ease;

    cursor: pointer;

    position: relative;

    overflow: hidden;

}

.team-square-card::before {

    content: "";

    position: absolute;

    top: 0;

    left: 0;

    right: 0;

    height: 4px;

    background: linear-gradient(90deg, #1d4ed8 0%, #fbbf24 50%, #1d4ed8 100%);

    opacity: 0.75;

}

a.team-tile-link:hover .team-square-card {

    transform: translateY(-6px);

    border-color: #fbbf24;

    background: radial-gradient(circle at 50% 34%, rgba(251, 191, 36, 0.25) 0%, rgba(18, 40, 71, 0.98) 60%, #0b172a 100%);

    box-shadow: 0 16px 34px rgba(251, 191, 36, 0.24);

}

.ts-watermark {

    position: absolute;

    top: 42%;

    left: 50%;

    transform: translate(-50%, -50%) scale(1.85);

    width: 75%;

    height: 75%;

    object-fit: contain;

    opacity: 0.06;

    pointer-events: none;

    filter: grayscale(30%);

    z-index: 0;

}

.ts-top-row {

    width: 100%;

    display: flex;

    align-items: center;

    justify-content: space-between;

    font-size: 11.5px;

    font-weight: 900;

    z-index: 2;

}

.ts-pos-pill {

    background: rgba(251, 191, 36, 0.2);

    color: #fbbf24;

    border: 1px solid rgba(251, 191, 36, 0.5);

    border-radius: 999px;

    padding: 3px 10px;

}

.ts-pts-pill {

    background: rgba(15, 23, 42, 0.88);

    color: #bae6fd;

    border: 1px solid rgba(148, 163, 184, 0.3);

    border-radius: 999px;

    padding: 3px 10px;

}

.ts-logo-stage {

    flex: 1;

    width: 100%;

    display: flex;

    align-items: center;

    justify-content: center;

    padding: 6px 0;

    z-index: 2;

}

.ts-logo-box {

    width: 118px;

    height: 118px;

    background: #ffffff;

    border-radius: 22px;

    padding: 9px;

    display: flex;

    align-items: center;

    justify-content: center;

    border: 2.5px solid rgba(255, 255, 255, 0.9);

    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.42), 0 0 0 5px rgba(255, 255, 255, 0.08);

    transition: transform 0.18s ease, box-shadow 0.18s ease;

}

a.team-tile-link:hover .ts-logo-box {

    transform: scale(1.06);

    box-shadow: 0 12px 28px rgba(0, 0, 0, 0.5), 0 0 0 5px rgba(251, 191, 36, 0.28);

}

.ts-logo-box img {

    width: 100%;

    height: 100%;

    object-fit: contain;

}

.ts-bottom-panel {

    width: 100%;

    background: rgba(8, 14, 24, 0.84);

    border: 1px solid rgba(148, 163, 184, 0.22);

    border-radius: 12px;

    padding: 8px 10px;

    z-index: 2;

    backdrop-filter: blur(4px);

}

.ts-metrics-row {

    display: flex;

    align-items: center;

    justify-content: space-between;

    font-size: 11.5px;

    font-weight: 800;

    color: #e2e8f0;

    margin-bottom: 6px;

}

.ts-rec-w { color: #4ade80; font-weight: 900; }

.ts-rec-l { color: #f87171; font-weight: 900; }

.ts-diff-pos { color: #4ade80; font-weight: 900; }

.ts-diff-neg { color: #f87171; font-weight: 900; }

.ts-diff-zero { color: #94a3b8; font-weight: 800; }

.ts-streak-pills {

    display: flex;

    align-items: center;

    justify-content: center;

    gap: 5px;

}

.ts-mini-w {

    display: inline-flex;

    align-items: center;

    justify-content: center;

    width: 20px;

    height: 20px;

    border-radius: 5px;

    font-size: 10.5px;

    font-weight: 900;

    background: #16a34a;

    color: #ffffff;

    border: 1px solid #22c55e;

}

.ts-mini-l {

    display: inline-flex;

    align-items: center;

    justify-content: center;

    width: 20px;

    height: 20px;

    border-radius: 5px;

    font-size: 10.5px;

    font-weight: 900;

    background: #dc2626;

    color: #ffffff;

    border: 1px solid #ef4444;

}

.ts-mini-none {

    font-size: 10.5px;

    color: #94a3b8;

    font-weight: 700;

}

.ts-caption-below {

    margin-top: 10px;

    font-size: 13px;

    font-weight: 900;

    color: #f8fafc;

    text-align: center;

    text-transform: uppercase;

    line-height: 1.25;

    letter-spacing: 0.2px;

    transition: color 0.15s ease;

}

a.team-tile-link:hover .ts-caption-below {

    color: #fbbf24;

}

</style>

"""



MATCH_DETAIL_CSS = """

<style>

.md-hero {

    background: linear-gradient(135deg, #09182b 0%, #102a4c 55%, #163b69 100%);

    border: 1px solid rgba(148, 163, 184, 0.24);

    border-radius: 14px;

    padding: 24px 20px;

    margin-bottom: 16px;

    box-shadow: 0 10px 26px rgba(0, 0, 0, 0.35);

}

.md-grid {

    display: grid;

    grid-template-columns: 1fr auto 1fr;

    gap: 16px;

    align-items: center;

    text-align: center;

}

.md-team-block {

    display: flex;

    flex-direction: column;

    align-items: center;

    gap: 10px;

}

.md-logo-box {

    width: 74px;

    height: 74px;

    background: #ffffff;

    border-radius: 16px;

    padding: 8px;

    display: flex;

    align-items: center;

    justify-content: center;

    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.35);

}

.md-logo-box img {

    max-width: 100%;

    max-height: 100%;

    object-fit: contain;

}

.md-team-name {

    font-size: 15px;

    font-weight: 800;

    color: #f8fafc;

    text-transform: uppercase;

}

.md-center {

    display: flex;

    flex-direction: column;

    align-items: center;

    gap: 4px;

}

.md-date {

    font-size: 12.5px;

    font-weight: 700;

    color: #bae6fd;

}

.md-score {

    font-size: 46px;

    font-weight: 900;

    color: #ffffff;

    letter-spacing: 2px;

    line-height: 1.1;

}

.md-status {

    font-size: 11.5px;

    font-weight: 800;

    letter-spacing: 1.2px;

    color: #fbbf24;

    text-transform: uppercase;

}

.md-sec-card {

    background: linear-gradient(180deg, #0d1828 0%, #0a121f 100%);

    border: 1px solid rgba(148, 163, 184, 0.2);

    border-radius: 14px;

    padding: 18px;

    margin-bottom: 16px;

    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.25);

}

.md-sec-title {

    font-size: 13px;

    font-weight: 900;

    letter-spacing: 0.8px;

    text-transform: uppercase;

    color: #fbbf24;

    margin-bottom: 14px;

    display: flex;

    align-items: center;

    justify-content: space-between;

}

.md-res-table {

    width: 100%;

    border-collapse: collapse;

    color: #f1f5f9;

    font-size: 13.5px;

}

.md-res-table th {

    text-align: center;

    color: #94a3b8;

    font-size: 11.5px;

    font-weight: 800;

    text-transform: uppercase;

    padding: 9px 10px;

    border-bottom: 1px solid rgba(148, 163, 184, 0.22);

    background: rgba(15, 23, 42, 0.65);

}

.md-res-table th.team-col, .md-res-table td.team-col {

    text-align: left;

    font-weight: 800;

}

.md-res-table td {

    text-align: center;

    padding: 10px;

    border-bottom: 1px solid rgba(148, 163, 184, 0.1);

}

.md-res-table td.tot-col {

    font-weight: 900;

    color: #fbbf24;

    font-size: 15px;

}



.lba-box-card {

    margin-bottom: 20px;

    border-radius: 14px;

    overflow: hidden;

    box-shadow: 0 10px 26px rgba(0, 0, 0, 0.35);

    border: 1px solid rgba(148, 163, 184, 0.28);

    background: #ffffff;

}

.lba-team-banner {

    display: flex;

    align-items: center;

    justify-content: space-between;

    gap: 14px;

    background: linear-gradient(90deg, #0f172a 0%, #1e293b 100%);

    color: #ffffff;

    padding: 14px 18px;

    border-bottom: 2px solid #f59e0b;

}

.lba-banner-left {

    display: flex;

    align-items: center;

    gap: 14px;

}

.lba-team-logo {

    width: 46px;

    height: 46px;

    object-fit: contain;

    background: #ffffff;

    border-radius: 10px;

    padding: 4px;

    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.25);

}

.lba-team-title {

    font-size: 18px;

    font-weight: 900;

    color: #ffffff;

    letter-spacing: -0.2px;

    text-transform: uppercase;

    line-height: 1.15;

}

.lba-team-coach {

    font-size: 12px;

    font-weight: 600;

    color: #cbd5e1;

    margin-top: 3px;

}

.lba-tag-pill {

    font-size: 10.5px;

    font-weight: 800;

    text-transform: uppercase;

    letter-spacing: 0.6px;

    padding: 4px 10px;

    border-radius: 999px;

    background: rgba(251, 191, 36, 0.16);

    color: #fbbf24;

    border: 1px solid rgba(251, 191, 36, 0.45);

    white-space: nowrap;

}

.lba-table-wrap {

    width: 100%;

    overflow-x: auto;

    background: #ffffff;

}

table.lba-box {

    width: 100%;

    border-collapse: collapse;

    font-size: 12px;

    color: #1e293b;

}

table.lba-box.full-stats {

    min-width: 900px;

}

table.lba-box.compact-stats {

    min-width: 580px;

}

table.lba-box th.grp-hdr {

    background: #1e293b;

    color: #f8fafc;

    font-weight: 800;

    font-size: 10px;

    letter-spacing: 0.6px;

    padding: 6px 6px;

    text-align: center;

    border-right: 1px solid #334155;

}

table.lba-box th.grp-empty {

    background: #1e293b;

    border-right: 1px solid #334155;

}

table.lba-box th.sub-hdr {

    background: #f8fafc;

    color: #334155;

    font-weight: 800;

    font-size: 10px;

    padding: 7px 6px;

    text-align: center;

    border-bottom: 2px solid #cbd5e1;

    border-right: 1px solid #e2e8f0;

}

table.lba-box th.sub-hdr.left-col {

    text-align: left;

    padding-left: 12px;

}

table.lba-box th.sub-hdr.pts-col {

    color: #d97706;

}

table.lba-box td {

    padding: 7px 6px;

    text-align: center;

    border-bottom: 1px solid #e2e8f0;

    border-right: 1px solid #f1f5f9;

    font-weight: 500;

}

table.lba-box td.player-name {

    text-align: left;

    padding-left: 12px;

    font-weight: 700;

    color: #0f172a;

    white-space: nowrap;

}

.num-badge {

    display: inline-block;

    min-width: 24px;

    padding: 1px 6px;

    border-radius: 5px;

    background: #f1f5f9;

    color: #0f172a;

    font-weight: 800;

    font-size: 11px;

    margin-right: 6px;

    border: 1px solid #cbd5e1;

}

table.lba-box td.pts-val {

    font-weight: 900;

    color: #d97706;

}

table.lba-box td.pct-val {

    font-weight: 800;

    color: #d97706;

}

table.lba-box td.sf-check {

    color: #15803d;

    font-weight: 900;

}

table.lba-box tr:nth-child(even) td {

    background: #fcfcfd;

}

table.lba-box tr.total-row td {

    background: #e2e8f0;

    font-weight: 900;

    color: #0f172a;

    border-top: 2px solid #94a3b8;

    font-size: 12.5px;

}

table.lba-box tr.total-row td.pts-val,

table.lba-box tr.total-row td.pct-val {

    color: #b45309;

}



.formation-3col {

    display: grid;

    grid-template-columns: minmax(215px, 1fr) minmax(420px, 600px) minmax(215px, 1fr);

    gap: 14px;

    align-items: center;

}

@media (max-width: 1100px) {

    .formation-3col {

        grid-template-columns: 1fr;

    }

}

.roster-side-card {

    background: #0d1624;

    border: 1px solid rgba(148, 163, 184, 0.22);

    border-radius: 12px;

    padding: 12px 14px;

    height: 100%;

}

.roster-side-head {

    display: flex;

    align-items: center;

    gap: 8px;

    padding-bottom: 8px;

    margin-bottom: 8px;

    border-bottom: 1px solid rgba(148, 163, 184, 0.18);

    font-size: 12px;

    font-weight: 900;

    color: #f8fafc;

    text-transform: uppercase;

}

.roster-side-head img {

    width: 24px;

    height: 24px;

    object-fit: contain;

    background: #ffffff;

    border-radius: 5px;

    padding: 2px;

}

.roster-group-lbl {

    font-size: 10px;

    font-weight: 800;

    letter-spacing: 0.6px;

    text-transform: uppercase;

    color: #fbbf24;

    margin-bottom: 6px;

}

.roster-player-line {

    display: flex;

    align-items: center;

    gap: 7px;

    padding: 4px 6px;

    border-radius: 6px;

    font-size: 12px;

    font-weight: 700;

    color: #f1f5f9;

    margin-bottom: 3px;

    background: rgba(15, 23, 42, 0.75);

}

.roster-player-line.starter {

    border-left: 3px solid #22c55e;

}

.roster-num-pill {

    min-width: 24px;

    text-align: center;

    font-size: 11px;

    font-weight: 900;

    color: #fbbf24;

    background: rgba(30, 41, 59, 0.95);

    border-radius: 4px;

    padding: 1px 4px;

}

.roster-divider {

    border: none;

    border-top: 1px dashed rgba(148, 163, 184, 0.35);

    margin: 8px 0;

}



.court-compact-wrap {

    display: flex;

    flex-direction: column;

    align-items: center;

    width: 100%;

}

.court-stage {

    position: relative;

    width: 100%;

    max-width: 600px;

    aspect-ratio: 28 / 15;

    min-height: 270px;

    border-radius: 14px;

    overflow: hidden;

    border: 1.5px solid rgba(148, 163, 184, 0.32);

    background: radial-gradient(circle at center, #1c2b45 0%, #101929 100%);

    box-shadow: 0 12px 26px rgba(0, 0, 0, 0.45), inset 0 0 28px rgba(0, 0, 0, 0.45);

}

.court-svg-bg {

    position: absolute;

    inset: 0;

    width: 100%;

    height: 100%;

    z-index: 1;

}

.court-players-layer {

    position: relative;

    z-index: 2;

    display: grid;

    grid-template-columns: 1fr 1fr;

    height: 100%;

    padding: 12px 10px;

    gap: 10px;

}

.half-court-col {

    display: flex;

    flex-direction: column;

    justify-content: space-between;

    align-items: center;

}

.half-row-top, .half-row-bot {

    display: flex;

    justify-content: center;

    gap: 12px;

    flex-wrap: wrap;

}

.half-row-mid {

    display: flex;

    justify-content: center;

}

.jersey-card {

    display: flex;

    flex-direction: column;

    align-items: center;

    gap: 2px;

    transition: transform 0.16s ease;

}

.jersey-card:hover {

    transform: translateY(-3px) scale(1.08);

}

.jersey-svg-wrap {

    width: 44px;

    height: 46px;

    display: flex;

    align-items: center;

    justify-content: center;

    filter: drop-shadow(0 5px 8px rgba(0, 0, 0, 0.52));

}

.jersey-name {

    background: rgba(9, 15, 27, 0.88);

    color: #f8fafc;

    border: 1px solid rgba(255, 255, 255, 0.18);

    border-radius: 6px;

    padding: 1px 7px;

    font-size: 10px;

    font-weight: 800;

    text-transform: uppercase;

    letter-spacing: 0.3px;

    max-width: 96px;

    white-space: nowrap;

    overflow: hidden;

    text-overflow: ellipsis;

    box-shadow: 0 3px 8px rgba(0, 0, 0, 0.35);

}



.hist-grid {

    display: grid;

    grid-template-columns: 1fr 1fr;

    gap: 16px;

}

@media (max-width: 850px) {

    .hist-grid {

        grid-template-columns: 1fr;

    }

}

.hist-col {

    background: #0d1624;

    border: 1px solid rgba(148, 163, 184, 0.2);

    border-radius: 12px;

    padding: 14px;

}

.hist-col-head {

    display: flex;

    align-items: center;

    gap: 10px;

    padding-bottom: 10px;

    margin-bottom: 10px;

    border-bottom: 1px solid rgba(148, 163, 184, 0.18);

    font-size: 13px;

    font-weight: 900;

    color: #ffffff;

    text-transform: uppercase;

}

.hist-col-head img {

    width: 28px;

    height: 28px;

    object-fit: contain;

    background: #ffffff;

    border-radius: 6px;

    padding: 2px;

}

.hist-item {

    display: grid;

    grid-template-columns: 62px 1fr auto;

    gap: 8px;

    align-items: center;

    padding: 8px 10px;

    border-radius: 8px;

    background: rgba(15, 23, 42, 0.85);

    border: 1px solid rgba(148, 163, 184, 0.12);

    margin-bottom: 7px;

    font-size: 12px;

}

.hist-badge-w {

    background: rgba(22, 163, 74, 0.22);

    color: #4ade80;

    border: 1px solid rgba(74, 222, 128, 0.45);

    border-radius: 5px;

    padding: 2px 6px;

    font-weight: 900;

    font-size: 10.5px;

    text-align: center;

}

.hist-badge-l {

    background: rgba(220, 38, 38, 0.22);

    color: #f87171;

    border: 1px solid rgba(248, 113, 113, 0.45);

    border-radius: 5px;

    padding: 2px 6px;

    font-weight: 900;

    font-size: 10.5px;

    text-align: center;

}

.hist-score {

    font-weight: 900;

    color: #fbbf24;

    white-space: nowrap;

}



.team-hero {

    background: linear-gradient(135deg, #09182b 0%, #10325c 100%);

    border: 1px solid rgba(148, 163, 184, 0.24);

    border-radius: 14px;

    padding: 20px;

    margin-bottom: 16px;

    display: flex;

    align-items: center;

    gap: 18px;

}

.team-hero-title {

    font-size: 23px;

    font-weight: 900;

    color: #ffffff;

    text-transform: uppercase;

}

.team-hero-sub {

    font-size: 13px;

    font-weight: 700;

    color: #bae6fd;

    margin-top: 2px;

}

.kpi-grid {

    display: grid;

    grid-template-columns: repeat(auto-fit, minmax(115px, 1fr));

    gap: 10px;

    margin-bottom: 16px;

}

.kpi-card {

    background: #0d1624;

    border: 1px solid rgba(148, 163, 184, 0.18);

    border-radius: 10px;

    padding: 12px;

    text-align: center;

}

.kpi-label {

    font-size: 11px;

    font-weight: 800;

    color: #94a3b8;

    text-transform: uppercase;

}

.kpi-val {

    font-size: 20px;

    font-weight: 900;

    color: #fbbf24;

    margin-top: 2px;

}

</style>

"""



TEAM_PAGE_CSS = """

<style>

.tp-stats-card {

    background: #ffffff;

    border-radius: 14px;

    overflow: hidden;

    border: 1px solid rgba(148, 163, 184, 0.28);

    box-shadow: 0 10px 26px rgba(0, 0, 0, 0.32);

    margin-bottom: 20px;

}

.tp-stats-head {

    background: linear-gradient(90deg, #0f172a 0%, #1e293b 100%);

    color: #ffffff;

    padding: 12px 16px;

    font-size: 13px;

    font-weight: 900;

    letter-spacing: 0.6px;

    text-transform: uppercase;

    border-bottom: 2px solid #f59e0b;

    display: flex;

    justify-content: space-between;

    align-items: center;

}

.tp-table-wrap {

    width: 100%;

    overflow-x: auto;

    background: #ffffff;

}

table.tp-stats-table {

    width: 100%;

    border-collapse: collapse;

    font-size: 12px;

    color: #1e293b;

    min-width: 780px;

}

table.tp-stats-table th {

    background: #f8fafc;

    color: #334155;

    font-weight: 800;

    font-size: 10.5px;

    text-transform: uppercase;

    padding: 8px 7px;

    border-bottom: 2px solid #cbd5e1;

    border-right: 1px solid #e2e8f0;

    text-align: center;

    white-space: nowrap;

}

table.tp-stats-table th.left-col {

    text-align: left;

    padding-left: 12px;

}

table.tp-stats-table th.hi-col {

    color: #d97706;

}

table.tp-stats-table td {

    padding: 7px 7px;

    text-align: center;

    border-bottom: 1px solid #e2e8f0;

    border-right: 1px solid #f1f5f9;

    font-weight: 600;

}

table.tp-stats-table td.num-col {

    font-weight: 900;

    color: #0f172a;

    background: #f8fafc;

}

table.tp-stats-table td.name-col {

    text-align: left;

    padding-left: 12px;

    font-weight: 800;

    color: #0f172a;

    white-space: nowrap;

}

table.tp-stats-table td.pts-col {

    font-weight: 900;

    color: #d97706;

}

table.tp-stats-table tr:nth-child(even) td {

    background: #fcfcfd;

}

table.tp-stats-table tr:nth-child(even) td.num-col {

    background: #f1f5f9;

}

a.tp-player-link {

    color: #0f172a !important;

    text-decoration: none !important;

    font-weight: 800;

    border-bottom: 1.5px dashed rgba(217, 119, 6, 0.55);

    transition: color 0.14s ease, border-color 0.14s ease;

}

a.tp-player-link:hover {

    color: #d97706 !important;

    border-bottom-color: #d97706;

}

.pm-hero-card {

    background: linear-gradient(135deg, #09182b 0%, #132d52 100%);

    border: 1px solid rgba(251, 191, 36, 0.35);

    border-radius: 14px;

    padding: 14px 18px;

    margin-bottom: 14px;

    display: flex;

    align-items: center;

    justify-content: space-between;

    gap: 12px;

}

.pm-name-title {

    font-size: 20px;

    font-weight: 900;

    color: #ffffff;

    line-height: 1.2;

}

.pm-jersey-tag {

    color: #fbbf24;

    font-weight: 900;

    margin-right: 6px;

}

.pm-team-sub {

    display: flex;

    align-items: center;

    gap: 8px;

    margin-top: 6px;

    font-size: 11.5px;

    font-weight: 800;

    color: #93c5fd;

    text-transform: uppercase;

}

.pm-team-sub img {

    width: 24px;

    height: 24px;

    object-fit: contain;

    background: #ffffff;

    border-radius: 6px;

    padding: 2px;

}

.pm-kpi-grid {

    display: grid;

    grid-template-columns: repeat(4, minmax(0, 1fr));

    gap: 10px;

    margin-bottom: 12px;

}

@media (max-width: 680px) {

    .pm-kpi-grid {

        grid-template-columns: repeat(2, minmax(0, 1fr));

    }

}

.pm-kpi-box {

    background: #0d1624;

    border: 1px solid rgba(148, 163, 184, 0.22);

    border-radius: 10px;

    padding: 10px 12px;

}

.pm-kpi-lbl {

    font-size: 10.5px;

    font-weight: 800;

    color: #94a3b8;

    text-transform: uppercase;

}

.pm-kpi-val {

    font-size: 21px;

    font-weight: 900;

    color: #f8fafc;

    margin-top: 2px;

}

.pm-kpi-val.gold {

    color: #fbbf24;

}

.pm-extra-bar {

    background: rgba(15, 23, 42, 0.85);

    border: 1px solid rgba(148, 163, 184, 0.18);

    border-radius: 9px;

    padding: 8px 12px;

    font-size: 11.5px;

    font-weight: 700;

    color: #cbd5e1;

    margin-bottom: 14px;

}

.pm-hist-section-title {

    font-size: 12px;

    font-weight: 900;

    letter-spacing: 0.6px;

    text-transform: uppercase;

    color: #fbbf24;

    margin: 6px 0 10px 0;

}

.pm-game-card {

    background: #0e1726;

    border: 1px solid rgba(148, 163, 184, 0.22);

    border-radius: 12px;

    overflow: hidden;

    margin-bottom: 10px;

    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.28);

}

.pm-game-row {

    display: grid;

    grid-template-columns: 112px 1fr 86px 1fr;

    gap: 8px;

    align-items: center;

    padding: 10px 12px;

    background: linear-gradient(90deg, #101b2e 0%, #142238 100%);

}

.pm-game-footer {

    background: #09101c;

    border-top: 1px solid rgba(148, 163, 184, 0.14);

    padding: 7px 12px;

    display: flex;

    align-items: center;

    justify-content: space-between;

    flex-wrap: wrap;

    gap: 6px;

    font-size: 11.5px;

    color: #cbd5e1;

}

.pm-stat-pills {

    display: flex;

    align-items: center;

    gap: 6px;

    flex-wrap: wrap;

}

.pm-stat-chip {

    background: rgba(30, 41, 59, 0.9);

    border: 1px solid rgba(148, 163, 184, 0.25);

    border-radius: 6px;

    padding: 2px 7px;

    font-size: 11px;

    font-weight: 800;

    color: #e2e8f0;

}

.pm-stat-chip.pts {

    background: rgba(251, 191, 36, 0.16);

    border-color: rgba(251, 191, 36, 0.48);

    color: #fbbf24;

    font-weight: 900;

}

</style>

"""





@st.cache_data(show_spinner=False)

def build_games_df(version: str = DATA_VERSION) -> pd.DataFrame:

    _ = version

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





def load_full_games_df() -> pd.DataFrame:

    base_df = build_games_df(DATA_VERSION).copy()

    overrides = load_game_overrides()

    st.session_state["game_overrides"] = overrides

    return apply_overrides_to_df(base_df, overrides)





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

            mapping[f"raw_src::{squadra}"] = src

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

            mapping[f"hero::{squadra}"] = (

                f'<div class="md-logo-box"><img src="{src}" alt="{squadra}" /></div>'

                if src

                else '<div class="md-logo-box"><span style="font-size:32px;">🏀</span></div>'

            )

            mapping[f"lba::{squadra}"] = (

                f'<img class="lba-team-logo" src="{src}" alt="{squadra}" />'

                if src

                else '<div class="lba-team-logo" style="display:flex;align-items:center;justify-content:center;font-size:22px;">🏀</div>'

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

        return '<div class="streak-track"><span class="streak-empty">—</span></div>'

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

    group_names = [r["squadra"] for r in group_rows]

    h2h_pts = _h2h_points_for_group(group_names, played_games)

    return sorted(

        group_rows,

        key=lambda r: (-h2h_pts.get(r["squadra"], 0), -r["diff"], r["squadra"]),

    )





def _compute_quarter_differentials_by_team(girone: str, games_df: pd.DataFrame) -> dict[str, dict]:

    teams = [t["squadra"] for t in GIRONI_TEAMS.get(girone, [])]

    q_stats = {

        sq: {

            "games_with_q": 0,

            "q_pf": [0, 0, 0, 0],

            "q_ps": [0, 0, 0, 0],

            "q_diff_avg": [0.0, 0.0, 0.0, 0.0],

        }

        for sq in teams

    }

    played = games_df[

        (games_df["Girone"] == girone)

        & (games_df["Stato"].astype(str).str.strip().str.lower() == "giocata")

    ]

    for g in played.itertuples(index=False):

        gid = str(g.ID_Partita)

        home = str(g.Casa)

        away = str(g.Trasferta)

        det = _get_match_detail(gid)

        qh = det.get("quarters_home", [0, 0, 0, 0])

        qa = det.get("quarters_away", [0, 0, 0, 0])

        if sum(qh) == 0 and sum(qa) == 0:

            continue

        if home in q_stats:

            q_stats[home]["games_with_q"] += 1

            for i in range(4):

                q_stats[home]["q_pf"][i] += int(qh[i])

                q_stats[home]["q_ps"][i] += int(qa[i])

        if away in q_stats:

            q_stats[away]["games_with_q"] += 1

            for i in range(4):

                q_stats[away]["q_pf"][i] += int(qa[i])

                q_stats[away]["q_ps"][i] += int(qh[i])



    for sq, d in q_stats.items():

        n = d["games_with_q"]

        if n > 0:

            d["q_diff_avg"] = [round((d["q_pf"][i] - d["q_ps"][i]) / n, 1) for i in range(4)]

    return q_stats





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

            "pf_g": 0.0,

            "ps_g": 0.0,

            "home_w": 0,

            "home_l": 0,

            "away_w": 0,

            "away_l": 0,

            "vs50_w": 0,

            "vs50_l": 0,

            "streak_events": [],

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

            stats[home]["home_w"] += 1

            stats[away]["l"] += 1

            stats[away]["away_l"] += 1

            stats[home]["pts"] += 2

            stats[home]["streak_events"].append({"res": "W", "game_id": gid, "tooltip_data": tip_data})

            stats[away]["streak_events"].append({"res": "L", "game_id": gid, "tooltip_data": tip_data})

        elif p_away > p_home:

            stats[away]["w"] += 1

            stats[away]["away_w"] += 1

            stats[home]["l"] += 1

            stats[home]["home_l"] += 1

            stats[away]["pts"] += 2

            stats[away]["streak_events"].append({"res": "W", "game_id": gid, "tooltip_data": tip_data})

            stats[home]["streak_events"].append({"res": "L", "game_id": gid, "tooltip_data": tip_data})



    above_50_teams = {

        sq for sq, r in stats.items() if r["p"] > 0 and (r["w"] / r["p"]) >= 0.5

    }



    for g in played_tuples:

        home = str(g.Casa)

        away = str(g.Trasferta)

        p_home = int(g.Punti_Casa)

        p_away = int(g.Punti_Trasferta)

        if home not in stats or away not in stats:

            continue

        if away in above_50_teams:

            if p_home > p_away:

                stats[home]["vs50_w"] += 1

            elif p_away > p_home:

                stats[home]["vs50_l"] += 1

        if home in above_50_teams:

            if p_away > p_home:

                stats[away]["vs50_w"] += 1

            elif p_home > p_away:

                stats[away]["vs50_l"] += 1



    for r in stats.values():

        r["diff"] = r["pf"] - r["ps"]

        r["pf_g"] = round(r["pf"] / r["p"], 1) if r["p"] > 0 else 0.0

        r["ps_g"] = round(r["ps"] / r["p"], 1) if r["p"] > 0 else 0.0



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





def render_standings(

    girone: str,

    rows: list[dict],

    thirds_board: list[dict],

    logo_html_map: dict[str, str],

    games_df: pd.DataFrame | None = None,

) -> None:

    st.markdown(STANDINGS_CSS, unsafe_allow_html=True)

    playout_start = max(len(rows) - 3, 5)

    best_third = thirds_board[0] if thirds_board else None



    st.subheader(f"Classifica — {girone}")

    st.caption("Clicca sul nome di una squadra per aprire la scheda squadra oppure passa sul quadratino W/L per i dettagli gara.")



    html = [

        '<div class="board-box" style="overflow-x:auto;">',

        '<div class="board-head" style="min-width:960px;">'

        '<div>POS</div><div>LOGO</div><div class="left">SQUADRA</div>'

        '<div>P</div><div>W</div><div>L</div>'

        '<div>PF/G</div><div>PS/G</div><div>CASA</div><div>TRASF</div><div>vs ≥50%</div>'

        '<div>DIFF</div><div>STREAK</div><div>PTS</div>'

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



        if str(r["squadra"]).strip().upper() == HIGHLIGHT_TEAM.upper():

            row_cls = f"{row_cls} row-highlight-team".strip()



        diff_val = r["diff"]

        diff_str = f"+{diff_val}" if diff_val > 0 else str(diff_val)

        streak_html = _render_streak_html(r.get("streak_events", []))

        team_encoded = quote(str(r["squadra"]), safe="")

        logo_tag = logo_html_map.get(f"board::{r['squadra']}", '<div class="b-pos">🏀</div>')



        casa_rec = f"{r.get('home_w', 0)}-{r.get('home_l', 0)}"

        trasf_rec = f"{r.get('away_w', 0)}-{r.get('away_l', 0)}"

        vs50_rec = f"{r.get('vs50_w', 0)}-{r.get('vs50_l', 0)}"



        html.append(

            f'<div class="board-row {row_cls}" style="min-width:960px;">'

            f'<div class="b-pos">{pos}</div>'

            f'<div><a href="?team={team_encoded}" target="_self">{logo_tag}</a></div>'

            f'<div><a class="team-link" href="?team={team_encoded}" target="_self">{r["squadra"]}</a></div>'

            f'<div class="b-val">{r["p"]}</div>'

            f'<div class="b-val">{r["w"]}</div>'

            f'<div class="b-val">{r["l"]}</div>'

            f'<div class="b-val" style="color:#4ade80;">{r.get("pf_g", 0.0):.1f}</div>'

            f'<div class="b-val" style="color:#fca5a5;">{r.get("ps_g", 0.0):.1f}</div>'

            f'<div class="b-val">{casa_rec}</div>'

            f'<div class="b-val">{trasf_rec}</div>'

            f'<div class="b-val" style="color:#93c5fd;">{vs50_rec}</div>'

            f'<div class="b-val">{diff_str}</div>'

            f'<div style="text-align:center;">{streak_html}</div>'

            f'<div class="b-pts">{r["pts"]}</div>'

            f'</div>'

        )



    html.append("</div>")

    st.markdown("".join(html), unsafe_allow_html=True)



    # Pannello espandibile: Livello del Girone (Attacco vs Difesa, Fattore Campo, Differenziale Quarti)

    with st.expander(f"📊 Livello del Girone & Analisi Tecnica — {girone}", expanded=False):

        if not rows or sum(r["p"] for r in rows) == 0:

            st.info("Dati insufficienti per elaborare l'analisi tecnica del girone.")

        else:

            df_lvl = pd.DataFrame(rows)

            tot_games = int(df_lvl["p"].sum() // 2)

            tot_home_w = int(df_lvl["home_w"].sum())

            tot_away_w = int(df_lvl["away_w"].sum())

            home_win_pct = round((tot_home_w / tot_games) * 100, 1) if tot_games > 0 else 0.0

            away_win_pct = round(100.0 - home_win_pct, 1) if tot_games > 0 else 0.0

            active_df = df_lvl[df_lvl["p"] > 0].copy()

            avg_league_pts = round(active_df["pf_g"].mean(), 1) if not active_df.empty else 0.0



            m1, m2, m3, m4 = st.columns(4)

            m1.metric("Media Punti / Squadra", f"{avg_league_pts:.1f} PT/G")

            m2.metric("Impatto Fattore Campo (Casa)", f"{home_win_pct}%", f"{tot_home_w}W su {tot_games} gare")

            m3.metric("Colpi Esterni (Trasferta)", f"{away_win_pct}%", f"{tot_away_w}W su {tot_games} gare")

            best_off = active_df.sort_values(by="pf_g", ascending=False).iloc[0]

            m4.metric("Miglior Attacco", f"{best_off['pf_g']:.1f} PF/G", str(best_off["squadra"]))



            st.markdown("#### ⚔️ Grafico Attacco vs Difesa (PF/G vs PS/G)")

            st.caption("In basso a destra: squadre con attacco prolifico e difesa solida.")

            chart_df = active_df[["squadra", "pf_g", "ps_g"]].rename(

                columns={"squadra": "Squadra", "pf_g": "Attacco (PF/G)", "ps_g": "Difesa (PS/G)"}

            )

            st.scatter_chart(

                chart_df,

                x="Attacco (PF/G)",

                y="Difesa (PS/G)",

                color="Squadra",

                use_container_width=True,

            )



            if games_df is not None:

                st.markdown("#### ⏱️ Differenziale Medio per Quarto (da tabellini con parziali)")

                q_map = _compute_quarter_differentials_by_team(girone, games_df)

                q_rows = []

                for r in rows:

                    sq = r["squadra"]

                    qd = q_map.get(sq, {})

                    n_q = qd.get("games_with_q", 0)

                    avgs = qd.get("q_diff_avg", [0.0, 0.0, 0.0, 0.0])

                    q_rows.append(

                        {

                            "Squadra": sq,

                            "Gare con Parziali": n_q,

                            "Q1 Diff/G": f"{avgs[0]:+.1f}" if n_q else "—",

                            "Q2 Diff/G": f"{avgs[1]:+.1f}" if n_q else "—",

                            "Q3 Diff/G": f"{avgs[2]:+.1f}" if n_q else "—",

                            "Q4 Diff/G": f"{avgs[3]:+.1f}" if n_q else "—",

                        }

                    )

                st.dataframe(pd.DataFrame(q_rows), use_container_width=True, hide_index=True)



    if thirds_board:

        st.subheader("Mini-Classifica Terze Classificate (Migliore Terza ai Play-off)")

        t_html = [

            '<div class="board-box">',

            '<div class="board-head board-head-thirds">'

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

                f'<div class="board-row board-row-thirds {r_cls}">'

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





def render_teams_grid(girone: str, games_df: pd.DataFrame, logo_html_map: dict[str, str]) -> None:

    st.markdown(TEAMS_GRID_CSS, unsafe_allow_html=True)

    st.subheader(f"Squadre — {girone}")

    st.caption("Clicca su uno dei riquadri squadra per aprire la scheda completa con statistiche, calendario e tabellini.")



    board = compute_standings(girone, games_df)

    pos_map = {r["squadra"]: idx for idx, r in enumerate(board, start=1)}

    stats_map = {r["squadra"]: r for r in board}



    teams_list = sorted(GIRONI_TEAMS.get(girone, []), key=lambda x: x["squadra"])

    row_slices = [

        ("teams-row-4", teams_list[0:4]),

        ("teams-row-4", teams_list[4:8]),

        ("teams-row-3", teams_list[8:11]),

    ]



    for row_cls, chunk in row_slices:

        if not chunk:

            continue

        cards_html = [f'<div class="{row_cls}">']

        for item in chunk:

            sq = item["squadra"]

            sq_enc = quote(sq, safe="")

            st_row = stats_map.get(sq, {"pts": 0, "p": 0, "w": 0, "l": 0, "diff": 0, "streak_events": []})

            pos_val = pos_map.get(sq, "-")

            pts_val = int(st_row.get("pts", 0))

            p_val = int(st_row.get("p", 0))

            w_val = int(st_row.get("w", 0))

            l_val = int(st_row.get("l", 0))

            diff_val = int(st_row.get("diff", 0))



            if diff_val > 0:

                diff_html = f'<span class="ts-diff-pos">+{diff_val}</span>'

            elif diff_val < 0:

                diff_html = f'<span class="ts-diff-neg">{diff_val}</span>'

            else:

                diff_html = '<span class="ts-diff-zero">0</span>'



            logo_src = logo_html_map.get(f"raw_src::{sq}", "")

            watermark_html = f'<img class="ts-watermark" src="{logo_src}" alt="" />' if logo_src else ""

            logo_inner = (

                f'<img src="{logo_src}" alt="{sq}" loading="lazy" />'

                if logo_src

                else '<span style="font-size:48px;">🏀</span>'

            )



            events = st_row.get("streak_events", [])[-5:]

            if events:

                pills = "".join(

                    f'<span class="{"ts-mini-w" if e["res"] == "W" else "ts-mini-l"}">{e["res"]}</span>'

                    for e in events

                )

            else:

                pills = '<span class="ts-mini-none">Nessuna gara giocata</span>'



            sq_pal = _get_team_palette(sq)

            sq_card_style = (

                f'style="background:radial-gradient(circle at 50% 34%, {_rgba(sq_pal["rich_main"], 0.38)} 0%, rgba(13, 29, 52, 0.96) 58%, #091323 100%);'

                f'border-color:{_rgba(sq_pal["visible_main"], 0.45)};"'

            )

            cards_html.append(

                f'<a class="team-tile-link" href="?team={sq_enc}" target="_self">'

                f'<div class="team-square-card" {sq_card_style}>'

                f'{watermark_html}'

                f'<div class="ts-top-row">'

                f'<span class="ts-pos-pill">#{pos_val} CLASSIFICA</span>'

                f'<span class="ts-pts-pill">{pts_val} PT</span>'

                f'</div>'

                f'<div class="ts-logo-stage">'

                f'<div class="ts-logo-box">{logo_inner}</div>'

                f'</div>'

                f'<div class="ts-bottom-panel">'

                f'<div class="ts-metrics-row">'

                f'<span>{p_val}G • <span class="ts-rec-w">{w_val}V</span> - <span class="ts-rec-l">{l_val}P</span></span>'

                f'<span>DIFF {diff_html}</span>'

                f'</div>'

                f'<div class="ts-streak-pills">{pills}</div>'

                f'</div>'

                f'</div>'

                f'<div class="ts-caption-below">{sq}</div>'

                f'</a>'

            )

        cards_html.append("</div>")

        st.markdown("".join(cards_html), unsafe_allow_html=True)





def build_round_html(

    round_num: int,

    round_games: pd.DataFrame,

    logo_html_map: dict[str, str],

    is_ritorno: bool = False,

    girone_label: str = "DR2 Puglia",

) -> str:

    display_num = round_num - 11 if is_ritorno and round_num > 11 else round_num

    phase_label = "RITORNO" if is_ritorno else "ANDATA"



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

            '<div class="cal-side-away"><span class="cal-side-name">corrispondente ai filtri</span></div>'

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





def _extract_surname(full_name: str) -> str:

    cleaned = re.sub(r"\s*\(N\.E\.\)\s*$", "", str(full_name or ""), flags=re.IGNORECASE).strip()

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





def _players_to_editor_df(player_list: list[dict], full_stats: bool = True, min_rows: int = 8) -> pd.DataFrame:

    rows = _normalize_player_rows(player_list)

    while len(rows) < min_rows:

        rows.append(_p_row(""))

    df = pd.DataFrame(rows)

    if full_stats:

        front_cols = ["NUM", "Giocatore"]

        rest_cols = [c for c in df.columns if c not in front_cols and c not in ("SC", "ASS")]

        return df[front_cols + rest_cols]

    compact_cols = ["NUM", "Giocatore", "PUN", "MIN", "SF", "F_C", "2PT_R", "3PT_R", "TL_R", "TL_T"]

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



        raw_num = getattr(r, "NUM", None)

        if raw_num is None or (isinstance(raw_num, float) and pd.isna(raw_num)):

            raw_num = prev.get("NUM", None)



        out.append(

            _p_row(

                giocatore=name,

                numero=raw_num,

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

    allenatore_txt = coach_name.strip() if coach_name.strip() else "—"

    badge_txt = "STATISTICHE DETTAGLIATE" if full_stats else "TABELLINO ESSENZIALE"

    table_cls = "lba-box full-stats" if full_stats else "lba-box compact-stats"



    if full_stats:

        header_html = (

            "<tr>"

            '<th class="grp-empty" colspan="4"></th>'

            '<th class="grp-hdr" colspan="2">FALLI</th>'

            '<th class="grp-hdr" colspan="3">TIRI DA 2</th>'

            '<th class="grp-hdr" colspan="3">TIRI DA 3</th>'

            '<th class="grp-hdr" colspan="3">TIRI LIBERI</th>'

            '<th class="grp-hdr" colspan="3">RIMBALZI</th>'

            '<th class="grp-hdr" colspan="2">STOPPATE</th>'

            '<th class="grp-hdr" colspan="2">PALLE</th>'

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

            '<th class="grp-hdr" colspan="1">TIRI DA 3</th>'

            '<th class="grp-hdr" colspan="3">TIRI LIBERI</th>'

            "</tr>"

            "<tr>"

            '<th class="sub-hdr left-col">GIOCATORE</th>'

            '<th class="sub-hdr pts-col">PUN</th>'

            '<th class="sub-hdr">MIN</th>'

            '<th class="sub-hdr">SF</th>'

            '<th class="sub-hdr">C</th>'

            '<th class="sub-hdr">R</th>'

            '<th class="sub-hdr">R</th>'

            '<th class="sub-hdr">R</th>'

            '<th class="sub-hdr">T</th>'

            '<th class="sub-hdr pts-col">%</th>'

            "</tr>"

        )



    b_pal = _get_team_palette(team_name)

    banner_style = (

        f'style="background:linear-gradient(90deg, {_rgba(b_pal["rich_main"], 0.65)} 0%, #0f172a 78%);'

        f'border-bottom:2.5px solid {b_pal["visible_accent"]};"'

    )

    html = [

        '<div class="lba-box-card">',

        f'<div class="lba-team-banner" {banner_style}>',

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

    tot_2r = tot_2t = 0

    tot_3r = tot_3t = 0

    tot_tlr = tot_tlt = 0

    tot_rimo = tot_rimd = tot_rimt = 0

    tot_std = tot_sts = 0

    tot_palp = tot_palr = 0

    tot_val = 0



    for p in norm_players:

        pun = int(p["PUN"])

        min_str = str(p["MIN"]) if str(p["MIN"]).strip() else "0"

        sf_mark = "✓" if p["SF"] else ""

        fc = int(p["F_C"])

        fs = int(p["F_S"])

        r2 = int(p["2PT_R"])

        t2 = int(p["2PT_T"])

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

        val_l = int(p["VAL"])

        oer_v = f"{float(p['OER']):.1f}" if float(p["OER"]) != 0 else "0"

        num_disp_val = _format_jersey_display(p.get("NUM"), empty_placeholder="")

        num_badge = f'<span class="num-badge">{num_disp_val}</span>' if num_disp_val != "" else ""



        tot_pun += pun

        tot_min_num += _parse_minutes_to_int(min_str)

        tot_fc += fc

        tot_fs += fs

        tot_2r += r2

        tot_2t += t2

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

                f"<td>{r3}</td>"

                f"<td>{rtl}</td>"

                f"<td>{ttl}</td>"

                f'<td class="pct-val">{_fmt_pct(rtl, ttl)}</td>'

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

            f'<td>{tot_2r}</td><td>{tot_2t}</td><td class="pct-val">{_fmt_pct(tot_2r, tot_2t)}</td>'

            f'<td>{tot_3r}</td><td>{tot_3t}</td><td class="pct-val">{_fmt_pct(tot_3r, tot_3t)}</td>'

            f'<td>{tot_tlr}</td><td>{tot_tlt}</td><td class="pct-val">{_fmt_pct(tot_tlr, tot_tlt)}</td>'

            f"<td>{tot_rimo}</td><td>{tot_rimd}</td><td>{tot_rimt}</td>"

            f"<td>{tot_std}</td><td>{tot_sts}</td>"

            f"<td>{tot_palp}</td><td>{tot_palr}</td>"

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

            f"<td>{tot_3r}</td>"

            f"<td>{tot_tlr}</td>"

            f"<td>{tot_tlt}</td>"

            f'<td class="pct-val">{_fmt_pct(tot_tlr, tot_tlt)}</td>'

            "</tr>"

        )



    html.append("</tbody></table></div></div>")

    st.markdown("".join(html), unsafe_allow_html=True)





def _jersey_svg(number: str, fill_hex: str, trim_hex: str, text_hex: str) -> str:

    return (

        f'<svg viewBox="0 0 64 68" width="44" height="46" xmlns="http://www.w3.org/2000/svg">'

        f'<path d="M18 6 L24 6 Q32 14 40 6 L46 6 L54 19 L49 23 L48 62 L16 62 L15 23 L10 19 Z" '

        f'fill="{fill_hex}" stroke="{trim_hex}" stroke-width="2.6" stroke-linejoin="round"/>'

        f'<path d="M24 6 Q32 15 40 6" fill="none" stroke="{trim_hex}" stroke-width="2.4"/>'

        f'<text x="32" y="42" text-anchor="middle" fill="{text_hex}" '

        f'font-family="sans-serif" font-weight="900" font-size="18">{number}</text>'

        f'</svg>'

    )





def _render_roster_sidebar_html(team_name: str, logo_html_map: dict[str, str], starters: list[dict], bench: list[dict]) -> str:

    logo_src = logo_html_map.get(f"raw_src::{team_name}", "")

    logo_tag = f'<img src="{logo_src}" alt="" />' if logo_src else "🏀"

    pal = _get_team_palette(team_name)

    card_border = _rgba(pal["visible_main"], 0.45)



    def _rows_html(plist: list[dict], is_starter: bool) -> str:

        if not plist:

            return '<div style="font-size:11px;color:#64748b;padding:4px 0;">—</div>'

        out = []

        cls = "roster-player-line starter" if is_starter else "roster-player-line"

        line_style = f'style="border-left:3px solid {pal["visible_main"]};"' if is_starter else ""

        for p in plist:

            num_disp = _format_jersey_display(p.get("NUM"), empty_placeholder="—")

            surname = _extract_surname(p.get("Giocatore", ""))

            out.append(

                f'<div class="{cls}" {line_style}>'

                f'<span class="roster-num-pill">{num_disp}</span>'

                f'<span>{surname}</span>'

                f"</div>"

            )

        return "".join(out)



    return (

        f'<div class="roster-side-card" style="border-color:{card_border};">'

        f'<div class="roster-side-head">{logo_tag}<span>{team_name}</span></div>'

        f'<div style="font-size:10px;font-weight:700;color:#94a3b8;margin:-4px 0 8px 0;">Colori sociali: <span style="color:#f8fafc;">{pal["label"]}</span></div>'

        f'<div class="roster-group-lbl">Quintetto Titolare</div>'

        f'{_rows_html(starters, True)}'

        f'<hr class="roster-divider" />'

        f'<div class="roster-group-lbl" style="color:#94a3b8;">Panchina / Altri</div>'

        f'{_rows_html(bench, False)}'

        f"</div>"

    )





def render_court_formations(

    home_team: str,

    away_team: str,

    home_players: list[dict],

    away_players: list[dict],

    logo_html_map: dict[str, str],

) -> None:

    st.markdown('<div class="md-sec-card">', unsafe_allow_html=True)

    st.markdown(

        '<div class="md-sec-title"><span>🏀 Formazioni in Campo (Quintetti Titolari & Panchine)</span></div>',

        unsafe_allow_html=True,

    )



    h_norm = _normalize_player_rows(home_players)

    a_norm = _normalize_player_rows(away_players)



    h_starters = [p for p in h_norm if p["SF"]][:5]

    a_starters = [p for p in a_norm if p["SF"]][:5]



    h_starter_ids = {id(p) for p in h_starters}

    a_starter_ids = {id(p) for p in a_starters}

    h_bench = [p for p in h_norm if id(p) not in h_starter_ids]

    a_bench = [p for p in a_norm if id(p) not in a_starter_ids]



    if not h_starters and not a_starters:

        st.info("Nessun giocatore selezionato in quintetto (SF) nei tabellini di questa partita.")

        st.markdown("</div>", unsafe_allow_html=True)

        return



    home_pal = _get_team_palette(home_team)

    away_pal = _get_team_palette(away_team)



    def _half_court_jerseys(starters: list[dict], pal: dict[str, str]) -> str:

        fill = pal["primary"]

        trim = pal["secondary"]

        txt = pal["text"]

        if not starters:

            return '<div style="color:#94a3b8;font-size:11px;margin:auto;">Quintetto non indicato</div>'

        cards = []

        for idx, p in enumerate(starters, start=1):

            num_val = _extract_jersey_number(p.get("Giocatore", ""), p.get("NUM", None))

            num = str(num_val) if 0 <= num_val <= 99 else str(idx)

            surname = _extract_surname(p.get("Giocatore", ""))

            svg = _jersey_svg(num, fill, trim, txt)

            cards.append(

                f'<div class="jersey-card">'

                f'<div class="jersey-svg-wrap">{svg}</div>'

                f'<div class="jersey-name">{surname}</div>'

                f"</div>"

            )

        top_row = "".join(cards[0:2])

        mid_row = "".join(cards[2:3])

        bot_row = "".join(cards[3:5])

        return (

            f'<div class="half-court-col">'

            f'<div class="half-row-top">{top_row}</div>'

            f'<div class="half-row-mid">{mid_row}</div>'

            f'<div class="half-row-bot">{bot_row}</div>'

            f"</div>"

        )



    court_svg = """

    <svg class="court-svg-bg" viewBox="0 0 840 450" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">

      <rect x="0" y="0" width="840" height="450" fill="none"/>

      <rect x="18" y="16" width="804" height="418" rx="6" fill="none" stroke="rgba(226,232,240,0.42)" stroke-width="2.5"/>

      <line x1="420" y1="16" x2="420" y2="434" stroke="rgba(226,232,240,0.42)" stroke-width="2.5"/>

      <circle cx="420" cy="225" r="54" fill="rgba(59,130,246,0.08)" stroke="rgba(226,232,240,0.42)" stroke-width="2.5"/>

      <circle cx="420" cy="225" r="14" fill="none" stroke="rgba(226,232,240,0.35)" stroke-width="2"/>

      <!-- Area sinistra -->

      <rect x="18" y="152" width="142" height="146" fill="rgba(59,130,246,0.12)" stroke="rgba(226,232,240,0.42)" stroke-width="2.2"/>

      <circle cx="160" cy="225" r="54" fill="none" stroke="rgba(226,232,240,0.38)" stroke-width="2"/>

      <path d="M 18 46 L 86 46 A 192 192 0 0 1 86 404 L 18 404" fill="none" stroke="rgba(226,232,240,0.42)" stroke-width="2.2"/>

      <!-- Area destra -->

      <rect x="680" y="152" width="142" height="146" fill="rgba(245,158,11,0.12)" stroke="rgba(226,232,240,0.42)" stroke-width="2.2"/>

      <circle cx="680" cy="225" r="54" fill="none" stroke="rgba(226,232,240,0.38)" stroke-width="2"/>

      <path d="M 822 46 L 754 46 A 192 192 0 0 0 754 404 L 822 404" fill="none" stroke="rgba(226,232,240,0.42)" stroke-width="2.2"/>

    </svg>

    """



    left_roster = _render_roster_sidebar_html(home_team, logo_html_map, h_starters, h_bench)

    right_roster = _render_roster_sidebar_html(away_team, logo_html_map, a_starters, a_bench)

    left_court = _half_court_jerseys(h_starters, home_pal)

    right_court = _half_court_jerseys(a_starters, away_pal)



    st.markdown(

        f'<div class="formation-3col">'

        f"{left_roster}"

        f'<div class="court-compact-wrap">'

        f'<div class="court-stage">{court_svg}<div class="court-players-layer">{left_court}{right_court}</div></div>'

        f"</div>"

        f"{right_roster}"

        f"</div>"

        f"</div>",

        unsafe_allow_html=True,

    )





def render_team_recent_games(

    home_team: str,

    away_team: str,

    games_df: pd.DataFrame,

    logo_html_map: dict[str, str],

) -> None:

    def _team_col_html(team_name: str) -> str:

        logo_src = logo_html_map.get(f"raw_src::{team_name}", "")

        logo_tag = f'<img src="{logo_src}" alt="" />' if logo_src else "🏀"

        sub_df = games_df[

            ((games_df["Casa"] == team_name) | (games_df["Trasferta"] == team_name))

            & (games_df["Stato"].astype(str).str.strip().str.lower() == "giocata")

        ].sort_values(by=["Giornata", "ID_Partita"], ascending=False).head(5)



        items_html = []

        for g in sub_df.itertuples(index=False):

            is_home = str(g.Casa) == team_name

            opp = str(g.Trasferta) if is_home else str(g.Casa)

            my_pts = int(g.Punti_Casa) if is_home else int(g.Punti_Trasferta)

            opp_pts = int(g.Punti_Trasferta) if is_home else int(g.Punti_Casa)

            won = my_pts > opp_pts

            badge = '<span class="hist-badge-w">V</span>' if won else '<span class="hist-badge-l">P</span>'

            venue = "vs" if is_home else "@"

            gid_enc = quote(str(g.ID_Partita), safe="")

            items_html.append(

                f'<a href="?match={gid_enc}" target="_self" style="text-decoration:none;color:inherit;">'

                f'<div class="hist-item">'

                f"{badge}"

                f'<div style="color:#e2e8f0;font-weight:700;">G{int(g.Giornata)} • {venue} {opp}</div>'

                f'<div class="hist-score">{my_pts}-{opp_pts}</div>'

                f"</div></a>"

            )

        if not items_html:

            items_html.append('<div style="color:#94a3b8;font-size:12px;">Nessuna partita disputata.</div>')

        return f'<div class="hist-col"><div class="hist-col-head">{logo_tag}<span>{team_name}</span></div>{"".join(items_html)}</div>'



    st.markdown(

        '<div class="md-sec-card">'

        '<div class="md-sec-title"><span>📈 Ultime Gare Disputate dalle Due Squadre</span></div>'

        f'<div class="hist-grid">{_team_col_html(home_team)}{_team_col_html(away_team)}</div>'

        "</div>",

        unsafe_allow_html=True,

    )





def render_match_detail_page(

    match_id: str,

    games_df: pd.DataFrame,

    logo_html_map: dict[str, str],

) -> None:

    st.markdown(MATCH_DETAIL_CSS, unsafe_allow_html=True)

    sub = games_df[games_df["ID_Partita"] == match_id]

    if sub.empty:

        st.error("Partita non trovata.")

        if st.button("← Torna alla vista principale"):

            st.query_params.clear()

            st.rerun()

        return



    row = sub.iloc[0]

    girone = str(row["Girone"])

    giornata = int(row["Giornata"])

    data_ora = str(row["Data"])

    casa = str(row["Casa"])

    trasferta = str(row["Trasferta"])

    p_casa = int(row["Punti_Casa"])

    p_trasf = int(row["Punti_Trasferta"])

    stato = str(row["Stato"])

    is_played = stato.strip().lower() == "giocata"



    if st.button("← Torna a Classifica e Calendario", key="btn_back_from_match"):

        st.query_params.clear()

        st.rerun()



    st.caption(f"{girone} • Giornata {giornata} • ID {match_id}")



    h_logo = logo_html_map.get(f"hero::{casa}", '<div class="md-logo-box">🏀</div>')

    a_logo = logo_html_map.get(f"hero::{trasferta}", '<div class="md-logo-box">🏀</div>')

    score_txt = f"{p_casa} - {p_trasf}" if is_played else "VS"

    status_txt = "FINALE" if is_played else "DA GIOCARE"



    h_pal = _get_team_palette(casa)

    a_pal = _get_team_palette(trasferta)

    hero_style = (

        f'style="background:linear-gradient(115deg, {_rgba(h_pal["rich_main"], 0.42)} 0%, #0d1d34 50%, {_rgba(a_pal["rich_main"], 0.42)} 100%);'

        f'border:1.5px solid rgba(148,163,184,0.3);"'

    )



    st.markdown(

        f'<div class="md-hero" {hero_style}>'

        '<div class="md-grid">'

        f'<div class="md-team-block">{h_logo}<div class="md-team-name">{casa}</div>'

        f'<div style="font-size:10.5px;font-weight:800;color:{h_pal["visible_accent"]};">{h_pal["label"]}</div></div>'

        f'<div class="md-center"><div class="md-date">{data_ora}</div><div class="md-score">{score_txt}</div><div class="md-status">{status_txt}</div></div>'

        f'<div class="md-team-block">{a_logo}<div class="md-team-name">{trasferta}</div>'

        f'<div style="font-size:10.5px;font-weight:800;color:{a_pal["visible_accent"]};">{a_pal["label"]}</div></div>'

        "</div></div>",

        unsafe_allow_html=True,

    )



    det = _get_match_detail(match_id)

    qh = det["quarters_home"]

    qa = det["quarters_away"]

    oth = det["ot_home"]

    ota = det["ot_away"]



    # Parziali per quarto

    st.markdown(

        '<div class="md-sec-card">'

        '<div class="md-sec-title"><span>⏱️ Risultato e Parziali per Quarto</span></div>'

        '<table class="md-res-table">'

        '<thead><tr><th class="team-col">Squadra</th><th>Q1</th><th>Q2</th><th>Q3</th><th>Q4</th><th>TS</th><th>TOT</th></tr></thead>'

        "<tbody>"

        f'<tr><td class="team-col">{casa}</td><td>{qh[0]}</td><td>{qh[1]}</td><td>{qh[2]}</td><td>{qh[3]}</td><td>{oth}</td><td class="tot-col">{p_casa if is_played else "-"}</td></tr>'

        f'<tr><td class="team-col">{trasferta}</td><td>{qa[0]}</td><td>{qa[1]}</td><td>{qa[2]}</td><td>{qa[3]}</td><td>{ota}</td><td class="tot-col">{p_trasf if is_played else "-"}</td></tr>'

        "</tbody></table></div>",

        unsafe_allow_html=True,

    )



    # Tabellini in stile LBA

    home_full = (casa == HIGHLIGHT_TEAM)

    away_full = (trasferta == HIGHLIGHT_TEAM)



    if det["home_players"] or det["away_players"]:

        if det["home_players"]:

            render_lba_boxscore(casa, det["coach_home"], det["home_players"], logo_html_map, full_stats=home_full)

        if det["away_players"]:

            render_lba_boxscore(trasferta, det["coach_away"], det["away_players"], logo_html_map, full_stats=away_full)

    else:

        st.info("Nessun tabellino individuale inserito per questa gara. Puoi aggiungerlo qui sotto nel pannello Staff.")



    # Formazioni in campo

    render_court_formations(casa, trasferta, det["home_players"], det["away_players"], logo_html_map)



    # Ultime gare disputate dalle due squadre

    render_team_recent_games(casa, trasferta, games_df, logo_html_map)



    # Sezione Staff per modificare risultato, parziali e tabellini

    with st.expander("🔐 Area Staff — Inserisci / Modifica Risultato, Parziali e Tabellino", expanded=False):

        if not st.session_state.get("staff_unlocked", False):

            pwd = st.text_input("Password Staff", type="password", key=f"pwd_md_{match_id}")

            if st.button("Sblocca Area Staff", key=f"unlock_md_{match_id}"):

                if pwd == STAFF_PASSWORD:

                    st.session_state["staff_unlocked"] = True

                    st.rerun()

                else:

                    st.error("Password non corretta.")

        else:

            st.success("Modalità Staff attiva: ogni salvataggio aggiorna permanentemente i dati su GitHub.")

            c1, c2, c3 = st.columns([2, 1, 1])

            new_data = c1.text_input("Data e Ora", value=data_ora, key=f"md_date_{match_id}")

            new_stato = c2.selectbox(

                "Stato",

                ["Giocata", "Da giocare"],

                index=0 if is_played else 1,

                key=f"md_state_{match_id}",

            )

            new_coach_h = c3.text_input("Coach Casa", value=det["coach_home"], key=f"md_ch_{match_id}")



            c4, c5, c6 = st.columns([1, 1, 2])

            new_pc = c4.number_input(f"Punti {casa}", min_value=0, max_value=250, value=p_casa, key=f"md_pc_{match_id}")

            new_pt = c5.number_input(f"Punti {trasferta}", min_value=0, max_value=250, value=p_trasf, key=f"md_pt_{match_id}")

            new_coach_a = c6.text_input("Coach Trasferta", value=det["coach_away"], key=f"md_ca_{match_id}")



            st.markdown("##### Parziali per Quarto")

            q_cols_h = st.columns(5)

            qh1 = q_cols_h[0].number_input(f"{casa[:12]} Q1", 0, 100, int(qh[0]), key=f"qh1_{match_id}")

            qh2 = q_cols_h[1].number_input(f"{casa[:12]} Q2", 0, 100, int(qh[1]), key=f"qh2_{match_id}")

            qh3 = q_cols_h[2].number_input(f"{casa[:12]} Q3", 0, 100, int(qh[2]), key=f"qh3_{match_id}")

            qh4 = q_cols_h[3].number_input(f"{casa[:12]} Q4", 0, 100, int(qh[3]), key=f"qh4_{match_id}")

            oth_in = q_cols_h[4].number_input(f"{casa[:12]} TS", 0, 100, int(oth), key=f"oth_{match_id}")



            q_cols_a = st.columns(5)

            qa1 = q_cols_a[0].number_input(f"{trasferta[:12]} Q1", 0, 100, int(qa[0]), key=f"qa1_{match_id}")

            qa2 = q_cols_a[1].number_input(f"{trasferta[:12]} Q2", 0, 100, int(qa[1]), key=f"qa2_{match_id}")

            qa3 = q_cols_a[2].number_input(f"{trasferta[:12]} Q3", 0, 100, int(qa[2]), key=f"qa3_{match_id}")

            qa4 = q_cols_a[3].number_input(f"{trasferta[:12]} Q4", 0, 100, int(qa[3]), key=f"qa4_{match_id}")

            ota_in = q_cols_a[4].number_input(f"{trasferta[:12]} TS", 0, 100, int(ota), key=f"ota_{match_id}")



            st.markdown(f"##### Tabellino Giocatori — {casa}")

            df_h_edit = st.data_editor(

                _players_to_editor_df(det["home_players"], full_stats=home_full),

                num_rows="dynamic",

                use_container_width=True,

                key=f"ed_h_{match_id}",

            )



            st.markdown(f"##### Tabellino Giocatori — {trasferta}")

            df_a_edit = st.data_editor(

                _players_to_editor_df(det["away_players"], full_stats=away_full),

                num_rows="dynamic",

                use_container_width=True,

                key=f"ed_a_{match_id}",

            )



            if st.button("💾 Salva Partita e Tabellini su GitHub", type="primary", key=f"save_md_{match_id}"):

                ov_payload = {

                    "Data": new_data.strip(),

                    "Stato": new_stato,

                    "Punti_Casa": int(new_pc),

                    "Punti_Trasferta": int(new_pt),

                }

                ok1, msg1, new_ov = save_game_override_persistent(match_id, ov_payload)

                st.session_state["game_overrides"] = new_ov



                det_payload = {

                    "coach_home": new_coach_h.strip(),

                    "coach_away": new_coach_a.strip(),

                    "quarters_home": [int(qh1), int(qh2), int(qh3), int(qh4)],

                    "quarters_away": [int(qa1), int(qa2), int(qa3), int(qa4)],

                    "ot_home": int(oth_in),

                    "ot_away": int(ota_in),

                    "home_players": _editor_df_to_players(df_h_edit, det["home_players"]),

                    "away_players": _editor_df_to_players(df_a_edit, det["away_players"]),

                }

                ok2, msg2, new_store = save_match_detail_persistent(match_id, det_payload)

                st.session_state["match_details_store"] = new_store



                if ok1 and ok2:

                    st.success("Risultato e tabellini salvati correttamente!")

                else:

                    st.warning(f"{msg1} | {msg2}")

                st.rerun()





def _normalize_player_key(name: str) -> str:

    cleaned = re.sub(r"\s*\(N\.E\.\)\s*$", "", str(name or ""), flags=re.IGNORECASE).strip()

    cleaned = re.sub(r"^\s*#?\d+\s*[-–.]?\s*", "", cleaned).strip()

    return cleaned.upper()





def _is_dnp_player(name: str) -> bool:

    return bool(re.search(r"\(N\.E\.\)", str(name or ""), flags=re.IGNORECASE))





def _compute_team_player_season_stats(team_name: str, games_df: pd.DataFrame) -> tuple[list[dict], list[dict]]:

    """Aggrega le statistiche stagionali di ogni giocatore della squadra dalle partite giocate."""

    team_games = games_df[

        ((games_df["Casa"] == team_name) | (games_df["Trasferta"] == team_name))

        & (games_df["Stato"].astype(str).str.strip().str.lower() == "giocata")

    ].sort_values(by=["Giornata", "ID_Partita"])



    agg: dict[str, dict] = {}

    game_logs: list[dict] = []



    for g in team_games.itertuples(index=False):

        gid = str(g.ID_Partita)

        is_home = str(g.Casa) == team_name

        opp = str(g.Trasferta) if is_home else str(g.Casa)

        my_pts = int(g.Punti_Casa) if is_home else int(g.Punti_Trasferta)

        opp_pts = int(g.Punti_Trasferta) if is_home else int(g.Punti_Casa)



        det = _get_match_detail(gid)

        plist = det.get("home_players", []) if is_home else det.get("away_players", [])



        for p in plist:

            raw_name = str(p.get("Giocatore", "")).strip()

            if not raw_name:

                continue

            pkey = _normalize_player_key(raw_name)

            display_name = re.sub(r"\s*\(N\.E\.\)\s*$", "", raw_name, flags=re.IGNORECASE).strip()

            dnp = _is_dnp_player(raw_name)



            if pkey not in agg:

                agg[pkey] = {

                    "key": pkey,

                    "name": display_name,

                    "num": 999,

                    "pg": 0,

                    "sf": 0,

                    "pts": 0,

                    "min_sec": 0,

                    "fc": 0,

                    "fs": 0,

                    "t2_r": 0,

                    "t2_t": 0,

                    "t3_r": 0,

                    "t3_t": 0,

                    "tl_r": 0,

                    "tl_t": 0,

                    "rim_o": 0,

                    "rim_d": 0,

                    "st_d": 0,

                    "st_s": 0,

                    "pal_p": 0,

                    "pal_r": 0,

                    "val": 0,

                    "logs": [],

                }



            rec = agg[pkey]

            if len(display_name) > len(rec["name"]) and not dnp:

                rec["name"] = display_name



            num_candidate = _extract_jersey_number(raw_name, p.get("NUM", None))

            if 0 <= num_candidate <= 99:

                rec["num"] = num_candidate



            if not dnp:

                rec["pg"] += 1

            if bool(p.get("SF", False)):

                rec["sf"] += 1



            pts = int(p.get("PUN", 0) or 0)

            fc = int(p.get("F_C", 0) or 0)

            fs = int(p.get("F_S", 0) or 0)

            r2 = int(p.get("2PT_R", 0) or 0)

            t2 = int(p.get("2PT_T", 0) or 0)

            r3 = int(p.get("3PT_R", 0) or 0)

            t3 = int(p.get("3PT_T", 0) or 0)

            rtl = int(p.get("TL_R", 0) or 0)

            ttl = int(p.get("TL_T", 0) or 0)

            ro = int(p.get("RIM_O", 0) or 0)

            rd = int(p.get("RIM_D", 0) or 0)

            sd = int(p.get("ST_D", 0) or 0)

            ss = int(p.get("ST_S", 0) or 0)

            pp = int(p.get("PAL_P", 0) or 0)

            pr = int(p.get("PAL_R", 0) or 0)

            val = int(p.get("VAL", 0) or 0)

            min_str = str(p.get("MIN", "0") or "0").strip()



            m_sec = 0

            if ":" in min_str:

                try:

                    mm, ss_p = min_str.split(":", 1)

                    m_sec = int(float(mm)) * 60 + int(float(ss_p))

                except Exception:

                    m_sec = 0

            else:

                try:

                    m_sec = int(float(min_str)) * 60

                except Exception:

                    m_sec = 0



            rec["pts"] += pts

            rec["min_sec"] += m_sec

            rec["fc"] += fc

            rec["fs"] += fs

            rec["t2_r"] += r2

            rec["t2_t"] += t2

            rec["t3_r"] += r3

            rec["t3_t"] += t3

            rec["tl_r"] += rtl

            rec["tl_t"] += ttl

            rec["rim_o"] += ro

            rec["rim_d"] += rd

            rec["st_d"] += sd

            rec["st_s"] += ss

            rec["pal_p"] += pp

            rec["pal_r"] += pr

            rec["val"] += val



            rec["logs"].append(

                {

                    "game_id": gid,

                    "giornata": int(g.Giornata),

                    "data": str(g.Data),

                    "casa": str(g.Casa),

                    "trasferta": str(g.Trasferta),

                    "p_casa": int(g.Punti_Casa),

                    "p_trasf": int(g.Punti_Trasferta),

                    "is_home": is_home,

                    "opp": opp,

                    "won": my_pts > opp_pts,

                    "dnp": dnp,

                    "pts": pts,

                    "min": min_str,

                    "sf": bool(p.get("SF", False)),

                    "fc": fc,

                    "fs": fs,

                    "t2_r": r2,

                    "t2_t": t2,

                    "t3_r": r3,

                    "t3_t": t3,

                    "tl_r": rtl,

                    "tl_t": ttl,

                    "rim_o": ro,

                    "rim_d": rd,

                    "val": val,

                }

            )



    players_summary = sorted(

        agg.values(),

        key=lambda x: (-x["pts"], -(x["pts"] / x["pg"] if x["pg"] > 0 else 0), x["num"], x["name"]),

    )

    for item in players_summary:

        pg = item["pg"]

        item["ppg"] = round(item["pts"] / pg, 1) if pg > 0 else 0.0

        item["rpg"] = round((item["rim_o"] + item["rim_d"]) / pg, 1) if pg > 0 else 0.0

        item["val_pg"] = round(item["val"] / pg, 1) if pg > 0 else 0.0

        avg_sec = int(round(item["min_sec"] / pg)) if pg > 0 else 0

        item["mpg_str"] = f"{avg_sec // 60}:{avg_sec % 60:02d}" if avg_sec > 0 else "0:00"



    return players_summary, game_logs





def _fmt_stat_pair_pct(made: int, att: int) -> str:

    if att <= 0:

        return f"{made}/0 (-)"

    pct = (made / att) * 100.0

    return f"{made}/{att} ({pct:.1f}%)"





def _render_player_modal_content(

    team_name: str,

    player_rec: dict,

    logo_html_map: dict[str, str],

) -> None:

    """Renderizza il contenuto HTML della finestra modale giocatore (usata da @st.dialog o fallback)."""

    st.markdown(TEAM_PAGE_CSS, unsafe_allow_html=True)

    logo_src = logo_html_map.get(f"raw_src::{team_name}", "")

    logo_mini = f'<img src="{logo_src}" alt="" />' if logo_src else "🏀"

    num_tag = _format_jersey_display(player_rec.get("num"), empty_placeholder="—")



    p_name_esc = html_lib.escape(str(player_rec.get("name", "")))

    team_esc = html_lib.escape(str(team_name))



    st.markdown(

        f'<div class="pm-hero-card">'

        f'<div>'

        f'<div class="pm-name-title"><span class="pm-jersey-tag">{num_tag}</span>{p_name_esc}</div>'

        f'<div class="pm-team-sub">{logo_mini}<span>{team_esc} • Stagione 2026/27</span></div>'

        f'</div>'

        f'</div>',

        unsafe_allow_html=True,

    )



    pg = int(player_rec.get("pg", 0))

    pts = int(player_rec.get("pts", 0))

    ppg = float(player_rec.get("ppg", 0.0))

    sf_cnt = int(player_rec.get("sf", 0))

    tot_rim = int(player_rec.get("rim_o", 0)) + int(player_rec.get("rim_d", 0))

    rpg = float(player_rec.get("rpg", 0.0))

    fc_tot = int(player_rec.get("fc", 0))

    val_tot = int(player_rec.get("val", 0))

    mpg_str = str(player_rec.get("mpg_str", "0:00"))



    st.markdown(

        '<div class="pm-kpi-grid">'

        f'<div class="pm-kpi-box"><div class="pm-kpi-lbl">Partite (Quintetto)</div><div class="pm-kpi-val">{pg} ({sf_cnt})</div></div>'

        f'<div class="pm-kpi-box"><div class="pm-kpi-lbl">Punti Totali</div><div class="pm-kpi-val gold">{pts}</div></div>'

        f'<div class="pm-kpi-box"><div class="pm-kpi-lbl">Media Punti (PPG)</div><div class="pm-kpi-val gold">{ppg:.1f}</div></div>'

        f'<div class="pm-kpi-box"><div class="pm-kpi-lbl">Minuti / Gara</div><div class="pm-kpi-val">{mpg_str}</div></div>'

        f'<div class="pm-kpi-box"><div class="pm-kpi-lbl">Tiri da 2</div><div class="pm-kpi-val" style="font-size:15px;">{_fmt_stat_pair_pct(player_rec.get("t2_r", 0), player_rec.get("t2_t", 0))}</div></div>'

        f'<div class="pm-kpi-box"><div class="pm-kpi-lbl">Tiri da 3</div><div class="pm-kpi-val" style="font-size:15px;">{_fmt_stat_pair_pct(player_rec.get("t3_r", 0), player_rec.get("t3_t", 0))}</div></div>'

        f'<div class="pm-kpi-box"><div class="pm-kpi-lbl">Tiri Liberi</div><div class="pm-kpi-val" style="font-size:15px;">{_fmt_stat_pair_pct(player_rec.get("tl_r", 0), player_rec.get("tl_t", 0))}</div></div>'

        f'<div class="pm-kpi-box"><div class="pm-kpi-lbl">Rimbalzi (RPG)</div><div class="pm-kpi-val">{tot_rim} ({rpg:.1f})</div></div>'

        '</div>',

        unsafe_allow_html=True,

    )



    st.markdown(

        f'<div class="pm-extra-bar">'

        f'Falli Commessi: <strong style="color:#f8fafc;">{fc_tot}</strong> ({round(fc_tot / pg, 1) if pg else 0.0}/g) • '

        f'Falli Subiti: <strong style="color:#f8fafc;">{player_rec.get("fs", 0)}</strong> • '

        f'Palle Recuperate: <strong style="color:#4ade80;">{player_rec.get("pal_r", 0)}</strong> • '

        f'Palle Perse: <strong style="color:#f87171;">{player_rec.get("pal_p", 0)}</strong> • '

        f'Valutazione Tot: <strong style="color:#fbbf24;">{val_tot}</strong>'

        f'</div>',

        unsafe_allow_html=True,

    )



    st.markdown('<div class="pm-hist-section-title">📅 Storico Partite Giocate</div>', unsafe_allow_html=True)



    logs = sorted(player_rec.get("logs", []), key=lambda x: x["giornata"], reverse=True)

    if not logs:

        st.info("Nessun tabellino registrato per questo giocatore.")

        return



    cards_html = []

    for lg in logs:

        gid_enc = quote(str(lg["game_id"]), safe="")

        tokens = str(lg["data"]).strip().split()

        date_str = tokens[1] if len(tokens) >= 3 else (tokens[0] if len(tokens) >= 1 else "")

        casa_name = html_lib.escape(str(lg["casa"]))

        trasf_name = html_lib.escape(str(lg["trasferta"]))

        p_casa = int(lg["p_casa"])

        p_trasf = int(lg["p_trasf"])



        h_src = logo_html_map.get(f"raw_src::{lg['casa']}", "")

        a_src = logo_html_map.get(f"raw_src::{lg['trasferta']}", "")

        h_logo = f'<img class="cal-side-logo" src="{h_src}" alt="" />' if h_src else "🏀"

        a_logo = f'<img class="cal-side-logo" src="{a_src}" alt="" />' if a_src else "🏀"



        h_win = p_casa > p_trasf

        a_win = p_trasf > p_casa

        esito_lbl = "VITTORIA" if lg["won"] else "SCONFITTA"

        esito_col = "#4ade80" if lg["won"] else "#f87171"



        if lg.get("dnp"):

            chips_html = '<span class="pm-stat-chip">N.E. (Non entrato)</span>'

        else:

            chips = [f'<span class="pm-stat-chip pts">{lg["pts"]} PT</span>']

            if lg["min"] and lg["min"] != "0":

                chips.append(f'<span class="pm-stat-chip">{html_lib.escape(str(lg["min"]))} MIN</span>')

            if lg["sf"]:

                chips.append('<span class="pm-stat-chip" style="color:#4ade80;">Quintetto</span>')

            if lg["t2_t"] > 0 or lg["t2_r"] > 0:

                chips.append(f'<span class="pm-stat-chip">2P: {lg["t2_r"]}/{lg["t2_t"]}</span>')

            if lg["t3_t"] > 0 or lg["t3_r"] > 0:

                chips.append(f'<span class="pm-stat-chip">3P: {lg["t3_r"]}/{lg["t3_t"]}</span>')

            if lg["tl_t"] > 0 or lg["tl_r"] > 0:

                chips.append(f'<span class="pm-stat-chip">TL: {lg["tl_r"]}/{lg["tl_t"]}</span>')

            rim_g = lg["rim_o"] + lg["rim_d"]

            if rim_g > 0:

                chips.append(f'<span class="pm-stat-chip">RIM: {rim_g}</span>')

            if lg["fc"] > 0:

                chips.append(f'<span class="pm-stat-chip">Falli: {lg["fc"]}</span>')

            chips_html = "".join(chips)



        cards_html.append(

            f'<div class="pm-game-card">'

            f'<a class="cal-row-link" href="?match={gid_enc}" target="_self">'

            f'<div class="pm-game-row">'

            f'<div class="cal-round-col">'

            f'<div class="cal-round-num">{lg["giornata"]}ª Giornata</div>'

            f'<div class="cal-round-date">{html_lib.escape(date_str)}</div>'

            f'</div>'

            f'<div class="cal-side-home"><span class="cal-side-name {"win" if h_win else ""}">{casa_name}</span>{h_logo}</div>'

            f'<div class="cal-score-box">'

            f'<div class="cal-score-line"><span class="{"cal-pts-win" if h_win else "cal-pts-lose"}">{p_casa}</span>'

            f'<span style="color:#64748b;margin:0 3px;">-</span>'

            f'<span class="{"cal-pts-win" if a_win else "cal-pts-lose"}">{p_trasf}</span></div>'

            f'<div class="cal-state-sub" style="color:{esito_col};">{esito_lbl}</div>'

            f'</div>'

            f'<div class="cal-side-away">{a_logo}<span class="cal-side-name {"win" if a_win else ""}">{trasf_name}</span></div>'

            f'</div>'

            f'</a>'

            f'<div class="pm-game-footer">'

            f'<div class="pm-stat-pills">{chips_html}</div>'

            f'<a href="?match={gid_enc}" target="_self" style="color:#93c5fd;font-weight:800;font-size:11px;text-decoration:none;">Apri tabellino →</a>'

            f'</div>'

            f'</div>'

        )



    st.markdown("".join(cards_html), unsafe_allow_html=True)





def _open_player_profile_dialog(

    team_name: str,

    player_rec: dict,

    logo_html_map: dict[str, str],

) -> None:

    """Apre una finestra modale con statistiche totali/medie e storico partite del giocatore."""

    if hasattr(st, "dialog"):



        @st.dialog(f"Scheda Giocatore — {player_rec.get('name', '')}", width="large")

        def _player_modal() -> None:

            _render_player_modal_content(team_name, player_rec, logo_html_map)

            if st.button("Chiudi scheda giocatore", key=f"close_pm_{team_name}_{player_rec.get('key', '')}"):

                st.query_params["team"] = team_name

                if "player" in st.query_params:

                    del st.query_params["player"]

                st.rerun()



        _player_modal()

    else:

        st.markdown("---")

        _render_player_modal_content(team_name, player_rec, logo_html_map)

        if st.button("Chiudi scheda giocatore", key=f"close_pm_fb_{team_name}_{player_rec.get('key', '')}"):

            st.query_params["team"] = team_name

            if "player" in st.query_params:

                del st.query_params["player"]

            st.rerun()

        st.markdown("---")





def render_team_detail_page(

    team_name: str,

    games_df: pd.DataFrame,

    logo_html_map: dict[str, str],

) -> None:

    st.markdown(MATCH_DETAIL_CSS, unsafe_allow_html=True)

    st.markdown(CALENDAR_CSS, unsafe_allow_html=True)

    st.markdown(TEAM_PAGE_CSS, unsafe_allow_html=True)

    girone = _find_team_girone(team_name)

    if not girone:

        st.error("Squadra non trovata.")

        if st.button("← Torna alla vista principale"):

            st.query_params.clear()

            st.rerun()

        return



    if st.button("← Torna a Classifica e Calendario", key="btn_back_from_team"):

        st.query_params.clear()

        st.rerun()



    board = compute_standings(girone, games_df)

    pos_idx = next((i + 1 for i, r in enumerate(board) if r["squadra"] == team_name), "-")

    team_stats = next((r for r in board if r["squadra"] == team_name), None)



    hero_logo = logo_html_map.get(f"hero::{team_name}", '<div class="md-logo-box">🏀</div>')

    t_pal = _get_team_palette(team_name)

    team_hero_style = (

        f'style="background:linear-gradient(125deg, {_rgba(t_pal["rich_main"], 0.45)} 0%, #0d1d34 65%);'

        f'border-left:5px solid {t_pal["visible_main"]};"'

    )

    st.markdown(

        f'<div class="team-hero" {team_hero_style}>'

        f"{hero_logo}"

        f'<div><div class="team-hero-title">{team_name}</div>'

        f'<div class="team-hero-sub">{girone} • Posizione attuale: #{pos_idx} • Colori: <span style="color:{t_pal["visible_accent"]};">{t_pal["label"]}</span></div></div>'

        f"</div>",

        unsafe_allow_html=True,

    )



    if team_stats:

        diff_v = team_stats["diff"]

        diff_s = f"+{diff_v}" if diff_v > 0 else str(diff_v)

        st.markdown(

            '<div class="kpi-grid">'

            f'<div class="kpi-card"><div class="kpi-label">Punti Classifica</div><div class="kpi-val">{team_stats["pts"]}</div></div>'

            f'<div class="kpi-card"><div class="kpi-label">Giocate</div><div class="kpi-val">{team_stats["p"]}</div></div>'

            f'<div class="kpi-card"><div class="kpi-label">Vinte</div><div class="kpi-val">{team_stats["w"]}</div></div>'

            f'<div class="kpi-card"><div class="kpi-label">Perse</div><div class="kpi-val">{team_stats["l"]}</div></div>'

            f'<div class="kpi-card"><div class="kpi-label">Punti Fatti</div><div class="kpi-val">{team_stats["pf"]}</div></div>'

            f'<div class="kpi-card"><div class="kpi-label">Punti Subiti</div><div class="kpi-val">{team_stats["ps"]}</div></div>'

            f'<div class="kpi-card"><div class="kpi-label">Differenza</div><div class="kpi-val">{diff_s}</div></div>'

            "</div>",

            unsafe_allow_html=True,

        )



    # ==========================================

    # SEZIONE GIOCATORI & STATISTICHE STAGIONALI

    # ==========================================

    players_summary, _ = _compute_team_player_season_stats(team_name, games_df)

    team_enc = quote(team_name, safe="")



    selected_player_key = str(st.query_params.get("player", "") or "").strip()

    if selected_player_key:

        matched_player = next(

            (p for p in players_summary if p["key"] == _normalize_player_key(selected_player_key)),

            None,

        )

        if matched_player is not None:

            _open_player_profile_dialog(team_name, matched_player, logo_html_map)



    st.subheader(f"Roster e Statistiche Individuali — {team_name}")

    st.caption("Clicca sul nome di un giocatore per aprire la finestra con statistiche complete e tutte le partite disputate.")



    if not players_summary:

        st.info("Nessun tabellino individuale ancora registrato per questa squadra.")

    else:

        has_advanced = any(

            (p["t2_t"] > p["t2_r"]) or (p["t3_t"] > p["t3_r"]) or (p["rim_o"] + p["rim_d"] > 0) or (p["val"] != 0)

            for p in players_summary

        )



        if has_advanced:

            tbl_head = (

                "<tr>"

                "<th>#</th>"

                '<th class="left-col">GIOCATORE</th>'

                "<th>PG</th>"

                "<th>SF</th>"

                '<th class="hi-col">PTS</th>'

                '<th class="hi-col">PPG</th>'

                "<th>MIN/G</th>"

                "<th>2PT</th>"

                "<th>3PT</th>"

                "<th>TL</th>"

                "<th>RIM (RPG)</th>"

                "<th>FC</th>"

                "<th>VAL</th>"

                "</tr>"

            )

        else:

            tbl_head = (

                "<tr>"

                "<th>#</th>"

                '<th class="left-col">GIOCATORE</th>'

                "<th>PG</th>"

                "<th>SF</th>"

                '<th class="hi-col">PTS</th>'

                '<th class="hi-col">PPG</th>'

                "<th>2PT R</th>"

                "<th>3PT R</th>"

                "<th>TL</th>"

                "<th>FC</th>"

                "</tr>"

            )



        rows_html = []

        for p in players_summary:

            num_disp = _format_jersey_display(p.get("num"), empty_placeholder="—")

            p_enc = quote(p["key"], safe="")

            p_name_safe = html_lib.escape(str(p.get("name", "")))

            link_html = f'<a class="tp-player-link" href="?team={team_enc}&player={p_enc}" target="_self">{p_name_safe}</a>'



            if has_advanced:

                tot_r = p["rim_o"] + p["rim_d"]

                rows_html.append(

                    "<tr>"

                    f'<td class="num-col">{num_disp}</td>'

                    f'<td class="name-col">{link_html}</td>'

                    f'<td>{p["pg"]}</td>'

                    f'<td>{p["sf"]}</td>'

                    f'<td class="pts-col">{p["pts"]}</td>'

                    f'<td class="pts-col">{p["ppg"]:.1f}</td>'

                    f'<td>{p["mpg_str"]}</td>'

                    f'<td>{_fmt_stat_pair_pct(p["t2_r"], p["t2_t"])}</td>'

                    f'<td>{_fmt_stat_pair_pct(p["t3_r"], p["t3_t"])}</td>'

                    f'<td>{_fmt_stat_pair_pct(p["tl_r"], p["tl_t"])}</td>'

                    f'<td>{tot_r} ({p["rpg"]:.1f})</td>'

                    f'<td>{p["fc"]}</td>'

                    f'<td>{p["val"]}</td>'

                    "</tr>"

                )

            else:

                tl_disp = f"{p['tl_r']}/{p['tl_t']}" if p["tl_t"] > 0 else str(p["tl_r"])

                rows_html.append(

                    "<tr>"

                    f'<td class="num-col">{num_disp}</td>'

                    f'<td class="name-col">{link_html}</td>'

                    f'<td>{p["pg"]}</td>'

                    f'<td>{p["sf"]}</td>'

                    f'<td class="pts-col">{p["pts"]}</td>'

                    f'<td class="pts-col">{p["ppg"]:.1f}</td>'

                    f'<td>{p["t2_r"]}</td>'

                    f'<td>{p["t3_r"]}</td>'

                    f'<td>{tl_disp}</td>'

                    f'<td>{p["fc"]}</td>'

                    "</tr>"

                )



        st.markdown(

            '<div class="tp-stats-card">'

            f'<div class="tp-stats-head"><span>📊 Statistiche Giocatori ({len(players_summary)} a referto)</span><span style="font-size:11px;color:#fbbf24;">Clicca su un giocatore per il dettaglio</span></div>'

            f'<div class="tp-table-wrap"><table class="tp-stats-table"><thead>{tbl_head}</thead><tbody>{"".join(rows_html)}</tbody></table></div>'

            '</div>',

            unsafe_allow_html=True,

        )



    # ==========================================

    # CALENDARIO E RISULTATI DELLA SQUADRA

    # ==========================================

    st.subheader(f"Calendario Completo — {team_name}")

    team_games = games_df[

        (games_df["Casa"] == team_name) | (games_df["Trasferta"] == team_name)

    ].sort_values(by=["Giornata", "ID_Partita"])



    andata_df = team_games[team_games["Giornata"] <= 11]

    ritorno_df = team_games[team_games["Giornata"] > 11]



    st.markdown('<div class="cal-phase-hdr">Andata (Giornate 1 – 11)</div>', unsafe_allow_html=True)

    for rnd in sorted(andata_df["Giornata"].unique()):

        st.markdown(

            build_round_html(

                int(rnd),

                andata_df[andata_df["Giornata"] == rnd],

                logo_html_map,

                is_ritorno=False,

                girone_label=girone,

            ),

            unsafe_allow_html=True,

        )



    st.markdown('<div class="cal-phase-hdr">Ritorno (Giornate 12 – 22)</div>', unsafe_allow_html=True)

    for rnd in sorted(ritorno_df["Giornata"].unique()):

        st.markdown(

            build_round_html(

                int(rnd),

                ritorno_df[ritorno_df["Giornata"] == rnd],

                logo_html_map,

                is_ritorno=True,

                girone_label=girone,

            ),

            unsafe_allow_html=True,

        )





def render_calendar(girone: str, games_df: pd.DataFrame, logo_html_map: dict[str, str]) -> None:

    st.markdown(CALENDAR_CSS, unsafe_allow_html=True)

    st.subheader(f"Calendario — {girone}")



    st.markdown(

        f'<div class="cal-filter-banner">'

        f'<div>'

        f'<div class="cal-filter-title">🔎 Filtra il Calendario — {girone}</div>'

        f'<div class="cal-filter-sub">Seleziona una o più giornate, filtra per squadra o clicca su una riga partita per aprire tabellino e formazioni.</div>'

        f'</div>'

        f'<div class="cal-filter-pills">'

        f'<span class="cal-pill">Giornate: <span>1 – 22</span></span>'

        f'<span class="cal-pill">Squadre: <span>11</span></span>'

        f'</div>'

        f'</div>',

        unsafe_allow_html=True,

    )



    sub = games_df[games_df["Girone"] == girone].copy()

    all_rounds = sorted(sub["Giornata"].unique().tolist())

    all_teams = sorted(set(sub["Casa"].tolist()) | set(sub["Trasferta"].tolist()))



    c1, c2 = st.columns(2)

    with c1:

        sel_rounds = st.multiselect(

            "📅 Giornata",

            options=all_rounds,

            default=[],

            format_func=lambda r: f"Giornata {r} ({'Ritorno ' + str(r - 11) if r > 11 else 'Andata ' + str(r)})",

            placeholder="Tutte le giornate (1 – 22)...",

            key=f"cal_rounds_{girone}",

        )

    with c2:

        sel_teams = st.multiselect(

            "🏀 Squadra",

            options=all_teams,

            default=[],

            placeholder="Tutte le squadre del girone...",

            key=f"cal_teams_{girone}",

        )



    if sel_rounds:

        sub = sub[sub["Giornata"].isin(sel_rounds)]

    if sel_teams:

        sub = sub[sub["Casa"].isin(sel_teams) | sub["Trasferta"].isin(sel_teams)]



    st.markdown(

        f'<div style="display:flex;align-items:center;justify-content:space-between;margin:4px 0 12px 2px;font-size:12px;color:#94a3b8;font-weight:700;">'

        f'<span>Partite visualizzate: <strong style="color:#fbbf24;">{len(sub)}</strong></span>'

        f'<span>💡 Clicca su qualsiasi gara per aprire il tabellino</span>'

        f'</div>',

        unsafe_allow_html=True,

    )



    if sub.empty:

        st.info("Nessuna partita trovata con i filtri selezionati.")

        return



    andata_sub = sub[sub["Giornata"] <= 11].sort_values(by=["Giornata", "ID_Partita"])

    ritorno_sub = sub[sub["Giornata"] > 11].sort_values(by=["Giornata", "ID_Partita"])



    if not andata_sub.empty:

        st.markdown('<div class="cal-phase-hdr">Andata (Giornate 1 – 11)</div>', unsafe_allow_html=True)

        for rnd in sorted(andata_sub["Giornata"].unique()):

            st.markdown(

                build_round_html(

                    int(rnd),

                    andata_sub[andata_sub["Giornata"] == rnd],

                    logo_html_map,

                    is_ritorno=False,

                    girone_label=girone,

                ),

                unsafe_allow_html=True,

            )



    if not ritorno_sub.empty:

        st.markdown('<div class="cal-phase-hdr">Ritorno (Giornate 12 – 22)</div>', unsafe_allow_html=True)

        for rnd in sorted(ritorno_sub["Giornata"].unique()):

            st.markdown(

                build_round_html(

                    int(rnd),

                    ritorno_sub[ritorno_sub["Giornata"] == rnd],

                    logo_html_map,

                    is_ritorno=True,

                    girone_label=girone,

                ),

                unsafe_allow_html=True,

            )





def render_our_team(games_df: pd.DataFrame, logo_html_map: dict[str, str]) -> None:

    st.markdown(CALENDAR_CSS, unsafe_allow_html=True)

    st.subheader(f"Focus Squadra — {OUR_TEAM}")

    st.caption(f"Riferimento campionato FIP: {HIGHLIGHT_TEAM} (Girone A)")



    render_team_detail_page(HIGHLIGHT_TEAM, games_df, logo_html_map)





# ==========================================

# MAIN APP

# ==========================================

def main() -> None:

    st.markdown(GLOBAL_UI_CSS, unsafe_allow_html=True)



    games_df = load_full_games_df()

    if "match_details_store" not in st.session_state:

        st.session_state["match_details_store"] = load_match_details_store()



    logo_html_map = build_team_logo_html_map(GITHUB_RAW_BASE)



    st.markdown(

        '<div class="topbar-card">'

        '<div class="topbar-title">🏀 Divisione Regionale 2 Puglia — 2026/27</div>'

        '<div class="topbar-sub">Classifiche ufficiali, mini-classifica migliori terze, tabellini completi e calendario Gironi A, B e C</div>'

        "</div>",

        unsafe_allow_html=True,

    )



    qp_match = st.query_params.get("match", "")

    qp_team = st.query_params.get("team", "")



    with st.sidebar:

        st.header("Navigazione")

        selected_girone = st.radio(

            "Seleziona Girone",

            ["Girone A", "Girone B", "Girone C"],

            index=0,

            key="sb_girone",

        )

        selected_section = st.radio(

            "Sezione",

            ["Classifica", "Calendario", "Squadre", "New Virtus Basket Toritto"],

            index=0,

            key="sb_section",

        )

        st.divider()

        cfg = _get_github_config()

        if cfg["token"]:

            st.caption(f"🟢 Persistenza GitHub attiva ({cfg['owner']}/{cfg['repo']})")

        else:

            st.caption("🟡 GITHUB_TOKEN non impostato: salvataggio locale temporaneo")



    if qp_match:

        render_match_detail_page(str(qp_match), games_df, logo_html_map)

        return



    if qp_team:

        render_team_detail_page(str(qp_team), games_df, logo_html_map)

        return



    if selected_section == "New Virtus Basket Toritto":

        render_our_team(games_df, logo_html_map)

        return



    if selected_section == "Classifica":

        rows = compute_standings(selected_girone, games_df)

        thirds = compute_thirds_standings(games_df)

        render_standings(selected_girone, rows, thirds, logo_html_map, games_df=games_df)

    elif selected_section == "Squadre":

        render_teams_grid(selected_girone, games_df, logo_html_map)

    else:

        render_calendar(selected_girone, games_df, logo_html_map)





if __name__ == "__main__":

    main()
