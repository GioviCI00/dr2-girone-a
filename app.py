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
    {
        "Girone": "Girone A",
        "Squadra": "Angiulli Bari",
        "Logo_URL": logo_url("Angiulli Basket Bari.png"),
        "Note_Tattiche": "",
    },
    {
        "Girone": "Girone A",
        "Squadra": "A.G.S.D. Toritto",
        "Logo_URL": logo_url("A.G.S.D. TORITTO.png"),
        "Note_Tattiche": "",
    },
    {
        "Girone": "Girone A",
        "Squadra": "Orsa Capurso",
        "Logo_URL": logo_url("orsa capurso.png"),
        "Note_Tattiche": "",
    },
    {
        "Girone": "Girone A",
        "Squadra": "Nuova Matteotti Corato",
        "Logo_URL": logo_url("Nuova Matteotti Corato.png"),
        "Note_Tattiche": "",
    },
    {
        "Girone": "Girone A",
        "Squadra": "Magic Bari",
        "Logo_URL": logo_url("Magic Bari.png"),
        "Note_Tattiche": "",
    },
    {
        "Girone": "Girone A",
        "Squadra": "Mediterranea Cerignola",
        "Logo_URL": logo_url("Mediterranea Cerignola.png"),
        "Note_Tattiche": "",
    },
    {
        "Girone": "Girone A",
        "Squadra": "Vigor San Severo",
        "Logo_URL": logo_url("Vigor San Severo.png"),
        "Note_Tattiche": "",
    },
    {
        "Girone": "Girone A",
        "Squadra": "Basket Bitritto",
        "Logo_URL": logo_url("basket bitritto.png"),
        "Note_Tattiche": "",
    },
    {
        "Girone": "Girone A",
        "Squadra": "Fortitudo BK Apricena",
        "Logo_URL": logo_url("Fortitudo Basket Apricena.png"),
        "Note_Tattiche": "",
    },
    {
        "Girone": "Girone A",
        "Squadra": "Olimpia Corato",
        "Logo_URL": logo_url("Olimpia Corato.png"),
        "Note_Tattiche": "",
    },
    {
        "Girone": "Girone A",
        "Squadra": "Virtus Foggia",
        "Logo_URL": logo_url("Virtus Foggia.png"),
        "Note_Tattiche": "",
    },
]

# Calendario ufficiale CU n. 91 (Squadra A = Casa, Squadra B = Trasferta)
# Campi: (ID_Partita, Giornata, Data_Ora, Casa, Trasferta, Punti_Casa, Punti_Trasferta, Stato)
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
    ("G03_1880", 3, "Sab 21/11/2026 19:00", "Nuova Matteotti Corato", "A.G.S.D. Toritto", 64, 72, "Giocata"),
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
        pd.DataFrame(
            columns=[
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
            ]
        ).to_csv(BOX_FILE, index=False)


def load_data():
    init_data()
    teams_df = pd.read_csv(TEAMS_FILE, dtype=str).fillna("")
    games_df = pd.read_csv(GAMES_FILE, dtype=str).fillna("")
    box_df = pd.read_csv(BOX_FILE, dtype=str).fillna("")

    for col in ["Giornata", "Punti_Casa", "Punti_Trasferta"]:
        if col in games_df.columns:
            games_df[col] = pd.to_numeric(games_df[col], errors="coerce").fillna(0).astype(int)

    for col in ["Punti", "2P_Segnati", "3P_Segnati", "TL_Segnati", "TL_Sbagliati"]:
        if col in box_df.columns:
            box_df[col] = pd.to_numeric(box_df[col], errors="coerce").fillna(0).astype(int)

    if "Quintetto_Base" in box_df.columns:
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


def compute_record(team_name: str, girone: str, games_df: pd.DataFrame):
    played = games_df[
        (games_df["Girone"] == girone) & (games_df["Stato"].str.lower() == "giocata")
    ]
    wins = 0
    losses = 0
    for _, row in played.iterrows():
        if row["Casa"] == team_name:
            if row["Punti_Casa"] > row["Punti_Trasferta"]:
                wins += 1
            elif row["Punti_Casa"] < row["Punti_Trasferta"]:
                losses += 1
        elif row["Trasferta"] == team_name:
            if row["Punti_Trasferta"] > row["Punti_Casa"]:
                wins += 1
            elif row["Punti_Trasferta"] < row["Punti_Casa"]:
                losses += 1
    return wins, losses


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
            }
        )

    res = pd.DataFrame(rows)
    return res.sort_values(by="Media Punti", ascending=False).reset_index(drop=True)


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

st.sidebar.title("🏀 DR2 Puglia")
page = st.sidebar.radio("Navigazione", ["Gironi", "Calendario & Tabellini", "Gestione Squadre"])
if st.sidebar.button("Esci"):
    st.session_state.authenticated = False
    st.rerun()

# ==========================================
# PAGINA 1: GIRONI (A, B, C) & ROSTER
# ==========================================
if page == "Gironi":
    st.title("Gironi — Divisione Regionale 2 Puglia")
    st.caption("Focus sulla Regular Season del Girone A. I Gironi B e C sono pronti per eventuale post-season.")

    girone_sel = st.selectbox("Seleziona Girone", ["Girone A", "Girone B", "Girone C"])

    g_teams = teams_df[teams_df["Girone"] == girone_sel].reset_index(drop=True)
    if g_teams.empty:
        st.info(
            f"Nessuna squadra inserita in **{girone_sel}** al momento. "
            "Puoi aggiungere squadre da *Gestione Squadre* (utile per Play-off / Play-out o post-season)."
        )
    else:
        st.subheader(f"Squadre — {girone_sel} ({len(g_teams)} squadre)")

        summary_rows = []
        for _, trow in g_teams.iterrows():
            w, l = compute_record(trow["Squadra"], girone_sel, games_df)
            summary_rows.append(
                {
                    "Squadra": trow["Squadra"],
                    "Vittorie": w,
                    "Sconfitte": l,
                    "Record (V-S)": f"{w}-{l}",
                    "Logo": trow["Logo_URL"] if trow["Logo_URL"] else "—",
                }
            )
        st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("Dettaglio Squadra e Roster")
        selected_team = st.selectbox(
            "Seleziona una squadra per vedere logo, record, roster e statistiche",
            g_teams["Squadra"].tolist(),
        )

        team_info = g_teams[g_teams["Squadra"] == selected_team].iloc[0]
        w, l = compute_record(selected_team, girone_sel, games_df)

        col1, col2 = st.columns([1, 4])
        with col1:
            if team_info["Logo_URL"].strip():
                st.image(team_info["Logo_URL"].strip(), width=100)
            else:
                st.markdown("### 🏀")
        with col2:
            st.markdown(f"### {selected_team}")
            st.markdown(f"**Record (V-S):** {w} Vittorie - {l} Sconfitte ({w}-{l})")
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
    st.title("Calendario & Tabellini")

    girone_cal = st.selectbox("Girone", ["Girone A", "Girone B", "Girone C"], key="cal_girone")
    cal_teams = teams_df[teams_df["Girone"] == girone_cal]["Squadra"].tolist()

    with st.expander("➕ Aggiungi nuova partita al calendario"):
        with st.form("add_game_form"):
            c1, c2, c3 = st.columns(3)
            giornata = c1.number_input("Giornata", min_value=1, max_value=40, value=1, step=1)
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
                            }
                        ]
                    )
                    games_df = pd.concat([games_df, new_row], ignore_index=True)
                    save_games(games_df)
                    st.success("Partita salvata.")
                    st.rerun()

    st.subheader(f"Partite — {girone_cal}")
    g_games = games_df[games_df["Girone"] == girone_cal].copy()
    if g_games.empty:
        st.info("Nessuna partita ancora presente per questo girone.")
    else:
        g_games_sorted = g_games.sort_values(by=["Giornata", "ID_Partita"]).reset_index(drop=True)
        display_games = g_games_sorted.copy()
        display_games["Risultato"] = display_games.apply(
            lambda r: f"{r['Punti_Casa']} - {r['Punti_Trasferta']}" if r["Stato"].lower() == "giocata" else "—",
            axis=1,
        )
        st.dataframe(
            display_games[["Giornata", "Data", "Casa", "Risultato", "Trasferta", "Stato"]],
            use_container_width=True,
            hide_index=True,
        )

        st.divider()
        st.subheader("Inserisci / Aggiorna Risultato e Tabellino Giocatore")

        game_labels = {
            f"G{r['Giornata']} | {r['Casa']} vs {r['Trasferta']} ({r['Stato']})": r["ID_Partita"]
            for _, r in g_games_sorted.iterrows()
        }
        sel_game_label = st.selectbox("Seleziona Partita", list(game_labels.keys()))
        sel_game_id = game_labels[sel_game_label]
        game_row = games_df[games_df["ID_Partita"] == sel_game_id].iloc[0]

        with st.form("update_result_form"):
            col_r1, col_r2, col_r3, col_r4 = st.columns(4)
            upd_casa = col_r1.number_input("Punti Casa", min_value=0, max_value=200, value=int(game_row["Punti_Casa"]), step=1)
            upd_trasf = col_r2.number_input("Punti Trasferta", min_value=0, max_value=200, value=int(game_row["Punti_Trasferta"]), step=1)
            upd_stato = col_r3.selectbox("Stato Partita", ["Da giocare", "Giocata"], index=0 if game_row["Stato"] == "Da giocare" else 1)
            if col_r4.form_submit_button("Aggiorna Risultato"):
                idx = games_df.index[games_df["ID_Partita"] == sel_game_id][0]
                games_df.loc[idx, "Punti_Casa"] = int(upd_casa)
                games_df.loc[idx, "Punti_Trasferta"] = int(upd_trasf)
                games_df.loc[idx, "Stato"] = upd_stato
                save_games(games_df)
                st.success("Risultato aggiornato.")
                st.rerun()

        with st.form("add_box_row_form"):
            b1, b2, b3, b4 = st.columns([2.5, 2.5, 1.2, 1.5])
            sq_options = [s for s in [game_row["Casa"], game_row["Trasferta"]] if s] or cal_teams
            tab_sq = b1.selectbox("Squadra Giocatore", sq_options if sq_options else ["Squadra"])
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

            if st.form_submit_button("Aggiungi Giocatore a Tabellino"):
                if not giocatore.strip():
                    st.error("Inserisci Nome e Cognome del giocatore.")
                else:
                    new_box = pd.DataFrame(
                        [
                            {
                                "ID_Partita": sel_game_id,
                                "Girone": girone_cal,
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
                            }
                        ]
                    )
                    box_df = pd.concat([box_df, new_box], ignore_index=True)
                    save_box(box_df)
                    st.success("Riga di tabellino salvata.")
                    st.rerun()

        st.markdown("#### Tabellino Registrato per la Partita Selezionata")
        game_box = box_df[box_df["ID_Partita"] == sel_game_id]
        if game_box.empty:
            st.info("Nessun giocatore inserito ancora per questa partita.")
        else:
            st.dataframe(
                game_box[
                    [
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
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )

# ==========================================
# PAGINA 3: GESTIONE SQUADRE & EXPORT
# ==========================================
elif page == "Gestione Squadre":
    st.title("Gestione Squadre e Dati")
    st.caption("Modifica squadre/loghi/note del Girone A o aggiungi squadre per eventuale post-season.")

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
    st.subheader("Esporta Dati (CSV)")
    c_exp1, c_exp2, c_exp3 = st.columns(3)
    c_exp1.download_button("Scarica Squadre CSV", teams_df.to_csv(index=False).encode("utf-8"), "squadre.csv", "text/csv")
    c_exp2.download_button("Scarica Partite CSV", games_df.to_csv(index=False).encode("utf-8"), "partite.csv", "text/csv")
    c_exp3.download_button("Scarica Tabellini CSV", box_df.to_csv(index=False).encode("utf-8"), "tabellini.csv", "text/csv")
