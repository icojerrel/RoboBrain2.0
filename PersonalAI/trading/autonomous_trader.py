"""
PersonalAI Autonomous Trader

Self-improving trading agent with decision loop:
1. READ - Market data + memory
2. QUERY - Successful strategies
3. THINK - Generate/select strategy
4. ACT - Backtest → Trade
5. RECORD - Results to memory
6. LEARN - Improve from P&L
"""

import sys
import time
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import sqlite3

sys.path.append(str(Path(__file__).parent.parent))
from core.autonomous_memory import (
    get_short_term_memory,
    get_long_term_memory,
    remember_short,
    remember_long,
    recall_recent
)

from trading.mt5_connector import get_mt5_connector, MT5Config
from trading.strategy_generator import get_strategy_generator
from trading.backtester import get_backtester
from trading.risk_manager import get_risk_manager, RiskLimits

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AutonomousTrader:
    """
    Autonomous Trading Agent

    Self-directed trader that:
    - Generates trading strategies
    - Backtests and optimizes
    - Trades autonomously
    - Learns from P&L
    - Improves over time
    """

    def __init__(self,
                 mt5_config: MT5Config = None,
                 risk_limits: RiskLimits = None,
                 mode: str = "paper"):  # "paper" or "live"

        # Components
        self.mt5 = get_mt5_connector(mt5_config)
        self.strategy_gen = get_strategy_generator()
        self.backtester = get_backtester()
        self.risk_mgr = get_risk_manager(risk_limits)

        # Memory
        self.short_memory = get_short_term_memory()
        self.long_memory = get_long_term_memory()

        # State
        self.mode = mode
        self.running = False
        self.cycle_count = 0

        # Current strategy
        self.current_strategy = None
        self.strategy_performance = {}

        logger.info(f"🤖 Autonomous Trader initialized ({mode} mode)")

    def start(self):
        """Start autonomous trading"""

        self.running = True

        remember_short("goal", f"Start autonomous trading ({self.mode} mode)")
        logger.info("🚀 Autonomous Trader starting...\n")

        # Connect to MT5
        if not self.mt5.connect():
            logger.error("Failed to connect to MT5")
            return

        try:
            while self.running:
                self.decision_cycle()
                self.cycle_count += 1

                # Sleep between cycles (5 minutes for MNQ)
                time.sleep(300)

        except KeyboardInterrupt:
            logger.info("\n⏸️ Autonomous Trader stopping...")
            self.running = False

        # Cleanup
        self.mt5.disconnect()
        remember_short("observation", "Autonomous trading stopped")
        logger.info("🛑 Autonomous Trader stopped")

    def decision_cycle(self):
        """
        Single decision cycle

        1. READ - Market data + memory
        2. QUERY - Successful strategies
        3. THINK - Generate/select strategy
        4. ACT - Backtest → Trade
        5. RECORD - Results
        6. LEARN - Improve
        """

        logger.info(f"\n{'='*60}")
        logger.info(f"🔄 TRADING CYCLE #{self.cycle_count}")
        logger.info(f"{'='*60}\n")

        # 1. READ - Market data + context
        market_data = self._read_market()
        context = self._read_context()

        # 2. QUERY - Find successful strategies
        knowledge = self._query_knowledge()

        # 3. THINK - Decide strategy/action
        decision = self._think(market_data, context, knowledge)

        # 4. ACT - Execute decision
        result = self._act(decision, market_data)

        # 5. RECORD - Log results
        self._record(decision, result)

        # 6. LEARN - Store insights
        self._learn(decision, result)

    def _read_market(self) -> Dict:
        """Read market data"""

        logger.info("📖 READ Market Data:")

        # Get current price
        price = self.mt5.get_current_price()

        # Get historical bars
        bars = self.mt5.get_bars(count=1000)

        # Calculate ATR for risk management
        atr = self.risk_mgr.calculate_atr(bars) if bars is not None else None

        # Get account info
        account = self.mt5.get_account_info()

        # Get open positions
        positions = self.mt5.get_positions()

        market_data = {
            'price': price,
            'bars': bars,
            'atr': atr,
            'account_balance': account['balance'] if account else 0,
            'account_equity': account['equity'] if account else 0,
            'positions': positions
        }

        logger.info(f"  Price: ${price['bid'] if price else 0:.2f}")
        logger.info(f"  ATR: {atr:.2f}" if atr else "  ATR: N/A")
        logger.info(f"  Balance: ${market_data['account_balance']:.2f}")
        logger.info(f"  Open positions: {len(positions)}")

        return market_data

    def _read_context(self) -> Dict:
        """Read context from memory"""

        recent = recall_recent(10)

        context = {
            'recent_trades': [m for m in recent if 'trade' in m.content.lower()],
            'recent_strategies': [m for m in recent if 'strategy' in m.content.lower()],
            'recent_performance': [m for m in recent if 'profit' in m.content.lower() or 'loss' in m.content.lower()]
        }

        logger.info("📖 READ Context:")
        logger.info(f"  Recent trades: {len(context['recent_trades'])}")
        logger.info(f"  Recent strategies: {len(context['recent_strategies'])}")

        return context

    def _query_knowledge(self) -> List:
        """Query long-term memory for successful strategies"""

        logger.info("🔍 QUERY Knowledge:")

        if not self.long_memory.enabled:
            logger.info("  (Long-term memory disabled)")
            return []

        # Search for profitable strategies
        profitable = self.long_memory.search(
            query="profitable trading strategy high sharpe ratio",
            type="discovery",
            limit=3
        )

        for mem in profitable:
            logger.info(f"  Found: {mem.content[:60]}...")

        return profitable

    def _think(self, market_data: Dict, context: Dict, knowledge: List) -> Dict:
        """Decide what to do"""

        logger.info("💭 THINK:")

        # Check if should stop trading (risk limits)
        should_stop, reason = self.risk_mgr.should_stop_trading(market_data['account_balance'])

        if should_stop:
            return {
                'action': 'stop_trading',
                'reasoning': reason,
                'priority': 10
            }

        # Decision logic based on cycle
        if self.cycle_count % 10 == 0 or self.current_strategy is None:
            # Generate new strategy every 10 cycles
            decision = {
                'action': 'generate_strategy',
                'reasoning': 'Time to generate/optimize new strategy',
                'priority': 8
            }

        elif len(market_data['positions']) > 0:
            # Monitor existing positions
            decision = {
                'action': 'monitor_positions',
                'reasoning': 'Active positions need monitoring',
                'priority': 7
            }

        else:
            # Look for trading opportunity
            decision = {
                'action': 'find_trade',
                'reasoning': 'No open positions - seeking opportunity',
                'priority': 6
            }

        logger.info(f"  Decision: {decision['action']}")
        logger.info(f"  Reasoning: {decision['reasoning']}")

        return decision

    def _act(self, decision: Dict, market_data: Dict) -> Dict:
        """Execute decision"""

        logger.info(f"⚡ ACT: {decision['action']}")

        action = decision['action']

        try:
            if action == 'stop_trading':
                return {
                    'success': True,
                    'message': f"Trading stopped: {decision['reasoning']}"
                }

            elif action == 'generate_strategy':
                return self._generate_and_test_strategy(market_data)

            elif action == 'monitor_positions':
                return self._monitor_positions(market_data)

            elif action == 'find_trade':
                return self._find_trading_opportunity(market_data)

            else:
                return {
                    'success': False,
                    'message': f"Unknown action: {action}"
                }

        except Exception as e:
            logger.error(f"Action failed: {e}")
            return {
                'success': False,
                'message': f"Error: {e}"
            }

    def _generate_and_test_strategy(self, market_data: Dict) -> Dict:
        """Generate new strategy and backtest"""

        # Generate momentum strategy
        strategy = self.strategy_gen.generate_strategy(
            "momentum",
            {"lookback": 20, "threshold": 0.02}
        )

        # Save strategy
        filepath = self.strategy_gen.save_strategy(strategy)

        # Load strategy instance
        strategy_instance = self.strategy_gen.load_strategy(filepath)

        if strategy_instance is None:
            return {
                'success': False,
                'message': 'Failed to load generated strategy'
            }

        # Backtest
        result = self.backtester.run(strategy_instance, market_data['bars'])

        # Store performance
        self.strategy_performance[strategy.name] = result

        # Set as current if good performance
        if result.sharpe_ratio > 1.0:
            self.current_strategy = strategy_instance

            return {
                'success': True,
                'message': f"New strategy '{strategy.name}' - Sharpe: {result.sharpe_ratio:.2f}",
                'strategy': strategy,
                'backtest_result': result
            }

        return {
            'success': True,
            'message': f"Strategy tested but not adopted (Sharpe: {result.sharpe_ratio:.2f})"
        }

    def _monitor_positions(self, market_data: Dict) -> Dict:
        """Monitor open positions"""

        positions = market_data['positions']

        for pos in positions:
            logger.info(f"  Position {pos.ticket}: {pos.type} {pos.volume} @ ${pos.open_price:.2f}")
            logger.info(f"    Current P&L: ${pos.profit:.2f}")

        return {
            'success': True,
            'message': f"Monitored {len(positions)} positions"
        }

    def _find_trading_opportunity(self, market_data: Dict) -> Dict:
        """Find trading opportunity using current strategy"""

        if self.current_strategy is None:
            return {
                'success': False,
                'message': 'No active strategy'
            }

        # Generate signals
        signals = self.current_strategy.generate_signals(market_data['bars'])

        # Check latest signal
        latest_signal = signals.iloc[-1]

        if latest_signal == 0:
            return {
                'success': True,
                'message': 'No trading signal'
            }

        # Assess risk
        direction = "buy" if latest_signal == 1 else "sell"

        risk_assessment = self.risk_mgr.assess_trade(
            symbol="MNQ",
            direction=direction,
            entry_price=market_data['price']['bid'],
            account_balance=market_data['account_balance'],
            current_positions=market_data['positions'],
            atr=market_data['atr']
        )

        if not risk_assessment.approved:
            return {
                'success': False,
                'message': f"Trade rejected: {risk_assessment.reason}"
            }

        # Execute trade (paper trading mode check)
        if self.mode == "paper":
            logger.info(f"  [PAPER] Would execute: {direction.upper()} {risk_assessment.position_size:.2f} @ ${market_data['price']['bid']:.2f}")
            logger.info(f"  [PAPER] SL: ${risk_assessment.stop_loss:.2f}, TP: ${risk_assessment.take_profit:.2f}")

            return {
                'success': True,
                'message': f"Paper trade: {direction} signal",
                'paper_trade': True
            }

        else:
            # Live trading
            ticket = self.mt5.place_order(
                order_type=direction,
                volume=risk_assessment.position_size,
                sl=risk_assessment.stop_loss,
                tp=risk_assessment.take_profit
            )

            if ticket:
                return {
                    'success': True,
                    'message': f"Trade executed: {direction} ticket #{ticket}",
                    'ticket': ticket
                }
            else:
                return {
                    'success': False,
                    'message': 'Trade execution failed'
                }

    def _record(self, decision: Dict, result: Dict):
        """Record to memory"""

        remember_short(
            'action',
            f"{decision['action']}: {result['message']}"
        )

        if result['success']:
            remember_short('observation', f"✅ {decision['action']} completed")
        else:
            remember_short('observation', f"❌ {decision['action']} failed: {result['message']}")

        logger.info("📝 RECORD: Logged to memory")

    def _learn(self, decision: Dict, result: Dict):
        """Learn from results"""

        if not self.long_memory.enabled:
            return

        # Store successful strategy generation
        if decision['action'] == 'generate_strategy' and result.get('backtest_result'):
            backtest = result['backtest_result']

            if backtest.sharpe_ratio > 1.5:
                remember_long(
                    type='discovery',
                    content=f"High-performing strategy: {result['strategy'].name} - Sharpe: {backtest.sharpe_ratio:.2f}, Return: {backtest.total_return*100:.2f}%",
                    tags=['trading', 'strategy', 'profitable'],
                    importance=9
                )
                logger.info("🧠 LEARN: Stored high-performing strategy")

        # Store trading lessons
        if decision['action'] == 'find_trade' and not result['success']:
            remember_long(
                type='lesson',
                content=f"Trade rejected: {result['message']} - risk management working",
                tags=['trading', 'risk', 'safety'],
                importance=7
            )


def main():
    """Run autonomous trader"""

    print("🤖 PersonalAI Autonomous Trader\n")
    print("=" * 60)
    print()
    print("Decision Loop (every 5 minutes):")
    print("  1. READ   - Market data + memory")
    print("  2. QUERY  - Successful strategies")
    print("  3. THINK  - Generate/select strategy")
    print("  4. ACT    - Backtest → Trade")
    print("  5. RECORD - Results to memory")
    print("  6. LEARN  - Improve from P&L")
    print()
    print("=" * 60)
    print()
    print("Mode: PAPER TRADING (safe mode)")
    print()
    print("🚀 Starting autonomous trading...")
    print("⏸️  Press Ctrl+C to stop")
    print()

    trader = AutonomousTrader(mode="paper")
    trader.start()


if __name__ == "__main__":
    main()
