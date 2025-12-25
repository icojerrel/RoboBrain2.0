"""
Risk Management System

Manages trading risk, position sizing, and safety limits
"""

from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class RiskLimits:
    """Risk management limits"""
    max_risk_per_trade: float = 0.01  # 1% max risk per trade
    max_daily_loss: float = 0.03  # 3% max daily loss
    max_total_risk: float = 0.05  # 5% max total portfolio risk
    max_position_size: float = 0.1  # 10% max single position
    max_open_positions: int = 3  # Max concurrent positions
    max_correlation: float = 0.7  # Max correlation between positions
    stop_loss_atr_mult: float = 2.0  # Stop loss = 2x ATR
    take_profit_ratio: float = 2.0  # TP/SL ratio


@dataclass
class TradeRisk:
    """Individual trade risk assessment"""
    approved: bool
    position_size: float
    stop_loss: float
    take_profit: float
    risk_amount: float
    risk_percent: float
    reason: str


class RiskManager:
    """
    Risk management system

    Enforces position sizing, risk limits, and safety checks
    """

    def __init__(self, limits: RiskLimits = None):
        self.limits = limits or RiskLimits()

        # Track daily P&L
        self.daily_pnl = {}
        self.last_reset = datetime.now().date()

        logger.info("🛡️ Risk Manager initialized")
        logger.info(f"   Max risk/trade: {self.limits.max_risk_per_trade*100}%")
        logger.info(f"   Max daily loss: {self.limits.max_daily_loss*100}%")
        logger.info(f"   Max positions: {self.limits.max_open_positions}")

    def assess_trade(self,
                     symbol: str,
                     direction: str,  # "buy" or "sell"
                     entry_price: float,
                     account_balance: float,
                     current_positions: List = None,
                     atr: float = None) -> TradeRisk:
        """
        Assess if trade should be taken

        Args:
            symbol: Trading symbol
            direction: "buy" or "sell"
            entry_price: Proposed entry price
            account_balance: Current account balance
            current_positions: List of open positions
            atr: Average True Range for stop loss calculation

        Returns:
            TradeRisk assessment
        """

        current_positions = current_positions or []

        # Check daily loss limit
        today = datetime.now().date()
        if today != self.last_reset:
            self.daily_pnl = {}
            self.last_reset = today

        daily_loss = sum(pnl for pnl in self.daily_pnl.values() if pnl < 0)
        if abs(daily_loss) > account_balance * self.limits.max_daily_loss:
            return TradeRisk(
                approved=False,
                position_size=0,
                stop_loss=0,
                take_profit=0,
                risk_amount=0,
                risk_percent=0,
                reason=f"Daily loss limit exceeded: ${abs(daily_loss):.2f}"
            )

        # Check max open positions
        if len(current_positions) >= self.limits.max_open_positions:
            return TradeRisk(
                approved=False,
                position_size=0,
                stop_loss=0,
                take_profit=0,
                risk_amount=0,
                risk_percent=0,
                reason=f"Max open positions reached: {len(current_positions)}"
            )

        # Calculate stop loss using ATR
        if atr is None:
            atr = entry_price * 0.02  # Default 2% if ATR not provided

        if direction == "buy":
            stop_loss = entry_price - (atr * self.limits.stop_loss_atr_mult)
            take_profit = entry_price + (atr * self.limits.stop_loss_atr_mult * self.limits.take_profit_ratio)
        else:  # sell
            stop_loss = entry_price + (atr * self.limits.stop_loss_atr_mult)
            take_profit = entry_price - (atr * self.limits.stop_loss_atr_mult * self.limits.take_profit_ratio)

        # Calculate risk
        risk_per_unit = abs(entry_price - stop_loss)
        risk_amount = account_balance * self.limits.max_risk_per_trade

        # Calculate position size
        position_size = risk_amount / risk_per_unit

        # Check max position size
        max_position_value = account_balance * self.limits.max_position_size
        if position_size * entry_price > max_position_value:
            position_size = max_position_value / entry_price

        # Calculate actual risk
        actual_risk = position_size * risk_per_unit
        risk_percent = actual_risk / account_balance

        return TradeRisk(
            approved=True,
            position_size=position_size,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_amount=actual_risk,
            risk_percent=risk_percent,
            reason="Trade approved"
        )

    def record_trade_result(self, symbol: str, pnl: float):
        """Record trade P&L for tracking"""
        if symbol not in self.daily_pnl:
            self.daily_pnl[symbol] = 0

        self.daily_pnl[symbol] += pnl

        logger.info(f"📊 Trade result: {symbol} P&L = ${pnl:.2f}")
        logger.info(f"   Daily P&L: ${sum(self.daily_pnl.values()):.2f}")

    def get_daily_pnl(self) -> float:
        """Get total daily P&L"""
        return sum(self.daily_pnl.values())

    def should_stop_trading(self, account_balance: float) -> Tuple[bool, str]:
        """
        Check if trading should be stopped

        Returns:
            (should_stop, reason)
        """

        # Check daily loss limit
        daily_pnl = self.get_daily_pnl()

        if daily_pnl < -account_balance * self.limits.max_daily_loss:
            return True, f"Daily loss limit hit: ${abs(daily_pnl):.2f}"

        return False, ""

    def calculate_kelly_criterion(self,
                                  win_rate: float,
                                  avg_win: float,
                                  avg_loss: float) -> float:
        """
        Calculate optimal position size using Kelly Criterion

        Args:
            win_rate: Historical win rate (0-1)
            avg_win: Average win amount
            avg_loss: Average loss amount

        Returns:
            Kelly fraction (0-1)
        """

        if avg_loss == 0 or win_rate == 0:
            return 0

        win_loss_ratio = avg_win / abs(avg_loss)
        kelly = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio

        # Use half Kelly for safety
        kelly = max(0, min(kelly / 2, self.limits.max_risk_per_trade))

        return kelly

    def calculate_atr(self, data: pd.DataFrame, period: int = 14) -> float:
        """
        Calculate Average True Range

        Args:
            data: DataFrame with high, low, close
            period: ATR period

        Returns:
            ATR value
        """

        high = data['high']
        low = data['low']
        close = data['close']

        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())

        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(period).mean()

        return atr.iloc[-1]


# Singleton
_risk_manager: Optional[RiskManager] = None


def get_risk_manager(limits: RiskLimits = None) -> RiskManager:
    """Get risk manager (singleton)"""
    global _risk_manager
    if _risk_manager is None:
        _risk_manager = RiskManager(limits)
    return _risk_manager


# Test
if __name__ == "__main__":
    print("🛡️ Risk Manager Test\n")

    risk_mgr = get_risk_manager()

    # Test trade assessment
    assessment = risk_mgr.assess_trade(
        symbol="MNQ",
        direction="buy",
        entry_price=16000,
        account_balance=10000,
        current_positions=[],
        atr=50
    )

    print(f"✅ Trade Assessment:")
    print(f"   Approved: {assessment.approved}")
    print(f"   Position size: {assessment.position_size:.2f}")
    print(f"   Stop loss: ${assessment.stop_loss:.2f}")
    print(f"   Take profit: ${assessment.take_profit:.2f}")
    print(f"   Risk amount: ${assessment.risk_amount:.2f}")
    print(f"   Risk %: {assessment.risk_percent*100:.2f}%")
    print(f"   Reason: {assessment.reason}")

    # Test Kelly criterion
    kelly = risk_mgr.calculate_kelly_criterion(
        win_rate=0.55,
        avg_win=100,
        avg_loss=50
    )

    print(f"\n📊 Kelly Criterion: {kelly*100:.2f}% position size")
