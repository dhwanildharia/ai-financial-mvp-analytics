import pandas as pd

def merge_data():
    # Load daily gold prices
    gold = pd.read_csv('data/gold_prices.csv', parse_dates=['Date'])
    gold = gold[['Date', 'Gold_Price']]

    # Load SPY data, extracting Open and Close
    spy = pd.read_csv('data/spy_data.csv', skiprows=[1, 2])
    spy.rename(columns={'Price': 'Date', 'Open': 'SPY_Open', 'Close': 'SPY_Close'}, inplace=True)
    spy['Date'] = pd.to_datetime(spy['Date'], errors='coerce')
    spy = spy[['Date', 'SPY_Open', 'SPY_Close']].dropna()

    # Load Sensex data, extracting Open and Close
    sensex = pd.read_csv('data/sensex_data.csv', parse_dates=['Date'])
    sensex.rename(columns={'Open': 'Sensex_Open', 'Close': 'Sensex_Close'}, inplace=True)
    sensex = sensex[['Date', 'Sensex_Open', 'Sensex_Close']].dropna()

    # Merge datasets on Date
    merged = pd.merge(gold, spy, on='Date', how='inner')
    merged = pd.merge(merged, sensex, on='Date', how='inner')
    merged.sort_values('Date', inplace=True)

    # Save merged data
    merged.to_csv('data/merged_data_open_close.csv', index=False)
    print('✅ Merged data saved to data/merged_data_open_close.csv')

if __name__ == '__main__':
    merge_data()