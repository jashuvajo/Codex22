from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TrailingPosition:
    symbol: str
    entry: float
    qty: int
    stop: float
    target: float
    best_price: float
    opened_at: datetime = field(default_factory=datetime.utcnow)


class TrailingEngine:
    def __init__(self) -> None:
        self.positions: dict[str, TrailingPosition] = {}

    def register(self, symbol: str, entry: float, qty: int, target_points: float, stop_points: float) -> None:
        self.positions[symbol] = TrailingPosition(
            symbol=symbol,
            entry=entry,
            qty=qty,
            stop=entry - stop_points,
            target=entry + target_points,
            best_price=entry,
        )

    def update(self, symbol: str, ltp: float, trailing_factor: float) -> dict[str, str] | None:
        position = self.positions.get(symbol)
        if not position:
            return None

        if ltp > position.best_price:
            position.best_price = ltp
            # Aggressive trailing: lock part of gains quickly.
            locked = (position.best_price - position.entry) * 0.65 * trailing_factor
            position.stop = max(position.stop, position.entry + locked)
            if position.best_price - position.entry > 5:
                position.target = position.best_price + 1.5

        if ltp <= position.stop:
            self.positions.pop(symbol, None)
            return {"action": "EXIT", "reason": "Trailing stop hit"}

        if ltp >= position.target:
            position.stop = max(position.stop, ltp - 1.2)
            position.target = ltp + 1.8
            return {"action": "HOLD", "reason": "Adaptive target extension"}

        return None
