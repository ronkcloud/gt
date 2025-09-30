from grids import SimpleGridTrading
from utils import load_crypto_trading_data
from plotter import plot_grid_history2

ticker = 'SOL'
coin_data = load_crypto_trading_data(ticker, start_date='2025-08-01', end_date='2025-10-01')
if coin_data is None:
	print("Failed to fetch trading data, exiting.")
	exit(1)

print(f"\n{ticker} Data Sample:")
print(coin_data[['Close', 'Daily_Range_Pct']].head())
initial_coin_price = float(coin_data['Close'].iloc[0])	

grid = SimpleGridTrading(
    symbol=ticker,
    initial_price=initial_coin_price,
    grid_spacing_pct=1.7,
	profit_target_pct=3.4,
    num_grids=18,
    budget=1000
)

trading_log, portofolio_history = grid.simulate_grid_trading(coin_data)
grid.analyze_performance(portofolio_history, trading_log, coin_data)
plot_grid_history2(portofolio_history)