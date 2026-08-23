import streamlit as st
import pandas as pd
from pathlib import Path
from src.clean import clean_motor_data
from src.features import add_features
from src.match import parse_requirement, match_product, recommend_products
from src.pdf_extract import analyze_motor_pdf

st.set_page_config(page_title="TwinIQ | Industrial Intelligence", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');
:root { --bg:#08111f; --panel:#101b2d; --panel2:#0c1626; --line:rgba(148,163,184,.16); --text:#e8eef8; --muted:#94a3b8; --cyan:#35d3ff; --violet:#8b5cf6; --green:#38e08f; }
.stApp { background: radial-gradient(circle at 12% 4%, rgba(53,211,255,.12), transparent 25%), radial-gradient(circle at 88% 8%, rgba(139,92,246,.12), transparent 26%), var(--bg); color:var(--text); font-family:'Inter',sans-serif; }
#MainMenu, footer, header { visibility:hidden; }
.block-container { padding-top:1.4rem; max-width:1450px; }
.hero { padding:1.4rem 1.7rem; border:1px solid var(--line); border-radius:22px; background:linear-gradient(135deg,rgba(16,27,45,.94),rgba(10,20,35,.82)); box-shadow:0 20px 50px rgba(0,0,0,.22); margin-bottom:1.25rem; }
.hero h1 { font-family:'Space Grotesk',sans-serif; margin:0; font-size:2.35rem; letter-spacing:-1px; background:linear-gradient(90deg,#fff,#9bdfff); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.hero p { color:var(--muted); margin:.4rem 0 0; font-size:1rem; }
.badge { display:inline-block; margin-bottom:.65rem; padding:.35rem .65rem; border-radius:999px; color:#9be8ff; background:rgba(53,211,255,.1); border:1px solid rgba(53,211,255,.25); font-size:.75rem; font-weight:700; letter-spacing:.06em; }
section[data-testid="stSidebar"] { background:linear-gradient(180deg,#0b1525,#08111f); border-right:1px solid var(--line); }
section[data-testid="stSidebar"] * { color:#dce7f5; }
.stTabs [data-baseweb="tab-list"] { gap:.45rem; background:rgba(16,27,45,.62); padding:.45rem; border:1px solid var(--line); border-radius:16px; }
.stTabs [data-baseweb="tab"] { height:42px; border-radius:11px; padding:0 15px; color:#9fb0c7; font-weight:600; }
.stTabs [aria-selected="true"] { background:linear-gradient(90deg,rgba(53,211,255,.17),rgba(139,92,246,.17)); color:#fff !important; }
div[data-testid="stMetric"] { background:linear-gradient(145deg,rgba(16,27,45,.92),rgba(10,19,33,.92)); border:1px solid var(--line); padding:1rem; border-radius:16px; }
.stButton>button, .stDownloadButton>button { border-radius:12px; border:1px solid rgba(53,211,255,.28); background:linear-gradient(90deg,#0d7490,#2563eb); color:white; font-weight:700; min-height:42px; box-shadow:0 10px 24px rgba(37,99,235,.16); }
.stButton>button:hover, .stDownloadButton>button:hover { transform:translateY(-1px); border-color:#7de7ff; }
div[data-baseweb="input"]>div, div[data-baseweb="textarea"]>div { background:#0b1626 !important; border-color:var(--line) !important; border-radius:12px !important; color:#fff !important; }
[data-testid="stFileUploader"] { border:1px dashed rgba(53,211,255,.35); border-radius:18px; padding:.5rem; background:rgba(53,211,255,.03); }
[data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:14px; overflow:hidden; }
hr { border-color:var(--line) !important; }
</style>""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div class="badge">INDUSTRIAL AI · PDF-FIRST INTELLIGENCE</div>
  <h1>⚡ TwinIQ</h1>
  <p>Transform electric motor datasheets into trusted product intelligence, explain suitability, and recommend the best alternatives.</p>
</div>
""", unsafe_allow_html=True)


DATA = Path("data/raw/electric_motors_seed.csv")
df = add_features(clean_motor_data(pd.read_csv(DATA)))

with st.sidebar:
    st.markdown("### ⚙️ TwinIQ Control Center")
    st.caption("Industrial product intelligence workspace")
    st.divider()
    st.metric("Catalog Motors", len(df))
    st.metric("PDF Product", "Ready" if st.session_state.get("pdf_product") else "Not analyzed")
    st.divider()
    st.markdown("**Quick workflow**")
    st.caption("1. Upload PDF → 2. Extract specifications → 3. Match requirements → 4. Explore recommendations")
    st.divider()
    st.caption("Electric Motors · Explainable AI")

if "pdf_product" not in st.session_state:
    st.session_state.pdf_product = None
if "pdf_evidence" not in st.session_state:
    st.session_state.pdf_evidence = {}
if "pdf_pages" not in st.session_state:
    st.session_state.pdf_pages = []

tabs = st.tabs(["PDF Analysis", "Product Intelligence", "Requirement Match", "Recommendations Catalog", "Product Catalog", "Raw Extraction", "Dataset Learning"])

with tabs[0]:
    st.markdown("## 📄 Analyze Technical Document")
    st.caption("Upload a manufacturer datasheet or catalogue. TwinIQ extracts evidence-backed specifications automatically.")
    st.write("Upload a manufacturer datasheet, catalogue, or technical document. TwinIQ extracts specifications directly from the PDF, so you do not need to type the product details manually.")
    uploaded_pdf = st.file_uploader("Upload Electric Motor PDF", type=["pdf"], key="motor_pdf")
    if uploaded_pdf is not None:
        st.info(f"Selected file: {uploaded_pdf.name}")
        if st.button("Analyze PDF", type="primary"):
            with st.spinner("Extracting pages and analyzing motor specifications..."):
                result = analyze_motor_pdf(uploaded_pdf.getvalue(), uploaded_pdf.name)
                st.session_state.pdf_product = result["product"]
                st.session_state.pdf_evidence = result["evidence"]
                st.session_state.pdf_pages = result["pages"]
            st.success("PDF analysis completed.")

    if st.session_state.pdf_product:
        product = st.session_state.pdf_product
        extracted_count = sum(v is not None and v != "" for k, v in product.items() if k not in {"source_type", "source_reference", "description", "motor_type"})
        st.metric("Extracted Specification Fields", extracted_count)
        st.subheader("Structured Product Intelligence")
        st.json({k: v for k, v in product.items() if v is not None})
        if st.session_state.pdf_evidence:
            st.subheader("Evidence and Traceability")
            rows = []
            for field, ev in st.session_state.pdf_evidence.items():
                rows.append({"field": field, "page": ev["page"], "evidence": ev["snippet"]})
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.download_button("Download Extracted Product JSON", pd.Series(product).to_json(indent=2), "twin_iq_extracted_motor.json", mime="application/json")

with tabs[1]:
    st.subheader("Product Intelligence")
    mode = st.radio("Choose input method", ["Upload PDF (Recommended)", "Manual product input"], horizontal=True)

    if mode == "Upload PDF (Recommended)":
        if st.session_state.pdf_product:
            st.success("A PDF has already been analyzed. The extracted product intelligence is ready to use.")
            st.json({k: v for k, v in st.session_state.pdf_product.items() if v is not None})
        else:
            st.warning("First go to the PDF Analysis tab, upload a motor PDF, and click Analyze PDF.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            brand = st.text_input("Brand", "Siemens")
        with c2:
            mpn = st.text_input("Manufacturer Part Number", "SI-15000-4P-001")
        desc = st.text_area("Short Product Description", "15 kW three-phase industrial motor")
        if st.button("Generate Product Intelligence"):
            found = df[(df["brand"].str.lower() == brand.lower()) | (df["manufacturer_part_number"].str.lower() == mpn.lower())]
            if found.empty:
                st.warning("Product not found in the local dataset. Use PDF Analysis to analyze its official datasheet.")
            else:
                st.json(found.iloc[0].dropna().to_dict())

with tabs[2]:
    st.markdown("## 🎯 Requirement Intelligence")
    st.caption("Describe the operating need in natural language and get an explainable engineering match.")
    req_text = st.text_area("Describe what you need", "I need a three-phase industrial motor with 15 kW power, 415 V, 50 Hz, around 1500 RPM, IP55 and continuous operation.")

    options = ["Uploaded PDF product"] if st.session_state.pdf_product else []
    options += df["manufacturer_part_number"].tolist()
    selected = st.selectbox("Match against", options)

    if st.button("Analyze Suitability", type="primary"):
        if selected == "Uploaded PDF product":
            product = st.session_state.pdf_product
        else:
            product = df.loc[df["manufacturer_part_number"] == selected].iloc[0].to_dict()
        req = parse_requirement(req_text)
        result = match_product(product, req)
        st.metric("Compatibility Score", f'{result["score"]}%')
        st.subheader(result["verdict"])
        st.dataframe(pd.DataFrame(result["checks"]), use_container_width=True, hide_index=True)
        st.subheader("Product Used for Matching")
        st.json({k: v for k, v in product.items() if v is not None})

with tabs[3]:
    st.markdown("## ✨ Smart Recommendations Catalog")
    st.caption("One requirement. Ranked alternatives. Clear reasons for every recommendation.")
    st.write("Describe your requirement once and TwinIQ ranks the most suitable motors from the catalog using the same explainable matching rules.")
    rec_text = st.text_area(
        "What motor do you need?",
        "I need a three-phase industrial motor with 15 kW power, 415 V, 50 Hz, around 1500 RPM, IP55 and continuous operation.",
        key="recommendation_requirement",
    )
    top_n = st.slider("Number of recommendations", min_value=3, max_value=min(10, len(df)), value=min(5, len(df)))

    if st.button("Find Best Recommendations", type="primary"):
        req = parse_requirement(rec_text)
        if not req:
            st.error("Please include at least one measurable requirement such as kW, V, Hz, RPM, IP rating, or continuous/S1 duty.")
        else:
            extras = [st.session_state.pdf_product] if st.session_state.pdf_product else None
            recs = recommend_products(df, req, top_n=top_n, extra_products=extras)
            st.subheader("Top Recommended Motors")
            summary_rows = []
            for rank, item in enumerate(recs, start=1):
                product = item["product"]
                result = item["result"]
                summary_rows.append({
                    "Rank": rank,
                    "Part Number": product.get("manufacturer_part_number", "Unknown"),
                    "Brand": product.get("brand", "Unknown"),
                    "Power (kW)": product.get("rated_power_kw"),
                    "Voltage (V)": product.get("voltage_v"),
                    "Speed (RPM)": product.get("speed_rpm"),
                    "IP Rating": product.get("ip_rating"),
                    "Compatibility": f'{result["score"]}%',
                    "Verdict": result["verdict"],
                })
            st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)

            for rank, item in enumerate(recs, start=1):
                product = item["product"]
                result = item["result"]
                label = f'#{rank} — {product.get("manufacturer_part_number", "Unknown Product")} | {result["score"]}% | {result["verdict"]}'
                with st.expander(label, expanded=(rank == 1)):
                    st.write("**Why TwinIQ recommends it**")
                    passed = [c["requirement"] for c in result["checks"] if c["status"] == "PASS"]
                    failed = [c["requirement"] for c in result["checks"] if c["status"] == "FAIL"]
                    unknown = [c["requirement"] for c in result["checks"] if c["status"] == "UNKNOWN"]
                    if passed:
                        st.success("Matches: " + ", ".join(passed))
                    if failed:
                        st.warning("Does not match: " + ", ".join(failed))
                    if unknown:
                        st.info("Missing product data: " + ", ".join(unknown))
                    st.dataframe(pd.DataFrame(result["checks"]), use_container_width=True, hide_index=True)
                    st.json({k: v for k, v in product.items() if v is not None})

with tabs[4]:
    st.markdown("## 🗂️ Verified Product Catalog")
    st.caption("Browse the structured electric-motor knowledge base.")
    st.dataframe(df, use_container_width=True)
    if st.session_state.pdf_product:
        st.divider()
        st.write("Latest PDF-analyzed product")
        st.json({k: v for k, v in st.session_state.pdf_product.items() if v is not None})
    st.download_button("Download cleaned catalog CSV", df.to_csv(index=False).encode("utf-8"), "twin_iq_catalog.csv")

with tabs[5]:
    st.markdown("## 🔎 Source Evidence Explorer")
    st.caption("Inspect page-level extracted text for transparency and traceability.")
    if not st.session_state.pdf_pages:
        st.info("Upload and analyze a PDF first.")
    else:
        for page in st.session_state.pdf_pages:
            with st.expander(f"Page {page['page']}"):
                st.text(page["text"] if page["text"].strip() else "No machine-readable text found on this page.")

with tabs[6]:
    st.markdown("## 📊 Dataset Intelligence")
    st.caption("Quick overview of the motor catalog used by TwinIQ.")
    st.write("Rows:", len(df), "| Columns:", len(df.columns))
    st.bar_chart(df["brand"].value_counts())
    st.scatter_chart(df[["rated_power_kw", "efficiency_percent"]].set_index("rated_power_kw"))
