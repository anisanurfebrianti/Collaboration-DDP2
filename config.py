from pathlib import Path
from datetime import timedelta

DOWNLOADS_DIR = Path.home() / "Downloads"
DATA_FILE = Path(__file__).parent / "jadwal.json"
TEMP_EXTENSIONS = {".crdownload", ".part", ".tmp", ".download"}
IGNORED_NAMES = {"desktop.ini"}
IGNORED_PREFIXES = ("~$",)
IGNORE_HIDDEN_FILES = True
STABLE_SECONDS = 2
DURATIONS = {
    "1 Hari": timedelta(days=1),
    "1 Minggu": timedelta(weeks=1),
    "1 Bulan": timedelta(days=30),
    "1 Tahun": timedelta(days=365),
}
REMIND_AGAIN_MINUTES = 60
CHECK_INTERVAL_SEC = 30
MAX_RETRY = 3
DEMO_MODE = False

if DEMO_MODE:
    DURATIONS["15 Detik (Demo)"] = timedelta(seconds=15)
    CHECK_INTERVAL_SEC = 2