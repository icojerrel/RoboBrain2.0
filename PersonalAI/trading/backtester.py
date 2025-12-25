"""
Backtesting Framework

Tests trading strategies on historical data
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class BacktestResult:
    """Backtest results"""
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_win: float
    avg_loss: float
    equity_curve: pd.Series
    trades: List[Dict]


class Backtester:
    """
    Backtesting framework

    Tests strategies on historical data with realistic simulation
    """

    def __init__(self,
                 initial_capital: float = 10000,
                 commission: float = 0.0002,  # 0.02% per trade
                 slippage: float = 0.0001):    # 0.01%
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage

        logger.info("📊 Backtester initialized")
        logger.info(f"   Initial capital: ${initial_capital}")
        logger.info(f"   Commission: {commission*100:.3f}%")
        logger.info(f"   Slippage: {slippage*100:.3f}%")

    def run(self,
            strategy,
            data: pd.DataFrame,
            position_size: float = 1.0) -> BacktestResult:
        """
        Run backtest

        Args:
            strategy: Strategy instance with generate_signals() method
            data: DataFrame with OHLCV columns
            position_size: Position size multiplier

        Returns:
            BacktestResult
        """

        logger.info(f"🚀 Running backtest: {strategy.get_name()}")

        # Generate signals
        signals = strategy.generate_signals(data)

        # Initialize tracking
        capital = self.initial_capital
        position = 0  # 1 = long, -1 = short, 0 = flat
        entry_price = 0
        equity_curve = []
        trades = []

        wins = 0
        losses = 0
        total_profit = 0
        total_loss = 0

        for i in range(len(data)):
            current_price = data['close'].iloc[i]
            signal = signals.iloc[i]

            # Calculate equity
            if position != 0:
                unrealized_pnl = (current_price - entry_price) * position
                current_equity = capital + unrealized_pnl
            else:
                current_equity = capital

            equity_curve.append(current_equity)

            # Execute trades
            if signal != 0 and position == 0:
                # Open position
                position = signal
                entry_price = current_price * (1 + self.slippage * signal)
                capital -= abs(capital * position_size * self.commission)

                trades.append({
                    'entry_time': data['time'].iloc[i],
                    'entry_price': entry_price,
                    'type': 'long' if position == 1 else 'short',
                    'status': 'open'
                })

            elif signal == -position and position != 0:
                # Close position
                exit_price = current_price * (1 - self.slippage * position)
                pnl = (exit_price - entry_price) * position

                # Apply commission
                pnl -= abs(capital * position_size * self.commission)

                capital += pnl

                # Track wins/losses
                if pnl > 0:
                    wins += 1
                    total_profit += pnl
                else:
                    losses += 1
                    total_loss += abs(pnl)

                # Update last trade
                trades[-1].update({
                    'exit_time': data['time'].iloc[i],
                    'exit_price': exit_price,
                    'pnl': pnl,
                    'status': 'closed'
                })

                position = 0

        # Close any open position at end
        if position != 0:
            exit_price = data['close'].iloc[-1]
            pnl = (exit_price - entry_price) * position
            capital += pnl

            if pnl > 0:
                wins += 1
                total_profit += pnl
            else:
                losses += 1
                total_loss += abs(pnl)

            trades[-1].update({
                'exit_time': data['time'].iloc[-1],
                'exit_price': exit_price,
                'pnl': pnl,
                'status': 'closed'
            })

        # Calculate metrics
        equity_series = pd.Series(equity_curve)
        returns = equity_series.pct_change().dropna()

        total_return = (capital - self.initial_capital) / self.initial_capital
        sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
        max_drawdown = (equity_series / equity_series.cummax() - 1).min()
        win_rate = wins / (wins + losses) if (wins + losses) > 0 else 0
        profit_factor = total_profit / total_loss if total_loss > 0 else 0
        avg_win = total_profit / wins if wins > 0 else 0
        avg_loss = total_loss / losses if losses > 0 else 0

        result = BacktestResult(
            total_return=total_return,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            profit_factor=profit_factor,
            total_trades=len(trades),
            winning_trades=wins,
            losing_trades=losses,
            avg_win=avg_win,
            avg_loss=avg_loss,
            equity_curve=equity_series,
            trades=trades
        )

        self._print_results(result)

        return result

    def _print_results(self, result: BacktestResult):
        """Print backtest results"""

        logger.info("\n" + "=" * 60)
        logger.info("BACKTEST RESULTS")
        logger.info("=" * 60)
        logger.info(f"Total Return:    {result.total_return*100:>10.2f}%")
        logger.info(f"Sharpe Ratio:    {result.sharpe_ratio:>10.2f}")
        logger.info(f"Max Drawdown:    {result.max_drawdown*100:>10.2f}%")
        logger.info(f"Win Rate:        {result.win_rate*100:>10.2f}%")
        logger.info(f"Profit Factor:   {result.profit_factor:>10.2f}")
        logger.info("")
        logger.info(f"Total Trades:    {result.total_trades:>10}")
        logger.info(f"Winning Trades:  {result.winning_trades:>10}")
        logger.info(f"Losing Trades:   {result.losing_trades:>10}")
        logger.info(f"Avg Win:         ${result.avg_win:>10.2f}")
        logger.info(f"Avg Loss:        ${result.avg_loss:>10.2f}")
        logger.info("=" * 60 + "\n")

    def compare_strategies(self,
                          strategies: List,
                          data: pd.DataFrame) -> pd.DataFrame:
        """
        Compare multiple strategies

        Args:
            strategies: List of strategy instances
            data: Historical data

        Returns:
            DataFrame with comparison
        """

        results = []

        for strategy in strategies:
            result = self.run(strategy, data)

            results.append({
                'Strategy': strategy.get_name(),
                'Return': result.total_return,
                'Sharpe': result.sharpe_ratio,
                'Max DD': result.max_drawdown,
                'Win Rate': result.win_rate,
                'Profit Factor': result.profit_factor,
                'Trades': result.total_trades
            })

        df = pd.DataFrame(results)
        df = df.sort_values('Sharpe', ascending=False)

        logger.info("\n" + "=" * 80)
        logger.info("STRATEGY COMPARISON")
        logger.info("=" * 80)
        logger.info(df.to_string(index=False))
        logger.info("=" * 80 + "\n")

        return df


# Singleton
_backtester: Optional[Backtester] = None


def get_backtester(initial_capital: float = 10000) -> Backtester:
    """Get backtester (singleton)"""
    global _backtester
    if _backtester is None:
        _backtester = Backtester(initial_capital=initial_capital)
    return _backtester


# Test
if __name__ == "__main__":
    print("📊 Backtester Test\n")

    # Create sample data
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=1000, freq='5min')
    data = pd.DataFrame({
        'time': dates,
        'open': 100 + np.cumsum(np.random.randn(1000) * 0.1),
        'high': 100 + np.cumsum(np.random.randn(1000) * 0.1) + 0.5,
        'low': 100 + np.cumsum(np.random.randn(1000) * 0.1) - 0.5,
        'close': 100 + np.cumsum(np.random.randn(1000) * 0.1),
        'volume': np.random.randint(1000, 10000, 1000)
    })

    # Simple strategy for testing
    class SimpleStrategy:
        def get_name(self):
            return "Simple Momentum"

        def generate_signals(self, data):
            momentum = data['close'].pct_change(10)
            signals = pd.Series(0, index=data.index)
            signals[momentum > 0.01] = 1
            signals[momentum < -0.01] = -1
            return signals

    # Run backtest
    backtester = get_backtester()
    result = backtester.run(SimpleStrategy(), data)

    print(f"✅ Backtest complete")
    print(f"   Final equity: ${backtester.initial_capital * (1 + result.total_return):.2f}")
