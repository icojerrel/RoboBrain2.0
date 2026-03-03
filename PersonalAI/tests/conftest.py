"""
Pytest configuration and shared fixtures
"""

import pytest
import sys
from pathlib import Path

# Add PersonalAI to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Suppress warnings
pytest.register_assert_rewrite('tests')
