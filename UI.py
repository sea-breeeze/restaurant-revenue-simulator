# User Interface
import pandas as pd
import streamlit as st
import plotly.express as px
from simulation import monte_carlo_simulation, run_single_simulation, save_config

st.set_page_config(page_title="Restaurant Revenue Simulator", layout="wide")

st.title('Restaurant Revenue Simulator')

days = st.slider('Days to simulate', 1, 60, 30, key="days")
customers = st.slider('Average customers per day', 10, 500, 100, key="customers")
simulations = st.slider('Monte Carlo Runs', 10, 500, 100, key="simulations")

st.sidebar.header("Save / Load Setup")

menu = {}

st.subheader("Menu Configuration")

num_items = st.number_input(
    'Number of menu items:',
    min_value=1,
    max_value=10,
    value=3,
    step=1
)

for i in range(num_items):
    st.markdown(f"### Item {i + 1}")
    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input("Name", key=f"name_{i}")
    with col2:
        price = st.number_input("Price ($)", key=f"price_{i}")
    with col3:
        percentage = st.slider("Chance %", 0, 100, 50, key=f"perc_{i}")

    if name.strip() != "":
        menu[name] = {
            "Percentage": percentage,
            "Price": price
        }
    else:
        st.caption("⚠ Item skipped — name is blank")

    st.divider()

if menu:
    total_pct = sum(v["Percentage"] for v in menu.values())
    if total_pct > 100:
        st.warning(
            f"Item chances add up to {total_pct}% — if these are meant to be a "
            f"distribution, they should sum to 100% or less."
        )

if st.sidebar.button("Save Current Setup"):
    if menu:
        save_config(menu, days, customers, simulations)
        st.sidebar.success("Saved to config.json")
    else:
        st.sidebar.error("No menu to save")

if st.button('Run Simulation'):

    if not menu:
        st.error("Please load or create a menu first.")
        st.stop()

    results = monte_carlo_simulation(days, menu, customers, simulations)

    single_run, _ = run_single_simulation(days, menu, customers)

    daily_totals = [sum(day.values()) for day in single_run.values()]
    day_labels = list(single_run.keys())

    fig2 = px.line(
        x=day_labels,
        y=daily_totals,
        markers=True,
        title="Daily Revenue Trend"
    )

    st.plotly_chart(fig2)

    avg = sum(results) / len(results)
    st.subheader("Simulation Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Average Revenue", f"${avg:,.2f}")
    col2.metric("Min Revenue", f"${min(results):,.2f}")
    col3.metric("Max Revenue", f"${max(results):,.2f}")

    st.subheader("Current Menu")

    menu_df = pd.DataFrame(menu).T.reset_index()
    menu_df.columns = ["Item", "Purchase %", "Price ($)"]
    menu_df["Price ($)"] = menu_df["Price ($)"].map("${:,.2f}".format)

    st.dataframe(menu_df, use_container_width=True)

    fig = px.histogram(
        x=results,
        nbins=20,
        labels={
            'x': 'Total revenue ($)',
            'count': 'Number of simulations',
        },
        title='Revenue Distribution'
    )

    fig.update_layout(
        template="simple_white",
        title_x=0.5
    )

    st.plotly_chart(fig)

    df = pd.DataFrame({
        "Simulation": range(1, len(results) + 1),
        "Total Revenue": results
    })

    st.download_button(
        label="Download Results",
        data=df.to_csv(index=False),
        file_name="simulation_results.csv",
        mime="text/csv"
    )
