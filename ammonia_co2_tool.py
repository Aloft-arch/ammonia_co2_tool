# -*- coding: utf-8 -*-
"""
Created on Wed Mar 26 14:33:08 2025

@author: vasbes
"""

# ammonia_co2_tool.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# === App title ===
st.set_page_config(page_title="Marine Fuel CO₂ Savings Calculator", layout="centered")
st.title("🌊 Marine Fuel CO₂ Savings Calculator")
st.markdown("""
Use this tool to explore how switching from fuel oil to **ammonia plus pilot fuel** impacts carbon emissions.
Just enter your **daily ammonia production** and adjust the **pilot fuel share**.
""")

# === User Inputs ===
ammonia_tons_per_day = st.number_input("Ammonia production (tons/day):", min_value=100, max_value=10000, value=4000, step=100)
pilot_share_pct = st.slider("Pilot fuel share (% of total energy):", min_value=0.0, max_value=20.0, value=7.0, step=0.5)

# === Constants ===
days_per_year = 365
pilot_share = pilot_share_pct / 100
ammonia_share = 1 - pilot_share

LHV = {
    "NH3": 18.6,
    "HFO": 40.2,
    "MGO": 42.7
}

EF = {
    "NH3_prod": 0.28,
    "HFO": 3.114,
    "MGO": 3.206,
    "HFO_upstream": 0.45,
    "MGO_upstream": 0.45
}

# === Energy Calculations ===
ammonia_kg_per_day = ammonia_tons_per_day * 1000
ammonia_energy_MJ_per_day = ammonia_kg_per_day * LHV["NH3"]
total_energy_required_MJ_per_day = ammonia_energy_MJ_per_day / ammonia_share

mgo_energy_MJ_per_day = total_energy_required_MJ_per_day * pilot_share
mgo_kg_per_day = mgo_energy_MJ_per_day / LHV["MGO"]
mgo_tons_per_year = (mgo_kg_per_day / 1000) * days_per_year
ammonia_tons_per_year = ammonia_tons_per_day * days_per_year

# === Emissions ===
co2_nh3_prod = ammonia_tons_per_year * EF["NH3_prod"]
co2_mgo_combustion = mgo_tons_per_year * EF["MGO"]
co2_mgo_upstream = mgo_tons_per_year * EF["MGO_upstream"]
total_co2_nh3_mgo = co2_nh3_prod + co2_mgo_combustion + co2_mgo_upstream

# === Baseline HFO emissions ===
hfo_energy_MJ_per_day = total_energy_required_MJ_per_day
hfo_kg_per_day = hfo_energy_MJ_per_day / LHV["HFO"]
hfo_tons_per_year = (hfo_kg_per_day / 1000) * days_per_year
co2_hfo_combustion = hfo_tons_per_year * EF["HFO"]
co2_hfo_upstream = hfo_tons_per_year * EF["HFO_upstream"]
total_co2_hfo = co2_hfo_combustion + co2_hfo_upstream

# === Results ===
co2_saved = total_co2_hfo - total_co2_nh3_mgo
co2_reduction_pct = 100 * co2_saved / total_co2_hfo

results = {
    "Ammonia Produced (t/year)": ammonia_tons_per_year,
    "Pilot Fuel Used (MGO, t/year)": round(mgo_tons_per_year, 0),
    "CO₂ from NH₃ Production (t/year)": round(co2_nh3_prod, 0),
    "CO₂ from MGO Combustion (t/year)": round(co2_mgo_combustion, 0),
    "CO₂ from MGO Upstream (t/year)": round(co2_mgo_upstream, 0),
    "Total CO₂ (NH₃ + MGO) (t/year)": round(total_co2_nh3_mgo, 0),
    "Total CO₂ (HFO baseline) (t/year)": round(total_co2_hfo, 0),
    "CO₂ Saved (t/year)": round(co2_saved, 0),
    "CO₂ Reduction (%)": round(co2_reduction_pct, 1)
}

# === Display Results ===
st.subheader("📊 Annual Emissions Summary")
st.dataframe(pd.DataFrame([results]))

# === Optional: Bar Chart ===
st.subheader("🔎 CO₂ Emissions Comparison")
emissions = pd.DataFrame({
    "Scenario": ["NH₃ + MGO", "HFO baseline"],
    "Total CO₂ (t/year)": [total_co2_nh3_mgo, total_co2_hfo]
})
st.bar_chart(emissions.set_index("Scenario"))

# === Optional: Download as Excel ===
st.subheader("📥 Export Results")
excel_df = pd.DataFrame([results])
st.download_button("Download Excel File", data=excel_df.to_csv(index=False).encode(), file_name="co2_savings_results.csv", mime="text/csv")
