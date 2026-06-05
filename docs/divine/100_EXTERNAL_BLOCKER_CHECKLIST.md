# 100 — EXTERNAL BLOCKER CHECKLIST — v100

> Lingua: Italiano.

Questa checklist contiene tutto quello che l'utente deve fare **fuori dal container Emergent** per chiudere i 5 external blockers Closed Alpha.

## 1. Google / Apple credentials

### Env vars richieste
```
GOOGLE_CLIENT_ID_ANDROID
GOOGLE_CLIENT_ID_IOS
GOOGLE_WEB_CLIENT_ID
APPLE_CLIENT_ID
APPLE_TEAM_ID
APPLE_KEY_ID
APPLE_PRIVATE_KEY
```

### Steps
1. Google Cloud Console → APIs & Services → Credentials
2. Create OAuth client Android (package name + SHA-1 release)
3. Create OAuth client iOS (bundle id reale)
4. Create OAuth client Web (per audience check backend)
5. Apple Developer Account → Identifiers → Services IDs
6. Create App ID con Sign in with Apple capability
7. Create Services ID + Key ID + Team ID
8. Generate Private Key (.p8) per identity token validation

### Dev build requirements
- Expo development build (non Expo Go) per provider sign-in nativo
- `app.json` plugin: `@react-native-google-signin/google-signin`
- `app.json` plugin: `expo-apple-authentication`

### Test verifica id_token
1. Login utente da app → ricevi `id_token`
2. Backend chiama JWKS (Google: `https://www.googleapis.com/oauth2/v3/certs` ; Apple: `https://appleid.apple.com/auth/keys`)
3. Validate signature + audience + issuer + exp
4. Reject se invalid (no fallback to client claims)
5. NESSUN raw token log

## 2. Privacy / Terms / Account Deletion URLs

### Pagine richieste
- Privacy Policy (GDPR Art.13/14 compliant)
- Terms of Service
- Account Deletion Instructions (GDPR Art.17 + Google Play / Apple Store requirement)
- Support Contact / Email

### Minimum content
- **Privacy**: data collected, purposes, lawful basis, retention, sharing, user rights, contact DPO
- **Terms**: service description, accounts, prohibited conduct, IP, disclaimers, governing law
- **Account Deletion**: step-by-step how to request, verification, grace period 30gg, hard delete confirmation

### Env vars
```
PRIVACY_POLICY_URL
TERMS_OF_SERVICE_URL
ACCOUNT_DELETION_URL
SUPPORT_CONTACT_URL
SUPPORT_EMAIL
```

- **Staging URL minimum**: `https://staging.<dominio>/privacy` puo bastare per Closed Alpha private testing
- **Live URL required for store**: Production URL su dominio legale obbligatorio per Google Play + Apple Store

### Where to configure
- `backend/.env` → `PRIVACY_POLICY_URL` etc.
- frontend `app.json`/expo extra → URL link nel login + settings

## 3. Physical Mobile QA

### Android (10 voci)
1. Install via Google Play Internal Testing track
2. Cold start <5s
3. Login guest OK + session restore dopo killapp
4. Logout pulisce sessione
5. 15 game modes navigation
6. Combat scene rendering + tap targets >=44dp
7. Live hub + bot status panel + chat preview + announcements
8. Safe area su notch/foldable
9. Crash test (kill+restart, low-mem, airplane mode)
10. Screenshot + adb logcat richiesti come proof

### iOS (12 voci)
1. Install via Apple TestFlight
2. Sign in with Apple button visibility (App Store requirement)
3. Bundle id reale + provisioning profile
4. Cold start <5s
5. Login guest + Apple
6. Session restore dopo background
7. Logout pulisce KeyChain
8. 15 modes idem Android
9. Combat scene + tap targets >=44pt
10. Safe area + Dynamic Island handling
11. Crash test (kill+restart, low-mem, airplane mode)
12. Screenshot + Xcode console logs richiesti come proof

### Pass/Fail criteria
- Cold start <5s = PASS
- 15 modes navigation senza crash = PASS
- Combat scene render senza freeze/crash = PASS
- Session restore corretto = PASS
- Tap targets >=44dp/44pt = PASS
- Crash test recovery senza data loss = PASS

### Deliverables
- matrix device coverage (almeno 3 Android + 2 iOS)
- screenshots per ogni mode
- crash logs (se presenti)
- performance metrics (cold start ms, scene transition ms)

## 4. Full Locust / Load >=1000

### External environment requirements
- staging cluster dedicato con DB MongoDB isolato
- Redis disponibile
- almeno 4 vCPU + 8GB RAM per locust master + workers
- isolato dalla produzione (no shared DB)

### Locust command
```
locust -f backend/scripts/locust_v99_closed_alpha_full.py \
  --host https://staging.<dominio> \
  --headless -u 1000 -r 50 -t 30m \
  --html /tmp/v100_load.html
```

### Targets
- p95 < 250 ms
- p99 < 500 ms
- error rate < 1%
- DB write safety: solo collezione `users` (auth/account), NESSUNA economy/inventory/reward

## 5. Store Internal Testing

### Google Play Internal Track
1. Create Play Console app entry
2. Bundle id definitivo (`com.<azienda>.<gioco>`)
3. Sign release AAB con keystore release
4. Upload to Internal Testing track
5. Compile Data Safety form
6. Compile Content Rating questionnaire
7. Add internal testers

### Apple TestFlight
1. Create App Store Connect app entry
2. Bundle id definitivo + provisioning profile
3. Build via Xcode/EAS con cert distribution
4. Upload to TestFlight
5. Compile App Privacy questionnaire
6. Compile Age Rating
7. Add internal testers

### Required signing credentials
- **Android**: keystore release (.jks) + storePassword + keyAlias + keyPassword
- **iOS**: AppStore Connect API key (.p8) + Distribution Certificate + Provisioning Profile

### Data Safety
- Google Play Data Safety: collected data minimum (account id + provider id only)
- Apple Privacy questionnaire: 'Data Not Linked to You' per analytics, 'Account' per auth

### App access instructions
- Includere test account login con guest mode (no real credentials)
- Fornire revisori Apple un demo account per Sign in with Apple

## Safety

```
fake_credentials               = false
fake_mobile_qa                 = false
fake_load_result               = false
fake_store_readiness           = false
commercial_release_claim       = false
```
