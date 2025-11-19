from pathlib import Path
import sys

def ensure_project_root():
    """どの場所から実行しても 'src' が import できるようにする"""
    root = Path(__file__).resolve().parents[2]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return root

def data_dir() -> Path:
    return ensure_project_root() / "data" / "menu_planner"

def assets_dir() -> Path:
    return ensure_project_root() / "assets" / "menu_planner"
