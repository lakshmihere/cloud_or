import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def show_cost_risk_multi_lambda(csv_path: str = "solutions_all.csv"):
    """Cost vs Risk plot across multiple lambda_penalty values."""
    # Load data
    df = pd.read_csv(csv_path)

    # Basic sanity check
    if "lambda_penalty" not in df.columns:
        st.error("Column 'lambda_penalty' not found in solutions_all.csv")
        st.stop()
    if "total_cost" not in df.columns or "shortfall_total" not in df.columns:
        st.error("Columns 'total_cost' and 'shortfall_total' are required.")
        st.stop()

    st.subheader("Cost vs Risk for Different λ_penalty Settings")

    # Let user choose which λ values to visualize
    lam_options = sorted(df["lambda_penalty"].unique())
    selected_lams = st.multiselect(
        "Select λ_penalty values to display",
        lam_options,
        default=lam_options,  # show all by default
    )

    if not selected_lams:
        st.info("Select at least one λ_penalty value to display.")
        return

    sub = df[df["lambda_penalty"].isin(selected_lams)]

    # Build scatter plot
    fig, ax = plt.subplots()
    for lam, grp in sub.groupby("lambda_penalty"):
        ax.scatter(
            grp["total_cost"],
            grp["shortfall_total"],
            label=f"λ = {lam}",
            alpha=0.7,
        )

    ax.set_xlabel("Total Cost (per hour)")
    ax.set_ylabel("Total Shortfall (CPU + MEM)")
    ax.set_title("Cost–Risk Trade-offs Across λ_penalty")
    ax.legend(title="λ_penalty")

    st.pyplot(fig)

    # Optional: show summary table
    st.markdown("### Scenario Summary (filtered)")
    st.dataframe(
        sub[["scenario_id", "lambda_penalty", "total_cost", "shortfall_total", "latency_excess"]]
        .sort_values(["lambda_penalty", "scenario_id"])
        .reset_index(drop=True)
    )


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
col2.metric("Avg Shortfall", f"{solutions['shortfall_total'].mean():.3f}")
col3.metric("Avg Latency Excess (ms)", f"{solutions['latency_excess'].mean():.2f}")

# --- Scenario-level view ---
st.subheader(f"Scenario {scenario_id} details")

scen = solutions[solutions["scenario_id"] == scenario_id].iloc[0]
st.write(f"**Total cost:** ${scen['total_cost']:.2f} / hr")
st.write(f"**Shortfall:** {scen['shortfall_total']:.3f}")
st.write(f"**Latency excess:** {scen['latency_excess']:.2f} ms")

# Allocation breakdown for this scenario
scen_alloc = allocations[allocations["scenario_id"] == scenario_id]
instance_counts = scen_alloc.groupby("instance_type")["assigned"].sum()

fig1, ax1 = plt.subplots()
instance_counts.plot(kind="bar", ax=ax1)
ax1.set_ylabel("Number of tasks")
ax1.set_title("Tasks per instance type")
st.pyplot(fig1)

# Distribution of Latency SLO Violations
fig, ax = plt.subplots()
ax.hist(solutions["latency_excess"], bins=20)
ax.set_xlabel("Latency Excess (ms over SLO)")
ax.set_ylabel("Number of Scenarios")
ax.set_title("Distribution of Latency SLO Violations")
st.pyplot(fig)

st.title("Risk-Aware Cloud Provisioning Dashboard")

# Existing tabs
tab_overview, tab_risk, tab_alloc, tab_tradeoff = st.tabs(
    ["Overview", "Risk (single run)", "Allocations", "Cost–Risk Tradeoff"]
)

with tab_tradeoff:
    show_cost_risk_multi_lambda("solutions_all.csv")

