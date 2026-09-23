"""Pre-request cost reservation, including requests with unknown final billing."""

from dataclasses import dataclass, field


class BudgetExceeded(RuntimeError):
    pass


@dataclass
class Budget:
    limit: float | None
    charged: float = 0.0


@dataclass
class Ledger:
    run: Budget
    episode: Budget
    records: list[dict] = field(default_factory=list)

    def reserve(self, amount: float):
        for name, budget in (("run", self.run), ("episode", self.episode)):
            if budget.limit is not None and budget.charged + amount > budget.limit + 1e-9:
                raise BudgetExceeded(f"{name} budget cannot cover the next request")
        self.run.charged += amount
        self.episode.charged += amount

    def settle(self, reserved: float, charged: float, record: dict):
        self.run.charged += charged - reserved
        self.episode.charged += charged - reserved
        self.records.append({**record, "budget_charge_usd": charged})

    def summary(self):
        return {
            "budget_charge_usd": round(self.episode.charged, 6),
            "run_budget_charge_usd": round(self.run.charged, 6),
            "records": self.records,
        }
