#!/bin/bash
# AF2-N controlled runtime flip CANARY ROLLBACK script.
#
# Action: removes the AF2-N env vars from /etc/supervisor/conf.d/backend.conf,
# restarts backend, and verifies that gift-spend returns 423 again. The
# canary ledger rows are NOT deleted (they remain as evidence). To clear
# them, run: python3 -c "from pymongo import MongoClient; MongoClient('mongodb://localhost:27017')['divine_waifus']['gift_transaction_ledger'].delete_many({'canary': True})"
#
# This script is idempotent and safe to re-run.
set -eu

CONF=/etc/supervisor/conf.d/backend.conf
BACKUP_DIR=/app/backups
TS=$(date -u +%Y%m%dT%H%M%SZ)

if [ ! -f "$CONF" ]; then
  echo "[AF2-N-RBK] FATAL: $CONF missing"; exit 2
fi

mkdir -p "$BACKUP_DIR"
cp "$CONF" "$BACKUP_DIR/backend.conf.pre-rbk.$TS.bak"
echo "[AF2-N-RBK] backup taken at $BACKUP_DIR/backend.conf.pre-rbk.$TS.bak"

# Strip AF2-N env vars from the `environment=` line. Leaves PYTHONUNBUFFERED="1".
sed -i 's/^environment=.*/environment=PYTHONUNBUFFERED="1"/' "$CONF"
echo "[AF2-N-RBK] AF2-N env vars removed from $CONF"

supervisorctl reread
supervisorctl update
supervisorctl restart backend
sleep 6

# Verify gift-spend is back to 423
CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST \
  http://127.0.0.1:8001/api/affinity/gift-spend \
  -H "Content-Type: application/json" -d '{}')
if [ "$CODE" != "423" ]; then
  echo "[AF2-N-RBK] FATAL: gift-spend returned $CODE (expected 423) after rollback."
  exit 3
fi
echo "[AF2-N-RBK] gift-spend back to 423."

# Verify /api/heroes still 100
COUNT=$(curl -s http://127.0.0.1:8001/api/heroes | python3 -c 'import sys,json; print(len(json.load(sys.stdin)))')
if [ "$COUNT" != "100" ]; then
  echo "[AF2-N-RBK] FATAL: /api/heroes count = $COUNT (expected 100)."
  exit 4
fi
echo "[AF2-N-RBK] /api/heroes count = 100."
echo "[AF2-N-RBK] rollback complete. (Canary ledger rows are NOT removed; see script comment.)"
