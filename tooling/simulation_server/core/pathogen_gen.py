import random
import uuid
from typing import List, Dict, Any

# Internal CoreGraph imports (Task 027 persistent paths)
import sys
import os
root = os.getcwd()
if root not in sys.path:
    sys.path.insert(0, root)

class PathogenGenerator:
    """
    S.U.S.E. Pathogen Injector (Task 015).
    Architect of Contagion for the 3.88M node software ocean.
    """
    def __init__(self, seed: int = 1337):
        self.rng = random.Random(seed)

    def inject_cve(self, target_type: str = "FOUNDATIONAL") -> Dict[str, Any]:
        cve_id = f"CVE-2026-{self.rng.randint(1000, 9999)}"

        # Target Selection Matrix
        if target_type == "FOUNDATIONAL":
            purl = "pkg:npm/core-utility-hub"
            cvss = 9.8
        elif target_type == "DEEP_CHAIN":
            purl = "pkg:pypi/obscure-transitive-leaf"
            cvss = 7.5
        else: # SOCIAL_TRUST
            purl = "pkg:github/trusted-maintainer-lib"
            cvss = 8.4

        return {
            "cve_id": cve_id,
            "patient_zero": purl,
            "severity": cvss,
            "type": target_type,
            "infected_versions": ["1.2.3", "1.2.4"]
        }

if __name__ == "__main__":
    gen = PathogenGenerator()
    outbreak = gen.inject_cve(target_type="FOUNDATIONAL")
    print(f"[PATHOGEN] Injected {outbreak['cve_id']} into {outbreak['patient_zero']} (CVSS: {outbreak['severity']})")
