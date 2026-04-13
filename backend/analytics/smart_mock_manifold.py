import asyncio
import json
import os
import sys
import hashlib
import random
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import google.generativeai as genai
from backend.core.config import settings

class NeuralBridgeManifold:
    """Asynchronous Gemini 1.5 Flash Cognition Kernel"""
    def __init__(self):
        api_key = settings.GOOGLE_AI_API_KEY.get_secret_value() if settings.GOOGLE_AI_API_KEY else "MOCK_KEY"
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction="You are a Senior OSINT Engineer tracking a 3.81M node dependency graph. Return deterministic, binary-compatible JSON.",
            generation_config=genai.GenerationConfig(temperature=0.0)
        )
        self.cache = {}

    async def synthesize_audit(self, package_id: str) -> dict:
        if package_id in self.cache: return self.cache[package_id]
        payload = f"Generate forensic risk metrics for {package_id}. Fields: entropy (float), risk (float), status (STABLE, ANOMALY, CRITICAL), detail (string max 50 chars)."
        try:
            response = await self.model.generate_content_async(payload)
            raw_text = response.text.replace("```json", "").replace("```", "").strip()
            result = json.loads(raw_text)
            self.cache[package_id] = result
            return result
        except Exception as e:
            return {"entropy": 1.0, "risk": 1.0, "status": "CRITICAL", "detail": f"LOCAL FALLBACK ENGAGED: API FAULT"}

class VolumetricInfusionKernel:
    """Asynchronous 3.81M Node Procedural Sharding Kernel"""
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.target_nodes = 3810000
        self.active = True

    def _deterministic_hash(self, index: int) -> str:
        return hashlib.md5(f"node_{self.seed}_{index}".encode()).hexdigest()[:12]

    async def lazily_stream_topology(self, batch_size: int = 5000):
        current = 0
        while current < self.target_nodes and self.active:
            batch = []
            max_range = min(current + batch_size, self.target_nodes)
            for i in range(current, max_range):
                batch.append(f"pkg_{self._deterministic_hash(i)}")
            current = max_range
            yield batch
            await asyncio.sleep(0.001)

class ForensicVerdictEngine:
    """Sovereign Synthesizer for Multivariate Risk Scaling and Intelligent Impact Reporting"""
    def __init__(self):
        api_key = settings.GOOGLE_AI_API_KEY.get_secret_value() if settings.GOOGLE_AI_API_KEY else "MOCK_KEY"
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction="You are a Senior Strategic OSINT Architect. Evaluate telemetry closures. Provide Multivariate Risk Scoring. Output strict JSON: {\"adversarial\": \"...\", \"maintenance\": \"...\", \"structural\": \"...\", \"verdict\": \"...\"}",
            generation_config=genai.GenerationConfig(temperature=0.0)
        )

    async def generate_impact_report(self, node_context: dict) -> dict:
        try:
            payload = f"Generate precise technical summary for cluster telemetry. Impose absolute authority: {json.dumps(node_context)[:1000]}"
            response = await self.model.generate_content_async(payload)
            raw_text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(raw_text)
        except Exception as e:
            return {
                "adversarial": "CRITICAL - MULTIVARIATE TIMEOUT",
                "maintenance": "UNKNOWN - FRAGILE BOUNDARY",
                "structural": "DEGRADED - CONTEXT OVERFLOW",
                "verdict": f"NON-REPUDIABLE FALLBACK: {str(e)[:50]}"
            }

