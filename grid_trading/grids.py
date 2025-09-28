import pandas as pd
from datetime import datetime

class SimpleGridTrading:
    def __init__(self, symbol, initial_price, grid_spacing_pct, num_grids=10, budget=1000):
        self.symbol = symbol
        self.initial_price = initial_price
        self.grid_spacing_pct = grid_spacing_pct
        self.num_grids = num_grids
        self.budget = budget

        self.position_size = budget / num_grids

        self.grid_levels = self._calculate_grid_levels()

        self.cash = budget
        self.positions = {}
        self.total_crypto = 0.0
        self.realized_profit = 0.0

        print(f"Grid Trading Setup for {symbol}")
        print(f"Initial Price: ${initial_price:,.2f}")
        print(f"Grid Spacing: {grid_spacing_pct}%")
        print(f"Number of Grids: {num_grids}")
        print(f"Budget: ${budget:,}")
        print(f"Position Size per Grid: ${self.position_size:.2f}")

    def _calculate_grid_levels(self):
        levels = []
        for i in range(1, self.num_grids + 1):
            level = self.initial_price * (1 - i * self.grid_spacing_pct / 100)
            levels.append(level)
        return levels
	
    def display_grid_setup(self):
        print(f"\nGrid Levels untuk {self.symbol}:")
        print("-" * 50)

        for i, level in enumerate(self.grid_levels):
            discount = ((self.initial_price - level) / self.initial_price) * 100
            quantity = self.position_size / level
            print(f"Grid {i+1:2d}: ${level:8,.2f} | Discount: {discount:5.2f}% | Buy Qty: {quantity:.6f}")
        
        print("-" * 50)
        print(f"Total Budget Ready: ${self.budget:,}")

    def execute_buy_order(self, current_price):
        executed_orders = []

        for level in self.grid_levels:
            # Check if price touches level dan kita belum punya position di level ini
            if current_price <= level and level not in self.positions:
                # Check if kita punya enough cash
                if self.cash >= self.position_size:
                    quantity = self.position_size / level

                    # Execute buy
                    self.positions[level] = {
                        'quantity': quantity,
                        'buy_price': level,
                        'timestamp': datetime.now()
                    }

                    self.cash -= self.position_size
                    self.total_crypto += quantity
                    
                    executed_orders.append({
                        'type': 'BUY',
                        'price': level,
                        'quantity': quantity,
                        'amount': self.position_size
                    })
                    
                    print(f"🟢 BUY : {quantity:.4f} {self.symbol} at ${level:,.2f} | Remaining Cash: ${self.cash:,.2f}")
                    
        return executed_orders

    def execute_sell_order(self, current_price, profit_target_pct=3.4):
        executed_orders = []

        for level, position in list(self.positions.items()):
            target_price = position['buy_price'] * (1 + profit_target_pct / 100)

            if current_price >= target_price:
                sell_amount = position['quantity'] * current_price
                profit = sell_amount - self.position_size

                self.cash += sell_amount
                self.total_crypto -= position['quantity']
                self.realized_profit += profit

                executed_orders.append({
                    'type' : 'SELL',
                    'buy_price': position['buy_price'],
                    'sell_price': current_price,
                    'quantity': position['quantity'],
                    'profit': profit
                })

                print(f"🔴 SELL: {position['quantity']:.4f} {self.symbol} at ${level:,.2f} | Remaining Cash: ${self.cash:,.2f} | target_pirce: {target_price} | current_price: {current_price}")

                del self.positions[level]

        return executed_orders

    def simulate_grid_trading(self, price_data, profit_target_pct=3.4):
        print(f"\nSimulating Grid Trading untuk {self.symbol}...")

        trading_log = []
        portfolio_history = []

        for date, row in price_data.iterrows():
            current_price = float(row['Close'])
            
            # Execute trading logic
            buy_orders = self.execute_buy_order(current_price)
            sell_orders = self.execute_sell_order(current_price, profit_target_pct=profit_target_pct)
            
            # Log all trades
            for order in buy_orders + sell_orders:
                order['date'] = date
                trading_log.append(order)

            # Record portfolio state
            crypto_value = self.total_crypto * current_price
            total_value = self.cash + crypto_value

            portfolio_history.append({
                'date': date,
                'price': current_price,
                'cash': self.cash,
                'crypto_value': crypto_value,
                'total_value': total_value,
                'realized_profit': self.realized_profit,
                'active_positions': len(self.positions)
            })

        return pd.DataFrame(trading_log), pd.DataFrame(portfolio_history)
    
    def analyze_performance(self, portfolio_history, trading_log, price_data):
        """
        Analyze grid trading performance vs buy & hold
        """
        initial_investment = self.budget
        final_value = portfolio_history['total_value'].iloc[-1]
        grid_return = (final_value / initial_investment - 1) * 100

        # Buy & hold comparison
        initial_price = float(price_data['Close'].iloc[0])
        final_price = float(price_data['Close'].iloc[-1])
        buy_hold_return = ((final_price / initial_price) - 1) * 100

        print(f"PERFORMANCE ANALYSIS - {self.symbol}")
        print("=" * 50)
        print(f"Initial Investment:      ${initial_investment:,.2f}")
        print(f"Final Portfolio Value:   ${final_value:,.2f}")
        print(f"Grid Trading Return:     {grid_return:+.2f}%")
        print(f"Buy & Hold Return:       {buy_hold_return:+.2f}%")
        print(f"Excess Return:           {(grid_return - buy_hold_return):+.2f}%")

        # Trading Statistics:
        print(f"\nTrading Statistics:")
        print(f"Realized Profit:        ${self.realized_profit:.2f}")
        print(f"Remaining Cash:         ${self.cash:.2f}")
        print(f"Crypto Holdings Value:  ${portfolio_history['crypto_value'].iloc[-1]:.2f}")
        print(f"Active Positions:       {len(self.positions)}")

        # Win rate calculation
        sell_trades = trading_log[trading_log['type'] == 'SELL']
        buy_trades = trading_log[trading_log['type'] == 'BUY']
        win_rate = len(sell_trades) / len(buy_trades) * 100

        print(f"Win Rate:               {win_rate:.1f}%")

        if not sell_trades.empty:
            avg_profit = sell_trades['profit'].mean()
            print(f"Average Profit/Trade:   ${avg_profit:.2f}")