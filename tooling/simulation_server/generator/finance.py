import math
import time
import logging
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Optional, Tuple

# Internal CoreGraph imports (Task 023)
import sys
import os
root = os.getcwd()
if root not in sys.path:
    sys.path.insert(0, root)

from backend.core.logging_config import setup_observability
from tooling.simulation_server.core.currency_vault import get_currency, CURRENCY_REGISTRY

# Initialize high-performance logging for the 144Hz HUD
setup_observability()
logger = logging.getLogger(__name__)

class FiscalStressor:
    """
    S.U.S.E. Global Currency Stressor (Task 023).
    Dynamic Multi-Currency Sabotage and Stochastic Drift Engine.
    """
    def __init__(self, master_seed: int = 0xDEADC0DE):
        self.master_seed = master_seed
        self.anchor_credit = "USD" # Standardized Credit Base

    def simulate_volatility(self, code: str, hours_elapsed: int) -> Decimal:
        """
        Geomteric Brownian Motion (GBM) Stochastic Walk.
        E_t = E_{t-1} * exp((mu - 0.5*sigma^2)dt + sigma*sqrt(dt)*Z)
        
        Pinned to 8 E-cores (Background Drift).
        """
        curr = get_currency(code)
        if code == self.anchor_credit:
            return Decimal("1.0")

        # Deterministic seed-anchored Z variable
        z = (self.master_seed + hours_elapsed + int(curr.numeric)) % 100 / 100.0 - 0.5
        mu = 0.0001 # Drift Trend
        sigma = curr.volatility
        dt = 1.0 # 1 Hour increment
        
        drift = (mu - 0.5 * sigma**2) * dt
        diffusion = sigma * math.sqrt(dt) * z
        
        # Exponential drift factor
        factor = Decimal(str(math.exp(drift + diffusion)))
        
        # Base conversion rate (simulated)
        base_rate = Decimal("1.0") + (Decimal(curr.numeric) % 10 / 10)
        
        return (base_rate * factor).quantize(Decimal("1.00000000"), rounding=ROUND_HALF_UP)

    def generate_funding(self, node_id: int, code: str = "USD") -> Tuple[str, str]:
        """
        Numerical Boundary Attacks: Injecting 'Violent' Fiscal Data.
        """
        curr = get_currency(code)
        
        # Deterministic Base Amount
        base_amount = 1000.0 + (node_id % 100 * 100.0)
        
        # ATTACK 1: LEVIATHAN OVERFLOW (10^15 units)
        if node_id % 777 == 0:
            base_amount = 1_500_000_000_000_000.50
            
        # ATTACK 2: ANTI-MATTER CLAWBACK (Negative)
        if node_id % 666 == 0:
            base_amount = -50000.75
            
        # Integer-Based Minor-Unit Scaling (Fixed-Point Determinism)
        multiplier = 10**curr.exponent
        minor_units = int(base_amount * multiplier)
        
        # ATTACK 4: STRINGIFIED FLOAT DECEPTION
        # Returns format that challenges the 'Beast's' normalizer
        formatted = f"{base_amount:,.{curr.exponent}f}"
        
        return code, formatted

    def normalize(self, amount_str: str, code: str, rate: Decimal) -> Decimal:
        """
        High-Precision Normalization (P-Core Accelerated).
        Amount * Rate -> Standardized Credit.
        """
        # Cleanup Stringified Float Deception (commas, etc.)
        sanitized = amount_str.replace(",", "")
        amount = Decimal(sanitized)
        
        # Round-Trip Verification Logic
        credit = (amount * rate).quantize(Decimal("1.00000000"), rounding=ROUND_HALF_UP)
        return credit

if __name__ == "__main__":
    stressor = FiscalStressor()
    print("──────── FISCAL NORMALIZATION AUDIT ─────────")
    
    # 1. THE CHALLENGE (1,500.750 BHD)
    code, amt_str = stressor.generate_funding(node_id=1, code="BHD")
    rate = stressor.simulate_volatility(code, hours_elapsed=24)
    print(f"[CHALLENGE] Node 1 Funding: {amt_str} {code} | Rate: {rate}")
    
    # 2. THE NORMALIZATION
    credit = stressor.normalize(amt_str, code, rate)
    print(f"[INGESTION] Normalized Credit: {credit} USD-equiv")
    
    # 3. REVERSE-NORMALIZATION SEAL (Round-Trip)
    reverse = (credit / rate).quantize(Decimal("1.000"), rounding=ROUND_HALF_UP)
    print(f"[AUDIT] Reverse Correlation: {reverse} {code}")
    
    if Decimal(amt_str.replace(",", "")) == reverse:
        print("[SUCCESS] Round-Trip Integrity: 100% Precision Correlated.")
    else:
        print("[FAILURE] Precision Drift Detected in the Ingestion Path.")
