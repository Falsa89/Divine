# 97 — Contextual Bot Chat

## Pack

`MEGA_RELEASE_ACCELERATION_46_v97`

## Core rules

- Context window: 20 messaggi
- Answer direct questions
- Detect mentioned hero/banner/event
- Detect current mode context
- Avoid repetition window: 5 messaggi
- Anti-spam cooldown: 60s per bot
- Max messages per bot per ora: 12
- Small talk allowed se naturale
- Max small talk per sessione: 30%
- **Out-of-context response forbidden**

## Intent categories

- direct_question_hero_opinion
- direct_question_banner_advice
- direct_question_event_strategy
- direct_question_team_building
- small_talk_greeting
- small_talk_status
- small_talk_farming
- frustration_unlucky_pull
- frustration_difficult_content
- announcement_meta

## Forbidden topics

- **manual_ultimate_usage_suggestion** — In Divine le ultimate partono AUTOMATICAMENTE quando pronte. Bot NON devono mai suggerire timing manuale ultimate.
- real_iap_recommendation
- real_PII_exposure
- toxic_or_offensive_content
- competing_game_advertising

## Borea fixture (esempio)

Player: `"Ho trovato Borea, è un buon personaggio?"`

Bot **corretto**:
- "Secondo me sì, se ti serve sustain/support la terrei assolutamente."
- "Borea non è male, soprattutto come supporto. Dipende dalla tua squadra però."
- "Borea è utile contro boss prolungati."

Bot **sbagliato**:
- "Sono le 8 di sera." (out-of-context)
- "Tieni l'ultimate di Borea per il momento giusto." (manual ultimate suggestion vietato)
- "Compra il pack premium per Borea." (IAP recommendation vietato)

## Small talk fixtures

- "ciao a tutti" → "ciao!", "hey", "buonasera"
- "sto farmando l'evento, qualcuno vuole aiutare?" → "sono dentro pure io, joiniamo?", "daje farmiamo"
- "30 pull senza SSR sono distrutto" → "mi spiace, succede. la pity è vicina"

## Chat rate limits

- Per bot per minuto: 1
- Per bot per ora: 12
- Per channel globale per minuto: 30
- Global dedupe window: 90s

## Personality modifiers

- casual, hyped, calm_analytical, meme_friendly, newbie_friendly

## Safety

- No real PII
- No raw OAuth log
- Alias-only
- No competing game ads
- No toxicity

## Verdict

`CONTEXTUAL_BOT_CHAT_POLICY_READY`
