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
    st.write(f"Final median wealth: {np.median(wealth):.2f}")  # New: Median wealth
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

    # Create and display quartile-based graph
    quartiles = np.percentile(wealth, [25, 50, 75, 100])  # Calculate quartiles
    labels = ['0-25% (Q1)', '25-50% (Q2)', '50-75% (Q3)', '75-100% (Q4)']
    counts, _ = np.histogram(wealth, bins=quartiles)
    
    fig2, ax2 = plt.subplots(figsize=(8, 6))
    ax2.bar(labels, counts, color=['lightblue', 'lightgreen', 'lightcoral', 'lightyellow'])
    ax2.set_title('Wealth Distribution by Quartiles')
    ax2.set_ylabel('Number of Individuals')
    ax2.set_xlabel('Wealth Quartiles')
    ax2.grid(True, alpha=0.3)
    st.pyplot(fig2)

# Add some instructions
st.write("""
    Adjust the sliders and input fields above to change the simulation parameters.
    Click 'Run Simulation' to see the wealth distribution after random luck events.
    The app now shows the median wealth and a quartile-based distribution of wealth.
""")