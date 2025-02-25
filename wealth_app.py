import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Custom CSS for styling based on the new color palette
st.markdown("""
    <style>
    .main { background-color: #FAFAFA; padding: 20px; }
    .title { color: #191970; font-size: 36px; font-weight: bold; text-align: center; }
    .header { color: #1E90FF; font-size: 24px; text-align: center; }
    .stButton>button { background-color: #1E90FF; color: white; border-radius: 5px; padding: 10px 20px; font-size: 16px; border: none; transition: background-color 0.3s; }
    .stButton>button:hover { background-color: #87CEEB; }
    .stat-number { font-size: 28px; font-weight: bold; color: #FF6F61; }
    .stat-label { font-size: 16px; color: #191970; }
    .stSlider .st-bk { background-color: #1E90FF; }
    .stSlider .stSliderValue { color: #191970; font-size: 16px; }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="title">Monte Carlo Wealth Inequality Simulator with Momentum</h1>', unsafe_allow_html=True)

# Session State for Persistence
if "wealth_data" not in st.session_state:
    st.session_state["wealth_data"] = None

# Input Parameters
n = st.number_input("Number of Individuals", min_value=1, max_value=1000000, value=1000, step=1000, format="%d")
w = st.number_input("Initial Wealth per Person", min_value=1.0, value=100.0)
t = st.number_input("Number of Time Steps", min_value=1, max_value=1000, value=50, step=10, format="%d")

up_percentage = st.slider("Wealth Increase per Step (%)", 0.01, 0.5, 0.1, format="%.2f")
st.write(f"Current Wealth Increase: {up_percentage:.2f}")

down_percentage = st.slider("Wealth Decrease per Step (%)", 0.01, 0.5, 0.08, format="%.2f")
st.write(f"Current Wealth Decrease: {down_percentage:.2f}")

momentum_window = st.slider("Momentum Window (Steps to Track)", 1, 5, 3)
st.write(f"Tracking last {momentum_window} steps for momentum.")

momentum_magnitude = st.slider("Momentum Magnitude (Effect on Probability, %)", 0, 40, 20)
st.write(f"Momentum impact on probability: {momentum_magnitude}%")

probability_of_success = st.slider("Probability of Success (%)", 45, 55, 50)
st.write(f"Base probability of success: {probability_of_success}%")

# Run Simulation
if st.button("Run Simulation"):
    with st.spinner("Running simulation..."):
        wealth = np.full(n, w, dtype=float)
        momentum_history = np.zeros((n, momentum_window), dtype=int)
        
        for _ in range(t):
            momentum = np.sum(momentum_history, axis=1)
            gain_prob = np.full(n, probability_of_success / 100)
            gain_prob[momentum == momentum_window] = np.clip(0.5 + (momentum_magnitude / 100), 0, 1)
            gain_prob[momentum == -momentum_window] = np.clip(0.5 - (momentum_magnitude / 100), 0, 1)
            luck = (np.random.random(n) < gain_prob)
            wealth *= np.where(luck, (1 + up_percentage), (1 - down_percentage))
            momentum_history = np.roll(momentum_history, -1, axis=1)
            momentum_history[:, -1] = luck.astype(int) * 2 - 1
        
        st.session_state["wealth_data"] = wealth

# Display Results
if st.session_state["wealth_data"] is not None:
    wealth = st.session_state["wealth_data"]
    st.markdown('<h3 class="header">Simulation Statistics</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<div class='stat-number'>{np.mean(wealth):.2f}</div><div class='stat-label'>Final Average Wealth</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='stat-number'>{np.median(wealth):.2f}</div><div class='stat-label'>Final Median Wealth</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='stat-number'>{np.std(wealth):.2f}</div><div class='stat-label'>Wealth Standard Deviation</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='stat-number'>{np.min(wealth):.2f}</div><div class='stat-label'>Minimum Wealth</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='stat-number'>{np.max(wealth):.2f}</div><div class='stat-label'>Maximum Wealth</div>", unsafe_allow_html=True)
    
    # Histogram
    fig, ax = plt.subplots(figsize=(10, 5))
    bins = np.histogram_bin_edges(wealth, bins='auto')
    ax.hist(wealth, bins=bins, color='skyblue', edgecolor='black', log=True)
    ax.set_title("Wealth Distribution", fontsize=14, color='#1E90FF')
    ax.set_xlabel("Wealth")
    ax.set_ylabel("Individuals (Log Scale)")
    st.pyplot(fig)