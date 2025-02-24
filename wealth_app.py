import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Custom CSS for styling (using st.markdown with HTML)
st.markdown("""
    <style>
    .main {
        background-color: #F5F5F5; /* Light gray background */
        padding: 20px;
    }
    .title {
        color: #1E90FF; /* Deep blue for title */
        font-size: 36px;
        font-weight: bold;
        text-align: center;
    }
    .header {
        color: #2ECC71; /* Emerald green for headers */
        font-size: 24px;
    }
    .stButton>button {
        background-color: #FFD700; /* Gold for buttons */
        color: black;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
    }
    .stSlider > div > div > div {
        background-color: #E6F3FF; /* Light blue for slider track */
    }
    .stSlider > div > div > div > div {
        background-color: #2ECC71; /* Emerald green for slider handle */
    }
    </style>
""", unsafe_allow_html=True)

# Title of the app with custom styling
st.markdown('<h1 class="title">Monte Carlo Wealth Inequality Simulator with Momentum</h1>', unsafe_allow_html=True)

# Use columns for better layout
col1, col2 = st.columns(2)

with col1:
    # Input parameters from users (left column)
    n = st.slider("Number of Individuals", 100, 5000, 1000, key="n_slider")
    w = st.number_input("Initial Wealth per Person", min_value=1.0, value=100.0, key="wealth_input")
    t = st.slider("Number of Time Steps", 10, 100, 50, key="time_slider")

with col2:
    # More inputs (right column)
    luck_magnitude = st.slider("Luck Magnitude (±% Change)", 0.05, 0.5, 0.1, key="luck_slider")
    momentum_window = st.slider("Momentum Window (Steps to Track)", 1, 5, 3, key="momentum_window_slider")
    momentum_magnitude = st.slider("Momentum Magnitude (Effect on Probability, %)", 0, 40, 20, key="momentum_magnitude_slider")

# Run simulation button (centered for visual appeal)
if st.button("Run Simulation", key="run_button"):
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
                gain_prob = 0.5 + (momentum_magnitude / 100)  # e.g., 50% + 20% = 70% chance of gain
                luck[i] = 1 if np.random.random() < gain_prob else -1  # Higher gain probability
            elif momentum[i] == -momentum_window:  # All losses (e.g., 3 losses in a 3-step window)
                gain_prob = 0.5 - (momentum_magnitude / 100)  # e.g., 50% - 20% = 30% chance of gain
                luck[i] = 1 if np.random.random() < gain_prob else -1  # Lower gain probability
            else:  # Mixed or no clear streak, use 50% chance (neutral)
                luck[i] = 1 if np.random.random() < 0.5 else -1

        # Apply wealth change
        wealth *= (1 + luck * luck_magnitude)

        # Update momentum history (shift left, add new change)
        momentum_history = np.roll(momentum_history, -1, axis=1)
        momentum_history[:, -1] = luck  # Add the latest luck (+1 or -1) to the end

    # Display statistics in columns for better layout
    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<h3 class="header">Simulation Statistics</h3>', unsafe_allow_html=True)
        st.write(f"Initial wealth per person: {w}")
        st.write(f"Final average wealth: {np.mean(wealth):.2f}")
        st.write(f"Final median wealth: {np.median(wealth):.2f}")
    with col4:
        st.write(f"Final wealth inequality (standard deviation): {np.std(wealth):.2f}")
        st.write(f"Minimum final wealth: {np.min(wealth):.2f}")
        st.write(f"Maximum final wealth: {np.max(wealth):.2f}")

    # Create and display histogram of wealth distribution
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    ax1.hist(wealth, bins=30, color='skyblue', edgecolor='black')
    ax1.set_title('Wealth Distribution After Random Luck Events with Momentum', color='#1E90FF')
    ax1.set_xlabel('Wealth', color='#2ECC71')
    ax1.set_ylabel('Number of Individuals', color='#2ECC71')
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
    bars = ax2.bar(labels, wealth_percentages, color=['lightblue', 'lightgreen', 'lightcoral', 'lightyellow'])
    ax2.set_title('Percentage of Total Wealth by Quartiles', color='#1E90FF')
    ax2.set_ylabel('Percentage of Total Wealth (%)', color='#2ECC71')
    ax2.set_xlabel('Wealth Quartiles', color='#2ECC71')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 100)
    # Add value labels on top of bars for clarity
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height, f'{height:.1f}%', 
                 ha='center', va='bottom', color='black', fontweight='bold')
    st.pyplot(fig2)

# Add some instructions with custom styling
st.markdown('<h3 class="header">Instructions</h3>', unsafe_allow_html=True)
st.write("""
    Adjust the sliders and input fields above to change the simulation parameters.
    Click 'Run Simulation' to see the wealth distribution after random luck events with momentum.
    Momentum increases the chance of continued gains or losses based on recent trends, with customizable magnitude.
    Setting Momentum Magnitude to 0% removes the momentum effect (50% chance up or down regardless of streaks).
""")