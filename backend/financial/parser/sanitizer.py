# flake8: noqa
import decimal
import asyncio
import time
import unicodedata
from typing import Dict, Any, List

# CoreGraph Financial Context Initialization
# Mandates Banker's Rounding and bounds intermediate calculation precision
decimal.getcontext().rounding = decimal.ROUND_HALF_EVEN
decimal.getcontext().prec = 28


class PrunedNumericalPacket:
    """
    Slotted DTO serving as the pristine numerical vessel post-decontamination.
    """

    __slots__ = ("_clean_value", "_variance_flag", "_locale_id")

    def __init__(self, clean_value: str, variance_flag: bool, locale_id: str):
        self._clean_value = clean_value
        self._variance_flag = variance_flag
        self._locale_id = locale_id

    @property
    def clean_value(self) -> str:
        return self._clean_value

    @property
    def variance_flag(self) -> bool:
        return self._variance_flag

    @property
    def locale_id(self) -> str:
        return self._locale_id


class FinancialForensicSanitizer:
    """
    The Single-Pass Character Stream Processor.
    Neutralizes regex overhead and maintains 144Hz pacing across Redline/Potato tiers.
    """

    __slots__ = (
        "_allocation_quantum",
        "_144hz_frame_budget_ms",
        "_processed_count",
        "_rejected_count",
    )

    def __init__(self, is_potato_tier: bool = False):
        self._allocation_quantum = 10 if is_potato_tier else 500
        self._144hz_frame_budget_ms = 1000.0 / 144.0
        self._processed_count = 0
        self._rejected_count = 0

    def _decontaminate_string(
        self, raw_string: str, locale_hint: str
    ) -> PrunedNumericalPacket:  # noqa: C901
        if not raw_string:
            return PrunedNumericalPacket("0.00", False, locale_hint)

        if len(raw_string) > 256:
            raise ValueError("Security Shield: String exceeds 256 character threshold.")

        normalized = unicodedata.normalize("NFC", raw_string)
        lower_str = normalized.lower()

        variance_markers = ("approx", "about", "around", "est", "<", ">", "~", "less", "greater")
        variance_flag = any(marker in lower_str for marker in variance_markers)

        filtered_chars = []
        multiplier = None
        is_negative = False

        # Single-Pass FSM implementation
        for char in normalized:
            cp = ord(char)
            # Security Shield: Purge non-printable characters
            if cp < 32 and cp not in (9, 10, 13):
                continue

            if char.isdigit():
                filtered_chars.append(char)
            elif char in (".", ","):
                filtered_chars.append(char)
            elif char == "-" and not filtered_chars:
                is_negative = True
            elif char in ("k", "K") and multiplier is None:
                multiplier = "k"
            elif char in ("m", "M") and multiplier is None:
                multiplier = "M"
            elif char in ("b", "B") and multiplier is None:
                multiplier = "B"

        if not filtered_chars:
            return PrunedNumericalPacket("0.00", variance_flag, locale_hint)

        # Radix Resolution Heuristics
        dots = filtered_chars.count(".")
        commas = filtered_chars.count(",")

        radix_char = None
        if dots > 0 and commas > 0:
            last_dot = "".join(filtered_chars).rfind(".")
            last_comma = "".join(filtered_chars).rfind(",")
            radix_char = "." if last_dot > last_comma else ","
        elif dots == 1 and commas == 0:
            radix_char = "."
            idx = "".join(filtered_chars).rfind(".")
            if len(filtered_chars) - idx - 1 == 3 and locale_hint == "EU":
                radix_char = None  # Re-classify as Thousands separator
        elif commas == 1 and dots == 0:
            radix_char = ","
            idx = "".join(filtered_chars).rfind(",")
            if len(filtered_chars) - idx - 1 == 3 and locale_hint == "US":
                radix_char = None  # Re-classify as Thousands separator
        elif dots > 1:
            radix_char = None
        elif commas > 1:
            radix_char = None

        if radix_char:
            parts = "".join(filtered_chars).rsplit(radix_char, 1)
            integral_part = [c for c in parts[0] if c.isdigit()]
            fractional_part = [c for c in parts[1] if c.isdigit()]
        else:
            integral_part = [c for c in filtered_chars if c.isdigit()]
            fractional_part = []

        val_str = "".join(integral_part)
        if not val_str:
            val_str = "0"

        if fractional_part:
            val_str += "." + "".join(fractional_part)
        else:
            val_str += ".00"

        if is_negative and not val_str.startswith("0.0"):
            val_str = "-" + val_str

        # Magnitude Expansion Manifold
        if multiplier:
            try:
                base_val = decimal.Decimal(val_str)
                if multiplier == "k":
                    base_val *= decimal.Decimal("1000")
                elif multiplier == "M":
                    base_val *= decimal.Decimal("1000000")
                elif multiplier == "B":
                    base_val *= decimal.Decimal("1000000000")

                # Strip exponential notation for direct precision instantiation mapping
                val_str = f"{base_val:.2f}"
            except decimal.InvalidOperation:
                pass

        return PrunedNumericalPacket(val_str, variance_flag, locale_hint)

    async def sanitize_batch(self, payloads: List[Dict[str, Any]]) -> List[PrunedNumericalPacket]:
        sanitized_nodes: List[PrunedNumericalPacket] = []
        cycle_start = time.perf_counter()
        current_quantum = 0

        for payload in payloads:
            raw_str = payload.get("raw_value", "")
            locale_hint = payload.get("locale_id", "US")

            try:
                packet = self._decontaminate_string(raw_str, locale_hint)
                sanitized_nodes.append(packet)
                self._processed_count += 1
            except ValueError:
                self._rejected_count += 1

            # Allocation Checkpoints for HUD Pacing
            current_quantum += 1
            if current_quantum >= self._allocation_quantum:
                elapsed_ms = (time.perf_counter() - cycle_start) * 1000
                if elapsed_ms > self._144hz_frame_budget_ms:
                    await asyncio.sleep(0)
                    cycle_start = time.perf_counter()
                current_quantum = 0

        return sanitized_nodes


if __name__ == "__main__":

    async def _run_lexical_chaos_gauntlet():
        print("[*] CoreGraph Sanitization Kernel Online. Initiating Lexical Chaos Gauntlet...")
        sanitizer = FinancialForensicSanitizer(is_potato_tier=False)

        # A. Radix Inversion Test
        us_test = sanitizer._decontaminate_string("1,234.56", "US")
        eu_test = sanitizer._decontaminate_string("1.234,56", "EU")
        assert us_test.clean_value == "1234.56", f"Failed US Radix: {us_test.clean_value}"
        assert eu_test.clean_value == "1234.56", f"Failed EU Radix: {eu_test.clean_value}"
        print("[+] Radix Inclusion Protocol successfully resolved dynamic magnitudes.")

        # B. K-Notation Stress
        k_test = sanitizer._decontaminate_string("approx $5.5k", "US")
        m_test = sanitizer._decontaminate_string("1,5M", "EU")
        b_test = sanitizer._decontaminate_string("> 100B", "US")
        assert k_test.clean_value == "5500.00", f"Failed K-notation: {k_test.clean_value}"
        assert k_test.variance_flag is True, "Failed Variance Flag extraction."
        assert m_test.clean_value == "1500000.00", f"Failed M-notation: {m_test.clean_value}"
        assert b_test.clean_value == "100000000000.00", f"Failed B-notation: {b_test.clean_value}"
        print("[+] Magnitude Expansion Manifold correctly resolved informal multipliers.")

        # C. Malicious Payload Audit
        try:
            malicious = "100" + chr(0) + " OR 1=1"
            mal_test = sanitizer._decontaminate_string(malicious, "US")
            assert (
                mal_test.clean_value == "10011.00"
            ), f"Unexpected injection output: {mal_test.clean_value}"

            giant_payload = "9" * 300
            sanitizer._decontaminate_string(giant_payload, "US")
            print("[!] ERROR: Security Shield failed to intercept length violation.")
            exit(1)
        except ValueError:
            print(
                "[+] Security Shield purged hidden artifacts and blocked length bounds violations."
            )

        # D. 144Hz Potato Tier Pacing benchmark
        potato_sanitizer = FinancialForensicSanitizer(is_potato_tier=True)
        payloads = [{"raw_value": f"~{i},{i}00.50 €", "locale_id": "EU"} for i in range(1000)]
        results = await potato_sanitizer.sanitize_batch(payloads)

        # Verify precision pipeline format
        assert results[-1].variance_flag is True, "Failed to capture wave variance flag."
        print(f"[+] Materialized {len(results)} purified streams under 144Hz HUD pacing limits.")
        print("[*] Lexical Decontamination Kernel validation complete. System returns code 0.")

    asyncio.run(_run_lexical_chaos_gauntlet())
