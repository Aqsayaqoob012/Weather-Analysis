import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
import os
import numpy as np

API_KEY = st.secrets["API_KEY"]

st.markdown("""
<style>

            /* Top Header Remove */
header {
    background-color: transparent !important;
}
/* Animated App Background */
.stApp {
    background: linear-gradient(-45deg, #e3f2fd, #fce4ec, #e8f5e9, #fff3e0);
    background-size: 400% 400%;
    animation: gradient 12s ease infinite;
}

@keyframes gradient {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

/* Dark readable text */
h1, h2, h3, h4, h5, h6, p, div {
    color: #7D1A61;
}


.weather-card {
    border: 3px solid #7D1A2F;
    border-radius: 18px;
    padding: 20px;
    text-align: center;

    background: linear-gradient(-45deg, #FCE1E7, #E3F2FD, #E8F5E9, #FFF3E0);
    background-size: 400% 400%;
    animation: gradientMove 8s ease infinite;

    box-shadow: 0 5px 20px #7D1A2F;
    transition: 0.4s;
}

/* Hover effect 🔥 */
.weather-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 20px 40px #7D1A2F;
}

@keyframes gradientMove {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}
            

   .graph-box {
    border: 3px solid #7D1A2F;
    border-radius: 12px;
    padding: 0px; /* remove inner padding so border hugs graph */
    overflow: hidden; /* ensures graph doesn't overflow border */
    margin-bottom: 20px; /* space between graphs */
}

/* Main Heading */
.compare-heading {
    font-size: 30px;
    font-weight: bold;
    margin-top: 20px;
    color : #7D1A2F
}

/* Small Heading */
.small-heading {
    font-size: 20px;
    margin-bottom: 10px;
}

/* Rounded Year Boxes */
.year-box {
    display: flex;
    gap: 15px;
}

.year {
    background-color: #FCE1E7;
    padding: 12px 25px;
    border-radius: 25px;
    font-weight: bold;
    text-align: center;
    border: 2px solid #12080A;
    box-shadow: 2px 5px 10px #7D1A2F;
            
}
            /* Scrollable DataFrame box */
[data-testid="stDataFrameContainer"] {
    background-color: rgba(0,0,0,0);  /* fully transparent */
}
div.element-container:nth-child(n) .stDataFrame div {
    background-color: rgba(0,0,0,0);  /* table cells transparent */
}
            

/* Left-align metric text */
[data-testid="stMetric"] > div {
    display: flex !important;
    flex-direction: column !important;
    align-items: flex-start !important;
}

</style>
""", unsafe_allow_html=True)

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(page_title="Weather Dashboard", layout="wide")



cities = ["Karachi", "Lahore", "Islamabad", "Multan"]

st.title("Weather Dashboard")

# -------------------------
# CACHE (Makes app faster)
# -------------------------
@st.cache_data(ttl=3600)
def get_forecast(city):
    city = city.strip() 
    geo_url = f"https://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
    geo = requests.get(geo_url).json()

    # 🔹 Safe check
    if not geo or not isinstance(geo, list) or len(geo) == 0:
        st.warning(f"⚠️ City '{city}' not found or API returned empty data.")
        return pd.DataFrame()  # Return empty df to avoid crash

    lat = geo[0].get("lat")
    lon = geo[0].get("lon")

    forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    forecast = requests.get(forecast_url).json()

    if forecast.get("cod") != "200":
        st.warning(f"⚠️ Forecast API error for {city}")
        return pd.DataFrame()

    df = pd.DataFrame(forecast["list"])
    df["date"] = pd.to_datetime(df["dt_txt"])
    df["temp"] = df["main"].apply(lambda x: x["temp"])
    df["humidity"] = df["main"].apply(lambda x: x["humidity"])
    df["wind"] = df["wind"].apply(lambda x: x["speed"])
    df["city"] = city

    # Optional: add 'weather' column for icon/description later
    df["weather"] = df["weather"]

    return df[["date", "temp", "humidity", "wind", "city", "weather"]]




# -------------------------
# LOAD DATA
# -------------------------
data = pd.concat([get_forecast(city) for city in cities])

# -------------------------
# METRICS (Top cards)
# -------------------------
# -------------------------
# METRICS (Top cards)
# -------------------------
st.subheader(" Current Snapshot")

cols = st.columns(4)

for col, city in zip(cols, cities):
    latest = data[data["city"]==city].iloc[0]

    # ✅ Safe weather icon & description handling
    if 'weather' in latest and len(latest['weather']) > 0:
        icon_code = latest['weather'][0].get('icon', '01d')  # default sunny icon
        description = latest['weather'][0].get('description', 'N/A')
    else:
        icon_code = '01d'
        description = 'N/A'

    icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"

    card_html = f"""
    <div class="weather-card">
        <h3>{city}</h3>
        <img src="{icon_url}" width="90">
        <h2>{latest['temp']}°C</h2>
        <p>💧 Humidity: {latest['humidity']}%</p>
        <p>{description}</p>
    </div>
    """

    col.markdown(card_html, unsafe_allow_html=True)




# -------------------------
# GRAPHS
# -------------------------

# Temperature Trend
st.subheader("🌡 Temperature Trend")

fig1 = px.line(
    data,
    x="date",
    y="temp",
    color="city",
    markers=True
)

fig1.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",  # transparent
    paper_bgcolor="rgba(0,0,0,0)"  # transparent
)

st.markdown('<div class="graph-box">', unsafe_allow_html=True)
st.plotly_chart(fig1, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)


# Humidity + Wind Side by Side


col1, col2 = st.columns(2)

# -------------------------
# Humidity Comparison
# -------------------------
with col1:
    st.subheader("💧 Humidity Comparison")
    fig2 = px.line(
        data,
        x="date",
        y="humidity",
        color="city",
        markers=True  # ✅ dots on line
    )
    # Mota line aur transparent background
    fig2.update_traces(line=dict(width=4))  # ✅ line thickness
    fig2.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=50, b=20)
    )

    st.markdown('<div class="graph-box">', unsafe_allow_html=True)
    st.plotly_chart(fig2, use_container_width=True, key="humidity_line")
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# Wind Speed
# -------------------------
with col2:
    st.subheader("🌬 Wind Speed")
    fig3 = px.line(
        data,
        x="date",
        y="wind",
        color="city",
        markers=True  # ✅ dots on line
    )
    fig3.update_traces(line=dict(width=4))  # ✅ line thickness
    fig3.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=50, b=20)
    )

    st.markdown('<div class="graph-box">', unsafe_allow_html=True)
    st.plotly_chart(fig3, use_container_width=True, key="wind_line")
    st.markdown('</div>', unsafe_allow_html=True)


st.subheader("📊 Weather Overview Charts")

col1, col2 = st.columns(2)

# ------------------------- 
# 1️⃣ Pie Chart — Avg Temperature
# -------------------------
with col1:
    avg_temp = data.groupby("city")["temp"].mean().reset_index()

    fig_pie = px.pie(
        avg_temp,
        names="city",
        values="temp",
        title="🌡 Average Temperature",
        color="city",
        color_discrete_sequence=px.colors.qualitative.Set2
    )

    fig_pie.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=50, b=20)
    )

    st.markdown('<div class="graph-box">', unsafe_allow_html=True)
    st.plotly_chart(fig_pie, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------- 
# 2️⃣ Bar Chart — Avg Humidity
# -------------------------
with col2:
    avg_humidity = data.groupby("city")["humidity"].mean().reset_index()

    fig_bar = px.bar(
        avg_humidity,
        x="city",
        y="humidity",
        title="💧 Average Humidity",
        color="city",
        color_discrete_sequence=px.colors.qualitative.Set2
    )

    fig_bar.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=50, b=20)
    )

    st.markdown('<div class="graph-box">', unsafe_allow_html=True)
    st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)



st.subheader("🌡 Temp vs Humidity Scatter")

fig_scatter = px.scatter(
    data,
    x="temp",
    y="humidity",
    color="city",
    size="wind",           # wind speed ko point size me show kare
    hover_data=["date"],
    title="Temperature vs Humidity (Wind size)"
)

fig_scatter.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=20,r=20,t=50,b=20)
)

st.markdown('<div class="graph-box">', unsafe_allow_html=True)
st.plotly_chart(fig_scatter, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)



st.subheader("🌡 Stacked Temperature Trend")

fig_area = px.area(
    data,
    x="date",
    y="temp",
    color="city",
    title="Stacked Temperature Trend by City"
)

fig_area.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=20,r=20,t=50,b=20)
)

st.markdown('<div class="graph-box">', unsafe_allow_html=True)
st.plotly_chart(fig_area, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)




# Simulate wind direction for Polar chart
data["wind_dir"] = np.random.randint(0,360,len(data))

# -------------------------
# 1️⃣ Scatter Plot — Full row
# -------------------------
st.subheader("🌡 Temp vs Humidity Scatter")

fig_scatter = px.scatter(
    data,
    x="temp",
    y="humidity",
    color="city",
    size="wind",
    hover_data=["date"],
    title="Temperature vs Humidity (Wind size)"
)

fig_scatter.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=20,r=20,t=50,b=20)
)

st.markdown('<div class="graph-box">', unsafe_allow_html=True)
st.plotly_chart(fig_scatter, use_container_width=True, key="scatter_plot")  # ✅ unique key
st.markdown('</div>', unsafe_allow_html=True)


# -------------------------
# 2️⃣ Stacked Area + Polar Side by Side
# -------------------------
col1, col2 = st.columns([2,1])  # left side double width, right side smaller

# Left: Stacked Area Chart
with col1:
    st.subheader("🌡 Stacked Temperature Trend")
    fig_area = px.area(
        data,
        x="date",
        y="temp",
        color="city",
        title="Stacked Temperature Trend by City"
    )
    fig_area.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20,r=20,t=50,b=20)
    )
    st.markdown('<div class="graph-box">', unsafe_allow_html=True)
    st.plotly_chart(fig_area, use_container_width=True, key="area_plot")  # ✅ unique key
    st.markdown('</div>', unsafe_allow_html=True)

# Right: Polar Chart
with col2:
    st.subheader("🌬 Wind Speed & Direction")
    fig_polar = px.line_polar(
        data,
        r="wind",
        theta="wind_dir",
        color="city",
        line_close=True,
        title="Wind Speed vs Direction"
    )
    fig_polar.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20,r=20,t=50,b=20)
    )
    st.markdown('<div class="graph-box">', unsafe_allow_html=True)
    st.plotly_chart(fig_polar, use_container_width=True, key="polar_plot")  # ✅ unique key
    st.markdown('</div>', unsafe_allow_html=True)
