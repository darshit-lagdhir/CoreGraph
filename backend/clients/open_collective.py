import uuid
from typing import Any, Dict, List

from clients.base import ResilientClient
from database import AsyncSessionLocal
from models import FinancialHealth
from sqlalchemy.dialects.postgresql import insert


class OpenCollectiveClient:
    def __init__(self):
        self.api_client = ResilientClient(base_url="https://api.opencollective.com")
        self.currency_rates = {
            "USD": 1.0,
            "EUR": 1.08,
            "GBP": 1.25,
            "INR": 0.012,
        }

    def normalize_currency(self, amount: float, currency: str) -> float:
        rate = self.currency_rates.get(currency.upper(), 1.0)
        return float(amount) * rate

    async def ingest_financial_ledgers(self, package_id: uuid.UUID, slug: str):
        url = "/graphql/v2"
        query = f"""
        query {{
            collective(slug: "{slug}") {{
                currency
                stats {{
                    yearlyBudget {{ value }}
                    balance {{ value }}
                }}
            }}
        }}
        """
        response = await self.api_client.execute_request("POST", url, json={"query": query})

        if response.status_code != 200:
            return

        data = response.json().get("data", {}).get("collective")

        if not data:
            return

        currency = data.get("currency", "USD")
        stats = data.get("stats", {})
        budget = stats.get("yearlyBudget", {}).get("value", 0.0)
        balance = stats.get("balance", {}).get("value", 0.0)

        normalized_budget = self.normalize_currency(float(budget or 0), currency)
        normalized_balance = self.normalize_currency(float(balance or 0), currency)

        financial_insert = {
            "id": uuid.uuid4(),
            "package_id": package_id,
            "funding_platform": "OpenCollective",
            "platform_slug": slug,
            "annual_budget_usd": normalized_budget,
            "current_balance_usd": normalized_balance,
            "is_commercially_backed": False,
        }

        async with AsyncSessionLocal() as session:
            stmt = insert(FinancialHealth).values([financial_insert])
            stmt = stmt.on_conflict_do_nothing(index_elements=["package_id"])
            await session.execute(stmt)
            await session.commit()

        await self.api_client.close()
