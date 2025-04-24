# Gold vs S&P 500 vs BSE Sensex — Merged Data Version

This Streamlit app reads a single `merged_data.csv` containing daily:
- Gold_Price
- SPY_Close
- Sensex_Close

## Files
- `merged_data.csv` — Combined dataset (Date, Gold_Price, SPY_Close, Sensex_Close)
- `app.py` — Streamlit application
- `requirements.txt` — Python dependencies

## Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Cloud
1. Push this repo to GitHub.
2. Create new app on Streamlit Cloud, select `app.py`.
3. Deploy and enjoy!