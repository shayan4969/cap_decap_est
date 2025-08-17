import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# -------------------------------
# Capacitor library (Murata/TDK sample)
# -------------------------------
capacitor_library = [
    {"value": "0.1 µF", "C": 0.1e-6, "ESR": 0.02, "ESL": 0.5e-9, "pkg": "0402", "V": 25},
    {"value": "0.47 µF", "C": 0.47e-6, "ESR": 0.015, "ESL": 0.6e-9, "pkg": "0402", "V": 16},
    {"value": "1 µF", "C": 1e-6, "ESR": 0.01, "ESL": 0.7e-9, "pkg": "0402", "V": 16},
    {"value": "4.7 µF", "C": 4.7e-6, "ESR": 0.005, "ESL": 0.8e-9, "pkg": "0603", "V": 10},
    {"value": "10 µF", "C": 10e-6, "ESR": 0.003, "ESL": 1.0e-9, "pkg": "0603", "V": 6.3},
]

# -------------------------------
# Calculation function
# -------------------------------
def calculate_decaps(voltage, current, ripple, step_ratio, freq_points):
    ΔV = voltage * ripple
    ΔI = current * step_ratio
    Z_target = ΔV / ΔI

    results = []
    for f in freq_points:
        C_required = 1 / (2 * np.pi * f * Z_target)
        # Pick closest from library
        best = min(capacitor_library, key=lambda c: abs(c["C"] - C_required))
        qty = int(np.ceil(C_required / best["C"]))
        results.append({
            "Frequency": f,
            "Z_target (Ω)": Z_target,
            "C_required (µF)": C_required * 1e6,
            "Selected Cap": best["value"],
            "Pkg": best["pkg"],
            "Qty": qty,
            "Reason": f"Matches target impedance at {f/1e6:.1f} MHz"
        })
    return pd.DataFrame(results)

# -------------------------------
# Streamlit App
# -------------------------------
st.title("Decoupling Capacitor Estimator")

V = st.number_input("Rail Voltage (V)", 0.5, 5.0, 1.0)
I = st.number_input("Max Current (A)", 0.1, 10.0, 2.0)
ripple = st.slider("Allowed Ripple (%)", 1, 10, 5) / 100
step_ratio = st.slider("Step Current Ratio", 0.1, 1.0, 0.5)
freq_points = [0.5e6, 5e6, 50e6]

if st.button("Calculate"):
    df = calculate_decaps(V, I, ripple, step_ratio, freq_points)
    st.dataframe(df)

    # Plot
    fig, ax = plt.subplots()
    ax.semilogx(df["Frequency"], df["Z_target (Ω)"], 'r--', label="Target Z")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Impedance (Ω)")
    ax.legend()
    st.pyplot(fig)
