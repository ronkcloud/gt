import matplotlib.pyplot as plt

def plot_grid_history(coin_data, trading_log, portofolio_history):
    plt.figure(figsize=(15, 10))

    plt.subplot(2, 2, 1)
    plt.plot(coin_data.index, coin_data['Close'], label='BTC Price', color='black')

    if not trading_log.empty:
        buy_signals = trading_log[trading_log['type'] == 'BUY']
        sell_signals = trading_log[trading_log['type'] == 'SELL']
        
        if not buy_signals.empty:
            plt.scatter(buy_signals['date'], coin_data.loc[buy_signals['date']]['Close'],
                        color='green', marker='^', s=100, alpha=0.7, label='Buy Signal')
        
        if not sell_signals.empty:
            plt.scatter(sell_signals['date'], sell_signals['sell_price'],
                        color='red', marker='v', s=100, alpha=0.7, label='Sell Signal')

    plt.title('BTC Price & Grid Trading Signals')
    plt.title('Portfolio Value Comparison')
    plt.ylabel('Portfolio Value (USD)')
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Plot 3: Cash vs Crypto allocation
    plt.subplot(2, 2, 3)
    plt.plot(portofolio_history['date'], portofolio_history['cash'], label='Cash')
    plt.plot(portofolio_history['date'], portofolio_history['crypto_value'], label='Crypto')
    plt.title('Portfolio Allocation')
    plt.ylabel('Value (USD)')
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Plot 4: Active positions over time
    plt.subplot(2, 2, 4)
    plt.plot(portofolio_history['date'], portofolio_history['active_positions'], label='Active Grid Positions')
    plt.title('Active Grid Positions')
    plt.ylabel('Number of Positions')
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

def plot_grid_history2(th):
    plt.figure(figsize=(10, 5))

    plt.plot(th['Date'], th['Closing Price ($)'], label='Price ($)', color='black')

    buy_signals = th[th['Transaction Type'] == '🟢 BUY']
    sell_signals = th[th['Transaction Type'] == '🔴 SELL']
    
    if not buy_signals.empty:
        plt.scatter(buy_signals['Date'], buy_signals['Closing Price ($)'],
                    color='green', marker='^', s=100, alpha=0.7, label='Buy Signal')
    
    if not sell_signals.empty:
        plt.scatter(sell_signals['Date'], sell_signals['Closing Price ($)'],
                    color='red', marker='v', s=100, alpha=0.7, label='Sell Signal')

    plt.title('Price & Grid Trading Signals')
    plt.ylabel('Portfolio Value ($)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()