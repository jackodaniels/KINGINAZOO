import random
import streamlit as st

st.set_page_config(
    page_title="KINGINAZOO",
    page_icon="👑",
    layout="centered",
)

ANIMALS = [
    {"id": "monkey", "name": "Monkey", "emoji": "🐒", "multiplier": 5},
    {"id": "koala", "name": "Koala", "emoji": "🐨", "multiplier": 5},
    {"id": "panda", "name": "Panda", "emoji": "🐼", "multiplier": 5},
    {"id": "lion", "name": "Lion", "emoji": "🦁", "multiplier": 5},
    {"id": "fish", "name": "Fish", "emoji": "🐟", "multiplier": 10},
    {"id": "crab", "name": "Crab", "emoji": "🦀", "multiplier": 15},
    {"id": "jelly", "name": "Jellyfish", "emoji": "🪼", "multiplier": 25},
    {"id": "turtle", "name": "Turtle", "emoji": "🐢", "multiplier": 50},
]

BET_OPTIONS = [1, 10, 100, 1000]

if "balance" not in st.session_state:
    st.session_state.balance = 10_000
if "round" not in st.session_state:
    st.session_state.round = 531
if "bets" not in st.session_state:
    st.session_state.bets = {}
if "history" not in st.session_state:
    st.session_state.history = []
if "selected_bet" not in st.session_state:
    st.session_state.selected_bet = 1
if "winner" not in st.session_state:
    st.session_state.winner = None
if "status" not in st.session_state:
    st.session_state.status = "Choose your bet and animals"

def total_bet():
    return sum(st.session_state.bets.values())

def fmt(value):
    return f"{int(value):,}"

st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #fff8dc 0%, #fffdf5 100%);
}
.brand {
    text-align:center;
    font-size:clamp(42px, 8vw, 68px);
    font-weight:1000;
    letter-spacing:2px;
    line-height:1;
    background:linear-gradient(90deg,#6843a5,#e39a18,#6843a5);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
    margin: 10px 0 5px;
}
.tagline {
    text-align:center;
    font-size:13px;
    font-weight:900;
    letter-spacing:4px;
    opacity:.65;
    margin-bottom:18px;
}
.card {
    background:rgba(255,255,255,.75);
    border:1px solid #e5dcc4;
    border-radius:20px;
    padding:18px;
}
.winner {
    text-align:center;
    font-size:88px;
    line-height:1;
    padding:15px;
}
.center {
    text-align:center;
}
.mult {
    display:inline-block;
    background:#ffe08a;
    border-radius:999px;
    padding:3px 8px;
    font-size:12px;
    font-weight:900;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="brand">👑 KINGINAZOO 🐾</div>', unsafe_allow_html=True)
st.markdown('<div class="tagline">GUESS • BET • WIN</div>', unsafe_allow_html=True)

c1, c2 = st.columns(2)
c1.metric("ROUND", f"#{st.session_state.round}")
c2.metric("💎 COINS", fmt(st.session_state.balance))

st.markdown('<div class="card">', unsafe_allow_html=True)
winner = st.session_state.winner
winner_emoji = winner["emoji"] if winner else "❓"
st.markdown(f'<div class="winner">{winner_emoji}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="center"><strong>{st.session_state.status}</strong></div>', unsafe_allow_html=True)

st.write("### Choose Bet")
bet_cols = st.columns(4)
for col, amount in zip(bet_cols, BET_OPTIONS):
    if col.button(
        f"💎 {fmt(amount)}",
        key=f"bet_{amount}",
        use_container_width=True,
        type="primary" if st.session_state.selected_bet == amount else "secondary",
    ):
        st.session_state.selected_bet = amount
        st.rerun()

current_total = total_bet()
available = st.session_state.balance - current_total
s1, s2 = st.columns(2)
s1.metric("Total Bet", f"💎 {fmt(current_total)}")
s2.metric("Available", f"💎 {fmt(available)}")
st.markdown("</div>", unsafe_allow_html=True)

st.write("### Choose Animals")
animal_cols = st.columns(4)

for i, animal in enumerate(ANIMALS):
    amount = st.session_state.bets.get(animal["id"], 0)
    with animal_cols[i % 4]:
        st.markdown(
            f"<div class='center' style='font-size:42px'>{animal['emoji']}</div>"
            f"<div class='center'><strong>{animal['name']}</strong></div>"
            f"<div class='center'><span class='mult'>x{animal['multiplier']}</span></div>"
            f"<div class='center' style='font-size:12px;margin:5px 0 8px'>"
            f"{'💎 ' + fmt(amount) if amount else 'No bet'}"
            f"</div>",
            unsafe_allow_html=True,
        )
        if st.button(
            f"+ 💎 {fmt(st.session_state.selected_bet)}",
            key=f"animal_{animal['id']}",
            use_container_width=True,
        ):
            if current_total + st.session_state.selected_bet <= st.session_state.balance:
                st.session_state.bets[animal["id"]] = amount + st.session_state.selected_bet
                st.session_state.status = f"Bet added to {animal['name']}"
            else:
                st.session_state.status = "⚠️ Not enough coins"
            st.rerun()

st.write("")
p1, p2 = st.columns([3, 1])

if p1.button("🎯 START ROUND", use_container_width=True, type="primary"):
    stake = total_bet()

    if stake <= 0:
        st.session_state.status = "⚠️ Place at least one bet first"
        st.rerun()

    if stake > st.session_state.balance:
        st.session_state.status = "⚠️ Not enough coins"
        st.rerun()

    # Deduct all bets first.
    placed = dict(st.session_state.bets)
    st.session_state.balance -= stake

    # Pick winner once; the UI cycles through animals several times before
    # displaying the final result, matching the requested flashing behavior.
    winner = random.choice(ANIMALS)

    # Flashing reveal using Streamlit reruns.
    placeholders = st.empty()
    for delay in [0.06] * 10 + [0.09] * 8 + [0.13] * 7 + [0.20] * 5:
        shown = random.choice(ANIMALS)
        placeholders.markdown(
            f'<div class="winner">{shown["emoji"]}</div>',
            unsafe_allow_html=True,
        )
        import time
        time.sleep(delay)

    placeholders.markdown(
        f'<div class="winner">{winner["emoji"]}</div>',
        unsafe_allow_html=True,
    )

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
            "stake": stake,
            "winning_bet": winning_bet,
            "payout": payout,
            "won": won,
        },
    )
    st.session_state.history = st.session_state.history[:15]
    st.session_state.bets = {}
    st.session_state.winner = winner
    st.session_state.status = result
    st.session_state.round += 1
    st.rerun()

if p2.button("CLEAR", use_container_width=True):
    st.session_state.bets = {}
    st.session_state.winner = None
    st.session_state.status = "Choose your bet and animals"
    st.rerun()

st.write("### 📜 Round History")
if not st.session_state.history:
    st.info("No rounds played yet.")
else:
    for item in st.session_state.history:
        winner = item["winner"]
        result = (
            f"+💎 {fmt(item['payout'])}"
            if item["won"]
            else f"−💎 {fmt(item['stake'])}"
        )
        st.write(
            f"**#{item['round']}** {winner['emoji']} {winner['name']} "
            f"×{winner['multiplier']} — **{result}**"
        )

st.caption("KINGINAZOO prototype — virtual coins only.")
