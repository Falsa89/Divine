# Expo Wrapper Recovery (OPS-A)

L'avvio di Metro/Expo per il preview frontend dipende da:

- `/usr/local/bin/start-expo.sh` (wrapper)
- Blocco supervisor `[program:expo]` con `command=/usr/local/bin/start-expo.sh`

Il wrapper a volte scompare dopo reset del container. Quando succede, expo va offline. Recupero rapido:

```bash
# 1) Verifica presenza
ls -la /usr/local/bin/start-expo.sh

# 2) Se assente, ricrea con questo contenuto esatto:
cat > /usr/local/bin/start-expo.sh <<'EOF'
#!/bin/bash
set -e
cd /app/frontend
fuser -k 3000/tcp 2>/dev/null || true
pkill -9 -f "expo start" 2>/dev/null || true
pkill -9 -f "metro" 2>/dev/null || true
sleep 1
export NODE_OPTIONS="--max-old-space-size=4096"
export EXPO_NO_TELEMETRY=1
exec npx expo start --port 3000
EOF
chmod +x /usr/local/bin/start-expo.sh

# 3) Aggiorna supervisor e (ri)avvia
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart expo

# 4) Verifica
sleep 5
sudo supervisorctl status expo
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:3000
```

Note chiave:

- `fuser -k 3000/tcp` libera la porta da processi orfani.
- `pkill -9 -f "expo start"` e `pkill -9 -f "metro"` puliscono PID orfani.
- `exec` su `npx expo start` garantisce che supervisor abbia il PID corretto.
- HMR resta attivo (no `CI=1`).
