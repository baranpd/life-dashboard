import streamlit as st
import json
import datetime
import hashlib
import time
import requests
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from pathlib import Path

# ============================================================
# 🌟 Baran Family Life Dashboard — Streamlit Edition
# ============================================================

st.set_page_config(
    page_title="🌟 Baran Family Life Dashboard",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- CONSTANTS ----
PILLARS = [
    {"emoji": "💪", "name": "Strong Body", "desc": "Move and eat well", "color": "#e85d75"},
    {"emoji": "🧠", "name": "Smart Brain", "desc": "Read, learn, build skills", "color": "#4a90d9"},
    {"emoji": "😊", "name": "Big Feelings", "desc": "Stay calm when frustrated", "color": "#e07baa"},
    {"emoji": "🤝", "name": "Kind Friend", "desc": "Treat people well", "color": "#3aafa9"},
    {"emoji": "🎯", "name": "Try Hard Things", "desc": "Don't quit when it's tough", "color": "#e8793a"},
    {"emoji": "💰", "name": "Money Smarts", "desc": "Save some of what you get", "color": "#e0aa3e"},
    {"emoji": "🏠", "name": "Help the Family", "desc": "Chores + responsibility", "color": "#5cb85c"},
    {"emoji": "🌎", "name": "Big Dreams", "desc": "Think big", "color": "#9b72cf"},
]

DATA_FILE = "family_data.json"

# ---- DATA PERSISTENCE (JSON file) ----
def load_data():
    if "store" not in st.session_state:
        if Path(DATA_FILE).exists():
            with open(DATA_FILE, "r") as f:
                st.session_state.store = json.load(f)
        else:
            st.session_state.store = {"family": "Baran", "members": []}
    return st.session_state.store

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(st.session_state.store, f, indent=2, default=str)

def uid():
    return hashlib.md5(f"{datetime.datetime.now().isoformat()}{id(object())}".encode()).hexdigest()[:10]

def new_member(name, role, is_kid, dreams):
    return {
        "id": uid(),
        "name": name,
        "role": role,
        "isKid": is_kid,
        "dreams": dreams or {"want": "", "curious": "", "learn": ""},
        "pillars": [
            {"name": p["name"], "subs": [{"text": "", "done": False} for _ in range(8)]}
            for p in PILLARS
        ],
        "goals": [],
        "wins": [],
        "snapshots": [],
    }

def get_active():
    store = load_data()
    mid = st.session_state.get("active_member")
    if mid:
        for m in store["members"]:
            if m["id"] == mid:
                return m
    return None

# ---- CUSTOM CSS ----
st.markdown("""
<style>
    .stApp { background-color: #fef9f0; }
    .main .block-container { padding-top: 1rem; max-width: 1200px; }
    
    div[data-testid="stMetric"] {
        background: white;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 2px 12px rgba(45,42,38,0.06);
    }
    
    .pillar-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 12px rgba(45,42,38,0.06);
        border-top: 4px solid;
        margin-bottom: 12px;
    }
    
    .goal-card {
        background: #fff7eb;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 8px;
        border-left: 4px solid;
    }
    
    .dream-banner {
        background: linear-gradient(135deg, #fff0e4, #fdf5e0);
        border-radius: 16px;
        padding: 24px;
        border: 2px dashed #e0aa3e;
        text-align: center;
        margin-bottom: 20px;
    }
    
    .win-card {
        background: white;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 2px 8px rgba(45,42,38,0.05);
    }
    
    .snap-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 12px rgba(45,42,38,0.06);
    }
    
    .mandala-cell {
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        border-radius: 4px;
        padding: 4px;
        font-size: 11px;
        min-height: 50px;
        word-break: break-word;
    }
    
    .overdue { color: #e85d75; font-weight: 700; }

    h1, h2, h3 { font-family: 'Nunito', sans-serif !important; }

    /* NFL Draft styles */
    .nfl-header {
        background: linear-gradient(135deg, #013369 0%, #0a3d8a 60%, #d50a0a 100%);
        border-radius: 16px;
        padding: 22px 28px;
        color: white;
        margin-bottom: 18px;
    }
    .clock-card {
        background: linear-gradient(135deg, #013369, #0a3d8a);
        border-radius: 14px;
        padding: 22px 26px;
        color: white;
        margin-bottom: 16px;
        border: 2px solid #d4af37;
        box-shadow: 0 4px 20px rgba(1,51,105,0.25);
    }
    .pick-row {
        background: white;
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 7px;
        box-shadow: 0 1px 6px rgba(0,0,0,0.06);
        border-left: 4px solid;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .pick-number {
        font-size: 20px;
        font-weight: 800;
        color: #013369;
        min-width: 40px;
        text-align: center;
    }
    .pos-badge {
        display: inline-block;
        padding: 3px 9px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        color: white;
        letter-spacing: 0.5px;
    }
    .upcoming-card {
        background: white;
        border-radius: 10px;
        padding: 14px;
        text-align: center;
        border: 2px solid #ede6da;
        margin-bottom: 8px;
    }
    .upcoming-card.on-clock {
        background: #fff8e0;
        border-color: #d4af37;
    }
    .draft-complete-banner {
        background: linear-gradient(135deg, #1a6e1a, #2e9e2e);
        border-radius: 14px;
        padding: 24px;
        color: white;
        text-align: center;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)

# ---- SIDEBAR ----
store = load_data()

with st.sidebar:
    st.markdown("## 🌟 Family Dashboard")
    
    # Member selector
    member_names = [f"{m['name']} ({m['role']})" if m.get("role") else m["name"] for m in store["members"]]
    
    if member_names:
        selected_idx = st.selectbox(
            "👤 Family Member",
            range(len(member_names)),
            format_func=lambda i: member_names[i],
            key="member_selector"
        )
        st.session_state.active_member = store["members"][selected_idx]["id"]
    else:
        st.info("No family members yet. Add one below!")
    
    st.divider()
    
    # Add member
    with st.expander("➕ Add Family Member"):
        new_name = st.text_input("Name", key="new_name")
        new_role = st.selectbox("Role", ["Dad", "Mom", "Son", "Daughter", "Other"], key="new_role")
        new_dream = st.text_area("Big Dream", placeholder="What's the ONE thing you'd love to accomplish?", key="new_dream")
        
        if st.button("🚀 Create Roadmap", type="primary", use_container_width=True):
            if new_name:
                is_kid = new_role in ["Son", "Daughter"]
                member = new_member(new_name, new_role, is_kid, {"want": new_dream, "curious": "", "learn": ""})
                store["members"].append(member)
                st.session_state.active_member = member["id"]
                save_data()
                st.rerun()
            else:
                st.warning("Please enter a name")
    
    st.divider()
    
    # Import / Export
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Export", use_container_width=True):
            st.download_button(
                "📥 Download JSON",
                json.dumps(store, indent=2, default=str),
                "baran-life-dashboard.json",
                "application/json",
                use_container_width=True
            )
    with col2:
        uploaded = st.file_uploader("📂 Import", type=["json"], label_visibility="collapsed")
        if uploaded:
            try:
                imported = json.loads(uploaded.read())
                if "members" in imported:
                    st.session_state.store = imported
                    save_data()
                    st.success("Imported!")
                    st.rerun()
            except:
                st.error("Invalid file")

# ---- MAIN CONTENT ----
member = get_active()

if not member:
    st.markdown("""
    <div class="dream-banner">
        <h1>🌟 Welcome to the Baran Family Life Dashboard</h1>
        <p style="font-size: 18px; color: #7a7267;">
            Based on Shohei Ohtani's Mandala Chart — turn your big dream into 8 life areas and 64 actions.
        </p>
        <p style="color: #b0a898;">Add a family member in the sidebar to get started →</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show the 8 pillars as intro
    cols = st.columns(4)
    for i, p in enumerate(PILLARS):
        with cols[i % 4]:
            st.markdown(f"""
            <div class="pillar-card" style="border-top-color: {p['color']};">
                <div style="font-size: 32px;">{p['emoji']}</div>
                <h3 style="margin: 4px 0;">{p['name']}</h3>
                <p style="font-size: 13px; color: #7a7267;">{p['desc']}</p>
            </div>
            """, unsafe_allow_html=True)
    st.stop()

# ---- TABS ----
tab_life, tab_goals, tab_wins, tab_snap, tab_grid, tab_chat, tab_nfl = st.tabs([
    "🎯 Life Board", "⭐ Growth Goals", "🟢 Weekly Wins",
    "📸 Snapshots", "🧩 Full Grid", "💬 Growth Chat", "🏈 NFL Draft R2"
])

# ==========================
# 🎯 LIFE BOARD
# ==========================
with tab_life:
    # Dream banner
    dreams = member.get("dreams", {})
    st.markdown(f"""
    <div class="dream-banner">
        <h2>🌎 {member['name']}'s Big Dreams</h2>
        {'<p>🚀 <strong>Dream:</strong> ' + dreams.get('want', '') + '</p>' if dreams.get('want') else ''}
        {'<p>🔍 <strong>Curious about:</strong> ' + dreams.get('curious', '') + '</p>' if dreams.get('curious') else ''}
        {'<p>📚 <strong>Want to learn:</strong> ' + dreams.get('learn', '') + '</p>' if dreams.get('learn') else ''}
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("✏️ Edit Dreams"):
        d_want = st.text_area("When I grow up I might want to…", value=dreams.get("want", ""), key="d_want")
        d_curious = st.text_area("I'm curious about…", value=dreams.get("curious", ""), key="d_curious")
        d_learn = st.text_area("I want to learn more about…", value=dreams.get("learn", ""), key="d_learn")
        if st.button("Save Dreams", type="primary"):
            member["dreams"] = {"want": d_want, "curious": d_curious, "learn": d_learn}
            save_data()
            st.rerun()
    
    # Overall metrics
    total_goals = len(member["goals"])
    nailed = len([g for g in member["goals"] if g.get("status") == "nailed"])
    goals_with_target = [g for g in member["goals"] if g.get("target", 0) > 0]
    avg_progress = (
        round(sum(min(100, round(g["actual"] / g["target"] * 100)) for g in goals_with_target) / len(goals_with_target))
        if goals_with_target else 0
    )
    overdue_count = len([
        g for g in member["goals"]
        if g.get("due") and g["due"] < str(datetime.date.today()) and g.get("status") != "nailed"
    ])
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Goals", total_goals)
    c2.metric("🏆 Nailed", nailed)
    c3.metric("📊 Avg Progress", f"{avg_progress}%")
    c4.metric("⚠️ Overdue", overdue_count)
    
    # Charts
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        # Ring chart
        fig_ring = go.Figure(go.Pie(
            values=[nailed, max(total_goals - nailed, 0)],
            labels=["Nailed", "In Progress"],
            hole=0.7,
            marker_colors=["#e8793a", "#ede6da"],
            textinfo="none"
        ))
        fig_ring.update_layout(
            title="Overall Completion",
            showlegend=False,
            height=250,
            margin=dict(t=40, b=20, l=20, r=20),
            paper_bgcolor="rgba(0,0,0,0)",
            annotations=[dict(text=f"{round(nailed/total_goals*100) if total_goals else 0}%", 
                            x=0.5, y=0.5, font_size=28, font_color="#e8793a", showarrow=False)]
        )
        st.plotly_chart(fig_ring, use_container_width=True)
    
    with col_chart2:
        # Bar chart by pillar
        pillar_pcts = []
        for i, p in enumerate(PILLARS):
            pg = [g for g in member["goals"] if g.get("area") == i and g.get("target", 0) > 0]
            pct = round(sum(min(100, round(g["actual"]/g["target"]*100)) for g in pg) / len(pg)) if pg else 0
            pillar_pcts.append(pct)
        
        fig_bar = go.Figure(go.Bar(
            x=[p["emoji"] + " " + p["name"] for p in PILLARS],
            y=pillar_pcts,
            marker_color=[p["color"] for p in PILLARS],
            text=[f"{v}%" for v in pillar_pcts],
            textposition="outside"
        ))
        fig_bar.update_layout(
            title="Progress by Area",
            height=250,
            margin=dict(t=40, b=20, l=20, r=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(range=[0, 110], showgrid=False),
            xaxis=dict(tickangle=-45)
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Pillar tiles
    st.markdown("### 📋 Life Areas")
    cols = st.columns(4)
    for i, p in enumerate(PILLARS):
        with cols[i % 4]:
            area_goals = [g for g in member["goals"] if g.get("area") == i]
            wt = [g for g in area_goals if g.get("target", 0) > 0]
            pct = round(sum(min(100, round(g["actual"]/g["target"]*100)) for g in wt) / len(wt)) if wt else 0
            od = len([g for g in area_goals if g.get("due") and g["due"] < str(datetime.date.today()) and g.get("status") != "nailed"])
            
            st.markdown(f"""
            <div class="pillar-card" style="border-top-color: {p['color']};">
                <div style="font-size: 28px;">{p['emoji']}</div>
                <h4 style="margin: 4px 0;">{p['name']}</h4>
                <p style="font-size: 12px; color: #7a7267; margin-bottom: 8px;">{p['desc']}</p>
                <p style="font-size: 12px;"><strong>{len(area_goals)}</strong> goals · <strong>{pct}%</strong> progress
                {'<span class="overdue"> · ⚠️ ' + str(od) + ' overdue</span>' if od else ''}</p>
                <div style="height:6px;background:#ede6da;border-radius:6px;overflow:hidden;margin-top:8px;">
                    <div style="height:100%;width:{pct}%;background:{p['color']};border-radius:6px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ==========================
# ⭐ GROWTH GOALS
# ==========================
with tab_goals:
    st.markdown(f"### ⭐ {member['name']}'s Growth Goals")
    
    # Filter
    filter_options = ["All"] + [f"{p['emoji']} {p['name']}" for p in PILLARS]
    selected_filter = st.selectbox("Filter by area", filter_options, key="goal_filter")
    
    filtered_goals = member["goals"]
    if selected_filter != "All":
        filter_idx = filter_options.index(selected_filter) - 1
        filtered_goals = [g for g in member["goals"] if g.get("area") == filter_idx]
    
    # Display goals
    for g in filtered_goals:
        p = PILLARS[g.get("area", 0)]
        pct = min(100, round(g["actual"] / g["target"] * 100)) if g.get("target", 0) > 0 else 0
        is_overdue = g.get("due") and g["due"] < str(datetime.date.today()) and g.get("status") != "nailed"
        status_label = {"growing": "🌱 Growing", "working": "💪 Working Hard", "nailed": "🏆 Nailed It"}.get(g.get("status"), "🌱 Growing")
        due_str = g.get("due", "")
        ms_done = len([ms for ms in g.get("milestones", []) if ms.get("done")])
        ms_total = len(g.get("milestones", []))
        
        with st.expander(f"{p['emoji']} **{g['name']}** — {status_label} {'⚠️ OVERDUE' if is_overdue else ''}", expanded=False):
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                if g.get("betterAt"):
                    st.caption(f"**Better at:** {g['betterAt']}")
                if g.get("habit"):
                    st.caption(f"**Habit:** {g['habit']}")
            with col2:
                st.caption(f"**Quarter:** {g.get('quarter', 'Q1')}")
                if due_str:
                    st.caption(f"**Due:** {due_str}")
            with col3:
                if g.get("target", 0) > 0:
                    st.metric("Progress", f"{g.get('actual', 0)}/{g['target']} {g.get('unit', '')}", f"{pct}%")
            
            # Progress bar
            if g.get("target", 0) > 0:
                bar_color = "#5cb85c" if pct >= 100 else "#e85d75" if is_overdue else "#e8793a"
                st.markdown(f"""
                <div style="height:10px;background:#ede6da;border-radius:10px;overflow:hidden;">
                    <div style="height:100%;width:{pct}%;background:{bar_color};border-radius:10px;"></div>
                </div>
                """, unsafe_allow_html=True)
            
            # Milestones
            if ms_total > 0:
                st.caption(f"**Milestones:** {ms_done}/{ms_total}")
                for mi, ms in enumerate(g.get("milestones", [])):
                    new_done = st.checkbox(ms["text"], value=ms.get("done", False), key=f"ms_{g['id']}_{mi}")
                    if new_done != ms.get("done", False):
                        ms["done"] = new_done
                        save_data()
                        st.rerun()
            
            # Edit
            st.divider()
            ecol1, ecol2 = st.columns(2)
            with ecol1:
                new_actual = st.number_input("Update Actual", value=g.get("actual", 0), min_value=0, key=f"act_{g['id']}")
                if new_actual != g.get("actual", 0):
                    g["actual"] = new_actual
                    save_data()
            with ecol2:
                new_status = st.selectbox("Status", ["growing", "working", "nailed"],
                    index=["growing", "working", "nailed"].index(g.get("status", "growing")),
                    format_func=lambda s: {"growing": "🌱 Growing", "working": "💪 Working Hard", "nailed": "🏆 Nailed It"}[s],
                    key=f"st_{g['id']}")
                if new_status != g.get("status"):
                    g["status"] = new_status
                    save_data()
            
            if st.button("🗑️ Delete Goal", key=f"del_{g['id']}"):
                member["goals"] = [x for x in member["goals"] if x["id"] != g["id"]]
                save_data()
                st.rerun()
    
    # Add goal
    st.divider()
    st.markdown("### ➕ Add New Goal")
    with st.form("add_goal_form"):
        gc1, gc2 = st.columns(2)
        with gc1:
            g_name = st.text_input("Goal Name", placeholder="e.g., Read 20 books")
            g_area = st.selectbox("Growth Area", range(8), format_func=lambda i: f"{PILLARS[i]['emoji']} {PILLARS[i]['name']}")
            g_better = st.text_input("What I want to be better at", placeholder="e.g., Focusing")
            g_habit = st.text_input("My small habit", placeholder="e.g., Read 15 min before bed")
        with gc2:
            g_target = st.number_input("Target", min_value=0, value=0)
            g_actual = st.number_input("Current actual", min_value=0, value=0)
            g_unit = st.text_input("Unit", placeholder="e.g., books, miles, dollars")
            g_due = st.date_input("Due date", value=None)
            g_quarter = st.selectbox("Quarter", ["Q1", "Q2", "Q3", "Q4"])
        
        # Milestones
        st.markdown("**Milestones** (one per line)")
        g_milestones_text = st.text_area("Enter milestones", placeholder="Finish chapter 1\nFinish chapter 5\nComplete final project", key="ms_text")
        
        if st.form_submit_button("💾 Save Goal", type="primary"):
            if g_name:
                milestones = [{"text": line.strip(), "done": False} for line in g_milestones_text.split("\n") if line.strip()]
                new_goal = {
                    "id": uid(), "name": g_name, "area": g_area, "betterAt": g_better,
                    "habit": g_habit, "target": g_target, "actual": g_actual, "unit": g_unit,
                    "due": str(g_due) if g_due else "", "quarter": g_quarter,
                    "status": "growing", "milestones": milestones
                }
                member["goals"].append(new_goal)
                save_data()
                st.rerun()
            else:
                st.warning("Goal needs a name!")

# ==========================
# 🟢 WEEKLY WINS
# ==========================
with tab_wins:
    st.markdown(f"### 🟢 {member['name']}'s Weekly Wins")
    
    # Add win
    with st.expander("➕ Log This Week", expanded=len(member.get("wins", [])) == 0):
        with st.form("add_win_form"):
            w_date = st.date_input("Week of", value=datetime.date.today())
            wc1, wc2 = st.columns(2)
            with wc1:
                w_body = st.slider("💪 Took care of my body", 1, 5, 3)
                w_practice = st.slider("🧠 Practiced something", 1, 5, 3)
            with wc2:
                w_kind = st.slider("🤝 Was kind", 1, 5, 3)
                w_tried = st.slider("🎯 Tried even when hard", 1, 5, 3)
            w_proud = st.text_area("Something I'm proud of", placeholder="Something that made me feel good...")
            
            st.caption("**Scoring:** 1 = I forgot · 3 = I tried sometimes · 5 = I really did it")
            
            if st.form_submit_button("🟢 Save Win", type="primary"):
                win = {
                    "id": uid(), "date": str(w_date),
                    "body": w_body, "practice": w_practice,
                    "kind": w_kind, "tried": w_tried,
                    "proud": w_proud
                }
                if "wins" not in member:
                    member["wins"] = []
                member["wins"].append(win)
                save_data()
                st.rerun()
    
    # Display wins
    wins = sorted(member.get("wins", []), key=lambda w: w.get("date", ""), reverse=True)
    
    if wins:
        # Trend chart
        if len(wins) >= 2:
            win_df = pd.DataFrame(wins)
            win_df["avg"] = (win_df["body"] + win_df["practice"] + win_df["kind"] + win_df["tried"]) / 4
            win_df["date"] = pd.to_datetime(win_df["date"])
            fig_trend = px.line(win_df.sort_values("date"), x="date", y="avg",
                              title="Weekly Average Over Time", markers=True)
            fig_trend.update_traces(line_color="#e8793a")
            fig_trend.update_layout(height=250, paper_bgcolor="rgba(0,0,0,0)",
                                   plot_bgcolor="rgba(0,0,0,0)", yaxis=dict(range=[0, 5.5]))
            st.plotly_chart(fig_trend, use_container_width=True)
        
        cols = st.columns(2)
        for i, w in enumerate(wins):
            with cols[i % 2]:
                avg = round((w["body"] + w["practice"] + w["kind"] + w["tried"]) / 4, 1)
                st.markdown(f"""
                <div class="win-card">
                    <div style="display:flex;justify-content:space-between;margin-bottom:12px;">
                        <strong>Week of {w['date']}</strong>
                        <span style="color:#b0a898;">Avg: {avg}/5</span>
                    </div>
                    <p>💪 Body: <strong>{w['body']}/5</strong> · 🧠 Practice: <strong>{w['practice']}/5</strong></p>
                    <p>🤝 Kind: <strong>{w['kind']}/5</strong> · 🎯 Tried: <strong>{w['tried']}/5</strong></p>
                    {'<p style="margin-top:8px;padding-top:8px;border-top:1px solid #ede6da;font-style:italic;color:#7a7267;">✨ ' + w.get("proud", "") + '</p>' if w.get("proud") else ''}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No wins logged yet — start tracking above!")

# ==========================
# 📸 SNAPSHOTS
# ==========================
with tab_snap:
    st.markdown(f"### 📸 {member['name']}'s Quarterly Snapshots")
    
    if st.button("📸 Take Snapshot Now", type="primary"):
        now = datetime.datetime.now()
        q_num = (now.month - 1) // 3 + 1
        snap = {
            "id": uid(),
            "date": now.isoformat(),
            "quarter": f"Q{q_num} {now.year}",
            "totalGoals": len(member["goals"]),
            "nailed": len([g for g in member["goals"] if g.get("status") == "nailed"]),
            "pillars": []
        }
        for i, p in enumerate(PILLARS):
            ag = [g for g in member["goals"] if g.get("area") == i]
            wt = [g for g in ag if g.get("target", 0) > 0]
            pct = round(sum(min(100, round(g["actual"]/g["target"]*100)) for g in wt) / len(wt)) if wt else 0
            snap["pillars"].append({
                "emoji": p["emoji"], "name": p["name"],
                "goalCount": len(ag), "avgPct": pct,
                "nailed": len([g for g in ag if g.get("status") == "nailed"]),
                "color": p["color"]
            })
        if "snapshots" not in member:
            member["snapshots"] = []
        member["snapshots"].append(snap)
        save_data()
        st.rerun()
    
    snapshots = list(reversed(member.get("snapshots", [])))
    
    if snapshots:
        # Compare chart if multiple
        if len(snapshots) >= 2:
            snap_data = []
            for s in snapshots:
                for sp in s["pillars"]:
                    snap_data.append({"Quarter": s["quarter"], "Pillar": sp["name"], "Progress": sp["avgPct"]})
            snap_df = pd.DataFrame(snap_data)
            fig_comp = px.bar(snap_df, x="Pillar", y="Progress", color="Quarter", barmode="group",
                            title="Progress Comparison Across Quarters")
            fig_comp.update_layout(height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_comp, use_container_width=True)
        
        cols = st.columns(min(len(snapshots), 3))
        for i, snap in enumerate(snapshots):
            with cols[i % 3]:
                overall_pct = round(snap["nailed"] / snap["totalGoals"] * 100) if snap["totalGoals"] else 0
                st.markdown(f"""
                <div class="snap-card">
                    <h4>📸 {snap['quarter']}</h4>
                    <p style="font-size:12px;color:#b0a898;">{snap['date'][:10]}</p>
                """, unsafe_allow_html=True)
                
                for sp in snap["pillars"]:
                    st.markdown(f"""
                    <div style="display:flex;align-items:center;gap:8px;margin:6px 0;font-size:13px;">
                        <span>{sp['emoji']}</span>
                        <span style="flex:1;">{sp['name']}</span>
                        <div style="width:60px;height:6px;background:#ede6da;border-radius:6px;overflow:hidden;">
                            <div style="height:100%;width:{sp['avgPct']}%;background:{sp['color']};border-radius:6px;"></div>
                        </div>
                        <strong style="min-width:35px;text-align:right;">{sp['avgPct']}%</strong>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown(f"""
                    <div style="text-align:center;margin-top:12px;padding-top:12px;border-top:1px solid #ede6da;">
                        <div style="font-size:28px;font-weight:800;color:#e8793a;">{overall_pct}%</div>
                        <p style="font-size:12px;color:#b0a898;">{snap['nailed']}/{snap['totalGoals']} nailed</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No snapshots yet — take one to freeze your current progress!")

# ==========================
# 🧩 MANDALA GRID
# ==========================
with tab_grid:
    st.markdown(f"### 🧩 {member['name']}'s 9×9 Roadmap Grid")
    st.caption("Ohtani-style Mandala chart. Edit goals in the Goals tab.")
    
    block_order = [(0,0),(0,3),(0,6),(3,0),(3,3),(3,6),(6,0),(6,3),(6,6)]
    pillar_block_idx = [0,1,2,3,5,6,7,8]
    surround = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    
    cells = [[None]*9 for _ in range(9)]
    
    # Center block
    cells[4][4] = {"type": "dream", "text": dreams.get("want", "My Dream")}
    for si, off in enumerate(surround):
        cells[4+off[0]][4+off[1]] = {"type": "pillar", "pi": si}
    
    # Pillar blocks
    for pi, bi in enumerate(pillar_block_idx):
        br, bc = block_order[bi]
        cells[br+1][bc+1] = {"type": "pillar", "pi": pi}
        for si, off in enumerate(surround):
            sub = member["pillars"][pi]["subs"][si]
            cells[br+1+off[0]][bc+1+off[1]] = {"type": "sub", "pi": pi, "si": si, "text": sub.get("text", ""), "done": sub.get("done", False)}
    
    colors_bg = ["#fde5ea","#e4effa","#fce8f2","#e0f5f4","#fff0e4","#fdf5e0","#e6f5e6","#f0e8fa"]
    colors_fg = ["#e85d75","#4a90d9","#e07baa","#3aafa9","#e8793a","#e0aa3e","#5cb85c","#9b72cf"]
    
    # Render as HTML table
    html = '<table style="width:100%;border-collapse:separate;border-spacing:3px;">'
    for r in range(9):
        html += '<tr>'
        for c in range(9):
            cell = cells[r][c]
            if cell is None:
                html += '<td style="min-height:50px;"></td>'
            elif cell["type"] == "dream":
                html += f'<td class="mandala-cell" style="background:linear-gradient(135deg,#e8793a,#e0aa3e);color:#fff;font-weight:800;font-size:11px;">{cell["text"]}</td>'
            elif cell["type"] == "pillar":
                pi = cell["pi"]
                html += f'<td class="mandala-cell" style="background:{colors_fg[pi]};color:#fff;font-weight:700;font-size:10px;">{PILLARS[pi]["emoji"]} {PILLARS[pi]["name"]}</td>'
            elif cell["type"] == "sub":
                pi = cell["pi"]
                txt = cell.get("text", "") or "·"
                opacity = "0.45" if cell.get("done") else "0.85"
                dec = "line-through" if cell.get("done") else "none"
                html += f'<td class="mandala-cell" style="background:{colors_bg[pi]};opacity:{opacity};text-decoration:{dec};font-size:9px;">{txt}</td>'
        html += '</tr>'
    html += '</table>'
    st.markdown(html, unsafe_allow_html=True)
    
    # Edit pillars
    st.divider()
    st.markdown("### ✏️ Edit Grid Actions")
    edit_pillar = st.selectbox("Select pillar to edit", range(8), 
                               format_func=lambda i: f"{PILLARS[i]['emoji']} {PILLARS[i]['name']}")
    
    pillar = member["pillars"][edit_pillar]
    changed = False
    for si in range(8):
        col1, col2 = st.columns([5, 1])
        with col1:
            new_text = st.text_input(f"Action {si+1}", value=pillar["subs"][si].get("text", ""), key=f"grid_{edit_pillar}_{si}")
        with col2:
            new_done = st.checkbox("Done", value=pillar["subs"][si].get("done", False), key=f"grid_done_{edit_pillar}_{si}")
        
        if new_text != pillar["subs"][si].get("text", "") or new_done != pillar["subs"][si].get("done", False):
            pillar["subs"][si]["text"] = new_text
            pillar["subs"][si]["done"] = new_done
            changed = True
    
    if changed:
        save_data()

# ==========================
# 💬 GROWTH CHAT
# ==========================
with tab_chat:
    st.markdown(f"### 💬 {member['name']}'s Monthly Growth Chat")
    st.caption("20 minutes. No fixing. No overcoaching. Just reflection.")
    
    questions = [
        f"Hey {member['name']}! 👋 Let's do our growth chat.",
        "What felt **hard** this month? Something you struggled with.",
        "What felt **easy**? Something that came naturally.",
        "What are you most **proud** of?",
        "What do you want to **try next** month?",
        "🎉 Great chat! Remember — it's not about being perfect. It's about getting **1% better**."
    ]
    
    if "chat_step" not in st.session_state:
        st.session_state.chat_step = 0
    
    for i in range(st.session_state.chat_step + 1):
        if i < len(questions):
            st.markdown(f"""
            <div style="background:white;border:1px solid #ede6da;border-radius:18px;border-bottom-left-radius:4px;
                        padding:14px 18px;max-width:80%;margin-bottom:12px;box-shadow:0 1px 3px rgba(45,42,38,0.06);">
                {questions[i]}
            </div>
            """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.session_state.chat_step < len(questions) - 1:
            if st.button("Next Question →", type="primary"):
                st.session_state.chat_step += 1
                st.rerun()
    with col2:
        if st.button("Start Over"):
            st.session_state.chat_step = 0
            st.rerun()
    
    st.divider()
    st.markdown("""
    **Dad Mode — Monthly Prompts:**
    - What felt hard?
    - What felt easy?
    - What are you proud of?
    - What do you want to try next?

    *No fixing. No overcoaching. Just reflection.*
    """)

# ==========================
# 🏈 NFL DRAFT ROUND 2
# ==========================
with tab_nfl:
    # Position → display color mapping
    POS_COLORS = {
        "QB": "#e85d75",
        "RB": "#4a90d9", "FB": "#4a90d9",
        "WR": "#5cb85c", "TE": "#e07baa",
        "OT": "#e0aa3e", "OG": "#e0aa3e", "C": "#e0aa3e", "OL": "#e0aa3e",
        "DE": "#9b72cf", "DT": "#9b72cf", "NT": "#9b72cf", "DL": "#9b72cf",
        "LB": "#3aafa9", "ILB": "#3aafa9", "OLB": "#3aafa9", "MLB": "#3aafa9",
        "CB": "#e8793a", "S": "#e8793a", "FS": "#e8793a", "SS": "#e8793a", "DB": "#e8793a",
        "K": "#b0a898", "P": "#b0a898", "LS": "#b0a898",
        "EDGE": "#9b72cf", "DL/DE": "#9b72cf",
    }

    @st.cache_data(ttl=45)
    def fetch_round2_picks():
        endpoints = [
            "https://site.api.espn.com/apis/site/v2/sports/football/nfl/draft/picks?round=2&year=2026",
            "https://site.api.espn.com/apis/site/v2/sports/football/nfl/draft/summary?year=2026",
            "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2026/draft/rounds/2/picks?limit=100",
        ]
        headers = {"User-Agent": "Mozilla/5.0 (compatible; LifeDashboard/1.0)"}
        for url in endpoints:
            try:
                resp = requests.get(url, headers=headers, timeout=10)
                if resp.status_code == 200:
                    return resp.json(), url
            except Exception:
                continue
        return None, None

    def parse_picks(data, source_url):
        if not data:
            return []
        picks = []
        # Shape 1: {"picks": [...]}
        raw = data.get("picks", [])
        # Shape 2: {"rounds": [{"picks": [...]}, ...]}
        if not raw and data.get("rounds"):
            for rnd in data["rounds"]:
                if rnd.get("round") == 2 or rnd.get("number") == 2:
                    raw = rnd.get("picks", [])
                    break
            if not raw and len(data["rounds"]) >= 2:
                raw = data["rounds"][1].get("picks", [])
        # Shape 3: {"items": [...]} from core API
        if not raw and data.get("items"):
            raw = data["items"]
        for p in raw:
            # Normalise round filter: keep only round 2 picks (or all if pre-filtered)
            rnd_num = p.get("round") or p.get("roundNumber", 0)
            if rnd_num and rnd_num != 2:
                continue
            team = p.get("team") or p.get("franchise") or {}
            athlete = p.get("athlete") or p.get("player") or None
            picks.append({
                "overall": p.get("overallPick") or p.get("overall", 0),
                "round_pick": p.get("roundPick") or p.get("pickInRound", 0),
                "team_name": team.get("displayName") or team.get("name", "Unknown"),
                "team_abbr": team.get("abbreviation", ""),
                "team_color": team.get("color") or team.get("alternateColor", "013369"),
                "player_name": athlete.get("displayName") or athlete.get("fullName", "") if athlete else None,
                "player_short": athlete.get("shortName", "") if athlete else None,
                "position": (athlete.get("position") or {}).get("abbreviation", "?") if athlete else None,
                "college": ((athlete.get("college") or {}).get("displayName", "")
                            or (athlete.get("college") or "")) if athlete else None,
                "headshot": ((athlete.get("headshot") or {}).get("href", "")) if athlete else None,
            })
        return picks

    # ---- Header ----
    st.markdown("""
    <div class="nfl-header">
        <h2 style="margin:0;color:white;font-size:26px;">🏈 2026 NFL Draft — Round 2 Live</h2>
        <p style="margin:6px 0 0;opacity:0.85;font-size:14px;">Picks #33 through #64 · April 25, 2026 · Kansas City, MO</p>
    </div>
    """, unsafe_allow_html=True)

    # ---- Controls ----
    ctrl1, ctrl2, ctrl3 = st.columns([3, 1, 1])
    with ctrl1:
        auto_refresh = st.toggle("🔄 Auto-Refresh", value=False, key="nfl_auto")
    with ctrl2:
        refresh_sec = st.selectbox("Interval", [30, 60, 120],
                                   format_func=lambda x: f"{x}s", key="nfl_interval")
    with ctrl3:
        if st.button("🔄 Refresh Now", use_container_width=True, key="nfl_refresh_btn"):
            st.cache_data.clear()
            st.rerun()

    st.caption(f"Last refreshed: {datetime.datetime.now().strftime('%I:%M:%S %p ET')}")

    # ---- Fetch & Parse ----
    raw_data, source = fetch_round2_picks()
    picks = parse_picks(raw_data, source)

    completed = [p for p in picks if p["player_name"]]
    pending   = [p for p in picks if not p["player_name"]]
    total     = len(picks)

    # ---- Draft Status Banner ----
    if not picks:
        st.markdown("""
        <div style="background:white;border-radius:14px;padding:48px 32px;text-align:center;
                    box-shadow:0 2px 12px rgba(0,0,0,0.06);border:2px dashed #ede6da;">
            <div style="font-size:52px;margin-bottom:14px;">🏈</div>
            <h3 style="color:#013369;">Round 2 Hasn't Started Yet</h3>
            <p style="color:#7a7267;max-width:480px;margin:0 auto;">
                Pick data will stream in as selections are made. Hit <strong>Refresh Now</strong>
                or enable Auto-Refresh to keep this board live.
            </p>
        </div>
        """, unsafe_allow_html=True)

    elif not pending:
        st.markdown(f"""
        <div class="draft-complete-banner">
            <div style="font-size:40px;margin-bottom:8px;">🎉</div>
            <h3 style="margin:0;color:white;">Round 2 Complete!</h3>
            <p style="margin:6px 0 0;opacity:0.85;">All {total} picks have been made.</p>
        </div>
        """, unsafe_allow_html=True)

    else:
        # On the clock
        on_clock = pending[0]
        tc = on_clock["team_color"].lstrip("#") if on_clock["team_color"] else "013369"
        st.markdown(f"""
        <div class="clock-card">
            <div style="font-size:11px;letter-spacing:1.5px;text-transform:uppercase;opacity:0.7;margin-bottom:6px;">
                ⏰ On the Clock
            </div>
            <div style="font-size:30px;font-weight:800;line-height:1.1;">
                {on_clock["team_name"]}
            </div>
            <div style="font-size:14px;opacity:0.85;margin-top:6px;">
                Pick <strong>#{on_clock["overall"]}</strong> overall &nbsp;·&nbsp;
                #{on_clock["round_pick"]} in Round 2
            </div>
            <div style="margin-top:12px;font-size:12px;opacity:0.6;">
                {len(completed)} of {total} picks made
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ---- Progress Bar ----
    if total > 0:
        pct_done = len(completed) / total
        st.progress(pct_done, text=f"Round 2: {len(completed)}/{total} picks complete")

    # ---- Position Breakdown Chart ----
    if completed:
        pos_counts: dict[str, int] = {}
        for p in completed:
            pos = p["position"] or "?"
            pos_counts[pos] = pos_counts.get(pos, 0) + 1

        pos_sorted = sorted(pos_counts.items(), key=lambda x: -x[1])
        pos_labels = [x[0] for x in pos_sorted]
        pos_vals   = [x[1] for x in pos_sorted]
        pos_clrs   = [POS_COLORS.get(lbl, "#b0a898") for lbl in pos_labels]

        fig_pos = go.Figure(go.Bar(
            x=pos_labels, y=pos_vals,
            marker_color=pos_clrs,
            text=pos_vals, textposition="outside",
        ))
        fig_pos.update_layout(
            title=f"Round 2 Picks by Position ({len(completed)} made)",
            height=220,
            margin=dict(t=40, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(showgrid=False, showticklabels=False),
            xaxis=dict(tickfont=dict(size=12, color="#013369")),
            font=dict(color="#2d2a26"),
        )
        st.plotly_chart(fig_pos, use_container_width=True)

    # ---- Completed Picks Board ----
    if completed:
        st.markdown(f"### ✅ Completed Picks — {len(completed)} made")

        col_a, col_b = st.columns(2)
        for idx, pick in enumerate(sorted(completed, key=lambda x: x["overall"] or 0)):
            pos       = pick["position"] or "?"
            pos_color = POS_COLORS.get(pos, "#b0a898")
            college   = pick["college"] or ""
            abbr      = pick["team_abbr"] or ""

            card_html = f"""
            <div class="pick-row" style="border-left-color:{pos_color};">
                <span class="pick-number">#{pick['overall']}</span>
                <div style="flex:1;min-width:0;">
                    <div style="font-weight:700;font-size:14px;white-space:nowrap;overflow:hidden;
                                text-overflow:ellipsis;">{pick['player_name']}</div>
                    <div style="font-size:11px;color:#7a7267;margin-top:2px;">
                        {abbr} &nbsp;·&nbsp; {college}
                    </div>
                </div>
                <span class="pos-badge" style="background:{pos_color};">{pos}</span>
            </div>
            """
            if idx % 2 == 0:
                col_a.markdown(card_html, unsafe_allow_html=True)
            else:
                col_b.markdown(card_html, unsafe_allow_html=True)

    # ---- Upcoming Picks ----
    if pending:
        st.markdown(f"### 🕐 Coming Up — {len(pending)} picks remaining")
        up_cols = st.columns(4)
        for i, pick in enumerate(pending[:8]):
            is_next = (i == 0)
            card_cls = "upcoming-card on-clock" if is_next else "upcoming-card"
            label    = "⏰ ON THE CLOCK" if is_next else f"Pick #{pick['round_pick']} R2"
            with up_cols[i % 4]:
                st.markdown(f"""
                <div class="{card_cls}">
                    <div style="font-size:10px;color:#7a7267;letter-spacing:0.5px;
                                font-weight:600;text-transform:uppercase;">{label}</div>
                    <div style="font-size:22px;font-weight:800;color:#013369;
                                margin:4px 0;">#{pick['overall']}</div>
                    <div style="font-size:12px;font-weight:600;color:#2d2a26;
                                line-height:1.3;">{pick['team_name']}</div>
                    <div style="font-size:10px;color:#b0a898;margin-top:2px;">
                        {pick['team_abbr']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ---- Auto-refresh (runs after full render) ----
    if auto_refresh and picks is not None:
        countdown_slot = st.empty()
        for remaining in range(refresh_sec, 0, -1):
            countdown_slot.caption(f"⏳ Auto-refreshing in {remaining}s…")
            time.sleep(1)
        st.cache_data.clear()
        st.rerun()
