#!/usr/bin/env python3
"""
PersonalAI - Jouw Persoonlijke AI Assistent
Main launcher voor alle interfaces
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import config

def launch_telegram_bot():
    """Start Telegram bot interface"""
    print("🤖 Starting Telegram Bot...")
    from interfaces.telegram_bot import main
    main()

def launch_web_interface():
    """Start web dashboard"""
    print("🌐 Starting Web Interface...")
    try:
        from interfaces.web_app import main
        main()
    except ImportError:
        print("❌ Gradio niet geïnstalleerd!")
        print("📦 Installeer met: pip install gradio")
        sys.exit(1)

def run_tests():
    """Run system tests"""
    print("🧪 Running System Tests...\n")

    # Test brain
    print("1️⃣ Testing Brain...")
    try:
        from core.brain import get_brain
        brain = get_brain()
        print(f"   ✅ Brain ready: {brain.get_capabilities()}")
    except Exception as e:
        print(f"   ❌ Brain failed: {e}")
        return False

    # Test memory
    print("\n2️⃣ Testing Memory...")
    try:
        from core.memory import get_memory, get_preferences
        memory = get_memory("test_user")
        memory.add_message("user", "Test message")
        print(f"   ✅ Memory working: {memory.get_stats()}")
    except Exception as e:
        print(f"   ❌ Memory failed: {e}")
        return False

    # Test vision
    print("\n3️⃣ Testing Vision Module...")
    try:
        from modules.vision import get_vision_assistant
        vision = get_vision_assistant()
        print("   ✅ Vision module ready")
    except Exception as e:
        print(f"   ❌ Vision failed: {e}")
        return False

    # Test X-ray (optioneel)
    if config.ENABLE_XRAY_MODULE:
        print("\n4️⃣ Testing X-ray Module...")
        try:
            from modules.xray import get_xray_analyzer
            xray = get_xray_analyzer()
            print("   ✅ X-ray module ready")
        except Exception as e:
            print(f"   ⚠️ X-ray not available: {e}")

    print("\n✅ All tests passed!")
    return True

def show_status():
    """Show system status"""
    print("📊 PersonalAI System Status\n")
    print(f"📁 Base Directory: {config.BASE_DIR}")
    print(f"💾 Data Directory: {config.DATA_DIR}")
    print(f"🤖 Model: {config.ROBOBRAIN_MODEL}")
    print(f"🧠 Thinking Mode: {'Enabled' if config.DEFAULT_THINKING else 'Disabled'}")
    print(f"🔬 X-ray Module: {'Enabled' if config.ENABLE_XRAY_MODULE else 'Disabled'}")
    print(f"🌐 Language: {config.LANGUAGE}")
    print(f"📱 Telegram Token: {'✅ Set' if config.TELEGRAM_TOKEN else '❌ Not set'}")

def main():
    """Main launcher"""
    parser = argparse.ArgumentParser(
        description="PersonalAI - Jouw Persoonlijke AI Assistent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s telegram           Start Telegram bot
  %(prog)s web                Start web interface
  %(prog)s test               Run system tests
  %(prog)s status             Show system status

Voor meer informatie, zie README.md
        """
    )

    parser.add_argument(
        'interface',
        choices=['telegram', 'web', 'test', 'status'],
        help='Interface om te starten'
    )

    args = parser.parse_args()

    # Show banner
    print("""
╔═══════════════════════════════════════╗
║      PersonalAI - v1.0                ║
║  Jouw Persoonlijke AI Assistent       ║
║                                       ║
║  Powered by RoboBrain 2.0             ║
╚═══════════════════════════════════════╝
    """)

    if args.interface == 'telegram':
        launch_telegram_bot()
    elif args.interface == 'web':
        launch_web_interface()
    elif args.interface == 'test':
        run_tests()
    elif args.interface == 'status':
        show_status()

if __name__ == "__main__":
    main()
