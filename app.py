"""
NYC Neighborhood Pulse — Streamlit App v2
Dark-themed, multi-tab layout
Run with:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go  # noqa: F401 (used for Scattermap)
import json, os

st.set_page_config(
    page_title="NYC Neighborhood Pulse",
    page_icon="🗽",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
  .stApp { background-color: #0a0d14; color: #e0e0e0; }
  .block-container { padding: 0 2rem 2rem 2rem; max-width: 1280px; }

  /* Site header */
  .site-header {
    padding: 1.8rem 0 0 0;
    margin-bottom: 0;
    border-bottom: 1px solid #1e2535;
  }
  .site-title {
    color: #c084fc !important; font-size: 2.625rem !important; font-weight: 700 !important;
    letter-spacing: 0.18em; text-transform: uppercase; margin: 0;
  }
  .site-subtitle { color: #64748b; font-size: 0.9rem; margin: 0.3rem 0 1.2rem 0; }

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] {
    background: transparent; border-bottom: 1px solid #1e2535; gap: 0;
  }
  .stTabs [data-baseweb="tab"] {
    background: transparent; color: #64748b; font-size: 0.83rem;
    font-weight: 500; padding: 0.55rem 1.1rem;
    border-radius: 0; border-bottom: 2px solid transparent;
  }
  .stTabs [aria-selected="true"] {
    background: transparent !important;
    color: #c084fc !important;
    border-bottom: 2px solid #c084fc !important;
  }
  .stTabs [data-baseweb="tab-panel"] { padding-top: 2rem; }

  /* KPI cards */
  .kpi-card {
    background: #141824; border: 1px solid #1e2535; border-radius: 12px;
    padding: 1.2rem 1.5rem; margin-bottom: 0.75rem;
  }
  .kpi-value { font-size: 5rem !important; font-weight: 700 !important; color: #c084fc !important; margin: 0; line-height: 1; }
  .kpi-label { font-size: 0.8rem; color: #64748b; margin-top: 0.4rem;
    text-transform: uppercase; letter-spacing: 0.08em; }

  /* Insight cards strip */
  .insight-strip { display: flex; gap: 0.75rem; margin-bottom: 2.5rem; flex-wrap: wrap; }
  .insight-card {
    background: #141824; border: 1px solid #1e2535;
    border-left: 3px solid #c084fc; border-radius: 8px;
    padding: 1rem 1.2rem; flex: 1; min-width: 200px;
    font-size: 0.82rem; color: #cbd5e1; line-height: 1.55;
  }
  .insight-card strong { color: #e2e8f0; display: block; margin-bottom: 0.3rem; font-size: 0.87rem; }

  /* Section headings */
  .section-title { font-size: 3.375rem !important; font-weight: 700 !important; color: #e2e8f0 !important; margin-bottom: 0.3rem; }
  .section-sub { font-size: 0.88rem; color: #94a3b8; margin-bottom: 1.4rem; line-height: 1.65; }

  /* Map labels */
  .map-label { font-size: 0.78rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.12em; color: #c084fc; margin-bottom: 0.4rem; }
  .map-desc { font-size: 0.84rem; color: #94a3b8; margin-bottom: 0.8rem; line-height: 1.6; }

  /* Methodology step boxes */
  .step-box {
    background: #141824; border: 1px solid #1e2535; border-radius: 10px;
    padding: 1.3rem 1.5rem; height: 100%;
  }
  .step-num { color: #c084fc; font-weight: 700; font-size: 0.75rem;
    text-transform: uppercase; letter-spacing: 0.12em; }
  .step-title { color: #e2e8f0; font-size: 1rem; font-weight: 600; margin: 0.35rem 0 0.6rem 0; }
  .step-body { color: #94a3b8; font-size: 0.84rem; line-height: 1.65; }

  /* Footer */
  .footer { border-top: 1px solid #1e2535; margin-top: 3rem;
    padding-top: 1.5rem; color: #475569; font-size: 0.78rem; }

  /* Hide Streamlit chrome */
  #MainMenu { visibility: hidden; }
  footer { visibility: hidden; }
  header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs')

# ── Topic subtitles (plain-language description shown under each topic label) ─
TOPIC_SUBTITLES = {
    'Great Location & Transit':    'subway access · walkability · central location',
    'Spanish-Speaking Visitors':   'Latino communities · Spanish-language reviews',
    'Parks & Outdoor Life':        'green space · outdoor activities · nature',
    'Nightlife & Entertainment':   'bars · music · evening energy',
    'Truly Enjoyable Experience':  'memorable stays · highly recommended',
    'Clean & Comfortable Stay':    'cleanliness · check-in · apartment basics',
    'Feels Like Home':             'warmth · residential character · local vibe',
    'NYC City Experience':         'urban energy · iconic neighborhoods · city life',
    'German-Speaking Visitors':    'German-speaking visitors · European travelers',
    'French-Speaking Visitors':    'Francophone visitors · French-language reviews',
    'Nice & Pleasant Place':       'charming atmosphere · welcoming · pleasant stays',
    'Practical Comfort':           'cleanliness · check-in · apartment basics',
}

# ── Topic color palette ───────────────────────────────────────────────────────
TOPIC_COLORS = {
    'Great Location & Transit':    '#00c8ff',
    'Spanish-Speaking Visitors':   '#dc32ff',
    'Parks & Outdoor Life':        '#32ff64',
    'Nightlife & Entertainment':   '#ff3264',
    'Truly Enjoyable Experience':  '#ffb432',
    'Clean & Comfortable Stay':    '#a78bfa',
    'Feels Like Home':             '#64c8ff',
    'NYC City Experience':         '#ff8c00',
    'German-Speaking Visitors':    '#b400ff',
    'French-Speaking Visitors':    '#ff50b4',
    'Nice & Pleasant Place':       '#50ffc8',
    'Practical Comfort':           '#96c896',
}

PLOTLY_DARK = dict(
    paper_bgcolor='#0a0d14',
    plot_bgcolor='#0a0d14',
    font=dict(color='#94a3b8', size=11),
    margin=dict(l=0, r=10, t=24, b=20),
)

# ── Data loaders ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv(os.path.join(OUTPUT_DIR, 'neighborhoods_topics.csv'))
    if 'borough' not in df.columns:
        df['borough'] = 'Unknown'
    return df

@st.cache_data
def load_listings():
    return pd.read_csv(os.path.join(OUTPUT_DIR, 'listing_locations.csv'))

@st.cache_data
def load_topics():
    with open(os.path.join(OUTPUT_DIR, 'topic_keywords.json')) as f:
        return json.load(f)


# ── Load everything ───────────────────────────────────────────────────────────
try:
    neigh_df  = load_data()
    topics    = load_topics()
    listings  = load_listings()
    data_ok   = True
except Exception as e:
    st.error(f"⚠️  Data load error: {e}. Run notebooks 01 and 02 first.")
    st.stop()

# ── Site header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="site-header">
  <p class="site-title">🗽 NYC Neighborhood Pulse</p>
  <p class="site-subtitle">Mapping the social character of New York City through 149,000 Airbnb reviews</p>
</div>
""", unsafe_allow_html=True)

# ── Navigation tabs ───────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Introduction", "Key Insights", "Data Explorer", "Methodology", "About"
])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — INTRODUCTION
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    left, right = st.columns([3, 2], gap="large")

    with left:
        st.markdown('<p class="section-title">Can Airbnb reviews reveal a social geography of NYC that differs from official neighborhood categories?</p>', unsafe_allow_html=True)
        st.markdown("""
        <p class="section-sub">
        New York City's 220 neighborhoods are officially defined by administrative boundaries —
        but boundaries don't capture how a place actually <em>feels</em>. This project asks
        whether the language of 149,903 Airbnb guest reviews can surface a different kind of map:
        one organized around social character, visitor perception, and lived urban experience.
        </p>
        <p class="section-sub">
        Visitors leave behind traces of what they noticed, loved, and remembered —
        transit access, local food scenes, a sense of safety, a distinctly local energy.
        By applying NLP topic modeling to these reviews, we extract ten recurring themes
        and map them across the city, revealing a <strong style="color:#c084fc">social geography
        of NYC</strong> that cuts across borough lines and official classifications.
        </p>
        <p class="section-sub">
        The result is two complementary interactive maps: one showing
        <strong style="color:#c084fc">where Airbnb activity concentrates</strong>
        at listing-level resolution, and another revealing
        <strong style="color:#c084fc">what each neighborhood is distinctively known for</strong>
        — not what is common everywhere, but what makes each place unusually itself.
        </p>
        """, unsafe_allow_html=True)

    with right:
        for val, label in [
            ("149,903", "Airbnb reviews analyzed"),
            ("220",     "NYC neighborhoods covered"),
            ("10",      "Discovered topic clusters"),
            ("5",       "NYC boroughs"),
        ]:
            st.markdown(f"""
            <div class="kpi-card">
              <p class="kpi-value">{val}</p>
              <p class="kpi-label">{label}</p>
            </div>""", unsafe_allow_html=True)

    st.divider()

    # Topic overview grid
    st.markdown('<p class="section-title" style="font-size:1.1rem;">The 10 Neighborhood Topics</p>', unsafe_allow_html=True)
    st.markdown("""<p class="section-sub">
    Each neighborhood is assigned the topic that most <em>distinctively</em> characterizes it —
    not just what is common city-wide, but what makes it stand out relative to the rest of NYC.
    </p>""", unsafe_allow_html=True)

    topic_counts = neigh_df['dominant_topic_label'].value_counts()
    cols = st.columns(5)
    for i, (topic, count) in enumerate(topic_counts.items()):
        color = TOPIC_COLORS.get(topic, '#888888')
        subtitle = TOPIC_SUBTITLES.get(topic, '')
        with cols[i % 5]:
            st.markdown(f"""
            <div style="background:#141824;border:1px solid #1e2535;border-top:3px solid {color};
                        border-radius:8px;padding:0.9rem;margin-bottom:0.75rem;text-align:center;">
              <div style="font-size:1.5rem;font-weight:700;color:{color};">{count}</div>
              <div style="font-size:0.75rem;font-weight:600;color:#e2e8f0;margin-top:0.25rem;line-height:1.4;">{topic}</div>
              <div style="font-size:0.65rem;color:#64748b;margin-top:0.2rem;line-height:1.4;font-style:italic;">{subtitle}</div>
            </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — KEY INSIGHTS
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:

    # ── Insight strip ─────────────────────────────────────────────────────────
    st.markdown("""
    <div class="insight-strip">
      <div class="insight-card">
        <strong>Manhattan dominates review volume</strong>
        Midtown, Hell's Kitchen, and the Lower East Side generate the city's densest
        cluster of Airbnb activity — but Brooklyn's Bed-Stuy has the single highest
        review count of any individual neighborhood.
      </div>
      <div class="insight-card">
        <strong>Visitor language reveals geography</strong>
        Spanish-, French-, and German-speaking visitors don't distribute randomly —
        they cluster in specific neighborhoods, reflecting cultural networks
        and diaspora communities.
      </div>
      <div class="insight-card">
        <strong>Small neighborhoods, stronger identities</strong>
        Neighborhoods with fewer reviews tend to score higher on distinctiveness.
        High-volume areas attract such diverse visitors that no single theme dominates.
      </div>
      <div class="insight-card">
        <strong>"Feels Like Home" dominates outer boroughs</strong>
        63 of 220 neighborhoods are defined by warmth and residential comfort —
        the dominant theme of Queens, Bronx, and Staten Island listings.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Chart 1: Borough review distribution ──────────────────────────────────
    c1l, c1r = st.columns([2, 3], gap="large")
    with c1l:
        st.markdown('<p class="section-title" style="font-size:1.15rem;">Review Concentration by Borough</p>', unsafe_allow_html=True)
        st.markdown("""<p class="section-sub">
        Manhattan accounts for the majority of Airbnb reviews, reflecting its status as
        the city's tourist core. Brooklyn is a close second, driven by neighborhoods like
        Bed-Stuy, Williamsburg, and Bushwick.<br><br>
        The outer boroughs remain underrepresented despite housing nearly half the city's
        population — suggesting Airbnb tourism stays concentrated in well-branded enclaves.
        </p>""", unsafe_allow_html=True)

    with c1r:
        borough_agg = (
            neigh_df.groupby('borough')['review_count']
            .sum().sort_values().reset_index()
        )
        fig1 = px.bar(
            borough_agg, x='review_count', y='borough', orientation='h',
            color='review_count',
            color_continuous_scale=[[0,'#1e1535'],[0.4,'#7c3aed'],[1,'#c084fc']],
            labels={'review_count': 'Total Reviews', 'borough': ''},
        )
        fig1.update_layout(**PLOTLY_DARK, height=260, coloraxis_showscale=False)
        fig1.update_traces(marker_line_width=0)
        fig1.update_xaxes(gridcolor='#1e2535', zerolinecolor='#1e2535')
        fig1.update_yaxes(gridcolor='#1e2535')
        st.plotly_chart(fig1, use_container_width=True)

    st.divider()

    # ── Chart 2: Topic distribution ───────────────────────────────────────────
    c2l, c2r = st.columns([3, 2], gap="large")
    with c2r:
        st.markdown('<p class="section-title" style="font-size:1.15rem;">What Topics Define NYC Neighborhoods?</p>', unsafe_allow_html=True)
        st.markdown("""<p class="section-sub">
        "Feels Like Home" is the most common neighborhood character — 63 neighborhoods
        are defined by warmth, comfort, and residential authenticity.<br><br>
        Three topics (Spanish-, French-, German-Speaking Visitors) reflect the
        international composition of NYC's rental market. These emerge from the
        clustering of non-English reviews, revealing communities of visitors that
        gravitate toward specific parts of the city.
        </p>""", unsafe_allow_html=True)

    with c2l:
        topic_bar = neigh_df['dominant_topic_label'].value_counts().reset_index()
        topic_bar.columns = ['Topic', 'Neighborhoods']
        fig2 = px.bar(
            topic_bar, x='Neighborhoods', y='Topic', orientation='h',
            color='Topic', color_discrete_map=TOPIC_COLORS,
            labels={'Neighborhoods': 'Number of Neighborhoods', 'Topic': ''},
        )
        fig2.update_layout(**PLOTLY_DARK, height=360, showlegend=False)
        fig2.update_traces(marker_line_width=0)
        fig2.update_xaxes(gridcolor='#1e2535', zerolinecolor='#1e2535')
        fig2.update_yaxes(gridcolor='#1e2535')
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # ── Chart 3: Distinctiveness vs review count ──────────────────────────────
    c3l, c3r = st.columns([3, 2], gap="large")
    with c3l:
        fig3 = px.scatter(
            neigh_df,
            x='review_count', y='distinctiveness',
            color='dominant_topic_label',
            color_discrete_map=TOPIC_COLORS,
            hover_data=['neighborhood', 'borough'],
            labels={
                'review_count':        'Review Count',
                'distinctiveness':     'Distinctiveness Score',
                'dominant_topic_label':'Topic',
            },
        )
        fig3.update_layout(
            **PLOTLY_DARK, height=340,
            legend=dict(bgcolor='#141824', bordercolor='#1e2535', borderwidth=1,
                        font=dict(size=10), title=''),
        )
        fig3.update_traces(marker=dict(size=8, line=dict(width=0)))
        fig3.update_xaxes(gridcolor='#1e2535', zerolinecolor='#1e2535')
        fig3.update_yaxes(gridcolor='#1e2535')
        st.plotly_chart(fig3, use_container_width=True)

    with c3r:
        st.markdown('<p class="section-title" style="font-size:1.15rem;">Small Neighborhoods, Stronger Identities</p>', unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#1a1035;border-left:3px solid #c084fc;border-radius:6px;
                    padding:0.8rem 1rem;margin-bottom:1rem;">
          <span style="color:#e2e8f0;font-size:0.88rem;font-style:italic;">
          "Instead of showing what is common everywhere, this score highlights
          what a neighborhood is <strong>unusually</strong> known for."
          </span>
        </div>
        <p class="section-sub">
        The <strong style="color:#c084fc">distinctiveness score</strong> divides each
        neighborhood's topic proportion by the city-wide average — a geographic TF-IDF.
        A score of 2.0 means that topic is twice as prevalent here as across NYC overall.<br><br>
        There is a clear inverse relationship: high-volume areas like Midtown or Williamsburg
        attract such diverse visitors that no single theme dominates, pushing scores lower.
        Smaller, niche neighborhoods draw a more homogeneous visitor type, making their
        character sharper and more legible.<br><br>
        <span style="color:#64748b;">Hover over points to explore individual neighborhoods.</span>
        </p>""", unsafe_allow_html=True)

    st.divider()

    # ── Chart 4: Top 15 neighborhoods ─────────────────────────────────────────
    st.markdown('<p class="section-title" style="font-size:1.15rem;">Most Reviewed Neighborhoods</p>', unsafe_allow_html=True)
    top15 = neigh_df.nlargest(15, 'review_count').sort_values('review_count')
    fig4 = px.bar(
        top15, x='review_count', y='neighborhood', orientation='h',
        color='dominant_topic_label', color_discrete_map=TOPIC_COLORS,
        hover_data=['borough', 'distinctiveness'],
        labels={'review_count': 'Reviews', 'neighborhood': '', 'dominant_topic_label': 'Topic'},
    )
    fig4.update_layout(
        **PLOTLY_DARK, height=380,
        legend=dict(bgcolor='#141824', bordercolor='#1e2535', borderwidth=1,
                    font=dict(size=10), title=''),
    )
    fig4.update_traces(marker_line_width=0)
    fig4.update_xaxes(gridcolor='#1e2535', zerolinecolor='#1e2535')
    fig4.update_yaxes(gridcolor='#1e2535')
    st.plotly_chart(fig4, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — DATA EXPLORER
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<p class="section-title">Interactive Map Explorer</p>', unsafe_allow_html=True)
    st.markdown("""<p class="section-sub">
    Two complementary views of NYC's neighborhood landscape.
    Zoom, pan, and hover to discover spatial patterns.
    </p>""", unsafe_allow_html=True)

    map_tab1, map_tab2 = st.tabs([
        "🔵  Review Density",
        "🎨  Dominant Topic per Neighborhood",
    ])

    MAP_LAYOUT = dict(
        paper_bgcolor='#0a0d14',
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(bgcolor='rgba(20,24,36,0.85)', bordercolor='#1e2535',
                    borderwidth=1, font=dict(size=11, color='#cbd5e1')),
    )

    with map_tab1:
        st.markdown('<p class="map-label">Airbnb Listing Density Across NYC</p>', unsafe_allow_html=True)
        st.markdown("""<p class="map-desc">
        Each point is an individual Airbnb listing (~25,000 active listings).
        Color intensity — dark navy to bright cyan — encodes review concentration.
        Brighter clusters indicate denser short-term rental activity and higher tourist foot traffic.
        </p>""", unsafe_allow_html=True)

        fig_density = go.Figure(go.Scattermap(
            lat=listings['lat'],
            lon=listings['lon'],
            mode='markers',
            marker=dict(size=5, color='#22d4b5', opacity=0.18),
            hoverinfo='skip',
            showlegend=False,
        ))
        fig_density.update_layout(
            **MAP_LAYOUT,
            height=580,
            map=dict(
                style='carto-darkmatter',
                center=dict(lat=40.73, lon=-73.97),
                zoom=10,
            ),
        )
        st.plotly_chart(fig_density, use_container_width=True)

    with map_tab2:
        st.markdown('<p class="map-label">Dominant Topic per Neighborhood</p>', unsafe_allow_html=True)
        st.markdown("""<p class="map-desc">
        Each circle is a neighborhood centroid. <strong>Size</strong> = total review volume;
        <strong>color</strong> = distinctive topic that most characterizes that neighborhood
        relative to the city average. Hover to see neighborhood name, topic, and top keywords.
        </p>""", unsafe_allow_html=True)

        fig_topics = px.scatter_map(
            neigh_df,
            lat='lat', lon='lon',
            color='dominant_topic_label',
            size='review_count',
            hover_name='neighborhood',
            hover_data={
                'borough': True,
                'dominant_topic_label': True,
                'review_count': True,
                'top_keywords': True,
                'lat': False, 'lon': False,
            },
            color_discrete_map=TOPIC_COLORS,
            size_max=45,
            zoom=10,
            center={"lat": 40.73, "lon": -73.98},
            map_style='carto-darkmatter',
            height=580,
            labels={
                'dominant_topic_label': 'Topic',
                'review_count': 'Reviews',
                'borough': 'Borough',
                'top_keywords': 'Keywords',
            },
        )
        fig_topics.update_layout(**MAP_LAYOUT)
        st.plotly_chart(fig_topics, use_container_width=True)

    st.divider()

    # Filterable table
    st.markdown('<p class="section-title" style="font-size:1.1rem;">Browse All Neighborhoods</p>', unsafe_allow_html=True)
    fc1, fc2 = st.columns(2)
    with fc1:
        sel_borough = st.multiselect(
            "Filter by Borough",
            sorted(neigh_df['borough'].dropna().unique()),
            default=sorted(neigh_df['borough'].dropna().unique()),
        )
    with fc2:
        sel_topic = st.multiselect(
            "Filter by Topic",
            sorted(neigh_df['dominant_topic_label'].dropna().unique()),
            default=sorted(neigh_df['dominant_topic_label'].dropna().unique()),
        )

    filtered = neigh_df[
        neigh_df['borough'].isin(sel_borough) &
        neigh_df['dominant_topic_label'].isin(sel_topic)
    ][['neighborhood','borough','dominant_topic_label','review_count','distinctiveness','top_keywords']].copy()
    filtered.columns = ['Neighborhood','Borough','Dominant Topic','Reviews','Distinctiveness','Top Keywords']
    filtered = filtered.sort_values('Reviews', ascending=False).reset_index(drop=True)
    st.dataframe(filtered, use_container_width=True, height=320)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — METHODOLOGY
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<p class="section-title">How We Built This</p>', unsafe_allow_html=True)
    st.markdown("""<p class="section-sub">
    A three-stage pipeline: data collection and cleaning → NLP topic modeling → geospatial visualization.
    </p>""", unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3, gap="medium")
    with m1:
        st.markdown("""
        <div class="step-box">
          <div class="step-num">Step 01 — Data</div>
          <div class="step-title">Loading &amp; Preprocessing</div>
          <div class="step-body">
            Raw data from <strong style="color:#c084fc">Inside Airbnb NYC</strong>:
            1,003,480 reviews merged with 36,445 listing records across 224 neighborhoods.<br><br>
            Filtered to reviews from <strong>2022 onwards</strong>, dropped reviews under
            50 characters, then applied <strong>stratified neighborhood sampling</strong>
            to reach 149,903 reviews while preserving smaller neighborhoods.
          </div>
        </div>""", unsafe_allow_html=True)
    with m2:
        st.markdown("""
        <div class="step-box">
          <div class="step-num">Step 02 — NLP</div>
          <div class="step-title">Topic Modeling</div>
          <div class="step-body">
            Text vectorized with <strong style="color:#c084fc">TF-IDF</strong>
            (top 5,000 terms), dimensionality-reduced via
            <strong>Truncated SVD</strong> (50 components),
            and clustered into 10 topics using <strong>KMeans</strong>.<br><br>
            Each neighborhood was assigned its <strong>distinctive topic</strong> —
            the topic whose neighborhood proportion most exceeds the city-wide average
            (a geographic TF-IDF approach).
          </div>
        </div>""", unsafe_allow_html=True)
    with m3:
        st.markdown("""
        <div class="step-box">
          <div class="step-num">Step 03 — Viz</div>
          <div class="step-title">Geospatial Visualization</div>
          <div class="step-body">
            Review coordinates aggregated to an <strong style="color:#c084fc">H3 hexagonal grid</strong>
            (resolution 10, ~65 m cells) for the density layer.<br><br>
            Neighborhood topics plotted as sized, colored circles using
            <strong>Kepler.gl</strong> — a GPU-accelerated geospatial library.
            Both maps use a dark basemap to foreground the data layer.
          </div>
        </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown('<p class="section-title" style="font-size:1.05rem;">Tech Stack</p>', unsafe_allow_html=True)
    tech_cols = st.columns(4)
    for col, (name, desc) in zip(tech_cols, [
        ("pandas + numpy",  "Data wrangling &amp; sampling"),
        ("scikit-learn",    "TF-IDF · SVD · KMeans NLP pipeline"),
        ("Kepler.gl",       "Interactive geospatial maps"),
        ("Streamlit",       "Web app framework"),
    ]):
        with col:
            st.markdown(f"""
            <div style="background:#141824;border:1px solid #1e2535;border-radius:8px;
                        padding:1rem;text-align:center;">
              <div style="color:#c084fc;font-weight:600;font-size:0.88rem;">{name}</div>
              <div style="color:#64748b;font-size:0.76rem;margin-top:0.3rem;">{desc}</div>
            </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — ABOUT
# ═══════════════════════════════════════════════════════════════════════════════
with tab5:
    al, ar = st.columns([2, 1], gap="large")

    with al:
        st.markdown('<p class="section-title">About This Project</p>', unsafe_allow_html=True)
        st.markdown("""
        <p class="section-sub">
        <strong>NYC Neighborhood Pulse</strong> is a data visualization final project exploring
        the social geography of New York City through the lens of Airbnb guest reviews.
        Built as part of a graduate course in Data Visualization at Columbia University.
        </p>
        <p class="section-sub">
        The core research question: <em>Can the unstructured text of short-term rental reviews
        reveal something meaningful about neighborhood character — and can that be mapped?</em>
        </p>
        <p class="section-sub">
        The answer is yes. While reviews are noisy and tourist-centric, their aggregate patterns
        reflect real geographic phenomena: cultural clusters, transit accessibility gradients,
        the spatial distribution of international visitors, and the contrast between
        residential and tourist-facing neighborhoods.
        </p>
        <div style="margin-top:1.5rem;">
          <div style="color:#64748b;font-size:0.75rem;text-transform:uppercase;
                      letter-spacing:0.1em;margin-bottom:0.5rem;">Data Source</div>
          <div style="color:#94a3b8;font-size:0.84rem;">
            Inside Airbnb —
            <a href="http://insideairbnb.com" style="color:#c084fc;">insideairbnb.com</a><br/>
            NYC listings and reviews dataset. Used for academic research purposes only.
          </div>
        </div>
        """, unsafe_allow_html=True)

    with ar:
        st.markdown("""
        <div style="background:#141824;border:1px solid #1e2535;border-radius:12px;padding:1.5rem;">
          <div style="color:#64748b;font-size:0.75rem;text-transform:uppercase;
                      letter-spacing:0.1em;margin-bottom:1.1rem;">Project Stats</div>
        """, unsafe_allow_html=True)
        for val, label in [
            ("1,003,480", "Raw reviews in dataset"),
            ("149,903",   "Reviews after filtering &amp; sampling"),
            ("220 / 224", "Neighborhoods with data coverage"),
            ("10",        "Topic clusters (KMeans k=10)"),
            ("2022–2024", "Review date range analyzed"),
        ]:
            st.markdown(f"""
            <div style="margin-bottom:0.9rem;">
              <div style="color:#c084fc;font-size:1.25rem;font-weight:700;">{val}</div>
              <div style="color:#64748b;font-size:0.74rem;">{label}</div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
  NYC Neighborhood Pulse &nbsp;·&nbsp; Columbia University &nbsp;·&nbsp;
  Data Visualization Final Project &nbsp;·&nbsp; 2025 &nbsp;&nbsp;|&nbsp;&nbsp;
  Data: <a href="http://insideairbnb.com" style="color:#c084fc;">Inside Airbnb</a>
  &nbsp;&nbsp;|&nbsp;&nbsp;
  Built with Streamlit · Kepler.gl · Plotly
</div>
""", unsafe_allow_html=True)
