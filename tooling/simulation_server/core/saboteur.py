import random
import json
from typing import Dict, Any, Optional

class PayloadSaboteur:
    """
    S.U.S.E. Lethal Payload Corruption Kernel (Task 024).
    Adversarial Byte Sabotage and mid-transmission structural mutation.
    """
    def __init__(self):
        self.active_mutations: Dict[str, Any] = {}

    def configure(self, mutations: Dict[str, Any]):
        """
        Dynamically update the Sabotage Registry via the Chaos Interface.
        """
        self.active_mutations.update(mutations)

    def apply_sabotage(self, payload: str, endpoint: str) -> str:
        """
        Asynchronous Byte Interceptor: Applying 'Lethal Mutations'.
        """
        mutation = self.active_mutations.get(endpoint)
        if not mutation:
            return payload

        mode = mutation.get("mode")
        probability = mutation.get("probability", 0.1)

        if random.random() > probability:
            return payload

        # MODE 1: ADVERSARIAL JSON TRUNCATION (50% Split)
        if mode == "TRUNCATE":
            split_at = len(payload) // 2
            return payload[:split_at]

        # MODE 2: BRACKET TRAP (Removing closing braces)
        if mode == "BRACKET_TRAP":
            return payload.rstrip("}] \n\r")

        # MODE 3: CHARACTER-ENCODING SABOTAGE (Null-Byte Injection)
        if mode == "NULL_BYTE":
            # Injecting Mid-String Termination into a critical field
            index = payload.find('"purl"')
            if index != -1:
                return payload[:index+15] + "\x00" + payload[index+15:]
            return payload

        # MODE 4: TYPE BOMB (Primitive Swap)
        if mode == "TYPE_BOMB":
            # Swapping List of Nodes for a Boolean 'True'
            if '"nodes": [' in payload:
                return payload.replace('"nodes": [', '"nodes": true, "junk": [')
            return payload

        return payload

if __name__ == "__main__":
    saboteur = PayloadSaboteur()
    test_json = '{"data": {"nodes": [{"id": "1", "purl": "pkg:npm/react"}]}}'

    print("──────── PAYLOAD SABOTEUR SHIELD AUDIT ─────────")
    # Test Truncation
    saboteur.configure({"test": {"mode": "TRUNCATE", "probability": 1.0}})
    res = saboteur.apply_sabotage(test_json, "test")
    print(f"[MUTATION] Truncated Payload: {res}")

    # Test Null-Byte
    saboteur.configure({"test": {"mode": "NULL_BYTE", "probability": 1.0}})
    res = saboteur.apply_sabotage(test_json, "test")
    print(f"[MUTATION] Null-Byte Poison: {res.encode('utf-8')}")

    # Test Type Bomb
    saboteur.configure({"test": {"mode": "TYPE_BOMB", "probability": 1.0}})
    res = saboteur.apply_sabotage(test_json, "test")
    print(f"[MUTATION] Type Bomb Swapped: {res}")
