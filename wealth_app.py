import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Custom CSS for styling with the new palette and UI adjustments
st.markdown("""
    <style>
    .main {
        background-color: #FAFAFA; /* Soft White background */
        padding: 20px;
    }
    .title {
        color: #191970; /* Midnight Blue for title */
        font-size: 36px;
        font-weight: bold;
        text-align: center;
    }
    .header {
        color: #1E90FF; /* Dodger Blue for headers */
        font-size: 24px;
        text-align: center;
    }
    .stButton>button {
        background-color: #1E90FF; /* Dodger Blue for buttons */
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #87CEEB; /* Sky Blue on hover for buttons */
    }
    .stSlider > div > div > div {
        background-color: #87CEEB; /* Sky Blue for slider track */
        height: 20px; /* Increased height for better visibility */
    }
    .stSlider > div > div > div > div {
        background-color: #191970; /* Midnight Blue for slider handle (replacing orange) */
    }
    .stSlider .stSliderValue {
        color: #000000; /* Black for slider min/max values, remove background */
        background: transparent; /* Remove background from min/max values */
    }
    .stText {
        color: #000000; /* Black for text readability */
    }
    .stat-number {
        font-size: 28px;
        font-weight: bold;
        color: #1E90FF; /* Dodger Blue for emphasis */
    }
    .stat-label {
        font-size: 16px;
        color: #191970; /* Midnight Blue for labels */
    }
    </style>
""", unsafe_allow_html=True)

# Title of the app with custom styling
st.markdown('<h1 class="title">Monte Carlo Wealth Inequality Simulator with Momentum</h1>', unsafe_allow_html=True)

# Use columns for better layout
col1, col2 = st.columns(2)

with col1:
    # Input parameters from users (left column) - Number inputs for individuals and steps
    n = st.number_input("Number of Individuals", min_value=1, max_value=10000, value=1000, step=10, format="%d", key="n_input", help="Number of people in the simulation (use + or - to adjust by 10, or type a number 1–10,000).")
    w = st.number_input("Initial Wealth per Person", min_value=1.0, value=100.0, key="wealth_input", help="Starting wealth for each individual.")
    t = st.number_input("Number of Time Steps", min_value=1, max_value=250, value=50, step=5, format="%d", key="t_input", help="Number of simulation steps (use + or - to adjust by 5, or type a number 1–250).")
    probability_of_success = st.slider("Probability of Success (%)", 45, 55, 50, key="success_prob_slider", help="Baseline chance of gaining wealth per step (before momentum). 50% = neutral, >50% favors gains, <50% favors losses.")

with col2:
    # More inputs (right column) - Sliders with updated styling
    luck_magnitude = st.slider("Δ wealth per step", 0.05, 0.5, 0.1, key="luck_slider", help="Magnitude of random wealth changes per step.")
    momentum_window = st.slider("Momentum Window (Steps to Track)", 1, 5, 3, key="momentum_window_slider", help="Number of recent steps to track for momentum.")
    momentum_magnitude = st.slider("Momentum Magnitude (Effect on Probability, %)", 0, 40, 20, key="momentum_magnitude_slider", help="Sets how much recent streaks influence future outcomes. 0% = no momentum (uses Probability of Success), 40% = max effect (90% gain for lucky streaks, 10% for unlucky).")

# Run simulation button (centered)
if st.button("Run Simulation", key="run_button"):
    with st.spinner("Running simulation..."):  # Add loading animation
        # Initialize wealth as floats
        wealth = np.array([w] * n, dtype=float)
        
        # Initialize momentum history for each individual
        momentum_history = np.zeros((n, momentum_window), dtype=int)

        # Simulate wealth changes over time with momentum and probability of success
        for _ in range(t):
            # Calculate momentum for each individual
            momentum = np.sum(momentum_history, axis=1)
            
            # Adjust probability of gain based on momentum and probability of success
            luck = np.zeros(n, dtype=int)
            for i in range(n):
                if momentum[i] == momentum_window:  # All gains
                    gain_prob = min(1.0, max(0.0, 0.5 + (momentum_magnitude / 100)))  # Cap at 0%–100%
                    luck[i] = 1 if np.random.random() < gain_prob else -1
                elif momentum[i] == -momentum_window:  # All losses
                    gain_prob = min(1.0, max(0.0, 0.5 - (momentum_magnitude / 100)))  # Cap at 0%–100%
                    luck[i] = 1 if np.random.random() < gain_prob else -1
                else:  # Mixed or no clear streak, use probability of success
                    luck[i] = 1 if np.random.random() < (probability_of_success / 100) else -1

            # Apply wealth change
            wealth *= (1 + luck * luck_magnitude)

            # Update momentum history
            momentum_history = np.roll(momentum_history, -1, axis=1)
            momentum_history[:, -1] = luck

        # Display "Simulation Statistics" title centered, with a line break/spacing below
        st.markdown('<h3 class="header">Simulation Statistics</h3>', unsafe_allow_html=True)
        st.write("")  # Add a blank line for spacing

        # Display statistics in perfectly aligned columns with numbers first and bold
        col3, col4 = st.columns(2)
        with col3:
            st.markdown(f'<div class="stat-number">100.0</div><div class="stat-label">Initial wealth per person $</div>', unsafe_allow_html=True)  # Added $ icon
            st.markdown(f'<div class="stat-number">{np.mean(wealth):.2f}</div><div class="stat-label">Final average wealth $</div>', unsafe_allow_html=True)  # Added $ icon
            st.markdown(f'<div class="stat-number">{np.median(wealth):.2f}</div><div class="stat-label">Final median wealth $</div>', unsafe_allow_html=True)  # Added $ icon

        with col4:
            st.markdown(f'<div class="stat-number">{np.std(wealth):.2f}</div><div class="stat-label">Final wealth inequality (standard deviation)</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="stat-number">{np.min(wealth):.2f}</div><div class="stat-label">Minimum final wealth $</div>', unsafe_allow_html=True)  # Added $ icon
            st.markdown(f'<div class="stat-number">{np.max(wealth):.2f}</div><div class="stat-label">Maximum final wealth $</div>', unsafe_allow_html=True)  # Added $ icon

        # Create and display histogram of wealth distribution
        fig1, ax1 = plt.subplots(figsize=(12, 6))  # Larger figure size for wider bars
        ax1.hist(wealth, bins=30, color='skyblue', edgecolor='black')  # Using Sky Blue for histogram
        ax1.set_title('Wealth Distribution After Random Luck Events with Momentum', color='#1E90FF')  # Dodger Blue
        ax1.set_xlabel('Wealth', color='#191970')  # Midnight Blue
        ax1.set_ylabel('Number of Individuals', color='#191970')  # Midnight Blue
        ax1.grid(True, alpha=0.3, color='#D3D3D3')  # Cool Gray for grid
        # Add mean and median lines
        ax1.axvline(x=np.mean(wealth), color='#FF6F61', linestyle='--', label='Mean')  # Sunset Orange for mean
        ax1.axvline(x=np.median(wealth), color='#2ECC71', linestyle='--', label='Median')  # Emerald Green (placeholder, adjust if needed)
        ax1.legend()
        st.pyplot(fig1)

        # Calculate total wealth
        total_wealth = np.sum(wealth)

        # Calculate quartiles
        quartiles = np.percentile(wealth, [0, 25, 50, 75, 100])
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

        # Create and display bar chart of wealth distribution by quartiles
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        bars = ax2.bar(labels, wealth_percentages, color=['#87CEEB', '#2ECC71', '#FF6F61', '#1E90FF'])  # Sky Blue, Emerald Green, Sunset Orange, Dodger Blue
        ax2.set_title('Percentage of Total Wealth by Quartiles', color='#1E90FF')  # Dodger Blue
        ax2.set_ylabel('Percentage of Total Wealth (%)', color='#191970')  # Midnight Blue
        ax2.set_xlabel('Wealth Quartiles', color='#191970')  # Midnight Blue
        ax2.grid(True, alpha=0.3, color='#D3D3D3')  # Cool Gray for grid
        ax2.set_ylim(0, 100)
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height, f'{height:.1f}%', 
                     ha='center', va='bottom', color='black', fontweight='bold')
        st.pyplot(fig2)

# Add instructions with custom styling
st.markdown('<h3 class="header">Instructions</h3>', unsafe_allow_html=True)
st.write("""
    Adjust the inputs and sliders above to change the simulation parameters.
    Click 'Run Simulation' to see the wealth distribution after random luck events with momentum.
    Momentum increases the chance of continued gains or losses based on recent trends, with customizable magnitude.
    Probability of Success sets the baseline chance of gaining wealth, independent of momentum.
    Setting Momentum Magnitude to 0% removes the momentum effect (uses Probability of Success only).
""")