import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo   # Python 3.9+
import pandas as pd
import time
from streamlit_autorefresh import st_autorefresh

# --- constants --------------------------------------------------------------
SECONDS_PER_DAY     = 24 * 60 * 60  # 86,400 seconds in a day
UPDATE_INTERVAL_SEC = 2             # update frequency (seconds)
TZ                  = ZoneInfo("America/Los_Angeles")

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


# --- helper functions ------------------------------------------------------

def time_elapsed_seconds(now: datetime) -> float:
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elapsed = (now - midnight).total_seconds()
    return max(0, min(elapsed, SECONDS_PER_DAY))

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
    """Format large numbers: 130k, 1.5M, 2.2B, etc."""
    if val >= 1_000_000_000:
        return f"{val / 1_000_000_000:.1f}B".rstrip('0').rstrip('.')
    elif val >= 1_000_000:
        return f"{val / 1_000_000:.1f}M".rstrip('0').rstrip('.')
    elif val >= 1_000:
        return f"{val / 1_000:.0f}k"
    else:
        return f"{val:,.0f}"

# --- Carbon emissions specific ----------------------------------------------

def load_total_today_emissions() -> float:
    df = pd.read_csv(FILE_PATH, names=["region", "date", "sector", "co2_mt"])
    
    def parse_date(date_str):
        for fmt in ("%m/%d/%Y", "%d/%m/%Y"):
            try:
                return datetime.strptime(date_str, fmt).date()
            except:
                continue
        try:
            return pd.to_datetime(date_str).date()
        except:
            return None

    df["date"] = df["date"].apply(parse_date)
    df = df.dropna(subset=["date"])

    today_2024 = datetime.now(TZ).date().replace(year=2024)
    today_data = df[df["date"] == today_2024]

    total_today_mt = today_data["co2_mt"].sum()
    total_today_metric_tons = total_today_mt * 1_000_000
    return total_today_metric_tons

def emissions_so_far(now: datetime, total_today: float) -> float:
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elapsed_seconds = (now - midnight).total_seconds()
    elapsed_seconds = max(0, min(elapsed_seconds, SECONDS_PER_DAY))
    return total_today * (elapsed_seconds / SECONDS_PER_DAY)

# --- Streamlit app main -----------------------------------------------------

def main():
    # Make the title bigger
    st.markdown("<h1 style='font-size: 3em;'>Environmental Dashboard — Live Statistics</h1>", unsafe_allow_html=True)

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

        # Calculate values
        ha_lost = hectares_lost_so_far(now)
        ha_to_washdc = (ha_lost / 1500) * 365 # This delta calculation seems to be for annual percentage of Washington DC

        plastic_produced = plastic_produced_so_far(now)
        plastic_to_cars = plastic_produced / 1500 # Assuming 1500 kg per car for comparison

        ocean_plastic = ocean_plastic_entered_so_far(now)
        ocean_to_statues = ocean_plastic / 204116 # Assuming 204116 kg per Statue of Liberty for comparison

        microplastic = microplastic_ingested_so_far(now)
        # This delta calculation seems to be for percentage of a credit card per week
        # 5000 mg is roughly the weight of a credit card
        # 7 days in a week
        credit_card_equiv = ((microplastic / 5000) / (time_elapsed_seconds(now) / SECONDS_PER_DAY * 7)) * 100 if time_elapsed_seconds(now) > 0 else 0

        acres_lost = acres_lost_so_far(now)
        acres_to_football = acres_lost / 1.32 # Assuming 1.32 acres per football field for comparison

        co2_emitted = emissions_so_far(now, total_today_emissions)
        pyramids = co2_emitted / 5_750_000 # Assuming 5,750,000 tons for Great Pyramid of Giza for comparison

        # Re-render metrics without reloading page
        with placeholder.container():
            # Forest lost today
            st.metric(
                "Forest lost today",
                f"<span style='font-size: 2em;'>{acres_lost:,.0f} acres</span>",
                unsafe_allow_html=True
            )
            st.markdown(f'<span style="color: green; font-size: 1.2em;">≈{k_format(acres_to_football)} football fields</span>', unsafe_allow_html=True)

            # CO₂ emitted today
            st.metric(
                "CO₂ emitted today",
                f"<span style='font-size: 2em;'>{co2_emitted:,.0f} t CO₂</span>",
                unsafe_allow_html=True
            )
            st.markdown(f'<span style="color: green; font-size: 1.2em;">≈{k_format(pyramids)} Great Pyramids of Giza</span>', unsafe_allow_html=True)

            # Land lost today
            st.metric(
                "Land lost today",
                f"<span style='font-size: 2em;'>{ha_lost:,.0f} ha</span>",
                unsafe_allow_html=True
            )
            st.markdown(f'<span style="color: green; font-size: 1.2em;">≈{ha_to_washdc:.0f}% Washington DC per year</span>', unsafe_allow_html=True)

            # Plastic produced today
            st.metric(
                "Plastic produced today",
                f"<span style='font-size: 2em;'>{plastic_produced:,.0f} kg</span>",
                unsafe_allow_html=True
            )
            st.markdown(f"<span style='color: green; font-size: 1.2em;'>≈{plastic_to_cars:,.0f} cars</span>", unsafe_allow_html=True)

            # Plastic entered ocean today
            st.metric(
                "Plastic entered ocean today",
                f"<span style='font-size: 2em;'>{ocean_plastic:,.0f} kg</span>",
                unsafe_allow_html=True
            )
            st.markdown(f"<span style='color: green; font-size: 1.2em;'>≈{ocean_to_statues:,.0f} Statues of Liberty</span>", unsafe_allow_html=True)

            # Microplastic ingested today
            st.metric(
                "Microplastic ingested today",
                f"<span style='font-size: 2em;'>{microplastic:,.0f} mg</span>",
                unsafe_allow_html=True
            )
            st.markdown(f"<span style='color: green; font-size: 1.2em;'>≈{credit_card_equiv:.0f}% credit card in a week</span>", unsafe_allow_html=True)


        time.sleep(UPDATE_INTERVAL_SEC)


if __name__ == "__main__":
    main()
