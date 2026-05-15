import os
from datetime import datetime, timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="WoodSpace Lead Dashboard",
    page_icon="🪵",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Cormorant+Garamond:wght@500;600&display=swap');

  :root {
    --border: rgba(201, 169, 110, 0.18);
    --gold: #c9a96e;
    --gold-soft: #e8d4a8;
    --text: #f5f0e8;
    --muted: #b7ac98;
  }

  .stApp {
    background:
      radial-gradient(circle at top right, rgba(201, 169, 110, 0.10), transparent 28%),
      radial-gradient(circle at left center, rgba(110, 197, 168, 0.08), transparent 22%),
      linear-gradient(180deg, #0d0c0a 0%, #12100d 100%);
    color: var(--text);
  }

  .block-container {
    max-width: 1320px;
    padding-top: 2.5rem;
    padding-bottom: 2rem;
  }

  h1, h2, h3 {
    color: var(--gold-soft) !important;
  }

  .dashboard-shell {
    margin-bottom: 1.75rem;
  }

  .dashboard-kicker {
    color: var(--gold);
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    margin-bottom: 0.7rem;
  }

  .dashboard-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: clamp(2.4rem, 4vw, 4rem);
    line-height: 0.98;
    color: var(--text);
    margin: 0;
  }

  .dashboard-subtitle {
    margin-top: 0.8rem;
    max-width: 760px;
    color: var(--muted);
    font-size: 0.96rem;
    line-height: 1.8;
  }

  .summary-band {
    background: linear-gradient(135deg, rgba(201, 169, 110, 0.14), rgba(22, 20, 16, 0.96));
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1.2rem 1.4rem;
    margin: 1.3rem 0 2rem;
    color: var(--text);
  }

  .metric-card {
    background: linear-gradient(180deg, rgba(29, 26, 21, 0.95), rgba(18, 16, 13, 0.98));
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1.25rem 1.3rem;
    min-height: 148px;
    box-shadow: 0 18px 40px rgba(0, 0, 0, 0.18);
  }

  .metric-label {
    color: var(--muted);
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
  }

  .metric-value {
    color: var(--gold-soft);
    font-size: 2.3rem;
    font-weight: 700;
    margin: 0.65rem 0 0.35rem;
    line-height: 1;
  }

  .metric-footnote {
    color: var(--muted);
    font-size: 0.86rem;
    line-height: 1.6;
  }

  .section-title {
    color: var(--gold-soft);
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin: 0.4rem 0 0.8rem;
  }

  .chart-panel {
    background: linear-gradient(180deg, rgba(24, 21, 17, 0.98), rgba(15, 13, 10, 0.98));
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 1rem 1rem 0.35rem;
    box-shadow: 0 18px 40px rgba(0, 0, 0, 0.16);
    margin-bottom: 1rem;
  }

  .panel-title {
    color: var(--gold-soft);
    font-size: 0.95rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin: 0 0 0.2rem;
  }

  .panel-copy {
    color: var(--muted);
    font-size: 0.88rem;
    line-height: 1.7;
    margin-bottom: 0.4rem;
  }

  div[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: 16px;
    overflow: hidden;
  }

  div[data-baseweb="select"] > div,
  div[data-testid="stTextInput"] input {
    background: rgba(22, 20, 16, 0.95) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
  }

  div[data-testid="stDownloadButton"] button,
  div[data-testid="stButton"] button {
    border-radius: 12px;
    border: 1px solid rgba(201, 169, 110, 0.32);
    background: linear-gradient(135deg, rgba(201, 169, 110, 0.18), rgba(201, 169, 110, 0.08));
    color: var(--text);
    font-weight: 600;
  }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data(ttl=30)
def load_data():
    if not os.path.exists("leads.csv"):
        return pd.DataFrame(
            columns=["Timestamp", "Name", "Phone", "Service", "Budget", "Message"]
        )

    df = pd.read_csv("leads.csv")
    if "Timestamp" in df.columns:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
        df["Date"] = df["Timestamp"].dt.date
        df["Hour"] = df["Timestamp"].dt.hour
        df["Day"] = df["Timestamp"].dt.day_name()
    return df


def metric_card(label, value, footnote):
    return f"""
    <div class="metric-card">
      <div class="metric-label">{label}</div>
      <div class="metric-value">{value}</div>
      <div class="metric-footnote">{footnote}</div>
    </div>
    """


def panel_header(title, copy):
    st.markdown(
        f"""
<div class="chart-panel">
  <div class="panel-title">{title}</div>
  <div class="panel-copy">{copy}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def apply_figure_style(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#f5f0e8",
        margin=dict(t=18, b=20, l=10, r=10),
        showlegend=False,
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            linecolor="rgba(255,255,255,0.08)",
            tickfont=dict(color="#b7ac98"),
            title_font=dict(color="#b7ac98"),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.07)",
            zeroline=False,
            tickfont=dict(color="#b7ac98"),
            title_font=dict(color="#b7ac98"),
        ),
    )
    return fig


df = load_data()

st.markdown(
    """
<div class="dashboard-shell">
  <div class="dashboard-kicker">Lead Intelligence</div>
  <h1 class="dashboard-title">WoodSpace Sales Dashboard</h1>
  <p class="dashboard-subtitle">
    Monitor incoming enquiries, identify demand patterns, and review lead quality from a single professional reporting view.
  </p>
</div>
""",
    unsafe_allow_html=True,
)

if df.empty:
    st.info(
        "No leads have been captured yet. Once a visitor submits the website form, records will appear here automatically."
    )
    st.stop()

total_leads = len(df)
today_leads = (
    df[df["Date"] == datetime.today().date()]
    if "Date" in df.columns
    else pd.DataFrame()
)
weekly_leads = (
    df[df["Timestamp"] >= (datetime.now() - timedelta(days=7))]
    if "Timestamp" in df.columns
    else pd.DataFrame()
)
top_service = (
    df["Service"].mode()[0]
    if "Service" in df.columns and not df["Service"].dropna().empty
    else "Not available"
)
latest_entry = (
    df["Timestamp"].max().strftime("%d %b %Y, %I:%M %p")
    if "Timestamp" in df.columns and df["Timestamp"].notna().any()
    else "Not available"
)

st.markdown(
    f"""
<div class="summary-band">
  Latest lead received: <strong>{latest_entry}</strong> &nbsp;|&nbsp; Preferred service: <strong>{top_service}</strong>
</div>
""",
    unsafe_allow_html=True,
)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(
        metric_card("Total Leads", total_leads, "All enquiries captured in the current dataset."),
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        metric_card("Today", len(today_leads), "Leads received since midnight."),
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        metric_card("Last 7 Days", len(weekly_leads), "Rolling weekly lead volume."),
        unsafe_allow_html=True,
    )
with col4:
    st.markdown(
        metric_card("Top Service", top_service, "Most frequently requested service."),
        unsafe_allow_html=True,
    )

st.markdown('<div class="section-title">Lead Trends</div>', unsafe_allow_html=True)
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    if "Service" in df.columns:
        panel_header(
            "Service Mix",
            "Compare which services are generating the highest share of inbound demand.",
        )
        service_counts = df["Service"].fillna("Unspecified").value_counts().reset_index()
        service_counts.columns = ["Service", "Count"]
        fig = go.Figure(
            go.Bar(
                x=service_counts["Service"],
                y=service_counts["Count"],
                marker=dict(
                    color=service_counts["Count"],
                    colorscale=[[0.0, "#6f5b36"], [0.45, "#b89356"], [1.0, "#e8d4a8"]],
                    line=dict(color="rgba(255,255,255,0.12)", width=1.2),
                ),
                text=service_counts["Count"],
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>Leads: %{y}<extra></extra>",
            )
        )
        apply_figure_style(fig)
        fig.update_layout(yaxis_title="Lead Count", xaxis_title=None)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Service data is not available in the current file.")

with chart_col2:
    if "Date" in df.columns:
        panel_header(
            "Demand Trend",
            "Track daily lead flow and spot growth periods or sudden drop-offs quickly.",
        )
        daily = df.groupby("Date").size().reset_index(name="Leads")
        daily["Date"] = pd.to_datetime(daily["Date"])
        fig2 = go.Figure()
        fig2.add_trace(
            go.Scatter(
                x=daily["Date"],
                y=daily["Leads"],
                mode="lines+markers",
                line=dict(color="#d7bb86", width=3),
                marker=dict(size=8, color="#f5f0e8", line=dict(color="#c9a96e", width=2)),
                fill="tozeroy",
                fillcolor="rgba(201, 169, 110, 0.14)",
                hovertemplate="%{x|%d %b %Y}<br>Leads: %{y}<extra></extra>",
            )
        )
        apply_figure_style(fig2)
        fig2.update_layout(yaxis_title="Lead Count", xaxis_title=None)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Timestamp data is not available in the current file.")

st.markdown('<div class="section-title">Lead Behavior</div>', unsafe_allow_html=True)
chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    if "Hour" in df.columns:
        panel_header(
            "Peak Hours",
            "Understand when prospects are most active so the sales response can be timed better.",
        )
        hour_counts = df.groupby("Hour").size().reset_index(name="Leads")
        fig3 = go.Figure(
            go.Scatter(
                x=hour_counts["Hour"],
                y=hour_counts["Leads"],
                mode="lines+markers",
                line=dict(color="#78d0b2", width=3, shape="spline"),
                marker=dict(size=9, color="#78d0b2", line=dict(color="#e8fff8", width=1.5)),
                fill="tozeroy",
                fillcolor="rgba(110, 197, 168, 0.14)",
                hovertemplate="%{x}:00<br>Leads: %{y}<extra></extra>",
            )
        )
        apply_figure_style(fig3)
        fig3.update_layout(
            yaxis_title="Lead Count",
            xaxis_title="Hour of Day",
            xaxis=dict(
                tickmode="array",
                tickvals=hour_counts["Hour"],
                ticktext=[f"{hour}:00" for hour in hour_counts["Hour"]],
                showgrid=False,
                zeroline=False,
                linecolor="rgba(255,255,255,0.08)",
                tickfont=dict(color="#b7ac98"),
                title_font=dict(color="#b7ac98"),
            ),
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Hourly data is not available in the current file.")

with chart_col4:
    if "Day" in df.columns:
        panel_header(
            "Weekday Performance",
            "Review which days consistently bring stronger enquiry volume across the week.",
        )
        day_order = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        day_counts = df.groupby("Day").size().reset_index(name="Leads")
        day_counts["Day"] = pd.Categorical(day_counts["Day"], categories=day_order, ordered=True)
        day_counts = day_counts.sort_values("Day")
        fig4 = go.Figure(
            go.Bar(
                x=day_counts["Day"],
                y=day_counts["Leads"],
                marker=dict(
                    color=["#7a73b8", "#857ec6", "#9189d3", "#9c95e1", "#a9a1eb", "#b8b0f2", "#c8c1fb"]
                ),
                text=day_counts["Leads"],
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>Leads: %{y}<extra></extra>",
            )
        )
        apply_figure_style(fig4)
        fig4.update_layout(yaxis_title="Lead Count", xaxis_title=None)
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("Weekday data is not available in the current file.")

st.markdown('<div class="section-title">Lead Register</div>', unsafe_allow_html=True)
filter_col1, filter_col2, filter_col3 = st.columns([2, 2, 1])
with filter_col1:
    search = st.text_input("Search by client name or phone number", "")
with filter_col2:
    if "Service" in df.columns:
        services = ["All Services"] + sorted(df["Service"].dropna().unique().tolist())
        selected_service = st.selectbox("Filter by service", services)
    else:
        selected_service = "All Services"
with filter_col3:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Refresh data"):
        st.cache_data.clear()
        st.rerun()

filtered = df.copy()
if search:
    filtered = filtered[
        filtered["Name"].astype(str).str.contains(search, case=False, na=False)
        | filtered["Phone"].astype(str).str.contains(search, na=False)
    ]
if selected_service != "All Services" and "Service" in filtered.columns:
    filtered = filtered[filtered["Service"] == selected_service]

display_cols = [
    col
    for col in ["Timestamp", "Name", "Phone", "Service", "Budget", "Message"]
    if col in filtered.columns
]

st.dataframe(
    filtered[display_cols].sort_values("Timestamp", ascending=False)
    if "Timestamp" in filtered.columns
    else filtered[display_cols],
    use_container_width=True,
    height=430,
)

st.caption(f"Showing {len(filtered)} of {len(df)} leads.")

st.markdown("---")
csv_data = filtered[display_cols].to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download filtered leads as CSV",
    data=csv_data,
    file_name=f"woodspace_leads_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv",
)
