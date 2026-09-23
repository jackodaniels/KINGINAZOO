# KINGINAZOO v2 — embedded jungle background (no relative asset URL)
# KINGINAZOO — generated jungle background is loaded from assets/zoobg.png
import json
import random
import secrets
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import base64

@st.cache_data(show_spinner=False)
def get_bg_data_uri():
    bg_path = Path(__file__).resolve().parent / "assets" / "zoobg.png"
    data = base64.b64encode(bg_path.read_bytes()).decode("ascii")
    return "data:image/png;base64," + data

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
    {"id": "turtle", "name": "Turtle", "emoji": "🐢", "multiplier": 50, "category": "Ocean"},
]
BET_OPTIONS = [1, 10, 100, 1000]

DEFAULTS = {
    "balance": 10_000,
    "round": 531,
    "bets": {},
    "selected_bet": 1,
    "winner": None,
    "status": "Choose your bet and animals",
    "history": [],
    "show_reveal": False,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


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
    padding: 18px 18px 38px !important;
    margin: auto !important;
}

.kz-page {
    position: relative;
    max-width: 1120px;
    margin: auto;
    overflow: hidden;
}


/* Brand — keep KINGINAZOO clearly readable above the background art */
.kz-brand {
    position: relative;
    z-index: 4;
    height: clamp(58px, 7vw, 82px);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin: 0 auto 5px;
    pointer-events: none;
}
.kz-logo {
    display: block !important;
    color: #ffe66b;
    font-size: clamp(30px, 4.4vw, 54px);
    line-height: .95;
    font-weight: 1000;
    letter-spacing: clamp(1px, .35vw, 4px);
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
    margin-top: 5px;
    text-shadow: 0 2px 5px #000;
}

/* Top stats */
.kz-top {
    position: relative;
    z-index: 2;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
    margin-bottom: 14px;
}
.kz-stat {
    background: linear-gradient(180deg, rgba(6,59,32,.88), rgba(2,41,20,.90));
    border: 2px solid var(--gold);
    border-radius: 20px;
    padding: 12px 18px;
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
    min-height: 135px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background:
      radial-gradient(circle at 50% 20%, rgba(21,137,65,.20), transparent 45%),
      linear-gradient(180deg,rgba(6,61,32,.86),rgba(2,29,16,.90));
    border: 3px solid var(--gold);
    border-radius: 28px;
    box-shadow:
      0 0 25px rgba(255,214,67,.18),
      inset 0 0 25px rgba(0,0,0,.3);
    margin-bottom: 15px;
}
.kz-arena-round {
    color: #d8cf93;
    font-size: 11px;
    font-weight: 1000;
    letter-spacing: 2px;
}
.kz-winner {
    height: 76px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: clamp(58px, 7vw, 82px);
    line-height: 1;
    filter: drop-shadow(0 8px 7px rgba(0,0,0,.5));
}
.kz-status {
    color: #fff4b0;
    font-size: clamp(14px, 2vw, 19px);
    font-weight: 1000;
}


/* Compact last-five history inside the main yellow arena */
.kz-arena-history {
    display:flex;
    align-items:center;
    justify-content:center;
    gap:7px;
    margin-top:5px;
    min-height:24px;
    padding:3px 8px;
    border-radius:999px;
    background:rgba(0,25,12,.45);
    border:1px solid rgba(255,216,77,.35);
    box-shadow:inset 0 0 10px rgba(0,0,0,.2);
}
.kz-arena-history-label {
    color:#ffe87e;
    font-size:9px;
    font-weight:1000;
    letter-spacing:1px;
}
.kz-arena-history-item {
    display:inline-flex;
    align-items:center;
    justify-content:center;
    width:25px;
    height:25px;
    border-radius:50%;
    background:linear-gradient(180deg,#0a542b,#06361e);
    border:1px solid rgba(255,216,77,.6);
    font-size:17px;
    line-height:1;
}
.kz-arena-history-empty {
    color:#a9b28d;
    font-size:9px;
}
@media (max-width:650px) {
    .kz-arena-history { gap:5px; margin-top:3px; padding:2px 6px; min-height:20px; }
    .kz-arena-history-label { font-size:7px; }
    .kz-arena-history-item { width:21px; height:21px; font-size:14px; }
}

/* Section */
.kz-section-title {
    position: relative;
    z-index: 2;
    color: #ffe888;
    font-size: 17px;
    font-weight: 1000;
    letter-spacing: 1px;
    margin: 13px 2px 8px;
    text-shadow: 0 2px 4px #000;
}

/* Bet chips */
.kz-bets {
    position: relative;
    z-index: 2;
    display: grid;
    grid-template-columns: repeat(4,1fr);
    gap: 10px;
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
    margin: 9px 5px;
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
.st-key-animal-card-turtle div.stButton > button::before { content: "🐢"; }
[class*="st-key-animal-card-"] div.stButton > button::before {
    display: block !important;
    font-size: clamp(52px, 6vw, 72px) !important;
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
    gap: 11px;
}
.kz-animal {
    min-height: 88px;
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
    border-radius: 22px;
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
    margin-top: 8px;
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
    gap: 10px;
    margin-top: 8px;
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

/* History */
.kz-history {
    display: block !important;
    position: relative;
    z-index: 2;
    margin-top: 18px;
    background: linear-gradient(180deg,#063a20,#022715);
    border: 2px solid #d5ae31;
    border-radius: 20px;
    padding: 13px;
}
.kz-history-title {
    color: #ffe87e;
    font-size: 16px;
    font-weight: 1000;
}
.kz-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    padding: 8px 2px;
    border-bottom: 1px solid rgba(255,216,77,.15);
    color: #fff5bf;
    font-size: 12px;
    font-weight: 900;
}
.kz-row:last-child { border-bottom: 0; }
.kz-win { color: #72e69a; }
.kz-loss { color: #ff8d8d; }

/* Winning history */
.kz-history {
    margin-top: 10px;
    background: rgba(2,39,21,.82);
    border: 2px solid #d5ae31;
    border-radius: 14px;
    padding: 8px 10px;
    overflow: hidden;
}
.kz-history-title {
    color: #ffe87e;
    font-size: 13px;
    font-weight: 1000;
    letter-spacing: 1px;
    margin-bottom: 5px;
}
.kz-history-list {
    display: flex;
    gap: 6px;
    overflow: hidden;
    flex-wrap: nowrap;
}
.kz-history-chip {
    flex: 0 0 auto;
    min-width: 72px;
    padding: 4px 7px;
    border-radius: 9px;
    background: linear-gradient(180deg,#0a542b,#06361e);
    border: 1px solid rgba(255,216,77,.55);
    text-align: center;
    color: #fff5bf;
    font-size: 10px;
    font-weight: 900;
}
.kz-history-chip .animal {
    display: block;
    font-size: 22px;
    line-height: 1;
}
.kz-history-chip .round {
    display: block;
    color: #d9ce8b;
    font-size: 8px;
    margin-top: 2px;
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
        padding: 9px 7px 24px !important;
    }
    .block-container { padding: 4px 6px 6px !important; }
    .kz-brand { height: 45px; margin-bottom: 2px; }
    .kz-logo { font-size: clamp(30px, 9vw, 42px); letter-spacing: 1px; }
    .kz-tag { font-size: 7px; letter-spacing: 2px; margin-top: 2px; }
    .kz-top { gap: 5px; margin-bottom: 5px; }
    .kz-stat { padding: 6px 8px; border-radius: 12px; }
    .kz-stat-label { font-size: 7px; letter-spacing: 1px; }
    .kz-stat-value { font-size: 16px; }
    .kz-arena { min-height: 78px; border-radius: 15px; margin-bottom: 5px; }
    .kz-arena-round { font-size: 7px; letter-spacing: 1px; }
    .kz-winner { height: 40px; font-size: 38px; }
    .kz-status { font-size: 10px; }
    .kz-section-title { font-size: 11px; margin: 5px 1px 4px; letter-spacing: .5px; }
    .kz-bets { gap: 4px; }
    .kz-bet { min-height: 35px; border-radius: 10px; font-size: 11px; border-width: 1.5px; }
    .kz-summary { font-size: 9px; margin: 4px 2px; }
    .kz-animals { grid-template-columns: repeat(2, 1fr); gap: 5px; }
    [class*="st-key-animal-card-"] div.stButton > button {
        min-height: 78px !important;
        border-radius: 11px !important;
        border-width: 1.5px !important;
        padding: 3px 4px !important;
    }
    [class*="st-key-animal-card-"] div.stButton > button::before {
        font-size: clamp(42px, 13vw, 52px) !important;
        line-height: .78 !important;
        margin-bottom: 2px !important;
    }
    [class*="st-key-animal-card-"] div.stButton > button p {
        font-size: 9px !important;
        line-height: 1 !important;
    }
    .kz-actions { gap: 5px; margin-top: 4px; }
    .kz-action { min-height: 36px; font-size: 10px; border-radius: 10px; }
    div.stButton > button { min-height: 34px !important; font-size: 10px !important; }
    .kz-history { display: block !important; margin-top: 7px !important; padding: 7px 8px !important; border-radius: 12px !important; }
    .kz-footer { display: block !important; margin-top: 18px !important; padding: 8px 0 18px !important; font-size: 28px !important; }
    .kz-footer .powered-by { font-size: 28px !important; font-weight: 900 !important; letter-spacing: 1.5px !important; }
}

/* Final MARGAUX footer sizing */
.kz-footer .powered-by {
    display: inline-block !important;
    font-size: 32px !important;
    font-weight: 900 !important;
    letter-spacing: 2px !important;
    color: #FFD84D !important;
    text-shadow: 0 2px 8px rgba(0,0,0,.9) !important;
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
    [class*="st-key-animal-card-"] div.stButton > button::before { font-size: 42px !important; }
    .kz-actions { margin-top: 3px; }
    .kz-action { min-height: 32px; }
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

# Main arena
winner = st.session_state.winner
winner_emoji = winner["emoji"] if winner else "❓"

st.markdown(
    f"""
<div class="kz-arena">
  <div class="kz-arena-round">KINGINAZOO • ROUND #{st.session_state.round}</div>
  <div class="kz-winner">{winner_emoji}</div>
  <div class="kz-status">{st.session_state.status}</div>
  <div class="kz-arena-history">
    <span class="kz-arena-history-label">LAST 5:</span>
    {"".join(f'<span class="kz-arena-history-item" title="Round #{item["round"]}">{item["winner"]["emoji"]}</span>' for item in st.session_state.history[:5]) or '<span class="kz-arena-history-empty">No results yet</span>'}
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# Random category is chosen automatically when a round starts.
# There is intentionally NO jackpot selector shown to the player.

# Flashing winner animation.
# Winner is already selected server-side. The browser only reveals it through
# a rapid random sequence that slows down before stopping.
if st.session_state.show_reveal and st.session_state.winner:
    winner = st.session_state.winner
    animals_json = json.dumps(
        [{"emoji": a["emoji"], "name": a["name"]} for a in ANIMALS]
    )
    winner_json = json.dumps(
        {"emoji": winner["emoji"], "name": winner["name"]}
    )

    components.html(
        f"""
<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{{margin:0;background:transparent;font-family:Arial,sans-serif}}
.box{{margin-top:8px;background:#032715;border:3px solid #ffd84d;border-radius:22px;
padding:7px;text-align:center;box-shadow:0 0 22px rgba(255,216,77,.18);box-sizing:border-box;height:132px;overflow:hidden}}
.label{{color:#e5d68b;font-size:10px;font-weight:900;letter-spacing:2px}}
.animal{{height:82px;display:flex;align-items:center;justify-content:center;font-size:68px;
filter:drop-shadow(0 8px 6px rgba(0,0,0,.5))}}
.status{{color:#fff1a4;font-size:13px;font-weight:900;line-height:1.05}}
@keyframes winpop{{0%{{transform:scale(.75)}}60%{{transform:scale(1.18)}}100%{{transform:scale(1)}}}}
.win{{animation:winpop .5s ease}}
</style>
</head>
<body>
<div class="box">
 <div class="label">🎰 DRAWING • FLASHING</div>
 <div id="animal" class="animal">❓</div>
 <div id="status" class="status">Selecting...</div>
</div>
<script>
const animals={animals_json};
const winner={winner_json};
const el=document.getElementById("animal");
const status=document.getElementById("status");

let i=0;
const sequence=[];
for(let n=0;n<28;n++) {{
  sequence.push(animals[Math.floor(Math.random()*animals.length)]);
}}
sequence.push(winner,winner,winner);

function next() {{
  const item=sequence[i];
  el.className="animal";
  el.textContent=item.emoji;

  if(i < 24) {{
    status.textContent="Flashing...";
  }} else if(i < sequence.length-1) {{
    status.textContent="Slowing down...";
  }} else {{
    status.textContent="🎉 " + winner.name + " — WINNER!";
    el.className="animal win";
  }}

  if(i < sequence.length-1) {{
    i++;
    const delay = i < 10 ? 55 : (i < 19 ? 80 : (i < 27 ? 130 : 240));
    setTimeout(next,delay);
  }}
}}
next();
</script>
</body>
</html>
""",
        height=138,
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
    else:
        st.session_state.status = "⚠️ Not enough coins"

def clear_bets():
    st.session_state.bets = {}
    st.session_state.status = "Choose your bet and animals"
    st.session_state.show_reveal = False

def start_round():
    stake = total_bet()
    if stake <= 0:
        st.session_state.status = "⚠️ Tap an animal to place a bet first"
        return
    if stake > st.session_state.balance:
        st.session_state.status = "⚠️ Not enough coins"
        return

    placed = dict(st.session_state.bets)

    # FAIR DRAW: select exactly one animal index independently of all bets.
    # secrets.randbelow(n) uses the OS-backed cryptographic RNG and gives each
    # index an equal probability. With 8 animals, each animal is 1/8 per round.
    # Bets, stake size, payout multiplier, and previous results are NOT inputs
    # to the draw. Repeated winners are therefore possible in true randomness.
    winner_index = secrets.randbelow(len(ANIMALS))
    winner = ANIMALS[winner_index]
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

    st.session_state.history.insert(
        0,
        {
            "round": st.session_state.round,
            "winner": winner,
            "category": category,
            "stake": stake,
            "winning_bet": winning_bet,
            "payout": payout,
            "won": won,
        },
    )
    st.session_state.history = st.session_state.history[:5]
    st.session_state.bets = {}
    st.session_state.winner = winner
    st.session_state.status = result
    st.session_state.round += 1
    st.session_state.show_reveal = True

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
with action_cols[0]:
    st.button(
        "▶ START ROUND",
        key="start_round",
        use_container_width=True,
        on_click=start_round,
    )
with action_cols[1]:
    st.button(
        "CLEAR",
        key="clear_bets",
        use_container_width=True,
        on_click=clear_bets,
    )

# History is displayed inside the main arena above.
# Keep the dedicated bottom history hidden to preserve the one-screen layout.
st.markdown('<div class="kz-history" style="display:none !important;">', unsafe_allow_html=True)
st.markdown('<div class="kz-history-title">🏆 LAST 5 WINNING RESULTS</div>', unsafe_allow_html=True)

if not st.session_state.history:
    st.markdown('<div style="color:#9e9f76;font-size:10px">No winning rounds yet.</div>', unsafe_allow_html=True)
else:
    chips = []
    for item in st.session_state.history[:5]:
        w = item["winner"]
        chips.append(
            f'<div class="kz-history-chip"><span class="animal">{w["emoji"]}</span>'
            f'{w["name"]}<span class="round">Round #{item["round"]}</span></div>'
        )
    st.markdown('<div class="kz-history-list">' + ''.join(chips) + '</div>', unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    '<div class="kz-footer">'
    '<span class="powered-by">POWERED BY MARGAUX Technology</span>'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown("</div>", unsafe_allow_html=True)
