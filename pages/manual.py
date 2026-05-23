import urllib.parse

import streamlit as st

st.set_page_config(
    page_title="User Manual — MBE Tool",
    page_icon="📖",
    layout="wide",
)

BASE_URL = "/"


def _build_url(params: dict) -> str:
    return BASE_URL + "?" + urllib.parse.urlencode(params)


def _example_button(label: str, params: dict):
    url = _build_url(params)
    st.markdown(
        f'<a href="{url}" target="_self" style="display:inline-block;'
        f"padding:0.5em 1em;background:#1f77b4;color:white;"
        f'text-decoration:none;border-radius:6px;font-weight:bold;">'
        f"{label}</a>",
        unsafe_allow_html=True,
    )


def _pdf_button(label: str, path: str):
    with open(path, "rb") as f:
        st.download_button(
            label=label,
            data=f,
            file_name=path.split("/")[-1],
            mime="application/pdf",
        )


st.title("MBE Calculator — User Manual")
st.caption("A beginner-friendly guide to the Material Balance Equation solver.")

st.markdown("---")

# ── 0. Front Matter ─────────────────────────────────────────────────────────

st.header("About This Tool")

st.markdown("""
This tool solves the **Material Balance Equation (MBE)** — a formula petroleum
engineers use to figure out what's happening inside an oil or gas reservoir.

**Think of it like a bank account:**
- You know how much came out (production)
- You know the interest rates (fluid expansion)
- You might know about deposits (water influx)
- The tool tells you the original balance (oil or gas in place)

You don't need to be an engineer to use it. Pick a scenario, enter the numbers,
and the calculator handles the math. The sections below walk you through every
feature with real examples from the textbooks.
""")

st.header("Based On These Textbooks")

st.markdown("""
The calculator implements the equations from four reference chapters.
Download them below — each example in this manual comes from these pages.
""")

col_a, col_b = st.columns(2)

with col_a:
    _pdf_button(
        "Chapter 3 — Fundamentals of Reservoir Eng. (Dake)",
        "Chapter-3-Fundamentals-of-Reservoir-Engineering.pdf",
    )
    _pdf_button(
        "Chapter 11 — Reservoir Eng. Handbook (MBE)",
        "Chapter-11-Reservoir-Engineering-Handbook-1.pdf",
    )

with col_b:
    _pdf_button(
        "Chapter 12 — Reservoir Eng. Handbook (Prediction)",
        "Chapter-12-Reservoir-Engineering-Handbook.pdf",
    )
    _pdf_button(
        "Chapter 13 — Reservoir Eng. Handbook (Gas)",
        "Chapter-13-Reservoir-Engineering-Handbook.pdf",
    )

with st.expander("What's in each chapter?"):
    st.markdown("""
    | Chapter | What it covers | Why you'd look at it |
    |---|---|---|
    | **Ch 3 (Dake)** | MBE theory, drive mechanisms (solution gas, gas cap, water, compaction), Havlena-Odeh straight lines | The theoretical foundation. Best read first |
    | **Ch 11 (Handbook)** | All 6 Havlena-Odeh cases, water influx models, worked examples 11-3, 11-4, 11-5 | The main reference. Most of the calculator is built on this chapter |
    | **Ch 12 (Handbook)** | Predicting future performance (Tracy's method), saturation tracking | Use this to forecast how the reservoir will behave |
    | **Ch 13 (Handbook)** | Gas reservoir MBE, p/Z plots, abnormally pressured gas, tight gas | Reference for gas-specific analysis |
    """)

st.markdown("---")


# ── 1. What Is The MBE? ─────────────────────────────────────────────────────

st.header("1. What Is The Material Balance Equation?")

st.markdown(r"""
The Material Balance Equation is a **conservation law** — a fancy way of saying
what comes out must be balanced by what expands or flows in.

In a reservoir, there are four things that can happen when you produce oil:

| Mechanism | What happens | Analogy |
|---|---|---|
| **Solution Gas Drive** | Oil expands and gas bubbles out as pressure drops | Opening a soda bottle — gas pushes liquid out |
| **Gas Cap Drive** | A gas cap on top of the oil expands and pushes oil down | A balloon pressing on water |
| **Water Drive** | An underground lake (aquifer) pushes water into the reservoir | A sponge being squeezed from below |
| **Rock & Water Expansion** | The rock itself compresses slightly and helps push oil out | Squeezing a wet sponge |

The MBE combines all four mechanisms into one equation. You tell it which ones
are active in your reservoir, enter the numbers, and it solves for the unknown.

If this sounds complicated — don't worry. The examples in this manual walk you
through every click, from the first number to the final answer.
""")

st.markdown("---")


# ── 2. Quick Start ────────────────────────────────────────────────────────

st.header("2. Quick Start")

st.markdown(r"""
Using the calculator takes three steps:

### Step 1: Set up (sidebar)
Open the app. The sidebar on the left is your control panel:
1. **Fluid Type** — Oil or Gas (most examples use oil)
2. **Target Variable** — What do you want to find out? Pick N (oil in place),
   We (water influx), m (gas cap size), or deltaP (pressure drop)
3. **Reservoir State** — Saturated (below bubble point) or Unsaturated (above)
4. **Drive Mechanisms** — Check which forces are active in your reservoir

The sidebar automatically hides variables you don't need. No clutter.

### Step 2: Enter numbers
Type your known values into the input boxes below the sidebar. The app shows
only the variables it needs — everything else is greyed out or hidden.

For time-varying data (production at different pressures), expand the
**"Time-Series Data"** section and enter one row per time step.

### Step 3: Click Calculate
Hit the blue **Calculate** button. The results appear below in a clean layout:
- The answer is shown in big blue text
- Key numbers appear in metric cards
- Details are hidden behind expanders — click them when you want to dig deeper
""")

st.markdown("---")


# ── 3. The Interface ────────────────────────────────────────────────────────

st.header("3. The Interface")

st.subheader("Sidebar")
st.markdown("""
**Fluid Type**
: Choose Oil or Gas. Gas reservoirs are simpler — fewer variables, fewer options.

**Target Variable**
: The single number you want to calculate. Options depend on fluid type:
- N (oil in place) — How much oil was originally underground
- We (water influx) — How much water has pushed in
- m (gas cap ratio) — Size of the gas cap relative to the oil
- deltaP (pressure drop) — Change in reservoir pressure
- G (gas in place) — How much gas was originally underground (gas only)

**Reservoir State** (Oil only)
: **Saturated** — Pressure has dropped below the bubble point. Gas is coming out
of solution and is present as free gas in the reservoir.
: **Unsaturated** — Pressure is still above the bubble point. No free gas exists.
The app hides gas-related variables and forces Rp = Rsi.

**Drive Mechanism checkboxes**
: Each checkbox represents a physical force that can push oil out. Check the ones
active in your reservoir. When you uncheck one, the app zeros out its variables
and hides them — so you only see what matters.

**Water Influx Model** (appears when Water Drive is checked)
: Choose how the water influx We is calculated:
- **None** — Simple We = K×ΔP (the default)
- **Pot-Aquifer** — From aquifer geometry (radii, thickness, porosity)
- **Schilthuis** — Time-integrated model (needs time data)
- **Van Everdingen-Hurst** — Most rigorous (uses dimensionless tables)
""")

st.subheader("Data Input")
st.markdown("""
Below the sidebar, the main area shows input boxes for each required variable.
The app intelligently hides:
- The variable you're solving for (that's the unknown)
- Variables forced to zero by your drive mechanism choices

**Time-Series Table** — Expand the "Time-Series Data" section to enter multiple
rows of data at different pressures. This unlocks pressure-decline charts and
Havlena-Odeh regression plots.
""")

st.subheader("Results")
st.markdown("""
After clicking Calculate:
1. **The answer** — big blue text at the top (N, We, m, or whatever you solved for)
2. **Metric cards** — Recovery factor, water influx, gas cap ratio, drive mechanism
3. **Expandable sections** — Click to open:
   - Drive Indices & Insights (pie chart + warnings)
   - Variable Summary (full table + CSV download)
   - Time-Series Analysis (plots, only if you entered time data)
4. **Rp Sensitivity** (saturated oil only) — Interactive slider showing how
   recovery factor changes with produced gas-oil ratio
""")

st.markdown("---")


st.subheader("Example E — Combination Drive (All Three Active)")
st.markdown("""
*Goal: Solve for N with water drive, gas cap, and expansion all contributing.*

This is the most complete scenario. A saturated reservoir has a gas cap (m > 0),
water influx (We > 0), and rock/water expansion. All three drive mechanisms are
active. The full MBE handles them all at once.

**Setup:**
- Fluid: **Oil**
- Target: **N**
- Reservoir State: **Saturated**
- Drives: all three **ON**

**What you'll type:**
- Np = 5,000,000 STB, Bo = 1.33, Boi = 1.35
- Rsi = 600, Rs = 500, Rp = 1,100
- Bg = 0.0015, Bgi = 0.0011
- We = 3,000,000, Wp = 200,000, Bw = 1.0
- m = 0.2

**What happens:** The answer is N ≈ 36.6 MMSTB. The pie chart shows how much
each mechanism contributes. The drive classification says "Combination Drive."
""")
_example_button(
    "▶️ Load Example E in Calculator",
    {
        "target_var": "N",
        "fluid_type": "Oil",
        "reservoir_state": "Saturated",
        "water_drive_active": "true",
        "gas_cap_active": "true",
        "expansion_active": "true",
        "Np": "5000000",
        "Bo": "1.33",
        "Boi": "1.35",
        "Rsi": "600",
        "Rs": "500",
        "Rp": "1100",
        "Bg": "0.0015",
        "Bgi": "0.0011",
        "We": "3000000",
        "Wp": "200000",
        "Bw": "1.0",
        "m": "0.2",
        "auto_calculate": "true",
    },
)

st.markdown("---")


# ── 4. Understanding the Results ───────────────────────────────────────────

st.header("4. Understanding the Results")

st.markdown("""
### The collapsible layout
After clicking Calculate, the results appear in a compact layout designed to
show the most important numbers first and hide details until you need them.

### Metric cards (always visible)
| Card | What it means |
|---|---|
| Recovery Factor | What percentage of the oil has been produced so far |
| Water Influx | How much water has flowed in from the aquifer (in million bbl) |
| Gas Cap Ratio | Size of the gas cap compared to the oil zone (e.g., 0.2 = 20%) |
| Drive Mechanism | Which force is pushing oil out (Solution Gas, Gas Cap, Water, or Combo) |

### Drive Indices & Insights (click to expand)
A pie chart showing each mechanism's percentage contribution. If the chart shows
100% one thing, that's your dominant drive. The insights section gives warnings:
- "Rp > Rsi" — gas is breaking out, losing pressure energy
- "Rock and fluid expansion only" — least efficient drive, expect low recovery

### Variable Summary (click to expand)
Every variable and its value in a table. Use the **Download CSV** button to
export for reports. Column includes Variable, Description, Value, and Status
(Target / Input / Forced Zero).

### Time-Series Analysis (click to expand)
Only appears if you entered time-varying data. Shows:
- **Pressure Decline** — How pressure drops as oil is produced
- **Havlena-Odeh Plots** — Straight-line diagnostics for your drive mechanisms
- **Interpretation** — "F vs Et straight line → assumptions correct. Curves upward
  → missing energy source."
""")

st.markdown("---")


# ── 5. Performance Prediction (Ch 12) ──────────────────────────────────────

st.header("5. Performance Prediction (Tracy's Method)")

st.markdown("""
The **prediction** page — accessed via the radio button at the top of the app —
tells you what happens next: how much oil you'll produce as pressure drops.

It uses **Tracy's method** (Ch 12), which iteratively predicts Np, Gp, GOR, and
saturations at each pressure step below the bubble point.

### When to use it
- You already know N (from the MBE solver or geology)
- You have PVT data (Bo, Bg, Rs) and relative permeability (krg/kro)
- You want to forecast recovery, GOR behavior, and gas saturation

### What you get
Six performance curves: Np vs pressure, GOR vs pressure, Gp vs pressure,
So/Sg vs pressure, Rp vs pressure, and krg/kro vs Sg.

### Workflow
1. Use the **MBE Solver** to find N
2. Switch to **Performance Prediction** mode
3. Enter N, PVT table, and relative permeability data
4. Click Run Prediction
5. Review the curves and insights
""")

st.markdown("---")


# ── 6. Water Influx Models ──────────────────────────────────────────────────

st.header("6. Water Influx Models (Ch 11 / Ch 3)")

st.markdown("""
When you enable **Water Drive Active** in the sidebar, a Water Influx Model
dropdown appears. This controls how the calculator computes We (water influx).

| Model | Best for |
|---|---|
| None (default) | Simple cases where We = K×ΔP is enough |
| Pot-Aquifer | You know the aquifer dimensions (radii, thickness, porosity) |
| Schilthuis | You have time-series data and want to account for production rate |
| Van Everdingen-Hurst | Large aquifers where pressure transients matter |

All three models feed into the Havlena-Odeh diagnostic plot: **F/Eo vs We/Eo**.
A 45° straight line means the model is correct.
""")

st.markdown("---")


# ── 7. Variable Glossary ──────────────────────────────────────────────────

st.header("7. Variable Glossary")

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("""
**N** — Initial Oil-In-Place (STB)
: Oil that was originally underground. The most common answer.

**Np** — Cumulative Oil Produced (STB)
: Oil you've pumped out so far.

**Bo** — Current Oil FVF (bbl/STB)
: How much space 1 barrel of oil takes up at reservoir conditions.
  Like dough rising — oil expands as pressure drops.

**Boi** — Initial Oil FVF (bbl/STB)
: How much space 1 barrel of oil took up originally.

**Rs** — Current Solution GOR (scf/STB)
: How much gas is dissolved in each barrel at current pressure.
  Higher pressure = more gas dissolved.

**Rp** — Cumulative Produced GOR (scf/STB)
: How much gas came out with each barrel, on average.

**Rsi** — Initial Solution GOR (scf/STB)
: How much gas was dissolved in each barrel originally.

**Bg** — Current Gas FVF (bbl/scf)
: How much space 1 cubic foot of gas takes up now. Changes with pressure.

**Bgi** — Initial Gas FVF (bbl/scf)
: Initial value of the above.
""")

with col_b:
    st.markdown("""
**G** — Initial Gas-In-Place (Mscf)
: Gas originally underground. Used in gas reservoir mode.

**Gp** — Cumulative Gas Produced (Mscf)
: Gas produced so far.

**We** — Cumulative Water Influx (bbl)
: Water that has flowed in from the aquifer. A deposit into the account.

**Wp** — Cumulative Water Produced (bbl)
: Water pumped out.

**Bw** — Water FVF (bbl/STB)
: Water formation volume factor (usually close to 1).

**m** — Gas Cap Ratio
: Size of the gas cap compared to the oil zone. m = 0.2 means the gas cap
  is 20% as large as the oil zone.

**Swi** — Initial Water Saturation
: Fraction of rock pores filled with water initially. 0.25 = 25%.

**cw, cf** — Water & Formation Compressibility (psi⁻¹)
: How much water and rock compress when pressure drops. Very tiny numbers.

**deltaP** — Change in Pressure (psi)
: How much pressure dropped from initial to current.
""")

st.markdown("---")


# ── 8. Troubleshooting ──────────────────────────────────────────────────────

st.header("8. Troubleshooting")

st.subheader("Common errors")

st.markdown("""
**"Missing known values for variables: ..."**
: You left input boxes empty. Fill them in and try again.

**"Division by zero"**
: You created a math impossibility — usually a zero in a denominator like
  Bg/Bgi when both are zero. Turn on the relevant drive mechanism.

**"Target variable cancels out"**
: The variable you're solving for disappears from the equation. For example,
  solving for deltaP when expansion is turned off. Turn on Rock & Water Expansion.

**"No valid solution found"**
: SymPy couldn't find an answer. Check that your inputs are physically
  reasonable (e.g., final pressure can't be higher than initial pressure).

**"SVD did not converge"**
: The trendline for time-series data can't be computed. Your data points may
  be too few or too similar. Add more varied rows.
""")

st.subheader("Quick tips")

st.markdown("""
1. **Start with the examples above.** Each one loads a working example with one
   click. Study the setup, then tweak one number to see how the answer changes.

2. **Turn off drives you don't need.** Unsure about water influx? Uncheck Water
   Drive. The app zeros it out and hides related input boxes.

3. **The pie chart tells you what's really driving production.** If you expected
    "Water Drive" but see 100% "Solution Gas Drive," your We value is wrong.
""")

# ── 9. Guided Examples ──────────────────────────────────────

st.header("9. Guided Examples")
st.caption("Work through these in order. Each one comes from a textbook example.")

st.markdown("---")

# ── Example A ──────────────────────────────────────────────────────────────

st.subheader("Example A — Oil Recovery Above Bubble Point (Exercise 3.1)")
st.markdown("""
*Source: Ch 3 (Dake), Exercise 3.1. Goal: Find how much oil you'll produce by
the time pressure drops to the bubble point.*

You have a reservoir above the bubble point. No gas cap, no water drive — only
rock and water expansion are pushing oil out. You want to know what fraction of
the oil you'll recover as pressure declines from 4000 psi to 3330 psi.

**Setup:**
- Fluid: **Oil**
- Target: **N** (but here we're really calculating recovery factor)
- Reservoir State: **Unsaturated**
- Drives: turn **OFF** Water and Gas Cap, turn **ON** Expansion

**What you'll type:**
- Np = 1000 (placeholder — the answer is a fraction, not an absolute number)
- Bo = 1.2511, Boi = 1.2417
- Swi = 0.20, cw = 3×10⁻⁶, cf = 8.6×10⁻⁶
- deltaP = 670

**What happens:** The app shows a recovery factor of about 1.5%. This is low
because liquid oil and water don't expand much — most of the energy comes from
gas, and there's no gas above the bubble point.
""")
_example_button(
    "▶️ Load Example A in Calculator",
    {
        "target_var": "N",
        "fluid_type": "Oil",
        "reservoir_state": "Unsaturated",
        "water_drive_active": "false",
        "gas_cap_active": "false",
        "expansion_active": "true",
        "Np": "1000",
        "Bo": "1.2511",
        "Boi": "1.2417",
        "Rs": "0",
        "Rsi": "0",
        "Swi": "0.20",
        "cw": "0.000003",
        "cf": "0.0000086",
        "deltaP": "670",
        "auto_calculate": "true",
    },
)

st.markdown("---")

# ── Example B ──────────────────────────────────────────────────────────────

st.subheader("Example B — Volumetric Undersaturated (Example 11-3)")
st.markdown("""
*Source: Ch 11, Example 11-3 (adapted). Goal: Find N using the F vs Eo+Efw plot.*

The Virginia Hills Beaverhill Lake field is a volumetric undersaturated reservoir.
That means no gas cap, no water influx — just oil expansion + rock/water
compression. You have production data at 12 different pressure points.

**Setup:**
- Fluid: **Oil**
- Target: **N**
- Reservoir State: **Unsaturated**
- Drives: all **OFF** (no gas cap, no water, no expansion)

**What to do:**
1. Copy the table below into the **Time-Series Data** expander
2. Click Calculate
3. Scroll to the **Volumetric Undersaturated** plot in the Time-Series section

**Expected result:** The slope of the F vs Eo+Efw line gives N ≈ 257 MMSTB.
""")
with st.expander("Example B data — copy into the time-series table"):
    st.dataframe(
        {
            "Np (STB)": [
                20481,
                34750,
                78557,
                101846,
                215681,
                364613,
                542985,
                841591,
                1273530,
                1691887,
                2127077,
                2575330,
            ],
            "Bo (bbl/STB)": [
                1.3104,
                1.3104,
                1.3105,
                1.3105,
                1.3109,
                1.3116,
                1.3122,
                1.3128,
                1.3130,
                1.3150,
                1.3160,
                1.3170,
            ],
            "Wp (bbl)": [0, 0, 0, 0, 0, 0, 159, 805, 2579, 5008, 6500, 8000],
            "deltaP (psi)": [5, 9, 18, 21, 45, 80, 118, 170, 237, 325, 410, 497],
        }
    )

st.markdown("---")

# ── Example C ──────────────────────────────────────────────────────────────

st.subheader("Example C — Gas Cap Drive (Ch 3 Exercise 3.4)")
st.markdown("""
*Source: Ch 3 (Dake), Exercise 3.4. Goal: Find N and m from production data.*

A gas-cap-drive reservoir has produced oil for several years. The gas cap size
(m) is uncertain from geology — the F/Eo vs Eg/Eo plot (Havlena-Odeh) solves
for both N and m simultaneously.

**Setup:**
- Fluid: **Oil**
- Target: **N**
- Reservoir State: **Saturated**
- Drives: turn Water **OFF**, turn Gas Cap **ON**, turn Expansion **OFF**

**What you'll type:**
- Enter Np, Bo, Rsi, Rs, Rp, Bg, Bgi at current conditions
- The gas cap ratio m is NOT entered here — the F/Eo vs Eg/Eo plot gives m
  as slope/intercept in the time-series analysis

**What happens:** The solver finds N (oil in place). Then in the time-series
section, the **F/Eo vs Eg/Eo** plot shows:
- Intercept = N
- Slope / Intercept = m (gas cap ratio)

From Dake Exercise 3.4: N ≈ 109 MMSTB, m ≈ 0.54.
""")
_example_button(
    "▶️ Load Example C in Calculator",
    {
        "target_var": "N",
        "fluid_type": "Oil",
        "reservoir_state": "Saturated",
        "water_drive_active": "false",
        "gas_cap_active": "true",
        "expansion_active": "false",
        "Np": "5000000",
        "Bo": "1.33",
        "Boi": "1.35",
        "Rsi": "600",
        "Rs": "500",
        "Rp": "1100",
        "Bg": "0.0015",
        "Bgi": "0.0011",
        "m": "0.2",
        "Wp": "0",
        "auto_calculate": "true",
    },
)

st.markdown("---")

# ── Example D ──────────────────────────────────────────────────────────────

st.subheader("Example D — Water Drive Reservoir (Example 11-5)")
st.markdown("""
*Source: Ch 11, Example 11-5. Goal: Find N with a simple water influx model.*

A saturated reservoir has an active aquifer pushing water in. You know the
pressure history but not the aquifer size. Using the simple pot-aquifer model
We = K×ΔP, the F/Eo vs ΔP/Eo plot gives you both N and the water influx constant K.

**Setup:**
- Fluid: **Oil**
- Target: **N**
- Reservoir State: **Saturated**
- Drives: Water **ON**, Gas Cap **OFF**, Expansion **OFF**

**What you'll type:**
- Production data: Np, Bo, Rsi, Rs, Rp, Bg, Wp, Bw, plus We and deltaP

**What happens:** The solver finds N. The F/Eo vs ΔP/Eo water drive plot in the
time-series section gives a straight line where:
- Intercept = N
- Slope = K (water influx constant)

From the textbook: N ≈ 35 MMSTB.
""")
_example_button(
    "▶️ Load Example D in Calculator",
    {
        "target_var": "N",
        "fluid_type": "Oil",
        "reservoir_state": "Saturated",
        "water_drive_active": "true",
        "gas_cap_active": "false",
        "expansion_active": "false",
        "Np": "3000000",
        "Bo": "1.28",
        "Boi": "1.30",
        "Rsi": "600",
        "Rs": "500",
        "Rp": "900",
        "Bg": "0.0012",
        "We": "2000000",
        "Wp": "100000",
        "Bw": "1.0",
        "deltaP": "200",
        "auto_calculate": "true",
    },
)

st.markdown("---")


st.subheader("Example F — Predict Performance (Example 12-4)")
st.markdown("""
*Source: Ch 12, Tracy (1955), pp.834-838. Goal: Forecast Np, Gp, GOR, So, Sg
as pressure declines from 4350 psi to 3350 psi.*

This is the classic Tracy's method example. You know N = 15 MMSTB, Swi = 30%,
and have PVT data plus relative permeability. The prediction tells you how much
oil and gas you'll produce at each pressure step.

**Setup:**
- Switch to **Performance Prediction** mode using the radio button at the top
- All data is pre-loaded with the default values from Example 12-4

**What's already filled in for you:**
- N = 15,000,000 STB, Swi = 0.30, pi = 4350, pb = 4350
- μo = 1.7 cp, μg = 0.023 cp, Soi = 0.70
- PVT table: 6 rows of pressure, Bo, Bg, Rs data
- Relperm table: Sg vs krg/kro (9 data points)

**Steps:**
1. Click **Run Prediction**
2. Review the **Prediction Results Table** — 4350 (no production) through 3350 psi
3. Check the **Performance Curves** — especially GOR vs Pressure and Np vs Pressure
4. Read the **Drive Mechanism Insights** at the bottom

**Expected results (from textbook Example 12-4):**
| Pressure | Np (STB) | Gp (scf) | (GOR)avg (scf/STB) | So | Sg |
|---|---|---|---|---|---|
| 4150 | 43,800 | 37.2×10⁶ | 845 | 0.693 | 0.007 |
| 3950 | 165,000 | 145.6×10⁶ | 880 | 0.675 | 0.025 |
| 3750 | 345,000 | 325.6×10⁶ | 1,000 | 0.660 | 0.040 |
| 3550 | 534,000 | 567.2×10⁶ | 1,280 | 0.643 | 0.057 |
| 3350 | 690,000 | 840×10⁶ | 1,650 | 0.631 | 0.069 |

**What this tells you:** GOR rises from 840 to a peak (average GOR of 1,650)
as gas evolves from solution. Gas saturation grows from 0 to 7%. Recovery
factor ~4.6% — typical for solution-gas drive without pressure support.

> Note: The table shows (GOR)avg — the average GOR used in Tracy's iteration.
> The actual instantaneous GOR at each pressure may be slightly higher.
> Your results from the calculator may vary slightly depending on relperm
> interpolation. The values above are the published textbook results.
""")
_example_button(
    "▶️ Switch to Prediction Mode (pre-loaded)",
    {"mode": "prediction"},
)

st.markdown("---")

st.subheader("Example G — Saturation Tracking (Example 12-2)")
st.markdown("""
*Source: Ch 12, p.818. Goal: Calculate oil and gas saturations after 10%
of the oil is produced.*

A simple check on your understanding of saturations. You don't need the full
predictor — just the MBE Solver.

**Setup:**
- Mode: **MBE Solver**
- Fluid: **Oil**
- Target: **N** (placeholder, you're checking So and Sg)
- Saturated, all drives OFF

**What you'll type:**
- Swi = 0.20
- Boi = 1.50 bbl/STB
- Bo = 1.38 bbl/STB
- Np = 10,000,000 (assuming N = 100,000,000)
- N = 100,000,000

**What happens:** The solver calculates N and shows the recovery factor.
Manually check saturations using:
- So = (1 - 0.20) × (1 - 10/100) × (1.38/1.50) = 0.662
- Sg = 1 - 0.662 - 0.20 = 0.138

**What this tells you:** After 10% of the oil is produced, 66% of the pore
space is still occupied by oil, 14% by gas, and 20% by water.
""")
_example_button(
    "▶️ Load Example G in Calculator",
    {
        "target_var": "N",
        "fluid_type": "Oil",
        "reservoir_state": "Saturated",
        "water_drive_active": "false",
        "gas_cap_active": "false",
        "expansion_active": "false",
        "Np": "10000000",
        "N": "100000000",
        "Bo": "1.38",
        "Boi": "1.50",
        "Swi": "0.20",
    },
)


st.markdown("---")

st.subheader("Example K — Gas Cap Drive Using Bt Data (Handbook Example 11-4)")
st.markdown("""
*Source: Ch 11, Example 11-4 (Ahmed). Goal: Find N and m using two-phase FVF data.*

The Handbook provides gas cap drive data using the **two-phase FVF (Bt)** instead
of separate Bo and Rs. The function `bt_to_bo_rs()` in `models/gas_hod.py`
converts Bt → Bo+Rs for use in the solver.

**Setup:**
- Fluid: **Oil**
- Target: **N**
- Reservoir State: **Saturated**
- Drives: turn Water **OFF**, turn Gas Cap **ON**, turn Expansion **OFF**

**Handbook data (from pp.791-792):**
| p (psi) | Np (MSTB) | Gp (MMscf) | Rp (scf/STB) | Bt (bbl/STB) | Bg (bbl/scf) |
|---|---|---|---|---|---|
| 4415 | — | — | — | 1.6291 | 0.00077 |
| 3875 | 492.5 | 751.3 | 1525 | 1.6839 | 0.00079 |
| 3315 | 1015.7 | 2409.6 | 2372 | 1.7835 | 0.00087 |
| 2845 | 1322.5 | 3901.6 | 2950 | 1.9110 | 0.00099 |

**Converted data (Bo+Rs estimated from Bt):**
""")
with st.expander("Converted data — copy into the time-series table"):
    st.dataframe(
        {
            "p": [3875, 3315, 2845],
            "Np": [492500, 1015700, 1322500],
            "Rp": [1525, 2372, 2950],
            "Bo": [1.5897, 1.5722, 1.5678],
            "Rs": [856, 732, 628],
            "Bg": [0.00079, 0.00087, 0.00099],
        }
    )
st.markdown("""
**Expected result (from Handbook):**  
The F/Eo vs Eg/Eo Havlena-Odeh plot gives:
- Intercept = N ≈ **9 MMSTB**
- Slope = m×N ≈ 3.1×10⁷ → m ≈ **3.44** (large gas cap)

**Note:** The single-point solver can't solve for both N and m at once. Enter
all three rows of the converted data in the time-series table, click Calculate,
then scroll to the **Gas Cap Drive** Havlena-Odeh plot to find N and m.
""")
_example_button(
    "▶️ Load Example K (gas cap, Bt converted)",
    {
        "target_var": "N",
        "fluid_type": "Oil",
        "reservoir_state": "Saturated",
        "water_drive_active": "false",
        "gas_cap_active": "true",
        "expansion_active": "false",
        "Rsi": "975",
        "Boi": "1.6291",
        "Bgi": "0.00077",
        "auto_calculate": "false",
    },
)
