# CTFd Backup Tool

## Introduction
CTFd Backup Tool is a Python script for backing up data from CTFd (Capture The Flag platform) instances. This tool helps users to create backups of challenges, teams, users, scoreboard, and an overview file for easy writeup creation. It allows you to maintain a local copy of your CTFd data for offline usage or disaster recovery.

## Features
- Backup challenges, teams, users, scoreboard, and an overview file.
- **🚀 Incremental backup support** - Skip unchanged files to save time and bandwidth
- **📊 Real-time progress bars** - Visual download progress for files and overall backup progress
- Organize challenges by category in the overview file for easy writeup creation.
- Retrieve data from CTFd instances via API.
- Save challenges including descriptions and files.
- Download files associated with challenges.
- **� Backup statistics and progress tracking**
- User-friendly command-line interface.

## Installation
1. Clone this repository:

    ```bash
    git clone https://github.com/mlgzackfly/CTFd-Backup-Tool.git
    ```

2. Navigate to the cloned directory:

    ```bash
    cd ctfd-backup-tool
    ```

3. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Usage
1. Navigate to the directory where the script is located.
2. Run the script using Python with the new parameterized interface:

    **Basic Usage:**
    ```bash
    python ctfbackup.py --url <url> --username <username> --password <password>
    ```

    **Using Short Options:**
    ```bash
    python ctfbackup.py -u <url> -n <username> -p <password>
    ```

    **Incremental Backup:**
    ```bash
    python ctfbackup.py -u <url> -n <username> -p <password> --incremental
    # or
    python ctfbackup.py -u <url> -n <username> -p <password> -i
    ```

    **Force Full Backup:**
    ```bash
    python ctfbackup.py -u <url> -n <username> -p <password> --force-full
    # or
    python ctfbackup.py -u <url> -n <username> -p <password> -f
    ```

    **Custom Output Directory:**
    ```bash
    python ctfbackup.py -u <url> -n <username> -p <password> --output-dir /path/to/backup
    ```

    **Quiet Mode (for scripts):**
    ```bash
    python ctfbackup.py -u <url> -n <username> -p <password> --quiet -i
    ```

    **Disable Progress Bars:**
    ```bash
    python ctfbackup.py -u <url> -n <username> -p <password> --no-progress
    ```

3. The script will start backing up your CTFd instance. Once completed, you will find the backups in the directory named after your CTFd instance.

### Command Line Options
- `--url`, `-u`: CTFd instance URL (required)
- `--username`, `--user`, `-n`: CTFd username (required)
- `--password`, `-p`: CTFd password (required)
- `--incremental`, `-i`: Enable incremental backup mode
- `--force-full`, `-f`: Force full backup (ignore metadata)
- `--output-dir`, `-o`: Custom output directory
- `--no-progress`: Disable progress bars
- `--quiet`, `-q`: Suppress non-essential output
- `--verbose`, `-v`: Enable verbose output for debugging
- `--help`, `-h`: Show help message and exit

### Incremental Backup
The tool tracks file metadata in `.backup_metadata.json` to determine which files have changed. This significantly reduces backup time for subsequent runs by:
- Comparing file sizes and modification times
- Calculating SHA256 hashes to detect content changes
- Skipping files that haven't changed since the last backup

### Progress Tracking
The tool now includes comprehensive progress tracking:
- **Real-time file download progress** with speed and ETA indicators
- **Overall backup progress** showing current challenge being processed
- **Visual progress bars** for teams and users backup with pagination support
- **Detailed statistics** at the end showing efficiency metrics

## Example
**First time backup (full):**
```bash
python ctfbackup.py --url demo.ctfd.com --username admin --password secret123
# or using short options
python ctfbackup.py -u demo.ctfd.com -n admin -p secret123
```

**Subsequent backups (incremental):**
```bash
python ctfbackup.py -u demo.ctfd.com -n admin -p secret123 --incremental
# or
python ctfbackup.py -u demo.ctfd.com -n admin -p secret123 -i
```

**Automated script with quiet mode:**
```bash
python ctfbackup.py -u demo.ctfd.com -n admin -p secret123 -i --quiet
```

**Custom output directory:**
```bash
python ctfbackup.py -u demo.ctfd.com -n admin -p secret123 --output-dir ./my-ctf-backup
```

**Output example:**
```
🔄 Running incremental backup...
🔍 Processing challenges...
📚 Challenges: 100%|████████████| 25/25 [00:30<00:00,  1.2challenge/s]
📥 challenge.zip: 100%|████████| 2.5MB/2.5MB [00:02<00:00, 1.2MB/s]
- ✔ Web Challenge 1
    ⬇️ Downloaded file: challenge.zip
📚 Processing: Crypto Challenge 1...
- ✔ Crypto Challenge 1  
    ⏭️ Skipped file: crypto.py (unchanged)
    ✅ Updated file: solution.txt
👥 Teams: 100%|████████████████| 5/5 [00:05<00:00,  1.0page/s]
👤 Users: 100%|████████████████| 10/10 [00:08<00:00,  1.2page/s]

==================================================
📊 BACKUP STATISTICS
==================================================
🔄 Mode: Incremental Backup
📁 Total files: 25
⬇️ Downloaded: 3
✅ Updated: 2
⏭️ Skipped: 20
💾 Efficiency: 80.0% files skipped
==================================================
```

![usage](image/usage.png)
