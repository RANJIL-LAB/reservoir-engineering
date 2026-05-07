import streamlit as st
import urllib.parse

st.set_page_config(
    page_title="Documentation — MBE Tool",
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
        f'padding:0.5em 1em;background:#1f77b4;color:white;'
        f'text-decoration:none;border-radius:6px;font-weight:bold;">'
        f'{label}</a>',
        unsafe_allow_html=True,
    )

st.title("📖 How to Use This Tool")
st.caption("A beginner-friendly guide. No math degree needed.")

with st.expander("What does this tool do?", expanded=True):
    st.markdown("""
    This tool solves the **Material Balance Equation (MBE)** — a formula that
    tells you about an oil reservoir.

    You give it some numbers (like how much oil you pumped out, what the 
    pressure is, etc.), and it calculates the one number you don't know.

    **It can tell you:**
    - **N** — How much oil was originally underground
    - **We** — How much water has flowed into the reservoir
    - **m** — How big the gas cap is
    - **deltaP** — How much the pressure dropped
    """)

with st.expander("What is the Material Balance Equation?"):
    st.markdown("""
    The MBE is a simple idea:

    > *"What you started with = what you took out + what moved around to fill the empty space."*

    Imagine an underground cave filled with oil. When you pump oil out:

    1. The pressure drops
    2. The oil shrinks a little
    3. Gas bubbles out of the oil (like soda fizzing)
    4. Any gas cap above expands to fill the void
    5. Water from surrounding rocks pushes in
    6. The rocks themselves squeeze slightly

    The MBE counts all these volume changes and makes sure they add up.
    """)

with st.expander("Step-by-step: How to use the app"):
    st.markdown("""
    ### Step 1 — Pick what you want to solve for
    In the sidebar, choose one of: **N**, **We**, **m**, or **deltaP**.

    ### Step 2 — Choose the reservoir state
    - **Saturated** — Pressure is at or below bubble point. Gas is bubbling out of the oil.
    - **Unsaturated** — Pressure is above bubble point. No free gas yet.

    ### Step 3 — Turn drives on or off
    Check the boxes for what's active in your reservoir:
    - **Water Drive** — Is an aquifer pushing water in?
    - **Gas Cap** — Is there a gas cap on top of the oil?
    - **Rock & Water Expansion** — Are the rocks and water squeezing?

    When you turn a drive OFF, the app hides the variables that don't matter
    anymore. This keeps the screen clean and prevents confusion.

    ### Step 4 — Enter your numbers
    Type numbers into the boxes, or upload a CSV/Excel file.

    ### Step 5 — Click Calculate
    The big blue button does the math.
    """)

with st.expander("What does each variable mean?"):
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        ### Oil & Production
        **N** — How much oil was originally in the ground (STB)

        **Np** — How much oil you've pumped out so far (STB)

        **Bt** — How much space 1 barrel of oil takes up now, at reservoir conditions (bbl/STB)

        **Bti** — How much space 1 barrel of oil took up originally (bbl/STB)
        """)

    with col2:
        st.markdown("""
        ### Gas
        **Rp** — How much gas came out with each barrel of oil (scf/STB)

        **Rsi** — How much gas was dissolved in each barrel of oil originally (scf/STB)

        **Bg** — How much space 1 cubic foot of gas takes up now (bbl/scf)

        **Bgi** — How much space 1 cubic foot of gas took up originally (bbl/scf)

        **m** — How big the gas cap is compared to the oil zone (dimensionless)
        """)

    with col3:
        st.markdown("""
        ### Water & Rock
        **We** — How much water has flowed in from the aquifer (bbl)

        **Wp** — How much water you've pumped out (bbl)

        **Bw** — How much space 1 barrel of water takes up (bbl/STB)

        **Swi** — What fraction of the rock pores were originally filled with water (decimal)

        **cw** — How much water compresses when pressure drops (psi⁻¹)

        **cf** — How much the rock compresses when pressure drops (psi⁻¹)

        **deltaP** — How much the pressure dropped (psi)
        """)

with st.expander("Understanding the units"):
    st.markdown("""
    | Unit | What it means |
    |------|---------------|
    | **STB** | Stock Tank Barrels — oil at surface conditions |
    | **bbl** | Barrels — volume at reservoir conditions |
    | **scf/STB** | Standard Cubic Feet per Stock Tank Barrel — gas per oil |
    | **psi** | Pounds per Square Inch — pressure |
    | **psi⁻¹** | Per psi — compressibility |
    | **decimal** | Fraction (e.g. 0.25 means 25%) |
    | **dimensionless** | No units — just a ratio |
    """)

with st.expander("What the results tell you"):
    st.markdown("""
    After you click Calculate, you'll see:

    1. **The answer** — The variable you wanted to solve for, shown large and clear
    2. **Recovery Factor** — What percentage of the oil you've produced so far
    3. **Drive Mechanism Analysis** — Which force is doing most of the pushing (gas cap? water? solution gas?)
    4. **Expert tips** — Warnings and advice based on your specific results
    5. **Drive Indices pie chart** — A donut chart showing how much each mechanism contributes
    6. **Summary table** — All your inputs and the answer in one table
    7. **Download button** — Save everything as a CSV file
    """)

with st.expander("Tips for beginners"):
    st.markdown("""
    ### Tip 1: If you don't know a value, turn off its drive
    Not sure about water influx? Uncheck "Water Drive Active?" and the app
    sets it to zero for you. The input box disappears too, so you don't
    get confused.

    ### Tip 2: Start simple
    Try Unsaturated reservoir with all drives OFF first. You only need
    **Np**, **Bt**, and **Bti** — just three numbers. That's the simplest
    possible calculation.

    ### Tip 3: Check the drive chart
    The pie chart tells you which mechanism is doing the most work.
    If you expected "Water Drive" but see "Solution Gas Drive," double-check
    your inputs.

    ### Tip 4: Upload a CSV for multi-row data
    If you have pressure and production data at multiple time points,
    upload a CSV with one row per time point. The app shows time-series
    charts (Pressure vs Np, Havlena-Odeh F vs Et).

    ### Tip 5: Column names in your CSV must match
    The app looks for columns like `N`, `Np`, `Bt`, `Bti`, etc.
    Capitalization doesn't matter — `np` and `Np` both work.
    """)

with st.expander("What is the Havlena-Odeh method?"):
    st.markdown("""
    The Havlena-Odeh method rearranges the MBE into a straight-line form:

    **F = N × Et**

    Where:
    - **F** = everything that came out of the reservoir (production + water)
    - **Et** = everything that expanded underground (oil + gas + rock + water)

    When you plot F vs Et with multi-row field data, you get a straight line
    through the origin. The slope of that line is **N** (Initial Oil-In-Place).

    This is a powerful way to verify your drive mechanism assumptions:
    - If the line is straight, your assumptions about **m** and **We** are correct
    - If the line curves up, you're missing an energy source (need larger **m** or **We**)
    - If the line curves down, you're overestimating the energy

    The app plots this chart automatically when you upload a multi-row CSV file.
    """)

st.markdown("---")
st.header("📋 Interactive Examples")
st.caption("Click any button to load the example directly into the calculator.")

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Example 1: Finding Missing Water")
    st.markdown("""
    **Oil reservoir with all drives active.** We know everything except
    how much water flowed in from the aquifer.

    - Target: **We** (Water Influx)
    - Fluid: Oil, Saturated
    - Drives: Water, Gas Cap, Expansion — all ON
    - N = 10,000,000 STB
    - Np = 1,000,000 STB, Bt = 1.655, Bti = 1.58
    - Rsi = 1040, Rp = 1100
    - Bg = 0.00092, Bgi = 0.00080
    - Wp = 50,000, Bw = 1.0, m = 0.25
    - Swi = 0.20, cw = 1.5×10⁻⁶, cf = 1.0×10⁻⁶, deltaP = 200
    """)
    _example_button("▶️ Run Example 1 in App", {
        'target_var': 'We',
        'fluid_type': 'Oil',
        'reservoir_state': 'Saturated',
        'water_drive_active': 'true',
        'gas_cap_active': 'true',
        'expansion_active': 'true',
        'N': '10000000',
        'Np': '1000000',
        'Bt': '1.655',
        'Bti': '1.58',
        'Rsi': '1040',
        'Rp': '1100',
        'Bg': '0.00092',
        'Bgi': '0.00080',
        'Wp': '50000',
        'Bw': '1.0',
        'm': '0.25',
        'Swi': '0.20',
        'cw': '0.0000015',
        'cf': '0.000001',
        'deltaP': '200',
        'auto_calculate': 'true',
    })

    st.subheader("Example 3: The Big Butte Field")
    st.markdown("""
    **Oil reservoir with water and gas cap drives active.**
    A typical saturated reservoir with moderate aquifer support.

    - Target: **N** (Oil-In-Place)
    - Fluid: Oil, Saturated
    - Drives: Water ON, Gas Cap ON, Expansion OFF
    - Np = 5,000,000 STB
    - Bt = 1.48, Bti = 1.35
    - Rsi = 600, Rp = 1100
    - Bg = 0.0015, Bgi = 0.0011
    - We = 3,000,000, Wp = 200,000, Bw = 1.0
    - m = 0.2
    """)
    _example_button("▶️ Run Example 3 in App", {
        'target_var': 'N',
        'fluid_type': 'Oil',
        'reservoir_state': 'Saturated',
        'water_drive_active': 'true',
        'gas_cap_active': 'true',
        'expansion_active': 'false',
        'Np': '5000000',
        'Bt': '1.48',
        'Bti': '1.35',
        'Rsi': '600',
        'Rp': '1100',
        'Bg': '0.0015',
        'Bgi': '0.0011',
        'We': '3000000',
        'Wp': '200000',
        'Bw': '1.0',
        'm': '0.2',
        'auto_calculate': 'true',
    })

with col_b:
    st.subheader("Example 2: Fractional Recovery Hack")
    st.markdown("""
    **Unsaturated oil reservoir — the simplest case.**
    A tight reservoir where only rock and water expansion provide energy.
    Great for understanding the expansion term.

    - Target: **N** (Oil-In-Place)
    - Fluid: Oil, Unsaturated
    - Drives: Water OFF, Gas Cap OFF, Expansion ON
    - Np = 1,000 STB
    - Bt = 1.2511, Bti = 1.2417
    - Swi = 0.20, cw = 3×10⁻⁶, cf = 8.6×10⁻⁶
    - deltaP = 670 psi
    """)
    _example_button("▶️ Run Example 2 in App", {
        'target_var': 'N',
        'fluid_type': 'Oil',
        'reservoir_state': 'Unsaturated',
        'water_drive_active': 'false',
        'gas_cap_active': 'false',
        'expansion_active': 'true',
        'Np': '1000',
        'Bt': '1.2511',
        'Bti': '1.2417',
        'Swi': '0.20',
        'cw': '0.000003',
        'cf': '0.0000086',
        'deltaP': '670',
        'auto_calculate': 'true',
    })

    st.subheader("Example 4: Gas — Volumetric Depletion")
    st.markdown("""
    **Dry gas reservoir with no water drive.**
    The simplest gas case: gas expansion is the only drive mechanism.

    - Target: **G** (Gas-In-Place)
    - Fluid: Gas
    - Drives: Water OFF, Expansion OFF
    - Gp = 5,000,000 Mscf
    - Bg = 0.0015, Bgi = 0.0012
    """)
    _example_button("▶️ Run Example 4 in App", {
        'target_var': 'G',
        'fluid_type': 'Gas',
        'water_drive_active': 'false',
        'expansion_active': 'false',
        'Gp': '5000000',
        'Bg': '0.0015',
        'Bgi': '0.0012',
        'auto_calculate': 'true',
    })
