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

DATA_DIR = Path("data_dr2")
DATA_DIR.mkdir(exist_ok=True)

TEAMS_FILE = DATA_DIR / "squadre.csv"
GAMES_FILE = DATA_DIR / "partite.csv"
BOX_FILE = DATA_DIR / "tabellini.csv"

DEFAULT_TEAMS = [
    # Girone A (11 squadre)
    {"Girone": "Girone A", "Squadra": "ASD MAGIC BARI", "Logo_URL": "", "Note_Tattiche": ""},
    {"Girone": "Girone A", "Squadra": "ASD POL. BASKET BITRITTO", "Logo_URL": "", "Note_Tattiche": ""},
    {"Girone": "Girone A", "Squadra": "ASD VI.G.OR BASKET SAN SEVERO", "Logo_URL": "", "Note_Tattiche": ""},
    {"Girone": "Girone A", "Squadra": "ASD VIRTUS FOGGIA", "Logo_URL": "", "Note_Tattiche": ""},
    {"Girone": "Girone A", "Squadra": "ECOFAN CERIGNOLA MEDITERRANEA 92", "Logo_URL": "", "Note_Tattiche": ""},
    {"Girone": "Girone A", "Squadra": "FORTITUDO BASKET APRICENA", "Logo_URL": "", "Note_Tattiche": ""},
    {"Girone": "Girone A", "Squadra": "GINNASTICA ANGIULLI BARI", "Logo_URL": "", "Note_Tattiche": ""},
    {"Girone": "Girone A", "Squadra": "PALLACANESTRO OLIMPIA CORATO", "Logo_URL": "", "Note_Tattiche": ""},
    {"Girone": "Girone A", "Squadra": "POL. DIL. NUOVA MATTEOTTI CORATO", "Logo_URL": "", "Note_Tattiche": ""},
    {"Girone": "Girone A", "Squadra": "POLISPORTIVA ORSA CAPURSO SSD ARL", "Logo_URL": "", "Note_Tattiche": ""},
    {"Girone": "Girone A", "Squadra": "AGS DIL. TORITTO", "Logo_URL": "", "Note_Tattiche": ""},
    # Girone B (11 squadre)
    {"Girone": "Girone B", "Squadra": "ASD ATLETICA BASKET PUTIGNANO", "Logo_URL": "", "Note_Tattiche": ""},
    {"Girone": "Girone B", "Squadra": "ASD BASKET FASANO", "Logo_URL": "", "Note_Tattiche": ""},
    {"Girone": "Girone B", "Squadra": "ASD CLUB GIGANTI CISTERNINO", "Logo_URL": "", "Note_Tattiche": ""},
    {"Girone": "Girone B", "Squadra": "ASD DREAM BASKET ALTAMURA", "Logo_URL": "", "Note_Tattiche": ""},
    {"Girone": "Girone B", "Squadra": "ASD MESSAPICA BASKET CEGLIE", "Logo_URL": "", "Note_Tattiche": ""},
    {"Girone": "Girone B", "Squadra": "ASD MURGIA BASKET SANTERAMO", "Logo_URL": "", "Note_Tattiche": ""},
    {"Girone": "Girone B", "Squadra": "ASD SCUOLA BASKET MARTINESE", "Logo_URL": "", "Note_Tattiche": ""},
    {"Girone": "Girone B", "Squadra": "DOMITI LA PINTA BASKET PULSANO", "Logo_URL": "", "Note_Tattiche": ""},
    {"Girone": "Girone B", "Squadra": "MASSERIA SEMERARO NEW SPORTING MOTTOLA", "Logo_URL": "", "Note_Tattiche": ""},
    {"Girone": "Girone B", "Squadra": "POL. OLYMPIA CLUB RUTIGLIANO", "Logo_URL": "", "Note_Tattiche": ""},
    {"Girone": "Girone B", "Squadra": "SUPPORT_O TARANTO", "Logo_URL": "", "Note_Tattiche": ""},
    # Girone C (11 squadre)
    {"Girone": "Girone C", "Squadra": "A.POL.DIL.AURORA BRINDISI", "Logo_URL": "", "Note_Tattiche": ""},
    {"Girone": "Girone C", "Squadra": "ALL STAR BASKET FRANCAVILLA", "Logo_URL": "", "Note_Tattiche": ""},
    {"Girone": "Girone C", "Squadra": "ASD ASSI BASKET BRINDISI", "Logo_URL": "", "Note_Tattiche": ""},
    {"Girone": "Girone C", "Squadra": "ASD BASKET TRICASE", "Logo_URL": "", "Note_Tattiche": ""},
    {"Girone": "Girone C", "Squadra": "ASD BELLFIKA MESAGNE", "Logo_URL": "", "Note_Tattiche": ""},
    {"Girone": "Girone C", "Squadra": "ASD MAGIC GALATINA", "Logo_URL": "", "Note_Tattiche": ""},
    {"Girone": "Girone C", "Squadra": "ASD NEW BASKET CARMIANO", "Logo_URL": "", "Note_Tattiche": ""},
    {"Girone": "Girone C", "Squadra": "ASD POLISPORTIVA MANDURIA", "Logo_URL": "", "Note_Tattiche": ""},
    {"Girone": "Girone C", "Squadra": "AZ DISINFESTAZIONI SRL VIRTUS BRINDISI", "Logo_URL": "", "Note_Tattiche": ""},
    {"Girone": "Girone C", "Squadra": "DIERRE ARREDAMENTI CALIMERA BASKET", "Logo_URL": "", "Note_Tattiche": ""},
    {"Girone": "Girone C", "Squadra": "SENSI PALLACANESTRO LUPA LECCE", "Logo_URL": "", "Note_Tattiche": ""},
]

# (ID_Partita, Girone, Giornata, Data, Casa, Trasferta, Punti_Casa, Punti_Trasferta, Stato)
DEFAULT_GAMES_RAW = [
    # ==========================================================
    # GIRONE A - CU N. 91 DEL 02/11/2026 (GARE 1867 - 1976)
    # ==========================================================
    ("A01_1867", "Girone A", 1, "Sab 07/11/2026 19:00", "POL. DIL. NUOVA MATTEOTTI CORATO", "PALLACANESTRO OLIMPIA CORATO", 0, 0, "Da giocare"),
    ("A01_1868", "Girone A", 1, "Dom 08/11/2026 18:30", "FORTITUDO BASKET APRICENA", "ECOFAN CERIGNOLA MEDITERRANEA 92", 0, 0, "Da giocare"),
    ("A01_1869", "Girone A", 1, "Dom 08/11/2026 18:00", "GINNASTICA ANGIULLI BARI", "ASD MAGIC BARI", 0, 0, "Da giocare"),
    ("A01_1870", "Girone A", 1, "Sab 07/11/2026 18:30", "ASD VIRTUS FOGGIA", "POLISPORTIVA ORSA CAPURSO SSD ARL", 0, 0, "Da giocare"),
    ("A01_1871", "Girone A", 1, "Dom 08/11/2026 18:30", "ASD POL. BASKET BITRITTO", "AGS DIL. TORITTO", 0, 0, "Da giocare"),

    ("A02_1872", "Girone A", 2, "Sab 14/11/2026 18:00", "ASD VI.G.OR BASKET SAN SEVERO", "ASD VIRTUS FOGGIA", 0, 0, "Da giocare"),
    ("A02_1873", "Girone A", 2, "Dom 15/11/2026 20:15", "PALLACANESTRO OLIMPIA CORATO", "FORTITUDO BASKET APRICENA", 0, 0, "Da giocare"),
    ("A02_1874", "Girone A", 2, "Dom 15/11/2026 19:00", "ECOFAN CERIGNOLA MEDITERRANEA 92", "POL. DIL. NUOVA MATTEOTTI CORATO", 0, 0, "Da giocare"),
    ("A02_1875", "Girone A", 2, "Dom 15/11/2026 19:00", "AGS DIL. TORITTO", "GINNASTICA ANGIULLI BARI", 0, 0, "Da giocare"),
    ("A02_1876", "Girone A", 2, "Dom 15/11/2026 17:30", "ASD MAGIC BARI", "ASD POL. BASKET BITRITTO", 0, 0, "Da giocare"),

    ("A03_1877", "Girone A", 3, "Sab 21/11/2026 19:30", "GINNASTICA ANGIULLI BARI", "ECOFAN CERIGNOLA MEDITERRANEA 92", 0, 0, "Da giocare"),
    ("A03_1878", "Girone A", 3, "Dom 22/11/2026 18:30", "FORTITUDO BASKET APRICENA", "ASD MAGIC BARI", 0, 0, "Da giocare"),
    ("A03_1879", "Girone A", 3, "Dom 22/11/2026 18:00", "POLISPORTIVA ORSA CAPURSO SSD ARL", "ASD VI.G.OR BASKET SAN SEVERO", 0, 0, "Da giocare"),
    ("A03_1880", "Girone A", 3, "Sab 21/11/2026 19:00", "POL. DIL. NUOVA MATTEOTTI CORATO", "AGS DIL. TORITTO", 0, 0, "Da giocare"),
    ("A03_1881", "Girone A", 3, "Dom 22/11/2026 18:30", "ASD POL. BASKET BITRITTO", "PALLACANESTRO OLIMPIA CORATO", 0, 0, "Da giocare"),

    ("A04_1882", "Girone A", 4, "Dom 29/11/2026 17:30", "ASD MAGIC BARI", "POL. DIL. NUOVA MATTEOTTI CORATO", 0, 0, "Da giocare"),
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
    ("A21_1969", "Girone A", 21, "Sab 17/04/2027 18:00", "ASD VI.G.OR BASKET SAN SEVERO", "POLISPORTIVA ORSA CAPURSO SSD ARL", 0, 0, "Da giocare"),
    ("A21_1970", "Girone A", 21, "Dom 18/04/2027 18:30", "FORTITUDO BASKET APRICENA", "GINNASTICA ANGIULLI BARI", 0, 0, "Da giocare"),
    ("A21_1971", "Girone A", 21, "Sab 17/04/2027 19:00", "POL. DIL. NUOVA MATTEOTTI CORATO", "ASD VIRTUS FOGGIA", 0, 0, "Da giocare"),

    ("A22_1972", "Girone A", 22, "Sab 24/04/2027 18:00", "POLISPORTIVA ORSA CAPURSO SSD ARL", "ASD POL. BASKET BITRITTO", 0, 0, "Da giocare"),
    ("A22_1973", "Girone A", 22, "Dom 25/04/2027 19:00", "AGS DIL. TORITTO", "ASD MAGIC BARI", 0, 0, "Da giocare"),
    ("A22_1974", "Girone A", 22, "Dom 25/04/2027 19:00", "ECOFAN CERIGNOLA MEDITERRANEA 92", "ASD VI.G.OR BASKET SAN SEVERO", 0, 0, "Da giocare"),
    ("A22_1975", "Girone A", 22, "Sab 24/04/2027 18:30", "ASD VIRTUS FOGGIA", "FORTITUDO BASKET APRICENA", 0, 0, "Da giocare"),
    ("A22_1976", "Girone A", 22, "Sab 24/04/2027 19:30", "GINNASTICA ANGIULLI BARI", "PALLACANESTRO OLIMPIA CORATO", 0, 0, "Da giocare"),

    # ==========================================================
    # GIRONE B - CU N. 92 DEL 02/11/2026 (GARE 2109 - 2218)
    # ==========================================================
    ("B01_2109", "Girone B", 1, "Sab 07/11/2026 18:45", "ASD SCUOLA BASKET MARTINESE", "ASD DREAM BASKET ALTAMURA", 0, 0, "Da giocare"),
    ("B01_2110", "Girone B", 1, "Dom 08/11/2026 17:30", "ASD MURGIA BASKET SANTERAMO", "MASSERIA SEMERARO NEW SPORTING MOTTOLA", 0, 0, "Da giocare"),
    ("B01_2111", "Girone B", 1, "Dom 08/11/2026 18:00", "SUPPORT_O TARANTO", "DOMITI LA PINTA BASKET PULSANO", 0, 0, "Da giocare"),
    ("B01_2112", "Girone B", 1, "Sab 07/11/2026 19:00", "ASD BASKET FASANO", "ASD ATLETICA BASKET PUTIGNANO", 0, 0, "Da giocare"),
    ("B01_2113", "Girone B", 1, "Sab 07/11/2026 19:00", "ASD CLUB GIGANTI CISTERNINO", "ASD MESSAPICA BASKET CEGLIE", 0, 0, "Da giocare"),

    ("B02_2114", "Girone B", 2, "Sab 14/11/2026 20:00", "ASD MESSAPICA BASKET CEGLIE", "POL. OLYMPIA CLUB RUTIGLIANO", 0, 0, "Da giocare"),
    ("B02_2115", "Girone B", 2, "Dom 15/11/2026 18:00", "ASD DREAM BASKET ALTAMURA", "ASD BASKET FASANO", 0, 0, "Da giocare"),
    ("B02_2116", "Girone B", 2, "Sab 14/11/2026 18:00", "ASD ATLETICA BASKET PUTIGNANO", "ASD SCUOLA BASKET MARTINESE", 0, 0, "Da giocare"),
    ("B02_2117", "Girone B", 2, "Dom 15/11/2026 18:30", "MASSERIA SEMERARO NEW SPORTING MOTTOLA", "SUPPORT_O TARANTO", 0, 0, "Da giocare"),
    ("B02_2118", "Girone B", 2, "Dom 15/11/2026 18:00", "DOMITI LA PINTA BASKET PULSANO", "ASD MURGIA BASKET SANTERAMO", 0, 0, "Da giocare"),

    ("B03_2119", "Girone B", 3, "Dom 22/11/2026 18:00", "ASD BASKET FASANO", "MASSERIA SEMERARO NEW SPORTING MOTTOLA", 0, 0, "Da giocare"),
    ("B03_2120", "Girone B", 3, "Sab 21/11/2026 18:45", "ASD SCUOLA BASKET MARTINESE", "DOMITI LA PINTA BASKET PULSANO", 0, 0, "Da giocare"),
    ("B03_2121", "Girone B", 3, "Dom 22/11/2026 18:00", "POL. OLYMPIA CLUB RUTIGLIANO", "ASD CLUB GIGANTI CISTERNINO", 0, 0, "Da giocare"),
    ("B03_2122", "Girone B", 3, "Dom 22/11/2026 18:00", "SUPPORT_O TARANTO", "ASD DREAM BASKET ALTAMURA", 0, 0, "Da giocare"),
    ("B03_2123", "Girone B", 3, "Dom 22/11/2026 17:30", "ASD MURGIA BASKET SANTERAMO", "ASD ATLETICA BASKET PUTIGNANO", 0, 0, "Da giocare"),

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

    ("B21_2209", "Girone B", 21, "Dom 18/04/2027 18:00", "ASD DREAM BASKET ALTAMURA", "DOMITI LA PINTA BASKET PULSANO", 0, 0, "Da giocare"),
    ("B21_2210", "Girone B", 21, "Dom 18/04/2027 18:00", "POL. OLYMPIA CLUB RUTIGLIANO", "ASD MURGIA BASKET SANTERAMO", 0, 0, "Da giocare"),
    ("B21_2211", "Girone B", 21, "Sab 17/04/2027 18:45", "ASD SCUOLA BASKET MARTINESE", "ASD MESSAPICA BASKET CEGLIE", 0, 0, "Da giocare"),
    ("B21_2212", "Girone B", 21, "Sab 17/04/2027 19:00", "ASD BASKET FASANO", "ASD CLUB GIGANTI CISTERNINO", 0, 0, "Da giocare"),
    ("B21_2213", "Girone B", 21, "Dom 18/04/2027 18:00", "SUPPORT_O TARANTO", "ASD ATLETICA BASKET PUTIGNANO", 0, 0, "Da giocare"),

    ("B22_2214", "Girone B", 22, "Dom 25/04/2027 18:00", "DOMITI LA PINTA BASKET PULSANO", "MASSERIA SEMERARO NEW SPORTING MOTTOLA", 0, 0, "Da giocare"),
    ("B22_2215", "Girone B", 22, "Dom 25/04/2027 18:30", "ASD MURGIA BASKET SANTERAMO", "ASD DREAM BASKET ALTAMURA", 0, 0, "Da giocare"),
    ("B22_2216", "Girone B", 22, "Sab 24/04/2027 20:00", "ASD MESSAPICA BASKET CEGLIE", "ASD BASKET FASANO", 0, 0, "Da giocare"),
    ("B22_2217", "Girone B", 22, "Sab 24/04/2027 18:00", "ASD ATLETICA BASKET PUTIGNANO", "POL. OLYMPIA CLUB RUTIGLIANO", 0, 0, "Da giocare"),
    ("B22_2218", "Girone B", 22, "Sab 24/04/2027 19:00", "ASD CLUB GIGANTI CISTERNINO", "SUPPORT_O TARANTO", 0, 0, "Da giocare"),

    # ==========================================================
    # GIRONE C - CU N. 93 DEL 02/11/2026 (GARE 2219 - 2328)
    # ==========================================================
    ("C01_2219", "Girone C", 1, "Dom 08/11/2026 18:00", "ASD BASKET TRICASE", "A.POL.DIL.AURORA BRINDISI", 0, 0, "Da giocare"),
    ("C01_2220", "Girone C", 1, "Sab 07/11/2026 18:00", "ALL STAR BASKET FRANCAVILLA", "ASD BELLFIKA MESAGNE", 0, 0, "Da giocare"),
    ("C01_2221", "Girone C", 1, "Dom 08/11/2026 18:30", "DIERRE ARREDAMENTI CALIMERA BASKET", "ASD MAGIC GALATINA", 0, 0, "Da giocare"),
    ("C01_2222", "Girone C", 1, "Dom 08/11/2026 18:00", "ASD ASSI BASKET BRINDISI", "ASD NEW BASKET CARMIANO", 0, 0, "Da giocare"),
    ("C01_2223", "Girone C", 1, "Dom 08/11/2026 18:30", "SENSI PALLACANESTRO LUPA LECCE", "AZ DISINFESTAZIONI SRL VIRTUS BRINDISI", 0, 0, "Da giocare"),

    ("C02_2224", "Girone C", 2, "Sab 14/11/2026 18:00", "ASD NEW BASKET CARMIANO", "ALL STAR BASKET FRANCAVILLA", 0, 0, "Da giocare"),
    ("C02_2225", "Girone C", 2, "Sab 14/11/2026 18:30", "ASD MAGIC GALATINA", "ASD BASKET TRICASE", 0, 0, "Da giocare"),
    ("C02_2226", "Girone C", 2, "Sab 14/11/2026 16:30", "AZ DISINFESTAZIONI SRL VIRTUS BRINDISI", "ASD POLISPORTIVA MANDURIA", 0, 0, "Da giocare"),
    ("C02_2227", "Girone C", 2, "Dom 15/11/2026 18:00", "ASD BELLFIKA MESAGNE", "ASD ASSI BASKET BRINDISI", 0, 0, "Da giocare"),
    ("C02_2228", "Girone C", 2, "Sab 14/11/2026 18:00", "A.POL.DIL.AURORA BRINDISI", "DIERRE ARREDAMENTI CALIMERA BASKET", 0, 0, "Da giocare"),

    ("C03_2229", "Girone C", 3, "Sab 21/11/2026 18:00", "ALL STAR BASKET FRANCAVILLA", "ASD MAGIC GALATINA", 0, 0, "Da giocare"),
    ("C03_2230", "Girone C", 3, "Sab 21/11/2026 18:00", "A.POL.DIL.AURORA BRINDISI", "ASD ASSI BASKET BRINDISI", 0, 0, "Da giocare"),
    ("C03_2231", "Girone C", 3, "Dom 22/11/2026 18:30", "DIERRE ARREDAMENTI CALIMERA BASKET", "ASD BELLFIKA MESAGNE", 0, 0, "Da giocare"),
    ("C03_2232", "Girone C", 3, "Dom 22/11/2026 18:00", "ASD POLISPORTIVA MANDURIA", "SENSI PALLACANESTRO LUPA LECCE", 0, 0, "Da giocare"),
    ("C03_2233", "Girone C", 3, "Dom 22/11/2026 18:00", "ASD BASKET TRICASE", "ASD NEW BASKET CARMIANO", 0, 0, "Da giocare"),

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
    ("C10_2265", "Girone C", 10, "Sab 23/01/2027 18:00", "ASD POLISPORTIVA MANDURIA", "ASD ASSI BASKET BRINDISI", 0, 0, "Da giocare"),
    ("C10_2266", "Girone C", 10, "Dom 24/01/2027 17:00", "ASD BELLFIKA MESAGNE", "ASD MAGIC GALATINA", 0, 0, "Da giocare"),
    ("C10_2267", "Girone C", 10, "Sab 23/01/2027 18:00", "A.POL.DIL.AURORA BRINDISI", "ALL STAR BASKET FRANCAVILLA", 0, 0, "Da giocare"),
    ("C10_2268", "Girone C", 10, "Sab 23/01/2027 16:30", "AZ DISINFESTAZIONI SRL VIRTUS BRINDISI", "DIERRE ARREDAMENTI CALIMERA BASKET", 0, 0, "Da giocare"),

    ("C11_2269", "Girone C", 11, "Dom 31/01/2027 20:00", "ASD NEW BASKET CARMIANO", "ASD BELLFIKA MESAGNE", 0, 0, "Da giocare"),
    ("C11_2270", "Girone C", 11, "Sab 30/01/2027 18:00", "ALL STAR BASKET FRANCAVILLA", "SENSI PALLACANESTRO LUPA LECCE", 0, 0, "Da giocare"),
    ("C11_2271", "Girone C", 11, "Dom 31/01/2027 18:00", "A.POL.DIL.AURORA BRINDISI", "ASD POLISPORTIVA MANDURIA", 0, 0, "Da giocare"),
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
    ("C19_2310", "Girone C", 19, "Sab 03/04/2027 18:00", "ASD NEW BASKET CARMIANO", "A.POL.DIL.AURORA BRINDISI", 0, 0, "Da giocare"),
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

    ("C22_2324", "Girone C", 22, "Sab 24/04/2027 18:00", "ASD ASSI BASKET BRINDISI", "ASD MAGIC GALATINA", 0, 0, "Da giocare"),
    ("C22_2325", "Girone C", 22, "Sab 24/04/2027 16:30", "AZ DISINFESTAZIONI SRL VIRTUS BRINDISI", "ASD BASKET TRICASE", 0, 0, "Da giocare"),
    ("C22_2326", "Girone C", 22, "Sab 24/04/2027 18:00", "A.POL.DIL.AURORA BRINDISI", "ASD POLISPORTIVA MANDURIA", 0, 0, "Da giocare"),
    ("C22_2327", "Girone C", 22, "Sab 24/04/2027 18:30", "SENSI PALLACANESTRO LUPA LECCE", "ALL STAR BASKET FRANCAVILLA", 0, 0, "Da giocare"),
    ("C22_2328", "Girone C", 22, "Dom 25/04/2027 17:00", "ASD BELLFIKA MESAGNE", "ASD NEW BASKET CARMIANO", 0, 0, "Da giocare"),
]

GAME_COLS = [
    "ID_Partita",
    "Girone",
    "Giornata",
    "Data",
    "Casa",
    "Trasferta",
    "Punti_Casa",
    "Punti_Trasferta",
    "Stato",
    "Q1_C",
    "Q2_C",
    "Q3_C",
    "Q4_C",
    "OT_C",
    "Q1_T",
    "Q2_T",
    "Q3_T",
    "Q4_T",
    "OT_T",
    "Note_Gara",
]

BOX_COLS = [
    "ID_Partita",
    "Girone",
    "Squadra",
    "Quintetto_Base",
    "Numero",
    "Ruolo",
    "Giocatore",
    "Punti",
    "2P_Segnati",
    "3P_Segnati",
    "TL_Segnati",
    "TL_Sbagliati",
    "Note",
]


def build_default_games_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "ID_Partita": gid,
                "Girone": girone,
                "Giornata": giornata,
                "Data": data_ora,
                "Casa": casa,
                "Trasferta": trasferta,
                "Punti_Casa": pts_casa,
                "Punti_Trasferta": pts_trasf,
                "Stato": stato,
                "Q1_C": 0,
                "Q2_C": 0,
                "Q3_C": 0,
                "Q4_C": 0,
                "OT_C": 0,
                "Q1_T": 0,
                "Q2_T": 0,
                "Q3_T": 0,
                "Q4_T": 0,
                "OT_T": 0,
                "Note_Gara": "",
            }
            for gid, girone, giornata, data_ora, casa, trasferta, pts_casa, pts_trasf, stato in DEFAULT_GAMES_RAW
        ]
    )


def reset_official_data():
    pd.DataFrame(DEFAULT_TEAMS).to_csv(TEAMS_FILE, index=False)
    build_default_games_df().to_csv(GAMES_FILE, index=False)
    if not BOX_FILE.exists():
        pd.DataFrame(columns=BOX_COLS).to_csv(BOX_FILE, index=False)


def init_data():
    if not TEAMS_FILE.exists():
        pd.DataFrame(DEFAULT_TEAMS).to_csv(TEAMS_FILE, index=False)

    if not GAMES_FILE.exists():
        build_default_games_df().to_csv(GAMES_FILE, index=False)

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

    int_game_cols = [
        "Giornata",
        "Punti_Casa",
        "Punti_Trasferta",
        "Q1_C",
        "Q2_C",
        "Q3_C",
        "Q4_C",
        "OT_C",
        "Q1_T",
        "Q2_T",
        "Q3_T",
        "Q4_T",
        "OT_T",
    ]
    for col in int_game_cols:
        games_df[col] = pd.to_numeric(games_df[col], errors="coerce").fillna(0).astype(int)

    for col in ["Punti", "2P_Segnati", "3P_Segnati", "TL_Segnati", "TL_Sbagliati"]:
        box_df[col] = pd.to_numeric(box_df[col], errors="coerce").fillna(0).astype(int)

    box_df["Quintetto_Base"] = (
        box_df["Quintetto_Base"].astype(str).str.lower().isin(["true", "1", "si", "sì", "yes"])
    )

    return teams_df, games_df, box_df


def save_teams(df):
    df.to_csv(TEAMS_FILE, index=False)


def save_games(df):
    df.to_csv(GAMES_FILE, index=False)


def save_box(df):
    df.to_csv(BOX_FILE, index=False)


def format_streak_text(streak: str) -> str:
    """Formatta le ultime partite come 'W W W' (mai '3 W' o '3W')."""
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
    return {
        "PTS": wins * 2,
        "PG": pg,
        "V": wins,
        "S": losses,
        "PF": pf,
        "DP": pf - pa,
        "STREAK": streak,
    }


def _head_to_head_metrics(group_teams: list[str], played_df: pd.DataFrame) -> dict[str, dict]:
    team_set = set(group_teams)
    stats = {t: {"h2h_pts": 0, "h2h_pf": 0, "h2h_dp": 0} for t in group_teams}
    for _, row in played_df.iterrows():
        home = row["Casa"]
        away = row["Trasferta"]
        if home in team_set and away in team_set:
            hp = int(row["Punti_Casa"])
            ap = int(row["Punti_Trasferta"])
            stats[home]["h2h_pf"] += hp
            stats[away]["h2h_pf"] += ap
            stats[home]["h2h_dp"] += hp - ap
            stats[away]["h2h_dp"] += ap - hp
            if hp > ap:
                stats[home]["h2h_pts"] += 2
            elif ap > hp:
                stats[away]["h2h_pts"] += 2
    return stats


def compute_standings_for_girone(girone: str, teams_df: pd.DataFrame, games_df: pd.DataFrame) -> list:
    g_teams = teams_df[teams_df["Girone"] == girone]
    if g_teams.empty:
        return []

    played = games_df[(games_df["Girone"] == girone) & (games_df["Stato"].str.lower() == "giocata")].copy()

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

    pts_buckets: dict[int, list[dict]] = {}
    for item in raw_items:
        pts_buckets.setdefault(item["PTS"], []).append(item)

    ordered_board = []
    for pts_val in sorted(pts_buckets.keys(), reverse=True):
        bucket = pts_buckets[pts_val]
        if len(bucket) == 1:
            ordered_board.extend(bucket)
        else:
            names = [x["Squadra"] for x in bucket]
            h2h = _head_to_head_metrics(names, played)
            bucket_sorted = sorted(
                bucket,
                key=lambda x: (
                    -h2h[x["Squadra"]]["h2h_pts"],
                    -h2h[x["Squadra"]]["h2h_dp"],
                    -h2h[x["Squadra"]]["h2h_pf"],
                    -x["DP"],
                    -x["PF"],
                    x["Squadra"],
                ),
            )
            ordered_board.extend(bucket_sorted)

    return ordered_board


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


def compute_roster_stats(team_name: str, girone: str, box_df: pd.DataFrame):
    sub = box_df[(box_df["Girone"] == girone) & (box_df["Squadra"] == team_name)].copy()
    if sub.empty:
        return pd.DataFrame(
            columns=[
                "Quintetto Base (Presenze)",
                "Numero",
                "Ruolo",
                "Nome e Cognome",
                "Partite",
                "Punti",
                "Media Punti",
                "TL Segnati",
                "TL Sbagliati",
                "% TL",
                "2P Segnati",
                "3P Segnati",
                "Note",
            ]
        )

    rows = []
    for player, grp in sub.groupby("Giocatore", sort=False):
        games_count = len(grp)
        quintetti = int(grp["Quintetto_Base"].sum())
        pts = int(grp["Punti"].sum())
        tl_m = int(grp["TL_Segnati"].sum())
        tl_x = int(grp["TL_Sbagliati"].sum())
        tl_att = tl_m + tl_x
        tl_pct = round((tl_m / tl_att) * 100, 1) if tl_att > 0 else 0.0
        p2 = int(grp["2P_Segnati"].sum())
        p3 = int(grp["3P_Segnati"].sum())
        ppg = round(pts / games_count, 1) if games_count > 0 else 0.0

        num_vals = [n for n in grp["Numero"].tolist() if str(n).strip()]
        role_vals = [r for r in grp["Ruolo"].tolist() if str(r).strip()]
        note_vals = [nt for nt in grp["Note"].tolist() if str(nt).strip()]

        rows.append(
            {
                "Quintetto Base (Presenze)": quintetti,
                "Numero": num_vals[-1] if num_vals else "-",
                "Ruolo": role_vals[-1] if role_vals else "-",
                "Nome e Cognome": player,
                "Partite": games_count,
                "Punti": pts,
                "Media Punti": ppg,
                "TL Segnati": tl_m,
                "TL Sbagliati": tl_x,
                "% TL": tl_pct,
                "2P Segnati": p2,
                "3P Segnati": p3,
                "Note": " | ".join(note_vals) if note_vals else "",
            }
        )

    res = pd.DataFrame(rows)
    return res.sort_values(by="Media Punti", ascending=False).reset_index(drop=True)


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

        logo_html = (
            f'<img class="s-logo" src="{item["Logo_URL"]}" alt="{item["Squadra"]}" />'
            if item["Logo_URL"].strip()
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
        st.markdown("#### Confronto Migliore Terza (Punti → Differenza Canestri → Punti Segnati)")
        t_rows = []
        for rank_i, t_item in enumerate(ranked_thirds, start=1):
            t_rows.append(
                {
                    "Pos": rank_i,
                    "Girone": t_item["Girone"],
                    "Squadra": t_item["Squadra"],
                    "PTS": t_item["PTS"],
                    "P": t_item["PG"],
                    "W": t_item["V"],
                    "L": t_item["S"],
                    "DIFF": format_dp(t_item["DP"]),
                    "PF": t_item["PF"],
                    "Streak": format_streak_text(t_item["STREAK"]),
                    "Stato": "QUALIFICATA PLAY-OFF" if rank_i == 1 else "FUORI PLAY-OFF",
                }
            )
        st.dataframe(pd.DataFrame(t_rows), use_container_width=True, hide_index=True)


def render_round_card(round_num: int, round_games: pd.DataFrame, logo_map: dict, girone_cal: str, is_ritorno: bool = False):
    display_num = round_num - 11 if is_ritorno and round_num > 11 else round_num
    phase_txt = "RITORNO" if is_ritorno else "ANDATA"
    label_round = f"GIORNATA {display_num} ({phase_txt})"

    st.markdown(
        """
        <style>
        .round-box {
            background: #14171c;
            border: 1px solid #262b34;
            border-radius: 10px;
            margin-bottom: 14px;
            overflow: hidden;
        }
        .round-title {
            background: #1b2028;
            color: #f1f5f9;
            font-weight: 700;
            font-size: 14px;
            padding: 8px 14px;
            border-bottom: 1px solid #262b34;
        }
        a.match-link {
            display: block;
            text-decoration: none !important;
            color: inherit !important;
            border-bottom: 1px solid #20252e;
            transition: background 0.15s ease;
        }
        a.match-link:last-child {
            border-bottom: none;
        }
        a.match-link:hover {
            background: #1c222b;
        }
        .match-row {
            display: grid;
            grid-template-columns: 92px 1fr 44px;
            gap: 10px;
            align-items: center;
            padding: 9px 14px;
            cursor: pointer;
        }
        .m-meta {
            text-align: center;
            line-height: 1.3;
        }
        .m-date {
            font-size: 11px;
            color: #cbd5e1;
            font-weight: 600;
        }
        .m-status-ft {
            font-size: 11px;
            color: #94a3b8;
            font-weight: 700;
        }
        .m-status-time {
            font-size: 11px;
            color: #94a3b8;
            font-weight: 600;
        }
        .m-teams {
            display: flex;
            flex-direction: column;
            gap: 5px;
            min-width: 0;
        }
        .m-team-line {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
            font-weight: 600;
            color: #e2e8f0;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .m-team-line.winner {
            color: #ffffff;
            font-weight: 800;
        }
        .m-logo {
            width: 20px;
            height: 20px;
            object-fit: contain;
            background: rgba(255,255,255,0.92);
            border-radius: 4px;
            padding: 1px;
            flex-shrink: 0;
        }
        .m-scores {
            display: flex;
            flex-direction: column;
            gap: 5px;
            text-align: right;
            font-size: 14px;
            font-weight: 700;
            color: #cbd5e1;
        }
        .m-score-win {
            color: #ffffff;
            font-weight: 800;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    parts = [f'<div class="round-box"><div class="round-title">{label_round}</div>']

    if round_games.empty:
        parts.append('<div class="match-row"><div class="m-meta">—</div><div class="m-team-line">Nessuna gara</div><div class="m-scores"></div></div>')
    else:
        for _, g in round_games.iterrows():
            is_played = str(g["Stato"]).lower() == "giocata"
            raw_dt = str(g["Data"]).strip()
            dt_tokens = raw_dt.split()
            if len(dt_tokens) >= 3:
                date_part = dt_tokens[1]
                time_part = dt_tokens[2]
            elif len(dt_tokens) == 2:
                date_part, time_part = dt_tokens[0], dt_tokens[1]
            else:
                date_part, time_part = raw_dt, ""

            status_html = (
                '<div class="m-status-ft">FT</div>'
                if is_played
                else f'<div class="m-status-time">{time_part}</div>'
            )

            home_name = g["Casa"]
            away_name = g["Trasferta"]
            home_pts = int(g["Punti_Casa"])
            away_pts = int(g["Punti_Trasferta"])

            home_win = is_played and home_pts > away_pts
            away_win = is_played and away_pts > home_pts

            home_logo = logo_map.get(home_name, "")
            away_logo = logo_map.get(away_name, "")
            h_logo_tag = f'<img class="m-logo" src="{home_logo}" alt="" />' if home_logo else "🏀"
            a_logo_tag = f'<img class="m-logo" src="{away_logo}" alt="" />' if away_logo else "🏀"

            s1 = str(home_pts) if is_played else ""
            s2 = str(away_pts) if is_played else ""

            href = f"?girone={quote(girone_cal)}&game={quote(str(g['ID_Partita']))}"

            parts.append(
                f'<a class="match-link" href="{href}" target="_self">'
                f'<div class="match-row">'
                f'<div class="m-meta"><div class="m-date">{date_part}</div>{status_html}</div>'
                f'<div class="m-teams">'
                f'<div class="m-team-line {"winner" if home_win else ""}">{h_logo_tag}<span>{home_name}</span></div>'
                f'<div class="m-team-line {"winner" if away_win else ""}">{a_logo_tag}<span>{away_name}</span></div>'
                f'</div>'
                f'<div class="m-scores">'
                f'<div class="{"m-score-win" if home_win else ""}">{s1}</div>'
                f'<div class="{"m-score-win" if away_win else ""}">{s2}</div>'
                f'</div>'
                f'</div></a>'
            )

    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)


def render_match_center(game_id: str, teams_df: pd.DataFrame, games_df: pd.DataFrame, box_df: pd.DataFrame, logo_map: dict, cal_teams: list):
    matches = games_df[games_df["ID_Partita"] == game_id]
    if matches.empty:
        st.session_state["selected_game_id"] = None
        if "game" in st.query_params:
            del st.query_params["game"]
        st.rerun()

    idx = matches.index[0]
    g = games_df.loc[idx]

    if st.button("← Torna al Calendario"):
        st.session_state["selected_game_id"] = None
        if "game" in st.query_params:
            del st.query_params["game"]
        st.rerun()

    home_name = g["Casa"]
    away_name = g["Trasferta"]
    home_logo = logo_map.get(home_name, "")
    away_logo = logo_map.get(away_name, "")
    is_played = str(g["Stato"]).lower() == "giocata"
    status_label = "FINALE" if is_played else "DA GIOCARE"

    st.markdown(
        """
        <style>
        .mc-header {
            background: #07131d;
            border: 1px solid #1b2e3d;
            border-radius: 12px;
            padding: 18px 20px;
            margin-bottom: 12px;
        }
        .mc-top-grid {
            display: grid;
            grid-template-columns: 1fr 220px 1fr;
            align-items: center;
            text-align: center;
            gap: 12px;
        }
        .mc-team-box {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
        }
        .mc-logo {
            width: 68px;
            height: 68px;
            object-fit: contain;
            background: #ffffff;
            border-radius: 14px;
            padding: 6px;
        }
        .mc-team-name {
            font-size: 18px;
            font-weight: 800;
            color: #ffffff;
        }
        .mc-dt {
            font-size: 12px;
            color: #94a3b8;
            font-weight: 600;
        }
        .mc-score {
            font-size: 38px;
            font-weight: 900;
            color: #ffffff;
            letter-spacing: 2px;
            line-height: 1.1;
        }
        .mc-status {
            font-size: 11px;
            font-weight: 800;
            color: #cbd5e1;
            letter-spacing: 1.2px;
            margin-top: 4px;
        }
        .box-table {
            width: 100%;
            border-collapse: collapse;
            background: #0b1620;
            color: #e2e8f0;
            font-size: 13px;
            border-radius: 8px;
            overflow: hidden;
        }
        .box-table th {
            background: #102230;
            color: #94a3b8;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            padding: 8px 8px;
            border-bottom: 1px solid #1d3345;
            text-align: center;
        }
        .box-table th.left, .box-table td.left {
            text-align: left;
        }
        .box-table td {
            padding: 8px 8px;
            border-bottom: 1px solid #152634;
            text-align: center;
            font-weight: 600;
        }
        .box-table td.pts-cell {
            font-weight: 800;
            color: #ffffff;
        }
        .starter-star {
            color: #facc15;
            font-weight: 900;
            margin-right: 4px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    h_img = f'<img class="mc-logo" src="{home_logo}" alt="" />' if home_logo else '<div class="mc-logo">🏀</div>'
    a_img = f'<img class="mc-logo" src="{away_logo}" alt="" />' if away_logo else '<div class="mc-logo">🏀</div>'
    score_txt = f"{int(g['Punti_Casa'])} - {int(g['Punti_Trasferta'])}" if is_played else "— : —"

    st.markdown(
        f'<div class="mc-header">'
        f'<div class="mc-top-grid">'
        f'<div class="mc-team-box">{h_img}<div class="mc-team-name">{home_name}</div></div>'
        f'<div><div class="mc-dt">{g["Data"]}</div><div class="mc-score">{score_txt}</div><div class="mc-status">{status_label}</div></div>'
        f'<div class="mc-team-box">{a_img}<div class="mc-team-name">{away_name}</div></div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    sub_view = st.radio(
        "Sezione partita",
        ["RIASSUNTO", "STATS GIOCATORE"],
        horizontal=True,
        key="match_subview_radio",
    )

    if sub_view == "RIASSUNTO":
        st.markdown("#### Risultato e Parziali per Quarto")
        has_ot = int(g["OT_C"]) > 0 or int(g["OT_T"]) > 0
        q_cols = ["Squadra", "TOT", "Q1", "Q2", "Q3", "Q4"] + (["OT"] if has_ot else [])

        r_home = {
            "Squadra": home_name,
            "TOT": int(g["Punti_Casa"]) if is_played else 0,
            "Q1": int(g["Q1_C"]),
            "Q2": int(g["Q2_C"]),
            "Q3": int(g["Q3_C"]),
            "Q4": int(g["Q4_C"]),
        }
        r_away = {
            "Squadra": away_name,
            "TOT": int(g["Punti_Trasferta"]) if is_played else 0,
            "Q1": int(g["Q1_T"]),
            "Q2": int(g["Q2_T"]),
            "Q3": int(g["Q3_T"]),
            "Q4": int(g["Q4_T"]),
        }
        if has_ot:
            r_home["OT"] = int(g["OT_C"])
            r_away["OT"] = int(g["OT_T"])

        st.dataframe(pd.DataFrame([r_home, r_away])[q_cols], use_container_width=True, hide_index=True)

        if str(g["Note_Gara"]).strip():
            st.info(f"**Note partita:** {g['Note_Gara']}")

        with st.form("mc_update_game_form"):
            st.markdown("##### Aggiorna Risultato, Parziali e Note Partita")
            c1, c2, c3 = st.columns(3)
            upd_casa = c1.number_input("Punti Casa", min_value=0, max_value=200, value=int(g["Punti_Casa"]), step=1)
            upd_trasf = c2.number_input("Punti Trasferta", min_value=0, max_value=200, value=int(g["Punti_Trasferta"]), step=1)
            upd_stato = c3.selectbox("Stato", ["Da giocare", "Giocata"], index=0 if not is_played else 1)

            qc1, qc2, qc3, qc4, qcot = st.columns(5)
            q1_c = qc1.number_input("Q1 Casa", min_value=0, max_value=80, value=int(g["Q1_C"]), step=1)
            q2_c = qc2.number_input("Q2 Casa", min_value=0, max_value=80, value=int(g["Q2_C"]), step=1)
            q3_c = qc3.number_input("Q3 Casa", min_value=0, max_value=80, value=int(g["Q3_C"]), step=1)
            q4_c = qc4.number_input("Q4 Casa", min_value=0, max_value=80, value=int(g["Q4_C"]), step=1)
            ot_c = qcot.number_input("OT Casa", min_value=0, max_value=80, value=int(g["OT_C"]), step=1)

            qt1, qt2, qt3, qt4, qtot = st.columns(5)
            q1_t = qt1.number_input("Q1 Trasf", min_value=0, max_value=80, value=int(g["Q1_T"]), step=1)
            q2_t = qt2.number_input("Q2 Trasf", min_value=0, max_value=80, value=int(g["Q2_T"]), step=1)
            q3_t = qt3.number_input("Q3 Trasf", min_value=0, max_value=80, value=int(g["Q3_T"]), step=1)
            q4_t = qt4.number_input("Q4 Trasf", min_value=0, max_value=80, value=int(g["Q4_T"]), step=1)
            ot_t = qtot.number_input("OT Trasf", min_value=0, max_value=80, value=int(g["OT_T"]), step=1)

            note_g = st.text_input("Note partita (opz.)", value=str(g["Note_Gara"]))

            if st.form_submit_button("Salva Partita"):
                games_df.loc[idx, "Punti_Casa"] = int(upd_casa)
                games_df.loc[idx, "Punti_Trasferta"] = int(upd_trasf)
                games_df.loc[idx, "Stato"] = upd_stato
                games_df.loc[idx, "Q1_C"] = int(q1_c)
                games_df.loc[idx, "Q2_C"] = int(q2_c)
                games_df.loc[idx, "Q3_C"] = int(q3_c)
                games_df.loc[idx, "Q4_C"] = int(q4_c)
                games_df.loc[idx, "OT_C"] = int(ot_c)
                games_df.loc[idx, "Q1_T"] = int(q1_t)
                games_df.loc[idx, "Q2_T"] = int(q2_t)
                games_df.loc[idx, "Q3_T"] = int(q3_t)
                games_df.loc[idx, "Q4_T"] = int(q4_t)
                games_df.loc[idx, "OT_T"] = int(ot_t)
                games_df.loc[idx, "Note_Gara"] = note_g.strip()
                save_games(games_df)
                st.success("Dati partita salvati.")
                st.rerun()

    else:
        st.markdown("#### Stats Giocatore & Note Scouting")
        team_filter = st.radio(
            "Filtro squadra",
            ["TOTALE", home_name, away_name],
            horizontal=True,
            key="mc_team_filter",
        )

        game_box = box_df[box_df["ID_Partita"] == game_id].copy()
        if team_filter != "TOTALE":
            game_box = game_box[game_box["Squadra"] == team_filter]

        if game_box.empty:
            st.info("Nessun giocatore inserito ancora per questo tabellino.")
        else:
            game_box = game_box.sort_values(by=["Punti", "Giocatore"], ascending=[False, True])
            rows_html = []
            for _, pr in game_box.iterrows():
                tl_m = int(pr["TL_Segnati"])
                tl_x = int(pr["TL_Sbagliati"])
                tl_att = tl_m + tl_x
                tl_pct = f"{round((tl_m / tl_att) * 100, 1)}%" if tl_att > 0 else "—"
                star = '<span class="starter-star" title="Quintetto base">★</span>' if bool(pr["Quintetto_Base"]) else ""
                num_txt = f"#{pr['Numero']} " if str(pr["Numero"]).strip() else ""
                role_txt = f" ({pr['Ruolo']})" if str(pr["Ruolo"]).strip() else ""
                note_txt = str(pr["Note"]).strip() if str(pr["Note"]).strip() else "—"

                rows_html.append(
                    f"<tr>"
                    f"<td class='left'>{star}{num_txt}<strong>{pr['Giocatore']}</strong>{role_txt}</td>"
                    f"<td>{pr['Squadra']}</td>"
                    f"<td class='pts-cell'>{int(pr['Punti'])}</td>"
                    f"<td>{int(pr['2P_Segnati'])}</td>"
                    f"<td>{int(pr['3P_Segnati'])}</td>"
                    f"<td>{tl_m}</td>"
                    f"<td>{tl_x}</td>"
                    f"<td>{tl_pct}</td>"
                    f"<td class='left'>{note_txt}</td>"
                    f"</tr>"
                )

            table_html = (
                "<table class='box-table'><thead><tr>"
                "<th class='left'>GIOCATORE</th><th>SQUADRA</th><th>PT</th>"
                "<th>2P</th><th>3P</th><th>TL+</th><th>TL-</th><th>%TL</th>"
                "<th class='left'>NOTE / SCOUTING</th>"
                "</tr></thead><tbody>"
                + "".join(rows_html)
                + "</tbody></table>"
            )
            st.markdown(table_html, unsafe_allow_html=True)

        st.divider()
        with st.form("mc_add_player_form"):
            st.markdown("##### Aggiungi Giocatore al Tabellino")
            b1, b2, b3, b4 = st.columns([2.2, 2.5, 1.1, 1.3])
            sq_opts = [s for s in [home_name, away_name] if s] or cal_teams
            tab_sq = b1.selectbox("Squadra", sq_opts if sq_opts else ["Squadra"])
            giocatore = b2.text_input("Nome e Cognome")
            numero = b3.text_input("Numero")
            ruolo = b4.text_input("Ruolo (opz.)")

            s1, s2, s3, s4, s5, s6 = st.columns(6)
            quintetto = s1.checkbox("Quintetto Base")
            punti = s2.number_input("Punti", min_value=0, max_value=100, value=0, step=1)
            p2 = s3.number_input("2P Segnati", min_value=0, max_value=50, value=0, step=1)
            p3 = s4.number_input("3P Segnati", min_value=0, max_value=30, value=0, step=1)
            tl_m = s5.number_input("TL Segnati", min_value=0, max_value=40, value=0, step=1)
            tl_x = s6.number_input("TL Sbagliati", min_value=0, max_value=40, value=0, step=1)

            note_p = st.text_input("Note / Statistiche qualitative giocatore")

            if st.form_submit_button("Salva Giocatore"):
                if not giocatore.strip():
                    st.error("Inserisci Nome e Cognome del giocatore.")
                else:
                    new_box = pd.DataFrame(
                        [
                            {
                                "ID_Partita": game_id,
                                "Girone": g["Girone"],
                                "Squadra": tab_sq,
                                "Quintetto_Base": quintetto,
                                "Numero": numero.strip(),
                                "Ruolo": ruolo.strip(),
                                "Giocatore": giocatore.strip(),
                                "Punti": int(punti),
                                "2P_Segnati": int(p2),
                                "3P_Segnati": int(p3),
                                "TL_Segnati": int(tl_m),
                                "TL_Sbagliati": int(tl_x),
                                "Note": note_p.strip(),
                            }
                        ]
                    )
                    box_df = pd.concat([box_df, new_box], ignore_index=True)
                    save_box(box_df)
                    st.success("Giocatore aggiunto al tabellino.")
                    st.rerun()


# ==========================================
# LOGIN STAFF
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

qp_game = st.query_params.get("game", None)
qp_girone = st.query_params.get("girone", None)
if qp_game:
    st.session_state["selected_game_id"] = qp_game

if not st.session_state.authenticated:
    st.title("🏀 DR2 Puglia — Area Riservata Staff")
    st.caption("Inserisci la password dello staff per accedere a calendari, gironi e tabellini.")
    pwd = st.text_input("Password", type="password")
    if st.button("Accedi"):
        if pwd == STAFF_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Password non valida.")
    st.stop()

teams_df, games_df, box_df = load_data()
logo_lookup = {
    row["Squadra"]: row["Logo_URL"].strip()
    for _, row in teams_df.iterrows()
    if row["Squadra"].strip()
}

if "selected_game_id" not in st.session_state:
    st.session_state["selected_game_id"] = None

default_nav_idx = 1 if st.session_state["selected_game_id"] else 0

st.sidebar.title("🏀 DR2 Puglia")
page = st.sidebar.radio("Navigazione", ["Gironi", "Calendario & Tabellini", "Gestione Squadre"], index=default_nav_idx)
if st.sidebar.button("Esci"):
    st.session_state.authenticated = False
    st.session_state["selected_game_id"] = None
    st.query_params.clear()
    st.rerun()

# ==========================================
# PAGINA 1: GIRONI (A, B, C) & ROSTER
# ==========================================
if page == "Gironi":
    st.session_state["selected_game_id"] = None
    if "game" in st.query_params:
        del st.query_params["game"]
    st.title("Gironi — Divisione Regionale 2 Puglia")
    st.caption("1ª sale in DR1 · 2ª Play-off · 3ª Play-off solo migliore terza · Ultime 4 Playout.")

    girone_sel = st.selectbox("Seleziona Girone", ["Girone A", "Girone B", "Girone C"])
    board = compute_standings_for_girone(girone_sel, teams_df, games_df)
    best_third_team, ranked_thirds = compute_best_third(teams_df, games_df)

    if not board:
        st.info(f"Nessuna squadra inserita in **{girone_sel}** al momento.")
    else:
        st.subheader(f"Classifica — {girone_sel}")
        render_standings_board(board, girone_sel, best_third_team, ranked_thirds)

        ordered_teams = [x["Squadra"] for x in board]
        st.divider()
        st.subheader("Dettaglio Squadra e Roster")
        selected_team = st.selectbox(
            "Seleziona una squadra per vedere logo, record, roster e statistiche",
            ordered_teams,
        )

        g_teams = teams_df[teams_df["Girone"] == girone_sel].reset_index(drop=True)
        team_info = g_teams[g_teams["Squadra"] == selected_team].iloc[0]
        m_sel = compute_team_metrics(selected_team, girone_sel, games_df)

        col1, col2 = st.columns([1, 4])
        with col1:
            if team_info["Logo_URL"].strip():
                st.image(team_info["Logo_URL"].strip(), width=100)
            else:
                st.markdown("### 🏀")
        with col2:
            st.markdown(f"### {selected_team}")
            st.markdown(
                f"**PTS:** {m_sel['PTS']} · **Record (W-L):** {m_sel['V']}-{m_sel['S']} · "
                f"**P:** {m_sel['PG']} · **DIFF:** {format_dp(m_sel['DP'])} · "
                f"**Streak:** {format_streak_text(m_sel['STREAK'])}"
            )
            if team_info["Note_Tattiche"].strip():
                st.info(f"**Note tattiche:** {team_info['Note_Tattiche']}")

        roster_df = compute_roster_stats(selected_team, girone_sel, box_df)
        st.markdown("#### Roster e Statistiche Giocatori")
        if roster_df.empty:
            st.warning("Nessun tabellino registrato ancora per questa squadra.")
        else:
            st.dataframe(roster_df, use_container_width=True, hide_index=True)

# ==========================================
# PAGINA 2: CALENDARIO & TABELLINI
# ==========================================
elif page == "Calendario & Tabellini":
    g_options = ["Girone A", "Girone B", "Girone C"]
    default_g_idx = g_options.index(qp_girone) if qp_girone in g_options else 0
    girone_cal = st.selectbox("Girone", g_options, index=default_g_idx, key="cal_girone")
    cal_teams = teams_df[teams_df["Girone"] == girone_cal]["Squadra"].tolist()

    if st.session_state["selected_game_id"]:
        render_match_center(
            st.session_state["selected_game_id"],
            teams_df,
            games_df,
            box_df,
            logo_lookup,
            cal_teams,
        )
    else:
        st.title("Calendario & Tabellini")
        st.caption("Clicca direttamente su una partita per aprire parziali per quarto, tabellini e note giocatori.")

        with st.expander("➕ Aggiungi nuova partita al calendario"):
            with st.form("add_game_form"):
                c1, c2, c3 = st.columns(3)
                giornata = c1.number_input("Giornata (1-11 Andata, 12-22 Ritorno)", min_value=1, max_value=40, value=1, step=1)
                data_gara = c2.text_input("Data e Ora (es. Dom 29/11/2026 18:00)", value="")
                stato = c3.selectbox("Stato", ["Da giocare", "Giocata"])

                c4, c5, c6, c7 = st.columns([3, 1, 1, 3])
                if len(cal_teams) >= 2:
                    casa = c4.selectbox("Squadra Casa", cal_teams, index=0)
                    trasferta = c7.selectbox("Squadra Trasferta", cal_teams, index=1)
                else:
                    casa = c4.text_input("Squadra Casa")
                    trasferta = c7.text_input("Squadra Trasferta")

                pts_casa = c5.number_input("Pti Casa", min_value=0, max_value=200, value=0, step=1)
                pts_trasf = c6.number_input("Pti Trasf", min_value=0, max_value=200, value=0, step=1)

                submitted = st.form_submit_button("Salva Partita")
                if submitted:
                    if not casa or not trasferta or casa == trasferta:
                        st.error("Seleziona due squadre differenti per Casa e Trasferta.")
                    else:
                        game_id = f"{girone_cal.replace(' ', '')}_G{giornata}_{casa[:8]}_{trasferta[:8]}_{len(games_df)+1}"
                        new_row = pd.DataFrame(
                            [
                                {
                                    "ID_Partita": game_id,
                                    "Girone": girone_cal,
                                    "Giornata": int(giornata),
                                    "Data": data_gara,
                                    "Casa": casa,
                                    "Trasferta": trasferta,
                                    "Punti_Casa": int(pts_casa),
                                    "Punti_Trasferta": int(pts_trasf),
                                    "Stato": stato,
                                    "Q1_C": 0,
                                    "Q2_C": 0,
                                    "Q3_C": 0,
                                    "Q4_C": 0,
                                    "OT_C": 0,
                                    "Q1_T": 0,
                                    "Q2_T": 0,
                                    "Q3_T": 0,
                                    "Q4_T": 0,
                                    "OT_T": 0,
                                    "Note_Gara": "",
                                }
                            ]
                        )
                        games_df = pd.concat([games_df, new_row], ignore_index=True)
                        save_games(games_df)
                        st.success("Partita salvata.")
                        st.rerun()

        g_games = games_df[games_df["Girone"] == girone_cal].copy()
        if g_games.empty:
            st.info("Nessuna partita ancora presente per questo girone.")
        else:
            g_games_sorted = g_games.sort_values(by=["Giornata", "ID_Partita"]).reset_index(drop=True)
            andata_rounds = sorted([int(r) for r in g_games_sorted["Giornata"].unique() if int(r) <= 11])
            ritorno_rounds = sorted([int(r) for r in g_games_sorted["Giornata"].unique() if int(r) > 11])

            base_turns = sorted(list(set(andata_rounds + [r - 11 for r in ritorno_rounds])))
            turn_filter = st.selectbox(
                "Visualizza Turno (Andata a sinistra / Ritorno a destra)",
                ["Tutti i turni (1ª–11ª)"] + [f"Turno {t} (G{t} Andata / G{t} Ritorno)" for t in base_turns],
            )

            turns_to_show = (
                base_turns
                if turn_filter.startswith("Tutti")
                else [int(turn_filter.split()[1])]
            )

            head_l, head_r = st.columns(2)
            head_l.markdown("### GIRONE DI ANDATA")
            head_r.markdown("### GIRONE DI RITORNO")

            for t_num in turns_to_show:
                col_and, col_rit = st.columns(2)
                with col_and:
                    df_and = g_games_sorted[g_games_sorted["Giornata"] == t_num]
                    render_round_card(t_num, df_and, logo_lookup, girone_cal, is_ritorno=False)
                with col_rit:
                    df_rit = g_games_sorted[g_games_sorted["Giornata"] == (t_num + 11)]
                    render_round_card(t_num + 11, df_rit, logo_lookup, girone_cal, is_ritorno=True)

# ==========================================
# PAGINA 3: GESTIONE SQUADRE, RIPRISTINO & EXPORT
# ==========================================
elif page == "Gestione Squadre":
    st.session_state["selected_game_id"] = None
    if "game" in st.query_params:
        del st.query_params["game"]
    st.title("Gestione Squadre e Dati")
    st.caption("Modifica squadre/loghi/note o ripristina tutti i gironi ufficiali.")

    girone_edit = st.selectbox("Girone da modificare", ["Girone A", "Girone B", "Girone C"], key="edit_girone")
    sub_teams = teams_df[teams_df["Girone"] == girone_edit].reset_index(drop=True)

    edited_df = st.data_editor(
        sub_teams,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
    )

    if st.button("Salva Modifiche Squadre"):
        edited_df["Girone"] = girone_edit
        other_teams = teams_df[teams_df["Girone"] != girone_edit]
        updated_all = pd.concat([other_teams, edited_df], ignore_index=True)
        save_teams(updated_all)
        st.success("Squadre salvate.")
        st.rerun()

    st.divider()
    st.subheader("Ripristino Dati Ufficiali (Gironi A, B e C)")
    if st.button("🔄 Ripristina Tutti i Gironi e Calendari Ufficiali (A, B, C)"):
        reset_official_data()
        st.success("33 squadre e calendari completi (G1–G22) di Gironi A, B e C ripristinati.")
        st.rerun()

    st.divider()
    st.subheader("Esporta Dati (CSV)")
    c_exp1, c_exp2, c_exp3 = st.columns(3)
    c_exp1.download_button("Scarica Squadre CSV", teams_df.to_csv(index=False).encode("utf-8"), "squadre.csv", "text/csv")
    c_exp2.download_button("Scarica Partite CSV", games_df.to_csv(index=False).encode("utf-8"), "partite.csv", "text/csv")
    c_exp3.download_button("Scarica Tabellini CSV", box_df.to_csv(index=False).encode("utf-8"), "tabellini.csv", "text/csv")
