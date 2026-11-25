# import time
# from pathlib import Path
# from watchdog.events import FileSystemEvent, FileSystemEventHandler
# from watchdog.observers import Observer

# TEMP_EXTENSIONS = (".crdownload", ".part", ".tmp", ".download")


# class MyEventHandler(FileSystemEventHandler):
#     def on_created(self, event: FileSystemEvent) -> None:
#         if event.is_directory:
#             return
#         file_path = event.src_path
#         if not file_path.lower().endswith(TEMP_EXTENSIONS):
#             print(f"[File Baru] {file_path}")

#     def on_moved(self, event: FileSystemEvent) -> None:
#         if event.is_directory:
#             return
#         file_path = event.dest_path
#         if not file_path.lower().endswith(TEMP_EXTENSIONS):
#             print(f"[Download Selesai] {file_path}")


# download_folder = str(Path.home() / "Downloads")
# observer = Observer()
# observer.schedule(MyEventHandler(), download_folder, recursive=False)

# print(f"Memantau folder: {download_folder}...")
# observer.start()

# try:
#     while True:
#         time.sleep(1)
# except KeyboardInterrupt:
#     observer.stop()
# observer.join()

import time
from pathlib import Path
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

TEMP_EXTENSIONS = (".crdownload", ".part", ".tmp", ".download")


class MyEventHandler(FileSystemEventHandler):
    def __init__(self) -> None:
        super().__init__()
        self.file_diproses = set()  # poin 5: file yang sudah terdeteksi selesai
        self.diabaikan = set()      # poin 6: file yang sedang diurus aplikasi sendiri

    def abaikan(self, file_path: str) -> None:
        # nanti dipanggil sebelum aplikasi memindah / menghapus file
        self.diabaikan.add(file_path)

    def on_moved(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        src = event.src_path
        dest = event.dest_path

        # poin 6: event ini akibat aksi aplikasi sendiri, abaikan
        if src in self.diabaikan or dest in self.diabaikan:
            self.diabaikan.discard(src)
            self.diabaikan.discard(dest)
            return

        # poin 4: selesai = dari file sementara menjadi nama akhir
        if src.lower().endswith(TEMP_EXTENSIONS) and not dest.lower().endswith(TEMP_EXTENSIONS):
            # poin 5: jangan proses file yang sama dua kali
            if dest in self.file_diproses:
                return
            self.file_diproses.add(dest)
            print(f"[Download Selesai] {dest}")

        # poin 7: file yang sedang dipantau di-rename / dipindah pengguna
        elif src in self.file_diproses:
            self.file_diproses.remove(src)
            print(f"[File Hilang] {src}")

    def on_deleted(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        file_path = event.src_path

        # poin 6: dihapus oleh aplikasi sendiri, abaikan
        if file_path in self.diabaikan:
            self.diabaikan.discard(file_path)
            return

        # poin 7: file yang sedang dipantau dihapus pengguna
        if file_path in self.file_diproses:
            self.file_diproses.remove(file_path)
            print(f"[File Hilang] {file_path}")


download_folder = str(Path.home() / "Downloads")
observer = Observer()
observer.schedule(MyEventHandler(), download_folder, recursive=False)

print(f"Memantau folder: {download_folder}...")
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
