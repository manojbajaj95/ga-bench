import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


def _replace_now_tags(text: str, base_time: datetime) -> str:
    """Replaces {{NOW}}, {{NOW+1d}}, {{NOW-2h}}, etc. with ISO 8601 strings."""
    pattern = re.compile(r"\{\{NOW(?:([+-]\d+)([dhm]))?\}\}")

    def replacer(match: re.Match) -> str:
        amount_str = match.group(1)
        unit = match.group(2)

        target_time = base_time
        if amount_str and unit:
            amount = int(amount_str)
            if unit == "d":
                target_time += timedelta(days=amount)
            elif unit == "h":
                target_time += timedelta(hours=amount)
            elif unit == "m":
                target_time += timedelta(minutes=amount)

        return target_time.isoformat()

    return pattern.sub(replacer, text)


def _process_node(node: Any, base_time: datetime) -> Any:
    """Recursively processes lists and dicts to replace datetime tags."""
    if isinstance(node, dict):
        return {k: _process_node(v, base_time) for k, v in node.items()}
    elif isinstance(node, list):
        return [_process_node(item, base_time) for item in node]
    elif isinstance(node, str):
        return _replace_now_tags(node, base_time)
    else:
        return node


def load_seed_data(app_name: str) -> dict:
    """
    Loads seed data from worlds/data/seed_data.json for a given app.
    Replaces {{NOW}}, {{NOW+1d}}, etc. with ISO formatted strings.
    """
    data_file = Path(__file__).parent / "data" / "seed_data.json"

    with open(data_file, encoding="utf-8") as f:
        all_data = json.load(f)

    app_data = all_data[app_name]
    base_time = datetime.now()

    return _process_node(app_data, base_time)
