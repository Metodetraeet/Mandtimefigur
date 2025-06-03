import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io

# --- Plot function ---
def plot_budget_vs_regnskab(df: pd.DataFrame, title="Budget vs. Regnskab (med 2024 som reference)") -> plt.Figure:
    budget = df["Budget"].to_numpy()
    regnskab = df["Regnskab"].to_numpy()
    regnskab2024 = df["Regnskab t-1"].to_numpy()

    måneder = ["Januar", "Februar", "Marts", "April", "Maj", "Juni",
               "Juli", "August", "September", "Oktober", "November", "December"]

    x = np.arange(len(måneder))
    mask = (regnskab != 0) & ~np.isnan(regnskab) & ~np.isnan(budget)
    x_shaded = x[mask]
    budget_shaded = budget[mask]
    regnskab_shaded = regnskab[mask]

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(x, budget, marker='o', label='Budget', linewidth=2.5)
    ax.plot(x, regnskab, marker='o', label='Regnskab', color='green', linewidth=2.5)
    ax.plot(x, regnskab2024, marker='D', label='Korrigeret regnskab for sidste år',
            color='black', linewidth=1.5, linestyle='--', markersize=4, zorder=1, alpha=0.3)

    overskridelse_mask = (regnskab_shaded < budget_shaded)
    besparelse_mask = (regnskab_shaded > budget_shaded)

    ax.fill_between(x_shaded, budget_shaded, regnskab_shaded,
                    where=overskridelse_mask, interpolate=True, color='red', alpha=0.3, label='Afvigelse (n)')
    ax.fill_between(x_shaded, budget_shaded, regnskab_shaded,
                    where=besparelse_mask, interpolate=True, color='green', alpha=0.3, label='Afvigelse (p)')

    for i in range(len(x)):
        if not np.isnan(regnskab[i]) and not np.isnan(budget[i]) and regnskab[i] != 0:
            forskel = int(regnskab[i] - budget[i])
            tegn = "+" if forskel > 0 else ""
            tekst = f"{tegn}{forskel}"
            y_pos = (regnskab[i] + budget[i]) / 2
            ax.text(x[i], y_pos, tekst, ha='center', va='center',
                    fontsize=9, fontweight='bold', color='black')

    ax.set_xticks(x)
    ax.set_xticklabels(måneder, rotation=45)
    ax.set_title(title)
    ax.set_ylabel("Timer")
    ax.grid(True)
    ax.legend()
    fig.tight_layout()

    return fig

# --- Streamlit App ---
st.title("📊 Budget vs. Regnskab Dashboard")

st.markdown("""
Denne graf viser forskellen mellem budgetterede og faktiske timer for hver måned.

- **Grøn skygge** = Flere timer registreret end budgetteret
- **Rød skygge** = Færre timer registreret end budgetteret
- **Sort stiplede linje** = Registrerede timer sidste år, korrigeret efter årsværk
""")

uploaded_file = st.file_uploader("Upload Excel-fil", type=["xlsx"])

@st.cache_data
def load_excel(file):
    return pd.read_excel(file)

if uploaded_file is not None:
    try:
        df = load_excel(uploaded_file)
        required_cols = ["Budget", "Regnskab", "Regnskab t-1"]
        if all(col in df.columns for col in required_cols):
            fig = plot_budget_vs_regnskab(df)
            st.pyplot(fig)

            # Export download
            buf = io.BytesIO()
            fig.savefig(buf, format="png")
            st.download_button(
                "📥 Download graf som billede",
                data=buf.getvalue(),
                file_name="budget_vs_regnskab.png",
                mime="image/png"
            )
        else:
            missing = [col for col in required_cols if col not in df.columns]
            st.error(f"Excel-filen mangler kolonner: {', '.join(missing)}")
    except Exception as e:
        st.error(f"Fejl ved indlæsning af Excel-fil: {e}")
else:
    st.info("Vent på, at du uploader en Excel-fil med relevante data.")
