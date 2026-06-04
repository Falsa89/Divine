# Test Credentials

> **NOTA HYGIENE — PROJECT_SOUL_FORGE_FORGE_CRASH_API_CONTRACT_AND_SHOP_NAV_FIX Track G:**
> Per policy di sicurezza, le password plaintext NON vengono committate in repo.
> Le credenziali QA reali (se necessarie) vanno richieste al main agent al momento dell'esecuzione, o create via `/api/register` con un'email random e password effimera (rotabile).
>
> Lo username/email QA standard per sessioni Soul Forge \u00e8 documentato qui solo come **placeholder logico**, NON come segreto utilizzabile direttamente.

## Main Test Account (Soul Forge QA — placeholder)
- Email: `sfqa@test.com`
- Password: `<EMPTY \u2014 set at runtime via /api/register; never commit a real password to repo>`
- Username: `sfqa`
- Notes: Se serve un account utilizzabile per QA mobile, il main agent pu\u00f2 ricrearlo on-demand chiamando `POST /api/register` con una password effimera, e annotarla **solo nei propri pensieri / log temporanei**, mai in questo file.

## Auth Test Helper (suggerito)
```bash
# Esempio di setup ephemero \u2014 NON committare l'output
EMAIL="qa_$(date +%s)@test.com"
PASSWORD="$(openssl rand -hex 12)"
curl -s -X POST http://localhost:8001/api/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\",\"username\":\"qa\"}"
# token in JSON output \u2192 da usare solo nella sessione corrente
```

## Storia delle modifiche
- **2026-05-26 (FORGE_CRASH Track G)**: rimossa password plaintext committata in chiaro nel pack precedente. Sostituita con placeholder logico + helper script ephemero.
- **2026-06-04 (v96 AUTH ACCOUNT)**: aggiunti endpoint v96 Google/Apple/Guest. Tutti in sandbox (credentials Google/Apple non presenti), marker `CREDENTIALS_REQUIRED_FOR_STORE_BUILD`.

## v96 Auth Endpoints (sandbox QA)

### Guest QA Login
```bash
curl -X POST http://localhost:8001/api/auth/guest \
  -H "Content-Type: application/json" \
  -d '{"alias_hint":"qa_v96"}'
# → restituisce token JWT (7 giorni) + account
```

### Google Sandbox
```bash
curl -X POST http://localhost:8001/api/auth/google \
  -H "Content-Type: application/json" \
  -d '{"sandbox_subject":"sub_g_qa_001"}'
# → status CREDENTIALS_REQUIRED_FOR_STORE_BUILD (no GOOGLE_CLIENT_ID env)
```

### Apple Sandbox
```bash
curl -X POST http://localhost:8001/api/auth/apple \
  -H "Content-Type: application/json" \
  -d '{"sandbox_subject":"sub_a_qa_001"}'
# → status CREDENTIALS_REQUIRED_FOR_STORE_BUILD (no APPLE_CLIENT_ID env)
```

### Authenticated calls
```bash
TOKEN=<token from above>
curl http://localhost:8001/api/auth/me -H "Authorization: Bearer $TOKEN"
curl http://localhost:8001/api/team/get-formation -H "Authorization: Bearer $TOKEN"
curl -X POST http://localhost:8001/api/auth/logout -H "Authorization: Bearer $TOKEN"
```

