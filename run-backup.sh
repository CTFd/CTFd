#!/bin/bash
set -euo pipefail

# --- Config ---
PROJECT_DIR="/Users/jij/ctfd-backup"
DOCKER="/opt/homebrew/bin/docker"

LOGFILE="$PROJECT_DIR/backup.log"

cd "$PROJECT_DIR"

echo "=== Backup started: $(date) ===" >> "$LOGFILE"

$DOCKER compose up --abort-on-container-exit >> "$LOGFILE" 2>&1

echo "=== Backup finished: $(date) ===" >> "$LOGFILE"
