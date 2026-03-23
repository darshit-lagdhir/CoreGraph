import uuid
from typing import Dict, Any, List

class SBOMMapper:
    """
    Forensic SBOM Generation Engine.
    Maps internal CoreGraph OSINT intelligence to CycloneDX 1.6 standards.
    Transforms graph-theoretic indices into compliant property extensions.
    """
    def __init__(self, bom_format: str = "CycloneDX", version: str = "1.6"):
        self.bom_format = bom_format
        self.version = version

    def map_node_to_cyclonedx(self, node_data: Dict[str, Any], risk_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transforms a 3.88M graph node into a legal evidence component.
        """
        return {
            "type": "library",
            "bom-ref": f"pkg:{node_data['ecosystem']}/{node_data['name']}@{node_data['version']}",
            "name": node_data['name'],
            "version": node_data['version'],
            "purl": f"pkg:{node_data['ecosystem']}/{node_data['name']}@{node_data['version']}",
            "hashes": [
                {"alg": "SHA-256", "content": node_data.get('sha256_checksum', "0"*64)}
            ],
            # PROPRIETARY EVIDENCE EXTENSIONS (Task 023.1)
            "properties": [
                {"name": "coregraph:risk_score", "value": str(risk_data.get('r_idx', 0.0))},
                {"name": "coregraph:criticality", "value": str(risk_data.get('c_idx', 0.0))},
                {"name": "coregraph:maintainer_velocity", "value": str(risk_data.get('v_beh', 0.0))},
                {"name": "coregraph:provenance_root", "value": risk_data.get('merkle_root', "NULL")}
            ]
        }

    def generate_full_bom(self, nodes: List[Dict[str, Any]], dependencies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Creates a complete CycloneDX document with dependency graph.
        """
        components = [self.map_node_to_cyclonedx(n, n.get('risk_meta', {})) for n in nodes]
        
        # Dependency Graph Reduction (Task 023.3)
        # Translates edges into SBOM 'dependencies' array
        bom_deps = []
        for d in dependencies:
            bom_deps.append({
                "ref": d['source_ref'],
                "dependsOn": [d['target_ref']]
            })
            
        return {
            "bomFormat": self.bom_format,
            "specVersion": self.version,
            "serialNumber": f"urn:uuid:{uuid.uuid4()}",
            "version": 1,
            "metadata": {
                "timestamp": "2026-03-23T14:40:00Z", # OSINT generation window
                "tool": {"name": "CoreGraph Sentinel", "version": "2.0.0"}
            },
            "components": components,
            "dependencies": bom_deps
        }
