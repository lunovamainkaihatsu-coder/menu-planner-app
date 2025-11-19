from dataclasses import dataclass
from pathlib import Path
from datetime import date
from typing import Optional
from src.common.fileio import read_json, write_json

@dataclass
class Item:
    name: str
    qty: float
    unit: str
    expires: Optional[str] = None
    photo: Optional[str] = None

def load_pantry(path: Path) -> dict:
    return read_json(path, default={"items":[]})

def save_pantry(path: Path, data: dict):
    write_json(path, data)

def near_expiry_score(expires: Optional[str]) -> float:
    if not expires: return 0.0
    try:
        d = date.fromisoformat(expires)
        diff = (d - date.today()).days
        if diff <= 0: return 2.0
        if diff <= 2: return 1.5
        if diff <= 5: return 1.0
        if diff <= 7: return 0.5
    except Exception:
        pass
    return 0.0
