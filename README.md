# 🌊 Fluid Flow & Pipe Friction Calculator

## Project Description
The **Fluid Flow & Pipe Friction Calculator** is an interactive, web-based engineering dashboard designed for undergraduate engineering students and fluid dynamics practitioners to evaluate internal pipe flow hydrodynamics. By converting input operating conditions into SI units, the application calculates cross-sectional pipe area, average fluid velocity, Reynolds number, flow-regime classification, Darcy friction factor (via exact laminar formulation, Swamee-Jain explicit turbulent approximation, and defensible transitional interpolation), Darcy-Weisbach head loss, and total pressure drop. An interactive Plotly visualization dynamically illustrates head loss as a function of volumetric flow rate, overlaying the user's specific operating point to assist in hydrodynamic pipe design and analysis.

---

## 🚀 Features
* **Interactive Operating Controls:** Sidebar selectors for standard fluid presets (Water 20°C, Light Oil, Glycerin, Custom) and sliders for pipe diameter, flow rate, pipe length, and wall roughness.
* **Reynolds Number Calculation:** Evaluates inertial to viscous force ratios to accurately classify flow into Laminar, Transitional, or Turbulent regimes.
* **Darcy Friction Factor Modeling:** Employs $f = 64 / \text{Re}$ for laminar flow, Swamee-Jain explicit equation for turbulent flow, and a linear transition model for $2300 \le \text{Re} \le 4000$.
* **Darcy-Weisbach Head Loss & Pressure Drop:** Computes frictional head loss ($h_f$) in meters and converts pressure drop ($\Delta P$) to kilopascals (kPa).
* **Comprehensive Results Table:** Formatted Pandas DataFrame displaying calculated parameters with explicit engineering units and formula references.
* **Dynamic Plotly Visualization:** Interactive $h_f$ vs. $Q$ curve with hover inspection metrics and an highlighted marker indicating the current operating point.
* **Input Validation & Error Safeguards:** Proactively catches division by zero, non-positive dimensions, and invalid log arguments, presenting user-friendly Streamlit warnings without code tracebacks.
* **Engineering Assumptions Expander:** Transparent documentation of physical fluid assumptions and mathematical formulas.

---

## 🧮 Engineering Equations

1. **Cross-Sectional Pipe Area:**
   $$A = \frac{\pi D^2}{4} \quad [\text{m}^2]$$

2. **Average Fluid Velocity:**
   $$v = \frac{Q}{A} \quad [\text{m/s}]$$

3. **Reynolds Number:**
   $$\text{Re} = \frac{\rho v D}{\mu} \quad [\text{dimensionless}]$$

4. **Flow Regime Classification:**
   * Laminar: $\text{Re} < 2300$
   * Transitional: $2300 \le \text{Re} \le 4000$
   * Turbulent: $\text{Re} > 4000$

5. **Darcy Friction Factor ($f$):**
   * Laminar: $f = \frac{64}{\text{Re}}$
   * Turbulent (Swamee-Jain Explicit):
     $$f = \frac{0.25}{\left[ \log_{10}\left( \frac{\varepsilon}{3.7D} + \frac{5.74}{\text{Re}^{0.9}} \right) \right]^2}$$
   * Transitional: Linear interpolation between $f_{\text{lam}}(2300)$ and $f_{\text{turb}}(4000, \varepsilon, D)$ as an engineering approximation.

6. **Darcy-Weisbach Head Loss:**
   $$h_f = f \cdot \left(\frac{L}{D}\right) \cdot \left(\frac{v^2}{2g}\right) \quad [\text{m}] \quad (g = 9.81\text{ m/s}^2)$$

7. **Pressure Drop:**
   $$\Delta P = \rho g h_f \quad [\text{Pa}] \rightarrow \Delta P_{\text{kPa}} = \frac{\Delta P}{1000} \quad [\text{kPa}]$$

---

## 🛠️ Technologies
* **Python** (3.10+)
* **Streamlit** (UI Framework)
* **Pandas** (Data Structuring)
* **NumPy** (Numerical Processing)
* **Plotly** (Interactive Graphics)
* **Git / GitHub** (Version Control & Deployment)

---

## 💻 Running Locally

To run this engineering dashboard locally on your machine:

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/<your-username>/P8-Fluid-Flow-Dashboard.git
   cd P8-Fluid-Flow-Dashboard
   ```

2. **Install Dependencies:**
   Ensure Python 3.10 or higher is installed, then run:
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the Streamlit Application:**
   ```bash
   streamlit run app.py
   ```
   The application will open automatically in your browser at `http://localhost:8501`.

---

## 🌐 GitHub Repository & Live App Links

* **GitHub Repository:** [https://github.com/<your-username>/P8-Fluid-Flow-Dashboard](https://github.com/<your-username>/P8-Fluid-Flow-Dashboard) *(Placeholder - update with your actual repository URL)*
* **Live Application URL:** [https://<your-app-name>.streamlit.app](https://<your-app-name>.streamlit.app) *(Placeholder - update with your Streamlit Community Cloud URL after deployment)*

---

## 🎓 Course Context
This application was developed as part of:
**Project 8 — Vibe Coding Mini-App: Deployed Engineering Dashboard**
*(University Engineering Assignment)*
