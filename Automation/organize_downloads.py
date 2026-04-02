import os
import shutil
import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ── Configuration ────────────────────────────────────────────────
DOWNLOADS = Path.home() / "Downloads"

EXTENSION_MAP = {
    # Images
    ".jpg": "Images", ".jpeg": "Images", ".png": "Images",
    ".gif": "Images", ".bmp": "Images", ".svg": "Images",
    ".webp": "Images", ".ico": "Images", ".heic": "Images",
    # Videos
    ".mp4": "Videos", ".mkv": "Videos", ".avi": "Videos",
    ".mov": "Videos", ".wmv": "Videos", ".flv": "Videos",
    ".webm": "Videos",
    # Audio
    ".mp3": "Audio", ".wav": "Audio", ".flac": "Audio",
    ".aac": "Audio", ".ogg": "Audio", ".m4a": "Audio",
    # Documents
    ".pdf": "Documents", ".doc": "Documents", ".docx": "Documents",
    ".txt": "Documents", ".xlsx": "Documents", ".xls": "Documents",
    ".pptx": "Documents", ".ppt": "Documents", ".csv": "Documents",
    ".odt": "Documents", ".rtf": "Documents",
    # Software / Installers
    ".exe": "Software", ".msi": "Software", ".dmg": "Software",
    ".deb": "Software", ".rpm": "Software", ".apk": "Software",
    ".pkg": "Software",
    # Archives
    ".zip": "Archives", ".rar": "Archives", ".7z": "Archives",
    ".tar": "Archives", ".gz": "Archives", ".bz2": "Archives",
    ".xz": "Archives",
    # Code
    ".py": "Code", ".js": "Code", ".ts": "Code", ".html": "Code",
    ".css": "Code", ".json": "Code", ".xml": "Code", ".sh": "Code",
    ".bat": "Code", ".cpp": "Code", ".c": "Code", ".java": "Code",
}

# ── Logging setup ─────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(DOWNLOADS / "organizer.log", encoding="utf-8"),
    ],
)
log = logging.getLogger()

# Debugging statements
print("Current Working Directory:", os.getcwd())
file_path = r'C:\Users\Sooraj\Documents\AI Labs\organize_download.py'
if not os.path.isfile(file_path):
    print(f"File does not exist: {file_path}")
else:
    print(f"File exists: {file_path}")

def build_folder_map():
    known = {name.lower(): name for name in set(EXTENSION_MAP.values())}
    known["others"] = "Others"
    folder_map = {}

    for item in DOWNLOADS.iterdir():
        if item.is_dir() and item.name != "__pycache__":
            key = item.name.lower()
            if key in known:
                folder_map[known[key]] = item.name
                log.info(f"[FOUND] Existing folder mapped: {item.name} -> '{known[key]}'")

    return folder_map


def resolve_folder(category: str, folder_map: dict) -> Path:
    if category in folder_map:
        folder_name = folder_map[category]
    else:
        folder_name = category
        folder_map[category] = folder_name
        log.info(f"[NEW] Created folder: {folder_name}/")

    target = DOWNLOADS / folder_name
    target.mkdir(exist_ok=True)
    return target


def move_file(file_path: Path, folder_map: dict):
    if not file_path.is_file():
        return
    if file_path.name == "organizer.log":
        return

    ext = file_path.suffix.lower()
    category = EXTENSION_MAP.get(ext, "Others")
    target_dir = resolve_folder(category, folder_map)

    dest = target_dir / file_path.name

    if dest.exists():
        stem = file_path.stem
        suffix = file_path.suffix
        counter = 1
        while dest.exists():
            dest = target_dir / f"{stem} ({counter}){suffix}"
            counter += 1

    shutil.move(str(file_path), str(dest))
    log.info(f"[MOVED] {file_path.name} -> {target_dir.name}/")


def sort_existing(folder_map: dict):
    files = [f for f in DOWNLOADS.iterdir() if f.is_file() and f.name != "organizer.log"]
    if not files:
        log.info("[SCAN] No loose files found — Downloads root is already clean.")
        return
    log.info(f"[SCAN] Found {len(files)} file(s) to sort...")
    for f in files:
        move_file(f, folder_map)
    log.info("[SCAN] Initial sort complete.")


class DownloadsHandler(FileSystemEventHandler):
    def __init__(self, folder_map):
        self.folder_map = folder_map

    def on_created(self, event):
        if not event.is_directory and event.src_path.startswith(str(DOWNLOADS)):
            move_file(Path(event.src_path), self.folder_map)

    def on_moved(self, event):
        if not event.is_directory and event.dest_path.startswith(str(DOWNLOADS)):
            move_file(Path(event.dest_path), self.folder_map)


if __name__ == "__main__":
    log.info("=" * 50)
    log.info(" Downloads Organizer | GAIA AI")
    log.info("=" * 50)
    log.info(f"[WATCH] Monitoring: {DOWNLOADS}")

    folder_map = build_folder_map()
    sort_existing(folder_map)

    handler = DownloadsHandler(folder_map)
    observer = Observer()
    observer.schedule(handler, str(DOWNLOADS), recursive=False)
    observer.start()
    log.info("[WATCH] Watcher active. Press Ctrl+C to stop.")
    log.info("-" * 50)

    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        log.info("[STOP] Watcher stopped.")
        observer.stop()
        observer.join()
