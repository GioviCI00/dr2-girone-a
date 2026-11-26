import base64
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
DATA_VERSION = "2026-11-26-v21-sortable-stats-fix-t2t3"
OUR_TEAM = "New Virtus Basket Toritto"
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
    # ==========================================
    # GIORNATA 1 — GIRONE A
    # ==========================================
    "A01_1867": {
        "coach_home": "Caressa",
        "coach_away": "Piarulli",
        "quarters_home": [18, 16, 21, 17],
        "quarters_away": [8, 20, 21, 18],
        "ot_home": 0,
        "ot_away": 0,
        "home_players": [
            _p_row("D'Imperio M.", pts=22),
            _p_row("Lovero L.", pts=20),
            _p_row("Eremita A.", pts=12),
            _p_row("Ricci R.", pts=6),
            _p_row("Maldera N.", pts=5),
            _p_row("Lavacca G.", pts=4),
            _p_row("Marcucci S.", pts=3),
            _p_row("Barile G.", pts=0),
            _p_row("Iannone C.", pts=0),
            _p_row("Berardi C.", pts=0),
            _p_row("Menduni G. (N.E.)", pts=0),
            _p_row("Cannillo N. (N.E.)", pts=0),
        ],
        "away_players": [
            _p_row("Volpicella P.", pts=13),
            _p_row("Scaringella F.", pts=11),
            _p_row("Lorusso M.", pts=9),
            _p_row("Ferrara L.", pts=8),
            _p_row("Cantatore E.", pts=8),
            _p_row("Catano K.", pts=6),
            _p_row("Mangione N.", pts=5),
            _p_row("Piccolo D.", pts=3),
            _p_row("Ferrante D. (K)", pts=3),
            _p_row("Di Vittorio S.", pts=1),
            _p_row("Lasorsa C.", pts=0),
            _p_row("De Marco G.", pts=0),
        ],
    },
    "A01_1868": {
        "coach_home": "Giuliani",
        "coach_away": "Menduni",
        "quarters_home": [15, 12, 10, 13],
        "quarters_away": [17, 16, 17, 26],
        "ot_home": 0,
        "ot_away": 0,
        "home_players": [
            _p_row("Franciosi S.", pts=12),
            _p_row("Tarantella E.", pts=11),
            _p_row("Di Santo F.", pts=9),
            _p_row("Conte A.", pts=3),
            _p_row("Guida M.", pts=3),
            _p_row("De Capua A.", pts=3),
            _p_row("Tartaglione R.", pts=3),
            _p_row("Di Gennaro D.", pts=2),
            _p_row("Ferrara A.", pts=2),
            _p_row("Caratù G.", pts=2),
            _p_row("Franciosi D.", pts=0),
            _p_row("Di Lella S.", pts=0),
        ],
        "away_players": [
            _p_row("Tricarico F.", pts=18),
            _p_row("Rinaldi P.", pts=18),
            _p_row("Santoro A.", pts=15),
            _p_row("Marano A.", pts=11),
            _p_row("Russo R.", pts=4),
            _p_row("Kharebava N.", pts=3),
            _p_row("Pepe S.", pts=3),
            _p_row("Russo W.", pts=2),
            _p_row("Carpinelli P.", pts=2),
            _p_row("Khelfat N.", pts=0),
            _p_row("Pysmenytski M.", pts=0),
            _p_row("Rizzi M.", pts=0),
        ],
    },
    "A01_1869": {
        "coach_home": "Zotti",
        "coach_away": "Ursi",
        "quarters_home": [17, 7, 21, 23],
        "quarters_away": [15, 7, 16, 12],
        "ot_home": 0,
        "ot_away": 0,
        "home_players": [
            _p_row("Ruotolo L.", pts=17),
            _p_row("Lamacchia G.", pts=9),
            _p_row("Mariani G.", pts=8),
            _p_row("Ruotolo A.", pts=7),
            _p_row("Natali F.", pts=7),
            _p_row("Germanà A.", pts=6),
            _p_row("Mastromarco P.", pts=6),
            _p_row("Riganti A.", pts=4),
            _p_row("Favale A.", pts=3),
            _p_row("Ancona L.", pts=1),
            _p_row("Bozzi D.", pts=0),
            _p_row("Patruno L.", pts=0),
        ],
        "away_players": [
            _p_row("Manigrasso A.", pts=13),
            _p_row("L'Abbate V.", pts=9),
            _p_row("Gaeta R.", pts=7),
            _p_row("D'Errico M.", pts=6),
            _p_row("Emiliano M.", pts=3),
            _p_row("Genchi R.", pts=3),
            _p_row("Stamerra S.", pts=3),
            _p_row("Lorusso D.", pts=2),
            _p_row("Grittani G.", pts=2),
            _p_row("Carlucci A.", pts=1),
            _p_row("Vaccaro V.", pts=1),
            _p_row("Montemurro D.", pts=0),
        ],
    },
    "A01_1870": {
        "coach_home": "",
        "coach_away": "Angelilli",
        "quarters_home": [19, 20, 18, 21],
        "quarters_away": [21, 27, 21, 18],
        "ot_home": 0,
        "ot_away": 0,
        "home_players": [
            _p_row("Russo R.", pts=18),
            _p_row("Amadey Verdun J.", pts=14),
            _p_row("Chiappinelli G.", pts=14),
            _p_row("Cristiani", pts=9),
            _p_row("Di Franco V.", pts=9),
            _p_row("Olivieri D.", pts=7),
            _p_row("Grosso F.", pts=5),
            _p_row("Podio K.", pts=2),
            _p_row("Tredanari L.", pts=0),
            _p_row("De Lillo G.", pts=0),
            _p_row("Nido A.", pts=0),
            _p_row("Nido N.", pts=0),
        ],
        "away_players": [
            _p_row("De Meo N.", pts=23),
            _p_row("Larocchia A.", pts=22),
            _p_row("Maietta G.", pts=17),
            _p_row("Iacovelli A. (K)", pts=7),
            _p_row("Angelilli D.", pts=6),
            _p_row("Panessa A.", pts=5),
            _p_row("Intino G.", pts=4),
            _p_row("Stillavato R.", pts=2),
            _p_row("Pastore A.", pts=1),
            _p_row("Sivo R.", pts=0),
            _p_row("Rutigliano A.", pts=0),
            _p_row("Casaburi R.", pts=0),
        ],
    },
    "A01_1871": {
        "coach_home": "Diana (Vice: Catucci)",
        "coach_away": "Panzarino",
        "quarters_home": [11, 20, 14, 17],
        "quarters_away": [21, 19, 20, 21],
        "ot_home": 0,
        "ot_away": 0,
        "home_players": [
            _p_row("Piccaluga R.", pts=12),
            _p_row("Sicolo M.", pts=11),
            _p_row("Cannarella R.", pts=10),
            _p_row("Urso M.", pts=7),
            _p_row("Chieco S.", pts=6),
            _p_row("Santeramo M.", pts=6),
            _p_row("Panebianco S.", pts=6),
            _p_row("Bozzi G.", pts=4),
            _p_row("Quaranta G.", pts=0),
            _p_row("De Bellis A. (N.E.)", pts=0),
            _p_row("Loconte L. (N.E.)", pts=0),
            _p_row("Colapinto D. (N.E.)", pts=0),
        ],
        "away_players": [
            _p_row("D'Erasmo F. (K)", pts=28),
            _p_row("Housni Z.", pts=16),
            _p_row("Derosa L.", pts=11),
            _p_row("Provaroni F.", pts=8),
            _p_row("Silletti D.", pts=8),
            _p_row("Colangelo A.", pts=4),
            _p_row("Digno S.", pts=2),
            _p_row("Tounkara D.", pts=2),
            _p_row("Fraccalvieri A.", pts=2),
            _p_row("Desiante V.", pts=0),
            _p_row("Coscia V.", pts=0),
            _p_row("Micunco M. (N.E.)", pts=0),
        ],
    },

    # ==========================================
    # GIORNATA 2 — GIRONE A
    # ==========================================
    "A02_1872": {
        "coach_home": "",
        "coach_away": "",
        "quarters_home": [18, 14, 15, 22],
        "quarters_away": [14, 11, 22, 18],
        "ot_home": 0,
        "ot_away": 0,
        "home_players": [
            _p_row("Scarponi I.", pts=21),
            _p_row("Fuiano M.", pts=15),
            _p_row("Mazzeo R.", pts=10),
            _p_row("Miale A.", pts=8),
            _p_row("Cicculli V.", pts=5),
            _p_row("D'Orsi A.", pts=5),
            _p_row("Miglio E.", pts=2),
            _p_row("Colucci A.", pts=2),
            _p_row("Barletta F.", pts=1),
            _p_row("Campagna G.", pts=0),
            _p_row("Cavallo E.", pts=0),
            _p_row("Giarrusso A. (N.E.)", pts=0),
        ],
        "away_players": [
            _p_row("Chiappinelli G.", pts=18),
            _p_row("Amadey Verdun J.", pts=15),
            _p_row("Russo R.", pts=13),
            _p_row("Di Franco V.", pts=9),
            _p_row("Olivieri D.", pts=4),
            _p_row("Cristiani", pts=3),
            _p_row("Podio K.", pts=3),
            _p_row("De Lillo G.", pts=0),
            _p_row("Grosso F.", pts=0),
            _p_row("Nido A.", pts=0),
            _p_row("Nido N.", pts=0),
            _p_row("Tredanari L. (N.E.)", pts=0),
        ],
    },
    "A02_1873": {
        "coach_home": "Piarulli",
        "coach_away": "Giuliani",
        "quarters_home": [10, 12, 22, 6],
        "quarters_away": [18, 16, 11, 11],
        "ot_home": 0,
        "ot_away": 0,
        "home_players": [
            _p_row("Catano K.", pts=15),
            _p_row("Scaringella F.", pts=11),
            _p_row("Lorusso M.", pts=6),
            _p_row("Lasorsa C.", pts=5),
            _p_row("Di Vittorio S.", pts=4),
            _p_row("Colonna F.", pts=3),
            _p_row("Ferrara L.", pts=2),
            _p_row("Piccolo D.", pts=2),
            _p_row("Ferrante D. (K)", pts=2),
            _p_row("De Marco G.", pts=0),
            _p_row("Sciscioli P.", pts=0),
            _p_row("Mangione N.", pts=0),
        ],
        "away_players": [
            _p_row("Guida M.", pts=12),
            _p_row("Tarantella E.", pts=10),
            _p_row("Tartaglione R.", pts=7),
            _p_row("Ferrara A.", pts=7),
            _p_row("De Capua A.", pts=6),
            _p_row("Di Santo F.", pts=6),
            _p_row("Di Gennaro D.", pts=5),
            _p_row("Franciosi S.", pts=3),
            _p_row("Conte A.", pts=0),
            _p_row("Franciosi D.", pts=0),
            _p_row("Rinaldi C.", pts=0),
            _p_row("Caratù G. (N.E.)", pts=0),
        ],
    },
    "A02_1874": {
        "coach_home": "",
        "coach_away": "Caressa",
        "quarters_home": [21, 7, 8, 13],
        "quarters_away": [11, 17, 17, 14],
        "ot_home": 0,
        "ot_away": 0,
        "home_players": [
            _p_row("Rinaldi P.", pts=11),
            _p_row("Santoro A.", pts=8),
            _p_row("Pysmenytski M.", pts=6),
            _p_row("Marano A.", pts=5),
            _p_row("Tricarico F.", pts=4),
            _p_row("Khelfat N.", pts=4),
            _p_row("Carpinelli P.", pts=3),
            _p_row("Daniello M.", pts=3),
            _p_row("Pepe S.", pts=3),
            _p_row("Rizzi M.", pts=2),
            _p_row("Russo R.", pts=0),
            _p_row("Russo W.", pts=0),
        ],
        "away_players": [
            _p_row("D'Imperio M.", pts=27),
            _p_row("Lavacca G.", pts=12),
            _p_row("Lovero L.", pts=7),
            _p_row("Berardi C.", pts=5),
            _p_row("Eremita A.", pts=5),
            _p_row("Ricci R.", pts=2),
            _p_row("Iannone C.", pts=1),
            _p_row("Basile L.", pts=0),
            _p_row("Maldera N.", pts=0),
            _p_row("Turturo J. (N.E.)", pts=0),
            _p_row("Cannillo A. (N.E.)", pts=0),
            _p_row("Di Terlizzi G. (N.E.)", pts=0),
        ],
    },
    "A02_1875": {
        "coach_home": "Panzarino",
        "coach_away": "Zotti (Vice: Macellaio)",
        "quarters_home": [21, 16, 23, 20],
        "quarters_away": [22, 20, 29, 9],
        "ot_home": 5,
        "ot_away": 16,
        "home_players": [
            _p_row("Tounkara D.", pts=18),
            _p_row("Derosa L.", pts=13),
            _p_row("D'Erasmo F. (K)", pts=13),
            _p_row("Silletti D.", pts=12),
            _p_row("Colangelo A.", pts=9),
            _p_row("Housni Z.", pts=7),
            _p_row("Provaroni F.", pts=5),
            _p_row("Desiante V.", pts=3),
            _p_row("Fraccalvieri A.", pts=3),
            _p_row("Micunco M.", pts=2),
            _p_row("Digno S.", pts=0),
            _p_row("Vero A. (N.E.)", pts=0),
        ],
        "away_players": [
            _p_row("Ruotolo L.", pts=41),
            _p_row("Mariani G.", pts=31),
            _p_row("Ruotolo A.", pts=9),
            _p_row("Mastromarco P.", pts=4),
            _p_row("Natali F.", pts=4),
            _p_row("Riganti A.", pts=4),
            _p_row("Lamacchia G.", pts=3),
            _p_row("Ancona L.", pts=0),
            _p_row("Bernardi A.", pts=0),
            _p_row("Bozzi D.", pts=0),
            _p_row("Patruno L.", pts=0),
            _p_row("Rubino A.", pts=0),
        ],
    },
    "A02_1876": {
        "coach_home": "Ursi",
        "coach_away": "Diana (Vice: Catucci)",
        "quarters_home": [11, 14, 15, 16],
        "quarters_away": [16, 13, 6, 13],
        "ot_home": 0,
        "ot_away": 0,
        "home_players": [
            _p_row("Merlo N.", pts=13),
            _p_row("D'Errico M.", pts=10),
            _p_row("L'Abbate V.", pts=8),
            _p_row("Carlucci A.", pts=7),
            _p_row("Manigrasso A.", pts=7),
            _p_row("Montemurro D.", pts=4),
            _p_row("Gaeta R.", pts=3),
            _p_row("Vaccaro V.", pts=2),
            _p_row("Emiliano M.", pts=2),
            _p_row("Stamerra S.", pts=0),
            _p_row("Genchi R.", pts=0),
            _p_row("Lorusso D.", pts=0),
        ],
        "away_players": [
            _p_row("Cannarella R.", pts=13),
            _p_row("Bozzi G.", pts=10),
            _p_row("Santeramo M.", pts=9),
            _p_row("Sicolo M.", pts=7),
            _p_row("Piccaluga R.", pts=6),
            _p_row("Quaranta G.", pts=2),
            _p_row("Chieco S.", pts=1),
            _p_row("Zaccaria G.", pts=0),
            _p_row("Caradonna P.", pts=0),
            _p_row("Panebianco S.", pts=0),
            _p_row("De Bellis A. (N.E.)", pts=0),
            _p_row("Loconte L. (N.E.)", pts=0),
        ],
    },

    # ==========================================
    # GIORNATA 3 — GIRONE A
    # ==========================================
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
            _p_row("Carlucci A.", pts=9),
            _p_row("D'Errico M.", pts=9),
            _p_row("Montemurro D.", pts=4),
            _p_row("Lorusso D.", pts=6),
            _p_row("Manigrasso A.", pts=25),
            _p_row("Merlo N.", pts=12),
            _p_row("Gaeta R.", pts=2),
            _p_row("Grittani G.", pts=3),
            _p_row("Genchi R.", pts=3),
            _p_row("Stamerra S.", pts=3),
            _p_row("Emiliano M.", pts=1),
            _p_row("Vaccaro V. A.", pts=2),
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
    grid-template-columns: 52px 52px 1fr 50px 50px 50px 66px 156px 62px;
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
    grid-template-columns: 52px 52px 1fr 50px 50px 50px 66px 156px 62px;
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
table.lba-box th.sub-hdr.active-sort {
    background: #fef3c7;
    color: #b45309;
    border-bottom: 2px solid #d97706;
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
    gap: 3px;
    transition: transform 0.16s ease;
}
.jersey-card:hover {
    transform: translateY(-3px) scale(1.06);
}
.jersey-shape {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 900;
    font-size: 13px;
    color: #ffffff;
    border: 2px solid rgba(255, 255, 255, 0.88);
}
.jersey-home {
    background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
    box-shadow: 0 6px 14px rgba(37, 99, 235, 0.48);
}
.jersey-away {
    background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%);
    box-shadow: 0 6px 14px rgba(220, 38, 38, 0.48);
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
    flex-wrap: wrap;
    gap: 8px;
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
table.tp-stats-table th.active-sort {
    background: #fef3c7;
    color: #b45309;
    border-bottom: 2px solid #d97706;
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

            cards_html.append(
                f'<a class="team-tile-link" href="?team={sq_enc}" target="_self">'
                f'<div class="team-square-card">'
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


def _parse_minutes_to_seconds(min_str: str) -> int:
    s = str(min_str or "").strip()
    if not s or s == "-":
        return 0
    if ":" in s:
        try:
            m_part, s_part = s.split(":", 1)
            return int(float(m_part)) * 60 + int(float(s_part))
        except Exception:
            return 0
    try:
        return int(float(s)) * 60
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
    for row_dict in df.to_dict("records"):
        name = str(row_dict.get("Giocatore", "") or "").strip()
        if not name:
            continue
        prev = existing_by_name.get(name.lower(), {})
        r2_val = int(pd.to_numeric(row_dict.get("2PT_R", prev.get("2PT_R", 0)), errors="coerce") or 0)
        t2_val = int(pd.to_numeric(row_dict.get("2PT_T", prev.get("2PT_T", r2_val)), errors="coerce") or 0)
        if t2_val < r2_val:
            t2_val = r2_val
        r3_val = int(pd.to_numeric(row_dict.get("3PT_R", prev.get("3PT_R", 0)), errors="coerce") or 0)
        t3_val = int(pd.to_numeric(row_dict.get("3PT_T", prev.get("3PT_T", r3_val)), errors="coerce") or 0)
        if t3_val < r3_val:
            t3_val = r3_val
        tl_r_val = int(pd.to_numeric(row_dict.get("TL_R", prev.get("TL_R", 0)), errors="coerce") or 0)
        tl_t_val = int(pd.to_numeric(row_dict.get("TL_T", prev.get("TL_T", tl_r_val)), errors="coerce") or 0)
        if tl_t_val < tl_r_val:
            tl_t_val = tl_r_val

        raw_num = row_dict.get("NUM", None)
        if raw_num is None or (isinstance(raw_num, float) and pd.isna(raw_num)):
            raw_num = prev.get("NUM", None)

        out.append(
            _p_row(
                giocatore=name,
                numero=raw_num,
                pts=int(pd.to_numeric(row_dict.get("PUN", prev.get("PUN", 0)), errors="coerce") or 0),
                minuti=str(row_dict.get("MIN", prev.get("MIN", "0")) or "0").strip(),
                sf=bool(row_dict.get("SF", prev.get("SF", False))),
                falli_c=int(pd.to_numeric(row_dict.get("F_C", prev.get("F_C", 0)), errors="coerce") or 0),
                falli_s=int(pd.to_numeric(row_dict.get("F_S", prev.get("F_S", 0)), errors="coerce") or 0),
                t2_r=r2_val,
                t2_t=t2_val,
                sc=int(pd.to_numeric(row_dict.get("SC", prev.get("SC", 0)), errors="coerce") or 0),
                t3_r=r3_val,
                t3_t=t3_val,
                tl_r=tl_r_val,
                tl_t=tl_t_val,
                rim_o=int(pd.to_numeric(row_dict.get("RIM_O", prev.get("RIM_O", 0)), errors="coerce") or 0),
                rim_d=int(pd.to_numeric(row_dict.get("RIM_D", prev.get("RIM_D", 0)), errors="coerce") or 0),
                st_d=int(pd.to_numeric(row_dict.get("ST_D", prev.get("ST_D", 0)), errors="coerce") or 0),
                st_s=int(pd.to_numeric(row_dict.get("ST_S", prev.get("ST_S", 0)), errors="coerce") or 0),
                pal_p=int(pd.to_numeric(row_dict.get("PAL_P", prev.get("PAL_P", 0)), errors="coerce") or 0),
                pal_r=int(pd.to_numeric(row_dict.get("PAL_R", prev.get("PAL_R", 0)), errors="coerce") or 0),
                ass=int(pd.to_numeric(row_dict.get("ASS", prev.get("ASS", 0)), errors="coerce") or 0),
                val_lega=int(pd.to_numeric(row_dict.get("VAL", prev.get("VAL", 0)), errors="coerce") or 0),
                oer=float(pd.to_numeric(row_dict.get("OER", prev.get("OER", 0.0)), errors="coerce") or 0.0),
            )
        )
    return out


BOXSCORE_SORT_OPTIONS_FULL: dict[str, str] = {
    "Ordine inserimento (predefinito)": "DEFAULT",
    "Punti (PUN)": "PUN",
    "Numero di maglia (#)": "NUM",
    "Nome Giocatore": "GIOCATORE",
    "Minuti giocati (MIN)": "MIN",
    "Falli commessi (F_C)": "F_C",
    "Falli subiti (F_S)": "F_S",
    "Tiri da 2 segnati (2PT R)": "2PT_R",
    "Tiri da 2 tentati (2PT T)": "2PT_T",
    "% Tiri da 2 (2PT %)": "2PT_PCT",
    "Tiri da 3 segnati (3PT R)": "3PT_R",
    "Tiri da 3 tentati (3PT T)": "3PT_T",
    "% Tiri da 3 (3PT %)": "3PT_PCT",
    "Tiri liberi segnati (TL R)": "TL_R",
    "Tiri liberi tentati (TL T)": "TL_T",
    "% Tiri liberi (TL %)": "TL_PCT",
    "Rimbalzi offensivi (RIM O)": "RIM_O",
    "Rimbalzi difensivi (RIM D)": "RIM_D",
    "Rimbalzi totali (RIM T)": "RIM_T",
    "Stoppate date (ST D)": "ST_D",
    "Stoppate subite (ST S)": "ST_S",
    "Palle perse (PAL P)": "PAL_P",
    "Palle recuperate (PAL R)": "PAL_R",
    "Valutazione Lega (VAL)": "VAL",
    "OER": "OER",
}

BOXSCORE_SORT_OPTIONS_COMPACT: dict[str, str] = {
    "Ordine inserimento (predefinito)": "DEFAULT",
    "Punti (PUN)": "PUN",
    "Numero di maglia (#)": "NUM",
    "Nome Giocatore": "GIOCATORE",
    "Minuti giocati (MIN)": "MIN",
    "Falli commessi (F_C)": "F_C",
    "Tiri da 2 segnati (2PT R)": "2PT_R",
    "Tiri da 3 segnati (3PT R)": "3PT_R",
    "Tiri liberi segnati (TL R)": "TL_R",
    "Tiri liberi tentati (TL T)": "TL_T",
    "% Tiri liberi (TL %)": "TL_PCT",
}


def _sort_boxscore_players(players: list[dict], sort_key: str, descending: bool = True) -> list[dict]:
    if not players or sort_key == "DEFAULT":
        return players

    def _val_fn(p: dict):
        if sort_key == "NUM":
            n = int(p.get("NUM", 999))
            return n if 0 <= n <= 99 else (999 if not descending else -1)
        if sort_key == "GIOCATORE":
            return str(p.get("Giocatore", "")).strip().lower()
        if sort_key == "MIN":
            return _parse_minutes_to_seconds(str(p.get("MIN", "0")))
        if sort_key == "2PT_PCT":
            att = int(p.get("2PT_T", 0))
            return (int(p.get("2PT_R", 0)) / att) if att > 0 else -1.0
        if sort_key == "3PT_PCT":
            att = int(p.get("3PT_T", 0))
            return (int(p.get("3PT_R", 0)) / att) if att > 0 else -1.0
        if sort_key == "TL_PCT":
            att = int(p.get("TL_T", 0))
            return (int(p.get("TL_R", 0)) / att) if att > 0 else -1.0
        if sort_key == "RIM_T":
            return int(p.get("RIM_O", 0)) + int(p.get("RIM_D", 0))
        if sort_key == "OER":
            return float(p.get("OER", 0.0))
        return int(p.get(sort_key, 0))

    return sorted(
        players,
        key=lambda p: (_val_fn(p), str(p.get("Giocatore", "")).strip().lower()),
        reverse=descending,
    )


def render_lba_boxscore(
    team_name: str,
    coach_name: str,
    players: list[dict],
    logo_html_map: dict[str, str],
    full_stats: bool = True,
    sort_key: str = "DEFAULT",
    sort_desc: bool = True,
) -> None:
    norm_players = _sort_boxscore_players(_normalize_player_rows(players), sort_key=sort_key, descending=sort_desc)
    logo_tag = logo_html_map.get(
        f"lba::{team_name}",
        '<div class="lba-team-logo" style="display:flex;align-items:center;justify-content:center;font-size:22px;">🏀</div>',
    )
    allenatore_txt = coach_name.strip() if coach_name.strip() else "—"
    badge_txt = "STATISTICHE DETTAGLIATE" if full_stats else "TABELLINO ESSENZIALE"
    table_cls = "lba-box full-stats" if full_stats else "lba-box compact-stats"
    arrow_txt = " ↓" if sort_desc else " ↑"

    def _th_cls(base_cls: str, col_keys: tuple[str, ...]) -> str:
        return f"{base_cls} active-sort" if sort_key in col_keys else base_cls

    def _th_lbl(label: str, col_keys: tuple[str, ...]) -> str:
        return f"{label}{arrow_txt}" if sort_key in col_keys else label

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
            f'<th class="{_th_cls("sub-hdr left-col", ("GIOCATORE", "NUM"))}">{_th_lbl("GIOCATORE", ("GIOCATORE", "NUM"))}</th>'
            f'<th class="{_th_cls("sub-hdr pts-col", ("PUN",))}">{_th_lbl("PUN", ("PUN",))}</th>'
            f'<th class="{_th_cls("sub-hdr", ("MIN",))}">{_th_lbl("MIN", ("MIN",))}</th>'
            '<th class="sub-hdr">SF</th>'
            f'<th class="{_th_cls("sub-hdr", ("F_C",))}">{_th_lbl("C", ("F_C",))}</th>'
            f'<th class="{_th_cls("sub-hdr", ("F_S",))}">{_th_lbl("S", ("F_S",))}</th>'
            f'<th class="{_th_cls("sub-hdr", ("2PT_R",))}">{_th_lbl("R", ("2PT_R",))}</th>'
            f'<th class="{_th_cls("sub-hdr", ("2PT_T",))}">{_th_lbl("T", ("2PT_T",))}</th>'
            f'<th class="{_th_cls("sub-hdr pts-col", ("2PT_PCT",))}">{_th_lbl("%", ("2PT_PCT",))}</th>'
            f'<th class="{_th_cls("sub-hdr", ("3PT_R",))}">{_th_lbl("R", ("3PT_R",))}</th>'
            f'<th class="{_th_cls("sub-hdr", ("3PT_T",))}">{_th_lbl("T", ("3PT_T",))}</th>'
            f'<th class="{_th_cls("sub-hdr pts-col", ("3PT_PCT",))}">{_th_lbl("%", ("3PT_PCT",))}</th>'
            f'<th class="{_th_cls("sub-hdr", ("TL_R",))}">{_th_lbl("R", ("TL_R",))}</th>'
            f'<th class="{_th_cls("sub-hdr", ("TL_T",))}">{_th_lbl("T", ("TL_T",))}</th>'
            f'<th class="{_th_cls("sub-hdr pts-col", ("TL_PCT",))}">{_th_lbl("%", ("TL_PCT",))}</th>'
            f'<th class="{_th_cls("sub-hdr", ("RIM_O",))}">{_th_lbl("O", ("RIM_O",))}</th>'
            f'<th class="{_th_cls("sub-hdr", ("RIM_D",))}">{_th_lbl("D", ("RIM_D",))}</th>'
            f'<th class="{_th_cls("sub-hdr", ("RIM_T",))}">{_th_lbl("T", ("RIM_T",))}</th>'
            f'<th class="{_th_cls("sub-hdr", ("ST_D",))}">{_th_lbl("D", ("ST_D",))}</th>'
            f'<th class="{_th_cls("sub-hdr", ("ST_S",))}">{_th_lbl("S", ("ST_S",))}</th>'
            f'<th class="{_th_cls("sub-hdr", ("PAL_P",))}">{_th_lbl("P", ("PAL_P",))}</th>'
            f'<th class="{_th_cls("sub-hdr", ("PAL_R",))}">{_th_lbl("R", ("PAL_R",))}</th>'
            f'<th class="{_th_cls("sub-hdr", ("VAL",))}">{_th_lbl("LEGA", ("VAL",))}</th>'
            f'<th class="{_th_cls("sub-hdr", ("OER",))}">{_th_lbl("OER", ("OER",))}</th>'
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
            f'<th class="{_th_cls("sub-hdr left-col", ("GIOCATORE", "NUM"))}">{_th_lbl("GIOCATORE", ("GIOCATORE", "NUM"))}</th>'
            f'<th class="{_th_cls("sub-hdr pts-col", ("PUN",))}">{_th_lbl("PUN", ("PUN",))}</th>'
            f'<th class="{_th_cls("sub-hdr", ("MIN",))}">{_th_lbl("MIN", ("MIN",))}</th>'
            '<th class="sub-hdr">SF</th>'
            f'<th class="{_th_cls("sub-hdr", ("F_C",))}">{_th_lbl("C", ("F_C",))}</th>'
            f'<th class="{_th_cls("sub-hdr", ("2PT_R",))}">{_th_lbl("R", ("2PT_R",))}</th>'
            f'<th class="{_th_cls("sub-hdr", ("3PT_R",))}">{_th_lbl("R", ("3PT_R",))}</th>'
            f'<th class="{_th_cls("sub-hdr", ("TL_R",))}">{_th_lbl("R", ("TL_R",))}</th>'
            f'<th class="{_th_cls("sub-hdr", ("TL_T",))}">{_th_lbl("T", ("TL_T",))}</th>'
            f'<th class="{_th_cls("sub-hdr pts-col", ("TL_PCT",))}">{_th_lbl("%", ("TL_PCT",))}</th>'
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
        html.append(
            '<tr class="total-row">'
            '<td class="player-name">TOTALI</td>'
            f'<td class="pts-val">{tot_pun}</td>'
            f"<td>{tot_min_num}</td>"
            "<td></td>"
            f"<td>{tot_fc}</td>"
            f"<td>{tot_fs}</td>"
            f"<td>{tot_2r}</td>"
            f"<td>{tot_2t}</td>"
            f'<td class="pct-val">{_fmt_pct(tot_2r, tot_2t)}</td>'
            f"<td>{tot_3r}</td>"
            f"<td>{tot_3t}</td>"
            f'<td class="pct-val">{_fmt_pct(tot_3r, tot_3t)}</td>'
            f"<td>{tot_tlr}</td>"
            f"<td>{tot_tlt}</td>"
            f'<td class="pct-val">{_fmt_pct(tot_tlr, tot_tlt)}</td>'
            f"<td>{tot_rimo}</td>"
            f"<td>{tot_rimd}</td>"
            f"<td>{tot_rimt}</td>"
            f"<td>{tot_std}</td>"
            f"<td>{tot_sts}</td>"
            f"<td>{tot_palp}</td>"
            f"<td>{tot_palr}</td>"
            f"<td>{tot_val}</td>"
            "<td>0</td>"
            "</tr>"
        )
    else:
        html.append(
            '<tr class="total-row">'
            '<td class="player-name">TOTALI</td>'
            f'<td class="pts-val">{tot_pun}</td>'
            f"<td>{tot_min_num}</td>"
            "<td></td>"
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


def _select_starting_five(players: list[dict]) -> list[dict]:
    norm = _normalize_player_rows(players)
    if not norm:
        return []
    starters = [p for p in norm if p.get("SF")]
    if len(starters) < 5:
        used = {p["Giocatore"] for p in starters}
        active_pool = [
            p
            for p in norm
            if p["Giocatore"] not in used and "(N.E.)" not in p["Giocatore"].upper()
        ]
        active_pool.sort(key=lambda x: (-_parse_minutes_to_int(x["MIN"]), -x["PUN"]))
        starters.extend(active_pool[: 5 - len(starters)])
    if len(starters) < 5:
        used = {p["Giocatore"] for p in starters}
        rest = [p for p in norm if p["Giocatore"] not in used]
        starters.extend(rest[: 5 - len(starters)])
    return starters[:5]


def _render_side_roster_html(
    team_name: str,
    players: list[dict],
    starters: list[dict],
    logo_html_map: dict[str, str],
) -> str:
    starter_names = {p["Giocatore"] for p in starters}
    bench = [p for p in players if p["Giocatore"] not in starter_names]
    logo_src = logo_html_map.get(f"raw_src::{team_name}", "")
    logo_img = f'<img src="{logo_src}" alt="" />' if logo_src else "<span>🏀</span>"

    def _player_line(p: dict, is_starter: bool) -> str:
        num_txt = _format_jersey_display(p.get("NUM"), empty_placeholder="—")
        cls = "roster-player-line starter" if is_starter else "roster-player-line"
        return (
            f'<div class="{cls}">'
            f'<span class="roster-num-pill">{num_txt}</span>'
            f'<span>{p["Giocatore"]}</span>'
            f"</div>"
        )

    s_lines = "".join(_player_line(p, True) for p in starters) if starters else '<div style="color:#94a3b8;font-size:11.5px;">Non disponibile</div>'
    b_lines = "".join(_player_line(p, False) for p in bench) if bench else '<div style="color:#94a3b8;font-size:11.5px;">Nessuna riserva</div>'

    return (
        '<div class="roster-side-card">'
        f'<div class="roster-side-head">{logo_img}<span>{team_name}</span></div>'
        '<div class="roster-group-lbl">Quintetto Base</div>'
        f"{s_lines}"
        '<hr class="roster-divider" />'
        '<div class="roster-group-lbl" style="color:#93c5fd;">Panchina</div>'
        f"{b_lines}"
        "</div>"
    )


def render_starting_five_court(
    home_team: str,
    away_team: str,
    home_players: list[dict],
    away_players: list[dict],
    logo_html_map: dict[str, str],
) -> None:
    norm_home = _normalize_player_rows(home_players)
    norm_away = _normalize_player_rows(away_players)
    home_five = _select_starting_five(norm_home)
    away_five = _select_starting_five(norm_away)

    def _jersey_html(p: dict, side_cls: str) -> str:
        surname = _extract_surname(p["Giocatore"]) or p["Giocatore"]
        num_disp = _format_jersey_display(p.get("NUM"), empty_placeholder="•")
        return (
            '<div class="jersey-card">'
            f'<div class="jersey-shape {side_cls}">{num_disp}</div>'
            f'<div class="jersey-name">{surname}</div>'
            "</div>"
        )

    def _half_html(five: list[dict], side_cls: str) -> str:
        if not five:
            return '<div class="half-court-col"><div class="half-row-mid"><span style="color:#94a3b8;font-size:12px;font-weight:700;">Quintetto N.D.</span></div></div>'
        top_p = five[0:2]
        mid_p = five[2:3]
        bot_p = five[3:5]
        return (
            '<div class="half-court-col">'
            f'<div class="half-row-top">{"".join(_jersey_html(p, side_cls) for p in top_p)}</div>'
            f'<div class="half-row-mid">{"".join(_jersey_html(p, side_cls) for p in mid_p)}</div>'
            f'<div class="half-row-bot">{"".join(_jersey_html(p, side_cls) for p in bot_p)}</div>'
            "</div>"
        )

    court_svg = """
    <svg class="court-svg-bg" viewBox="0 0 900 480" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="14" y="14" width="872" height="452" rx="10" fill="none" stroke="rgba(226,232,240,0.45)" stroke-width="3"/>
      <line x1="450" y1="14" x2="450" y2="466" stroke="rgba(226,232,240,0.45)" stroke-width="3"/>
      <circle cx="450" cy="240" r="64" fill="rgba(59,130,246,0.08)" stroke="rgba(226,232,240,0.45)" stroke-width="3"/>
      <circle cx="450" cy="240" r="10" fill="rgba(251,191,36,0.55)"/>
      <rect x="14" y="156" width="166" height="168" fill="rgba(59,130,246,0.12)" stroke="rgba(226,232,240,0.45)" stroke-width="2.5"/>
      <circle cx="180" cy="240" r="56" fill="none" stroke="rgba(226,232,240,0.4)" stroke-width="2.5"/>
      <path d="M 14 48 L 96 48 A 204 204 0 0 1 96 432 L 14 432" fill="none" stroke="rgba(251,191,36,0.42)" stroke-width="2.5"/>
      <line x1="42" y1="214" x2="42" y2="266" stroke="#f8fafc" stroke-width="4"/>
      <circle cx="56" cy="240" r="11" fill="none" stroke="#fbbf24" stroke-width="2.5"/>
      <rect x="720" y="156" width="166" height="168" fill="rgba(239,68,68,0.12)" stroke="rgba(226,232,240,0.45)" stroke-width="2.5"/>
      <circle cx="720" cy="240" r="56" fill="none" stroke="rgba(226,232,240,0.4)" stroke-width="2.5"/>
      <path d="M 886 48 L 804 48 A 204 204 0 0 0 804 432 L 886 432" fill="none" stroke="rgba(251,191,36,0.42)" stroke-width="2.5"/>
      <line x1="858" y1="214" x2="858" y2="266" stroke="#f8fafc" stroke-width="4"/>
      <circle cx="844" cy="240" r="11" fill="none" stroke="#fbbf24" stroke-width="2.5"/>
    </svg>
    """

    home_side_html = _render_side_roster_html(home_team, norm_home, home_five, logo_html_map)
    away_side_html = _render_side_roster_html(away_team, norm_away, away_five, logo_html_map)

    html = (
        '<div class="formation-3col">'
        f"{home_side_html}"
        '<div class="court-compact-wrap">'
        '<div class="court-stage">'
        f"{court_svg}"
        '<div class="court-players-layer">'
        f'{_half_html(home_five, "jersey-home")}'
        f'{_half_html(away_five, "jersey-away")}'
        "</div>"
        "</div>"
        "</div>"
        f"{away_side_html}"
        "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)


def render_recent_matches_comparison(
    home_team: str,
    away_team: str,
    current_match_id: str,
    games_df: pd.DataFrame,
    logo_html_map: dict[str, str],
) -> None:
    played = games_df[games_df["Stato"].astype(str).str.strip().str.lower() == "giocata"].copy()

    def _team_recent_html(team: str) -> str:
        sub = played[
            ((played["Casa"] == team) | (played["Trasferta"] == team))
            & (played["ID_Partita"] != current_match_id)
        ].sort_values(by=["Giornata", "ID_Partita"], ascending=[False, False]).head(5)

        logo_src = logo_html_map.get(f"raw_src::{team}", "")
        logo_img = f'<img src="{logo_src}" alt="" />' if logo_src else "<span>🏀</span>"

        rows_html = []
        if sub.empty:
            rows_html.append('<div style="color:#94a3b8;font-size:12px;">Nessuna partita precedente registrata.</div>')
        else:
            for g in sub.itertuples(index=False):
                is_home = str(g.Casa) == team
                opp = str(g.Trasferta) if is_home else str(g.Casa)
                my_pts = int(g.Punti_Casa) if is_home else int(g.Punti_Trasferta)
                opp_pts = int(g.Punti_Trasferta) if is_home else int(g.Punti_Casa)
                won = my_pts > opp_pts
                badge_cls = "hist-badge-w" if won else "hist-badge-l"
                badge_txt = "VINTA" if won else "PERSA"
                loc_txt = "Casa" if is_home else "Trasf."
                gid_enc = quote(str(g.ID_Partita), safe="")
                rows_html.append(
                    f'<a href="?match={gid_enc}" target="_self" style="text-decoration:none;color:inherit;">'
                    '<div class="hist-item">'
                    f'<div class="{badge_cls}">{badge_txt}</div>'
                    f'<div style="color:#e2e8f0;font-weight:700;">G{int(g.Giornata)} • vs {opp} <span style="color:#94a3b8;font-size:11px;">({loc_txt})</span></div>'
                    f'<div class="hist-score">{my_pts} - {opp_pts}</div>'
                    "</div>"
                    "</a>"
                )

        return (
            '<div class="hist-col">'
            f'<div class="hist-col-head">{logo_img}<span>{team}</span></div>'
            f'{"".join(rows_html)}'
            "</div>"
        )

    st.markdown(
        f'<div class="hist-grid">{_team_recent_html(home_team)}{_team_recent_html(away_team)}</div>',
        unsafe_allow_html=True,
    )


def render_match_detail_page(match_id: str, games_df: pd.DataFrame, logo_html_map: dict[str, str]) -> None:
    st.markdown(MATCH_DETAIL_CSS, unsafe_allow_html=True)

    sub = games_df[games_df["ID_Partita"] == match_id]
    if sub.empty:
        st.error("Partita non trovata.")
        if st.button("Torna a Classifica e Calendario", type="primary"):
            st.query_params.clear()
            st.rerun()
        return

    g = sub.iloc[0]
    girone = str(g["Girone"])
    giornata = int(g["Giornata"])
    data_str = str(g["Data"])
    casa = str(g["Casa"])
    trasferta = str(g["Trasferta"])
    pts_casa = int(g["Punti_Casa"])
    pts_trasf = int(g["Punti_Trasferta"])
    stato = str(g["Stato"])
    is_played = stato.strip().lower() == "giocata"

    if st.button("← Torna a Classifica e Calendario", key="back_from_match"):
        st.query_params.clear()
        st.rerun()

    home_logo = logo_html_map.get(f"hero::{casa}", '<div class="md-logo-box">🏀</div>')
    away_logo = logo_html_map.get(f"hero::{trasferta}", '<div class="md-logo-box">🏀</div>')
    score_display = f"{pts_casa} - {pts_trasf}" if is_played else "VS"
    status_display = "CONCLUSA" if is_played else "DA GIOCARE"
    casa_enc = quote(casa, safe="")
    trasf_enc = quote(trasferta, safe="")

    st.markdown(
        f'<div class="md-hero">'
        f'<div style="text-align:center;font-size:12px;font-weight:800;color:#fbbf24;letter-spacing:0.8px;text-transform:uppercase;margin-bottom:10px;">'
        f'{girone} — Giornata {giornata}'
        f'</div>'
        f'<div class="md-grid">'
        f'<div class="md-team-block">'
        f'<a href="?team={casa_enc}" target="_self">{home_logo}</a>'
        f'<a class="team-link" href="?team={casa_enc}" target="_self"><div class="md-team-name">{casa}</div></a>'
        f'</div>'
        f'<div class="md-center">'
        f'<div class="md-date">{data_str}</div>'
        f'<div class="md-score">{score_display}</div>'
        f'<div class="md-status">{status_display}</div>'
        f'</div>'
        f'<div class="md-team-block">'
        f'<a href="?team={trasf_enc}" target="_self">{away_logo}</a>'
        f'<a class="team-link" href="?team={trasf_enc}" target="_self"><div class="md-team-name">{trasferta}</div></a>'
        f'</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    detail = _get_match_detail(match_id)
    qh = detail["quarters_home"]
    qa = detail["quarters_away"]
    ot_h = int(detail.get("ot_home", 0))
    ot_a = int(detail.get("ot_away", 0))
    has_ot = (ot_h > 0 or ot_a > 0)

    tab_risultati, tab_statistiche, tab_formazione, tab_partite = st.tabs(
        ["RISULTATI", "STATISTICHE", "FORMAZIONE", "PARTITE"]
    )

    with tab_risultati:
        ot_th = "<th>OT</th>" if has_ot else ""
        ot_td_h = f"<td>{ot_h}</td>" if has_ot else ""
        ot_td_a = f"<td>{ot_a}</td>" if has_ot else ""
        st.markdown(
            '<div class="md-sec-card">'
            '<div class="md-sec-title"><span>Parziali per Quarto</span></div>'
            '<table class="md-res-table">'
            f'<thead><tr><th class="team-col">Squadra</th><th>1° Q</th><th>2° Q</th><th>3° Q</th><th>4° Q</th>{ot_th}<th>TOT</th></tr></thead>'
            '<tbody>'
            f'<tr><td class="team-col">{casa}</td><td>{qh[0]}</td><td>{qh[1]}</td><td>{qh[2]}</td><td>{qh[3]}</td>{ot_td_h}<td class="tot-col">{pts_casa}</td></tr>'
            f'<tr><td class="team-col">{trasferta}</td><td>{qa[0]}</td><td>{qa[1]}</td><td>{qa[2]}</td><td>{qa[3]}</td>{ot_td_a}<td class="tot-col">{pts_trasf}</td></tr>'
            '</tbody>'
            '</table>'
            '</div>',
            unsafe_allow_html=True,
        )

    with tab_statistiche:
        is_full_stats_match = (match_id == "A03_1880")
        sort_options_map = (
            BOXSCORE_SORT_OPTIONS_FULL if is_full_stats_match else BOXSCORE_SORT_OPTIONS_COMPACT
        )
        sc1, sc2 = st.columns([3, 1.3])
        with sc1:
            selected_sort_lbl = st.selectbox(
                "Ordina tabellino per",
                options=list(sort_options_map.keys()),
                index=0,
                key=f"match_box_sort_col_{match_id}",
            )
        with sc2:
            selected_sort_dir = st.radio(
                "Ordine",
                options=["Decrescente", "Crescente"],
                horizontal=True,
                index=0,
                key=f"match_box_sort_dir_{match_id}",
            )
        active_sort_key = sort_options_map[selected_sort_lbl]
        active_sort_desc = (selected_sort_dir == "Decrescente")

        if detail["home_players"] or detail["away_players"]:
            render_lba_boxscore(
                team_name=casa,
                coach_name=detail["coach_home"],
                players=detail["home_players"],
                logo_html_map=logo_html_map,
                full_stats=is_full_stats_match,
                sort_key=active_sort_key,
                sort_desc=active_sort_desc,
            )
            render_lba_boxscore(
                team_name=trasferta,
                coach_name=detail["coach_away"],
                players=detail["away_players"],
                logo_html_map=logo_html_map,
                full_stats=is_full_stats_match,
                sort_key=active_sort_key,
                sort_desc=active_sort_desc,
            )
        else:
            st.info("Tabellino completo non ancora disponibile per questa gara. Lo staff può inserirlo qui sotto.")

    with tab_formazione:
        st.markdown(
            '<div class="md-sec-card"><div class="md-sec-title"><span>Quintetti Iniziali e Roster</span>'
            '<span style="font-size:11px;color:#93c5fd;">Blu = Casa • Rosso = Ospiti</span></div>',
            unsafe_allow_html=True,
        )
        render_starting_five_court(
            home_team=casa,
            away_team=trasferta,
            home_players=detail["home_players"],
            away_players=detail["away_players"],
            logo_html_map=logo_html_map,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_partite:
        st.markdown(
            '<div class="md-sec-card"><div class="md-sec-title"><span>Ultime 5 Partite Disputate</span></div>',
            unsafe_allow_html=True,
        )
        render_recent_matches_comparison(casa, trasferta, match_id, games_df, logo_html_map)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    with st.expander("Area Staff — Aggiorna Risultato, Parziali e Tabellino Gara", expanded=False):
        if not st.session_state.get("staff_authenticated", False):
            pwd = st.text_input("Password Staff", type="password", key=f"pwd_match_{match_id}")
            if st.button("Sblocca Area Staff", key=f"unlock_match_{match_id}", type="primary"):
                if pwd == STAFF_PASSWORD:
                    st.session_state["staff_authenticated"] = True
                    st.rerun()
                else:
                    st.error("Password non corretta.")
        else:
            st.caption("Modalità Staff attiva. Modifica il punteggio ufficiale, i parziali dei quarti e il tabellino giocatori.")
            is_full_edit_match = (match_id == "A03_1880")
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1:
                new_date = st.text_input("Data e Ora", value=data_str, key=f"ed_date_{match_id}")
                new_status = st.selectbox(
                    "Stato Gara",
                    ["Giocata", "Da giocare"],
                    index=0 if is_played else 1,
                    key=f"ed_stat_{match_id}",
                )
            with c2:
                new_pts_h = st.number_input(f"Punti {casa}", min_value=0, max_value=250, value=pts_casa, key=f"ed_ph_{match_id}")
                coach_h = st.text_input(f"Allenatore {casa}", value=detail["coach_home"], key=f"ed_ch_{match_id}")
            with c3:
                new_pts_a = st.number_input(f"Punti {trasferta}", min_value=0, max_value=250, value=pts_trasf, key=f"ed_pa_{match_id}")
                coach_a = st.text_input(f"Allenatore {trasferta}", value=detail["coach_away"], key=f"ed_ca_{match_id}")

            st.markdown("**Parziali per Quarto + Eventuale Overtime (OT)**")
            q_cols_h = st.columns(5)
            new_qh = [
                int(q_cols_h[0].number_input(f"{casa} 1°Q", 0, 99, int(qh[0]), key=f"qh1_{match_id}")),
                int(q_cols_h[1].number_input(f"{casa} 2°Q", 0, 99, int(qh[1]), key=f"qh2_{match_id}")),
                int(q_cols_h[2].number_input(f"{casa} 3°Q", 0, 99, int(qh[2]), key=f"qh3_{match_id}")),
                int(q_cols_h[3].number_input(f"{casa} 4°Q", 0, 99, int(qh[3]), key=f"qh4_{match_id}")),
                int(q_cols_h[4].number_input(f"{casa} OT", 0, 99, ot_h, key=f"qhot_{match_id}")),
            ]
            q_cols_a = st.columns(5)
            new_qa = [
                int(q_cols_a[0].number_input(f"{trasferta} 1°Q", 0, 99, int(qa[0]), key=f"qa1_{match_id}")),
                int(q_cols_a[1].number_input(f"{trasferta} 2°Q", 0, 99, int(qa[1]), key=f"qa2_{match_id}")),
                int(q_cols_a[2].number_input(f"{trasferta} 3°Q", 0, 99, int(qa[2]), key=f"qa3_{match_id}")),
                int(q_cols_a[3].number_input(f"{trasferta} 4°Q", 0, 99, int(qa[3]), key=f"qa4_{match_id}")),
                int(q_cols_a[4].number_input(f"{trasferta} OT", 0, 99, ot_a, key=f"qaot_{match_id}")),
            ]

            editor_col_cfg = {
                "NUM": st.column_config.NumberColumn("#", min_value=0, max_value=99, step=1, format="%d"),
                "Giocatore": st.column_config.TextColumn("Giocatore"),
                "PUN": st.column_config.NumberColumn("PUN", min_value=0, max_value=150, step=1),
                "MIN": st.column_config.TextColumn("MIN"),
                "SF": st.column_config.CheckboxColumn("SF"),
                "F_C": st.column_config.NumberColumn("F_C", min_value=0, max_value=5, step=1),
                "2PT_R": st.column_config.NumberColumn("2PT_R", min_value=0, max_value=50, step=1),
                "3PT_R": st.column_config.NumberColumn("3PT_R", min_value=0, max_value=30, step=1),
                "TL_R": st.column_config.NumberColumn("TL_R", min_value=0, max_value=40, step=1),
                "TL_T": st.column_config.NumberColumn("TL_T", min_value=0, max_value=40, step=1),
            }

            st.markdown(f"**Tabellino {casa}**")
            home_df_init = _players_to_editor_df(detail["home_players"], full_stats=is_full_edit_match, min_rows=10)
            home_df_init["NUM"] = home_df_init["NUM"].apply(lambda x: int(x) if 0 <= int(x) <= 99 else None)
            edited_home_df = st.data_editor(
                home_df_init,
                num_rows="dynamic",
                use_container_width=True,
                column_config=editor_col_cfg,
                key=f"ed_home_tbl_{match_id}",
            )

            st.markdown(f"**Tabellino {trasferta}**")
            away_df_init = _players_to_editor_df(detail["away_players"], full_stats=is_full_edit_match, min_rows=10)
            away_df_init["NUM"] = away_df_init["NUM"].apply(lambda x: int(x) if 0 <= int(x) <= 99 else None)
            edited_away_df = st.data_editor(
                away_df_init,
                num_rows="dynamic",
                use_container_width=True,
                column_config=editor_col_cfg,
                key=f"ed_away_tbl_{match_id}",
            )

            if st.button("Salva Partita e Tabellino", key=f"save_all_{match_id}", type="primary"):
                ok_g, msg_g, new_ov = save_game_override_persistent(
                    match_id,
                    {
                        "Data": new_date.strip(),
                        "Stato": new_status,
                        "Punti_Casa": int(new_pts_h),
                        "Punti_Trasferta": int(new_pts_a),
                    },
                )
                st.session_state["game_overrides"] = new_ov

                detail_payload = {
                    "coach_home": coach_h.strip(),
                    "coach_away": coach_a.strip(),
                    "quarters_home": new_qh[:4],
                    "quarters_away": new_qa[:4],
                    "ot_home": int(new_qh[4]),
                    "ot_away": int(new_qa[4]),
                    "home_players": _editor_df_to_players(edited_home_df, existing_players=detail["home_players"]),
                    "away_players": _editor_df_to_players(edited_away_df, existing_players=detail["away_players"]),
                    "notes": detail.get("notes", ""),
                }
                ok_d, msg_d, new_store = save_match_detail_persistent(match_id, detail_payload)
                st.session_state["match_details_store"] = new_store

                if ok_g and ok_d:
                    st.success("Risultato e tabellino salvati in modo permanente!")
                else:
                    st.warning(f"{msg_g} | {msg_d}")
                st.rerun()


def _aggregate_team_season_players(team_name: str, games_df: pd.DataFrame) -> list[dict]:
    store = st.session_state.get("match_details_store", {})
    if not isinstance(store, dict):
        return []

    team_games = games_df[
        ((games_df["Casa"] == team_name) | (games_df["Trasferta"] == team_name))
        & (games_df["Stato"].astype(str).str.strip().str.lower() == "giocata")
    ].sort_values(by=["Giornata", "ID_Partita"])

    agg: dict[str, dict] = {}
    for g in team_games.itertuples(index=False):
        mid = str(g.ID_Partita)
        raw_det = store.get(mid)
        if not isinstance(raw_det, dict):
            continue
        is_home = str(g.Casa) == team_name
        raw_list = raw_det.get("home_players" if is_home else "away_players", [])
        players = _normalize_player_rows(raw_list)
        for p in players:
            raw_name = str(p["Giocatore"]).strip()
            if not raw_name:
                continue
            is_dnp = "(N.E.)" in raw_name.upper()
            clean_name = re.sub(r"\s*\(N\.E\.\)\s*$", "", raw_name, flags=re.IGNORECASE).strip()
            clean_name = re.sub(r"\s*\(K\)\s*$", "", clean_name, flags=re.IGNORECASE).strip()
            key = clean_name.lower()

            if key not in agg:
                agg[key] = {
                    "Giocatore": clean_name,
                    "NUM": 999,
                    "GP": 0,
                    "GS": 0,
                    "PUN": 0,
                    "MIN_SEC": 0,
                    "2PT_R": 0,
                    "2PT_T": 0,
                    "3PT_R": 0,
                    "3PT_T": 0,
                    "TL_R": 0,
                    "TL_T": 0,
                    "RIM_O": 0,
                    "RIM_D": 0,
                    "F_C": 0,
                    "F_S": 0,
                    "PAL_P": 0,
                    "PAL_R": 0,
                    "VAL": 0,
                }

            rec = agg[key]
            p_num = int(p.get("NUM", 999))
            if 0 <= p_num <= 99:
                rec["NUM"] = p_num

            if not is_dnp:
                rec["GP"] += 1
                if p.get("SF"):
                    rec["GS"] += 1
            rec["PUN"] += int(p["PUN"])
            rec["MIN_SEC"] += _parse_minutes_to_seconds(p["MIN"])
            rec["2PT_R"] += int(p["2PT_R"])
            rec["2PT_T"] += int(p["2PT_T"])
            rec["3PT_R"] += int(p["3PT_R"])
            rec["3PT_T"] += int(p["3PT_T"])
            rec["TL_R"] += int(p["TL_R"])
            rec["TL_T"] += int(p["TL_T"])
            rec["RIM_O"] += int(p["RIM_O"])
            rec["RIM_D"] += int(p["RIM_D"])
            rec["F_C"] += int(p["F_C"])
            rec["F_S"] += int(p["F_S"])
            rec["PAL_P"] += int(p["PAL_P"])
            rec["PAL_R"] += int(p["PAL_R"])
            rec["VAL"] += int(p["VAL"])

    rows = list(agg.values())
    rows.sort(
        key=lambda r: (
            int(r["NUM"]) if 0 <= int(r["NUM"]) <= 99 else 999,
            -int(r["PUN"]),
            str(r["Giocatore"]),
        )
    )
    return rows


TEAM_STATS_SORT_OPTIONS: dict[str, str] = {
    "Numero di maglia (#) (predefinito)": "DEFAULT",
    "Punti totali (PTS)": "PUN",
    "Media punti a partita (PPG)": "PPG",
    "Partite giocate (PG)": "GP",
    "Quintetti iniziali (SF)": "GS",
    "Minuti totali (MIN)": "MIN_SEC",
    "Tiri da 2 segnati (2PT R)": "2PT_R",
    "Tiri da 2 tentati (2PT T)": "2PT_T",
    "Tiri da 3 segnati (3PT R)": "3PT_R",
    "Tiri da 3 tentati (3PT T)": "3PT_T",
    "Tiri liberi segnati (TL R)": "TL_R",
    "Tiri liberi tentati (TL T)": "TL_T",
    "% Tiri liberi (TL %)": "TL_PCT",
    "Falli commessi (FC)": "F_C",
    "Falli subiti (FS)": "F_S",
    "Rimbalzi totali (RIM)": "RIM_T",
    "Palle recuperate (PR)": "PAL_R",
    "Palle perse (PP)": "PAL_P",
    "Valutazione Lega (VAL)": "VAL",
    "Nome Giocatore": "GIOCATORE",
}


def _sort_team_season_players(rows: list[dict], sort_key: str, descending: bool = True) -> list[dict]:
    if not rows or sort_key == "DEFAULT":
        return rows

    def _val_fn(r: dict):
        gp = int(r.get("GP", 0))
        if sort_key == "GIOCATORE":
            return str(r.get("Giocatore", "")).strip().lower()
        if sort_key == "PPG":
            return (int(r.get("PUN", 0)) / gp) if gp > 0 else 0.0
        if sort_key == "TL_PCT":
            att = int(r.get("TL_T", 0))
            return (int(r.get("TL_R", 0)) / att) if att > 0 else -1.0
        if sort_key == "RIM_T":
            return int(r.get("RIM_O", 0)) + int(r.get("RIM_D", 0))
        return int(r.get(sort_key, 0))

    return sorted(
        rows,
        key=lambda r: (_val_fn(r), str(r.get("Giocatore", "")).strip().lower()),
        reverse=descending,
    )


def render_team_page(team_name: str, games_df: pd.DataFrame, logo_html_map: dict[str, str]) -> None:
    st.markdown(MATCH_DETAIL_CSS + CALENDAR_CSS + TEAM_PAGE_CSS, unsafe_allow_html=True)

    girone = _find_team_girone(team_name)
    if not girone:
        st.error("Squadra non trovata.")
        if st.button("Torna a Classifica e Calendario", type="primary"):
            st.query_params.clear()
            st.rerun()
        return

    if st.button("← Torna a Classifica e Calendario", key="back_from_team"):
        st.query_params.clear()
        st.rerun()

    board = compute_standings(girone, games_df)
    pos = next((idx for idx, r in enumerate(board, start=1) if r["squadra"] == team_name), 1)
    row_stat = next(
        (r for r in board if r["squadra"] == team_name),
        {"p": 0, "w": 0, "l": 0, "pf": 0, "ps": 0, "diff": 0, "pts": 0, "streak_events": []},
    )

    logo_box = logo_html_map.get(f"hero::{team_name}", '<div class="md-logo-box">🏀</div>')
    st.markdown(
        f'<div class="team-hero">'
        f'{logo_box}'
        f'<div>'
        f'<div class="team-hero-title">{team_name}</div>'
        f'<div class="team-hero-sub">{girone} • {pos}° posto in classifica</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    diff_val = row_stat["diff"]
    diff_str = f"+{diff_val}" if diff_val > 0 else str(diff_val)
    ppg = f"{row_stat['pf'] / row_stat['p']:.1f}" if row_stat["p"] > 0 else "0.0"
    papg = f"{row_stat['ps'] / row_stat['p']:.1f}" if row_stat["p"] > 0 else "0.0"

    st.markdown(
        '<div class="kpi-grid">'
        f'<div class="kpi-card"><div class="kpi-label">Punti Classifica</div><div class="kpi-val">{row_stat["pts"]}</div></div>'
        f'<div class="kpi-card"><div class="kpi-label">Giocate</div><div class="kpi-val">{row_stat["p"]}</div></div>'
        f'<div class="kpi-card"><div class="kpi-label">Vinte</div><div class="kpi-val" style="color:#4ade80;">{row_stat["w"]}</div></div>'
        f'<div class="kpi-card"><div class="kpi-label">Perse</div><div class="kpi-val" style="color:#f87171;">{row_stat["l"]}</div></div>'
        f'<div class="kpi-card"><div class="kpi-label">Differenza</div><div class="kpi-val">{diff_str}</div></div>'
        f'<div class="kpi-card"><div class="kpi-label">Media Fatti</div><div class="kpi-val">{ppg}</div></div>'
        f'<div class="kpi-card"><div class="kpi-label">Media Subiti</div><div class="kpi-val">{papg}</div></div>'
        '</div>',
        unsafe_allow_html=True,
    )

    tab_cal, tab_stats = st.tabs(["CALENDARIO E RISULTATI", "STATISTICHE GIOCATORI"])

    with tab_cal:
        team_games = games_df[
            (games_df["Girone"] == girone)
            & ((games_df["Casa"] == team_name) | (games_df["Trasferta"] == team_name))
        ].sort_values(by=["Giornata", "ID_Partita"])

        st.subheader(f"Calendario Completo — {team_name}")
        st.caption("Clicca su una partita per aprire il dettaglio gara completo.")
        parts = [
            '<div class="cal-board">',
            '<div class="cal-board-head">'
            '<div class="c-left">GIORNATA</div>'
            '<div class="c-right">SQUADRA DI CASA</div>'
            '<div class="c-center">RISULTATO</div>'
            '<div class="c-left">SQUADRA OSPITE</div>'
            "</div>",
        ]
        for g in team_games.itertuples(index=False):
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
            g_num = int(g.Giornata)
            phase_lbl = "RITORNO" if g_num > 11 else "ANDATA"
            disp_g = g_num - 11 if g_num > 11 else g_num

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
                f'<div class="cal-round-league">{girone}</div>'
                f'<div class="cal-round-num">{disp_g}ª Giornata • {phase_lbl}</div>'
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
        st.markdown("".join(parts), unsafe_allow_html=True)

    with tab_stats:
        season_players = _aggregate_team_season_players(team_name, games_df)
        if not season_players:
            st.info("Nessun tabellino individuale disponibile finora per questa squadra.")
        else:
            ts1, ts2 = st.columns([3, 1.3])
            with ts1:
                sel_team_sort_lbl = st.selectbox(
                    "Ordina statistiche stagionali per",
                    options=list(TEAM_STATS_SORT_OPTIONS.keys()),
                    index=0,
                    key=f"team_stats_sort_col_{team_name}",
                )
            with ts2:
                default_dir_idx = 1 if TEAM_STATS_SORT_OPTIONS[sel_team_sort_lbl] in ("DEFAULT", "GIOCATORE") else 0
                sel_team_sort_dir = st.radio(
                    "Ordine",
                    options=["Decrescente", "Crescente"],
                    horizontal=True,
                    index=default_dir_idx,
                    key=f"team_stats_sort_dir_{team_name}",
                )

            t_sort_key = TEAM_STATS_SORT_OPTIONS[sel_team_sort_lbl]
            t_sort_desc = (sel_team_sort_dir == "Decrescente")
            sorted_season_players = _sort_team_season_players(
                season_players, sort_key=t_sort_key, descending=t_sort_desc
            )
            arrow_t = " ↓" if t_sort_desc else " ↑"

            def _t_th(label: str, key_name: str, extra_cls: str = "") -> str:
                is_act = (t_sort_key == key_name) or (t_sort_key == "DEFAULT" and key_name == "NUM")
                cls = f"{extra_cls} active-sort".strip() if is_act else extra_cls
                cls_attr = f' class="{cls}"' if cls else ""
                lbl = f"{label}{arrow_t}" if t_sort_key == key_name else label
                return f"<th{cls_attr}>{lbl}</th>"

            has_adv = any(
                (r["2PT_T"] > r["2PT_R"])
                or (r["3PT_T"] > r["3PT_R"])
                or (r["RIM_O"] + r["RIM_D"] > 0)
                or (r["F_S"] > 0)
                or (r["PAL_P"] + r["PAL_R"] > 0)
                or (r["VAL"] != 0)
                for r in sorted_season_players
            )

            s_html = [
                '<div class="tp-stats-card">',
                '<div class="tp-stats-head">'
                f'<span>Statistiche Stagionali Giocatori — {team_name}</span>'
                '<span style="font-size:11px;color:#fbbf24;">Cumulativo gare con tabellino</span>'
                '</div>',
                '<div class="tp-table-wrap"><table class="tp-stats-table"><thead><tr>',
                _t_th("#", "NUM"),
                _t_th("GIOCATORE", "GIOCATORE", "left-col"),
                _t_th("PG", "GP"),
                _t_th("SF", "GS"),
                _t_th("PTS", "PUN", "hi-col"),
                _t_th("PPG", "PPG", "hi-col"),
                _t_th("MIN", "MIN_SEC"),
                _t_th("2PT R", "2PT_R"),
            ]
            if has_adv:
                s_html.append(_t_th("2PT T", "2PT_T"))
            s_html.append(_t_th("3PT R", "3PT_R"))
            if has_adv:
                s_html.append(_t_th("3PT T", "3PT_T"))
            s_html.extend(
                [
                    _t_th("TL R", "TL_R"),
                    _t_th("TL T", "TL_T"),
                    _t_th("TL %", "TL_PCT", "hi-col"),
                    _t_th("FC", "F_C"),
                ]
            )
            if has_adv:
                s_html.extend(
                    [
                        _t_th("FS", "F_S"),
                        _t_th("RIM", "RIM_T"),
                        _t_th("PR", "PAL_R"),
                        _t_th("PP", "PAL_P"),
                        _t_th("VAL", "VAL"),
                    ]
                )
            s_html.append("</tr></thead><tbody>")

            for r in sorted_season_players:
                num_disp = _format_jersey_display(r.get("NUM"), empty_placeholder="—")
                gp = int(r["GP"])
                pts = int(r["PUN"])
                ppg_val = f"{pts / gp:.1f}" if gp > 0 else "0.0"
                tot_mins = int(round(r["MIN_SEC"] / 60.0))
                min_disp = str(tot_mins) if tot_mins > 0 else "-"
                rim_tot = int(r["RIM_O"]) + int(r["RIM_D"])

                s_html.append(
                    "<tr>"
                    f'<td class="num-col">{num_disp}</td>'
                    f'<td class="name-col">{r["Giocatore"]}</td>'
                    f"<td>{gp}</td>"
                    f"<td>{int(r['GS'])}</td>"
                    f'<td class="pts-col">{pts}</td>'
                    f'<td class="pts-col">{ppg_val}</td>'
                    f"<td>{min_disp}</td>"
                    f"<td>{int(r['2PT_R'])}</td>"
                )
                if has_adv:
                    s_html.append(f"<td>{int(r['2PT_T'])}</td>")
                s_html.append(f"<td>{int(r['3PT_R'])}</td>")
                if has_adv:
                    s_html.append(f"<td>{int(r['3PT_T'])}</td>")
                s_html.extend(
                    [
                        f"<td>{int(r['TL_R'])}</td>",
                        f"<td>{int(r['TL_T'])}</td>",
                        f'<td class="pts-col">{_fmt_pct(int(r["TL_R"]), int(r["TL_T"]))}</td>',
                        f"<td>{int(r['F_C'])}</td>",
                    ]
                )
                if has_adv:
                    s_html.extend(
                        [
                            f"<td>{int(r['F_S'])}</td>",
                            f"<td>{rim_tot}</td>",
                            f"<td>{int(r['PAL_R'])}</td>",
                            f"<td>{int(r['PAL_P'])}</td>",
                            f"<td>{int(r['VAL'])}</td>",
                        ]
                    )
                s_html.append("</tr>")

            s_html.append("</tbody></table></div></div>")
            st.markdown("".join(s_html), unsafe_allow_html=True)


def main() -> None:
    st.markdown(GLOBAL_UI_CSS, unsafe_allow_html=True)

    if "match_details_store" not in st.session_state:
        st.session_state["match_details_store"] = load_match_details_store()

    games_df = load_full_games_df()
    logo_html_map = build_team_logo_html_map(GITHUB_RAW_BASE)

    query_params = st.query_params
    selected_match = query_params.get("match", None)
    selected_team = query_params.get("team", None)

    st.markdown(
        '<div class="topbar-card">'
        '<div class="topbar-title">🏀 Campionati Regionali Maschili — DR2 Puglia 2026/2027</div>'
        '<div class="topbar-sub">Gironi A • B • C — Classifiche, Calendario Giornate e Schede Squadra</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    if selected_match:
        render_match_detail_page(str(selected_match), games_df, logo_html_map)
        return

    if selected_team:
        render_team_page(str(selected_team), games_df, logo_html_map)
        return

    with st.sidebar:
        st.header("Navigazione")
        selected_girone = st.selectbox(
            "Seleziona Girone",
            ["Girone A", "Girone B", "Girone C"],
            index=0,
        )
        st.divider()
        st.caption(f"Squadra di riferimento: **{OUR_TEAM}**")
        st.caption(f"Versione dati: `{DATA_VERSION}`")

    tab_classifica, tab_calendario, tab_squadre = st.tabs(
        ["🏆 CLASSIFICA", "📅 CALENDARIO E RISULTATI", "🛡️ SQUADRE"]
    )

    with tab_classifica:
        standings_rows = compute_standings(selected_girone, games_df)
        thirds_board = compute_thirds_standings(games_df)
        render_standings(selected_girone, standings_rows, thirds_board, logo_html_map)

    with tab_calendario:
        st.markdown(CALENDAR_CSS, unsafe_allow_html=True)
        st.subheader(f"Calendario e Risultati — {selected_girone}")

        g_df = games_df[games_df["Girone"] == selected_girone].copy()
        teams_in_girone = sorted([t["squadra"] for t in GIRONI_TEAMS[selected_girone]])
        all_rounds = sorted(g_df["Giornata"].unique().tolist())

        round_labels_map = {
            f"{(r - 11 if r > 11 else r)}ª Giornata • {'Ritorno' if r > 11 else 'Andata'}": r
            for r in all_rounds
        }

        st.markdown(
            f'<div class="cal-filter-banner">'
            f'<div>'
            f'<div class="cal-filter-title">Filtri Partite e Giornate</div>'
            f'<div class="cal-filter-sub">Seleziona una o più giornate oppure filtra per singole squadre del {selected_girone}.</div>'
            f'</div>'
            f'<div class="cal-filter-pills">'
            f'<span class="cal-pill">Gare totali: <span>{len(g_df)}</span></span>'
            f'<span class="cal-pill">Giocate: <span>{int((g_df["Stato"].astype(str).str.strip().str.lower() == "giocata").sum())}</span></span>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        f_col1, f_col2 = st.columns(2)
        with f_col1:
            sel_round_labels = st.multiselect(
                "Filtra per Giornata",
                options=list(round_labels_map.keys()),
                default=[],
                placeholder="Tutte le giornate (Andata e Ritorno)",
                key=f"cal_filter_rounds_{selected_girone}",
            )
        with f_col2:
            sel_teams = st.multiselect(
                "Filtra per Squadra",
                options=teams_in_girone,
                default=[],
                placeholder="Tutte le squadre del girone",
                key=f"cal_filter_teams_{selected_girone}",
            )

        selected_rounds = [round_labels_map[lbl] for lbl in sel_round_labels]
        if selected_rounds:
            g_df = g_df[g_df["Giornata"].isin(selected_rounds)]
        if sel_teams:
            g_df = g_df[g_df["Casa"].isin(sel_teams) | g_df["Trasferta"].isin(sel_teams)]

        if selected_rounds or sel_teams:
            st.caption(f"Visualizzate **{len(g_df)}** partite corrispondenti ai filtri selezionati.")

        tab_andata, tab_ritorno = st.tabs(["ANDATA (Giornate 1-11)", "RITORNO (Giornate 12-22)"])

        with tab_andata:
            st.markdown('<div class="cal-phase-hdr">FASE DI ANDATA — Giornate 1 - 11</div>', unsafe_allow_html=True)
            andata_rounds = sorted([r for r in g_df["Giornata"].unique().tolist() if r <= 11])
            if not andata_rounds:
                st.info("Nessuna partita di andata corrisponde ai filtri selezionati.")
            else:
                for r_num in andata_rounds:
                    r_games = g_df[g_df["Giornata"] == r_num].sort_values(by=["ID_Partita"])
                    st.markdown(
                        build_round_html(r_num, r_games, logo_html_map, is_ritorno=False, girone_label=selected_girone),
                        unsafe_allow_html=True,
                    )

        with tab_ritorno:
            st.markdown('<div class="cal-phase-hdr">FASE DI RITORNO — Giornate 12 - 22</div>', unsafe_allow_html=True)
            ritorno_rounds = sorted([r for r in g_df["Giornata"].unique().tolist() if r > 11])
            if not ritorno_rounds:
                st.info("Nessuna partita di ritorno corrisponde ai filtri selezionati.")
            else:
                for r_num in ritorno_rounds:
                    r_games = g_df[g_df["Giornata"] == r_num].sort_values(by=["ID_Partita"])
                    st.markdown(
                        build_round_html(r_num, r_games, logo_html_map, is_ritorno=True, girone_label=selected_girone),
                        unsafe_allow_html=True,
                    )

    with tab_squadre:
        render_teams_grid(selected_girone, games_df, logo_html_map)


if __name__ == "__main__":
    main()
