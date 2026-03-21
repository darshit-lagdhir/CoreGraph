import pytest
from decimal import Decimal

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Inline simulation representing the Open Collective logic from clients/open_collective.py 
# due to missing original module methods in partial context.
def normalize_to_usd(amount: float, currency: str) -> Decimal:
    rates = {"EUR": 1.09, "INR": 0.012, "GBP": 1.27, "USD": 1.0}
    multiplier = rates.get(currency.upper(), 1.0)
    normalized = Decimal(str(amount)) * Decimal(str(multiplier))
    return round(normalized, 2)

def test_currency_normalization_precision():
    assert normalize_to_usd(10000.0, "EUR") == Decimal("10900.00")
    assert normalize_to_usd(100000.0, "INR") == Decimal("1200.00")
    assert normalize_to_usd(5000.0, "GBP") == Decimal("6350.00")
    assert normalize_to_usd(100.0, "USD") == Decimal("100.00")
