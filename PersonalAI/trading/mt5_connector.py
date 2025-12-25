"""
MT5 Connector for PersonalAI Autonomous Trader

MetaTrader 5 integration for MNQ (Micro E-mini NASDAQ) futures trading
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MT5Config:
    """MT5 configuration"""
    symbol: str = "MNQ"  # Micro E-mini NASDAQ
    timeframe: int = mt5.TIMEFRAME_M5  # 5-minute bars
    magic_number: int = 888888  # Unique identifier
    lot_size: float = 0.1  # Micro contract size
    slippage: int = 10  # Points
    deviation: int = 10  # Points


@dataclass
class Position:
    """Trading position"""
    ticket: int
    symbol: str
    type: str  # "buy" or "sell"
    volume: float
    open_price: float
    current_price: float
    profit: float
    sl: float
    tp: float
    open_time: datetime
    magic: int


@dataclass
class BarData:
    """OHLCV bar data"""
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    tick_volume: int


class MT5Connector:
    """
    MetaTrader 5 connector

    Handles:
    - Connection to MT5 terminal
    - Market data retrieval (MNQ)
    - Order execution
    - Position management
    - Account information
    """

    def __init__(self, config: MT5Config = None):
        self.config = config or MT5Config()
        self.connected = False
        self.account_info = None

    def connect(self, login: int = None, password: str = None, server: str = None) -> bool:
        """
        Connect to MT5 terminal

        Args:
            login: MT5 account number
            password: MT5 account password
            server: MT5 server name

        Returns:
            True if connected successfully
        """
        try:
            # Initialize MT5
            if not mt5.initialize():
                logger.error(f"MT5 initialize failed: {mt5.last_error()}")
                return False

            # Login if credentials provided
            if login and password and server:
                if not mt5.login(login, password, server):
                    logger.error(f"MT5 login failed: {mt5.last_error()}")
                    return False

            self.connected = True
            self.account_info = mt5.account_info()._asdict() if mt5.account_info() else None

            logger.info(f"✅ Connected to MT5")
            logger.info(f"   Account: {self.account_info.get('login', 'Demo')}")
            logger.info(f"   Balance: ${self.account_info.get('balance', 0):.2f}")
            logger.info(f"   Equity: ${self.account_info.get('equity', 0):.2f}")

            return True

        except Exception as e:
            logger.error(f"MT5 connection error: {e}")
            return False

    def disconnect(self):
        """Disconnect from MT5"""
        if self.connected:
            mt5.shutdown()
            self.connected = False
            logger.info("🔌 Disconnected from MT5")

    def get_symbol_info(self, symbol: str = None) -> Optional[Dict]:
        """Get symbol information"""
        symbol = symbol or self.config.symbol

        if not self.connected:
            logger.warning("Not connected to MT5")
            return None

        info = mt5.symbol_info(symbol)
        if info is None:
            logger.error(f"Symbol {symbol} not found")
            return None

        return info._asdict()

    def get_bars(self,
                 symbol: str = None,
                 timeframe: int = None,
                 count: int = 1000,
                 start_pos: int = 0) -> Optional[pd.DataFrame]:
        """
        Get historical bar data

        Args:
            symbol: Trading symbol (default: MNQ)
            timeframe: MT5 timeframe (default: M5)
            count: Number of bars
            start_pos: Start position (0 = most recent)

        Returns:
            DataFrame with OHLCV data
        """
        symbol = symbol or self.config.symbol
        timeframe = timeframe or self.config.timeframe

        if not self.connected:
            logger.warning("Not connected to MT5")
            return None

        rates = mt5.copy_rates_from_pos(symbol, timeframe, start_pos, count)

        if rates is None or len(rates) == 0:
            logger.error(f"Failed to get bars: {mt5.last_error()}")
            return None

        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')

        return df

    def get_current_price(self, symbol: str = None) -> Optional[Dict]:
        """Get current bid/ask prices"""
        symbol = symbol or self.config.symbol

        if not self.connected:
            logger.warning("Not connected to MT5")
            return None

        tick = mt5.symbol_info_tick(symbol)

        if tick is None:
            logger.error(f"Failed to get tick: {mt5.last_error()}")
            return None

        return {
            'bid': tick.bid,
            'ask': tick.ask,
            'last': tick.last,
            'volume': tick.volume,
            'time': datetime.fromtimestamp(tick.time)
        }

    def place_order(self,
                    order_type: str,  # "buy" or "sell"
                    volume: float = None,
                    symbol: str = None,
                    sl: float = 0,
                    tp: float = 0,
                    comment: str = "Autonomous Trader") -> Optional[int]:
        """
        Place market order

        Args:
            order_type: "buy" or "sell"
            volume: Lot size (default: config.lot_size)
            symbol: Trading symbol
            sl: Stop loss price
            tp: Take profit price
            comment: Order comment

        Returns:
            Ticket number if successful
        """
        symbol = symbol or self.config.symbol
        volume = volume or self.config.lot_size

        if not self.connected:
            logger.warning("Not connected to MT5")
            return None

        # Get symbol info
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            logger.error(f"Symbol {symbol} not found")
            return None

        # Enable symbol if not enabled
        if not symbol_info.visible:
            if not mt5.symbol_select(symbol, True):
                logger.error(f"Failed to select symbol {symbol}")
                return None

        # Get current price
        price = self.get_current_price(symbol)
        if price is None:
            return None

        # Prepare request
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": mt5.ORDER_TYPE_BUY if order_type == "buy" else mt5.ORDER_TYPE_SELL,
            "price": price['ask'] if order_type == "buy" else price['bid'],
            "sl": sl,
            "tp": tp,
            "deviation": self.config.deviation,
            "magic": self.config.magic_number,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        # Send order
        result = mt5.order_send(request)

        if result is None:
            logger.error(f"Order failed: {mt5.last_error()}")
            return None

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"Order failed: {result.comment}")
            return None

        logger.info(f"✅ Order placed: {order_type.upper()} {volume} {symbol} @ {request['price']}")
        logger.info(f"   Ticket: {result.order}")

        return result.order

    def close_position(self, ticket: int) -> bool:
        """Close position by ticket"""

        if not self.connected:
            logger.warning("Not connected to MT5")
            return False

        # Get position
        position = mt5.positions_get(ticket=ticket)

        if position is None or len(position) == 0:
            logger.error(f"Position {ticket} not found")
            return False

        position = position[0]

        # Prepare close request
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": position.symbol,
            "volume": position.volume,
            "type": mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
            "position": ticket,
            "price": mt5.symbol_info_tick(position.symbol).bid if position.type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(position.symbol).ask,
            "deviation": self.config.deviation,
            "magic": self.config.magic_number,
            "comment": "Close by Autonomous Trader",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        # Send close order
        result = mt5.order_send(request)

        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"Failed to close position {ticket}: {result.comment if result else mt5.last_error()}")
            return False

        logger.info(f"✅ Position closed: {ticket}")
        return True

    def get_positions(self, symbol: str = None) -> List[Position]:
        """Get open positions"""

        if not self.connected:
            logger.warning("Not connected to MT5")
            return []

        symbol = symbol or self.config.symbol
        positions = mt5.positions_get(symbol=symbol)

        if positions is None:
            return []

        result = []
        for pos in positions:
            result.append(Position(
                ticket=pos.ticket,
                symbol=pos.symbol,
                type="buy" if pos.type == mt5.ORDER_TYPE_BUY else "sell",
                volume=pos.volume,
                open_price=pos.price_open,
                current_price=pos.price_current,
                profit=pos.profit,
                sl=pos.sl,
                tp=pos.tp,
                open_time=datetime.fromtimestamp(pos.time),
                magic=pos.magic
            ))

        return result

    def get_account_info(self) -> Optional[Dict]:
        """Get account information"""

        if not self.connected:
            logger.warning("Not connected to MT5")
            return None

        info = mt5.account_info()
        if info is None:
            return None

        return info._asdict()

    def calculate_position_size(self,
                                risk_percent: float = 1.0,
                                stop_loss_points: int = 50) -> float:
        """
        Calculate position size based on risk percentage

        Args:
            risk_percent: Risk percentage of account (e.g., 1.0 = 1%)
            stop_loss_points: Stop loss in points

        Returns:
            Lot size
        """
        if not self.connected:
            return self.config.lot_size

        account = self.get_account_info()
        if account is None:
            return self.config.lot_size

        balance = account['balance']
        risk_amount = balance * (risk_percent / 100)

        symbol_info = self.get_symbol_info()
        if symbol_info is None:
            return self.config.lot_size

        # Calculate lot size
        # risk_amount = lot_size * stop_loss_points * point_value
        point_value = symbol_info['trade_contract_size'] * symbol_info['point']
        lot_size = risk_amount / (stop_loss_points * point_value)

        # Round to valid lot size
        lot_step = symbol_info['volume_step']
        lot_size = round(lot_size / lot_step) * lot_step

        # Apply limits
        lot_min = symbol_info['volume_min']
        lot_max = symbol_info['volume_max']
        lot_size = max(lot_min, min(lot_max, lot_size))

        return lot_size


# Singleton
_mt5_connector: Optional[MT5Connector] = None


def get_mt5_connector(config: MT5Config = None) -> MT5Connector:
    """Get MT5 connector (singleton)"""
    global _mt5_connector
    if _mt5_connector is None:
        _mt5_connector = MT5Connector(config)
    return _mt5_connector


# Test
if __name__ == "__main__":
    print("🔌 MT5 Connector Test\n")

    # Initialize
    connector = get_mt5_connector()

    # Connect (demo account)
    if connector.connect():
        # Get account info
        account = connector.get_account_info()
        print(f"\n💰 Account Info:")
        print(f"   Balance: ${account['balance']:.2f}")
        print(f"   Equity: ${account['equity']:.2f}")
        print(f"   Margin: ${account['margin']:.2f}")

        # Get MNQ info
        symbol_info = connector.get_symbol_info("MNQ")
        if symbol_info:
            print(f"\n📊 MNQ Symbol Info:")
            print(f"   Bid: {symbol_info['bid']}")
            print(f"   Ask: {symbol_info['ask']}")
            print(f"   Spread: {symbol_info['spread']}")

        # Get bars
        bars = connector.get_bars(count=10)
        if bars is not None:
            print(f"\n📈 Last 10 bars:")
            print(bars[['time', 'open', 'high', 'low', 'close', 'volume']].tail())

        # Get positions
        positions = connector.get_positions()
        print(f"\n📍 Open positions: {len(positions)}")

        # Disconnect
        connector.disconnect()

    else:
        print("❌ Failed to connect to MT5")
        print("   Make sure MT5 is running and logged in")
