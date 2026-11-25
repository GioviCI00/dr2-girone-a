import base64
import json
import os
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
DATA_VERSION = "2026-11-25-v4-boxscore"
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


def _p_row(
    giocatore: str,
    pts: int = 0,
    tl_seg: int = 0,
    tl_sbag: int = 0,
    pt2: int = 0,
    pt3: int = 0,
    falli: int = 0,
    quintetto: bool = False,
    minuti: str = "",
) -> dict:
    return {
        "Giocatore": giocatore,
        "MIN": minuti,
        "PTS": int(pts),
        "TL_SEG": int(tl_seg),
        "TL_SBAG": int(tl_sbag),
        "2PT": int(pt2),
        "3PT": int(pt3),
        "FALLI": int(falli),
        "QUINTETTO": bool(quintetto),
    }


DEFAULT_ROUND3_DETAILS: dict[str, dict] = {
    "A03_1880": {
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
            _p_row("Provaroni F.", pts=3, tl_seg=0, tl_sbag=0, pt2=0, pt3=1, falli=1, quintetto=True, minuti="13:03"),
            _p_row("Derosa L.", pts=23, tl_seg=9, tl_sbag=3, pt2=7, pt3=0, falli=4, quintetto=True, minuti="35:42"),
            _p_row("Desiante V.", pts=5, tl_seg=0, tl_sbag=0, pt2=1, pt3=1, falli=3, quintetto=False, minuti="15:24"),
            _p_row("D'Erasmo F.", pts=15, tl_seg=7, tl_sbag=3, pt2=4, pt3=0, falli=4, quintetto=True, minuti="30:18"),
            _p_row("Housni Z.", pts=9, tl_seg=1, tl_sbag=2, pt2=4, pt3=0, falli=2, quintetto=True, minuti="36:17"),
            _p_row("Silletti D.", pts=8, tl_seg=2, tl_sbag=0, pt2=0, pt3=2, falli=3, quintetto=False, minuti="30:33"),
            _p_row("Micunco M.", pts=2, tl_seg=0, tl_sbag=0, pt2=1, pt3=0, falli=2, quintetto=False, minuti="02:27"),
            _p_row("Colangelo A.", pts=12, tl_seg=3, tl_sbag=0, pt2=3, pt3=1, falli=4, quintetto=True, minuti="29:52"),
            _p_row("Dario Iacobone", pts=0, tl_seg=0, tl_sbag=0, pt2=0, pt3=0, falli=1, quintetto=False, minuti="03:53"),
            _p_row("Fraccalvieri A.", pts=0, tl_seg=0, tl_sbag=0, pt2=0, pt3=0, falli=1, quintetto=False, minuti="02:31"),
            _p_row("Antonio Vero (N.E.)", pts=0),
            _p_row("Gianpiero Calabrese (N.E.)", pts=0),
        ],
    },
    "A03_1877": {
        "quarters_home": [21, 13, 28, 24],
        "quarters_away": [17, 23, 14, 21],
        "ot_home": 0,
        "ot_away": 0,
        "home_players": [
            _p_row("Ruotolo A.", pts=15),
            _p_row("Mastromarco P.", pts=2),
            _p_row("Mariani G.", pts=25, pt3=4),
            _p_row("Natali F.", pts=1),
            _p_row("Ruotolo L.", pts=19, pt3=3),
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
        "quarters_home": [19, 23, 24, 12],
        "quarters_away": [20, 12, 23, 20],
        "ot_home": 0,
        "ot_away": 0,
        "home_players": [
            _p_row("Centrone L.", pts=10),
            _p_row("Iacovelli A.", pts=15),
            _p_row("Panessa A.", pts=6),
            _p_row("Rutigliano A.", pts=3),
            _p_row("Maietta G.", pts=17, pt3=5),
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
            _p_row("Scarponi I.", pts=23, pt3=6),
        ],
    },
    "A03_1878": {
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
# PERSISTENZA SU GITHUB (modifiche_partita.json & dettagli_partite.json)
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
    grid-template-columns: 54px 52px 1fr 52px 52px 52px 68px 156px 64px;
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
    grid-template-columns: 54px 52px 1fr 52px 52px 52px 68px 156px 64px;
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
a.team-link {
    color: #ffffff !important;
    text-decoration: none !important;
    font-weight: 800;
    font-size: 14px;
    text-transform: uppercase;
}
a.team-link:hover {
    color: #ffd43b !important;
    text-decoration: underline !important;
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
.streak-track {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: #0d1218;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 8px;
    padding: 4px 12px 4px 6px;
    min-width: 122px;
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
    color: #ffd43b;
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
a.cal-match-link {
    text-decoration: none !important;
    color: inherit !important;
    display: block;
}
.cal-match {
    display: grid;
    grid-template-columns: 96px 1fr 48px;
    gap: 10px;
    align-items: center;
    padding: 9px 14px;
    border-bottom: 1px solid #20252e;
    transition: background 0.14s ease;
    cursor: pointer;
}
.cal-match:hover {
    background: #1d232d;
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

MATCH_DETAIL_CSS = """
<style>
.md-hero {
    background: linear-gradient(180deg, #061b26 0%, #092635 100%);
    border: 1px solid #163b4e;
    border-radius: 14px;
    padding: 24px 20px;
    margin-bottom: 14px;
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
    width: 76px;
    height: 76px;
    background: #ffffff;
    border-radius: 16px;
    padding: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 6px 18px rgba(0,0,0,0.35);
}
.md-logo-box img {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
}
.md-team-name {
    font-size: 16px;
    font-weight: 800;
    color: #f8fafc;
}
.md-center {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
}
.md-date {
    font-size: 13px;
    font-weight: 700;
    color: #cbd5e1;
}
.md-score {
    font-size: 46px;
    font-weight: 900;
    color: #ffffff;
    letter-spacing: 2px;
    line-height: 1.1;
}
.md-status {
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 1.2px;
    color: #94a3b8;
    text-transform: uppercase;
}
.md-sec-card {
    background: #071922;
    border: 1px solid #133343;
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 14px;
}
.md-sec-title {
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 0.7px;
    text-transform: uppercase;
    color: #e2e8f0;
    margin-bottom: 12px;
}
.md-res-table {
    width: 100%;
    border-collapse: collapse;
    color: #e2e8f0;
    font-size: 14px;
}
.md-res-table th {
    text-align: center;
    color: #94a3b8;
    font-size: 12px;
    padding: 6px 10px;
    border-bottom: 1px solid #163b4e;
}
.md-res-table th.team-col, .md-res-table td.team-col {
    text-align: left;
    font-weight: 700;
}
.md-res-table td {
    text-align: center;
    padding: 10px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}
.md-res-table td.tot-col {
    font-weight: 900;
    color: #ffffff;
}
.team-hero {
    background: linear-gradient(135deg, #072238 0%, #0d4b84 100%);
    border: 1px solid rgba(255,255,255,0.16);
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 18px;
}
.team-hero-title {
    font-size: 24px;
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
    background: #0e1a2b;
    border: 1px solid rgba(255,255,255,0.12);
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
    color: #ffd43b;
    margin-top: 2px;
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
    st.caption("Clicca sul nome di una squadra per aprire la scheda squadra con riepilogo e statistiche giocatori.")
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
            gid_encoded = quote(str(g.ID_Partita), safe="")
            is_played = str(g.Stato).strip().lower() == "giocata"
            tokens = str(g.Data).strip().split()
            if len(tokens) >= 3:
                date_str, time_str = tokens[1], tokens[2]
            elif len(tokens) == 2:
                date_str, time_str = tokens[0], tokens[1]
            else:
                date_str, time_str = str(g.Data).strip(), ""

            meta_sub = '<div class="cal-ft">FINALE</div>' if is_played else f'<div class="cal-time">{time_str}</div>'

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
                f'<a class="cal-match-link" href="?match={gid_encoded}" target="_self">'
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
                f'</a>'
            )

    parts.append("</div>")
    return "".join(parts)


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
        out.append(
            {
                "Giocatore": name,
                "MIN": str(item.get("MIN", "")).strip(),
                "PTS": int(pd.to_numeric(item.get("PTS", 0), errors="coerce") or 0),
                "TL_SEG": int(pd.to_numeric(item.get("TL_SEG", 0), errors="coerce") or 0),
                "TL_SBAG": int(pd.to_numeric(item.get("TL_SBAG", 0), errors="coerce") or 0),
                "2PT": int(pd.to_numeric(item.get("2PT", 0), errors="coerce") or 0),
                "3PT": int(pd.to_numeric(item.get("3PT", 0), errors="coerce") or 0),
                "FALLI": int(pd.to_numeric(item.get("FALLI", 0), errors="coerce") or 0),
                "QUINTETTO": bool(item.get("QUINTETTO", False)),
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
            "quarters_home": [int(x) for x in qh],
            "quarters_away": [int(x) for x in qa],
            "ot_home": int(raw.get("ot_home", 0) or 0),
            "ot_away": int(raw.get("ot_away", 0) or 0),
            "home_players": _normalize_player_rows(raw.get("home_players")),
            "away_players": _normalize_player_rows(raw.get("away_players")),
            "video_url": str(raw.get("video_url", "") or ""),
            "notes": str(raw.get("notes", "") or ""),
        }

    return {
        "quarters_home": [0, 0, 0, 0],
        "quarters_away": [0, 0, 0, 0],
        "ot_home": 0,
        "ot_away": 0,
        "home_players": [],
        "away_players": [],
        "video_url": "",
        "notes": "",
    }


def _players_to_editor_df(player_list: list[dict], min_rows: int = 8) -> pd.DataFrame:
    rows = _normalize_player_rows(player_list)
    while len(rows) < min_rows:
        rows.append(_p_row(""))
    return pd.DataFrame(rows)


def _editor_df_to_players(df: pd.DataFrame) -> list[dict]:
    if df is None or df.empty:
        return []
    out: list[dict] = []
    for r in df.itertuples(index=False):
        name = str(getattr(r, "Giocatore", "") or "").strip()
        if not name:
            continue
        out.append(
            _p_row(
                giocatore=name,
                minuti=str(getattr(r, "MIN", "") or "").strip(),
                pts=int(pd.to_numeric(getattr(r, "PTS", 0), errors="coerce") or 0),
                tl_seg=int(pd.to_numeric(getattr(r, "TL_SEG", 0), errors="coerce") or 0),
                tl_sbag=int(pd.to_numeric(getattr(r, "TL_SBAG", 0), errors="coerce") or 0),
                pt2=int(
                    pd.to_numeric(
                        getattr(r, "2PT") if hasattr(r, "2PT") else getattr(r, "_5", 0),
                        errors="coerce",
                    )
                    or 0
                ),
                pt3=int(
                    pd.to_numeric(
                        getattr(r, "3PT") if hasattr(r, "3PT") else getattr(r, "_6", 0),
                        errors="coerce",
                    )
                    or 0
                ),
                falli=int(pd.to_numeric(getattr(r, "FALLI", 0), errors="coerce") or 0),
                quintetto=bool(getattr(r, "QUINTETTO", False)),
            )
        )
    return out


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
        plist = det["home_players"] if str(g.Casa) == team_name else det["away_players"]
        for p in plist:
            raw_name = str(p.get("Giocatore", "")).strip()
            if not raw_name:
                continue
            key = raw_name.lower()
            if key not in agg:
                agg[key] = {
                    "Giocatore": raw_name,
                    "G": 0,
                    "PTS": 0,
                    "TL_SEG": 0,
                    "TL_SBAG": 0,
                    "2PT": 0,
                    "3PT": 0,
                    "FALLI": 0,
                }
            agg[key]["G"] += 1
            agg[key]["PTS"] += int(p.get("PTS", 0))
            agg[key]["TL_SEG"] += int(p.get("TL_SEG", 0))
            agg[key]["TL_SBAG"] += int(p.get("TL_SBAG", 0))
            agg[key]["2PT"] += int(p.get("2PT", 0))
            agg[key]["3PT"] += int(p.get("3PT", 0))
            agg[key]["FALLI"] += int(p.get("FALLI", 0))

    if not agg:
        return pd.DataFrame(columns=["Giocatore", "G", "PTS", "PPG", "TL_SEG", "TL_SBAG", "2PT", "3PT", "FALLI"])

    rows = []
    for item in agg.values():
        g_cnt = max(int(item["G"]), 1)
        rows.append(
            {
                "Giocatore": item["Giocatore"],
                "G": item["G"],
                "PTS": item["PTS"],
                "PPG": round(item["PTS"] / g_cnt, 1),
                "TL_SEG": item["TL_SEG"],
                "TL_SBAG": item["TL_SBAG"],
                "2PT": item["2PT"],
                "3PT": item["3PT"],
                "FALLI": item["FALLI"],
            }
        )
    return pd.DataFrame(rows).sort_values(by=["PTS", "Giocatore"], ascending=[False, True]).reset_index(drop=True)


def render_team_page(team_name: str, games_df: pd.DataFrame, logo_html_map: dict[str, str]) -> None:
    st.markdown(MATCH_DETAIL_CSS, unsafe_allow_html=True)

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
        f'<div class="team-hero">'
        f'{hero_logo}'
        f'<div>'
        f'<div class="team-hero-title">{team_name}</div>'
        f'<div class="team-hero-sub">{girone} • Posizione attuale: #{pos}</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    if t_row:
        st.markdown(
            f'<div class="kpi-grid">'
            f'<div class="kpi-card"><div class="kpi-label">Punti</div><div class="kpi-val">{t_row["pts"]}</div></div>'
            f'<div class="kpi-card"><div class="kpi-label">Giocate</div><div class="kpi-val">{t_row["p"]}</div></div>'
            f'<div class="kpi-card"><div class="kpi-label">Vittorie</div><div class="kpi-val">{t_row["w"]}</div></div>'
            f'<div class="kpi-card"><div class="kpi-label">Sconfitte</div><div class="kpi-val">{t_row["l"]}</div></div>'
            f'<div class="kpi-card"><div class="kpi-label">PF / PS</div><div class="kpi-val">{t_row["pf"]}/{t_row["ps"]}</div></div>'
            f'<div class="kpi-card"><div class="kpi-label">Diff</div><div class="kpi-val">{diff_str}</div></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown("**Forma recente (Streak):**")
        st.markdown(_render_streak_html(t_row.get("streak_events", [])), unsafe_allow_html=True)

    st.subheader("Statistiche Giocatori (da tabellini partita)")
    p_df = compute_team_player_stats(team_name, games_df)
    if p_df.empty:
        st.info("Nessun tabellino inserito ancora per questa squadra.")
    else:
        st.dataframe(p_df, use_container_width=True, hide_index=True)

    st.subheader("Calendario e Risultati Squadra")
    team_games = games_df[(games_df["Casa"] == team_name) | (games_df["Trasferta"] == team_name)].sort_values(
        by=["Giornata", "ID_Partita"]
    )
    for g in team_games.itertuples(index=False):
        is_played = str(g.Stato).strip().lower() == "giocata"
        score_txt = f"{int(g.Punti_Casa)} - {int(g.Punti_Trasferta)}" if is_played else str(g.Data)
        c_a, c_b = st.columns([4, 1])
        c_a.markdown(f"**Giornata {int(g.Giornata)}** — {g.Casa} vs {g.Trasferta} ({score_txt})")
        if c_b.button("Apri gara", key=f"open_team_game_{g.ID_Partita}"):
            st.session_state["selected_team_name"] = None
            if "team" in st.query_params:
                del st.query_params["team"]
            st.session_state["selected_match_id"] = str(g.ID_Partita)
            st.query_params["match"] = str(g.ID_Partita)
            st.rerun()


def render_match_detail(match_id: str, games_df: pd.DataFrame, logo_html_map: dict[str, str]) -> None:
    st.markdown(MATCH_DETAIL_CSS, unsafe_allow_html=True)

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
    is_played = str(g["Stato"]).strip().lower() == "giocata"
    status_label = "FINALE" if is_played else str(g["Stato"]).upper()

    h_hero_logo = logo_html_map.get(f"hero::{home_name}", '<div class="md-logo-box">🏀</div>')
    a_hero_logo = logo_html_map.get(f"hero::{away_name}", '<div class="md-logo-box">🏀</div>')

    score_text = f"{home_pts} - {away_pts}" if is_played else "VS"

    st.markdown(
        f'<div class="md-hero">'
        f'<div class="md-grid">'
        f'<div class="md-team-block">{h_hero_logo}<div class="md-team-name">{home_name}</div></div>'
        f'<div class="md-center">'
        f'<div class="md-date">{g["Data"]} • {g["Girone"]} (Giornata {int(g["Giornata"])})</div>'
        f'<div class="md-score">{score_text}</div>'
        f'<div class="md-status">{status_label}</div>'
        f'</div>'
        f'<div class="md-team-block">{a_hero_logo}<div class="md-team-name">{away_name}</div></div>'
        f'</div>'
        f'</div>',
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
                        st.rerun()
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
        ("RIASSUNTO", "STATS GIOCATORE", "STATISTICHE", "FORMAZIONI", "CRONOLOGIA DELL'INCONTRO"),
        horizontal=True,
        label_visibility="collapsed",
        key=f"md_tab_{match_id}",
    )

    if sezioni_gara == "RIASSUNTO":
        col_vid, col_res = st.columns([1.15, 1.35])
        with col_vid:
            st.markdown('<div class="md-sec-card"><div class="md-sec-title">HIGHLIGHTS / VIDEO</div>', unsafe_allow_html=True)
            if detail["video_url"].strip():
                st.video(detail["video_url"].strip())
            else:
                st.info("Nessun video collegato per questa gara. Puoi inserire qui sotto il link YouTube.")
            new_vid = st.text_input("Link YouTube Highlights", value=detail["video_url"], key=f"vid_input_{match_id}")
            if st.button("Salva link video", key=f"save_vid_{match_id}"):
                new_detail = dict(detail)
                new_detail["video_url"] = new_vid.strip()
                ok, msg, store = save_match_detail_persistent(match_id, new_detail)
                st.session_state["match_details_store"] = store
                st.session_state["flash_msg"] = ("success" if ok else "warning", msg)
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        with col_res:
            q_h = detail["quarters_home"]
            q_a = detail["quarters_away"]
            ot_h = int(detail.get("ot_home", 0))
            ot_a = int(detail.get("ot_away", 0))
            has_ot = (ot_h > 0 or ot_a > 0)
            ot_th = "<th>OT</th>" if has_ot else ""
            ot_td_h = f"<td>{ot_h}</td>" if has_ot else ""
            ot_td_a = f"<td>{ot_a}</td>" if has_ot else ""

            st.markdown(
                f'<div class="md-sec-card">'
                f'<div class="md-sec-title">RISULTATO</div>'
                f'<table class="md-res-table">'
                f'<thead><tr><th class="team-col">SQUADRA</th><th>TOT</th><th>Q1</th><th>Q2</th><th>Q3</th><th>Q4</th>{ot_th}</tr></thead>'
                f'<tbody>'
                f'<tr><td class="team-col">{home_name}</td><td class="tot-col">{home_pts}</td><td>{q_h[0]}</td><td>{q_h[1]}</td><td>{q_h[2]}</td><td>{q_h[3]}</td>{ot_td_h}</tr>'
                f'<tr><td class="team-col">{away_name}</td><td class="tot-col">{away_pts}</td><td>{q_a[0]}</td><td>{q_a[1]}</td><td>{q_a[2]}</td><td>{q_a[3]}</td>{ot_td_a}</tr>'
                f'</tbody></table></div>',
                unsafe_allow_html=True,
            )
            with st.expander("Modifica parziali quarti"):
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

    elif sezioni_gara == "STATS GIOCATORE":
        st.markdown('<div class="md-sec-card"><div class="md-sec-title">TABELLINI GIOCATORI (MODIFICABILI)</div>', unsafe_allow_html=True)
        st.caption("I campi non ancora compilati partono a 0. Modifica direttamente le celle e salva per aggiornare squadra e persistenza.")

        tab_h, tab_a = st.tabs([home_name, away_name])
        with tab_h:
            edited_h = st.data_editor(
                _players_to_editor_df(detail["home_players"]),
                num_rows="dynamic",
                use_container_width=True,
                key=f"editor_h_{match_id}",
            )
        with tab_a:
            edited_a = st.data_editor(
                _players_to_editor_df(detail["away_players"]),
                num_rows="dynamic",
                use_container_width=True,
                key=f"editor_a_{match_id}",
            )

        if st.button("💾 Salva tabellini giocatori per sempre", key=f"save_box_{match_id}"):
            new_detail = dict(detail)
            new_detail["home_players"] = _editor_df_to_players(edited_h)
            new_detail["away_players"] = _editor_df_to_players(edited_a)
            with st.spinner("Salvataggio tabellini su GitHub..."):
                ok, msg, store = save_match_detail_persistent(match_id, new_detail)
            st.session_state["match_details_store"] = store
            st.session_state["flash_msg"] = ("success" if ok else "warning", msg)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    elif sezioni_gara == "STATISTICHE":
        st.markdown('<div class="md-sec-card"><div class="md-sec-title">STATISTICHE DI SQUADRA</div>', unsafe_allow_html=True)
        hp = detail["home_players"]
        ap = detail["away_players"]
        tot_pts_h = sum(int(p.get("PTS", 0)) for p in hp)
        tot_pts_a = sum(int(p.get("PTS", 0)) for p in ap)
        tot_3pt_h = sum(int(p.get("3PT", 0)) for p in hp)
        tot_3pt_a = sum(int(p.get("3PT", 0)) for p in ap)
        tot_tl_seg_h = sum(int(p.get("TL_SEG", 0)) for p in hp)
        tot_tl_seg_a = sum(int(p.get("TL_SEG", 0)) for p in ap)
        tot_falli_h = sum(int(p.get("FALLI", 0)) for p in hp)
        tot_falli_a = sum(int(p.get("FALLI", 0)) for p in ap)

        st.table(
            pd.DataFrame(
                [
                    {"Statistica": "Punti (Tabellino / Referto)", home_name: f"{tot_pts_h} ({home_pts})", away_name: f"{tot_pts_a} ({away_pts})"},
                    {"Statistica": "Triple segnate (3PT)", home_name: tot_3pt_h, away_name: tot_3pt_a},
                    {"Statistica": "Tiri liberi segnati (TL_SEG)", home_name: tot_tl_seg_h, away_name: tot_tl_seg_a},
                    {"Statistica": "Falli totali", home_name: tot_falli_h, away_name: tot_falli_a},
                ]
            )
        )
        st.markdown("</div>", unsafe_allow_html=True)

    elif sezioni_gara == "FORMAZIONI":
        st.markdown('<div class="md-sec-card"><div class="md-sec-title">FORMAZIONI / ROSTER INSERITI</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**{home_name}**")
            players_h = [str(p.get("Giocatore", "")).strip() for p in detail["home_players"] if str(p.get("Giocatore", "")).strip()]
            st.write(", ".join(players_h) if players_h else "Nessun giocatore ancora inserito nel tabellino.")
        with c2:
            st.markdown(f"**{away_name}**")
            players_a = [str(p.get("Giocatore", "")).strip() for p in detail["away_players"] if str(p.get("Giocatore", "")).strip()]
            st.write(", ".join(players_a) if players_a else "Nessun giocatore ancora inserito nel tabellino.")
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.markdown('<div class="md-sec-card"><div class="md-sec-title">CRONOLOGIA DELL\'INCONTRO / NOTE</div>', unsafe_allow_html=True)
        new_notes = st.text_area(
            "Momenti chiave, parziali o note cronaca gara",
            value=detail["notes"],
            height=140,
            key=f"notes_{match_id}",
        )
        if st.button("Salva cronologia / note su GitHub", key=f"save_notes_{match_id}"):
            new_detail = dict(detail)
            new_detail["notes"] = new_notes
            ok, msg, store = save_match_detail_persistent(match_id, new_detail)
            st.session_state["match_details_store"] = store
            st.session_state["flash_msg"] = ("success" if ok else "warning", msg)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


def render_calendar_page(games_df: pd.DataFrame, logo_html_map: dict[str, str]) -> pd.DataFrame:
    st.markdown(CALENDAR_CSS, unsafe_allow_html=True)
    st.title("Calendario e Risultati")
    st.caption("Seleziona il girone e il turno. Clicca su una partita per modificare data/ora o inserire il risultato.")

    gironi_list = ("Girone A", "Girone B", "Girone C")
    current_idx = gironi_list.index(st.session_state["calendar_girone"])
    girone = st.selectbox("Filtra per Girone", gironi_list, index=current_idx, key="cal_girone_select")
    st.session_state["calendar_girone"] = girone

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

if "match_details_store" not in st.session_state:
    st.session_state["match_details_store"] = load_match_details_store()

if st.session_state.get("games_df_version") != DATA_VERSION or "games_df" not in st.session_state:
    st.session_state["games_df"] = load_full_games_df()
    st.session_state["games_df_version"] = DATA_VERSION

if "calendar_girone" not in st.session_state:
    st.session_state["calendar_girone"] = "Girone A"

if "selected_match_id" not in st.session_state:
    st.session_state["selected_match_id"] = None

if "selected_team_name" not in st.session_state:
    st.session_state["selected_team_name"] = None

query_match = st.query_params.get("match")
if query_match:
    st.session_state["selected_match_id"] = str(query_match)
    st.session_state["selected_team_name"] = None

query_team = st.query_params.get("team")
if query_team and not query_match:
    st.session_state["selected_team_name"] = str(query_team)
    st.session_state["selected_match_id"] = None

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
    sezione = st.radio(
        "Sezione",
        ("Classifiche", "Calendario e Risultati"),
        key="nav_sezione",
        on_change=lambda: (
            st.session_state.update({"selected_match_id": None, "selected_team_name": None}),
            st.query_params.pop("match", None),
            st.query_params.pop("team", None),
        ),
    )
    if st.button("🔄 Ricarica dati salvati"):
        st.session_state["match_details_store"] = load_match_details_store()
        st.session_state["games_df"] = load_full_games_df()
        st.session_state["games_df_version"] = DATA_VERSION
        st.rerun()

    cfg_status = _get_github_config()
    if cfg_status["token"]:
        st.caption(f"☁️ Salvataggio permanente attivo ({cfg_status['owner']}/{cfg_status['repo']})")
    else:
        st.warning("Token GitHub non configurato nei Secrets: le modifiche non sopravvivono al riavvio del server.")

    if st.button("Esci"):
        st.session_state.authenticated = False
        st.session_state["selected_match_id"] = None
        st.session_state["selected_team_name"] = None
        if "match" in st.query_params:
            del st.query_params["match"]
        if "team" in st.query_params:
            del st.query_params["team"]
        st.rerun()

logo_html_map = build_team_logo_html_map(GITHUB_RAW_BASE)

if st.session_state["selected_match_id"]:
    render_match_detail(st.session_state["selected_match_id"], st.session_state["games_df"], logo_html_map)
elif st.session_state["selected_team_name"]:
    render_team_page(st.session_state["selected_team_name"], st.session_state["games_df"], logo_html_map)
elif sezione == "Classifiche":
    girone_classifica = st.selectbox("Seleziona Girone", ("Girone A", "Girone B", "Girone C"))
    classifica = compute_standings(girone_classifica, st.session_state["games_df"])
    terze_classificate = compute_thirds_standings(st.session_state["games_df"])
    render_standings(girone_classifica, classifica, terze_classificate, logo_html_map)
else:
    render_calendar_page(st.session_state["games_df"], logo_html_map)
