import os
from pathlib import Path
from urllib.parse import quote
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="DR2 Puglia - Scouting & Tabellini",
    page_icon="🏀",
    layout="wide",
)

# ==========================================
# IMPOSTAZIONI ACCESSO STAFF
# ==========================================
STAFF_PASSWORD = os.environ.get("DR2_STAFF_PASSWORD", "dr2puglia2026")
RAW_BASE_URL = "https://raw.githubusercontent.com/GioviCI00/dr2-girone-a/main/"

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
TEAMS_FILE = DATA_DIR / "squadre.csv"
GAMES_FILE = DATA_DIR / "partite.csv"
BOX_FILE = DATA_DIR / "tabellini.csv"


def logo_url(filename: str) -> str:
    return RAW_BASE_URL + quote(filename)


DEFAULT_TEAMS = [
    {"Girone": "Girone A", "Squadra": "Angiulli Bari", "Logo_URL": logo_url("Angiulli Basket Bari.png"), "Note_Tattiche": ""},
    {"Girone": "Girone A", "Squadra": "A.G.S.D. Toritto", "Logo_URL": logo_url("A.G.S.D. TORITTO.png"), "Note_Tattiche": ""},
    {"Girone": "Girone A", "Squadra": "Orsa Capurso", "Logo_URL": logo_url("orsa capurso.png"), "Note_Tattiche": ""},
    {"Girone": "Girone A", "Squadra": "Nuova Matteotti Corato", "Logo_URL": logo_url("Nuova Matteotti Corato.png"), "Note_Tattiche": ""},
    {"Girone": "Girone A", "Squadra": "Magic Bari", "Logo_URL": logo_url("Magic Bari.png"), "Note_Tattiche": ""},
    {"Girone": "Girone A", "Squadra": "Mediterranea Cerignola", "Logo_URL": logo_url("Mediterranea Cerignola.png"), "Note_Tattiche": ""},
    {"Girone": "Girone A", "Squadra": "Vigor San Severo", "Logo_URL": logo_url("Vigor San Severo.png"), "Note_Tattiche": ""},
    {"Girone": "Girone A", "Squadra": "Basket Bitritto", "Logo_URL": logo_url("basket bitritto.png"), "Note_Tattiche": ""},
    {"Girone": "Girone A", "Squadra": "Fortitudo BK Apricena", "Logo_URL": logo_url("Fortitudo Basket Apricena.png"), "Note_Tattiche": ""},
    {"Girone": "Girone A", "Squadra": "Olimpia Corato", "Logo_URL": logo_url("Olimpia Corato.png"), "Note_Tattiche": ""},
    {"Girone": "Girone A", "Squadra": "Virtus Foggia", "Logo_URL": logo_url("Virtus Foggia.png"), "Note_Tattiche": ""},
]

# Calendario ufficiale CU n. 91 (Squadra A = Casa, Squadra B = Trasferta)
DEFAULT_GAMES_RAW = [
    # 1ª Giornata di andata
    ("G01_1867", 1, "Sab 07/11/2026 19:00", "Nuova Matteotti Corato", "Olimpia Corato", 72, 67, "Giocata"),
    ("G01_1868", 1, "Dom 08/11/2026 18:30", "Fortitudo BK Apricena", "Mediterranea Cerignola", 50, 76, "Giocata"),
    ("G01_1869", 1, "Dom 08/11/2026 18:00", "Angiulli Bari", "Magic Bari", 68, 50, "Giocata"),
    ("G01_1870", 1, "Sab 07/11/2026 18:30", "Virtus Foggia", "Orsa Capurso", 78, 87, "Giocata"),
    ("G01_1871", 1, "Dom 08/11/2026 18:30", "Basket Bitritto", "A.G.S.D. Toritto", 62, 81, "Giocata"),

    # 2ª Giornata di andata
    ("G02_1872", 2, "Sab 14/11/2026 18:00", "Virtus Foggia", "Vigor San Severo", 65, 69, "Giocata"),
    ("G02_1873", 2, "Dom 15/11/2026 20:15", "Olimpia Corato", "Fortitudo BK Apricena", 50, 56, "Giocata"),
    ("G02_1874", 2, "Dom 15/11/2026 19:00", "Mediterranea Cerignola", "Nuova Matteotti Corato", 49, 59, "Giocata"),
    ("G02_1875", 2, "Dom 15/11/2026 19:00", "A.G.S.D. Toritto", "Angiulli Bari", 85, 96, "Giocata"),
    ("G02_1876", 2, "Dom 15/11/2026 17:30", "Magic Bari", "Basket Bitritto", 56, 48, "Giocata"),

    # 3ª Giornata di andata
    ("G03_1877", 3, "Sab 21/11/2026 19:30", "Angiulli Bari", "Mediterranea Cerignola", 86, 75, "Giocata"),
    ("G03_1878", 3, "Dom 22/11/2026 18:30", "Fortitudo BK Apricena", "Magic Bari", 69, 79, "Giocata"),
    ("G03_1879", 3, "Dom 22/11/2026 18:00", "Orsa Capurso", "Vigor San Severo", 78, 75, "Giocata"),
    ("G03_1880", 3, "Sab 21/11/2026 19:00", "Nuova Matteotti Corato", "A.G.S.D. Toritto", 64, 77, "Giocata"),
    ("G03_1881", 3, "Dom 22/11/2026 18:30", "Basket Bitritto", "Olimpia Corato", 51, 50, "Giocata"),

    # 4ª Giornata di andata
    ("G04_1882", 4, "Dom 29/11/2026 17:30", "Magic Bari", "Nuova Matteotti Corato", 0, 0, "Da giocare"),
    ("G04_1883", 4, "Dom 29/11/2026 19:00", "A.G.S.D. Toritto", "Fortitudo BK Apricena", 0, 0, "Da giocare"),
    ("G04_1884", 4, "Sab 28/11/2026 18:30", "Virtus Foggia", "Angiulli Bari", 0, 0, "Da giocare"),
    ("G04_1885", 4, "Dom 29/11/2026 18:00", "Orsa Capurso", "Olimpia Corato", 0, 0, "Da giocare"),
    ("G04_1886", 4, "Sab 28/11/2026 19:45", "Vigor San Severo", "Basket Bitritto", 0, 0, "Da giocare"),

    # 5ª Giornata di andata
    ("G05_1887", 5, "Dom 06/12/2026 17:30", "Magic Bari", "Orsa Capurso", 0, 0, "Da giocare"),
    ("G05_1888", 5, "Dom 06/12/2026 19:00", "Mediterranea Cerignola", "A.G.S.D. Toritto", 0, 0, "Da giocare"),
    ("G05_1889", 5, "Dom 06/12/2026 20:15", "Olimpia Corato", "Vigor San Severo", 0, 0, "Da giocare"),
    ("G05_1890", 5, "Dom 06/12/2026 18:30", "Basket Bitritto", "Virtus Foggia", 0, 0, "Da giocare"),
    ("G05_1891", 5, "Sab 05/12/2026 19:30", "Angiulli Bari", "Nuova Matteotti Corato", 0, 0, "Da giocare"),

    # 6ª Giornata di andata
    ("G06_1892", 6, "Dom 13/12/2026 18:30", "Fortitudo BK Apricena", "Basket Bitritto", 0, 0, "Da giocare"),
    ("G06_1893", 6, "Dom 13/12/2026 20:15", "Olimpia Corato", "Magic Bari", 0, 0, "Da giocare"),
    ("G06_1894", 6, "Sab 12/12/2026 19:00", "Nuova Matteotti Corato", "Vigor San Severo", 0, 0, "Da giocare"),
    ("G06_1895", 6, "Dom 13/12/2026 18:00", "Orsa Capurso", "Angiulli Bari", 0, 0, "Da giocare"),
    ("G06_1896", 6, "Gio 17/12/2026 20:00", "Virtus Foggia", "Mediterranea Cerignola", 0, 0, "Da giocare"),

    # 7ª Giornata di andata
    ("G07_1897", 7, "Sab 19/12/2026 18:00", "Vigor San Severo", "Fortitudo BK Apricena", 0, 0, "Da giocare"),
    ("G07_1898", 7, "Dom 20/12/2026 19:00", "Mediterranea Cerignola", "Olimpia Corato", 0, 0, "Da giocare"),
    ("G07_1899", 7, "Dom 20/12/2026 18:30", "Basket Bitritto", "Nuova Matteotti Corato", 0, 0, "Da giocare"),
    ("G07_1900", 7, "Dom 20/12/2026 19:00", "A.G.S.D. Toritto", "Orsa Capurso", 0, 0, "Da giocare"),
    ("G07_1901", 7, "Dom 20/12/2026 17:30", "Magic Bari", "Virtus Foggia", 0, 0, "Da giocare"),

    # 8ª Giornata di andata
    ("G08_1902", 8, "Dom 10/01/2027 18:30", "Fortitudo BK Apricena", "Angiulli Bari", 0, 0, "Da giocare"),
    ("G08_1903", 8, "Dom 10/01/2027 19:00", "A.G.S.D. Toritto", "Vigor San Severo", 0, 0, "Da giocare"),
    ("G08_1904", 8, "Dom 10/01/2027 19:00", "Mediterranea Cerignola", "Magic Bari", 0, 0, "Da giocare"),
    ("G08_1905", 8, "Sab 09/01/2027 19:00", "Nuova Matteotti Corato", "Orsa Capurso", 0, 0, "Da giocare"),
    ("G08_1906", 8, "Dom 10/01/2027 20:15", "Olimpia Corato", "Virtus Foggia", 0, 0, "Da giocare"),

    # 9ª Giornata di andata
    ("G09_1907", 9, "Sab 16/01/2027 18:00", "Vigor San Severo", "Magic Bari", 0, 0, "Da giocare"),
    ("G09_1908", 9, "Sab 16/01/2027 18:30", "Virtus Foggia", "A.G.S.D. Toritto", 0, 0, "Da giocare"),
    ("G09_1909", 9, "Dom 17/01/2027 18:00", "Orsa Capurso", "Mediterranea Cerignola", 0, 0, "Da giocare"),
    ("G09_1910", 9, "Sab 16/01/2027 19:30", "Angiulli Bari", "Basket Bitritto", 0, 0, "Da giocare"),
    ("G09_1911", 9, "Sab 16/01/2027 17:00", "Nuova Matteotti Corato", "Fortitudo BK Apricena", 0, 0, "Da giocare"),

    # 10ª Giornata di andata
    ("G10_1912", 10, "Dom 24/01/2027 19:00", "A.G.S.D. Toritto", "Olimpia Corato", 0, 0, "Da giocare"),
    ("G10_1913", 10, "Dom 24/01/2027 19:00", "Mediterranea Cerignola", "Basket Bitritto", 0, 0, "Da giocare"),
    ("G10_1914", 10, "Dom 24/01/2027 18:00", "Orsa Capurso", "Fortitudo BK Apricena", 0, 0, "Da giocare"),
    ("G10_1915", 10, "Sab 23/01/2027 19:30", "Angiulli Bari", "Vigor San Severo", 0, 0, "Da giocare"),
    ("G10_1916", 10, "Sab 23/01/2027 18:30", "Virtus Foggia", "Nuova Matteotti Corato", 0, 0, "Da giocare"),

    # 11ª Giornata di andata
    ("G11_1917", 11, "Dom 31/01/2027 17:30", "Magic Bari", "A.G.S.D. Toritto", 0, 0, "Da giocare"),
    ("G11_1918", 11, "Dom 31/01/2027 18:30", "Basket Bitritto", "Orsa Capurso", 0, 0, "Da giocare"),
    ("G11_1919", 11, "Dom 31/01/2027 18:30", "Fortitudo BK Apricena", "Virtus Foggia", 0, 0, "Da giocare"),
    ("G11_1920", 11, "Dom 31/01/2027 20:15", "Olimpia Corato", "Angiulli Bari", 0, 0, "Da giocare"),
    ("G11_1921", 11, "Sab 30/01/2027 18:00", "Vigor San Severo", "Mediterranea Cerignola", 0, 0, "Da giocare"),

    # 1ª Giornata di ritorno
    ("G12_1922", 12, "Dom 07/02/2027 18:00", "Orsa Capurso", "Virtus Foggia", 0, 0, "Da giocare"),
    ("G12_1923", 12, "Dom 07/02/2027 19:00", "Mediterranea Cerignola", "Fortitudo BK Apricena", 0, 0, "Da giocare"),
    ("G12_1924", 12, "Dom 07/02/2027 17:30", "Magic Bari", "Angiulli Bari", 0, 0, "Da giocare"),
    ("G12_1925", 12, "Sab 06/02/2027 19:00", "A.G.S.D. Toritto", "Basket Bitritto", 0, 0, "Da giocare"),
    ("G12_1926", 12, "Dom 07/02/2027 20:15", "Olimpia Corato", "Nuova Matteotti Corato", 0, 0, "Da giocare"),

    # 2ª Giornata di ritorno
    ("G13_1927", 13, "Sab 13/02/2027 18:30", "Virtus Foggia", "Vigor San Severo", 0, 0, "Da giocare"),
    ("G13_1928", 13, "Sab 13/02/2027 19:30", "Angiulli Bari", "A.G.S.D. Toritto", 0, 0, "Da giocare"),
    ("G13_1929", 13, "Sab 13/02/2027 19:00", "Nuova Matteotti Corato", "Mediterranea Cerignola", 0, 0, "Da giocare"),
    ("G13_1930", 13, "Dom 14/02/2027 20:15", "Basket Bitritto", "Magic Bari", 0, 0, "Da giocare"),
    ("G13_1931", 13, "Dom 14/02/2027 18:30", "Fortitudo BK Apricena", "Olimpia Corato", 0, 0, "Da giocare"),

    # 3ª Giornata di ritorno
    ("G14_1932", 14, "Sab 20/02/2027 18:00", "Orsa Capurso", "Vigor San Severo", 0, 0, "Da giocare"),
    ("G14_1933", 14, "Dom 21/02/2027 19:00", "A.G.S.D. Toritto", "Nuova Matteotti Corato", 0, 0, "Da giocare"),
    ("G14_1934", 14, "Dom 21/02/2027 20:15", "Olimpia Corato", "Basket Bitritto", 0, 0, "Da giocare"),
    ("G14_1935", 14, "Dom 21/02/2027 19:00", "Mediterranea Cerignola", "Angiulli Bari", 0, 0, "Da giocare"),
    ("G14_1936", 14, "Dom 21/02/2027 17:30", "Magic Bari", "Fortitudo BK Apricena", 0, 0, "Da giocare"),

    # 4ª Giornata di ritorno
    ("G15_1937", 15, "Sab 27/02/2027 20:00", "Nuova Matteotti Corato", "Magic Bari", 0, 0, "Da giocare"),
    ("G15_1938", 15, "Dom 28/02/2027 18:30", "Fortitudo BK Apricena", "A.G.S.D. Toritto", 0, 0, "Da giocare"),
    ("G15_1939", 15, "Dom 28/02/2027 20:15", "Basket Bitritto", "Vigor San Severo", 0, 0, "Da giocare"),
    ("G15_1940", 15, "Dom 28/02/2027 20:15", "Olimpia Corato", "Orsa Capurso", 0, 0, "Da giocare"),
    ("G15_1941", 15, "Sab 27/02/2027 19:30", "Angiulli Bari", "Virtus Foggia", 0, 0, "Da giocare"),

    # 5ª Giornata di ritorno
    ("G16_1942", 16, "Sab 06/03/2027 18:00", "Vigor San Severo", "Olimpia Corato", 0, 0, "Da giocare"),
    ("G16_1943", 16, "Dom 07/03/2027 18:00", "Orsa Capurso", "Magic Bari", 0, 0, "Da giocare"),
    ("G16_1944", 16, "Dom 07/03/2027 19:00", "A.G.S.D. Toritto", "Mediterranea Cerignola", 0, 0, "Da giocare"),
    ("G16_1945", 16, "Sab 06/03/2027 17:00", "Nuova Matteotti Corato", "Angiulli Bari", 0, 0, "Da giocare"),
    ("G16_1946", 16, "Sab 06/03/2027 18:30", "Virtus Foggia", "Basket Bitritto", 0, 0, "Da giocare"),

    # 6ª Giornata di ritorno
    ("G17_1947", 17, "Sab 13/03/2027 19:30", "Angiulli Bari", "Orsa Capurso", 0, 0, "Da giocare"),
    ("G17_1948", 17, "Dom 14/03/2027 19:00", "Mediterranea Cerignola", "Virtus Foggia", 0, 0, "Da giocare"),
    ("G17_1949", 17, "Sab 13/03/2027 18:00", "Vigor San Severo", "Nuova Matteotti Corato", 0, 0, "Da giocare"),
    ("G17_1950", 17, "Dom 14/03/2027 17:30", "Magic Bari", "Olimpia Corato", 0, 0, "Da giocare"),
    ("G17_1951", 17, "Dom 14/03/2027 18:30", "Basket Bitritto", "Fortitudo BK Apricena", 0, 0, "Da giocare"),

    # 7ª Giornata di ritorno
    ("G18_1952", 18, "Dom 21/03/2027 18:30", "Virtus Foggia", "Magic Bari", 0, 0, "Da giocare"),
    ("G18_1953", 18, "Dom 21/03/2027 18:00", "Orsa Capurso", "A.G.S.D. Toritto", 0, 0, "Da giocare"),
    ("G18_1954", 18, "Dom 21/03/2027 18:30", "Fortitudo BK Apricena", "Vigor San Severo", 0, 0, "Da giocare"),
    ("G18_1955", 18, "Sab 20/03/2027 19:00", "Nuova Matteotti Corato", "Basket Bitritto", 0, 0, "Da giocare"),
    ("G18_1956", 18, "Dom 21/03/2027 20:15", "Olimpia Corato", "Mediterranea Cerignola", 0, 0, "Da giocare"),

    # 8ª Giornata di ritorno
    ("G19_1957", 19, "Sab 03/04/2027 18:30", "Olimpia Corato", "Virtus Foggia", 0, 0, "Da giocare"),
    ("G19_1958", 19, "Sab 03/04/2027 18:00", "Vigor San Severo", "A.G.S.D. Toritto", 0, 0, "Da giocare"),
    ("G19_1959", 19, "Dom 04/04/2027 17:30", "Magic Bari", "Mediterranea Cerignola", 0, 0, "Da giocare"),
    ("G19_1960", 19, "Sab 03/04/2027 19:30", "Angiulli Bari", "Fortitudo BK Apricena", 0, 0, "Da giocare"),
    ("G19_1961", 19, "Dom 04/04/2027 18:00", "Orsa Capurso", "Nuova Matteotti Corato", 0, 0, "Da giocare"),

    # 9ª Giornata di ritorno
    ("G20_1962", 20, "Dom 11/04/2027 19:00", "Mediterranea Cerignola", "Orsa Capurso", 0, 0, "Da giocare"),
    ("G20_1963", 20, "Dom 11/04/2027 17:30", "Magic Bari", "Vigor San Severo", 0, 0, "Da giocare"),
    ("G20_1964", 20, "Dom 11/04/2027 18:30", "Fortitudo BK Apricena", "Nuova Matteotti Corato", 0, 0, "Da giocare"),
    ("G20_1965", 20, "Dom 11/04/2027 19:00", "A.G.S.D. Toritto", "Virtus Foggia", 0, 0, "Da giocare"),
    ("G20_1966", 20, "Dom 11/04/2027 18:30", "Basket Bitritto", "Angiulli Bari", 0, 0, "Da giocare"),

    # 10ª Giornata di ritorno
    ("G21_1967", 21, "Dom 18/04/2027 20:15", "Olimpia Corato", "A.G.S.D. Toritto", 0, 0, "Da giocare"),
    ("G21_1968", 21, "Dom 18/04/2027 18:30", "Basket Bitritto", "Mediterranea Cerignola", 0, 0, "Da giocare"),
    ("G21_1969", 21, "Sab 17/04/2027 18:00", "Vigor San Severo", "Angiulli Bari", 0, 0, "Da giocare"),
    ("G21_1970", 21, "Dom 18/04/2027 18:30", "Fortitudo BK Apricena", "Orsa Capurso", 0, 0, "Da giocare"),
    ("G21_1971", 21, "Sab 17/04/2027 19:00", "Nuova Matteotti Corato", "Virtus Foggia", 0, 0, "Da giocare"),

    # 11ª Giornata di ritorno
    ("G22_1972", 22, "Sab 24/04/2027 18:00", "Orsa Capurso", "Basket Bitritto", 0, 0, "Da giocare"),
    ("G22_1973", 22, "Dom 25/04/2027 19:00", "A.G.S.D. Toritto", "Magic Bari", 0, 0, "Da giocare"),
    ("G22_1974", 22, "Dom 25/04/2027 19:00", "Mediterranea Cerignola", "Vigor San Severo", 0, 0, "Da giocare"),
    ("G22_1975", 22, "Sab 24/04/2027 18:30", "Virtus Foggia", "Fortitudo BK Apricena", 0, 0, "Da giocare"),
    ("G22_1976", 22, "Sab 24/04/2027 19:30", "Angiulli Bari", "Olimpia Corato", 0, 0, "Da giocare"),
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
                "Girone": "Girone A",
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
            for gid, giornata, data_ora, casa, trasferta, pts_casa, pts_trasf, stato in DEFAULT_GAMES_RAW
        ]
    )


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


def compute_team_metrics(team_name: str, girone: str, games_df: pd.DataFrame) -> dict:
    played = games_df[
        (games_df["Girone"] == girone) & (games_df["Stato"].str.lower() == "giocata")
    ].copy()
    played = played.sort_values(by=["Giornata", "ID_Partita"]).reset_index(drop=True)

    pg = 0
    wins = 0
    losses = 0
    pf = 0
    pa = 0
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

    pts = wins * 2
    dp = pf - pa
    streak = "—"
    if outcomes:
        last = outcomes[-1]
        cnt = 0
        for item in reversed(outcomes):
            if item == last:
                cnt += 1
            else:
                break
        streak = f"{cnt}{last}"

    return {
        "PTS": pts,
        "PG": pg,
        "V": wins,
        "S": losses,
        "DP": dp,
        "STREAK": streak,
    }


def compute_standings_for_girone(girone: str, teams_df: pd.DataFrame, games_df: pd.DataFrame) -> list:
    g_teams = teams_df[teams_df["Girone"] == girone]
    if g_teams.empty:
        return []
    rows = []
    for _, trow in g_teams.iterrows():
        m = compute_team_metrics(trow["Squadra"], girone, games_df)
        rows.append(
            {
                "Girone": girone,
                "Squadra": trow["Squadra"],
                "Logo_URL": trow["Logo_URL"],
                "PTS": m["PTS"],
                "PG": m["PG"],
                "V": m["V"],
                "S": m["S"],
                "DP": m["DP"],
                "STREAK": m["STREAK"],
            }
        )
    return sorted(rows, key=lambda x: (-x["PTS"], -x["DP"], -x["V"], -x["PG"], x["Squadra"]))


def compute_best_third(teams_df: pd.DataFrame, games_df: pd.DataFrame):
    thirds = []
    for g_name in ["Girone A", "Girone B", "Girone C"]:
        st_list = compute_standings_for_girone(g_name, teams_df, games_df)
        if len(st_list) >= 3:
            thirds.append(st_list[2])
    if not thirds:
        return None, []
    ranked_thirds = sorted(thirds, key=lambda x: (-x["PTS"], -x["DP"], -x["V"], x["Squadra"]))
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
            grid-template-columns: 56px 52px 1fr 64px 56px 56px 56px 76px 84px;
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
            grid-template-columns: 56px 52px 1fr 64px 56px 56px 56px 76px 84px;
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
        '<div>PTS</div><div>PG</div><div>V</div><div>S</div><div>DP</div><div>STREAK</div>'
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
                label_3 = "3° POSTO — MIGLIORE TERZA (IN ATTESA DATI GIRONI B/C)"
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

        html_parts.append(
            f'<div class="s-row {row_class}">'
            f'<div class="s-pos">{idx}</div>'
            f'<div>{logo_html}</div>'
            f'<div><div class="s-team">{item["Squadra"]}</div></div>'
            f'<div class="s-pts">{item["PTS"]}</div>'
            f'<div class="s-val">{item["PG"]}</div>'
            f'<div class="s-val">{item["V"]}</div>'
            f'<div class="s-val">{item["S"]}</div>'
            f'<div class="s-val">{dp_str}</div>'
            f'<div class="s-val">{item["STREAK"]}</div>'
            f'</div>'
        )

    html_parts.append("</div>")
    st.markdown("".join(html_parts), unsafe_allow_html=True)

    if ranked_thirds:
        st.markdown("#### Confronto Automatico Migliore Terza (Punti → Differenza Punti)")
        t_rows = []
        for rank_i, t_item in enumerate(ranked_thirds, start=1):
            t_rows.append(
                {
                    "Pos": rank_i,
                    "Girone": t_item["Girone"],
                    "Squadra": t_item["Squadra"],
                    "PTS": t_item["PTS"],
                    "PG": t_item["PG"],
                    "V": t_item["V"],
                    "S": t_item["S"],
                    "DP": format_dp(t_item["DP"]),
                    "Stato": "QUALIFICATA PLAY-OFF" if rank_i == 1 else "FUORI PLAY-OFF",
                }
            )
        st.dataframe(pd.DataFrame(t_rows), use_container_width=True, hide_index=True)


def render_round_card(round_num: int, round_games: pd.DataFrame, logo_map: dict, is_ritorno: bool = False, key_prefix: str = ""):
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
            margin-bottom: 6px;
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
        .match-row {
            display: grid;
            grid-template-columns: 92px 1fr 44px;
            gap: 10px;
            align-items: center;
            padding: 8px 14px;
            border-bottom: 1px solid #20252e;
        }
        .match-row:last-child { border-bottom: none; }
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
        parts.append("</div>")
        st.markdown("".join(parts), unsafe_allow_html=True)
        return

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

        row_html = (
            f'<div class="round-box" style="margin-bottom:4px;">'
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
            f'</div></div>'
        )
        c_card, c_btn = st.columns([6, 1.3])
        with c_card:
            st.markdown(row_html, unsafe_allow_html=True)
        with c_btn:
            if st.button("Dettagli", key=f"open_{key_prefix}_{g['ID_Partita']}", use_container_width=True):
                st.session_state["selected_game_id"] = g["ID_Partita"]
                st.session_state["match_tab"] = "RIASSUNTO"
                st.rerun()


def render_match_center(game_id: str, teams_df: pd.DataFrame, games_df: pd.DataFrame, box_df: pd.DataFrame, logo_map: dict, cal_teams: list):
    matches = games_df[games_df["ID_Partita"] == game_id]
    if matches.empty:
        st.session_state["selected_game_id"] = None
        st.rerun()

    idx = matches.index[0]
    g = games_df.loc[idx]

    if st.button("← Torna al Calendario"):
        st.session_state["selected_game_id"] = None
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

            note_p = st.text_input("Note / Statistiche qualitative giocatore (es. mano forte, tiro, falli, letture)")

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

st.sidebar.title("🏀 DR2 Puglia")
page = st.sidebar.radio("Navigazione", ["Gironi", "Calendario & Tabellini", "Gestione Squadre"])
if st.sidebar.button("Esci"):
    st.session_state.authenticated = False
    st.rerun()

# ==========================================
# PAGINA 1: GIRONI (A, B, C) & ROSTER
# ==========================================
if page == "Gironi":
    st.session_state["selected_game_id"] = None
    st.title("Gironi — Divisione Regionale 2 Puglia")
    st.caption("Classifica calcolata automaticamente dai risultati finali · Migliore 3ª calcolata per Punti e Differenza Punti.")

    girone_sel = st.selectbox("Seleziona Girone", ["Girone A", "Girone B", "Girone C"])
    board = compute_standings_for_girone(girone_sel, teams_df, games_df)
    best_third_team, ranked_thirds = compute_best_third(teams_df, games_df)

    if not board:
        st.info(
            f"Nessuna squadra inserita in **{girone_sel}** al momento. "
            "Quando caricheremo calendario e risultati di Girone B e Girone C, classifica e migliore terza si aggiorneranno in automatico."
        )
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
                f"**PTS:** {m_sel['PTS']} · **Record (V-S):** {m_sel['V']}-{m_sel['S']} · "
                f"**PG:** {m_sel['PG']} · **DP:** {format_dp(m_sel['DP'])} · **Streak:** {m_sel['STREAK']}"
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
    girone_cal = st.selectbox("Girone", ["Girone A", "Girone B", "Girone C"], key="cal_girone")
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
                    render_round_card(t_num, df_and, logo_lookup, is_ritorno=False, key_prefix="and")
                with col_rit:
                    df_rit = g_games_sorted[g_games_sorted["Giornata"] == (t_num + 11)]
                    render_round_card(t_num + 11, df_rit, logo_lookup, is_ritorno=True, key_prefix="rit")

# ==========================================
# PAGINA 3: GESTIONE SQUADRE, RIPRISTINO & EXPORT
# ==========================================
elif page == "Gestione Squadre":
    st.session_state["selected_game_id"] = None
    st.title("Gestione Squadre e Dati")
    st.caption("Modifica squadre/loghi/note o aggiungi squadre per Gironi B e C.")

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
    st.subheader("Ripristino Dati Ufficiali Girone A")
    if st.button("🔄 Ripristina 11 Squadre e Calendario Ufficiale"):
        save_teams(pd.DataFrame(DEFAULT_TEAMS))
        save_games(build_default_games_df())
        st.success("Squadre con loghi e calendario ufficiale ripristinati.")
        st.rerun()

    st.divider()
    st.subheader("Esporta Dati (CSV)")
    c_exp1, c_exp2, c_exp3 = st.columns(3)
    c_exp1.download_button("Scarica Squadre CSV", teams_df.to_csv(index=False).encode("utf-8"), "squadre.csv", "text/csv")
    c_exp2.download_button("Scarica Partite CSV", games_df.to_csv(index=False).encode("utf-8"), "partite.csv", "text/csv")
    c_exp3.download_button("Scarica Tabellini CSV", box_df.to_csv(index=False).encode("utf-8"), "tabellini.csv", "text/csv")
