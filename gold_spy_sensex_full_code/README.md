# Gold vs SPY vs Sensex — Complete Project

This repository includes raw data, merge script, and Streamlit app to visualize daily gold prices, SPY open/close, and Sensex open/close.

## Structure
```
.
├── app.py                  # Streamlit application
├── merge_data.py           # Script to merge raw data into merged_data_open_close.csv
├── requirements.txt        # Python dependencies
└── data/
    ├── gold_prices.csv                # Daily gold prices
    ├── spy_data.csv                   # Raw SPY data from CSV
    ├── sensex_data.csv                # Raw Sensex data from CSV
    └── merged_data_open_close.csv     # Pre-merged dataset
```

## Setup & Usage

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. (Optional) Regenerate merged data:
   ```
   python merge_data.py
   ```

3. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

## Deploy on Streamlit Cloud
- Push this repo to GitHub (public).
- On [Streamlit Cloud](https://streamlit.io/cloud), create a new app:
  - Repo: your GitHub repo
  - Main file: `app.py`
- Deploy.