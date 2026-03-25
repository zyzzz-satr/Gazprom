from typing import List, Dict
import random

def get_analytics(history: List[Dict]) -> Dict:
    # Simple heuristic analytics derived from history length
    seed = len(history) if history is not None else 0
    random.seed(seed)
    base = max(1, len(history))
    daily_volume = max(1, base * 2 + random.randint(-1, 3))
    avg_handle_time_ms = max(400, 1200 + random.randint(-300, 600))
    conversion_rate = round(min(0.95, max(0.1, 0.4 + random.random() * 0.5)), 2)
    top_clients = [
        {"name": "Клиент А", "amount": 12000},
        {"name": "Клиент Б", "amount": 8500},
        {"name": "Клиент В", "amount": 4900},
    ]
    return {
        "daily_volume": daily_volume,
        "avg_handle_time_ms": avg_handle_time_ms,
        "conversion_rate": conversion_rate,
        "top_clients": top_clients,
    }
