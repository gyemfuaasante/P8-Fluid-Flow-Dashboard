"""
===============================================================================
AI-ASSISTED DEVELOPMENT DOCUMENTATION HEADER
===============================================================================

AI Tools Used:
- Google AI Studio (models/gemini-3.6-flash)
- Gemini was utilized to formulate, refine, and structure the engineering dashboard prompts and python architecture.

Three Key Prompts Used During Development:
1. Prompt 1 (Structure & UI Setup):
   "Act as a Principal Software Engineer. Create the initial Streamlit layout for a Fluid Flow & Pipe Friction Calculator with wide mode, page title 'Fluid Flow Calculator' with icon 🌊, a main title, subtitle, sidebar controls for fluid selection (Water 20°C, Light Oil, Glycerin, Custom), density, viscosity, diameter (mm), flow rate (L/s), pipe length (m), and surface roughness (mm)."

2. Prompt 2 (Engineering Mechanics & Equations):
   "Implement SI unit conversions (L/s to m³/s, mm to m) and core fluid mechanics equations: Cross-sectional area A = πD²/4, average velocity v = Q/A, Reynolds number Re = ρvD/μ, flow regime classification (Laminar Re < 2300, Transitional 2300 <= Re <= 4000, Turbulent Re > 4000). Use Darcy friction factor f = 64/Re for laminar, Swamee-Jain explicit equation f = 0.25 / [log10(ε/(3.7D) + 5.74/Re^0.9)]² for turbulent, and a defensible linear interpolation between Re = 2300 and Re = 4000 for transitional flow. Calculate Darcy-Weisbach head loss h_f = f*(L/D)*(v²/(2g)) with g = 9.81 m/s² and pressure drop ΔP = ρgh_f in kPa."

3. Prompt 3 (Validation, Visualization & Safeguards):
   "Add robust input validation with st.warning() and st.stop() to prevent division by zero, negative parameters, or log domain errors. Add an interactive Plotly chart plotting Head Loss (m) vs. Flow Rate (L/s) across a parametric range around the operating point with a red star marker for the current operating condition. Add a Pandas summary table, metric cards, and an expander section detailing engineering assumptions."

Manual Verification / Fixes Performed by Developer:
- Verified SI unit conversion math:
  * Pipe Diameter D: converted from mm to meters (D_m = D_mm / 1000.0)
  * Flow Rate Q: converted from L/s to m³/s (Q_m3s = Q_Ls / 1000.0)
  * Pipe Roughness ε: converted from mm to meters (ε_m = ε_mm / 1000.0)
  * Pressure Drop: converted from Pa to kPa (ΔP_kPa = ΔP_Pa / 1000.0)
- Verified Reynolds number equation: Re = (ρ * v * D) / μ.
- Verified Friction Factor treatment:
  * Checked that Laminar flow uses 64 / Re.
  * Checked Swamee-Jain formula logarithm base 10 argument: ε/(3.7*D) + 5.74/(Re^0.9).
  * Verified transitional regime (2300 <= Re <= 4000) employs continuous linear interpolation between f_lam(2300) and f_turb(4000, ε, D), preventing math discontinuities.
- Verified Darcy-Weisbach equation: h_f = f * (L / D) * (v² / (2 * 9.81)).
- Verified Pressure Drop equation: ΔP = ρ * g * h_f [Pa], converted to kPa.
- Verified division-by-zero safeguards: Checked D > 0, ρ > 0, μ > 0, L > 0, Q > 0, and ε >= 0 before performing calculations.
===============================================================================
"""

import math
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# -----------------------------------------------------------------------------
# 1. STREAMLIT PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Fluid Flow Calculator",
    page_icon="🌊",
    layout="wide"
)

# -----------------------------------------------------------------------------
# 2. MAIN HEADER & USER INSTRUCTIONS
# -----------------------------------------------------------------------------
st.title("🌊 Fluid Flow & Pipe Friction Calculator")
st.caption("An Interactive Engineering Tool for Pipe Hydrodynamics")

with st.expander("📌 Quick User Instructions", expanded=True):
    st.markdown("""
    1. **Configure Parameters:** Select a fluid preset or custom fluid properties, pipe dimensions, and flow rate in the sidebar on the left.
    2. **Review Hydrodynamic Results:** Inspect calculated flow velocity, Reynolds number, flow regime classification, Darcy friction factor, head loss, and pressure drop in the metric cards and Pandas results table.
    3. **Analyze Interactive Chart:** Examine the dynamic Plotly curve showing **Head Loss (m) vs. Volumetric Flow Rate (L/s)** with your current operating condition highlighted.
    """)

# -----------------------------------------------------------------------------
# 3. HELPER FUNCTIONS FOR ENGINEERING CALCULATIONS
# -----------------------------------------------------------------------------
def calculate_area(diameter_m: float) -> float:
    """Calculate pipe cross-sectional area A = π D² / 4 in m²."""
    return (math.pi * (diameter_m ** 2)) / 4.0

def calculate_velocity(flow_rate_m3s: float, area_m2: float) -> float:
    """Calculate average fluid velocity v = Q / A in m/s."""
    return flow_rate_m3s / area_m2

def calculate_reynolds_number(density: float, velocity: float, diameter_m: float, viscosity: float) -> float:
    """Calculate Reynolds number Re = (ρ * v * D) / μ."""
    return (density * velocity * diameter_m) / viscosity

def classify_flow_regime(reynolds: float) -> str:
    """Classify flow regime based on Reynolds number thresholds."""
    if reynolds < 2300:
        return "Laminar"
    elif 2300 <= reynolds <= 4000:
        return "Transitional"
    else:
        return "Turbulent"

def calculate_darcy_friction_factor(reynolds: float, roughness_m: float, diameter_m: float) -> tuple[float, str]:
    """
    Calculate Darcy friction factor 'f':
    - Laminar (Re < 2300): f = 64 / Re
    - Turbulent (Re > 4000): Swamee-Jain explicit equation
      f = 0.25 / [log10( ε / (3.7 * D) + 5.74 / (Re ^ 0.9) )]²
    - Transitional (2300 <= Re <= 4000): Defensible linear interpolation between
      f_laminar(2300) and f_turbulent(4000, ε, D) labeled as an engineering approximation.
    """
    if reynolds < 2300:
        f = 64.0 / reynolds
        return f, "Laminar Exact (64/Re)"

    # Compute turbulent Swamee-Jain friction factor for a given Re
    def swamee_jain(re_val: float) -> float:
        rel_roughness = roughness_m / (3.7 * diameter_m)
        turb_term = 5.74 / (re_val ** 0.9)
        log_arg = rel_roughness + turb_term
        if log_arg <= 0:
            return 0.02
        return 0.25 / ((math.log10(log_arg)) ** 2)

    if reynolds > 4000:
        f = swamee_jain(reynolds)
        return f, "Swamee-Jain Explicit Approximation"

    # Transitional flow regime: 2300 <= Re <= 4000
    # Linear interpolation between f at Re = 2300 (laminar limit) and Re = 4000 (turbulent limit)
    f_2300 = 64.0 / 2300.0
    f_4000 = swamee_jain(4000.0)
    
    weight = (reynolds - 2300.0) / (4000.0 - 2300.0)
    f_trans = f_2300 + weight * (f_4000 - f_2300)
    return f_trans, "Transitional Linear Interpolation (Engineering Approximation)"

def calculate_head_loss(friction_factor: float, length_m: float, diameter_m: float, velocity: float, g: float = 9.81) -> float:
    """Calculate Darcy-Weisbach head loss h_f = f * (L / D) * (v² / (2 * g)) in meters."""
    return friction_factor * (length_m / diameter_m) * ((velocity ** 2) / (2.0 * g))

def calculate_pressure_drop(density: float, head_loss_m: float, g: float = 9.81) -> float:
    """Calculate pressure drop ΔP = ρ * g * h_f in Pascals, converted to kPa."""
    delta_p_pa = density * g * head_loss_m
    return delta_p_pa / 1000.0  # kPa

# -----------------------------------------------------------------------------
# 4. SIDEBAR CONTROLS & FLUID PRESETS
# -----------------------------------------------------------------------------
st.sidebar.header("⚙️ Operating Parameters")

FLUID_PRESETS = {
    "Water 20°C": {"density": 998.2, "viscosity": 0.001002},
    "Light Oil": {"density": 880.0, "viscosity": 0.029000},
    "Glycerin": {"density": 1260.0, "viscosity": 1.490000},
    "Custom": {"density": 1000.0, "viscosity": 0.001000}
}

preset_choice = st.sidebar.selectbox(
    "Fluid Preset",
    options=list(FLUID_PRESETS.keys()),
    index=0,
    help="Select a standard fluid preset to populate density and viscosity, or choose Custom."
)

preset_data = FLUID_PRESETS[preset_choice]

density_input = st.sidebar.number_input(
    "Fluid Density ρ (kg/m³)",
    min_value=1.0,
    max_value=20000.0,
    value=float(preset_data["density"]),
    step=10.0,
    format="%.2f",
    help="Mass density of the fluid in SI units (kg/m³)."
)

viscosity_input = st.sidebar.number_input(
    "Dynamic Viscosity μ (Pa·s)",
    min_value=1e-7,
    max_value=100.0,
    value=float(preset_data["viscosity"]),
    step=0.0001,
    format="%.6f",
    help="Dynamic viscosity of the fluid in SI units (Pa·s)."
)

st.sidebar.markdown("---")
st.sidebar.subheader("📐 Pipe Geometry & Flow Conditions")

diameter_mm = st.sidebar.slider(
    "Pipe Inner Diameter D (mm)",
    min_value=5.0,
    max_value=500.0,
    value=50.0,
    step=5.0,
    help="Internal diameter of the pipe in millimeters."
)

flow_rate_ls = st.sidebar.slider(
    "Volumetric Flow Rate Q (L/s)",
    min_value=0.1,
    max_value=100.0,
    value=5.0,
    step=0.1,
    help="Volumetric flow rate in Liters per second (L/s)."
)

pipe_length_m = st.sidebar.slider(
    "Pipe Length L (m)",
    min_value=1.0,
    max_value=1000.0,
    value=50.0,
    step=5.0,
    help="Total length of the pipe section in meters."
)

roughness_mm = st.sidebar.number_input(
    "Pipe Absolute Roughness ε (mm)",
    min_value=0.0,
    max_value=10.0,
    value=0.045,
    step=0.005,
    format="%.4f",
    help="Absolute surface roughness of the inner pipe wall in mm."
)

# -----------------------------------------------------------------------------
# 5. INPUT VALIDATION & ERROR HANDLING
# -----------------------------------------------------------------------------
validation_errors = []

if density_input <= 0:
    validation_errors.append("Fluid Density must be greater than 0 kg/m³.")
if viscosity_input <= 0:
    validation_errors.append("Dynamic Viscosity must be greater than 0 Pa·s.")
if diameter_mm <= 0:
    validation_errors.append("Pipe Diameter must be greater than 0 mm.")
if flow_rate_ls <= 0:
    validation_errors.append("Volumetric Flow Rate must be greater than 0 L/s.")
if pipe_length_m <= 0:
    validation_errors.append("Pipe Length must be greater than 0 m.")
if roughness_mm < 0:
    validation_errors.append("Pipe Roughness cannot be negative.")

if validation_errors:
    for err in validation_errors:
        st.warning(f"⚠️ Validation Error: {err}")
    st.info("Please correct the operating parameters in the sidebar to run calculations.")
    st.stop()

# -----------------------------------------------------------------------------
# 6. CALCULATIONS IN SI UNITS
# -----------------------------------------------------------------------------
diameter_m = diameter_mm / 1000.0
flow_rate_m3s = flow_rate_ls / 1000.0
roughness_m = roughness_mm / 1000.0

area_m2 = calculate_area(diameter_m)
velocity_ms = calculate_velocity(flow_rate_m3s, area_m2)
reynolds_num = calculate_reynolds_number(density_input, velocity_ms, diameter_m, viscosity_input)
flow_regime = classify_flow_regime(reynolds_num)
friction_factor, friction_method = calculate_darcy_friction_factor(reynolds_num, roughness_m, diameter_m)
head_loss_m = calculate_head_loss(friction_factor, pipe_length_m, diameter_m, velocity_ms)
pressure_drop_kpa = calculate_pressure_drop(density_input, head_loss_m)

relative_roughness = roughness_m / diameter_m

# -----------------------------------------------------------------------------
# 7. DISPLAY RESULTS & METRIC CARDS
# -----------------------------------------------------------------------------
st.subheader("📊 Hydrodynamic Summary Metrics")

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric("Velocity (v)", f"{velocity_ms:.2f} m/s")

with col2:
    st.metric("Reynolds (Re)", f"{reynolds_num:,.0f}")

with col3:
    regime_emoji = "🟢" if flow_regime == "Laminar" else ("🟡" if flow_regime == "Transitional" else "🔴")
    st.metric("Flow Regime", f"{regime_emoji} {flow_regime}")

with col4:
    st.metric("Friction Factor (f)", f"{friction_factor:.4f}")

with col5:
    st.metric("Head Loss (h_f)", f"{head_loss_m:.2f} m")

with col6:
    st.metric("Pressure Drop (ΔP)", f"{pressure_drop_kpa:.2f} kPa")

st.markdown("---")

# -----------------------------------------------------------------------------
# 8. PANDAS RESULTS TABLE
# -----------------------------------------------------------------------------
st.subheader("📋 Comprehensive Results Table")

results_data = [
    {"Parameter Name": "Cross-sectional Area (A)", "Calculated Value": f"{area_m2:.6e}", "Engineering Units": "m²"},
    {"Parameter Name": "Flow Velocity (v)", "Calculated Value": f"{velocity_ms:.4f}", "Engineering Units": "m/s"},
    {"Parameter Name": "Reynolds Number (Re)", "Calculated Value": f"{reynolds_num:,.2f}", "Engineering Units": "dimensionless"},
    {"Parameter Name": "Flow Regime", "Calculated Value": flow_regime, "Engineering Units": "—"},
    {"Parameter Name": "Darcy Friction Factor (f)", "Calculated Value": f"{friction_factor:.6f}", "Engineering Units": "dimensionless"},
    {"Parameter Name": "Friction Factor Formula Used", "Calculated Value": friction_method, "Engineering Units": "—"},
    {"Parameter Name": "Relative Roughness (ε/D)", "Calculated Value": f"{relative_roughness:.6e}", "Engineering Units": "dimensionless"},
    {"Parameter Name": "Head Loss (h_f)", "Calculated Value": f"{head_loss_m:.4f}", "Engineering Units": "m"},
    {"Parameter Name": "Pressure Drop (ΔP)", "Calculated Value": f"{pressure_drop_kpa:.4f}", "Engineering Units": "kPa"},
]

df_results = pd.DataFrame(results_data)

st.dataframe(
    df_results,
    use_container_width=True,
    hide_index=True
)

st.markdown("---")

# -----------------------------------------------------------------------------
# 9. INTERACTIVE PLOTLY CHART: HEAD LOSS vs FLOW RATE
# -----------------------------------------------------------------------------
st.subheader("📈 Dynamic Head Loss Curve vs. Volumetric Flow Rate")

max_q_ls = max(flow_rate_ls * 2.0, 10.0)
min_q_ls = max(0.1, flow_rate_ls * 0.1)
q_range_ls = np.linspace(min_q_ls, max_q_ls, 120)

curve_q = []
curve_hf = []
curve_re = []
curve_regime = []
curve_f = []
curve_v = []

for q_val_ls in q_range_ls:
    q_val_m3s = q_val_ls / 1000.0
    v_val = calculate_velocity(q_val_m3s, area_m2)
    re_val = calculate_reynolds_number(density_input, v_val, diameter_m, viscosity_input)
    reg_val = classify_flow_regime(re_val)
    f_val, _ = calculate_darcy_friction_factor(re_val, roughness_m, diameter_m)
    hf_val = calculate_head_loss(f_val, pipe_length_m, diameter_m, v_val)

    curve_q.append(q_val_ls)
    curve_hf.append(hf_val)
    curve_re.append(re_val)
    curve_regime.append(reg_val)
    curve_f.append(f_val)
    curve_v.append(v_val)

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=curve_q,
    y=curve_hf,
    mode='lines',
    name='Head Loss Curve',
    line=dict(color='#1E88E5', width=3),
    hovertemplate=(
        "<b>Flow Rate (Q):</b> %{x:.2f} L/s<br>" +
        "<b>Head Loss (h_f):</b> %{y:.2f} m<br>" +
        "<b>Velocity:</b> %{customdata[0]:.2f} m/s<br>" +
        "<b>Reynolds:</b> %{customdata[1]:,.0f}<br>" +
        "<b>Regime:</b> %{customdata[2]}<br>" +
        "<b>Friction Factor (f):</b> %{customdata[3]:.4f}<extra></extra>"
    ),
    customdata=np.stack((curve_v, curve_re, curve_regime, curve_f), axis=-1)
))

fig.add_trace(go.Scatter(
    x=[flow_rate_ls],
    y=[head_loss_m],
    mode='markers',
    name='Current Operating Point',
    marker=dict(
        size=14,
        color='#D81B60',
        symbol='star',
        line=dict(color='#FFFFFF', width=1.5)
    ),
    hovertemplate=(
        "<b>CURRENT OPERATING POINT</b><br>" +
        "<b>Flow Rate (Q):</b> %{x:.2f} L/s<br>" +
        "<b>Head Loss (h_f):</b> %{y:.2f} m<br>" +
        f"<b>Reynolds:</b> {reynolds_num:,.0f}<br>" +
        f"<b>Regime:</b> {flow_regime}<extra></extra>"
    )
))

fig.update_layout(
    title=dict(text=f"Darcy-Weisbach Head Loss vs. Flow Rate (Pipe L = {pipe_length_m:.1f} m, D = {diameter_mm:.1f} mm)", x=0.0),
    xaxis_title="Volumetric Flow Rate Q (L/s)",
    yaxis_title="Head Loss h_f (m)",
    hovermode="closest",
    template="plotly_white",
    height=500,
    legend=dict(x=0.02, y=0.98, bordercolor="Gray", borderwidth=1)
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------------------------------
# 10. ENGINEERING ASSUMPTIONS & EQUATIONS EXPANDER
# -----------------------------------------------------------------------------
with st.expander("📚 Engineering Assumptions & Equations Reference"):
    st.markdown("""
    ### Hydrodynamic Model Assumptions
    1. **Steady Internal Flow:** Fluid flow parameters at any cross-section do not vary with time.
    2. **Incompressible Single-Phase Fluid:** Constant fluid density ($\rho$) and dynamic viscosity ($\mu$).
    3. **Circular Cross-Section:** Cylindrical geometry with uniform inner diameter $D$.
    4. **Fully Developed Flow:** Darcy-Weisbach friction factor models fully developed turbulent or laminar velocity profiles.
    5. **Elevation Difference:** Negligible elevation change ($\Delta z = 0$) for pressure drop ($\Delta P = \rho g h_f$).
    6. **Minor Losses Excluded:** Straight pipe friction losses; minor fitting losses excluded.
    """)

st.markdown("---")
st.caption("Project 8 — Vibe Coding Mini-App: Deployed Engineering Dashboard | Developed with Google AI Studio")
