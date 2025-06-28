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
    def main():
        st.title("Environmental Dashboard — Live Statistics")

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
        ha_to_washdc = (ha_lost / 1500) * 365

        plastic_produced = plastic_produced_so_far(now)
        plastic_to_cars = plastic_produced / 1500

        ocean_plastic = ocean_plastic_entered_so_far(now)
        ocean_to_statues = ocean_plastic / 204116

        microplastic = microplastic_ingested_so_far(now)
        credit_card_equiv = ((microplastic / 5000) * 7) * 100

        acres_lost = acres_lost_so_far(now)
        acres_to_football = acres_lost / 1.32

        co2_emitted = emissions_so_far(now, total_today_emissions)
        pyramids = co2_emitted / 5_750_000

        # Re-render metrics without reloading page
        #with placeholder.container():
            #st.metric("Land lost today (hectares)", f"{ha_lost:,.0f} ha", delta=f"~{ha_to_washdc:.0f}% Washington DC per year")
            #st.metric("Plastic produced today (kilograms)", f"{plastic_produced:,.0f} kg", delta=f"~{plastic_to_cars:,.0f} cars worth")
            #st.metric("Plastic entered ocean today (kilograms)", f"{ocean_plastic:,.0f} kg", delta=f"~{ocean_to_statues:,.0f} Statues of Liberty")
            #st.metric("Microplastic ingested today (mg)", f"{microplastic:,.0f} mg", delta=f"~{credit_card_equiv:.0f}% credit card/week")
            #st.metric("Forest lost today (acres)", f"{acres_lost:,.0f} acres", delta=f"~{k_format(acres_to_football)} football fields")
            #st.metric("CO₂ emitted today (metric tons)", f"{co2_emitted:,.0f} t CO₂", delta=f"~{k_format(pyramids)} Great Pyramids of Giza")

        #with placeholder.container():
            #st.metric("Plastic produced today", f"{plastic_produced:,.0f} kg", delta=f"≈ {plastic_to_cars:,.0f} cars")
            #st.metric("Plastic entered ocean today", f"{ocean_plastic:,.0f} kg", delta=f"≈ {ocean_to_statues:,.0f} Statues of Liberty")
            #st.metric("Microplastic ingested today", f"{microplastic:,.0f} mg", delta=f"≈ {credit_card_equiv:.0f}% credit card in a week")
            #st.metric("Forest lost today", f"{acres_lost:,.0f} acres", delta=f"≈ {k_format(acres_to_football)} football fields")
            #st.metric("CO₂ emitted today", f"{co2_emitted:,.0f} t CO₂", delta=f"≈ {k_format(pyramids)} Great Pyramids of Giza")
            #st.metric("Land lost today", f"{ha_lost:,.0f} ha", delta=f"~{ha_to_washdc:.0f}% Washington DC per year")

        def custom_metric(label, value, delta, symbol="≈", color="gray"):
            st.markdown(f"""
                <div style="
                    background-color:#f0f2f6;
                    padding: 1rem;
                    border-radius: 0.5rem;
                    width: 280px;
                    margin-bottom: 1rem;
                    display: inline-block;
                    font-family: 'Segoe UI', sans-serif;
                ">
                    <div style="color: gray; font-size: 0.85rem;">{label}</div>
                    <div style="font-size: 1.5rem; font-weight: bold; margin: 0.25rem 0;">{value}</div>
                    <div style="font-size: 0.85rem; color: {color};">{symbol} {delta}</div>
                </div>
            """, unsafe_allow_html=True)

        with placeholder.container():
            custom_metric("Plastic produced today", f"{plastic_produced:,.0f} kg", f"{plastic_to_cars:,.0f} cars")
            custom_metric("Plastic entered ocean today", f"{ocean_plastic:,.0f} kg", f"{ocean_to_statues:,.0f} Statues of Liberty")
            custom_metric("Microplastic ingested today", f"{microplastic:,.0f} mg", f"{credit_card_equiv:.0f}% of a credit card in a week")
            # custom_metric("Forest lost today (acres)", f"{acres_lost:,.0f} acres", f"{k_format(acres_to_football)} football fields")
            # custom_metric("CO₂ emitted today", f"{co2_emitted:,.0f} t CO₂", f"{k_format(pyramids)} Great Pyramids of Giza")
            # custom_metric("Land lost today (hectares)", f"{ha_lost:,.0f} ha", f"{ha_to_washdc:.0f}% Washington DC/year")


        time.sleep(UPDATE_INTERVAL_SEC)


if __name__ == "__main__":
    main()
