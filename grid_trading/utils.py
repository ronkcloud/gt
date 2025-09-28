import yfinance as yf
import pandas as pd

def load_crypto_trading_data(symbol, start_date=None, end_date=None):
	if symbol == 'BTC':
		data = yf.download('BTC-USD', start='2025-01-01', end='2025-07-31', progress=False)
		
		if isinstance(data.columns, pd.MultiIndex):
			data.columns = [col[0] for col in data.columns]
			
		data['Daily_Return'] = data['Close'].pct_change()
		data['Daily_Range_Pct'] = (data['High'] - data['Low']) / data['Close'] * 100

		print(f"Loaded {len(data)} records for {symbol}")
		return data
	else:
		return None
