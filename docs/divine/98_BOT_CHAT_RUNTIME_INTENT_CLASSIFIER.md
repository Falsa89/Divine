# 98 — Bot Chat Runtime Intent Classifier

## Pack

`MEGA_RELEASE_ACCELERATION_47_v98`

## Stato

`DESIGN_READY_DRY_RUN_GATED_DEFAULT_OFF`

## Classifier

- Engine: pattern_based_with_keyword_extraction
- Context window: 20 messaggi
- Cooldown per bot: 60s
- Anti-spam: max 12/h
- Repetition avoidance: 5 messaggi
- Personas: casual/hyped/calm_analytical/meme_friendly/newbie_friendly
- **manual_ultimate_advice_forbidden = true**
- **out_of_context_response_forbidden = true**

## Intent categories (12)

direct_question_hero_opinion, direct_question_banner_advice, direct_question_event_strategy, direct_question_team_building, direct_question_guild_war_coordination, small_talk_greeting, small_talk_status, small_talk_farming, frustration_unlucky_pull, frustration_difficult_content, announcement_meta, off_topic_harmless.

## Borea fixture

Input: `"Ho trovato Borea, è un buon personaggio?"`
Output: `"Secondo me sì, come support è fortissima se il team la protegge bene."`

### Vietato

- `"Sono le 8 di sera."` (out-of-context)
- `"Tieni l'ultimate per dopo."` (manual ultimate advice forbidden — Divine ultimates trigger automatically)

## Fixtures runtime: 7/7 PASS

1. borea_question → hero_opinion
2. banner_pull_discussion → banner_advice
3. event_farming_discussion → small_talk_farming
4. guild_war_coordination → direct_question_guild_war
5. generic_hello → small_talk_greeting
6. off_topic_harmless → filtered (no response)
7. spam_throttle → rate limit applied

## Runtime apply

Env `V98_BOTS_DISABLE_CHAT` (default `true` => chat DISABILITATO).

## Verdict

`BOT_CHAT_RUNTIME_INTENT_CLASSIFIER_DESIGN_READY_DRY_RUN_GATED`
