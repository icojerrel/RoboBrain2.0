# 🤖 PersonalAI Autonomous Trader

**Self-Improving Trading Agent voor MT5 met MNQ Futures**

Complete autonomous trading systeem dat zelf winstgevende strategies genereert, test, perfectioneert en handelt.

---

## 🎯 Features

✅ **MT5 Integration** - MetaTrader 5 connector voor MNQ futures
✅ **Strategy Generator** - Genereert Python trading strategies automatisch
✅ **Backtesting** - Test strategies op historical data
✅ **Risk Management** - Position sizing, stop loss, dagelijkse limits
✅ **Autonomous Trading** - Zelfstandig handelen zonder human input
✅ **Self-Learning** - Verbetert van P&L resultaten
✅ **Memory System** - Onthoudt succesvolle strategies
✅ **Paper Trading** - Veilig testen zonder echt geld

---

## 🏗️ Architectuur

```
┌──────────────────────────────────────────┐
│    AUTONOMOUS TRADER                     │
│                                          │
│  Decision Loop (5 min cycles):          │
│  1. READ   - Market data + memory       │
│  2. QUERY  - Successful strategies      │
│  3. THINK  - Generate/select strategy   │
│  4. ACT    - Backtest → Trade           │
│  5. RECORD - Results to memory          │
│  6. LEARN  - Improve from P&L           │
│                                          │
│         ↓            ↓            ↓      │
│    ┌────────┐  ┌─────────┐  ┌────────┐ │
│    │ MT5    │  │Strategy │  │ Risk   │ │
│    │Connect │  │  Gen    │  │Manager │ │
│    └────────┘  └─────────┘  └────────┘ │
│         ↓            ↓            ↓      │
│    ┌──────────────────────────────┐     │
│    │   MNQ Market Data (5min)     │     │
│    └──────────────────────────────┘     │
└──────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### **1. Install Dependencies**

```bash
cd PersonalAI

# Install MT5 Python package
pip install MetaTrader5

# Install trading dependencies
pip install pandas numpy

# Already installed: qdrant-client (memory)
```

### **2. Setup MT5**

1. Download en installeer [MetaTrader 5](https://www.metatrader5.com/)
2. Open demo account (of real account)
3. Login in MT5 terminal
4. Laat MT5 draaien op achtergrond

### **3. Test Connection**

```bash
python trading/mt5_connector.py
```

**Output:**
```
✅ Connected to MT5
   Account: 12345678
   Balance: $10000.00
   Equity: $10000.00

📊 MNQ Symbol Info:
   Bid: 16245.50
   Ask: 16246.00
```

### **4. Generate Strategy**

```bash
python trading/strategy_generator.py
```

**Output:**
```
✅ Generated: momentum_20241225_142030
📝 Description: Momentum trading strategy
⚙️  Parameters: {'lookback': 20, 'threshold': 0.02}
💾 Saved to: trading/strategies/momentum_20241225_142030.py
```

### **5. Backtest Strategy**

```bash
python trading/backtester.py
```

**Output:**
```
============================================================
BACKTEST RESULTS
============================================================
Total Return:        23.45%
Sharpe Ratio:          1.87
Max Drawdown:        -8.32%
Win Rate:            58.00%
Profit Factor:         2.15
```

### **6. Start Autonomous Trader (Paper Mode)**

```bash
python trading/autonomous_trader.py
```

**Output:**
```
🤖 PersonalAI Autonomous Trader

Mode: PAPER TRADING (safe mode)

🚀 Starting autonomous trading...
⏸️  Press Ctrl+C to stop

============================================================
🔄 TRADING CYCLE #0
============================================================

📖 READ Market Data:
  Price: $16247.50
  ATR: 45.32
  Balance: $10000.00
  Open positions: 0

💭 THINK:
  Decision: generate_strategy
  Reasoning: Time to generate/optimize new strategy

⚡ ACT: generate_strategy
✅ New strategy 'momentum_20241225_142500' - Sharpe: 1.92

📝 RECORD: Logged to memory
🧠 LEARN: Stored high-performing strategy
```

---

## 📊 Components

### **1. MT5 Connector** (`mt5_connector.py`)

**Features:**
- Connect to MT5 terminal
- Get market data (MNQ futures)
- Place/close orders
- Position management
- Account info

**Usage:**
```python
from trading.mt5_connector import get_mt5_connector

mt5 = get_mt5_connector()
mt5.connect()

# Get price
price = mt5.get_current_price("MNQ")
print(f"Bid: {price['bid']}, Ask: {price['ask']}")

# Get bars
bars = mt5.get_bars(symbol="MNQ", count=1000)

# Place order
ticket = mt5.place_order(
    order_type="buy",
    volume=0.1,
    sl=16200,
    tp=16300
)
```

---

### **2. Strategy Generator** (`strategy_generator.py`)

**Generates 3 types:**
- Momentum strategies
- Mean reversion strategies
- Breakout strategies

**Usage:**
```python
from trading.strategy_generator import get_strategy_generator

gen = get_strategy_generator()

# Generate momentum strategy
strategy = gen.generate_strategy("momentum", {
    "lookback": 20,
    "threshold": 0.02
})

# Save strategy
filepath = gen.save_strategy(strategy)

# Load strategy
strategy_instance = gen.load_strategy(filepath)

# Generate signals
signals = strategy_instance.generate_signals(bars)
# Returns: 1 (buy), -1 (sell), 0 (hold)
```

**Parameter Optimization:**
```python
# Optimize parameters
best_params, best_score = gen.optimize_parameters(
    strategy_type="momentum",
    param_ranges={
        "lookback": (10, 30),
        "threshold": (0.01, 0.05)
    },
    backtest_data=bars,
    iterations=20
)
```

**Evolution:**
```python
# Evolve strategy
evolved = gen.evolve_strategy(base_strategy, mutation_rate=0.1)
```

---

### **3. Backtester** (`backtester.py`)

**Metrics:**
- Total return
- Sharpe ratio
- Max drawdown
- Win rate
- Profit factor
- Trade statistics

**Usage:**
```python
from trading.backtester import get_backtester

backtester = get_backtester(initial_capital=10000)

# Run backtest
result = backtester.run(strategy_instance, bars)

print(f"Return: {result.total_return*100:.2f}%")
print(f"Sharpe: {result.sharpe_ratio:.2f}")
print(f"Trades: {result.total_trades}")
```

**Compare Strategies:**
```python
comparison = backtester.compare_strategies(
    [strategy1, strategy2, strategy3],
    bars
)
# Returns DataFrame sorted by Sharpe ratio
```

---

### **4. Risk Manager** (`risk_manager.py`)

**Risk Limits:**
- Max 1% risk per trade
- Max 3% daily loss
- Max 5% total portfolio risk
- Max 3 concurrent positions
- Stop loss = 2x ATR
- Take profit = 2x stop loss

**Usage:**
```python
from trading.risk_manager import get_risk_manager

risk_mgr = get_risk_manager()

# Assess trade
assessment = risk_mgr.assess_trade(
    symbol="MNQ",
    direction="buy",
    entry_price=16250,
    account_balance=10000,
    atr=50
)

if assessment.approved:
    print(f"Position size: {assessment.position_size}")
    print(f"Stop loss: {assessment.stop_loss}")
    print(f"Take profit: {assessment.take_profit}")
else:
    print(f"Rejected: {assessment.reason}")
```

**Kelly Criterion:**
```python
# Optimal position sizing
kelly = risk_mgr.calculate_kelly_criterion(
    win_rate=0.60,
    avg_win=100,
    avg_loss=50
)
```

---

### **5. Autonomous Trader** (`autonomous_trader.py`)

**Decision Loop:**
1. **READ** - Market data + memory
2. **QUERY** - Successful strategies from long-term memory
3. **THINK** - Generate/select strategy or find trade
4. **ACT** - Backtest → Trade (paper or live)
5. **RECORD** - Log results to short-term memory
6. **LEARN** - Store discoveries in long-term memory

**Modes:**
- **Paper trading** - Safe testing
- **Live trading** - Real money (use with caution!)

**Usage:**
```python
from trading.autonomous_trader import AutonomousTrader

# Paper trading mode (safe)
trader = AutonomousTrader(mode="paper")
trader.start()

# Live trading mode (real money!)
trader = AutonomousTrader(mode="live")
trader.start()
```

---

## ⚙️ Configuration

**MT5 Config:**
```python
from trading.mt5_connector import MT5Config

config = MT5Config(
    symbol="MNQ",              # Micro E-mini NASDAQ
    timeframe=mt5.TIMEFRAME_M5,  # 5-minute bars
    lot_size=0.1,              # Micro contract
    magic_number=888888        # Unique ID
)
```

**Risk Limits:**
```python
from trading.risk_manager import RiskLimits

limits = RiskLimits(
    max_risk_per_trade=0.01,    # 1% per trade
    max_daily_loss=0.03,        # 3% daily max
    max_position_size=0.1,      # 10% max position
    max_open_positions=3,       # Max 3 concurrent
    stop_loss_atr_mult=2.0,     # SL = 2x ATR
    take_profit_ratio=2.0       # TP/SL = 2:1
)
```

---

## 🧠 Memory & Learning

**Short-Term Memory:**
- Last 50 trading decisions
- Recent P&L results
- Active strategies

**Long-Term Memory:**
- High-performing strategies (Sharpe > 1.5)
- Trading lessons (failures to avoid)
- Market patterns discovered

**Learning Process:**
```
Cycle 1: Generate momentum strategy
      → Backtest: Sharpe 1.92
      → Store: "High-performing momentum strategy"

Cycle 5: Trade rejected (risk limit)
      → Store: "Risk management prevented bad trade"

Cycle 10: Generate new strategy
      → Query: Find similar high-performing strategies
      → Evolve: Based on past successes
```

---

## 📈 Strategy Types

### **Momentum Strategy**

**Logic:** Buy when price momentum > threshold

**Parameters:**
- `lookback`: Period for momentum calculation (10-30)
- `threshold`: Momentum threshold (0.01-0.05)

**Best for:** Trending markets

---

### **Mean Reversion Strategy**

**Logic:** Buy oversold, sell overbought (Bollinger Bands)

**Parameters:**
- `sma_period`: Moving average period (10-50)
- `std_mult`: Standard deviation multiplier (1.5-3.0)

**Best for:** Range-bound markets

---

### **Breakout Strategy**

**Logic:** Buy on breakout above resistance

**Parameters:**
- `breakout_period`: Lookback for high/low (15-30)
- `confirmation_bars`: Confirmation candles (1-3)

**Best for:** Volatile markets

---

## 🎮 Paper Trading vs Live

**Paper Trading (Recommended First):**
```python
trader = AutonomousTrader(mode="paper")
```

- ✅ No real money at risk
- ✅ Test strategies safely
- ✅ Verify autonomous logic
- ✅ Build confidence

**Live Trading (After Proven):**
```python
trader = AutonomousTrader(mode="live")
```

- ⚠️ Real money at risk
- ⚠️ Start with small capital
- ⚠️ Monitor closely
- ⚠️ Use strict risk limits

---

## 🛡️ Safety Features

**Built-in Protection:**
1. **Daily Loss Limit** - Stops trading at 3% daily loss
2. **Position Limits** - Max 3 concurrent positions
3. **Risk Per Trade** - Never risk >1% per trade
4. **Stop Losses** - Always placed (2x ATR)
5. **Paper Mode** - Test before live
6. **Memory Learning** - Avoids repeated mistakes

**Manual Override:**
- Press Ctrl+C to stop anytime
- Check positions in MT5 terminal
- Close positions manually if needed

---

## 📊 Performance Tracking

**View Results:**
```python
# Get account info
account = mt5.get_account_info()
print(f"Balance: ${account['balance']}")
print(f"Equity: ${account['equity']}")

# Get trade history
# (Check MT5 terminal → Account History)
```

**Memory Check:**
```python
from core.autonomous_memory import recall_recent

# Recent trading decisions
recent = recall_recent(20)
for mem in recent:
    if 'strategy' in mem.content or 'trade' in mem.content:
        print(f"[{mem.type}] {mem.content}")
```

---

## 🔧 Troubleshooting

### **MT5 Connection Failed**

```
❌ MT5 initialize failed
```

**Fix:**
1. Ensure MT5 is running
2. Login to demo/real account
3. Check firewall settings
4. Reinstall MetaTrader5 package: `pip install --upgrade MetaTrader5`

---

### **Symbol Not Found**

```
❌ Symbol MNQ not found
```

**Fix:**
1. Open Market Watch in MT5
2. Right-click → Symbols
3. Search "MNQ" → Show symbol
4. Check broker supports MNQ futures

---

### **Strategy Generation Failed**

```
❌ Failed to load generated strategy
```

**Fix:**
1. Check `trading/strategies/` directory exists
2. Verify Python syntax in generated file
3. Check file permissions

---

### **Qdrant Not Available**

```
⚠️ Qdrant not available - long-term memory disabled
```

**Fix (Optional):**
```bash
# Start Qdrant for long-term learning
docker run -d -p 6333:6333 qdrant/qdrant
```

*Not required - trader works with short-term memory only*

---

## 🚀 Advanced Usage

### **Custom Strategy Template**

Add to `strategy_generator.py`:

```python
self.strategy_templates["custom"] = '''
# Custom Strategy - {name}

class {class_name}:
    def __init__(self, param1={param1}):
        self.param1 = param1

    def generate_signals(self, data):
        # Your logic here
        signals = pd.Series(0, index=data.index)
        # ... calculate signals ...
        return signals
'''
```

### **Integration with Telegram**

```python
# Add to autonomous_trader.py _learn() method
if backtest.sharpe_ratio > 2.0:
    # Send alert via Telegram bot
    send_telegram_message(
        f"🚀 New high-performing strategy!\n"
        f"Sharpe: {backtest.sharpe_ratio:.2f}\n"
        f"Return: {backtest.total_return*100:.2f}%"
    )
```

### **Multi-Symbol Trading**

```python
# Create traders for multiple symbols
trader_mnq = AutonomousTrader(
    mt5_config=MT5Config(symbol="MNQ")
)

trader_mes = AutonomousTrader(
    mt5_config=MT5Config(symbol="MES")  # Micro S&P 500
)
```

---

## ⚠️ Disclaimer

**IMPORTANT RISK WARNING:**

Trading futures involves substantial risk of loss. This software is provided for educational purposes.

- ❌ Not financial advice
- ❌ No guarantee of profits
- ❌ Past performance ≠ future results
- ❌ Start with paper trading
- ❌ Use only risk capital
- ✅ Understand the risks
- ✅ Test thoroughly first
- ✅ Start small

**The developers are not responsible for trading losses.**

---

## 📚 Resources

**MT5 Python:**
- https://www.mql5.com/en/docs/integration/python_metatrader5

**MNQ Futures:**
- https://www.cmegroup.com/markets/equities/nasdaq/micro-e-mini-nasdaq-100.html

**Trading Strategy Development:**
- https://www.quantstart.com/

---

## ✅ Summary

Je hebt nu een **volledig autonomous trading systeem**:

✅ **MT5 Integration** - Live market data + execution
✅ **Strategy Generation** - Auto-creates trading strategies
✅ **Backtesting** - Tests strategies on historical data
✅ **Risk Management** - Protects capital with limits
✅ **Autonomous Trading** - Trades without human input
✅ **Self-Learning** - Improves from P&L results
✅ **Memory System** - Remembers successes/failures
✅ **Paper Trading** - Safe testing environment

**Next Steps:**
1. Test in paper mode
2. Monitor performance
3. Adjust risk limits
4. Let it learn
5. Gradually increase capital (if profitable)

**PersonalAI Autonomous Trader v1.0**
🤖 Self-improving trading agent powered by RoboBrain architecture
