#!/usr/bin/env python3
"""
PersonalAI Unified Launcher

Start alle PersonalAI systemen:
- Autonomous Worker (general tasks)
- Autonomous Trader (MT5/MNQ)
- Telegram Bot
- Camera Dashboard
- Web Dashboard
"""

import sys
import argparse
import subprocess
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main launcher"""

    parser = argparse.ArgumentParser(description='PersonalAI Unified Launcher')
    parser.add_argument('mode', choices=[
        'worker',      # Autonomous worker (basic)
        'enhanced',    # Enhanced autonomous worker (vision+reasoning)
        'trader',      # Autonomous trader
        'telegram',    # Telegram bot
        'web',         # Web dashboard
        'camera',      # Camera dashboard
        'all',         # All systems
        'autonomous'   # Worker + Trader
    ], help='Which system to start')

    parser.add_argument('--paper', action='store_true',
                       help='Paper trading mode (trader only)')
    parser.add_argument('--live', action='store_true',
                       help='Live trading mode (trader only)')

    args = parser.parse_args()

    logger.info("🚀 PersonalAI Launcher")
    logger.info("=" * 60)

    if args.mode == 'worker':
        start_worker()

    elif args.mode == 'enhanced':
        start_enhanced_worker()

    elif args.mode == 'trader':
        mode = 'live' if args.live else 'paper'
        start_trader(mode)

    elif args.mode == 'telegram':
        start_telegram()

    elif args.mode == 'web':
        start_web()

    elif args.mode == 'camera':
        start_camera()

    elif args.mode == 'autonomous':
        start_autonomous()

    elif args.mode == 'all':
        start_all()


def start_worker():
    """Start basic autonomous worker"""
    logger.info("Starting Autonomous Worker (basic)...")
    subprocess.run([
        sys.executable,
        'core/autonomous_worker_standalone.py'
    ])


def start_enhanced_worker():
    """Start enhanced autonomous worker with vision+reasoning"""
    logger.info("Starting Enhanced Autonomous Worker (vision+reasoning)...")
    subprocess.run([
        sys.executable,
        'core/enhanced_autonomous_worker.py'
    ])


def start_trader(mode='paper'):
    """Start autonomous trader"""
    logger.info(f"Starting Autonomous Trader ({mode} mode)...")

    # Create trader script with mode
    script = f"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from trading.autonomous_trader import AutonomousTrader

trader = AutonomousTrader(mode="{mode}")
trader.start()
"""

    # Run trader
    subprocess.run([sys.executable, '-c', script])


def start_telegram():
    """Start Telegram bot"""
    logger.info("Starting Telegram Bot...")

    import os
    token = os.getenv('TELEGRAM_BOT_TOKEN')

    if not token:
        logger.error("❌ TELEGRAM_BOT_TOKEN not set")
        logger.info("   Set with: export TELEGRAM_BOT_TOKEN='your_token'")
        return

    subprocess.run([
        sys.executable,
        'interfaces/telegram_bot.py'
    ])


def start_web():
    """Start web dashboard"""
    logger.info("Starting Web Dashboard...")
    subprocess.run([
        sys.executable,
        'interfaces/web_app.py'
    ])


def start_camera():
    """Start camera dashboard"""
    logger.info("Starting Camera Dashboard...")
    subprocess.run([
        sys.executable,
        'interfaces/camera_dashboard.py'
    ])


def start_autonomous():
    """Start both autonomous systems"""
    logger.info("Starting Autonomous Systems (Worker + Trader)...")

    import multiprocessing

    # Start worker in background
    worker_process = multiprocessing.Process(target=start_worker)
    worker_process.start()

    # Start trader (paper mode by default)
    start_trader('paper')


def start_all():
    """Start all systems"""
    logger.info("Starting ALL PersonalAI Systems...")

    import multiprocessing

    # Start all in background
    processes = []

    p1 = multiprocessing.Process(target=start_worker)
    p1.start()
    processes.append(p1)

    p2 = multiprocessing.Process(target=lambda: start_trader('paper'))
    p2.start()
    processes.append(p2)

    # Wait for all
    for p in processes:
        p.join()


if __name__ == "__main__":
    main()
