
import json
from pathlib import Path

def save_product_json(product: dict, output_dir="data/structured"):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    mpn=str(product.get("manufacturer_part_number","product")).replace("/","_")
    path=Path(output_dir)/f"{mpn}.json"
    path.write_text(json.dumps(product, indent=2, default=str), encoding="utf-8")
    return str(path)
