# KINGINAZOO v2 — embedded jungle background (no relative asset URL)
# KINGINAZOO — generated jungle background is loaded from assets/zoobg.png
import json
import secrets
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import base64
import sqlite3
import threading
import time


try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

@st.cache_data(show_spinner=False)
def get_bg_data_uri():
    bg_path = Path(__file__).resolve().parent / "assets" / "zoobg.webp"
    data = base64.b64encode(bg_path.read_bytes()).decode("ascii")
    return "data:image/webp;base64," + data

BG_DATA_URI = get_bg_data_uri()

st.set_page_config(
    page_title="KINGINAZOO",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ANIMALS = [
    {"id": "monkey", "name": "Monkey", "emoji": "🐒", "multiplier": 5, "category": "Land"},
    {"id": "koala", "name": "Koala", "emoji": "🐨", "multiplier": 5, "category": "Land"},
    {"id": "panda", "name": "Panda", "emoji": "🐼", "multiplier": 5, "category": "Land"},
    {"id": "lion", "name": "Lion", "emoji": "🦁", "multiplier": 5, "category": "Land"},
    {"id": "fish", "name": "Fish", "emoji": "🐟", "multiplier": 10, "category": "Ocean"},
    {"id": "crab", "name": "Crab", "emoji": "🦀", "multiplier": 15, "category": "Ocean"},
    {"id": "jelly", "name": "Jellyfish", "emoji": "🪼", "multiplier": 25, "category": "Ocean"},
    {"id": "shell_pearl", "name": "Shell Pearl", "emoji": "🐚", "multiplier": 50, "category": "Ocean"},
]
BET_OPTIONS = [1, 10, 100, 1000]

# Persistent winning history. SQLite keeps the latest results available across
# Streamlit reruns/sessions while the deployed app storage is available.
HISTORY_DB = Path(__file__).resolve().parent / "kinginazoo_history.db"
_db_lock = threading.Lock()

@st.cache_resource(show_spinner=False)
def _history_db():
    conn = sqlite3.connect(HISTORY_DB, timeout=10, check_same_thread=False)
    conn.execute("""CREATE TABLE IF NOT EXISTS winning_history (
        round INTEGER PRIMARY KEY,
        animal_id TEXT NOT NULL,
        name TEXT NOT NULL,
        emoji TEXT NOT NULL,
        category TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.commit()
    return conn

@st.cache_data(ttl=2, show_spinner=False)
def load_history(limit=10):
    with _db_lock:
        conn = _history_db()
        rows = conn.execute(
            "SELECT round, animal_id, name, emoji, category FROM winning_history ORDER BY round DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [
        {
            "round": r[0],
            "winner": {"id": ("shell_pearl" if r[1] == "turtle" else r[1]), "name": ("Shell Pearl" if r[2] == "Turtle" else r[2]), "emoji": ("🐚" if r[3] == "🐢" else r[3]), "category": r[4]},
        }
        for r in rows
    ]

def save_winner(round_no, winner):
    with _db_lock:
        conn = _history_db()
        conn.execute(
            "INSERT OR REPLACE INTO winning_history (round, animal_id, name, emoji, category) VALUES (?, ?, ?, ?, ?)",
            (round_no, winner["id"], winner["name"], winner["emoji"], winner["category"]),
        )
        conn.commit()
    load_history.clear()

DEFAULTS = {
    "balance": 10_000,
    "round": 531,
    "bets": {},
    "selected_bet": 1,
    "winner": None,
    "status": "Choose your bet and animals",
    "history": [],
    "show_reveal": False,
    "last_result_round": None,
    "bet_timer_active": False,
    "bet_timer_end": None,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Reload the latest winning results on every rerun for realtime history.
st.session_state.history = load_history(10)


def fmt(value):
    return f"{int(value):,}"


def total_bet():
    return sum(st.session_state.bets.values())


def get_animal(animal_id):
    return next((a for a in ANIMALS if a["id"] == animal_id), None)


# ---------------------------------------------------------------------
# Full KINGINAZOO visual system
# ---------------------------------------------------------------------
CSS = """
<style>
:root {
    --green-1: #031f12;
    --green-2: #063b20;
    --green-3: #07582b;
    --green-4: #0b7435;
    --gold: #ffd84d;
    --gold-2: #f2b900;
    --gold-soft: #ffe994;
    --text: #fff7cf;
    --muted: #b8bd91;
    --card: rgba(2, 45, 24, .92);
}

/* Streamlit chrome */
#MainMenu, header, footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"] {
    display: none !important;
}

/* IMPORTANT: green app background */
html, body, [data-testid="stAppViewContainer"],
[data-testid="stApp"], .stApp, section.main {
    overflow: hidden !important;
    max-height: 100vh !important;
    background-image:
        linear-gradient(rgba(0, 25, 12, .10), rgba(0, 18, 9, .18)),
        url("__BG_DATA_URI__") !important;
    background-position: center top !important;
    background-size: cover !important;
    background-attachment: fixed !important;
    background-repeat: no-repeat !important;
    background-color: #031d11 !important;
    color: #fff7cf !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

.block-container {
    width: min(1180px, 100%) !important;
    max-width: 1180px !important;
    padding: 8px 14px 20px !important;
    margin: auto !important;
}

.kz-page {
    position: relative;
    z-index: 0;
    width: min(1080px, 100%);
    max-width: 1080px;
    margin: auto;
    overflow: hidden;
}

/* Mask the oversized KINGINAZOO artwork baked into the jungle background.
   The real foreground wordmark remains above this layer. */
.kz-page::before {
    content: "";
    position: absolute;
    z-index: 1;
    left: -2%;
    right: -2%;
    top: 72px;
    height: 465px;
    background:
        linear-gradient(
            180deg,
            rgba(1, 30, 16, .985) 0%,
            rgba(1, 38, 20, .975) 65%,
            rgba(1, 38, 20, .88) 88%,
            rgba(1, 38, 20, .40) 100%
        );
    pointer-events: none;
}


/* Brand — keep KINGINAZOO clearly readable above the background art */
.kz-brand {
    position: relative;
    z-index: 4;
    height: clamp(70px, 7vw, 88px);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin: 0 auto 4px;
    pointer-events: none;
}
.kz-logo {
    display: block !important;
    color: #ffe66b;
    font-size: clamp(38px, 5vw, 64px);
    line-height: .95;
    font-weight: 1000;
    letter-spacing: clamp(1px, .4vw, 5px);
    text-align: center;
    text-shadow: 0 3px 0 #5d3900, 0 0 12px rgba(255,216,77,.7), 0 5px 18px rgba(0,0,0,.85);
    white-space: nowrap;
}
.kz-tag {
    display: block !important;
    color: #fff4b0;
    font-size: clamp(8px, 1.2vw, 12px);
    font-weight: 1000;
    letter-spacing: clamp(2px, .55vw, 5px);
    margin-top: 2px;
    text-shadow: 0 2px 5px #000;
}


/* High-contrast brand treatment */
.kz-brand::before {
    content: "";
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    width: min(760px, 92%);
    height: 76%;
    background: radial-gradient(ellipse, rgba(0,28,14,.62) 0%, rgba(0,28,14,.28) 52%, transparent 78%);
    z-index: -1;
    pointer-events: none;
}

/* Top stats */
.kz-top {
    position: relative;
    z-index: 2;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-bottom: 8px;
}
.kz-stat {
    background: linear-gradient(180deg, rgba(6,59,32,.88), rgba(2,41,20,.90));
    border: 2px solid var(--gold);
    border-radius: 16px;
    padding: 8px 14px;
    box-shadow:
      0 0 0 2px rgba(255,216,77,.08),
      0 7px 18px rgba(0,0,0,.35);
}
.kz-stat-label {
    display: block;
    color: #e7d986;
    font-size: 12px;
    font-weight: 1000;
    letter-spacing: 2px;
}
.kz-stat-value {
    display: block;
    color: white;
    font-size: clamp(22px, 3vw, 34px);
    font-weight: 1000;
}

/* Arena */
.kz-arena {
    position: relative;
    z-index: 2;
    min-height: 112px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background:
      radial-gradient(circle at 50% 20%, rgba(21,137,65,.20), transparent 45%),
      linear-gradient(180deg,rgba(6,61,32,.86),rgba(2,29,16,.90));
    border: 2px solid var(--gold) !important;
    border-radius: 18px;
    box-shadow: 0 6px 18px rgba(0,0,0,.28);
    margin-bottom: 8px;
}
.kz-arena-round {
    color: #d8cf93;
    font-size: 11px;
    font-weight: 1000;
    letter-spacing: 2px;
}
.kz-winner {
    height: 58px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: clamp(42px, 5.5vw, 68px);
    line-height: 1;
    filter: drop-shadow(0 8px 7px rgba(0,0,0,.5));
}
.kz-status {
    color: #fff4b0;
    font-size: clamp(14px, 2vw, 19px);
    font-weight: 1000;
}

/* Section */
.kz-section-title {
    position: relative;
    z-index: 2;
    color: #ffe888;
    font-size: 17px;
    font-weight: 1000;
    letter-spacing: 1px;
    margin: 9px 4px 6px;
    text-shadow: 0 2px 4px #000;
}

/* Bet chips */
.kz-bets {
    position: relative;
    z-index: 2;
    display: grid;
    grid-template-columns: repeat(4,1fr);
    gap: 12px;
}
.kz-bet {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 46px;
    border: 2px solid #54a63b;
    border-radius: 18px;
    background: linear-gradient(180deg,#063b20,#022814);
    color: #fff8c9 !important;
    text-decoration: none !important;
    font-size: 18px;
    font-weight: 1000;
    box-shadow: 0 4px 0 #01170b;
    transition: transform .12s, box-shadow .12s;
}
.kz-bet:hover { transform: translateY(-2px); }
.kz-bet.active {
    background: linear-gradient(180deg,#ff5a55,#d9272e);
    border-color: #ffe45c;
    box-shadow: 0 0 15px rgba(255,73,54,.6);
}

/* Summary */
.kz-summary {
    position: relative;
    z-index: 2;
    display: flex;
    justify-content: space-between;
    gap: 15px;
    color: #fff7ce;
    font-size: 15px;
    font-weight: 1000;
    margin: 8px 6px 10px;
}

/* Native Streamlit buttons are used for betting so taps never open a new page. */
div.stButton > button {
    width: 100% !important;
    min-height: 46px !important;
    border-radius: 14px !important;
    border: 2px solid rgba(255,216,77,.78) !important;
    background: linear-gradient(180deg, rgba(7,88,43,.96), rgba(2,45,24,.98)) !important;
    color: #fff7cf !important;
    font-weight: 800 !important;
    box-shadow: 0 5px 14px rgba(0,0,0,.22) !important;
    white-space: pre-line !important;
    line-height: 1.08 !important;
    font-size: 15px !important;
}
div.stButton > button:hover {
    border-color: #ffe994 !important;
    transform: translateY(-1px);
}

/* Large animal icons: native buttons + per-animal pseudo-element. */
[class*="st-key-animal-card-"] div.stButton > button {
    min-height: 118px !important;
    padding: 8px 6px 7px !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 1px !important;
    overflow: hidden !important;
}
[class*="st-key-animal-card-"] div.stButton > button p {
    margin: 0 !important;
    white-space: pre-line !important;
    font-size: 11px !important;
    line-height: 1.08 !important;
    font-weight: 1000 !important;
}
.st-key-animal-card-monkey div.stButton > button::before { content: "🐒"; }
.st-key-animal-card-koala div.stButton > button::before { content: "🐨"; }
.st-key-animal-card-panda div.stButton > button::before { content: "🐼"; }
.st-key-animal-card-lion div.stButton > button::before { content: "🦁"; }
.st-key-animal-card-fish div.stButton > button::before { content: "🐟"; }
.st-key-animal-card-crab div.stButton > button::before { content: "🦀"; }
.st-key-animal-card-jelly div.stButton > button::before { content: "🪼"; }
.st-key-animal-card-shell_pearl div.stButton > button::before { content: "🐚"; }
[class*="st-key-animal-card-"] div.stButton > button::before {
    display: block !important;
    font-size: clamp(64px, 7vw, 86px) !important;
    line-height: .82 !important;
    margin-bottom: 3px !important;
    filter: drop-shadow(0 5px 4px rgba(0,0,0,.5));
}

/* Animal grid */
.kz-animals {
    position: relative;
    z-index: 2;
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
}
.kz-animal {
    min-height: 132px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-decoration: none !important;
    color: white !important;
    background:
      radial-gradient(circle at 50% 0%, rgba(28,117,55,.22), transparent 50%),
      linear-gradient(180deg,#063a20,#022716);
    border: 2px solid #f0ca39;
    border-radius: 16px;
    box-shadow:
      0 6px 0 #01180c,
      inset 0 0 15px rgba(255,216,77,.06);
    transition: transform .12s, border-color .12s, box-shadow .12s;
    touch-action: manipulation;
    -webkit-tap-highlight-color: transparent;
}
.kz-animal:hover {
    transform: translateY(-3px);
    border-color: #fff2a0;
}
.kz-animal:active {
    transform: scale(.97);
}
.kz-animal.hasbet {
    border-color: #fff05b;
    box-shadow:
      0 0 0 2px rgba(255,220,50,.25),
      0 0 20px rgba(255,215,60,.18),
      0 6px 0 #01180c;
}
.kz-animal-emoji {
    font-size: clamp(42px, 5vw, 62px);
    line-height: 1;
    filter: drop-shadow(0 7px 5px rgba(0,0,0,.45));
}
.kz-animal-name {
    font-size: 14px;
    font-weight: 1000;
    margin-top: 3px;
}
.kz-multi {
    background: linear-gradient(180deg,#ffe875,#eebd25);
    color: #17230d;
    border-radius: 99px;
    padding: 5px 13px;
    font-size: 11px;
    font-weight: 1000;
    margin-top: 3px;
}
.kz-amount {
    width: 75%;
    text-align: center;
    background: rgba(0,0,0,.22);
    border: 1px solid #d8c45d;
    border-radius: 12px;
    padding: 3px;
    color: #fff6b9;
    font-size: 11px;
    font-weight: 1000;
    margin-top: 5px;
}
.kz-add {
    color: #b6c49d;
    font-size: 10px;
    font-weight: 900;
    margin-top: 4px;
}

/* Actions */
.kz-actions {
    position: relative;
    z-index: 2;
    display: grid;
    grid-template-columns: 3fr 1fr;
    gap: 12px;
    margin-top: 10px;
}
.kz-action {
    min-height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 18px;
    text-decoration: none !important;
    font-size: 15px;
    font-weight: 1000;
    touch-action: manipulation;
}
.kz-start {
    color: #173006 !important;
    background: linear-gradient(180deg,#ffe86b,#e9aa16);
    border: 2px solid #fff0a1;
    box-shadow: 0 6px 0 #8a5d09;
}
.kz-clear {
    color: #fff7c9 !important;
    background: #07341d;
    border: 2px solid #b28a22;
}

/* Winning history — always above the drawing */
.kz-history {
    display: block !important;
    position: relative;
    z-index: 3;
    margin: 6px 0 8px;
    background: linear-gradient(180deg, rgba(3,58,32,.52), rgba(2,35,20,.38));
    border: none !important;
    border-radius: 12px;
    padding: 5px 4px 7px;
    overflow: hidden;
    box-shadow: none;
}
.kz-history-title {
    color: #ffe87e;
    font-size: 14px;
    font-weight: 1000;
    letter-spacing: 1px;
    text-align: center;
    margin-bottom: 5px;
    text-shadow: 0 2px 4px #000;
}
.kz-history-list {
    display: grid;
    grid-template-columns: repeat(10, minmax(0, 1fr));
    gap: 6px;
    width: 100%;
}
.kz-history-chip {
    min-width: 0;
    min-height: 62px;
    padding: 5px 3px;
    border-radius: 11px;
    background: linear-gradient(180deg,#0a542b,#06361e);
    border: 1px solid rgba(255,216,77,.58);
    text-align: center;
    color: #fff5bf;
    font-size: 10px;
    font-weight: 900;
    overflow: hidden;
    box-sizing: border-box;
}
.kz-history-chip.empty { display:none !important; }
.kz-history-empty {
    text-align:center;
    color:#b8bd91;
    font-size:12px;
    font-weight:800;
    padding:8px;
}
.kz-history-chip .animal {
    display: block;
    font-size: 34px;
    line-height: .95;
    filter: drop-shadow(0 5px 4px rgba(0,0,0,.5));
}
.kz-history-chip .round {
    display: block;
    color: #ffe87e;
    font-size: 9px;
    margin-top: 3px;
    font-weight: 1000;
}
/* 10-second betting timer */
.kz-timer-wrap {
    position: relative;
    z-index: 3;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    margin: 5px 0 8px;
    color: #fff5bf;
    font-weight: 1000;
    text-align: center;
}
.kz-timer {
    min-width: 74px;
    padding: 5px 12px;
    border: 2px solid #ffd84d;
    border-radius: 999px;
    background: rgba(2,39,20,.85);
    color: #ffe45c;
    font-size: 22px;
    line-height: 1;
    text-shadow: 0 2px 5px #000;
}
.kz-timer.hot {
    color: #ff6b5f;
    border-color: #ff6b5f;
}
@media (max-width: 650px) {
    .kz-page::before {
        top: 38px;
        height: 300px;
        background: linear-gradient(
            180deg,
            rgba(1, 38, 20, .97) 0%,
            rgba(1, 38, 20, .93) 55%,
            rgba(1, 38, 20, .55) 100%
        );
    }
    .kz-brand { height: 56px !important; }
    .kz-logo { font-size: clamp(34px, 10vw, 48px) !important; }
    .kz-top { gap: 5px !important; margin-bottom: 5px !important; }
    .kz-stat { padding: 4px 6px !important; }
    .kz-arena { min-height: 88px !important; margin-bottom: 5px !important; }
    .kz-winner { height: 44px !important; font-size: 44px !important; }
    .kz-history { margin: 2px 0 3px !important; padding: 2px !important; }
}

    .kz-timer-wrap { margin: 3px 0 5px; gap: 6px; }
    .kz-timer { min-width: 55px; padding: 4px 8px; font-size: 16px; border-width: 1.5px; }
}

/* Footer */
.kz-footer {
    display: block !important;
    position: relative;
    z-index: 2;
    text-align: center;
    color: #ffe87e;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1.5px;
    margin: 12px 0 4px;
    padding: 6px 0;
}
.kz-footer .powered-by {
    color: #ffffff;
    font-size: 32px;
    font-weight: 900;
    letter-spacing: 2px;
    opacity: .9;
}

/* Streamlit iframe animation should blend in */
iframe[title="streamlit.components.v1.html"] {
    width: 100% !important;
    border: 0 !important;
    background: transparent !important;
    overflow: hidden !important;
}
[data-testid="stAppViewContainer"] > .main { overflow: hidden !important; }
[data-testid="stVerticalBlock"] { gap: 0.15rem !important; }


/* Jackpot selector */
.kz-jackpot-wrap {
    display:none !important;

    position: relative;
    z-index: 2;
    margin: 15px 0 5px;
}
.kz-jackpot-title {
    text-align: center;
    color: #ffe87b;
    font-size: 19px;
    font-weight: 1000;
    letter-spacing: 1px;
    margin-bottom: 9px;
    text-shadow: 0 2px 5px #000;
}
.kz-jackpots {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
}
.kz-jackpot {
    display: block;
    text-align: center;
    text-decoration: none !important;
    color: #fff7c8 !important;
    background: linear-gradient(180deg,#073f22,#022914);
    border: 2px solid #3e9c42;
    border-radius: 18px;
    padding: 10px 8px;
    box-shadow: 0 4px 0 #01170b;
}
.kz-jackpot.active {
    border-color: #ffd84d;
    box-shadow: 0 0 18px rgba(255,216,77,.22), 0 4px 0 #01170b;
}
.kz-jackpot-icon {
    font-size: 25px;
}
.kz-jackpot-name {
    font-size: 14px;
    font-weight: 1000;
    margin-top: 2px;
}
.kz-jackpot-value {
    color: #ffe45c;
    font-size: 19px;
    font-weight: 1000;
    margin-top: 3px;
}
.kz-jackpot-sub {
    color: #a9c49d;
    font-size: 9px;
    font-weight: 900;
    margin-top: 2px;
}

/* Phone */
@media (max-width: 650px) {
    html, body, [data-testid="stAppViewContainer"],
    [data-testid="stApp"], .stApp, section.main {
        background-image:
            linear-gradient(rgba(0, 25, 12, .08), rgba(0, 18, 9, .15)),
            url("__BG_DATA_URI__") !important;
        background-position: center top !important;
        background-size: auto 100vh !important;
        background-attachment: fixed !important;
        background-repeat: no-repeat !important;
        background-color: #031d11 !important;
    }
.block-container {
        max-width: 560px !important;
        padding: 3px 5px 12px !important;
    }
    .kz-brand { height: 56px; margin-bottom: 2px; }
    .kz-logo { font-size: clamp(34px, 10.5vw, 50px); letter-spacing: .5px; line-height: .9; }
    .kz-tag { font-size: 7px; letter-spacing: 1.8px; margin-top: 1px; }
    .kz-top { gap: 5px; margin-bottom: 5px; }
    .kz-stat { padding: 5px 7px; border-radius: 10px; }
    .kz-stat-label { font-size: 7px; letter-spacing: 1px; }
    .kz-stat-value { font-size: 16px; }
    .kz-arena { min-height: 88px; border-radius: 14px; margin-bottom: 5px; }
    .kz-arena-round { font-size: 7px; letter-spacing: 1px; }
    .kz-winner { height: 44px; font-size: 44px; }
    .kz-status { font-size: 10px; }
    .kz-section-title { font-size: 11px; margin: 4px 1px 3px; letter-spacing: .5px; }
    .kz-bets { gap: 5px; }
    .kz-bet { min-height: 33px; border-radius: 9px; font-size: 11px; border-width: 1.5px; }
    .kz-summary { font-size: 9px; margin: 4px 2px; }
    .kz-animals { grid-template-columns: repeat(2, 1fr); gap: 6px; }
    [class*="st-key-animal-card-"] div.stButton > button {
        min-height: 96px !important;
        border-radius: 11px !important;
        border-width: 1.5px !important;
        padding: 3px 4px !important;
    }
    [class*="st-key-animal-card-"] div.stButton > button::before {
        font-size: clamp(52px, 16vw, 68px) !important;
        line-height: .78 !important;
        margin-bottom: 2px !important;
    }
    [class*="st-key-animal-card-"] div.stButton > button p {
        font-size: 9px !important;
        line-height: 1 !important;
    }
    .kz-actions { gap: 5px; margin-top: 6px; }
    .kz-action { min-height: 36px; font-size: 10px; border-radius: 10px; }
    div.stButton > button { min-height: 34px !important; font-size: 10px !important; }
    .kz-history { display: block !important; margin: 4px 0 5px !important; padding: 4px 4px 5px !important; border-radius: 10px !important; }
    .kz-history-title { font-size: 11px !important; margin-bottom: 5px !important; }
    .kz-history-list { grid-template-columns: repeat(5, minmax(0, 1fr)) !important; gap: 4px !important; }
    .kz-history-chip { min-height: 58px !important; padding: 3px 1px !important; border-radius: 8px !important; font-size: 7px !important; }
    .kz-history-chip .animal { font-size: 32px !important; }
    .kz-history-chip .round { font-size: 6px !important; margin-top: 1px !important; }
    .kz-footer { display: block !important; margin-top: 12px !important; padding: 8px 0 14px !important; font-size: 10px !important; }
    .kz-footer .powered-by { font-size: 24px !important; font-weight: 1000 !important; letter-spacing: 1px !important; text-align: center !important; }
}

/* Final MARGAUX footer sizing */
.kz-footer .powered-by {
    display: block !important;
    width: 100% !important;
    text-align: center !important;
    margin: 8px auto 2px !important;
    font-size: clamp(24px, 3vw, 36px) !important;
    font-weight: 1000 !important;
    letter-spacing: 2px !important;
    color: #FFD84D !important;
    text-shadow: 0 2px 8px rgba(0,0,0,.95), 0 0 12px rgba(255,216,77,.28) !important;
}
@media (max-width: 650px) {
    .kz-footer .powered-by { font-size: 26px !important; letter-spacing: 1.2px !important; }
}

/* Very short phone screens */
@media (max-width: 650px) and (max-height: 700px) {
    .kz-brand { height: 36px; }
    .kz-logo { font-size: 26px; }
    .kz-tag { display: none !important; }
    .kz-stat { padding: 4px 7px; }
    .kz-stat-value { font-size: 14px; }
    .kz-arena { min-height: 68px; }
    .kz-winner { height: 32px; font-size: 31px; }
    .kz-section-title { margin: 3px 1px 2px; }
    .kz-bet { min-height: 31px; }
    [class*="st-key-animal-card-"] div.stButton > button { min-height: 68px !important; }
    [class*="st-key-animal-card-"] div.stButton > button::before { font-size: 58px !important; }
    .kz-history { margin: 4px 0 5px !important; padding: 4px !important; }
    .kz-history-title { font-size: 9px !important; }
    .kz-history-chip { min-height: 50px !important; }
    .kz-history-chip .animal { font-size: 28px !important; }
    .kz-actions { margin-top: 3px; }
    .kz-action { min-height: 32px; }
}

/* Clean reference-style winner/drawing presentation */
.kz-arena, .kz-arena * { border-color: transparent !important; }
.kz-arena { background: linear-gradient(180deg, rgba(6,61,32,.38), rgba(2,29,16,.22)) !important; }
.kz-history { border: none !important; box-shadow: none !important; }

/* Performance: keep touch interactions cheap on phones. */
@media (hover: none) and (pointer: coarse) {
    .kz-bet:hover, .kz-animal:hover, div.stButton > button:hover { transform: none !important; }
}
</style>
"""

st.markdown(CSS.replace("__BG_DATA_URI__", BG_DATA_URI), unsafe_allow_html=True)

st.markdown('<div class="kz-page">', unsafe_allow_html=True)

# Brand
st.markdown(
    """
<div class="kz-brand">
  <div class="kz-logo">👑 KINGINAZOO</div>
  <div class="kz-tag">GUESS • BET • WIN</div>
</div>
""",
    unsafe_allow_html=True,
)

# Stats
st.markdown(
    f"""
<div class="kz-top">
  <div class="kz-stat">
    <span class="kz-stat-label">👑 ROUND</span>
    <span class="kz-stat-value">#{st.session_state.round}</span>
  </div>
  <div class="kz-stat" style="text-align:right">
    <span class="kz-stat-label">💎 COINS</span>
    <span class="kz-stat-value">💎 {fmt(st.session_state.balance)}</span>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# 10-second betting timer. The first animal bet starts the timer.
# streamlit-autorefresh keeps the countdown realtime without blocking the app.
timer_remaining = 0
if st.session_state.bet_timer_active and st.session_state.bet_timer_end:
    timer_remaining = max(0, int(st.session_state.bet_timer_end - time.time() + 0.999))
    if timer_remaining <= 0:
        st.session_state.bet_timer_active = False
        st.session_state.bet_timer_end = None
        if total_bet() > 0:
            start_round_pending = True
        else:
            start_round_pending = False
    else:
        start_round_pending = False
else:
    start_round_pending = False

# Main arena

winner = st.session_state.winner
is_flashing = bool(st.session_state.show_reveal and winner)

# The result is rendered now but remains invisible during the drawing.
# The CSS reveal is timed to the exact duration of the browser animation.
display_round = (
    st.session_state.last_result_round
    if winner and st.session_state.last_result_round is not None
    else st.session_state.round
)
arena_emoji = winner["emoji"] if winner else "❓"
arena_status = st.session_state.status if winner else "Choose your bet and animals"
result_class = "kz-result-hidden-during-draw" if is_flashing else ""

st.markdown(
    f"""
<div class="kz-arena {result_class}">
  <div class="kz-arena-round">KINGINAZOO • ROUND #{display_round}</div>
  <div class="kz-winner">{arena_emoji}</div>
  <div class="kz-status">{arena_status}</div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("""
<style>
/* Result stays hidden while the flashing iframe is running.
   The animation reaches its final frame at roughly 3.2 seconds. */
.kz-result-hidden-during-draw .kz-winner,
.kz-result-hidden-during-draw .kz-status {
    opacity: 0 !important;
    animation: kzShowFinalResult 0.12s linear 3.05s forwards !important;
}
@keyframes kzShowFinalResult {
    from { opacity: 0; }
    to { opacity: 1; }
}
</style>
""", unsafe_allow_html=True)

# Realtime betting countdown.
if st.session_state.bet_timer_active and timer_remaining > 0:
    timer_class = "kz-timer hot" if timer_remaining <= 3 else "kz-timer"
    st.markdown(
        f'<div class="kz-timer-wrap">⏳ BETTING OPEN <span class="{timer_class}">{timer_remaining}s</span></div>',
        unsafe_allow_html=True,
    )
elif not st.session_state.bet_timer_active and total_bet() == 0:
    st.markdown(
        '<div class="kz-timer-wrap">⏱️ <span>10-second betting window starts with your first animal bet</span></div>',
        unsafe_allow_html=True,
    )

# Random category is chosen automatically when a round starts.
# There is intentionally NO jackpot selector shown to the player.

# Winning history — shown above the drawing so players can see recent results.
st.markdown('<div class="kz-history">', unsafe_allow_html=True)
st.markdown('<div class="kz-history-title">🏆 LAST 10 WINNING RESULTS</div>', unsafe_allow_html=True)

chips = []
history_for_display = st.session_state.history[:10]
for idx, item in enumerate(history_for_display):
    w = item["winner"]
    current_class = " kz-current-history" if is_flashing and idx == 0 else ""
    chips.append(
        f'<div class="kz-history-chip{current_class}"><span class="animal">{w["emoji"]}</span>'
        f'<span>{w["name"]}</span><span class="round">#{item["round"]}</span></div>'
    )

# Show ONLY real completed results. Never create fake "Waiting" history items.
if chips:
    st.markdown('<div class="kz-history-list">' + ''.join(chips) + '</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="kz-history-empty">No completed rounds yet</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)


st.markdown("""
<style>
.kz-current-history {
    opacity: 0 !important;
    animation: kzShowHistory 0.12s linear 3.05s forwards !important;
}
@keyframes kzShowHistory {
    from { opacity: 0; }
    to { opacity: 1; }
}
</style>
""", unsafe_allow_html=True)

# Flashing winner animation.
# The winner is already selected server-side by secrets.choice().
# Browser Math.random() is used ONLY for the visual flashing sequence;
# it cannot change the server-selected winner.
if st.session_state.show_reveal and st.session_state.winner:
    winner = st.session_state.winner
    animals_json = json.dumps(
        [{"emoji": a["emoji"], "name": a["name"]} for a in ANIMALS]
    )
    winner_json = json.dumps(
        {"emoji": winner["emoji"], "name": winner["name"]}
    )
    # First visual frame is an actual random animal, not a slot-machine icon.
    flash_start = secrets.choice(ANIMALS)

    components.html(
        f"""
<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{{margin:0;background:transparent;font-family:Arial,sans-serif}}
.box{{margin-top:8px;background:#032715;border:0;border-radius:0;
padding:7px;text-align:center;box-shadow:none;box-sizing:border-box;height:150px;overflow:hidden}}
.label{{color:#e5d68b;font-size:10px;font-weight:900;letter-spacing:2px}}
.kz-live-indicator{{color:#7dffb2;font-size:9px;font-weight:900;letter-spacing:1px;margin-left:6px}}
.animal{{height:92px;display:flex;align-items:center;justify-content:center;font-size:82px;will-change:transform,opacity;
filter:drop-shadow(0 8px 6px rgba(0,0,0,.5))}}
.status{{color:#fff1a4;font-size:13px;font-weight:900;line-height:1.05}}
@keyframes winpop{{0%{{transform:scale(.75)}}60%{{transform:scale(1.18)}}100%{{transform:scale(1)}}}}
.win{{animation:winpop .5s ease}}
</style>
</head>
<body>
<div class="box">
 <div class="label">🐾 DRAWING • FLASHING <span class="kz-live-indicator">● LIVE</span></div>
 <div id="animal" class="animal">{flash_start["emoji"]}</div>
 <div id="status" class="status">Flashing...</div>
</div>
<script>
const animals={animals_json};
const winner={winner_json};
const el=document.getElementById("animal");
const status=document.getElementById("status");

const sequence=[];
sequence.push({json.dumps({"emoji": flash_start["emoji"], "name": flash_start["name"]})});
for(let n=1;n<28;n++){{
  sequence.push(animals[Math.floor(Math.random()*animals.length)]);
}}
sequence.push(winner,winner,winner);

let index=0;
let lastFrame=performance.now();
let finished=false;

function frameDelay(n){{
  if(n < 10) return 70;
  if(n < 19) return 105;
  if(n < 27) return 170;
  return 280;
}}

function draw(now){{
  if(finished) return;

  if(now-lastFrame >= frameDelay(index)){{
    const item=sequence[index];
    el.textContent=item.emoji;
    el.className="animal";

    if(index < 19){{
      status.textContent="🐾 Flashing...";
    }} else if(index < sequence.length-1){{
      status.textContent="⏳ Slowing down...";
    }} else {{
      el.textContent=winner.emoji;
      el.className="animal win";
      status.textContent="🎉 " + winner.name + " — WINNER!";
      finished=true;
      return;
    }}

    index++;
    lastFrame=now;
  }}

  requestAnimationFrame(draw);
}}

el.textContent=sequence[0].emoji;
status.textContent="🐾 Flashing...";
requestAnimationFrame(draw);
</script>
</body>
</html>
""",
        height=156,
        scrolling=False,
    )



def choose_bet(amount):
    st.session_state.selected_bet = amount
    st.session_state.status = f"💎 {fmt(amount)} bet selected"
    st.session_state.show_reveal = False

def add_animal_bet(animal_id):
    animal = get_animal(animal_id)
    if not animal:
        return
    current = st.session_state.bets.get(animal_id, 0)
    new_total = total_bet() + st.session_state.selected_bet
    if new_total <= st.session_state.balance:
        st.session_state.bets[animal_id] = current + st.session_state.selected_bet
        st.session_state.status = (
            f'{animal["emoji"]} {animal["name"]} • 💎 {fmt(st.session_state.bets[animal_id])}'
        )
        st.session_state.show_reveal = False
        if not st.session_state.bet_timer_active:
            st.session_state.bet_timer_active = True
            st.session_state.bet_timer_end = time.time() + 10
    else:
        st.session_state.status = "⚠️ Not enough coins"

def clear_bets():
    st.session_state.bets = {}
    st.session_state.status = "Choose your bet and animals"
    st.session_state.show_reveal = False
    st.session_state.bet_timer_active = False
    st.session_state.bet_timer_end = None

def start_round():
    stake = total_bet()
    if stake <= 0:
        st.session_state.status = "⚠️ Tap an animal to place a bet first"
        return
    if stake > st.session_state.balance:
        st.session_state.status = "⚠️ Not enough coins"
        return

    placed = dict(st.session_state.bets)

    # FAIR DRAW: one animal is selected independently of all bets.
    # secrets.randbelow(N) uses the OS-backed cryptographic RNG with uniform
    # rejection sampling, so each of the 8 animals has exactly 1/8 probability.
    # Bets, stake size, payout multiplier, balance, and previous results
    # are NOT inputs to the draw. Repeated winners are valid random outcomes.
    # FAIR RANDOM DRAW:
    # secrets.randbelow() uses Python's OS-backed CSPRNG source.
    # Every one of the 8 animals has exactly the same 1/8 selection
    # probability. Bets, stake size, payout, balance, and history are
    # deliberately NOT used as inputs to the draw.
    winner = ANIMALS[secrets.randbelow(len(ANIMALS))]
    category = winner["category"]

    st.session_state.balance -= stake
    winning_bet = placed.get(winner["id"], 0)
    payout = winning_bet * winner["multiplier"]
    won = winning_bet > 0

    if won:
        st.session_state.balance += payout
        result = f"🎉 {winner['name']} WON! +💎 {fmt(payout)}"
    else:
        result = f"{winner['name']} WON — no winning bet"

    # Persist the result immediately. The next Streamlit rerun will read it
    # back, keeping LAST 10 WINNING RESULTS realtime.
    result_round = st.session_state.round
    save_winner(result_round, winner)

    st.session_state.history.insert(
        0,
        {
            "round": result_round,
            "winner": winner,
            "category": category,
            "stake": stake,
            "winning_bet": winning_bet,
            "payout": payout,
            "won": won,
        },
    )
    st.session_state.history = st.session_state.history[:10]
    st.session_state.bets = {}
    st.session_state.winner = winner
    st.session_state.last_result_round = result_round
    st.session_state.status = result
    st.session_state.round = result_round + 1
    st.session_state.show_reveal = True
    st.session_state.bet_timer_active = False
    st.session_state.bet_timer_end = None

# Auto-draw when the 10-second betting window expires.
if start_round_pending:
    start_round()
    st.rerun()

# Refresh once per second only while the betting timer is active.
if st.session_state.bet_timer_active and not st.session_state.show_reveal and st_autorefresh is not None:
    st_autorefresh(interval=1000, key="kinginazoo_bet_timer")

# Bet buttons — native Streamlit buttons keep the user on the same page.
st.markdown('<div class="kz-section-title">💎 CHOOSE YOUR BET</div>', unsafe_allow_html=True)
bet_cols = st.columns(4, gap="small")
for col, amount in zip(bet_cols, BET_OPTIONS):
    with col:
        label = f"💎 {fmt(amount)}" + (" ✓" if amount == st.session_state.selected_bet else "")
        st.button(
            label,
            key=f"bet_{amount}",
            use_container_width=True,
            on_click=choose_bet,
            args=(amount,),
        )

st.markdown(
    f"""
<div class="kz-summary">
  <span>Total Bet: 💎 {fmt(total_bet())}</span>
  <span>Available: 💎 {fmt(st.session_state.balance - total_bet())}</span>
</div>
""",
    unsafe_allow_html=True,
)

# Animal cards — the entire visible button/card is clickable and adds the selected bet.
st.markdown('<div class="kz-section-title">🐾 TAP AN ANIMAL TO BET</div>', unsafe_allow_html=True)
animal_cols = st.columns(4, gap="small")
for index, animal in enumerate(ANIMALS):
    with animal_cols[index % 4]:
        amount = st.session_state.bets.get(animal["id"], 0)
        with st.container(key=f"animal-card-{animal['id']}"):
            label = (
                f"{animal['name']} x{animal['multiplier']}\n"
                f"💎 {fmt(amount)} • +💎 {fmt(st.session_state.selected_bet)}"
            )
            st.button(
                label,
                key=f"animal_{animal['id']}",
                use_container_width=True,
                on_click=add_animal_bet,
                args=(animal["id"],),
            )

# Actions
action_cols = st.columns([3, 1], gap="small")
def begin_betting_window():
    if total_bet() <= 0:
        st.session_state.status = "⚠️ Tap an animal to place a bet first"
        return
    if not st.session_state.bet_timer_active:
        st.session_state.bet_timer_active = True
        st.session_state.bet_timer_end = time.time() + 10
        st.session_state.status = "⏳ Betting is open for 10 seconds"

with action_cols[0]:
    if st.session_state.bet_timer_active:
        st.button(
            f"⏳ BETTING OPEN • {timer_remaining}s",
            key="start_round",
            use_container_width=True,
            disabled=True,
        )
    else:
        st.button(
            "▶ START 10s BETTING",
            key="start_round",
            use_container_width=True,
            on_click=begin_betting_window,
        )
with action_cols[1]:
    st.button(
        "CLEAR",
        key="clear_bets",
        use_container_width=True,
        on_click=clear_bets,
    )

st.markdown(
    '<div class="kz-footer">'
    '<span class="powered-by">POWERED BY MARGAUX Technology</span>'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("""
<script>
let kinginazooFlashComplete = false;
window.addEventListener("message", function(event) {
    if (
        !kinginazooFlashComplete &&
        event.data &&
        event.data.type === "KINGINAZOO_FLASH_COMPLETE"
    ) {
        kinginazooFlashComplete = true;
        window.location.reload();
    }
});
</script>
""", unsafe_allow_html=True)
