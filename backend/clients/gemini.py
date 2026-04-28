import httpx
from core.config import settings


class LiveGeminiClient:
    """Uses real GOOGLE_AI_API_KEY to generate live threat & blast-radius analysis."""

    def __init__(self):
        self.api_key = settings.GOOGLE_AI_API_KEY.get_secret_value()
        # Ensure we use an active model from Gemini limits
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={self.api_key.strip()}"
        self.client = httpx.AsyncClient(timeout=15.0)

    async def analyze_package(
        self, package: str, eco: str, deps_count: int, gh_stats: dict
    ) -> dict:
        if not self.api_key or self.api_key == "sk-dummy-token":
            return {"error": "Dummy AI token active.", "verdict": "SCAN ABORTED"}

        system_prompt = f"""
        Analyze '{package}' in the '{eco}' ecosystem.
        Live telemetry: Direct Dependencies: {deps_count}. GitHub metrics: {gh_stats.get('stars', 'Unknown')} stars, {gh_stats.get('issues', 'Unknown')} open issues.
        Return EXACTLY 2-3 short, highly in-depth technical sentences. Focus strictly on what the package is doing at a low level, its structural importance, and any real-world adversarial/security risks associated with it. Do not use fluff.
        """

        payload = {"contents": [{"parts": [{"text": system_prompt}]}]}

        try:
            resp = await self.client.post(self.url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                try:
                    verdict_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    # Splitting verdict casually into 3 blocks for the UI
                    sentences = [
                        s.strip() + "."
                        for s in verdict_text.replace("\n", " ").split(".")
                        if len(s.strip()) > 5
                    ]

                    return {
                        "adversarial": (
                            sentences[0] if len(sentences) > 0 else "Analysis inconclusive."
                        ),
                        "maintenance": (
                            sentences[1] if len(sentences) > 1 else "Maintenance check skipped."
                        ),
                        "structural": (
                            sentences[2] if len(sentences) > 2 else "Structural integrity untested."
                        ),
                        "verdict": (
                            "CRITICAL RELIANCE" if deps_count > 10 else "STABLE ARCHITECTURE"
                        ),
                    }
                except KeyError:
                    return {"error": "AI struct failure."}
            return {"error": f"AI Engine unreachable (HTTP {resp.status_code})"}
        except Exception as e:
            return {"error": f"AI Engine Error: {str(e)}"}

    async def close(self):
        await self.client.aclose()
