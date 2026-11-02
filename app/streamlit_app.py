## python -m streamlit run app/streamlit_app.py

"""BiasLens — Interactive Text Bias Detection Dashboard."""
import json
import sys
from pathlib import Path
import plotly.graph_objects as go
import streamlit as st
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from src.predict import analyze_text
st.set_page_config(
    page_title="BiasLens | See beyond the words",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)
BIAS = {
    "linguistic_bias": (
        "Linguistic Bias",
        "Linguistic",
        "#20B6A9",
        "Bias expressed through wording or framing.",
    ),
    "gender_bias": (
        "Gender Bias",
        "Gender",
        "#9878E6",
        "Gender-related stereotypes or assumptions.",
    ),
    "racial_bias": (
        "Racial Bias",
        "Racial",
        "#EFA261",
        "Race- or ethnicity-related stereotypes.",
    ),
    "context_bias": (
        "Text-Level / Context Bias",
        "Context",
        "#79A5EB",
        "Potential text-level bias patterns.",
    ),
}
SAMPLES = {
    "Neutral example": "The school published the examination timetable.",
    "Gender example": "Women are naturally less capable of leading engineering teams.",
    "Racial example": "People from that ethnic group should never be trusted.",
}
# -------------------- Styling --------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root { color-scheme: light; }
.stApp {
    background: #F8F9FE;
    color: #293650;
    font-family: 'DM Sans', sans-serif;
}
h1, h2, h3 {
    font-family: 'Manrope', sans-serif !important;
    letter-spacing: -.04em;
}
[data-testid="stHeader"] {
    background: transparent;
}
.block-container {
    max-width: 1210px;
    padding-top: 1.65rem;
    padding-bottom: 3rem;
}
/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(
        160deg, #F0EAFF, #F7F3FF 65%, #F8F9FE
    ) !important;
    border-right: 1px solid #DDD7EF !important;
    height: 100dvh !important;
}
[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    overflow-y: auto !important;
    max-height: 100dvh;
}
[data-testid="stSidebar"] :is(p, label, small),
[data-testid="stSidebar"] [role="radiogroup"] label p {
    color: #36415D !important;
    -webkit-text-fill-color: #36415D !important;
    opacity: 1 !important;
}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
    color: #71809E !important;
    -webkit-text-fill-color: #71809E !important;
}
[data-testid="stSidebar"] [role="radiogroup"] label {
    padding: 9px 11px !important;
    border-radius: 12px !important;
}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
    background: #E6DCFB !important;
    border: 1px solid #D7C8F5 !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] {
    background: #FFFFFFA8 !important;
    border: 1px solid #E1D9F2 !important;
    border-radius: 12px !important;
}
/* Inputs and buttons */
[data-testid="stTextArea"] textarea {
    background: #FFFFFF !important;
    color: #293650 !important;
    border: 1px solid #DCE3F0 !important;
    border-radius: 13px !important;
}
.stButton button,
[data-testid="stDownloadButton"] button {
    border-radius: 12px !important;
    border: 1px solid #DFE4F1 !important;
    background: #FFFFFF;
    color: #35415D;
}
.stButton button[kind="primary"],
[data-testid="stFormSubmitButton"] button[kind="primary"] {
    background: #876CD8 !important;
    color: #FFFFFF !important;
    border: none !important;
    font-weight: 700;
}
/* Dashboard text contrast */
[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] *,
[data-testid="stMetric"] label {
    color: #53627D !important;
    -webkit-text-fill-color: #53627D !important;
    opacity: 1 !important;
}
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] * {
    color: #293650 !important;
    -webkit-text-fill-color: #293650 !important;
    opacity: 1 !important;
}
[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #E3E2F2;
    border-radius: 14px;
    padding: 16px 20px;
}
.js-plotly-plot .xtick text,
.js-plotly-plot .ytick text {
    fill: #53627D !important;
}
/* Branding */
.bl-logo {
    font: 800 1.55rem 'Manrope', sans-serif;
    color: #27324D;
    letter-spacing: -.06em;
}
.bl-logo span,
.bl-hero h1 span {
    color: #876BD3;
}
.bl-hero {
    padding: 30px 35px;
    background: linear-gradient(
        115deg, #F0EBFF, #FAF8FF 60%, #EDF9F7
    );
    border: 1px solid #E7DFFC;
    border-radius: 21px;
    margin-bottom: 25px;
}
.bl-kicker {
    color: #856ED0;
    font-size: .69rem;
    font-weight: 800;
    letter-spacing: .15em;
    margin-bottom: 13px;
}
.bl-hero h1 {
    font: 800 clamp(1.95rem, 3.4vw, 3.1rem) 'Manrope', sans-serif;
    color: #283450;
    line-height: 1.18;
    letter-spacing: -.06em;
    margin: 0 0 12px;
}
.bl-hero p {
    color: #60708B;
    font-size: 1rem;
    line-height: 1.7;
    max-width: 760px;
    margin: 0;
}
.bl-section {
    font: 800 1.22rem 'Manrope', sans-serif;
    color: #2B3651;
    margin: 26px 0 6px;
}
.bl-sub {
    font-size: .88rem;
    color: #77849C;
    margin-bottom: 15px;
}
/* Pastel cards */
.bl-card {
    box-sizing: border-box;
    border: 1.5px solid #DBD4F4;
    border-radius: 17px;
    padding: 21px 22px;
    margin-bottom: 14px;
    min-height: 160px;
    box-shadow: 0 5px 19px rgba(53, 65, 107, .035);
}
.bl-card-kicker {
    font-size: .69rem;
    font-weight: 800;
    letter-spacing: .12em;
    margin-bottom: 11px;
}
.bl-card-title {
    font: 800 1.07rem 'Manrope', sans-serif;
    color: #293650;
    margin-bottom: 8px;
}
.bl-card-desc {
    font-size: .85rem;
    color: #66758F;
    line-height: 1.65;
}
/* Results */
.bl-summary {
    background: linear-gradient(105deg, #F3EEFF, #F1FAF9);
    border: 1px solid #E5DDF5;
    border-radius: 16px;
    padding: 21px 24px;
    margin: 14px 0;
}
.bl-summary strong {
    font: 800 1.2rem 'Manrope', sans-serif;
    color: #293650;
}
.bl-summary p {
    color: #63718A;
    font-size: .87rem;
    margin: 8px 0 0;
}
.bl-score {
    font: 800 1.9rem 'Manrope', sans-serif;
    color: #293650;
}
.bl-badge {
    border-radius: 20px;
    padding: 6px 10px;
    font-size: .68rem;
    font-weight: 800;
}
.bl-bar {
    height: 7px;
    background: #E9EDF5;
    border-radius: 8px;
    overflow: hidden;
    margin: 13px 0 9px;
}
@media (max-width: 720px) {
    .bl-hero { padding: 23px; }
}
</style>
""", unsafe_allow_html=True)
# -------------------- UI Helpers --------------------
def hero(kicker, heading, text):
    st.markdown(
        f'<div class="bl-hero">'
        f'<div class="bl-kicker">{kicker}</div>'
        f'<h1>{heading}</h1>'
        f'<p>{text}</p></div>',
        unsafe_allow_html=True,
    )
def section(title, subtitle=""):
    st.markdown(
        f'<div class="bl-section">{title}</div>'
        f'<div class="bl-sub">{subtitle}</div>',
        unsafe_allow_html=True,
    )
def card(label, title, description, color, extra="", height=160):
    st.markdown(
        f'<div class="bl-card" style="min-height:{height}px;'
        f'border-color:{color}88;'
        f'background:linear-gradient(120deg,{color}18,#FFFFFF 85%);">'
        f'<div class="bl-card-kicker" style="color:{color}">{label}</div>'
        f'<div class="bl-card-title">{title}</div>'
        f'<div class="bl-card-desc">{description}</div>'
        f'{extra}</div>',
        unsafe_allow_html=True,
    )
def set_sample(text):
    st.session_state.text_input = text
    st.session_state.analyzed_text = None
# -------------------- Visualization --------------------
def chart(result):
    keys = list(BIAS)
    values = [
        float(result["predictions"][key]["probability"])
        for key in keys
    ]
    fig = go.Figure(
        go.Bar(
            x=values,
            y=[BIAS[key][1] for key in keys],
            orientation="h",
            marker_color=[BIAS[key][2] for key in keys],
            text=[f"{value:.3f}" for value in values],
            textposition="outside",
            textfont=dict(
                color="#293650",
                size=13,
            ),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Model score: %{x:.4f}<extra></extra>"
            ),
        )
    )
    fig.add_vline(
        x=result["threshold"],
        line_dash="dash",
        line_color="#886FD5",
        line_width=2,
        annotation_text=f'Threshold {result["threshold"]:.2f}',
        annotation_font_color="#775CC4",
        annotation_font_size=12,
        annotation_position="top right",
    )
    fig.update_layout(
        height=335,
        margin=dict(l=15, r=45, t=45, b=45),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="DM Sans",
            color="#53627D",
            size=13,
        ),
        xaxis=dict(
            range=[0, 1.08],
            tickvals=[0, .25, .5, .75, 1],
            tickfont=dict(color="#53627D", size=12),
            title=dict(
                text="Positive-class model score",
                font=dict(color="#53627D", size=12),
            ),
            gridcolor="#E1E5F0",
            zeroline=False,
        ),
        yaxis=dict(
            autorange="reversed",
            showgrid=False,
            tickfont=dict(color="#36415D", size=13),
        ),
    )
    return fig
# -------------------- Text Analyzer --------------------
def analyzer():
    hero(
        "BIASLENS / TEXT ANALYZER",
        "See beyond <span>the words.</span>",
        "Check your English text for possible bias before you "
        "share, publish, or review it. Understand what stands "
        "out, all in one place.",
    )
    section(
        "01 / Text analyzer",
        "Write or paste a sentence, or choose an example to get started.",
    )
    for (name, sample), col in zip(SAMPLES.items(), st.columns(3)):
        with col:
            st.button(
                f"↗ {name}",
                on_click=set_sample,
                args=(sample,),
                use_container_width=True,
            )
    with st.form("analyze_form"):
        st.text_area(
            "Text to analyze",
            key="text_input",
            height=145,
            placeholder="Enter an English sentence or short passage...",
        )
        submitted = st.form_submit_button(
            "Analyze text  →",
            type="primary",
        )
    if submitted:
        st.session_state.analyzed_text = (
            st.session_state.text_input.strip() or None
        )
        if st.session_state.analyzed_text is None:
            st.warning("Please enter some text to analyze.")
    if not st.session_state.analyzed_text:
        st.caption(
            "Your analysis will appear here after you click Analyze text."
        )
        return
    try:
        with st.spinner("Analyzing your text..."):
            result = analyze_text(
                st.session_state.analyzed_text,
                threshold=float(st.session_state.threshold),
            )
    except Exception as exc:
        st.error(f"The analysis could not be completed: {exc}")
        return
    # Analysis summary
    section("02 / Analysis results")
    detected = result["detected_biases"]
    title = (
        f"{len(detected)} of 4 categories flagged"
        if detected else "No categories flagged"
    )
    detail = (
        "Potential signals: "
        + ", ".join(BIAS[key][1] for key in detected)
        + "."
        if detected
        else "No model score reached the selected threshold."
    )
    st.markdown(
        f'<div class="bl-summary">'
        f'<strong>{title}</strong>'
        f'<p>{detail}</p></div>',
        unsafe_allow_html=True,
    )
    a, b, c = st.columns(3)
    a.metric("Categories screened", "4")
    b.metric("Categories flagged", len(detected))
    c.metric("Decision threshold", f'{result["threshold"]:.2f}')
    # Interactive bias profile
    graph_col, text_col = st.columns([2, 1], gap="large")
    with graph_col:
        st.markdown("**Your bias profile**")
        st.plotly_chart(
            chart(result),
            use_container_width=True,
            config={"displayModeBar": False},
        )
    with text_col:
        st.markdown("**Reading your profile**")
        st.write(
            "The dashed line shows the selected decision threshold. "
            "Each bar represents a separate bias category."
        )
        st.markdown("**Your text**")
        st.code(
            result["text"],
            language=None,
            wrap_lines=True,
        )
    # Detailed results
    section(
        "03 / Detailed bias signals",
        "Explore each category separately.",
    )
    keys = list(BIAS)
    for pair in (keys[:2], keys[2:]):
        for key, col in zip(pair, st.columns(2)):
            with col:
                name, _, color, description = BIAS[key]
                item = result["predictions"][key]
                score = float(item["probability"])
                flagged = item["predicted_label"] == 1
                badge_color = "#B06C36" if flagged else "#138879"
                badge_bg = "#FFF0E1" if flagged else "#E5F7F2"
                extra = (
                    '<div style="display:flex;align-items:center;'
                    'justify-content:space-between;gap:8px;margin-top:20px">'
                    f'<span class="bl-score">{score:.4f}</span>'
                    f'<span class="bl-badge" '
                    f'style="color:{badge_color};background:{badge_bg}">'
                    f'{"FLAGGED" if flagged else "NOT FLAGGED"}'
                    '</span></div>'
                    '<div class="bl-bar">'
                    f'<div style="width:{score*100:.1f}%;height:100%;'
                    f'background:{color}"></div></div>'
                    '<div class="bl-card-desc">'
                    'Positive-class model score</div>'
                )
                card(
                    "BIAS SIGNAL",
                    name,
                    description,
                    color,
                    extra,
                    height=280,
                )
    with st.expander("Developer view · Full JSON response"):
        st.json(result)
        st.download_button(
            "Download JSON results",
            data=json.dumps(result, indent=2, ensure_ascii=False),
            file_name="biaslens_results.json",
            mime="application/json",
        )
# -------------------- Model Insights --------------------
def insights():
    hero(
        "MODEL INSIGHTS",
        "Behind <span>the lens.</span>",
        "Discover how BiasLens analyzes text and presents your results.",
    )
    section(
        "How BiasLens works",
        "Three simple steps, from your words to your results.",
    )
    steps = [
        (
            "STEP 01",
            "Enter text",
            "Write or paste an English sentence or passage.",
            "#20B6A9",
        ),
        (
            "STEP 02",
            "Analyze",
            "Screen the text for four types of potential bias.",
            "#9878E6",
        ),
        (
            "STEP 03",
            "Explore results",
            "Review your personalized bias profile.",
            "#79A5EB",
        ),
    ]
    for (label, title, description, color), col in zip(
        steps, st.columns(3)
    ):
        with col:
            card(
                label,
                title,
                description,
                color,
                height=165,
            )
    section(
        "The four lenses",
        "Each lens explores a different form of potential bias.",
    )
    keys = list(BIAS)
    for pair in (keys[:2], keys[2:]):
        for key, col in zip(pair, st.columns(2)):
            with col:
                name, _, color, description = BIAS[key]
                card(
                    "BIAS CATEGORY",
                    name,
                    description,
                    color,
                    height=160,
                )
    section(
        "Limitations & Future Directions",
        "Understanding today's limitations helps us build a better BiasLens tomorrow.",
    )

    limitations, future = st.columns(2)

    with limitations:
        card(
            "WHERE WE ARE TODAY",
            "Current Limitations",
            "<strong>Context matters.</strong> Subtle meaning and counter-speech "
            "can be difficult to interpret.<br><br>"
            "<strong>Predictions aren't perfect.</strong> Some biased text may "
            "be missed, while other text may be incorrectly flagged.<br><br>"
            "<strong>English only.</strong> The current models are designed "
            "for English text.<br><br>"
            "<strong>Human judgment matters.</strong> Scores indicate model "
            "signals, not definitive judgments or bias severity.",
            "#9878E6",
            height=335,
        )

    with future:
        card(
            "WHERE WE WANT TO GO",
            "Future Directions",
            "<strong>Deeper context.</strong> Explore language models that "
            "better capture meaning and context.<br><br>"
            "<strong>More diverse data.</strong> Improve annotation quality "
            "and representation across sources.<br><br>"
            "<strong>Clearer explanations.</strong> Help users understand "
            "which language patterns influence predictions.<br><br>"
            "<strong>Beyond English.</strong> Explore multilingual support, "
            "including Arabic.",
            "#20B6A9",
            height=335,
        )
# -------------------- About --------------------
def about():
    hero(
        "ABOUT BIASLENS",
        "A clearer view of <span>language.</span>",
        "BiasLens makes it easier to recognize potential bias "
        "in written English through Natural Language Processing.",
    )
    section("What is BiasLens?")
    card(
        "NLP-POWERED BIAS DETECTION & ANALYSIS",
        "See beyond the words.",
        "BiasLens is an NLP-powered tool designed to help users "
        "identify potential bias in written English text. "
        "It screens text across four categories: linguistic, "
        "gender, racial, and text-level bias, and presents "
        "the results through a clear, interactive dashboard.",
        "#9878E6",
        height=170,
    )
    section(
        "Meet the team",
        "Saudi Digital Academy × Le Wagon · Data Science & AI Bootcamp",
    )
    people = [
        ("Sarah Altaleb", "PROJECT CREATOR & TEAM LEAD"),
        ("Hadeel Alghashmari", "TEAM CONTRIBUTOR"),
        ("Afnan Alhasni", "TEAM CONTRIBUTOR"),
        ("Nouf Alsufyani", "TEAM CONTRIBUTOR"),
    ]
    for pair in (people[:2], people[2:]):
        for (name, role), col in zip(pair, st.columns(2)):
            with col:
                card(
                    role,
                    name,
                    "",
                    "#9878E6" if name == "Sarah Altaleb" else "#79A5EB",
                    height=105,
                )
    with st.expander("Technology behind BiasLens"):
        st.write(
            "Python · Natural Language Processing (NLP) · "
            "scikit-learn · TF-IDF · Logistic Regression · "
            "Streamlit · Plotly"
        )
    st.link_button(
        "View project on GitHub",
        "https://github.com/altaleb-sarah/BiasLens",
        use_container_width=True,
    )
# -------------------- State & Navigation --------------------
for key, initial in {
    "text_input": "",
    "analyzed_text": None,
    "threshold": 0.5,
}.items():
    if key not in st.session_state:
        st.session_state[key] = initial
with st.sidebar:
    st.markdown(
        '<div class="bl-logo">◈ Bias<span>Lens</span></div>',
        unsafe_allow_html=True,
    )
    st.caption("SEE BEYOND THE WORDS")
    st.divider()
    st.caption("NAVIGATION")
    page = st.radio(
        "Page",
        ["Text Analyzer", "Model Insights", "About"],
        label_visibility="collapsed",
    )
    if page == "Text Analyzer":
        st.divider()
        with st.expander("Analysis settings"):
            st.slider(
                "Decision threshold",
                min_value=0.05,
                max_value=0.95,
                step=0.05,
                key="threshold",
                help=(
                    "Adjusts the classification cutoff, "
                    "not the model scores."
                ),
            )
        if st.session_state.analyzed_text:
            st.button(
                "Clear analysis",
                on_click=set_sample,
                args=("",),
                use_container_width=True,
            )
    st.divider()
    st.caption("Saudi Digital Academy × Le Wagon")
    st.caption("Data Science & AI Bootcamp Project")
if page == "Text Analyzer":
    analyzer()
elif page == "Model Insights":
    insights()
else:
    about()
