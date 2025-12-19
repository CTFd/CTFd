import re
import requests
import os
import json
import sys
import hashlib
from datetime import datetime
from urllib.parse import urlparse
from termcolor import colored
from tqdm import tqdm
from config import *


# =====================
# DOCKER CONSTANTS
# =====================
BASE_OUTPUT_DIR = os.path.abspath(OUTPUT_DIR or "/data")

if not CTFD_API_TOKEN:
    raise RuntimeError("CTFD_API_TOKEN is not set")

class CTFdBackup:
    def __init__(self, url, incremental=False):
        self.nonce = None
        self.url = self.format_url(url)
        self.incremental = incremental

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Token {CTFD_API_TOKEN}",
            "Content-Type": "application/json"
        })

        if incremental:
            print("WARNING: Incremental backup disabled in timestamped mode")
        self.incremental = False
        
        self.ctf_hostname = self.get_ctf_name()
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.run_dir = os.path.join(BASE_OUTPUT_DIR, self.ctf_hostname, timestamp)
        os.makedirs(self.run_dir, exist_ok=True)


        self.metadata_file = os.path.join(self.run_dir, ".backup_metadata.json")

        self.backup_stats = {
            "files_skipped": 0,
            "files_downloaded": 0,
            "files_updated": 0,
            "total_files": 0,
        }

        self.show_progress = SHOW_PROGRESS
        self.quiet_mode = QUIET_MODE
        self.verbose_mode = VERBOSE_MODE

    def format_url(self, url):
        if not url.startswith(("http://", "https://")):
            return "https://" + url
        return url.rstrip("/")

    def get_ctf_name(self):
        return urlparse(self.url).netloc

    def load_backup_metadata(self):
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_backup_metadata(self, metadata):
        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)

    def get_file_hash(self, path):
        if not os.path.exists(path):
            return None
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()

    def should_download_file(self, file_url, local_path, metadata):
        if not self.incremental:
            return True
        if not os.path.exists(local_path):
            return True
        if file_url not in metadata:
            return True
        return metadata[file_url]["hash"] != self.get_file_hash(local_path)

    def get_data(self, endpoint):
        r = self.session.get(f"{self.url}/api/v1/{endpoint}")
        if r.status_code != 200:
            raise RuntimeError(f"API error {r.status_code}: {r.text}")
        return r.json().get("data", [])

    def download_file(self, url, path, metadata, file_url):
        r = self.session.get(url, stream=True)
        if r.status_code != 200:
            return False

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            for chunk in r.iter_content(8192):
                if chunk:
                    f.write(chunk)

        metadata[file_url] = {
            "hash": self.get_file_hash(path),
            "size": os.path.getsize(path),
            "downloaded_at": datetime.utcnow().isoformat(),
        }
        return True


    def backup_challenges(self):
        challenges = self.get_data("challenges")
        base_dir = os.path.join(self.run_dir, "challenges")
        metadata = self.load_backup_metadata()

        for ch in challenges:
            cid = ch["id"]
            name = ch["name"].replace("/", "-")
            data = self.get_data(f"challenges/{cid}")
            category = data.get("category", "misc").replace("/", "-")

            chal_dir = os.path.join(base_dir, category, name)
            os.makedirs(chal_dir, exist_ok=True)

            with open(os.path.join(chal_dir, f"{name}.md"), "w", encoding="utf-8") as f:
                f.write(f"# {name}\n\n{data.get('description', '')}\n")

            for file_url in data.get("files", []):
                fname = file_url.split("/")[-1].split("?")[0]
                fpath = os.path.join(chal_dir, fname)

                self.backup_stats["total_files"] += 1
                existed_before = os.path.exists(fpath)

                if self.should_download_file(file_url, fpath, metadata):
                    ok = self.download_file(
                        f"{self.url}/{file_url}",
                        fpath,
                        metadata,
                        file_url
                    )
                    if ok:
                        if existed_before:
                            self.backup_stats["files_updated"] += 1
                        else:
                            self.backup_stats["files_downloaded"] += 1
                else:
                    self.backup_stats["files_skipped"] += 1

        self.save_backup_metadata(metadata)


    def backup_simple(self, endpoint, dirname, filename):
        data = self.get_data(endpoint)
        outdir = os.path.join(self.run_dir, dirname)
        os.makedirs(outdir, exist_ok=True)

        with open(os.path.join(outdir, filename), "w") as f:
            json.dump(data, f, indent=4)

    def backup_all(self):
        self.backup_challenges()
        self.backup_simple("users", "users", "users.json")
        self.backup_simple("teams", "teams", "teams.json")
        self.backup_simple("scoreboard", "scoreboard", "scoreboard.json")

    def print_stats(self):
        print(json.dumps(self.backup_stats, indent=2))


def main():
    incremental = INCREMENTAL_BACKUP and not FORCE_FULL_BACKUP

    backup = CTFdBackup(
        url=CTFD_URL,
        incremental=incremental,
    )

    backup.backup_all()
    if not QUIET_MODE:
        backup.print_stats()


if __name__ == "__main__":
    main()
