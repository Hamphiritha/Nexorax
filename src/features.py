
import pandas as pd
import numpy as np

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "rated_power_kw" in df:
        df["power_class"] = pd.cut(df["rated_power_kw"], bins=[0,3,15,55,np.inf],
                                   labels=["Small","Medium","Large","Heavy"], include_lowest=True)
    if "speed_rpm" in df:
        df["speed_band"] = pd.cut(df["speed_rpm"], bins=[0,1200,2000,4000],
                                  labels=["Low","Medium","High"], include_lowest=True)
    if "efficiency_percent" in df:
        df["efficiency_band"] = pd.cut(df["efficiency_percent"], bins=[0,85,90,95,100],
                                       labels=["Basic","Good","High","Premium"], include_lowest=True)
    return df
