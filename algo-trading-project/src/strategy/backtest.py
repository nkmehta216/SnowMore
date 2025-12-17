"""
Backtest trading strategies.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from src.utils.logger import get_logger
from src.utils.config import (
    DEFAULT_TICKERS,
    SIGNALS_DIR,
    INITIAL_CAPITAL,
    COMMISSION_RATE,
)

logger = get_logger(__name__)


class SimpleBacktester:
    """
    Simple long-only backtesting engine.
    """

    def __init__(
        self,
        initial_capital: float = INITIAL_CAPITAL,
        commission: float = COMMISSION_RATE,
    ):
        self.initial_capital = initial_capital
        self.commission = commission
        self.reset()

    def reset(self):
        self.capital = self.initial_capital
        self.position = 0
        self.entry_price = None
        self.trades = []
        self.equity_curve = []

    def execute_trade(self, signal: int, price: float):
        """
        Execute trade based on signal.
        """
        # BUY
        if signal == 1 and self.position == 0:
            shares = int(self.capital / price)
            if shares <= 0:
                return

            cost = shares * price * (1 + self.commission)
            self.capital -= cost
            self.position = shares
            self.entry_price = price

            self.trades.append(
                {"type": "BUY", "price": price, "shares": shares}
            )

        # SELL
        elif signal == -1 and self.position > 0:
            proceeds = self.position * price * (1 - self.commission)
            pnl = proceeds - (
                self.position * self.entry_price * (1 + self.commission)
            )

            self.capital += proceeds

            self.trades.append(
                {
                    "type": "SELL",
                    "price": price,
                    "shares": self.position,
                    "pnl": pnl,
                }
            )

            self.position = 0
            self.entry_price = None

    def backtest(
        self,
        data: pd.DataFrame,
        signal_column: str = "combined_signal",
    ) -> dict:
        """
        Run backtest on historical data.
        """
        self.reset()

        for date, row in data.iterrows():
            signal = int(row.get(signal_column, 0))
            price = row["Close"]

            self.execute_trade(signal, price)

            equity = self.capital + self.position * price
            self.equity_curve.append(
                {"date": date, "equity": equity}
            )

        # Close open position at end
        if self.position > 0:
            self.execute_trade(-1, data.iloc[-1]["Close"])

        return self.calculate_metrics()

    def calculate_metrics(self) -> dict:
        """
        Calculate performance metrics.
        """
        equity_df = pd.DataFrame(self.equity_curve).set_index("date")

        returns = equity_df["equity"].pct_change().dropna()

        total_return = (
            equity_df["equity"].iloc[-1] - self.initial_capital
        ) / self.initial_capital

        sharpe = (
            returns.mean() / returns.std()
        ) * np.sqrt(252) if returns.std() > 0 else 0.0

        cum_max = equity_df["equity"].cummax()
        drawdown = (equity_df["equity"] - cum_max) / cum_max
        max_drawdown = drawdown.min()

        closed_trades = [t for t in self.trades if "pnl" in t]
        wins = [t for t in closed_trades if t["pnl"] > 0]

        metrics = {
            "final_equity": equity_df["equity"].iloc[-1],
            "total_return": total_return,
            "total_trades": len(closed_trades),
            "win_rate": len(wins) / len(closed_trades)
            if closed_trades else 0,
            "sharpe_ratio": sharpe,
            "max_drawdown": max_drawdown,
        }

        logger.info("📊 Backtest Results")
        for k, v in metrics.items():
            logger.info(f"{k}: {v}")

        return metrics

    def plot_equity_curve(self, save_path: Path | None = None):
        equity_df = pd.DataFrame(self.equity_curve)

        plt.figure(figsize=(10, 5))
        plt.plot(equity_df["date"], equity_df["equity"], label="Equity")
        plt.axhline(
            self.initial_capital,
            linestyle="--",
            color="red",
            label="Initial Capital",
        )
        plt.legend()
        plt.title("Equity Curve")
        plt.grid(True)

        if save_path:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, bbox_inches="tight")
        else:
            plt.show()

        plt.close()


def backtest_all_tickers():
    """
    Run backtests for all configured tickers.
    """
    results = []

    for ticker in DEFAULT_TICKERS:
        logger.info(f"🔁 Backtesting {ticker}")

        path = SIGNALS_DIR / f"{ticker}_combined_signals.csv"
        if not path.exists():
            logger.warning(f"Signals not found for {ticker}")
            continue

        data = pd.read_csv(path, index_col=0, parse_dates=True)

        backtester = SimpleBacktester()
        metrics = backtester.backtest(data)
        backtester.plot_equity_curve(
            Path("reports") / f"{ticker}_equity_curve.png"
        )

        metrics["ticker"] = ticker
        results.append(metrics)

    return pd.DataFrame(results)


if __name__ == "__main__":
    summary = backtest_all_tickers()
    if not summary.empty:
        print(summary.set_index("ticker").round(3))
