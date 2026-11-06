from dataclasses import dataclass
from typing import List, Optional

def round_to_tick(price: float, tick_size: float = 0.05) -> float:
    return round(round(price / tick_size) * tick_size, 2)

@dataclass
class Candle:
    timestamp: str
    open: float
    high: float
    low: float
    close: float

@dataclass
class TrailingState:
    symbol: str
    direction: str
    entry_price: float
    current_stop: float
    highest_price_seen: float
    atr: float
    stopped_out: bool = False
    exit_price: Optional[float] = None

class ChandelierTrailingEngine:
    def __init__(self, period: int = 14, multiplier: float = 2.5):
        self.period = period
        self.multiplier = multiplier

    def init_trade(self, symbol: str, direction: str, entry_price: float, initial_candles: List[Candle]) -> TrailingState:
        recent = initial_candles[-self.period:]
        highest_high = max(c.high for c in recent)
        tr_list = [c.high - c.low for c in initial_candles]
        atr = sum(tr_list[-self.period:]) / self.period
        raw_stop = highest_high - (self.multiplier * atr)
        stop = min(raw_stop, entry_price - (1.5 * atr))
        return TrailingState(symbol=symbol, direction=direction.upper(), entry_price=entry_price, current_stop=round_to_tick(stop), highest_price_seen=highest_high, atr=atr)
