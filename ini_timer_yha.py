import json
import os
import threading
import time
from datetime import datetime

DURATION_PRESETS = {
    "1 Hari": 1 * 86400,
    "3 Hari": 3 * 86400,
    "7 Hari": 7 * 86400,
    "2 Minggu": 14 * 86400,
    "1 Bulan": 30 * 86400,
}

class TimerManager:
    def __init__(self, on_expire_callback, schedule_file="schedules.json", check_interval=3):
        self.on_expire = on_expire_callback
        self.schedule_file = schedule_file
        self.check_interval = check_interval
        self.running = False
        self.lock = threading.Lock()
        self._thread = None

        self._ensure_schedule_file()

    def _ensure_schedule_file(self):
        if not os.path.exists(self.schedule_file):
            self._save_data({})
            return

        try:
            with open(self.schedule_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    self._save_data({})
        except (json.JSONDecodeError, OSError):
            self._save_data({})

    def _load_data(self):
        try:
            with open(self.schedule_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _save_data(self, data):
        with open(self.schedule_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def add_file(self, file_path, duration_seconds, label="Custom"):
        """Tambahkan atau perbarui jadwal kedaluwarsa file berdasarkan satuan detik."""
        normalized_path = os.path.abspath(file_path)
        now = time.time()
        expires_at = now + duration_seconds

        with self.lock:
            data = self._load_data()
            data[normalized_path] = {
                "file_name": os.path.basename(normalized_path),
                "duration_label": label,
                "duration_seconds": duration_seconds,
                "added_at": now,
                "expires_at": expires_at,
                "expires_readable": datetime.fromtimestamp(expires_at).strftime("%Y-%m-%d %H:%M:%S")
            }
            self._save_data(data)

        print(f"[TimerManager] '{os.path.basename(normalized_path)}' dijadwalkan ({label}) -> habis pada {data[normalized_path]['expires_readable']}")

    def add_file_by_preset(self, file_path, preset_name):
        if preset_name not in DURATION_PRESETS:
            raise ValueError(f"Preset '{preset_name}' tidak dikenal. Pilihan: {list(DURATION_PRESETS.keys())}")

        seconds = DURATION_PRESETS[preset_name]
        self.add_file(file_path, duration_seconds=seconds, label=preset_name)

    def add_file_by_days(self, file_path, days):
        seconds = days * 86400
        self.add_file(file_path, duration_seconds=seconds, label=f"{days} Hari")

    def extend_time_by_preset(self, file_path, preset_name):
        if preset_name not in DURATION_PRESETS:
            raise ValueError(f"Preset '{preset_name}' tidak dikenal.")

        extra_seconds = DURATION_PRESETS[preset_name]
        normalized_path = os.path.abspath(file_path)
        now = time.time()

        with self.lock:
            data = self._load_data()
            if normalized_path in data:
                base_time = max(now, data[normalized_path]["expires_at"])
                new_expires = base_time + extra_seconds
                data[normalized_path]["expires_at"] = new_expires
                data[normalized_path]["expires_readable"] = datetime.fromtimestamp(new_expires).strftime("%Y-%m-%d %H:%M:%S")
                self._save_data(data)
                print(f"[TimerManager] Diperpanjang +{preset_name}: {os.path.basename(normalized_path)}")
                return True
        return False

    def remove_file(self, file_path):
        normalized_path = os.path.abspath(file_path)
        with self.lock:
            data = self._load_data()
            if normalized_path in data:
                del data[normalized_path]
                self._save_data(data)
                print(f"[TimerManager] Di-keep (dihapus dari antrean): {os.path.basename(normalized_path)}")
                return True
        return False

    def handle_user_choice(self, file_path, choice):
        if choice == "Hapus":
            self.remove_file(file_path)
            self.on_expire(file_path)
        elif choice == "Keep":
            self.remove_file(file_path)
        else:
            self.add_file_by_preset(file_path, choice)

    def get_active_schedules(self):
        with self.lock:
            return self._load_data()

    def _check_loop(self):
        while self.running:
            now = time.time()
            expired_paths = []
            missing_paths = []

            with self.lock:
                data = self._load_data()
                for file_path, info in list(data.items()):
                    if not os.path.exists(file_path):
                        missing_paths.append(file_path)
                        del data[file_path]
                        continue

                    if now >= info["expires_at"]:
                        expired_paths.append(file_path)
                        del data[file_path]

                if expired_paths or missing_paths:
                    self._save_data(data)

            for path in missing_paths:
                print(f"[TimerManager] Dilewati (file sudah hilang/dipindah manual): {os.path.basename(path)}")

            for path in expired_paths:
                try:
                    self.on_expire(path)
                except Exception as e:
                    print(f"[TimerManager] Gagal mengeksekusi callback untuk {path}: {e}")

            time.sleep(self.check_interval)

    def start(self):
        if not self.running:
            self.running = True
            self._thread = threading.Thread(target=self._check_loop, daemon=True)
            self._thread.start()
            print("[TimerManager] Background timer berjalan...")

    def stop(self):
        self.running = False
        if self._thread:
            self._thread.join(timeout=2)
        print("[TimerManager] Background timer dihentikan.")

if __name__ == "__main__":
    os.makedirs("demo_downloads", exist_ok=True)

    files = {
        "1 Hari": "demo_downloads/dokumen_1hari.pdf",
        "3 Hari": "demo_downloads/gambar_3hari.png",
        "7 Hari": "demo_downloads/installer_7hari.exe",
        "2 Minggu": "demo_downloads/arsip_2minggu.zip",
        "1 Bulan": "demo_downloads/materi_1bulan.docx",
        "Test Cepat": "demo_downloads/file_tes_3detik.txt",
    }

    for path in files.values():
        with open(path, "w") as f:
            f.write("dummy data")

    def mock_move_to_trash(path):
        print(f"--> [AKSI HAPUS] Waktu habis! Memindahkan '{os.path.basename(path)}' ke Recycle Bin...")
        if os.path.exists(path):
            os.remove(path)

    tm = TimerManager(on_expire_callback=mock_move_to_trash, schedule_file="demo_schedules.json", check_interval=1)
    tm.start()

    tm.add_file_by_preset(files["1 Hari"], "1 Hari")
    tm.add_file_by_preset(files["3 Hari"], "3 Hari")
    tm.add_file_by_preset(files["7 Hari"], "7 Hari")
    tm.add_file_by_preset(files["2 Minggu"], "2 Minggu")
    tm.add_file_by_preset(files["1 Bulan"], "1 Bulan")

    tm.add_file(files["Test Cepat"], duration_seconds=3, label="Tes 3 Detik")

    time.sleep(5)
    tm.stop()

    for path in files.values():
        if os.path.exists(path):
            os.remove(path)
    if os.path.exists("demo_downloads"):
        os.rmdir("demo_downloads")
    if os.path.exists("demo_schedules.json"):
        os.remove("demo_schedules.json")
