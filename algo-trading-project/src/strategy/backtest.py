"""
Backtest trading strategies.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import get_logger

logger = get_logger(__name__)


class SimpleBacktester:
    """
    Simple backtesting engine for trading strategies.
    """
    
    def __init__(self, initial_capital: float = 100000, commission: float = 0.001):
        """
        Initialize backtester.
        
        Args:
            initial_capital: Starting capital
            commission: Commission rate (e.g., 0.001 for 0.1%)
        """
        self.initial_capital = initial_capital
        self.commission = commission
        self.reset()
    
    def reset(self):
        """Reset backtester state."""
        self.capital = self.initial_capital
        self.position = 0
        self.entry_price = 0
        self.trades = []
        self.equity_curve = []
    
    def execute_trade(self, signal: int, price: float, shares: int = None):
        """
        Execute a trade based on signal.
        
        Args:
            signal: Trading signal (1=buy, -1=sell, 0=hold)
            price: Current price
            shares: Number of shares (if None, uses all available capital)
        """
        if signal == 1 and self.position == 0:  # Buy
            if shares is None:
                shares = int(self.capital / price)
            
            cost = shares * price * (1 + self.commission)
            
            if cost <= self.capital:
                self.position = shares
                self.entry_price = price
                self.capital -= cost
                
                self.trades.append({
                    'type': 'BUY',
                    'price': price,
                    'shares': shares,
                    'capital': self.capital
                })
        
        elif signal == -1 and self.position > 0:  # Sell
            proceeds = self.position * price * (1 - self.commission)
            pnl = proceeds - (self.position * self.entry_price * (1 + self.commission))
            
            self.capital += proceeds
            
            self.trades.append({
                'type': 'SELL',
                'price': price,
                'shares': self.position,
                'pnl': pnl,
                'capital': self.capital
            })
            
            self.position = 0
            self.entry_price = 0
    
    def backtest(self, data: pd.DataFrame, signal_column: str = 'combined_signal') -> dict:
        """
        Run backtest on historical data.
        
        Args:
            data: DataFrame with OHLCV and signals
            signal_column: Name of signal column
        
        Returns:
            Dictionary with backtest results
        """
        self.reset()
        
        for idx, row in data.iterrows():
            signal = row[signal_column] if signal_column in row else 0
            price = row['Close']
            
            self.execute_trade(int(signal), price)
            
            # Track equity
            equity = self.capital + (self.position * price)
            self.equity_curve.append({
                'date': idx,
                'equity': equity,
                'position': self.position
            })
        
        # Close any open position at end
        if self.position > 0:
            last_price = data.iloc[-1]['Close']
            self.execute_trade(-1, last_price)
        
        return self.calculate_metrics()
    
    def calculate_metrics(self) -> dict:
        """
        Calculate backtest performance metrics.
        
        Returns:
            Dictionary with performance metrics
        """
        equity_df = pd.DataFrame(self.equity_curve)
        
        final_equity = equity_df['equity'].iloc[-1]
        total_return = (final_equity - self.initial_capital) / self.initial_capital
        
        # Calculate returns
        equity_df['returns'] = equity_df['equity'].pct_change()
        
        # Sharpe ratio (assuming 252 trading days)
        sharpe = (equity_df['returns'].mean() / equity_df['returns'].std()) * np.sqrt(252)
        
        # Max drawdown
        equity_df['cummax'] = equity_df['equity'].cummax()
        equity_df['drawdown'] = (equity_df['equity'] - equity_df['cummax']) / equity_df['cummax']
        max_drawdown = equity_df['drawdown'].min()
        
        # Win rate
        winning_trades = [t for t in self.trades if t.get('pnl', 0) > 0]
        total_trades = len([t for t in self.trades if 'pnl' in t])
        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
        
        metrics = {
            'total_return': total_return,
            'final_equity': final_equity,
            'total_trades': total_trades,
            'win_rate': win_rate,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown
        }
        
        logger.info(f"Backtest Results:")
        logger.info(f"Total Return: {total_return:.2%}")
        logger.info(f"Final Equity: ${final_equity:,.2f}")
        logger.info(f"Total Trades: {total_trades}")
        logger.info(f"Win Rate: {win_rate:.2%}")
        logger.info(f"Sharpe Ratio: {sharpe:.2f}")
        logger.info(f"Max Drawdown: {max_drawdown:.2%}")
        
        return metrics
    
    def plot_equity_curve(self, save_path: str = None):
        """
        Plot equity curve.
        
        Args:
            save_path: Path to save the plot
        """
        equity_df = pd.DataFrame(self.equity_curve)
        
        plt.figure(figsize=(12, 6))
        plt.plot(equity_df['date'], equity_df['equity'])
        plt.axhline(y=self.initial_capital, color='r', linestyle='--', label='Initial Capital')
        plt.title('Equity Curve')
        plt.xlabel('Date')
        plt.ylabel('Equity ($)')
        plt.legend()
        plt.grid(True)
        
        if save_path:
            plt.savefig(save_path)
            logger.info(f"Equity curve saved to {save_path}")
        else:
            plt.show()
        
        plt.close()


if __name__ == "__main__":
    # Example usage
    data = pd.read_csv("data/signals/AAPL_combined_signals.csv", index_col=0, parse_dates=True)
    
    backtester = SimpleBacktester(initial_capital=100000)
    results = backtester.backtest(data)
    backtester.plot_equity_curve("models/equity_curve.png")

