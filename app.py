import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load precomputed results
solutions = pd.read_csv("solutions.csv")
allocations = pd.read_csv("allocations.csv")

st.title("Risk-Aware Cloud Provisioning – Scenario Explorer")

# --- Sidebar controls ---
st.sidebar.header("Controls")
scenario_id = st.sidebar.slider("Scenario", 
                                int(solutions["scenario_id"].min()),
                                int(solutions["scenario_id"].max()),
                                int(solutions["scenario_id"].min()))

metric = st.sidebar.selectbox(
    "Metric to highlight",
    ["total_cost", "shortfall", "latency_excess"]
)

# --- Overview KPIs ---
st.subheader("Overall KPIs (across all scenarios)")
col1, col2, col3 = st.columns(3)
col1.metric("Avg Cost", f"${solutions['total_cost'].mean():.2f}/hr")
col2.metric("Avg Shortfall", f"{solutions['shortfall'].mean():.3f}")
col3.metric("Avg Latency Excess (ms)", f"{solutions['latency_excess'].mean():.2f}")

# --- Scenario-level view ---
st.subheader(f"Scenario {scenario_id} details")

scen = solutions[solutions["scenario_id"] == scenario_id].iloc[0]
st.write(f"**Total cost:** ${scen['total_cost']:.2f} / hr")
st.write(f"**Shortfall:** {scen['shortfall']:.3f}")
st.write(f"**Latency excess:** {scen['latency_excess']:.2f} ms")

# Allocation breakdown for this scenario
scen_alloc = allocations[allocations["scenario_id"] == scenario_id]
instance_counts = scen_alloc.groupby("instance_type")["assigned"].sum()

fig1, ax1 = plt.subplots()
instance_counts.plot(kind="bar", ax=ax1)
ax1.set_ylabel("Number of tasks")
ax1.set_title("Tasks per instance type")
st.pyplot(fig1)

# --- Cost vs Shortfall Scatter ---
st.subheader("Cost vs Risk (all scenarios)")
fig2, ax2 = plt.subplots()
ax2.scatter(solutions["total_cost"], solutions["shortfall"])
ax2.set_xlabel("Total cost")
ax2.set_ylabel("Shortfall")
st.pyplot(fig2)
