import httpx
import time
from tenacity import retry, wait_exponential_jitter, retry_if_exception_type, stop_after_attempt


class CircuitBreakerException(Exception):
    pass


class ResilientClient:
    def __init__(self, base_url: str = "", headers: dict = None):
        limits = httpx.Limits(max_connections=100, max_keepalive_connections=20)
        timeout = httpx.Timeout(10.0, connect=2.0)
        self.client = httpx.AsyncClient(
            base_url=base_url, headers=headers, limits=limits, timeout=timeout
        )
        self.failure_volume = 0
        self.circuit_open_expiration = 0.0

    def _verify_circuit(self):
        if time.time() < self.circuit_open_expiration:
            raise CircuitBreakerException(
                "Endpoint repeatedly dropped connections. Traffic locked."
            )

    def _register_failure(self):
        self.failure_volume += 1
        if self.failure_volume >= 5:
            self.circuit_open_expiration = time.time() + 60.0
            self.failure_volume = 0

    @retry(
        wait=wait_exponential_jitter(initial=2, max=60, exp_base=2, jitter=1.0),
        stop=stop_after_attempt(5),
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.RequestError)),
        reraise=True,
    )
    async def request_node(self, method: str, url: str, **kwargs) -> httpx.Response:
        self._verify_circuit()
        try:
            response = await self.client.request(method, url, **kwargs)
            if response.status_code == 404:
                return response

            if response.status_code in [429, 500, 502, 503, 504]:
                response.raise_for_status()

            self.failure_volume = 0
            return response
        except (httpx.HTTPStatusError, httpx.RequestError) as network_fault:
            self._register_failure()
            raise network_fault

    async def aclose(self):
        await self.client.aclose()
