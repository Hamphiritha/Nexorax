
# TwinIQ — Complete Electric Motors Project

This package keeps the original hackathon requirement:

> **Transform minimal product information into rich, structured, commerce-ready product intelligence, then explain whether a product is suitable for a user requirement.**

## What is included
- `notebooks/TwinIQ_Electric_Motors_Complete.ipynb` — main step-by-step notebook, organized like the supplied DSV notebook.
- `data/raw/electric_motors_seed.csv` — starter development dataset.
- `data/sources.csv` — fill this with official product/datasheet URLs for real collection.
- `src/collect.py` — downloads public datasheets listed in `sources.csv`.
- `src/pdf_extract.py` — page-wise PDF extraction.
- `src/clean.py` — cleaning and standardization.
- `src/features.py` — feature engineering.
- `src/match.py` — requirement parser and deterministic suitability engine.
- `app.py` — Streamlit demo.
- `requirements.txt` — Python packages.

## Important dataset note
The included seed dataset is synthetic and is provided only so that the notebook and app run immediately. For a final hackathon submission, replace or extend it with records extracted from official manufacturer product pages and datasheets, and keep source evidence.

## Run
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## Notebook workflow
1. Week 1 — Problem understanding and schema
2. Week 2 — Dataset collection and loading
3. Week 3 — Cleaning and validation
4. Week 4 — EDA
5. Week 5 — Feature engineering
6. Week 6 — Dataset learning and compatibility model
7. Week 7 — Dimensionality reduction
8. Final — Structured intelligence + requirement match + Streamlit deployment
