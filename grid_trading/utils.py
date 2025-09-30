import yfinance as yf
import pandas as pd

def load_crypto_trading_data(symbol, start_date, end_date):
	data = yf.download(f'{symbol}-USD', start=start_date, end=end_date, progress=False)
	
	if isinstance(data.columns, pd.MultiIndex):
		data.columns = [col[0] for col in data.columns]
		
	data['Daily_Return'] = data['Close'].pct_change()
	data['Daily_Range_Pct'] = (data['High'] - data['Low']) / data['Close'] * 100

	print(f"Loaded {len(data)} records for {symbol}")

	if len(data) > 0:
		return data
	else:
		return None