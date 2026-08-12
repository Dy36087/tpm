#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="$REPO_DIR/backups"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
TAG_NAME="backup-$TIMESTAMP"

mkdir -p "$BACKUP_DIR"

if [ -f "$REPO_DIR/db.sqlite3" ]; then
  cp "$REPO_DIR/db.sqlite3" "$BACKUP_DIR/db.sqlite3.$TIMESTAMP"
  echo "Banco copiado para $BACKUP_DIR/db.sqlite3.$TIMESTAMP"
else
  echo "Arquivo db.sqlite3 não encontrado em $REPO_DIR"
fi

git -C "$REPO_DIR" add .
if git -C "$REPO_DIR" diff --cached --quiet; then
  echo "Nenhuma alteração para commit."
else
  git -C "$REPO_DIR" commit -m "Backup do projeto PTM $TIMESTAMP"
fi

git -C "$REPO_DIR" tag -a "$TAG_NAME" -m "Backup PTM $TIMESTAMP"

git -C "$REPO_DIR" push origin main

git -C "$REPO_DIR" push origin "$TAG_NAME"

echo "Backup concluído. Tag criada: $TAG_NAME"
