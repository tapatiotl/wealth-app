import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Title of the app
st.title("Monte Carlo Wealth Inequality Simulator with Momentum")

# Input parameters from users
n = st.slider("Number of Individuals", 100, 5000, 1000)
w = st.number_input("Initial Wealth per Person", min_value=1.0, value=100.0)
t = st.slider("Number of Time Steps", 10, 100, 50)
luck_magnitude = st.slider("Luck Magnitude (±% Change)", 0.05, 0.5, 0.1)
momentum_window = st.slider("Momentum Window (Steps to Track)", 1, 5, 3)  # New: Number of steps to track for momentum

# Run simulation when user clicks a button
if st.button("Run Simulation"):
    # Initialize wealth as floats
    wealth = np.array([w] * n, dtype=float)
    
    # Initialize momentum history for each individual (list of last `momentum_window` changes: +1 for gain, -1 for loss, 0 for neutral)
    momentum_history = np.zeros((n, momentum_window), dtype=int)

    # Simulate wealth changes over time with momentum
    for _ in range(t):
        # Calculate momentum for each individual (sum of last `momentum_window` changes)
        momentum = np.sum(momentum_history, axis=1)
        
        # Adjust probability of gain based on momentum
        luck = np.zeros(n, dtype=int)
        for i in range(n):
            if momentum[i] == momentum_window:  # All gains (e.g., 3 gains in a 3-step window)
                luck[i] = 1 if np.random.random() < 0.7 else -1  # 70% chance of gain, 30% chance of loss
            elif momentum[i] == -momentum_window:  # All losses (e.g., 3 losses in a 3-step window)
                luck[i] = 1 if np.random.random() < 0.3 else -1  # 30% chance of gain, 70% chance of loss
            else:  # Mixed or no clear streak, use 50% chance (neutral)
                luck[i] = 1 if np.random.random() < 0.5 else -1

        # Apply wealth change
        wealth *= (1 + luck * luck_magnitude)

        # Update momentum history (shift left, add new change)
        momentum_history = np.roll(momentum_history, -1, axis=1)
        momentum_history[:, -1] = luck  # Add the latest luck (+1 or -1) to the end

    # Display statistics
    st.write(f"Initial wealth per person: {w}")
    st.write(f"Final average wealth: {np.mean(wealth):.2f}")
    st.write(f"Final median wealth: {np.median(wealth):.2f}")
    st.write(f"Final wealth inequality (standard deviation): {np.std(wealth):.2f}")
    st.write(f"Minimum final wealth: {np.min(wealth):.2f}")
    st.write(f"Maximum final wealth: {np.max(wealth):.2f}")

    # Create and display histogram of wealth distribution
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    ax1.hist(wealth, bins=30, color='skyblue', edgecolor='black')
    ax1.set_title('Wealth Distribution After Random Luck Events with Momentum')
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
    ax2.set_ylim(0, 100)
    st.pyplot(fig2)

# Add some instructions
st.write("""
    Adjust the sliders and input fields above to change the simulation parameters.
    Click 'Run Simulation' to see the wealth distribution after random luck events with momentum.
    Momentum increases the chance of continued gains or losses based on recent trends.
""")