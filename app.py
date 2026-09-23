# KINGINAZOO — generated jungle background is loaded from assets/zoobg.png
import json
import random
import streamlit as st
import streamlit.components.v1 as components

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
    "land_jackpot": 25000,
    "ocean_jackpot": 25000,
    "jackpot_category": "Land",
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
# Handle URL actions. HTML cards are real links, so the WHOLE animal
# card is clickable on mobile and desktop.
# ---------------------------------------------------------------------
params = st.query_params
action = params.get("action")
value = params.get("value")

if action:
    st.query_params.clear()

    if action == "bet":
        try:
            amount = int(value)
        except (TypeError, ValueError):
            amount = 1

        if amount in BET_OPTIONS:
            st.session_state.selected_bet = amount
            st.session_state.status = f"💎 {fmt(amount)} bet selected"
            st.session_state.show_reveal = False

    elif action == "animal":
        animal = get_animal(value)
        if animal:
            current = st.session_state.bets.get(animal["id"], 0)
            new_total = total_bet() + st.session_state.selected_bet

            if new_total <= st.session_state.balance:
                st.session_state.bets[animal["id"]] = (
                    current + st.session_state.selected_bet
                )
                st.session_state.status = (
                    f'{animal["emoji"]} {animal["name"]} • '
                    f'💎 {fmt(st.session_state.bets[animal["id"]])}'
                )
                st.session_state.show_reveal = False
            else:
                st.session_state.status = "⚠️ Not enough coins"

    elif action == "jackpot":
        if value in ("Land", "Ocean"):
            st.session_state.jackpot_category = value
            st.session_state.status = f"💰 {value} Jackpot selected"

    elif action == "clear":
        st.session_state.bets = {}
        st.session_state.status = "Choose your bet and animals"
        st.session_state.show_reveal = False

    elif action == "start":
        stake = total_bet()

        if stake <= 0:
            st.session_state.status = "⚠️ Tap an animal to place a bet first"
        elif stake > st.session_state.balance:
            st.session_state.status = "⚠️ Not enough coins"
        else:
            placed = dict(st.session_state.bets)
            pool = [a for a in ANIMALS if a["category"] == st.session_state.jackpot_category]
            winner = random.choice(pool)

            st.session_state.balance -= stake

            winning_bet = placed.get(winner["id"], 0)
            payout = winning_bet * winner["multiplier"]
            won = winning_bet > 0

            if won:
                st.session_state.balance += payout
                if winner["category"] == "Land":
                    st.session_state.land_jackpot += max(1, stake // 100)
                else:
                    st.session_state.ocean_jackpot += max(1, stake // 100)
                result = f"🎉 {winner['name']} WON! +💎 {fmt(payout)}"
            else:
                result = f"{winner['name']} WON — no winning bet"

            st.session_state.history.insert(
                0,
                {
                    "round": st.session_state.round,
                    "winner": winner,
                    "stake": stake,
                    "winning_bet": winning_bet,
                    "payout": payout,
                    "won": won,
                },
            )
            st.session_state.history = st.session_state.history[:12]

            st.session_state.bets = {}
            st.session_state.winner = winner
            st.session_state.status = result
            st.session_state.round += 1
            st.session_state.show_reveal = True


# ---------------------------------------------------------------------
# Full KINGINAZOO visual system
# ---------------------------------------------------------------------
st.markdown(
    """
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
    background:
        linear-gradient(rgba(0, 35, 18, .20), rgba(0, 22, 12, .34)),
        url("assets/zoobg.png") center top / cover fixed no-repeat !important;
    background-color: #031d11 !important;
    color: var(--text) !important;
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


/* Brand / generated background contains the main KINGINAZOO logo */
.kz-brand {
    position: relative;
    z-index: 2;
    height: clamp(95px, 15vw, 155px);
    text-align: center;
    margin: 0 auto 8px;
}
.kz-logo, .kz-tag {
    display: none;
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
    min-height: 210px;
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
    height: 125px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: clamp(76px, 10vw, 112px);
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
    min-height: 58px;
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

/* Animal grid */
.kz-animals {
    position: relative;
    z-index: 2;
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 11px;
}
.kz-animal {
    min-height: 205px;
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
    font-size: clamp(48px, 7vw, 75px);
    line-height: 1;
    filter: drop-shadow(0 7px 5px rgba(0,0,0,.45));
}
.kz-animal-name {
    font-size: 17px;
    font-weight: 1000;
    margin-top: 8px;
}
.kz-multi {
    background: linear-gradient(180deg,#ffe875,#eebd25);
    color: #17230d;
    border-radius: 99px;
    padding: 5px 13px;
    font-size: 14px;
    font-weight: 1000;
    margin-top: 6px;
}
.kz-amount {
    width: 75%;
    text-align: center;
    background: rgba(0,0,0,.22);
    border: 1px solid #d8c45d;
    border-radius: 12px;
    padding: 6px;
    color: #fff6b9;
    font-size: 14px;
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
    margin-top: 16px;
}
.kz-action {
    min-height: 64px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 18px;
    text-decoration: none !important;
    font-size: 20px;
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

/* Footer */
.kz-footer {
    position: relative;
    z-index: 2;
    text-align: center;
    color: #8d956e;
    font-size: 10px;
    letter-spacing: 3px;
    margin-top: 18px;
}

/* Streamlit iframe animation should blend in */
iframe[title="streamlit.components.v1.html"] {
    width: 100% !important;
    border: 0 !important;
    background: transparent !important;
}


/* Jackpot selector */
.kz-jackpot-wrap {
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
        background:
            linear-gradient(rgba(0, 35, 18, .25), rgba(0, 22, 12, .40)),
            url("assets/zoobg.png") center top / auto 100vh fixed no-repeat !important;
        background-color: #031d11 !important;
    }

    .block-container {
        max-width: 560px !important;
        padding: 9px 7px 24px !important;
    }
    .kz-logo { font-size: 40px; }
    .kz-tag { letter-spacing: 3px; }
    .kz-top { gap: 7px; }
    .kz-stat { padding: 9px 10px; border-radius: 15px; }
    .kz-stat-label { font-size: 9px; }
    .kz-stat-value { font-size: 19px; }
    .kz-arena { min-height: 160px; border-radius: 21px; }
    .kz-winner { height: 92px; font-size: 68px; }
    .kz-bets { gap: 5px; }
    .kz-bet { min-height: 49px; border-radius: 14px; font-size: 13px; }
    .kz-summary { font-size: 11px; }
    .kz-animals { gap: 6px; }
    .kz-animal { min-height: 140px; border-radius: 15px; }
    .kz-animal-emoji { font-size: 43px; }
    .kz-animal-name { font-size: 11px; margin-top: 5px; }
    .kz-multi { font-size: 10px; padding: 4px 8px; }
    .kz-amount { font-size: 10px; width: 82%; padding: 4px; }
    .kz-add { font-size: 8px; }
    .kz-actions { gap: 6px; margin-top: 10px; }
    .kz-action { min-height: 53px; font-size: 14px; border-radius: 15px; }
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown('<div class="kz-page">', unsafe_allow_html=True)

# Brand
st.markdown(
    """
<div class="kz-brand">
  <div class="kz-logo">👑 KINGINAZOO 🐾</div>
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
</div>
""",
    unsafe_allow_html=True,
)

# Jackpot selector
land_active = "active" if st.session_state.jackpot_category == "Land" else ""
ocean_active = "active" if st.session_state.jackpot_category == "Ocean" else ""

st.markdown(
    f"""
<div class="kz-jackpot-wrap">
  <div class="kz-jackpot-title">💰 JACKPOT</div>
  <div class="kz-jackpots">
    <a class="kz-jackpot {land_active}" href="?action=jackpot&value=Land">
      <div class="kz-jackpot-icon">🌿</div>
      <div class="kz-jackpot-name">LAND</div>
      <div class="kz-jackpot-value">💎 {fmt(st.session_state.land_jackpot)}</div>
      <div class="kz-jackpot-sub">Monkey • Koala • Panda • Lion</div>
    </a>
    <a class="kz-jackpot {ocean_active}" href="?action=jackpot&value=Ocean">
      <div class="kz-jackpot-icon">🌊</div>
      <div class="kz-jackpot-name">OCEAN</div>
      <div class="kz-jackpot-value">💎 {fmt(st.session_state.ocean_jackpot)}</div>
      <div class="kz-jackpot-sub">Fish • Crab • Jellyfish • Turtle</div>
    </a>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# Bet buttons
st.markdown('<div class="kz-section-title">💎 CHOOSE YOUR BET</div>', unsafe_allow_html=True)

bet_html = '<div class="kz-bets">'
for amount in BET_OPTIONS:
    active = "active" if amount == st.session_state.selected_bet else ""
    bet_html += (
        f'<a class="kz-bet {active}" '
        f'href="?action=bet&value={amount}">💎 {fmt(amount)}</a>'
    )
bet_html += "</div>"
st.markdown(bet_html, unsafe_allow_html=True)

st.markdown(
    f"""
<div class="kz-summary">
  <span>Total Bet: 💎 {fmt(total_bet())}</span>
  <span>Available: 💎 {fmt(st.session_state.balance - total_bet())}</span>
</div>
""",
    unsafe_allow_html=True,
)

# Animal cards
st.markdown('<div class="kz-section-title">🐾 TAP AN ANIMAL TO BET</div>', unsafe_allow_html=True)

animal_html = '<div class="kz-animals">'
for animal in ANIMALS:
    amount = st.session_state.bets.get(animal["id"], 0)
    active = "hasbet" if amount else ""
    animal_html += f"""
<a class="kz-animal {active}" href="?action=animal&value={animal['id']}">
  <div class="kz-animal-emoji">{animal['emoji']}</div>
  <div class="kz-animal-name">{animal['name']}</div>
  <div class="kz-multi">x{animal['multiplier']}</div>
  <div class="kz-amount">💎 {fmt(amount)}</div>
  <div class="kz-add">TAP +💎 {fmt(st.session_state.selected_bet)}</div>
</a>
"""
animal_html += "</div>"
st.markdown(animal_html, unsafe_allow_html=True)

# Actions
st.markdown(
    """
<div class="kz-actions">
  <a class="kz-action kz-start" href="?action=start">▶ START ROUND</a>
  <a class="kz-action kz-clear" href="?action=clear">CLEAR</a>
</div>
""",
    unsafe_allow_html=True,
)

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
.box{{margin-top:12px;background:#032715;border:3px solid #ffd84d;border-radius:22px;
padding:9px;text-align:center;box-shadow:0 0 22px rgba(255,216,77,.18)}}
.label{{color:#e5d68b;font-size:10px;font-weight:900;letter-spacing:2px}}
.animal{{height:105px;display:flex;align-items:center;justify-content:center;font-size:78px;
filter:drop-shadow(0 8px 6px rgba(0,0,0,.5))}}
.status{{color:#fff1a4;font-size:14px;font-weight:900}}
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
        height=145,
        scrolling=False,
    )

# History
st.markdown('<div class="kz-history">', unsafe_allow_html=True)
st.markdown('<div class="kz-history-title">🕘 RECENT ROUNDS</div>', unsafe_allow_html=True)

if not st.session_state.history:
    st.markdown(
        '<div style="color:#9e9f76;font-size:11px">No rounds yet.</div>',
        unsafe_allow_html=True,
    )
else:
    for item in st.session_state.history:
        w = item["winner"]
        result = (
            f'+💎 {fmt(item["payout"])}'
            if item["won"]
            else f'−💎 {fmt(item["stake"])}'
        )
        cls = "kz-win" if item["won"] else "kz-loss"
        st.markdown(
            f"""
<div class="kz-row">
  <span>#{item["round"]} &nbsp; {w["emoji"]} {w["name"]} ×{w["multiplier"]}</span>
  <span class="{cls}">{result}</span>
</div>
""",
            unsafe_allow_html=True,
        )

st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    '<div class="kz-footer">👑 &nbsp; KINGINAZOO &nbsp; 👑<br>'
    '<span style="font-size:8px">PLAY RESPONSIBLY • HAVE FUN!</span></div>',
    unsafe_allow_html=True,
)

st.markdown("</div>", unsafe_allow_html=True)
