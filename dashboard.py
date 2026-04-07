import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

# ─── PAGE CONFIG ───────────────────────────────────────────────
st.set_page_config(
    page_title="WoodSpace Dashboard",
    page_icon="🪵",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── CUSTOM CSS ─────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&display=swap');
  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
  .main { background: #0d0c0a; }
  h1, h2, h3 { color: #c9a96e !important; }
  .metric-card {
    background: #161410;
    border: 1px solid rgba(201,169,110,0.2);
    border-radius: 8px;
    padding: 1.2rem 1.5rem;
    text-align: center;
  }
  .metric-num { font-size: 2.2rem; font-weight: 500; color: #c9a96e; }
  .metric-label { font-size: 0.75rem; letter-spacing: 0.15em; text-transform: uppercase; opacity: 0.5; margin-top: 0.3rem; }
  .stDataFrame { border: 1px solid rgba(201,169,110,0.2) !important; }
</style>
""", unsafe_allow_html=True)

# ─── LOAD DATA ──────────────────────────────────────────────────
@st.cache_data(ttl=30)
def load_data():
    if not os.path.exists('leads.csv'):
        return pd.DataFrame(columns=['Timestamp','Name','Phone','Service','Budget','Message'])
    df = pd.read_csv('leads.csv')
    if 'Timestamp' in df.columns:
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        df['Date'] = df['Timestamp'].dt.date
        df['Hour'] = df['Timestamp'].dt.hour
        df['Day'] = df['Timestamp'].dt.day_name()
    return df

df = load_data()

# ─── HEADER ─────────────────────────────────────────────────────
st.markdown("## 🪵 WoodSpace — Leads Dashboard")
st.markdown("---")

if df.empty:
    st.info("Abhi tak koi lead nahi aayi. Jab form submit hoga, yahan dikhega.")
    st.stop()

# ─── KEY METRICS ────────────────────────────────────────────────
total = len(df)
today = df[df['Date'] == datetime.today().date()] if 'Date' in df.columns else pd.DataFrame()
this_week = df[df['Timestamp'] >= (datetime.now() - timedelta(days=7))] if 'Timestamp' in df.columns else pd.DataFrame()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="metric-card"><div class="metric-num">{total}</div><div class="metric-label">Total Leads</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card"><div class="metric-num">{len(today)}</div><div class="metric-label">Aaj Ke Leads</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card"><div class="metric-num">{len(this_week)}</div><div class="metric-label">Is Hafte</div></div>', unsafe_allow_html=True)
with col4:
    top_service = df['Service'].mode()[0] if 'Service' in df.columns and not df['Service'].isna().all() else "—"
    st.markdown(f'<div class="metric-card"><div class="metric-num" style="font-size:1.2rem;padding-top:0.4rem;">{top_service}</div><div class="metric-label">Top Service</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── CHARTS ─────────────────────────────────────────────────────
col_a, col_b = st.columns(2)

with col_a:
    st.markdown("### 📊 Service-wise Leads")
    if 'Service' in df.columns:
        service_counts = df['Service'].value_counts().reset_index()
        service_counts.columns = ['Service', 'Count']
        fig = px.bar(
            service_counts, x='Service', y='Count',
            color_discrete_sequence=['#c9a96e'],
            template='plotly_dark'
        )
        fig.update_layout(
            paper_bgcolor='#161410', plot_bgcolor='#161410',
            font_color='#f5f0e8', showlegend=False,
            margin=dict(t=20, b=20, l=10, r=10)
        )
        fig.update_traces(marker_line_color='#0d0c0a', marker_line_width=1)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Service data nahi hai")

with col_b:
    st.markdown("### 📅 Leads Over Time")
    if 'Date' in df.columns:
        daily = df.groupby('Date').size().reset_index(name='Leads')
        daily['Date'] = pd.to_datetime(daily['Date'])
        fig2 = px.line(
            daily, x='Date', y='Leads',
            color_discrete_sequence=['#c9a96e'],
            template='plotly_dark'
        )
        fig2.update_layout(
            paper_bgcolor='#161410', plot_bgcolor='#161410',
            font_color='#f5f0e8',
            margin=dict(t=20, b=20, l=10, r=10)
        )
        fig2.update_traces(line_width=2, mode='lines+markers', marker_size=6)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Timestamp data nahi hai")

# ─── SECOND ROW ─────────────────────────────────────────────────
col_c, col_d = st.columns(2)

with col_c:
    st.markdown("### 🕐 Peak Hours")
    if 'Hour' in df.columns:
        hour_counts = df.groupby('Hour').size().reset_index(name='Leads')
        fig3 = px.bar(
            hour_counts, x='Hour', y='Leads',
            color_discrete_sequence=['#5DCAA5'],
            template='plotly_dark'
        )
        fig3.update_layout(
            paper_bgcolor='#161410', plot_bgcolor='#161410',
            font_color='#f5f0e8', showlegend=False,
            margin=dict(t=20, b=20, l=10, r=10),
            xaxis_title="Hour of Day", yaxis_title="Leads"
        )
        st.plotly_chart(fig3, use_container_width=True)

with col_d:
    st.markdown("### 📆 Day-wise Performance")
    if 'Day' in df.columns:
        day_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        day_counts = df.groupby('Day').size().reset_index(name='Leads')
        day_counts['Day'] = pd.Categorical(day_counts['Day'], categories=day_order, ordered=True)
        day_counts = day_counts.sort_values('Day')
        fig4 = px.bar(
            day_counts, x='Day', y='Leads',
            color_discrete_sequence=['#AFA9EC'],
            template='plotly_dark'
        )
        fig4.update_layout(
            paper_bgcolor='#161410', plot_bgcolor='#161410',
            font_color='#f5f0e8', showlegend=False,
            margin=dict(t=20, b=20, l=10, r=10)
        )
        st.plotly_chart(fig4, use_container_width=True)

# ─── LEADS TABLE ────────────────────────────────────────────────
st.markdown("### 📋 All Leads")
col_filter1, col_filter2, col_filter3 = st.columns([2,2,1])
with col_filter1:
    search = st.text_input("🔍 Search by name/phone", "")
with col_filter2:
    if 'Service' in df.columns:
        services = ['All'] + sorted(df['Service'].dropna().unique().tolist())
        sel_service = st.selectbox("Filter by Service", services)
    else:
        sel_service = 'All'
with col_filter3:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Refresh"):
        st.cache_data.clear()
        st.rerun()

filtered = df.copy()
if search:
    filtered = filtered[
        filtered['Name'].str.contains(search, case=False, na=False) |
        filtered['Phone'].astype(str).str.contains(search, na=False)
    ]
if sel_service != 'All' and 'Service' in filtered.columns:
    filtered = filtered[filtered['Service'] == sel_service]

display_cols = [c for c in ['Timestamp','Name','Phone','Service','Budget','Message'] if c in filtered.columns]
st.dataframe(
    filtered[display_cols].sort_values('Timestamp', ascending=False) if 'Timestamp' in filtered.columns else filtered[display_cols],
    use_container_width=True, height=400
)

# ─── EXPORT ─────────────────────────────────────────────────────
st.markdown("---")
col_exp1, col_exp2 = st.columns([1, 4])
with col_exp1:
    csv_data = filtered[display_cols].to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ CSV Export",
        data=csv_data,
        file_name=f"woodspace_leads_{datetime.now().strftime('%Y%m%d')}.csv",
        mime='text/csv'
    )
