import streamlit as st
from agents import build_search_agent, build_reader_agent, writer_chain, critic_chain

st.set_page_config(
    page_title="YourResearch - AI Research Assistant",
    page_icon="⚡",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Archivo+Black&family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background-color: #0b0b0d;
        color: #f2f2f2;
    }

    /* Hide default streamlit chrome */
    #MainMenu, footer, header {visibility: hidden;}

    .eyebrow {
        color: #ff7a1a;
        letter-spacing: 6px;
        font-size: 13px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 6px;
    }

    .hero-title {
        font-family: 'Archivo Black', sans-serif;
        font-size: 76px;
        text-align: center;
        line-height: 1.0;
        margin: 0;
        letter-spacing: -1px;
    }
    .hero-title .white { color: #f5f2ea; }
    .hero-title .orange { color: #ff7a1a; }

    .hero-sub {
        text-align: center;
        color: #9a9a9f;
        font-size: 17px;
        max-width: 640px;
        margin: 18px auto 40px auto;
        line-height: 1.5;
    }

    .panel {
        background: #151517;
        border: 1px solid #26262a;
        border-radius: 14px;
        padding: 26px 26px;
    }

    .section-label {
        color: #ff7a1a;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 2px;
        margin-bottom: 10px;
    }

    .pipeline-title {
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 18px;
    }

    .step-card {
        background: #1a1a1d;
        border: 1px solid #29292d;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 12px;
    }
    .step-card.running { border-color: #ff7a1a; box-shadow: 0 0 0 1px #ff7a1a33; }
    .step-card.done { border-color: #2fbf71; }

    .step-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .step-name {
        font-weight: 700;
        font-size: 15px;
    }
    .step-num {
        color: #ff7a1a;
        font-weight: 700;
        margin-right: 8px;
        font-size: 13px;
    }
    .step-desc {
        color: #8a8a8f;
        font-size: 13px;
        margin-top: 4px;
    }
    .badge {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1px;
        padding: 3px 10px;
        border-radius: 20px;
    }
    .badge.waiting { background: #26262a; color: #8a8a8f; }
    .badge.running { background: #ff7a1a22; color: #ff7a1a; }
    .badge.done { background: #2fbf7122; color: #2fbf71; }

    div.stButton > button {
        background: linear-gradient(90deg, #ff7a1a, #ff9a4d);
        color: #0b0b0d;
        font-weight: 700;
        border: none;
        border-radius: 10px;
        padding: 14px 0;
        font-size: 16px;
        width: 100%;
    }
    div.stButton > button:hover {
        background: linear-gradient(90deg, #ff8a30, #ffab61);
        color: #0b0b0d;
    }

    .stTextInput > div > div > input {
        background: #1a1a1d;
        border: 1px solid #29292d;
        color: #f2f2f2;
        border-radius: 10px;
        padding: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------
st.markdown('<div class="eyebrow">MULTI-AGENT AI SYSTEM</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-title"><span class="white">Your</span><span class="orange">Research</span></div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="hero-sub">Four specialized AI agents collaborate — searching, scraping, '
    'writing, and critiquing — to deliver a polished research report on any topic.</div>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Pipeline step definitions
# ---------------------------------------------------------------------------
STEPS = [
    {"key": "search", "num": "01", "name": "Search Agent", "desc": "Gathers recent web information"},
    {"key": "reader", "num": "02", "name": "Reader Agent", "desc": "Scrapes & extracts deep content"},
    {"key": "writer", "num": "03", "name": "Writer Chain", "desc": "Drafts the research report"},
    {"key": "critic", "num": "04", "name": "Critic Chain", "desc": "Reviews & gives feedback"},
]

if "status" not in st.session_state:
    st.session_state.status = {s["key"]: "waiting" for s in STEPS}
if "result" not in st.session_state:
    st.session_state.result = None
if "topic" not in st.session_state:
    st.session_state.topic = ""


def render_step_card(step, status):
    label = {"waiting": "WAITING", "running": "RUNNING", "done": "DONE"}[status]
    return f"""
    <div class="step-card {status}">
        <div class="step-top">
            <div class="step-name"><span class="step-num">{step['num']}</span>{step['name']}</div>
            <div class="badge {status}">{label}</div>
        </div>
        <div class="step-desc">{step['desc']}</div>
    </div>
    """


# ---------------------------------------------------------------------------
# Layout: left = input/results, right = pipeline status
# ---------------------------------------------------------------------------
left, right = st.columns([1.3, 1], gap="large")

with right:
    st.markdown('<div class="pipeline-title">Pipeline</div>', unsafe_allow_html=True)
    placeholders = {}
    for step in STEPS:
        placeholders[step["key"]] = st.empty()
        placeholders[step["key"]].markdown(
            render_step_card(step, st.session_state.status[step["key"]]), unsafe_allow_html=True
        )

with left:
    st.markdown('<div class="section-label">RESEARCH TOPIC</div>', unsafe_allow_html=True)
    topic = st.text_input(
        "Research topic",
        placeholder="e.g. Quantum computing breakthroughs in 2025",
        label_visibility="collapsed",
    )
    run_clicked = st.button("⚡ Run Research Pipeline", disabled=not topic.strip())


def update_step(key, status):
    st.session_state.status[key] = status
    placeholders[key].markdown(render_step_card(next(s for s in STEPS if s["key"] == key), status), unsafe_allow_html=True)


if run_clicked and topic.strip():
    for s in STEPS:
        st.session_state.status[s["key"]] = "waiting"
    st.session_state.result = None

    try:
        state = {}

        # Step 1 - Search
        update_step("search", "running")
        search_agent = build_search_agent()
        search_results = search_agent.invoke(
            {"messages": [("user", f"Find recent and reliable and detailed information about: {topic}")]}
        )
        state["search_results"] = search_results["messages"][-1].content
        update_step("search", "done")

        # Step 2 - Reader
        update_step("reader", "running")
        reader_agent = build_reader_agent()
        reader_result = reader_agent.invoke(
            {
                "messages": [
                    (
                        "user",
                        f"Based on the following search results about '{topic}', "
                        f"pick the most relevant URL and scrape it for deeper content.\n\n"
                        f"Search Results:\n{state['search_results'][:800]}",
                    )
                ]
            }
        )
        state["scraped_content"] = reader_result["messages"][-1].content
        update_step("reader", "done")

        # Step 3 - Writer
        update_step("writer", "running")
        research_combined = (
            f"SEARCH RESULTS : \n {state['search_results']} \n\n"
            f"DETAILED SCRAPED CONTENT : \n {state['scraped_content']}"
        )
        state["report"] = writer_chain.invoke({"topic": topic, "research": research_combined})
        update_step("writer", "done")

        # Step 4 - Critic
        update_step("critic", "running")
        state["feedback"] = critic_chain.invoke({"report": state["report"]})
        update_step("critic", "done")

        st.session_state.result = state
        st.session_state.topic = topic.strip()

    except Exception as e:
        st.error(f"Pipeline failed: {e}")

# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------
if st.session_state.result:
    result = st.session_state.result
    st.markdown("---")
    st.success(f"Research complete for: **{st.session_state.topic}**")

    tab_report, tab_feedback, tab_search, tab_scraped = st.tabs(
        ["📄 Final Report", "🧐 Critic Feedback", "🔍 Search Results", "📰 Scraped Content"]
    )

    with tab_report:
        st.markdown(result.get("report", "_No report generated._"))
        st.download_button(
            "⬇️ Download report as .md",
            data=str(result.get("report", "")),
            file_name=f"{st.session_state.topic.replace(' ', '_')}_report.md",
            mime="text/markdown",
        )

    with tab_feedback:
        st.markdown(result.get("feedback", "_No feedback generated._"))

    with tab_search:
        st.text(result.get("search_results", "No search results."))

    with tab_scraped:
        st.text(result.get("scraped_content", "No scraped content."))