import io
import re
import fitz


def extract_pdf_text(pdf_source):
    """Extract text page-by-page from a PDF path, bytes or uploaded file."""
    if isinstance(pdf_source, (bytes, bytearray)):
        doc = fitz.open(stream=pdf_source, filetype="pdf")
    elif hasattr(pdf_source, "read"):
        data = pdf_source.read()
        doc = fitz.open(stream=data, filetype="pdf")
    else:
        doc = fitz.open(pdf_source)

    pages = []
    for i, page in enumerate(doc, start=1):
        pages.append({"page": i, "text": page.get_text("text")})
    doc.close()
    return pages


def _first_match(patterns, text, flags=re.I):
    for pattern in patterns:
        match = re.search(pattern, text, flags)
        if match:
            return match.group(1).strip()
    return None


def _num(value):
    try:
        return float(str(value).replace(",", ""))
    except Exception:
        return None


def analyze_motor_pdf(pdf_source, filename=None):
    """Extract common electric-motor specifications from PDF text using transparent regex rules.

    Every extracted field is accompanied by page-level evidence. Missing values remain None.
    """
    pages = extract_pdf_text(pdf_source)
    full_text = "\n".join(p["text"] for p in pages)
    product = {
        "brand": None,
        "manufacturer_part_number": None,
        "description": None,
        "motor_type": "Electric Motor",
        "rated_power_kw": None,
        "voltage_v": None,
        "frequency_hz": None,
        "speed_rpm": None,
        "current_a": None,
        "efficiency_percent": None,
        "power_factor": None,
        "ip_rating": None,
        "insulation_class": None,
        "mounting": None,
        "duty": None,
        "frame_size": None,
        "ambient_temperature_c": None,
        "weight_kg": None,
        "poles": None,
        "series": None,
        "source_type": "PDF datasheet",
        "source_reference": filename or "Uploaded PDF",
    }
    evidence = {}

    field_patterns = {
        "rated_power_kw": [r"(?:rated\s+)?power\s*[:=]?\s*([0-9]+(?:[.,][0-9]+)?)\s*kW\b", r"\b([0-9]+(?:[.,][0-9]+)?)\s*kW\b"],
        "voltage_v": [r"(?:rated\s+)?voltage\s*[:=]?\s*([0-9]+(?:\s*[-/]\s*[0-9]+)?)\s*V\b", r"\b([0-9]{3,4})\s*V\b"],
        "frequency_hz": [r"(?:frequency|freq\.)\s*[:=]?\s*([0-9]+(?:[.,][0-9]+)?)\s*Hz\b", r"\b([0-9]{2})\s*Hz\b"],
        "speed_rpm": [r"(?:rated\s+)?speed\s*[:=]?\s*([0-9]{3,5})\s*(?:rpm|r/min|min[- ]?1)\b", r"\b([0-9]{3,5})\s*rpm\b"],
        "current_a": [r"(?:rated\s+)?current\s*[:=]?\s*([0-9]+(?:[.,][0-9]+)?)\s*A\b", r"\b([0-9]+(?:[.,][0-9]+)?)\s*A\b"],
        "efficiency_percent": [r"(?:efficiency|η)\s*[:=]?\s*([0-9]+(?:[.,][0-9]+)?)\s*%"],
        "power_factor": [r"(?:power\s*factor|cos\s*φ|cosphi)\s*[:=]?\s*([0-9]+(?:[.,][0-9]+)?)"],
        "ip_rating": [r"\b(IP\s*\d{2,3})\b"],
        "insulation_class": [r"(?:insulation\s+class|thermal\s+class)\s*[:=]?\s*([A-Z])\b"],
        "mounting": [r"(?:mounting|mount)\s*[:=]?\s*(IM\s*[A-Z0-9]+|B\d+|V\d+)\b"],
        "duty": [r"(?:duty|duty\s+type)\s*[:=]?\s*(S\d+)\b"],
        "frame_size": [r"(?:frame\s*(?:size)?|IEC\s+frame)\s*[:=]?\s*([0-9]{2,4}[A-Z]{0,3})\b"],
        "ambient_temperature_c": [r"(?:ambient\s+temperature|max\.\s+ambient)\s*[:=]?\s*([+-]?[0-9]+(?:[.,][0-9]+)?)\s*°?C"],
        "weight_kg": [r"(?:weight|mass)\s*[:=]?\s*([0-9]+(?:[.,][0-9]+)?)\s*kg\b"],
        "poles": [r"(?:number\s+of\s+)?poles\s*[:=]?\s*([2468])\b"],
    }

    for field, patterns in field_patterns.items():
        value = _first_match(patterns, full_text)
        if value is not None:
            if field in {"rated_power_kw", "frequency_hz", "speed_rpm", "current_a", "efficiency_percent", "power_factor", "ambient_temperature_c", "weight_kg", "poles"}:
                value = _num(value)
                if field in {"speed_rpm", "poles"} and value is not None:
                    value = int(value)
            elif field == "voltage_v":
                value = value.replace(" ", "")
                if "/" not in value and "-" not in value:
                    value = _num(value)
            elif field == "ip_rating":
                value = value.replace(" ", "").upper()
            product[field] = value

    # Find page-level evidence for every extracted value.
    for field, value in product.items():
        if value is None or field in {"source_type", "source_reference"}:
            continue
        needle = str(value).lower().replace(".0", "")
        for p in pages:
            if needle and needle in p["text"].lower():
                snippet = " ".join(p["text"].split())
                evidence[field] = {"page": p["page"], "snippet": snippet[:350]}
                break

    # Simple brand detection from known manufacturers. No invented brand is used.
    known_brands = ["Siemens", "ABB", "WEG", "Nidec", "TECO", "Crompton", "CG Power", "Leroy-Somer", "Marathon", "Baldor"]
    for brand in known_brands:
        if re.search(r"\b" + re.escape(brand) + r"\b", full_text, re.I):
            product["brand"] = brand
            break

    # Common part-number labels.
    mpn = _first_match([
        r"(?:manufacturer\s+part\s+number|part\s+number|catalog(?:ue)?\s+number|type)\s*[:#]?\s*([A-Z0-9][A-Z0-9._/-]{3,})"
    ], full_text)
    if mpn:
        product["manufacturer_part_number"] = mpn

    product["description"] = f"Electric motor analyzed from {filename or 'uploaded PDF'}"
    return {"product": product, "pages": pages, "evidence": evidence, "full_text": full_text}
