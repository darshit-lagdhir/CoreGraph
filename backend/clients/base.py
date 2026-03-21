import httpx
from tenacity import retry, wait_exponential_jitter, retry_if_exception_type, stop_after_attempt

class ResilientClient:
    def __init__(self, base_url: str = "", headers: dict = None):
        limits = httpx.Limits(max_connections=100, max_keepalive_connections=20)
        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers=headers,
            limits=limits,
            timeout=10.0
        )

    @retry(
        wait=wait_exponential_jitter(initial=2, max=60, exp_base=2, jitter=1.0),
        stop=stop_after_attempt(5),
        retry=retry_if_exception_type(httpx.HTTPStatusError),
        reraise=True
    )
    async def execute_request(self, method: str, url: str, **kwargs) -> httpx.Response:
        response = await self.client.request(method, url, **kwargs)
        if response.status_code == 404:
            return response
        response.raise_for_status()
        return response

    async def close(self):
        await self.client.aclose()
