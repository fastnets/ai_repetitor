import os
import sys
from pathlib import Path

from dotenv import load_dotenv


if getattr(sys, "frozen", False):
    config_dir = Path(sys.executable).resolve().parent
    resource_dir = Path(getattr(sys, "_MEIPASS", config_dir))
else:
    config_dir = Path(__file__).resolve().parents[1]
    resource_dir = config_dir

load_dotenv(config_dir / ".env")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")
ASSETS_DIR = resource_dir / "assets"
