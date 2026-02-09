from vega_datasets import data
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

df = data.seattle_weather()
print(df.head())



# Convert 'date' to datetime
df['date'] = pd.to_datetime(df['date'])

# Filter for year 2012 (replace 2012 with 2025 if you have that data)
year = 2012
df_year = df[df['date'].dt.year == year]

# Compute summary metrics
max_temp = df_year['temp_max'].max()
min_temp = df_year['temp_min'].min()
max_precip = df_year['precipitation'].max()
min_precip = df_year['precipitation'].min()
max_wind = df_year['wind'].max()
min_wind = df_year['wind'].min()
most_common_weather = df_year['weather'].mode()[0]
least_common_weather = df_year['weather'].value_counts().idxmin()

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

/* Animated Metric Cards */
[data-testid="stMetric"] {
    border: 2px solid #12080A;
    border-radius: 12px;
    padding: 12px;
    box-shadow: 2px 5px 10px #7D1A2F;

    background: linear-gradient(-45deg, #FCE1E7, #E3F2FD, #E8F5E9, #FFF3E0);
    background-size: 300% 300%;
    animation: metricBG 6s ease infinite;
}

@keyframes metricBG {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
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

</style>
""", unsafe_allow_html=True)



# -------- Your UI --------
st.title("Weather Data Analysis")
st.header(f"{year} Summary")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Max Temperature (°C)", max_temp)
col2.metric("Min Temperature (°C)", min_temp)
col3.metric("Max Precipitation (mm)", max_precip)
col4.metric("Min Precipitation (mm)", min_precip)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Max Wind (km/h)", max_wind)
col2.metric("Min Wind (km/h)", min_wind)
col3.metric("Most Common Weather", most_common_weather)
col4.metric("Least Common Weather", least_common_weather)


# ---------- Headings ----------
st.markdown('<div class="compare-heading">Compare Different Years</div>', unsafe_allow_html=True)

st.markdown('<div class="small-heading">Years to Compare</div>', unsafe_allow_html=True)


# ---------- Rounded Years Box ----------
st.markdown("""
<div class="year-box">
    <div class="year">2012</div>
    <div class="year">2013</div>
    <div class="year">2014</div>
    <div class="year">2015</div>
</div>
""", unsafe_allow_html=True)



 #Convert date
df['date'] = pd.to_datetime(df['date'])
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.strftime('%b')

# Monthly average temperature
df = df.drop_duplicates()  # duplicate rows remove
monthly_temp = df.groupby(['year','month'])['temp_max'].mean().unstack(0)

# Fix months order
months_order = ["Jan","Feb","Mar","Apr","May","Jun",
                "Jul","Aug","Sep","Oct","Nov","Dec"]
monthly_temp = monthly_temp.reindex(months_order)

# -------- Plot --------
st.markdown('<div class="compare-heading">Temperature</div>', unsafe_allow_html=True)
fig, ax = plt.subplots(figsize=(10,5))

for year in monthly_temp.columns:
    ax.plot(monthly_temp.index, monthly_temp[year], marker='o', label=year)

# Transparent background
fig.patch.set_alpha(0)  # Figure background
ax.set_facecolor("none")  # Axes background transparent

# Labels & grid
ax.set_xlabel("Months")
ax.set_ylabel("Temperature (°C)")
ax.set_title("Temperature Comparison Across Years")
ax.grid(True, alpha=0.3)

# Legend
ax.legend(title="Years")

# Top margin (gap) for Streamlit
st.markdown("<div style='margin-top: 30px'></div>", unsafe_allow_html=True)

st.pyplot(fig)


# Remove duplicates if any
df = df.drop_duplicates()

# Count of each weather type
weather_counts = df['weather'].value_counts()

colors = {
    'drizzle': '#4DB6AC',   # teal
    'fog': '#90A4AE',       # steel grey
    'rain': '#1E88E5',      # bright blue
    'snow': '#81D4FA',      # light sky blue
    'sunny': "#E8E40D",     # golden yellow
    'cloudy': "#F11EB6"     # magenta/pink
}

# Map colors for only available weather types
color_list = [colors[w] if w in colors else "#E8E40D" for w in weather_counts.index]

# ---------- Plot Pie Chart ----------
st.markdown('<div class="compare-heading">Weather Distribution</div>', unsafe_allow_html=True)
fig, ax = plt.subplots(figsize=(6,6))

# Transparent background
fig.patch.set_alpha(0)
ax.set_facecolor("none")

# Pie chart
wedges, texts, autotexts = ax.pie(
    weather_counts, 
    labels=weather_counts.index,
    autopct='%1.1f%%',
    startangle=90,
    colors=color_list,
    wedgeprops={'edgecolor':'black','linewidth':1.2}
)

# Improve text visibility
for t in texts + autotexts:
    t.set_color('black')
    t.set_fontsize(10)


# Legend outside on right
ax.legend(
    wedges,
    weather_counts.index,
    title="Weather Type",
    loc="center left",
    bbox_to_anchor=(1,0,0.5,1)
)

st.pyplot(fig)


# ---------- 1) Line Graph: Average Wind over Past Two Weeks ----------
# Sample: last 14 days data

# ---------- Create month_day column ----------
df['month_day'] = df['date'].dt.strftime('%b %d')  # e.g., Jan 01, Mar 01

# ---------- Define years to show ----------
years_to_show = [2012, 2013, 2014, 2015]

# ---------- Colors for each year ----------
year_colors = {
    2012: '#4DB6AC',  # teal
    2013: '#1E88E5',  # blue
    2014: '#FFD700',  # yellow
    2015: '#F11EB6'   # pink/magenta
}

# ---------- Sample X-axis points (specific dates) ----------
x_dates = ['Jan 01', 'Mar 01', 'May 01', 'Jul 01', 'Sep 01', 'Nov 01']

st.markdown('<div class="compare-heading">Wind</div>', unsafe_allow_html=True)
fig, ax = plt.subplots(figsize=(10,5))
fig.patch.set_alpha(0)
ax.set_facecolor("none")

# Plot lines for each year
for year in years_to_show:
    df_year = df[df['year'] == year]
    
    # Select only x_dates
    df_year = df_year[df_year['month_day'].isin(x_dates)]
    
    # Sort by date
    df_year = df_year.sort_values('date')
    
    # Plot
    ax.plot(df_year['month_day'], df_year['wind'], marker='o', label=str(year), color=year_colors[year])

# Labels and grid
ax.set_xlabel("Date")
ax.set_ylabel("Wind (km/h)")
ax.set_title("Wind Comparison Across Years")
ax.grid(True, alpha=0.3)
ax.legend(title="Year")

st.markdown("<div style='margin-top:30px'></div>", unsafe_allow_html=True)
st.pyplot(fig)


# ---------- 2) Bar Chart: Monthly Precipitation per Year ----------

# ---------- Monthly precipitation per year ----------
monthly_precip = df.groupby(['month','year'])['precipitation'].sum().unstack(1)

# Fix month order
months_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
monthly_precip = monthly_precip.reindex(months_order)

# ---------- Colors per year ----------
year_colors = {
     2012: '#76C7C0',  # turquoise
    2013: "#E2756B",  # coral / reddish
    2014: "#E59A29",  # golden yellow
    2015: "#9F7AAF"   # purple
}

# ---------- Plot ----------

st.markdown('<div class="compare-heading">Precipitation</div>', unsafe_allow_html=True)
fig, ax = plt.subplots(figsize=(12,6))
fig.patch.set_alpha(0)
ax.set_facecolor("none")

bottom = [0]*len(months_order)  # start from 0 for stacking

for year in monthly_precip.columns:
    ax.bar(months_order, monthly_precip[year], bottom=bottom, color=year_colors[year], label=str(year))
    # Update bottom for next stack
    bottom = [i+j for i,j in zip(bottom, monthly_precip[year])]

ax.set_xlabel("Months")
ax.set_ylabel("Precipitation (mm)")
ax.set_title("Monthly Precipitation per Year (Stacked)")
ax.legend(title="Year")
ax.grid(True, alpha=0.3)

st.pyplot(fig)



# ---------- Monthly counts per weather ----------
weather_types = ['drizzle', 'fog', 'rain', 'snow' , 'sun']  # select types to show
monthly_weather = df.groupby(['month','weather']).size().unstack(fill_value=0)
monthly_weather = monthly_weather[weather_types]  # only selected types

# Fix month order
months_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
monthly_weather = monthly_weather.reindex(months_order)

# ---------- Colors for each weather ----------
weather_colors = {
    'drizzle': '#76C7C0',  # turquoise
    'fog':     "#9F7AAF" ,  # purple
    'rain': "#E59A29",     # blue
    'snow': '#FFD700' ,    # yellow
    'sun' : "#E2756B"
}

# ---------- Plot ----------

st.markdown('<div class="compare-heading">Monthly Weather Breakdown</div>', unsafe_allow_html=True)
fig, ax = plt.subplots(figsize=(12,6))
fig.patch.set_alpha(0)
ax.set_facecolor("none")

bottom = [0]*len(months_order)

for weather in weather_types:
    ax.bar(months_order, monthly_weather[weather], bottom=bottom, color=weather_colors[weather], label=weather)
    # Update bottom for stacking
    bottom = [i+j for i,j in zip(bottom, monthly_weather[weather])]

ax.set_xlabel("Months")
ax.set_ylabel("Number of Days")
ax.set_title("Monthly Weather Breakdown")
ax.legend(title="Weather Type")
ax.grid(True, alpha=0.3)

st.pyplot(fig)



# ---------- Convert DataFrame to HTML ----------
table_html = df.to_html(index=False)
st.markdown('<div class="compare-heading">Raw Data</div>', unsafe_allow_html=True)
# ---------- CSS + HTML for scrollable transparent box ----------
st.markdown(f"""
<div style="height:400px; overflow-y:scroll; overflow-x:hidden; background: rgba(0,0,0,0); padding:10px; border-radius:10px;">
{table_html}
</div>
<style>
table {{
    width: 100%;
    border-collapse: collapse;
    table-layout: fixed;  /* ensures table fits container width */
    background: rgba(255,255,255,0.1);  /* slightly transparent white */
}}
th, td {{
    border: 1px solid #ccc;
    padding: 6px;
    text-align: center;
    word-wrap: break-word;  /* long text wraps inside cell */
}}
th {{
    background-color: rgba(255,255,255,0.2);
}}
</style>
""", unsafe_allow_html=True)