import pandas as pd

class SimpleGridTrading:
    def __init__(self, symbol, initial_price, grid_spacing_pct, profit_target_pct, num_grids=10, budget=1000):
        self.symbol = symbol
        self.initial_price = initial_price
        self.grid_spacing_pct = grid_spacing_pct
        self.num_grids = num_grids
        self.budget = budget
        self.profit_target_pct = profit_target_pct
        self.position_size = budget / num_grids

        self.grid_levels = self._calculate_grid_levels()

        self.cash = budget
        self.positions = {}
        self.total_crypto = 0.0
        self.realized_profit = 0.0
        self.log_format = {
            f'Quantity ({self.symbol})': '{:.6f}',
        }

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

        for level_idx, level in enumerate(self.grid_levels):
            if current_price <= level and level not in self.positions:
                if self.cash >= self.position_size:
                    quantity = self.position_size / current_price

                    self.positions[level] = {
                        'quantity': quantity,
                        'buy_price': current_price,
                        'bought': quantity * current_price
                    }

                    previous_cash = self.cash
                    self.cash -= self.position_size
                    self.total_crypto += quantity

                    position = self.positions[level]
                    order = {
                        'Type': '🟢 BUY',
                        'Cash in ($)': previous_cash,
                        'Grid Level': level_idx,
                        'Grid Price ($)': level,
                        f'Quantity ({self.symbol})': quantity,
                        'Buy Price ($)': current_price,
                        'Sell Price ($)': None, 
                        'Minimum Selling Price ($)': current_price * (1 + self.profit_target_pct / 100),
                        'Bought ($)': quantity * current_price,
                        'Sold ($)': None,
                        'Profit ($)': None,
                        'Active Grids': len(self.positions) - 1,
                        'Cash Out ($)': self.cash,
                    }
                    executed_orders.append(order)
                    print(self.stringify_order(order))

        return executed_orders

    def execute_sell_order(self, current_price):
        executed_orders = []

        for level_idx, (level, position) in reversed(list(enumerate(self.positions.items()))):
            target_price = position['buy_price'] * (1 + self.profit_target_pct / 100)

            if current_price >= target_price:
                sell_amount = position['quantity'] * current_price
                profit = sell_amount - (position['buy_price'] * position['quantity'])

                previous_cash = self.cash
                self.cash += sell_amount
                self.total_crypto -= position['quantity']
                self.realized_profit += profit

                order = {
                    'Type': '🔴 SELL',
                    'Cash in ($)': previous_cash,
                    'Grid Level': level_idx,
                    'Grid Price ($)': level + 1,
                    f'Quantity ({self.symbol})': position['quantity'],
                    'Buy Price ($)': position['buy_price'],
                    'Sell Price ($)': current_price, 
                    'Minimum Selling Price ($)': target_price,
                    'Bought ($)': position['bought'],
                    'Sold ($)': current_price * position['quantity'],
                    'Profit ($)': profit,
                    'Active Grids': len(self.positions) - 1,
                    'Cash Out ($)': self.cash,
                }
                executed_orders.append(order)
                print(self.stringify_order(order))
                del self.positions[level]

        return executed_orders

    def stringify_order(self, order):
        return " -> TRANSACTION: " + " | ".join(
            f"{k}: {self.log_format.get(k, '{:,.2f}').format(v)}" if isinstance(v, float) else f"{k}: {v}"
            for k, v in order.items()
        )

    def simulate_grid_trading(self, price_data):
        print(f"\nSimulating Grid Trading untuk {self.symbol}...")
        print("Starting at current price:", price_data.iloc[0]['Close'])

        trading_log = []
        portfolio_history = []

        for date, row in price_data.iterrows():
            current_price = float(row['Close'])
            print(f"Date: {date}, Current price: {current_price:,.2f}")
            
            buy_orders = self.execute_buy_order(current_price)
            sell_orders = self.execute_sell_order(current_price)
            
            transaction_type = ''
            executed_grid_levels = []
            orders = buy_orders + sell_orders
            for order in orders:
                order['date'] = date
                trading_log.append(order)
                transaction_type = order['Type']
                executed_grid_levels.append(order['Grid Level'])

            crypto_value = self.total_crypto * current_price
            total_value = self.cash + crypto_value

            portfolio_history.append({
                'Date': date,
                'Closing Price ($)': current_price,
                'Transaction Type': transaction_type,
                'Number of Transactions': len(orders),
                'Levels': executed_grid_levels,
                'Active Grids': len(self.positions),
                f'Asset ({self.symbol})': self.total_crypto,
                'Cash ($)': self.cash,
                'Valuation ($)': total_value,
            })

        return pd.DataFrame(trading_log), pd.DataFrame(portfolio_history)
    
    def analyze_performance(self, portfolio_history, trading_log, price_data):
        """
        Analyze grid trading performance vs buy & hold
        """
        initial_investment = self.budget
        final_value = portfolio_history['Valuation ($)'].iloc[-1]
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
        print(f"Crypto Holdings Value:  ${portfolio_history[f'Asset ({self.symbol})'].iloc[-1]:.2f}")
        print(f"Active Positions:       {len(self.positions)}")

        # Win rate calculation
        sell_trades = trading_log[trading_log['Type'] == '🔴 SELL']
        buy_trades = trading_log[trading_log['Type'] == '🟢 BUY']
        win_rate = len(sell_trades) / len(buy_trades) * 100

        print(f"Win Rate:               {win_rate:.1f}%")

        if not sell_trades.empty:
            avg_profit = sell_trades['Profit ($)'].mean()
            print(f"Average Profit/Trade:   ${avg_profit:.2f}")