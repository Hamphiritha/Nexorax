
import pandas as pd
import numpy as np
import re

NUMERIC_COLS = ["rated_power_kw","voltage_v","frequency_hz","speed_rpm","current_a","efficiency_percent","power_factor","ambient_temperature_c","weight_kg","poles"]

def clean_motor_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]
    df = df.drop_duplicates(subset=["brand","manufacturer_part_number"], keep="first")
    for c in NUMERIC_COLS:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    for c in ["brand","motor_type","ip_rating","insulation_class","mounting","duty","frame_size","series"]:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()
    if "ip_rating" in df.columns:
        df["ip_rating"] = df["ip_rating"].str.upper().str.extract(r"(IP\d{2})", expand=False)
    if "duty" in df.columns:
        df["duty"] = df["duty"].str.upper().str.extract(r"(S\d)", expand=False)
    if "poles" not in df.columns or df["poles"].isna().all():
        if "speed_rpm" in df.columns:
            df["poles"] = np.select(
                [df["speed_rpm"] >= 2500, df["speed_rpm"].between(1200, 1800), df["speed_rpm"] < 1200],
                [2,4,6], default=np.nan)
    return df
