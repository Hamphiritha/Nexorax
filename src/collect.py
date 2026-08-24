
import os
import requests
import pandas as pd
from pathlib import Path

def download_from_sources(sources_csv="data/sources.csv", output_dir="data/raw/pdfs"):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    sources=pd.read_csv(sources_csv)
    results=[]
    for _,row in sources.iterrows():
        url=str(row.get("datasheet_url","")).strip()
        mpn=str(row.get("manufacturer_part_number","unknown")).strip()
        if not url or url.lower()=="nan":
            results.append({"mpn":mpn,"status":"SKIPPED","reason":"No datasheet_url"})
            continue
        try:
            r=requests.get(url, timeout=30, headers={"User-Agent":"TwinIQ research prototype"})
            r.raise_for_status()
            path=Path(output_dir)/f"{mpn}.pdf"
            path.write_bytes(r.content)
            results.append({"mpn":mpn,"status":"DOWNLOADED","path":str(path)})
        except Exception as e:
            results.append({"mpn":mpn,"status":"ERROR","reason":str(e)})
    return pd.DataFrame(results)
