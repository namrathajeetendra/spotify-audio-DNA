import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# --- Page Config ---
st.set_page_config(
    page_title="Spotify Audio DNA",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS (neon music vibe) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;600&display=swap');
    
    .stApp { background-color: #0a0a0f; }
    
    h1, h2, h3 { font-family: 'Orbitron', sans-serif !important; }
    
    .main-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.8rem;
        font-weight: 900;
        background: linear-gradient(135deg, #00ff88, #ff006e, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
        letter-spacing: 2px;
    }
    
    .subtitle {
        text-align: center;
        color: #888;
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        margin-bottom: 2rem;
        letter-spacing: 1px;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid #00ff8833;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 0 20px #00ff8811;
    }
    
    .metric-value {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.8rem;
        font-weight: 700;
        color: #00ff88;
    }
    
    .metric-label {
        color: #888;
        font-size: 0.8rem;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-top: 0.3rem;
    }
    
    .section-header {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.2rem;
        color: #00ff88;
        border-left: 3px solid #ff006e;
        padding-left: 1rem;
        margin: 2rem 0 1rem 0;
        letter-spacing: 1px;
    }

    .insight-box {
        background: linear-gradient(135deg, #1a1a2e, #0d0d1a);
        border: 1px solid #ff006e44;
        border-radius: 10px;
        padding: 1rem 1.5rem;
        margin: 0.5rem 0;
        color: #ccc;
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        line-height: 1.6;
    }

    div[data-testid="stSelectbox"] label,
    div[data-testid="stMultiSelect"] label {
        color: #00ff88 !important;
        font-family: 'Orbitron', sans-serif !important;
        font-size: 0.8rem !important;
        letter-spacing: 1px !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, #00ff88, #00d4ff);
        color: #0a0a0f;
        font-family: 'Orbitron', sans-serif;
        font-weight: 700;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        letter-spacing: 1px;
    }

    section[data-testid="stSidebar"] {
        background: #0d0d1a;
        border-right: 1px solid #00ff8822;
    }
</style>
""", unsafe_allow_html=True)

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_csv("dataset.csv")
    df = df.dropna()
    df = df[df['popularity'] > 0]
    # Extract decade from release year if available
    if 'track_genre' in df.columns:
        df['genre'] = df['track_genre']
    return df

df = load_data()

AUDIO_FEATURES = ['danceability', 'energy', 'valence', 'acousticness', 'instrumentalness', 'speechiness', 'liveness']
NEON_COLORS = ['#00ff88', '#ff006e', '#00d4ff', '#ff9500', '#bf00ff', '#00ffcc', '#ff4466']

# --- Header ---
st.markdown('<div class="main-title">🎵 SPOTIFY AUDIO DNA</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Decoding the science behind what makes songs hit different</div>', unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.markdown("### 🎛️ Controls")
all_genres = sorted(df['genre'].unique())
selected_genres = st.sidebar.multiselect("Select Genres", all_genres, default=all_genres[:5])
popularity_threshold = st.sidebar.slider("Popularity Threshold (for Hit Formula)", 0, 100, 70)

if not selected_genres:
    selected_genres = all_genres[:5]

filtered_df = df[df['genre'].isin(selected_genres)]

# --- KPI Row ---
st.markdown('<div class="section-header">DATASET OVERVIEW</div>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{len(df):,}</div>
        <div class="metric-label">Total Tracks</div>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{df['genre'].nunique()}</div>
        <div class="metric-label">Genres</div>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{df['artists'].nunique():,}</div>
        <div class="metric-label">Artists</div>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{df['popularity'].mean():.0f}</div>
        <div class="metric-label">Avg Popularity</div>
    </div>""", unsafe_allow_html=True)

st.markdown("---")

# --- Section 1: Genre DNA Radar ---
st.markdown('<div class="section-header">01 — GENRE AUDIO DNA</div>', unsafe_allow_html=True)
st.markdown("Each genre has a unique audio fingerprint. Select genres to compare their DNA.")

genre_avg = filtered_df.groupby('genre')[AUDIO_FEATURES].mean()

fig_radar = go.Figure()
for i, genre in enumerate(genre_avg.index):
    values = genre_avg.loc[genre, AUDIO_FEATURES].tolist()
    values += values[:1]
    fig_radar.add_trace(go.Scatterpolar(
        r=values,
        theta=AUDIO_FEATURES + [AUDIO_FEATURES[0]],
        fill='toself',
        name=genre,
        line_color=NEON_COLORS[i % len(NEON_COLORS)],
        fillcolor=f'rgba(0,255,136,0.1)' if i == 0 else f'rgba(255,0,110,0.1)' if i == 1 else f'rgba(0,212,255,0.1)' if i == 2 else f'rgba(255,149,0,0.1)' if i == 3 else f'rgba(191,0,255,0.1)',
        opacity=0.9
    ))

fig_radar.update_layout(
    polar=dict(
        bgcolor='#0d0d1a',
        radialaxis=dict(visible=True, range=[0, 1], color='#444', gridcolor='#222'),
        angularaxis=dict(color='#00ff88', gridcolor='#222')
    ),
    paper_bgcolor='#0a0a0f',
    plot_bgcolor='#0a0a0f',
    font=dict(color='#ccc', family='Inter'),
    legend=dict(bgcolor='#0d0d1a', bordercolor='#333', font=dict(color='#ccc')),
    height=500,
    margin=dict(t=40, b=40)
)
st.plotly_chart(fig_radar, use_container_width=True)

st.markdown("---")

# --- Section 2: Hit Formula ---
st.markdown('<div class="section-header">02 — THE HIT FORMULA</div>', unsafe_allow_html=True)
st.markdown(f"Comparing audio DNA of **hits** (popularity ≥ {popularity_threshold}) vs **flops** (popularity < 30)")

hits = df[df['popularity'] >= popularity_threshold][AUDIO_FEATURES].mean()
flops = df[df['popularity'] < 30][AUDIO_FEATURES].mean()

fig_hit = go.Figure()
fig_hit.add_trace(go.Bar(
    name=f'🔥 Hits (≥{popularity_threshold})',
    x=AUDIO_FEATURES,
    y=hits.values,
    marker_color='#00ff88',
    marker_line_color='#00ff88',
))
fig_hit.add_trace(go.Bar(
    name='💀 Flops (<30)',
    x=AUDIO_FEATURES,
    y=flops.values,
    marker_color='#ff006e',
    marker_line_color='#ff006e',
))
fig_hit.update_layout(
    barmode='group',
    paper_bgcolor='#0a0a0f',
    plot_bgcolor='#0a0a0f',
    font=dict(color='#ccc', family='Inter'),
    legend=dict(bgcolor='#0d0d1a', bordercolor='#333'),
    xaxis=dict(gridcolor='#1a1a2e', color='#888'),
    yaxis=dict(gridcolor='#1a1a2e', color='#888'),
    height=400
)
st.plotly_chart(fig_hit, use_container_width=True)

# Insight
hit_winner = (hits - flops).abs().idxmax()
st.markdown(f"""<div class="insight-box">
    💡 <b>Key Insight:</b> The biggest difference between hits and flops is <b style="color:#00ff88">{hit_winner}</b>. 
    Hits score {hits[hit_winner]:.2f} vs flops at {flops[hit_winner]:.2f} — a {abs(hits[hit_winner]-flops[hit_winner]):.2f} gap.
</div>""", unsafe_allow_html=True)

st.markdown("---")

# --- Section 3: Genre Battle ---
st.markdown('<div class="section-header">03 — GENRE BATTLE</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    genre_a = st.selectbox("Genre A", all_genres, index=0)
with col2:
    genre_b = st.selectbox("Genre B", all_genres, index=1)

ga = df[df['genre'] == genre_a][AUDIO_FEATURES].mean()
gb = df[df['genre'] == genre_b][AUDIO_FEATURES].mean()

fig_battle = go.Figure()
fig_battle.add_trace(go.Bar(name=genre_a, x=AUDIO_FEATURES, y=ga.values, marker_color='#00d4ff'))
fig_battle.add_trace(go.Bar(name=genre_b, x=AUDIO_FEATURES, y=gb.values, marker_color='#ff9500'))
fig_battle.update_layout(
    barmode='group',
    paper_bgcolor='#0a0a0f',
    plot_bgcolor='#0a0a0f',
    font=dict(color='#ccc', family='Inter'),
    legend=dict(bgcolor='#0d0d1a', bordercolor='#333'),
    xaxis=dict(gridcolor='#1a1a2e', color='#888'),
    yaxis=dict(gridcolor='#1a1a2e', color='#888'),
    height=400
)
st.plotly_chart(fig_battle, use_container_width=True)

st.markdown("---")

# --- Section 4: Correlation Heatmap ---
st.markdown('<div class="section-header">04 — WHAT ACTUALLY PREDICTS POPULARITY?</div>', unsafe_allow_html=True)
st.markdown("Correlation between audio features and popularity score.")

corr_features = AUDIO_FEATURES + ['popularity', 'duration_ms', 'tempo', 'loudness']
corr_features = [f for f in corr_features if f in df.columns]
corr = df[corr_features].corr()

fig_heatmap = go.Figure(data=go.Heatmap(
    z=corr.values,
    x=corr.columns,
    y=corr.columns,
    colorscale=[[0, '#ff006e'], [0.5, '#0a0a0f'], [1, '#00ff88']],
    zmid=0,
    text=np.round(corr.values, 2),
    texttemplate='%{text}',
    textfont=dict(size=10, color='white'),
))
fig_heatmap.update_layout(
    paper_bgcolor='#0a0a0f',
    plot_bgcolor='#0a0a0f',
    font=dict(color='#ccc', family='Inter'),
    height=500,
    margin=dict(t=40, b=40)
)
st.plotly_chart(fig_heatmap, use_container_width=True)

pop_corr = corr['popularity'].drop('popularity').abs().idxmax()
st.markdown(f"""<div class="insight-box">
    💡 <b>Key Insight:</b> <b style="color:#00ff88">{pop_corr}</b> has the strongest correlation with popularity among all audio features.
    This suggests it plays a key role in whether a song resonates with listeners.
</div>""", unsafe_allow_html=True)

st.markdown("---")

# --- Section 5: Top Artists ---
st.markdown('<div class="section-header">05 — MOST POPULAR ARTISTS BY GENRE</div>', unsafe_allow_html=True)
selected_genre_top = st.selectbox("Select Genre", all_genres, key="top_artists")
top_artists = (df[df['genre'] == selected_genre_top]
               .groupby('artists')['popularity']
               .mean()
               .nlargest(10)
               .reset_index())

fig_artists = px.bar(top_artists, x='popularity', y='artists', orientation='h',
                     color='popularity', color_continuous_scale=['#ff006e', '#00ff88'])
fig_artists.update_layout(
    paper_bgcolor='#0a0a0f',
    plot_bgcolor='#0a0a0f',
    font=dict(color='#ccc', family='Inter'),
    xaxis=dict(gridcolor='#1a1a2e', color='#888'),
    yaxis=dict(gridcolor='#1a1a2e', color='#888', categoryorder='total ascending'),
    coloraxis_showscale=False,
    height=420
)
st.plotly_chart(fig_artists, use_container_width=True)

# --- Footer ---
st.markdown("---")
st.markdown('<div style="text-align:center; color:#444; font-family:Inter; font-size:0.8rem; letter-spacing:1px;">SPOTIFY AUDIO DNA · BUILT WITH PYTHON & STREAMLIT · DATA FROM KAGGLE</div>', unsafe_allow_html=True)