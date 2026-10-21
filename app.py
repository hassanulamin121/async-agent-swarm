"""
HaxSwarm Studio - Streamlit frontend for the FastAPI multi-agent script generator.

Run:
    pip install streamlit requests
    streamlit run app.py
"""

import json
import math
import re
import threading
import time
from urllib.parse import urlparse

import requests
import streamlit as st
import streamlit.components.v1 as components

# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
DEFAULT_API_URL = "http://127.0.0.1:8000/api/v1/generate-script"
REQUEST_TIMEOUT = 180  # seconds
PAYLOAD_KEY = "topic"  # JSON key your FastAPI endpoint expects
NARRATION_WPM = 140  # used for the estimated runtime metric

EXAMPLE_TOPICS = [
    "The Microwave Mindset and Gen-Z Digital Solitude",
    "Last Train Through a Sleeping City",
    "What the Algorithm Remembers About You",
]

# (icon, agent, message, starts after N seconds)
STAGES = [
    ("🔍", "Researcher", "Gathering data...", 0),
    ("✍️", "Writer", "Drafting script...", 8),
    ("🧐", "Reviewer", "Polishing cut...", 20),
]

st.set_page_config(
    page_title="HaxSwarm Studio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------------------- #
# Styling
# --------------------------------------------------------------------------- #
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root {
  --bg: #07060f;
  --panel: rgba(18, 16, 36, 0.72);
  --panel-solid: #100e22;
  --line: rgba(139, 92, 246, 0.28);
  --cyan: #22d3ee;
  --violet: #a855f7;
  --pink: #f472b6;
  --text: #e8e6f5;
  --muted: #8b88a8;
}

html, body, [class*="css"], .stApp {
  font-family: 'Space Grotesk', system-ui, sans-serif;
  color: var(--text);
}

.stApp {
  background:
    radial-gradient(900px 500px at 12% -10%, rgba(168, 85, 247, 0.20), transparent 60%),
    radial-gradient(800px 480px at 95% 0%, rgba(34, 211, 238, 0.14), transparent 60%),
    linear-gradient(rgba(255,255,255,0.025) 1px, transparent 1px) 0 0 / 44px 44px,
    linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px) 0 0 / 44px 44px,
    var(--bg);
}

#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 2.2rem; max-width: 1080px; }

/* ---------- Hero ---------- */
.hero-title {
  font-size: clamp(2.2rem, 5vw, 3.6rem);
  font-weight: 700;
  letter-spacing: -0.03em;
  line-height: 1.05;
  margin: 0;
  background: linear-gradient(95deg, var(--cyan) 0%, var(--violet) 55%, var(--pink) 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  filter: drop-shadow(0 0 18px rgba(168, 85, 247, 0.45));
}
.hero-sub {
  color: var(--muted);
  font-size: 1.05rem;
  margin: 0.6rem 0 1.6rem 0;
  max-width: 640px;
}

/* ---------- Inputs ---------- */
div[data-testid="stForm"] {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 18px;
  padding: 1.3rem 1.3rem 1.1rem 1.3rem;
  backdrop-filter: blur(10px);
  box-shadow: 0 0 0 1px rgba(34,211,238,0.04), 0 18px 60px -20px rgba(168,85,247,0.35);
}
.stTextInput input {
  background: rgba(7, 6, 15, 0.85) !important;
  border: 1px solid var(--line) !important;
  border-radius: 12px !important;
  color: var(--text) !important;
  font-size: 1.05rem !important;
  padding: 0.85rem 1rem !important;
  transition: border-color .2s, box-shadow .2s;
}
.stTextInput input:focus {
  border-color: var(--cyan) !important;
  box-shadow: 0 0 0 3px rgba(34, 211, 238, 0.18), 0 0 24px rgba(34, 211, 238, 0.25) !important;
}
.stTextInput label p { color: var(--muted) !important; font-size: .9rem; }

/* ---------- Buttons ---------- */
.stButton > button, .stDownloadButton > button, div[data-testid="stFormSubmitButton"] > button {
  border-radius: 12px;
  border: 1px solid var(--line);
  background: rgba(24, 21, 48, 0.9);
  color: var(--text);
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 600;
  transition: transform .15s ease, box-shadow .2s ease, border-color .2s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover {
  border-color: var(--cyan);
  box-shadow: 0 0 18px rgba(34, 211, 238, 0.35);
  color: #fff;
  transform: translateY(-1px);
}
div[data-testid="stFormSubmitButton"] > button {
  background: linear-gradient(95deg, #0ea5c6, #7c3aed);
  border: none;
  color: #fff;
  height: 3rem;
  box-shadow: 0 0 22px rgba(124, 58, 237, 0.55);
}
div[data-testid="stFormSubmitButton"] > button:hover {
  box-shadow: 0 0 34px rgba(34, 211, 238, 0.65);
  transform: translateY(-1px);
}

/* ---------- Agent tracker ---------- */
.tracker {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 18px;
  padding: 1.4rem 1.4rem 1.2rem 1.4rem;
  box-shadow: 0 0 40px -10px rgba(34, 211, 238, 0.25);
}
.tracker-head {
  display: flex; justify-content: space-between; align-items: baseline;
  margin-bottom: 1rem;
}
.tracker-title { font-weight: 600; font-size: 1.05rem; }
.tracker-timer { font-family: 'JetBrains Mono', monospace; color: var(--cyan); }
.steps { display: grid; grid-template-columns: repeat(3, 1fr); gap: .8rem; }
.step {
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 14px;
  padding: .9rem 1rem;
  background: rgba(7, 6, 15, 0.55);
  opacity: .45;
  transition: all .3s ease;
}
.step .ico { font-size: 1.4rem; }
.step .who { font-weight: 600; margin-top: .25rem; }
.step .msg { color: var(--muted); font-size: .85rem; font-family: 'JetBrains Mono', monospace; }
.step.done { opacity: 1; border-color: rgba(34, 211, 238, 0.45); }
.step.done .msg { color: var(--cyan); }
.step.active {
  opacity: 1;
  border-color: var(--violet);
  animation: pulse 1.4s ease-in-out infinite;
}
.step.active .msg { color: var(--text); }
@keyframes pulse {
  0%, 100% { box-shadow: 0 0 6px rgba(168, 85, 247, 0.35); }
  50%      { box-shadow: 0 0 26px rgba(168, 85, 247, 0.85); }
}
.bar {
  margin-top: 1.1rem; height: 6px; border-radius: 99px;
  background: rgba(255,255,255,0.06); overflow: hidden;
}
.bar > div {
  height: 100%; border-radius: 99px;
  background: linear-gradient(90deg, var(--cyan), var(--violet), var(--pink));
  box-shadow: 0 0 14px rgba(34, 211, 238, 0.8);
  transition: width .3s ease;
}
@media (max-width: 700px) { .steps { grid-template-columns: 1fr; } }
@media (prefers-reduced-motion: reduce) { .step.active { animation: none; } }

/* ---------- Metrics ---------- */
.metrics { display: grid; grid-template-columns: repeat(4, 1fr); gap: .8rem; margin: 1.2rem 0 1rem 0; }
.metric {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: .9rem 1rem;
}
.metric .v {
  font-family: 'JetBrains Mono', monospace; font-size: 1.5rem; font-weight: 700;
  color: var(--cyan); text-shadow: 0 0 14px rgba(34, 211, 238, 0.55);
}
.metric .k { color: var(--muted); font-size: .85rem; }
@media (max-width: 700px) { .metrics { grid-template-columns: repeat(2, 1fr); } }

/* ---------- Script container ---------- */
.st-key-script-box {
  background: linear-gradient(180deg, rgba(16, 14, 34, 0.95), rgba(10, 9, 22, 0.95));
  border: 1px solid var(--line);
  border-left: 3px solid var(--cyan);
  border-radius: 16px;
  padding: 1.6rem 1.8rem;
  box-shadow: 0 0 50px -18px rgba(34, 211, 238, 0.45);
  font-family: 'JetBrains Mono', monospace;
  line-height: 1.75;
}
.st-key-script-box p, .st-key-script-box li, .st-key-script-box h1,
.st-key-script-box h2, .st-key-script-box h3 { font-family: 'JetBrains Mono', monospace; }
.st-key-script-box h1, .st-key-script-box h2, .st-key-script-box h3 { color: var(--cyan); }
.st-key-script-box p, .st-key-script-box li { font-size: .95rem; max-width: 78ch; }
.st-key-script-box strong { color: var(--pink); }

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0b0919, #08071280);
  border-right: 1px solid var(--line);
}
.side-brand { font-size: 1.35rem; font-weight: 700; letter-spacing: -0.02em; }
.side-brand span { color: var(--cyan); text-shadow: 0 0 14px rgba(34,211,238,.7); }
.status {
  display: flex; align-items: center; gap: .6rem;
  padding: .7rem .9rem; border-radius: 12px;
  background: var(--panel); border: 1px solid var(--line);
  font-size: .92rem; margin: .8rem 0 1.2rem 0;
}
.dot { width: 10px; height: 10px; border-radius: 50%; flex: none; }
.dot.on  { background: #22c55e; box-shadow: 0 0 10px #22c55e; }
.dot.off { background: #ef4444; box-shadow: 0 0 10px #ef4444; }
.side-h { font-weight: 600; margin: 1rem 0 .5rem 0; font-size: .95rem; }
.pipe { display: flex; flex-direction: column; gap: 0; }
.pipe .node {
  border: 1px solid var(--line); border-radius: 10px;
  padding: .5rem .75rem; background: rgba(7,6,15,.6); font-size: .9rem;
}
.pipe .arrow { text-align: center; color: var(--violet); line-height: 1.3; }
.side-note { color: var(--muted); font-size: .85rem; line-height: 1.55; }
.side-note code { color: var(--cyan); background: transparent; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
@st.cache_data(ttl=8, show_spinner=False)
def backend_online(api_url: str) -> bool:
    """Cheap reachability check. Any non-5xx HTTP answer means the server is up."""
    parts = urlparse(api_url)
    base = f"{parts.scheme}://{parts.netloc}"
    try:
        r = requests.get(f"{base}/openapi.json", timeout=1.5)
        return r.status_code < 500
    except requests.RequestException:
        return False


def extract_script(data) -> str:
    """Pull the script text out of whatever JSON shape the backend returns."""
    if isinstance(data, str):
        return data
    if isinstance(data, dict):
        for key in ("script", "final_script", "final", "result", "content", "output", "text"):
            val = data.get(key)
            if isinstance(val, str) and val.strip():
                return val
            if isinstance(val, dict):
                nested = extract_script(val)
                if nested:
                    return nested
        return json.dumps(data, indent=2, ensure_ascii=False)
    return json.dumps(data, indent=2, ensure_ascii=False)


def call_backend(api_url: str, topic: str, out: dict) -> None:
    """Runs in a worker thread so the UI can animate while waiting."""
    try:
        resp = requests.post(api_url, json={PAYLOAD_KEY: topic}, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        try:
            out["data"] = resp.json()
        except ValueError:
            out["data"] = resp.text
    except requests.HTTPError as exc:
        detail = ""
        try:
            detail = exc.response.json().get("detail", "")
        except Exception:
            detail = exc.response.text[:300] if exc.response is not None else ""
        out["error"] = ("http", exc.response.status_code if exc.response is not None else 0, str(detail))
    except requests.ConnectionError:
        out["error"] = ("offline", 0, "")
    except requests.Timeout:
        out["error"] = ("timeout", 0, "")
    except Exception as exc:  # noqa: BLE001
        out["error"] = ("unknown", 0, str(exc))


def render_tracker(elapsed: float, finished: bool = False) -> str:
    active = 0
    for i, (_, _, _, start) in enumerate(STAGES):
        if elapsed >= start:
            active = i
    pct = 100 if finished else 95 * (1 - math.exp(-elapsed / 18))

    cards = []
    for i, (icon, who, msg, _) in enumerate(STAGES):
        if finished or i < active:
            cls, text = "done", "Complete"
        elif i == active:
            cls, text = "active", msg
        else:
            cls, text = "", "Waiting..."
        cards.append(
            f'<div class="step {cls}"><div class="ico">{icon}</div>'
            f'<div class="who">{who}</div><div class="msg">{text}</div></div>'
        )

    title = "Swarm complete" if finished else "Agent swarm is working"
    return (
        '<div class="tracker">'
        f'<div class="tracker-head"><span class="tracker-title">{title}</span>'
        f'<span class="tracker-timer">{elapsed:0.1f}s</span></div>'
        f'<div class="steps">{"".join(cards)}</div>'
        f'<div class="bar"><div style="width:{pct:.1f}%"></div></div>'
        "</div>"
    )


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:48] or "script"


def fmt_runtime(words: int) -> str:
    secs = int(words / NARRATION_WPM * 60)
    return f"{secs // 60}:{secs % 60:02d}"


def copy_button(text: str) -> None:
    payload = json.dumps(text).replace("</", "<\\/")
    components.html(
        f"""
        <button id="copy" style="
          width:100%;height:40px;border-radius:12px;cursor:pointer;
          border:1px solid rgba(139,92,246,.4);background:rgba(24,21,48,.9);
          color:#e8e6f5;font:600 14px 'Space Grotesk',system-ui,sans-serif;
          transition:all .2s;">📋 Copy script</button>
        <script>
          const btn = document.getElementById('copy');
          const text = {payload};
          btn.onmouseenter = () => {{ btn.style.borderColor='#22d3ee'; btn.style.boxShadow='0 0 18px rgba(34,211,238,.35)'; }};
          btn.onmouseleave = () => {{ btn.style.borderColor='rgba(139,92,246,.4)'; btn.style.boxShadow='none'; }};
          async function doCopy() {{
            try {{ await navigator.clipboard.writeText(text); }}
            catch (e) {{
              const t = document.createElement('textarea');
              t.value = text; document.body.appendChild(t); t.select();
              document.execCommand('copy'); document.body.removeChild(t);
            }}
            btn.textContent = '✅ Copied';
            setTimeout(() => btn.textContent = '📋 Copy script', 1800);
          }}
          btn.addEventListener('click', doCopy);
        </script>
        """,
        height=44,
    )


def use_example(topic: str) -> None:
    st.session_state["topic_input"] = topic


# --------------------------------------------------------------------------- #
# Session state
# --------------------------------------------------------------------------- #
st.session_state.setdefault("topic_input", "")
st.session_state.setdefault("result", None)

# --------------------------------------------------------------------------- #
# Sidebar
# --------------------------------------------------------------------------- #
with st.sidebar:
    st.markdown('<div class="side-brand">Hax<span>Swarm</span> Studio</div>', unsafe_allow_html=True)

    with st.expander("Backend settings"):
        api_url = st.text_input("API endpoint", value=DEFAULT_API_URL, label_visibility="collapsed")
        if st.button("Re-check connection", use_container_width=True):
            backend_online.clear()

    online = backend_online(api_url)
    if online:
        st.markdown(
            '<div class="status"><span class="dot on"></span>🟢 Online - Gemini 3.8-Flash</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="status"><span class="dot off"></span>🔴 Offline - backend unreachable</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="side-h">Architecture</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="pipe">'
        '<div class="node">🔍 Researcher</div><div class="arrow">↓</div>'
        '<div class="node">✍️ Writer</div><div class="arrow">↓</div>'
        '<div class="node">🧐 Reviewer</div>'
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="side-h">Developer</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="side-note">Built by <b>Hassan</b><br>'
        "FastAPI (async) · Gemini 3.8-Flash · Streamlit<br>"
        "Endpoint: <code>/api/v1/generate-script</code></div>",
        unsafe_allow_html=True,
    )

# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
st.markdown('<h1 class="hero-title">HaxSwarm Studio</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-sub">Type a topic. Three AI agents research it, write the script, '
    "and edit the final cut.</p>",
    unsafe_allow_html=True,
)

with st.form("script_form", border=False):
    topic = st.text_input(
        "Script topic",
        key="topic_input",
        placeholder="e.g. The Microwave Mindset and Gen-Z Digital Solitude",
    )
    submitted = st.form_submit_button("⚡ Generate script", use_container_width=True)

chip_cols = st.columns(len(EXAMPLE_TOPICS))
for col, example in zip(chip_cols, EXAMPLE_TOPICS):
    col.button(example, key=f"ex_{slugify(example)}", on_click=use_example, args=(example,), use_container_width=True)

tracker_slot = st.empty()

# ----- Generate ----- #
if submitted:
    clean_topic = topic.strip()
    if not clean_topic:
        st.toast("Enter a topic first.", icon="⚠️")
        st.warning("Enter a topic to generate a script.")
    else:
        st.session_state["result"] = None
        out: dict = {}
        worker = threading.Thread(target=call_backend, args=(api_url, clean_topic, out), daemon=True)
        started = time.time()
        worker.start()

        while worker.is_alive():
            tracker_slot.markdown(render_tracker(time.time() - started), unsafe_allow_html=True)
            time.sleep(0.25)
        worker.join()
        elapsed = time.time() - started

        if "error" in out:
            tracker_slot.empty()
            kind, code, detail = out["error"]
            backend_online.clear()
            if kind == "offline":
                st.toast("Backend is offline.", icon="🔌")
                st.error(
                    "Can't reach the backend. Start your FastAPI server and try again.\n\n"
                    f"Expected at `{api_url}`"
                )
            elif kind == "timeout":
                st.toast("The request timed out.", icon="⏱️")
                st.error(f"The swarm took longer than {REQUEST_TIMEOUT} seconds. Try a narrower topic.")
            elif kind == "http":
                st.toast(f"Backend returned an error ({code}).", icon="🚨")
                st.error(f"The backend returned HTTP {code}." + (f"\n\n`{detail}`" if detail else ""))
            else:
                st.toast("Something went wrong.", icon="🚨")
                st.error(f"Unexpected error: {detail}")
        else:
            tracker_slot.markdown(render_tracker(elapsed, finished=True), unsafe_allow_html=True)
            st.session_state["result"] = {
                "topic": clean_topic,
                "script": extract_script(out["data"]),
                "seconds": elapsed,
            }
            st.toast("Script ready.", icon="🎬")

# ----- Result ----- #
result = st.session_state.get("result")
if result:
    script = result["script"]
    words = len(script.split())

    st.markdown(
        '<div class="metrics">'
        f'<div class="metric"><div class="v">{result["seconds"]:.1f}s</div><div class="k">Generation time</div></div>'
        f'<div class="metric"><div class="v">{words:,}</div><div class="k">Words</div></div>'
        f'<div class="metric"><div class="v">{len(script):,}</div><div class="k">Characters</div></div>'
        f'<div class="metric"><div class="v">{fmt_runtime(words)}</div><div class="k">Est. narration length</div></div>'
        "</div>",
        unsafe_allow_html=True,
    )

    a, b, c = st.columns(3)
    with a:
        copy_button(script)
    slug = slugify(result["topic"])
    with b:
        st.download_button(
            "⬇️ Download .txt", script, file_name=f"{slug}.txt", mime="text/plain", use_container_width=True
        )
    with c:
        st.download_button(
            "⬇️ Download .md",
            f"# {result['topic']}\n\n{script}\n",
            file_name=f"{slug}.md",
            mime="text/markdown",
            use_container_width=True,
        )

    tab_read, tab_raw = st.tabs(["Script view", "Raw text"])
    with tab_read:
        with st.container(key="script-box"):
            st.markdown(script)
    with tab_raw:
        st.code(script, language="markdown", wrap_lines=True)