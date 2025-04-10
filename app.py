
import streamlit as st
import pandas as pd
import altair as alt 

def forecast_sfd_wastewater(SFD_0, growth_rate, gpd_per_sfd, years, trigger_threshold=2.78):
    forecast = []
    sfd = SFD_0
    trigger_year = None

    for t in range(1, years + 1):
        sfd *= (1 + growth_rate)
        gpd = sfd * gpd_per_sfd
        mgd = gpd / 1_000_000
        year = 2023 + t
        forecast.append({
            'Year': year,
            'SFD_Estimate': round(sfd, 2),
            'Wastewater_MGD': round(mgd, 3)
        })
        if mgd >= trigger_threshold and not trigger_year:
            trigger_year = year

    return pd.DataFrame(forecast), trigger_year

st.set_page_config(page_title="LCSD Wastewater Forecast", layout="wide")
st.title("💧 LCSD Wastewater Forecast Tool")

st.sidebar.header("🔧 Input Parameters")
SFD_0 = st.sidebar.number_input("Starting SFD (2023)", value=14417)
growth_rate = st.sidebar.slider("Annual Growth Rate (%)", 0.0, 5.0, 0.92, step=0.01) / 100
years = st.sidebar.slider("Forecast Horizon (Years)", 10, 100, 60)
trigger_threshold = st.sidebar.number_input("Trigger Threshold (MGD)", value=2.78)

st.sidebar.markdown("### 💧 Gallons per SFD per Day (Scenario)")
gpd_option = st.sidebar.radio("Choose a Scenario:", 
                              ["Conservative", "Moderate", "Aggressive", "Custom"])

if gpd_option == "Conservative":
    gpd_per_sfd = 114
elif gpd_option == "Moderate":
    gpd_per_sfd = 157
elif gpd_option == "Aggressive":
    gpd_per_sfd = 180
else:
    gpd_per_sfd = st.sidebar.number_input("Enter Custom GPD per SFD:", value=157)

st.sidebar.markdown(f"**Selected GPD per SFD:** `{gpd_per_sfd}`")

results_df, trigger_year = forecast_sfd_wastewater(SFD_0, growth_rate, gpd_per_sfd, years, trigger_threshold)

# 🔧 Convert Year to string to prevent comma formatting in Altair
results_df["Year"] = results_df["Year"].astype(str)

# Chart
st.subheader("📊 Wastewater Forecast (MGD)")
chart = alt.Chart(results_df).mark_line().encode(
    x=alt.X('Year:O', axis=alt.Axis(format='d', title='Year')),  # format='d' removes the comma
    y=alt.Y('Wastewater_MGD', title='Wastewater (MGD)')
).properties(
    width=800,
    height=400
)

st.altair_chart(chart, use_container_width=True)

st.subheader("📄 Forecast Table")
st.dataframe(results_df)

st.markdown("---")
if trigger_year:
    st.warning(f"🚨 Projected to reach or exceed {trigger_threshold} MGD in **{trigger_year}**.")
else:
    st.success(f"✅ Not projected to reach {trigger_threshold} MGD within {years} years.")
