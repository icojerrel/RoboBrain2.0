"""
Autonomous Strategy Generator

Generates, tests, and optimizes trading strategies using code generation
"""

import sys
import os
import hashlib
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
import pandas as pd
import numpy as np

sys.path.append(str(Path(__file__).parent.parent))
from core.autonomous_memory import remember_long, recall_relevant

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Strategy:
    """Trading strategy"""
    name: str
    code: str
    description: str
    parameters: Dict
    performance: Optional[Dict] = None
    hash: Optional[str] = None


class StrategyGenerator:
    """
    Autonomous strategy generator

    Generates Python trading strategies and optimizes them
    """

    def __init__(self):
        self.strategies_dir = Path(__file__).parent / "strategies"
        self.strategies_dir.mkdir(exist_ok=True)

        self.strategy_templates = self._load_templates()

        logger.info("🧠 Strategy Generator initialized")

    def _load_templates(self) -> Dict:
        """Load strategy templates"""

        templates = {
            "momentum": """
# Momentum Strategy - {name}
# Generated: {timestamp}

import pandas as pd
import numpy as np

class {class_name}:
    '''
    {description}

    Parameters:
        lookback: {lookback}
        threshold: {threshold}
    '''

    def __init__(self, lookback={lookback}, threshold={threshold}):
        self.lookback = lookback
        self.threshold = threshold

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        '''
        Generate trading signals

        Args:
            data: DataFrame with OHLCV columns

        Returns:
            Series with signals: 1 (buy), -1 (sell), 0 (hold)
        '''
        # Calculate momentum
        momentum = data['close'].pct_change(self.lookback)

        # Generate signals
        signals = pd.Series(0, index=data.index)
        signals[momentum > self.threshold] = 1  # Buy signal
        signals[momentum < -self.threshold] = -1  # Sell signal

        return signals

    def get_name(self):
        return "{name}"

    def get_description(self):
        return "{description}"
""",

            "mean_reversion": """
# Mean Reversion Strategy - {name}
# Generated: {timestamp}

import pandas as pd
import numpy as np

class {class_name}:
    '''
    {description}

    Parameters:
        sma_period: {sma_period}
        std_mult: {std_mult}
    '''

    def __init__(self, sma_period={sma_period}, std_mult={std_mult}):
        self.sma_period = sma_period
        self.std_mult = std_mult

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        '''Generate trading signals'''

        # Calculate SMA and Bollinger Bands
        sma = data['close'].rolling(self.sma_period).mean()
        std = data['close'].rolling(self.sma_period).std()

        upper_band = sma + (std * self.std_mult)
        lower_band = sma - (std * self.std_mult)

        # Generate signals
        signals = pd.Series(0, index=data.index)
        signals[data['close'] < lower_band] = 1  # Oversold - buy
        signals[data['close'] > upper_band] = -1  # Overbought - sell

        return signals

    def get_name(self):
        return "{name}"

    def get_description(self):
        return "{description}"
""",

            "breakout": """
# Breakout Strategy - {name}
# Generated: {timestamp}

import pandas as pd
import numpy as np

class {class_name}:
    '''
    {description}

    Parameters:
        breakout_period: {breakout_period}
        confirmation_bars: {confirmation_bars}
    '''

    def __init__(self, breakout_period={breakout_period}, confirmation_bars={confirmation_bars}):
        self.breakout_period = breakout_period
        self.confirmation_bars = confirmation_bars

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        '''Generate trading signals'''

        # Calculate breakout levels
        high_breakout = data['high'].rolling(self.breakout_period).max()
        low_breakout = data['low'].rolling(self.breakout_period).min()

        # Generate signals
        signals = pd.Series(0, index=data.index)

        # Buy on breakout above high
        for i in range(self.confirmation_bars, len(data)):
            if all(data['close'].iloc[i-j] > high_breakout.iloc[i-self.confirmation_bars-1]
                   for j in range(self.confirmation_bars)):
                signals.iloc[i] = 1

            # Sell on breakdown below low
            elif all(data['close'].iloc[i-j] < low_breakout.iloc[i-self.confirmation_bars-1]
                     for j in range(self.confirmation_bars)):
                signals.iloc[i] = -1

        return signals

    def get_name(self):
        return "{name}"

    def get_description(self):
        return "{description}"
"""
        }

        return templates

    def generate_strategy(self,
                         strategy_type: str = "momentum",
                         parameters: Dict = None) -> Strategy:
        """
        Generate new trading strategy

        Args:
            strategy_type: "momentum", "mean_reversion", "breakout"
            parameters: Strategy parameters

        Returns:
            Strategy object
        """

        if strategy_type not in self.strategy_templates:
            logger.error(f"Unknown strategy type: {strategy_type}")
            return None

        # Default parameters
        if parameters is None:
            if strategy_type == "momentum":
                parameters = {"lookback": 20, "threshold": 0.02}
            elif strategy_type == "mean_reversion":
                parameters = {"sma_period": 20, "std_mult": 2.0}
            elif strategy_type == "breakout":
                parameters = {"breakout_period": 20, "confirmation_bars": 2}

        # Generate strategy name
        name = f"{strategy_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        class_name = "".join(word.capitalize() for word in name.split("_"))

        # Format template
        template = self.strategy_templates[strategy_type]
        code = template.format(
            name=name,
            class_name=class_name,
            timestamp=datetime.now().isoformat(),
            description=f"{strategy_type.replace('_', ' ').title()} trading strategy",
            **parameters
        )

        # Calculate hash
        code_hash = hashlib.md5(code.encode()).hexdigest()

        strategy = Strategy(
            name=name,
            code=code,
            description=f"{strategy_type.replace('_', ' ').title()} strategy",
            parameters=parameters,
            hash=code_hash
        )

        logger.info(f"✅ Generated strategy: {name}")

        return strategy

    def save_strategy(self, strategy: Strategy) -> Path:
        """Save strategy to file"""

        filepath = self.strategies_dir / f"{strategy.name}.py"
        filepath.write_text(strategy.code)

        logger.info(f"💾 Saved strategy: {filepath}")

        return filepath

    def load_strategy(self, filepath: Path) -> Optional[object]:
        """
        Load strategy from file and instantiate

        Args:
            filepath: Path to strategy file

        Returns:
            Strategy instance
        """

        try:
            # Load module
            spec = importlib.util.spec_from_file_location("strategy", filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Get strategy class (assumes single class in file)
            for item_name in dir(module):
                item = getattr(module, item_name)
                if isinstance(item, type) and hasattr(item, 'generate_signals'):
                    return item()

            logger.error(f"No strategy class found in {filepath}")
            return None

        except Exception as e:
            logger.error(f"Failed to load strategy {filepath}: {e}")
            return None

    def optimize_parameters(self,
                           strategy_type: str,
                           param_ranges: Dict,
                           backtest_data: pd.DataFrame,
                           iterations: int = 20) -> Tuple[Dict, float]:
        """
        Optimize strategy parameters using random search

        Args:
            strategy_type: Type of strategy
            param_ranges: Dict of parameter ranges {param: (min, max)}
            backtest_data: Historical data for backtesting
            iterations: Number of random trials

        Returns:
            (best_parameters, best_score)
        """

        logger.info(f"🔧 Optimizing {strategy_type} strategy...")

        best_params = None
        best_score = -float('inf')
        results = []

        for i in range(iterations):
            # Generate random parameters
            params = {}
            for param, (min_val, max_val) in param_ranges.items():
                if isinstance(min_val, int):
                    params[param] = np.random.randint(min_val, max_val + 1)
                else:
                    params[param] = np.random.uniform(min_val, max_val)

            # Generate strategy
            strategy = self.generate_strategy(strategy_type, params)

            # Simple backtest (calculate score)
            # In production: use full backtester
            score = self._quick_backtest(strategy, backtest_data)

            results.append((params, score))

            if score > best_score:
                best_score = score
                best_params = params
                logger.info(f"  Iteration {i+1}/{iterations}: New best score = {score:.4f}")

        logger.info(f"✅ Optimization complete")
        logger.info(f"   Best parameters: {best_params}")
        logger.info(f"   Best score: {best_score:.4f}")

        return best_params, best_score

    def _quick_backtest(self, strategy: Strategy, data: pd.DataFrame) -> float:
        """
        Quick backtest for optimization

        Returns:
            Sharpe ratio
        """

        try:
            # Save and load strategy
            filepath = self.save_strategy(strategy)
            strategy_instance = self.load_strategy(filepath)

            if strategy_instance is None:
                return -999

            # Generate signals
            signals = strategy_instance.generate_signals(data)

            # Calculate returns
            returns = data['close'].pct_change()
            strategy_returns = signals.shift(1) * returns

            # Calculate Sharpe ratio
            sharpe = strategy_returns.mean() / strategy_returns.std() * np.sqrt(252)

            return sharpe if not np.isnan(sharpe) else -999

        except Exception as e:
            logger.error(f"Quick backtest failed: {e}")
            return -999

    def evolve_strategy(self, base_strategy: Strategy, mutation_rate: float = 0.1) -> Strategy:
        """
        Evolve strategy by mutating parameters

        Args:
            base_strategy: Base strategy to evolve
            mutation_rate: Parameter mutation rate

        Returns:
            Evolved strategy
        """

        # Mutate parameters
        new_params = base_strategy.parameters.copy()

        for param, value in new_params.items():
            if np.random.random() < mutation_rate:
                if isinstance(value, int):
                    new_params[param] = max(1, value + np.random.randint(-5, 6))
                else:
                    new_params[param] = max(0.001, value * np.random.uniform(0.8, 1.2))

        # Extract strategy type from name
        strategy_type = base_strategy.name.split('_')[0]

        # Generate evolved strategy
        evolved = self.generate_strategy(strategy_type, new_params)
        evolved.name = f"{evolved.name}_evolved"

        logger.info(f"🧬 Evolved strategy: {evolved.name}")

        return evolved


# Singleton
_strategy_generator: Optional[StrategyGenerator] = None


def get_strategy_generator() -> StrategyGenerator:
    """Get strategy generator (singleton)"""
    global _strategy_generator
    if _strategy_generator is None:
        _strategy_generator = StrategyGenerator()
    return _strategy_generator


# Test
if __name__ == "__main__":
    print("🧠 Strategy Generator Test\n")

    generator = get_strategy_generator()

    # Generate momentum strategy
    strategy = generator.generate_strategy("momentum", {"lookback": 20, "threshold": 0.02})

    print(f"✅ Generated: {strategy.name}")
    print(f"📝 Description: {strategy.description}")
    print(f"⚙️  Parameters: {strategy.parameters}")

    # Save strategy
    filepath = generator.save_strategy(strategy)
    print(f"💾 Saved to: {filepath}")

    # Load strategy
    strategy_instance = generator.load_strategy(filepath)
    if strategy_instance:
        print(f"✅ Loaded successfully")
        print(f"   Name: {strategy_instance.get_name()}")
