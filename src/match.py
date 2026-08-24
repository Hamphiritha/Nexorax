import re
import pandas as pd


def parse_requirement(text: str) -> dict:
    t = text.lower()
    out = {}
    patterns = {
        "rated_power_kw": r"(\d+(?:\.\d+)?)\s*kw",
        "voltage_v": r"(\d+(?:\.\d+)?)\s*v(?:olts?)?",
        "frequency_hz": r"(\d+(?:\.\d+)?)\s*hz",
        "speed_rpm": r"(\d+(?:\.\d+)?)\s*rpm",
        "ip_rating": r"\b(ip\s*\d{2})\b",
        "duty": r"\b(s\s*1|continuous)\b",
    }
    for key, pat in patterns.items():
        m = re.search(pat, t)
        if m:
            val = m.group(1)
            if key in ["rated_power_kw", "voltage_v", "frequency_hz", "speed_rpm"]:
                out[key] = float(val)
            elif key == "ip_rating":
                out[key] = val.replace(" ", "").upper()
            else:
                out[key] = "S1"
    if "three phase" in t or "three-phase" in t or "3-phase" in t:
        out["motor_type"] = "three-phase"
    return out


def match_product(product: dict, req: dict) -> dict:
    checks = []

    def add(name, required, actual, status, note):
        checks.append({
            "requirement": name,
            "required": required,
            "actual": actual,
            "status": status,
            "note": note,
        })

    for field, label, tol in [
        ("rated_power_kw", "Power (kW)", 0.10),
        ("voltage_v", "Voltage (V)", 0.10),
        ("frequency_hz", "Frequency (Hz)", 0.02),
        ("speed_rpm", "Speed (RPM)", 0.10),
    ]:
        if field in req:
            actual = product.get(field)
            required = req[field]
            if actual is None or pd.isna(actual):
                add(label, required, actual, "UNKNOWN", "Product value missing")
            else:
                allowed = max(abs(float(required)) * tol, 1 if field != "speed_rpm" else 50)
                status = "PASS" if abs(float(actual) - float(required)) <= allowed else "FAIL"
                add(label, required, actual, status, f"Tolerance: {tol * 100:.0f}%")

    for field, label in [("ip_rating", "IP Rating"), ("duty", "Duty")]:
        if field in req:
            actual = product.get(field)
            missing = actual is None or actual == "" or (isinstance(actual, float) and pd.isna(actual))
            status = "UNKNOWN" if missing else ("PASS" if str(actual).upper() == str(req[field]).upper() else "FAIL")
            add(label, req[field], actual, status, "Exact match")

    passes = sum(c["status"] == "PASS" for c in checks)
    fails = sum(c["status"] == "FAIL" for c in checks)
    unknown = sum(c["status"] == "UNKNOWN" for c in checks)
    known = passes + fails
    score = round(100 * passes / known, 1) if known else 0.0
    verdict = "SUITABLE" if known and score >= 80 else ("PARTIALLY SUITABLE" if score >= 50 else "NOT SUITABLE")
    return {"verdict": verdict, "score": score, "checks": checks, "unknown_count": unknown}


def recommend_products(catalog: pd.DataFrame, req: dict, top_n: int = 5, extra_products=None) -> list:
    """Rank catalog products against a parsed requirement using the same explainable rules."""
    candidates = [row.dropna().to_dict() for _, row in catalog.iterrows()]
    if extra_products:
        candidates.extend(extra_products)

    recommendations = []
    for product in candidates:
        result = match_product(product, req)
        passes = sum(c["status"] == "PASS" for c in result["checks"])
        fails = sum(c["status"] == "FAIL" for c in result["checks"])
        recommendations.append({
            "product": product,
            "result": result,
            "passes": passes,
            "fails": fails,
        })

    # Highest compatibility first; then fewer failures; then more passed requirements.
    recommendations.sort(
        key=lambda x: (x["result"]["score"], -x["fails"], x["passes"]),
        reverse=True,
    )
    return recommendations[:top_n]
