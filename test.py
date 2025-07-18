import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9+
import pandas as pd
import time
import base64

# --- constants --------------------------------------------------------------
SECONDS_PER_DAY = 24 * 60 * 60  # 86,400 seconds in a day
UPDATE_INTERVAL_SEC = 2  # update frequency (seconds)
TZ = ZoneInfo("America/Los_Angeles")

FILE_PATH = "carbon-monitor-carbonmonitorGLOBAL-WORLD(datas).csv"

TOTAL_DAILY_HA = 437.16
HA_PER_SECOND = TOTAL_DAILY_HA / SECONDS_PER_DAY

TOTAL_DAILY_PLASTIC_KG = 1_260_273_973
PLASTIC_KG_PER_SECOND = TOTAL_DAILY_PLASTIC_KG / SECONDS_PER_DAY

TOTAL_DAILY_OCEAN_PLASTIC_KG = 30_136_986
OCEAN_PLASTIC_KG_PER_SECOND = TOTAL_DAILY_OCEAN_PLASTIC_KG / SECONDS_PER_DAY

TOTAL_DAILY_MICROPLASTIC_MG = 714.0
MICROPLASTIC_MG_PER_SECOND = TOTAL_DAILY_MICROPLASTIC_MG / SECONDS_PER_DAY

TOTAL_DAILY_ACRES_LOST = 202_513
ACRES_PER_SECOND = TOTAL_DAILY_ACRES_LOST / SECONDS_PER_DAY

ITALY_2023_ANNUAL_CO2_MILLION_METRIC_TONS = 312.67
ITALY_2023_ANNUAL_CO2_METRIC_TONS = ITALY_2023_ANNUAL_CO2_MILLION_METRIC_TONS * 1_000_000
ITALY_2023_DAILY_CO2_METRIC_TONS = int(ITALY_2023_ANNUAL_CO2_METRIC_TONS / 365)

# Weight of the Great Pyramid of Giza in metric tons (approximate)
GREAT_PYRAMID_WEIGHT_METRIC_TONS = 5_750_000


# --- Font Loader ------------------------------------------------------------
def load_woff_font_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# --- Helper Functions ------------------------------------------------------
def time_elapsed_seconds(now: datetime) -> float:
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return max(0, min((now - midnight).total_seconds(), SECONDS_PER_DAY))

def hectares_lost_so_far(now: datetime) -> float:
    return HA_PER_SECOND * time_elapsed_seconds(now)

def plastic_produced_so_far(now: datetime) -> float:
    return PLASTIC_KG_PER_SECOND * time_elapsed_seconds(now)

def ocean_plastic_entered_so_far(now: datetime) -> float:
    return OCEAN_PLASTIC_KG_PER_SECOND * time_elapsed_seconds(now)

def microplastic_ingested_so_far(now: datetime) -> float:
    return MICROPLASTIC_MG_PER_SECOND * time_elapsed_seconds(now)

def acres_lost_so_far(now: datetime) -> float:
    return ACRES_PER_SECOND * time_elapsed_seconds(now)

def k_format(val: float) -> str:
    if val >= 1_000_000_000:
        return f"{val / 1_000_000_000:.1f}B".rstrip('0').rstrip('.')
    elif val >= 1_000_000:
        return f"{val / 1_000_000:.1f}M".rstrip('0').rstrip('.')
    elif val >= 1_000:
        return f"{val / 1_000:.0f}k"
    else:
        return f"{val:,.0f}"

def load_total_today_emissions() -> float:
    df = pd.read_csv(FILE_PATH, names=["region", "date", "sector", "co2_mt"])
    df["date"] = df["date"].astype(str)

    def parse_date(date_str):
        for fmt in ("%m/%d/%Y", "%d/%m/%Y"):
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        try:
            return pd.to_datetime(date_str).date()
        except Exception:
            return None

    df["date"] = df["date"].apply(parse_date)
    df = df.dropna(subset=["date"])

    today_2024 = datetime.now(TZ).date().replace(year=2024)
    today_data = df[df["date"] == today_2024]
    return today_data["co2_mt"].sum() * 1_000_000

def emissions_so_far(now: datetime, total_today: float) -> float:
    return total_today * (time_elapsed_seconds(now) / SECONDS_PER_DAY)


# --- Streamlit App ---------------------------------------------------------
def main():
    st.set_page_config(layout="centered", initial_sidebar_state="collapsed")

    qartella_font = load_woff_font_base64("Qartella.woff")
    st.markdown(f"""
        <style>
        @font-face {{
            font-family: 'Qartella';
            src: url(data:font/woff;base64,{qartella_font}) format('woff');
            font-weight: normal;
            font-style: normal;
        }}

        html, body, [class*="st-"] {{
            font-family: 'Qartella', sans-serif !important;
        }}

        .stApp {{
            background-color: #0E1117;
            color: white;
        }}
        .metric-block {{ margin-bottom: 30px; }}
        .metric-label {{ color: white; font-size: 1.5em; margin-bottom: 5px; }}
        .metric-value {{ color: white; font-size: 3em; font-weight: bold; margin-bottom: 5px; }}
        .metric-comparison {{ color: #70c38B; font-size: 1.8em; margin-top: 0px; }}
        .bottom-left {{
            position: fixed;
            bottom: 10px;
            left: 10px;
            font-size: 1.3em;
            font-weight: bold;
            z-index: 1000;
        }}
        /* Removed .centered-image class */
        </style>
    """, unsafe_allow_html=True)

    @st.cache_data(ttl=SECONDS_PER_DAY)
    def get_emissions_total():
        try:
            return load_total_today_emissions()
        except Exception as e:
            st.error(f"Failed to load emissions data: {e}")
            return 0

    total_today_emissions = get_emissions_total()
    placeholder = st.empty()

    while True:
        now = datetime.now(TZ)
        elapsed_seconds = time_elapsed_seconds(now)
        running_hours = int(elapsed_seconds // 3600)

        ha_lost = hectares_lost_so_far(now)
        ha_to_washdc = (ha_lost / 1500) * 365

        plastic_produced = plastic_produced_so_far(now)
        ocean_plastic = ocean_plastic_entered_so_far(now)
        microplastic = microplastic_ingested_so_far(now)
        acres_lost = acres_lost_so_far(now)

        credit_card_equiv = ((microplastic / 5000) / (elapsed_seconds / SECONDS_PER_DAY * 7)) * 100 if elapsed_seconds > 0 else 0
        acres_to_football = acres_lost / 1.32

        co2_emitted = emissions_so_far(now, total_today_emissions)
        # Calculate comparison to Great Pyramids of Egypt, now as a whole number
        pyramid_comparison = co2_emitted / GREAT_PYRAMID_WEIGHT_METRIC_TONS if GREAT_PYRAMID_WEIGHT_METRIC_TONS > 0 else 0.0

        with placeholder.container():
            col1, col2, col3 = st.columns(3)
            with col1:
                hectares_lost = acres_lost * 0.404686
                st.markdown(f"""
                    <div class="metric-block">
                        <p class="metric-label">Forest lost today</p>
                        <p class="metric-value">{hectares_lost:,.0f} hectares</p>
                        <p class="metric-comparison">≈{k_format(acres_to_football)} football fields</p>
                    </div>
                """, unsafe_allow_html=True)
                # Reverted to st.image directly
                st.image("Frame 19.png", width=350)

            with col2:
                st.markdown(f"""
                    <div class="metric-block">
                        <p class="metric-label">CO₂ emitted today</p>
                        <p class="metric-value">{co2_emitted:,.0f} t CO₂</p>
                        <p class="metric-comparison">≈{pyramid_comparison:.0f}x Great Pyramid of Giza</p>
                    </div>
                """, unsafe_allow_html=True)
                # Reverted to st.image directly
                st.image("Frame 21.png", width=350)

            with col3:
                st.markdown(f"""
                    <div class="metric-block">
                        <p class="metric-label">Land lost today</p>
                        <p class="metric-value">{ha_lost:,.0f} hectares</p>
                        <p class="metric-comparison">≈{ha_to_washdc:.0f}% Washington DC/year</p>
                    </div>
                """, unsafe_allow_html=True)
                # Reverted to st.image directly
                st.image("Frame 22.png", width=350)

            st.markdown(f"""
                <div class="bottom-left">
                    Running Time: {running_hours} hours
                </div>
            """, unsafe_allow_html=True)

        time.sleep(UPDATE_INTERVAL_SEC)


if __name__ == "__main__":
    main()
