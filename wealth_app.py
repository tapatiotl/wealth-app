import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Title of the app
st.title("Monte Carlo Wealth Inequality Simulator")

# Input parameters from users
n = st.slider("Number of Individuals", 100, 5000, 1000)
w = st.number_input("Initial Wealth per Person", min_value=1.0, value=100.0)
t = st.slider("Number of Time Steps", 10, 100, 50)
luck_magnitude = st.slider("Luck Magnitude (±% Change)", 0.05, 0.5, 0.1)

# Run simulation when user clicks a button
if st.button("Run Simulation"):
    # Initialize wealth as floats
    wealth = np.array([w] * n, dtype=float)

    # Simulate wealth changes
    for _ in range(t):
        luck = np.random.choice([1, -1], size=n)
        wealth *= (1 + luck * luck_magnitude)

    # Display statistics
    st.write(f"Initial wealth per person: {w}")
    st.write(f"Final average wealth: {np.mean(wealth):.2f}")
    st.write(f"Final median wealth: {np.median(wealth):.2f}")  # Median wealth
    st.write(f"Final wealth inequality (standard deviation): {np.std(wealth):.2f}")
    st.write(f"Minimum final wealth: {np.min(wealth):.2f}")
    st.write(f"Maximum final wealth: {np.max(wealth):.2f}")

    # Create and display histogram of wealth distribution
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    ax1.hist(wealth, bins=30, color='skyblue', edgecolor='black')
    ax1.set_title('Wealth Distribution After Random Luck Events')
    ax1.set_xlabel('Wealth')
    ax1.set_ylabel('Number of Individuals')
    ax1.grid(True, alpha=0.3)
    st.pyplot(fig1)

    # Calculate total wealth
    total_wealth = np.sum(wealth)

    # Calculate quartiles (including 0% for a complete range)
    quartiles = np.percentile(wealth, [0, 25, 50, 75, 100])  # 0%, 25%, 50%, 75%, 100%
    labels = ['0-25% (Q1)', '25-50% (Q2)', '50-75% (Q3)', '75-100% (Q4)']

    # Calculate wealth in each quartile
    wealth_by_quartile = []
    for i in range(len(quartiles) - 1):
        lower_bound = quartiles[i]
        upper_bound = quartiles[i + 1]
        quartile_wealth = np.sum(wealth[(wealth > lower_bound) & (wealth <= upper_bound)])
        wealth_by_quartile.append(quartile_wealth)

    # Calculate percentages of total wealth for each quartile
    wealth_percentages = [w / total_wealth * 100 for w in wealth_by_quartile]

    # Create and display bar chart of wealth distribution by quartiles (as percentages)
    fig2, ax2 = plt.subplots(figsize=(8, 6))
    ax2.bar(labels, wealth_percentages, color=['lightblue', 'lightgreen', 'lightcoral', 'lightyellow'])
    ax2.set_title('Percentage of Total Wealth by Quartiles')
    ax2.set_ylabel('Percentage of Total Wealth (%)')
    ax2.set_xlabel('Wealth Quartiles')
    ax2.grid(True, alpha=0.3)
    # Adjust y-axis to show percentages (0-100)
    ax2.set_ylim(0, 100)
    st.pyplot(fig2)

# Add some instructions
st.write("""
    Adjust the sliders and input fields above to change the simulation parameters.
    Click 'Run Simulation' to see the wealth distribution after random luck events.
    The app now shows the median wealth and the percentage of total wealth held by each quartile.
""")