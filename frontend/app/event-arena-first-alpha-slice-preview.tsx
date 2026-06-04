// MEGA_RELEASE_ACCELERATION_19_EVENT_ARENA_FIRST_ALPHA_AND_FIRST_SESSION_ONBOARDING_SUPER_PACK_v70
// TRACK B - Event/Arena First Alpha Slice Preview (DEEPLINK-ONLY)
//
// Guardrail:
//   - deeplink-only, no public menu routing
//   - no backend fetch, no api story battle, no api battle simulate
//   - no import da story.tsx o combat.tsx
//   - no battle_engine
//   - no reward grant, no event currency, no arena ranking, no MMR
//   - no leaderboard writes, no matchmaking live
//   - no Reanimated, no AsyncStorage
//   - db_writes=0
//
// UI in italiano. TypeScript-only.

import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";

type ModeId = "event" | "arena";

type AlphaSlice = {
  mode: ModeId;
  title: string;
  subtitle: string;
  steps: string[];
  resultLabel: string;
};

const EVENT_SLICE: AlphaSlice = {
  mode: "event",
  title: "Event First Alpha Slice (preview)",
  subtitle: "event_id: event_alpha_test_001 - tema: trial_of_dawn_preview",
  steps: [
    "Spawn ondata 1 (preview)",
    "Skill alleato base (preview)",
    "Attacco coordinato evento (preview)",
    "Spawn ondata 2 (preview)",
    "Burst combo team (preview)",
    "Clear ondata finale (preview)",
    "Esito evento preview (non autoritativo)",
  ],
  resultLabel: "event_clear_preview",
};

const ARENA_SLICE: AlphaSlice = {
  mode: "arena",
  title: "Arena First Alpha Slice (preview)",
  subtitle: "arena_match_id: arena_alpha_bot_001 - opponent: bot_preview, bracket: unranked_alpha",
  steps: [
    "Match preview vs bot (preview)",
    "Skill alleato base (preview)",
    "Counter del bot (preview)",
    "Burst combo team (preview)",
    "Skill ultimate (preview)",
    "Esito match preview (non autoritativo, no ranking)",
  ],
  resultLabel: "arena_bot_match_preview",
};

const GUARDRAILS = {
  result_authoritative: false,
  db_writes: 0,
  battle_engine_runtime_used: false,
  reward_grant_enabled: false,
  event_currency_enabled: false,
  arena_ranking_enabled: false,
};

function SliceCard({
  slice,
}: {
  slice: AlphaSlice;
}) {
  const [stepIndex, setStepIndex] = useState<number>(0);
  const [complete, setComplete] = useState<boolean>(false);
  const [autoplay, setAutoplay] = useState<boolean>(false);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const lastStep: boolean = stepIndex >= slice.steps.length - 1;

  const stopAutoplay = useCallback(() => {
    if (timerRef.current !== null) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    setAutoplay(false);
  }, []);

  const goNext = useCallback(() => {
    if (complete) return;
    if (!lastStep) {
      setStepIndex((s: number) => s + 1);
    } else {
      setComplete(true);
      stopAutoplay();
    }
  }, [complete, lastStep, stopAutoplay]);

  const goPrev = useCallback(() => {
    if (stepIndex > 0) {
      setStepIndex((s: number) => s - 1);
      setComplete(false);
    }
  }, [stepIndex]);

  const reset = useCallback(() => {
    setStepIndex(0);
    setComplete(false);
    stopAutoplay();
  }, [stopAutoplay]);

  const togglePlay = useCallback(() => {
    if (autoplay) stopAutoplay();
    else setAutoplay(true);
  }, [autoplay, stopAutoplay]);

  useEffect(() => {
    if (!autoplay || complete) {
      if (timerRef.current !== null) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
      return;
    }
    timerRef.current = setInterval(() => goNext(), 900);
    return () => {
      if (timerRef.current !== null) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    };
  }, [autoplay, complete, goNext]);

  useEffect(() => {
    return () => {
      if (timerRef.current !== null) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    };
  }, []);

  const progressPct: number = useMemo<number>(() => {
    const done: number = stepIndex + (complete ? 1 : 0);
    return Math.min(100, Math.round((done / slice.steps.length) * 100));
  }, [stepIndex, complete, slice.steps.length]);

  return (
    <View style={styles.card}>
      <Text style={styles.cardTitle}>{slice.title}</Text>
      <Text style={styles.cardSub}>{slice.subtitle}</Text>
      <Text style={styles.progressLabel}>Avanzamento preview: {progressPct}%</Text>
      <View style={styles.progressBarBg}>
        <View style={[styles.progressBarFill, { width: `${progressPct}%` }]} />
      </View>

      <View style={styles.stepsBlock}>
        {slice.steps.map((label: string, i: number) => {
          const reached: boolean = i <= stepIndex;
          return (
            <View key={`${slice.mode}-${i}`} style={styles.stepRow}>
              <View style={[styles.stepDot, reached ? styles.stepDotOn : styles.stepDotOff]} />
              <Text style={[styles.stepText, reached ? styles.stepTextOn : styles.stepTextOff]}>
                {i + 1}. {label}
              </Text>
            </View>
          );
        })}
      </View>

      {complete ? (
        <View style={styles.resultBlock}>
          <Text style={styles.resultTitle}>Risultato {slice.mode.toUpperCase()} (PREVIEW)</Text>
          <Text style={styles.resultLine}>outcome_preview: {slice.resultLabel}</Text>
          <Text style={styles.resultLine}>result_authoritative: false</Text>
          <Text style={styles.disabledLine}>Reward: DISABILITATA (preview)</Text>
          {slice.mode === "event" ? (
            <Text style={styles.disabledLine}>Event Currency: DISABILITATA (preview)</Text>
          ) : (
            <Text style={styles.disabledLine}>Ranking / MMR: DISABILITATI (preview)</Text>
          )}
        </View>
      ) : null}

      <View style={styles.controls}>
        <TouchableOpacity style={[styles.btn, styles.btnSecondary]} onPress={goPrev} disabled={stepIndex === 0}>
          <Text style={styles.btnText}>Indietro</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.btn, styles.btnPrimary]} onPress={goNext}>
          <Text style={styles.btnText}>{complete ? "Slice completato" : "Step successivo"}</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.btn, styles.btnTertiary]} onPress={togglePlay}>
          <Text style={styles.btnText}>{autoplay ? "Pausa" : "Play"}</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.btn, styles.btnTertiary]} onPress={reset}>
          <Text style={styles.btnText}>Reset</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

export default function EventArenaFirstAlphaSlicePreviewScreen() {
  const [mode, setMode] = useState<ModeId>("event");
  const slice: AlphaSlice = mode === "event" ? EVENT_SLICE : ARENA_SLICE;

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.scroll}>
        <View style={styles.banner}>
          <Text style={styles.bannerText}>EVENT + ARENA FIRST ALPHA SLICE (DEEPLINK-ONLY)</Text>
          <Text style={styles.bannerSub}>
            Anteprima locale non autoritativa - nessun reward, nessun ranking, nessuna currency
          </Text>
        </View>

        <View style={styles.switchRow}>
          <TouchableOpacity
            style={[styles.switchBtn, mode === "event" ? styles.switchOn : styles.switchOff]}
            onPress={() => setMode("event")}
          >
            <Text style={styles.switchText}>Event</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.switchBtn, mode === "arena" ? styles.switchOn : styles.switchOff]}
            onPress={() => setMode("arena")}
          >
            <Text style={styles.switchText}>Arena (bot, unranked)</Text>
          </TouchableOpacity>
        </View>

        <SliceCard slice={slice} />

        <View style={styles.guardrailBlock}>
          <Text style={styles.guardrailTitle}>Guardrail preview</Text>
          <Text style={styles.guardrailLine}>
            result_authoritative: {String(GUARDRAILS.result_authoritative)}
          </Text>
          <Text style={styles.guardrailLine}>db_writes: {GUARDRAILS.db_writes}</Text>
          <Text style={styles.guardrailLine}>
            battle_engine_runtime_used: {String(GUARDRAILS.battle_engine_runtime_used)}
          </Text>
          <Text style={styles.guardrailLine}>
            reward_grant_enabled: {String(GUARDRAILS.reward_grant_enabled)}
          </Text>
          <Text style={styles.guardrailLine}>
            event_currency_enabled: {String(GUARDRAILS.event_currency_enabled)}
          </Text>
          <Text style={styles.guardrailLine}>
            arena_ranking_enabled: {String(GUARDRAILS.arena_ranking_enabled)}
          </Text>
        </View>

        <View style={styles.footer}>
          <Text style={styles.footerText}>
            Pack: MEGA_RELEASE_ACCELERATION_19_v70 - Event/Arena First Alpha Slice
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: "#0b0b13" },
  scroll: { padding: 16, paddingBottom: 48 },
  banner: {
    backgroundColor: "#1a1a2e",
    borderColor: "#ffaa00",
    borderWidth: 1,
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
  },
  bannerText: { color: "#ffaa00", fontWeight: "bold", fontSize: 13 },
  bannerSub: { color: "#c0c0c0", fontSize: 11, marginTop: 4 },
  switchRow: { flexDirection: "row", gap: 8, marginBottom: 12 },
  switchBtn: { flex: 1, paddingVertical: 10, borderRadius: 6, alignItems: "center", minHeight: 44 },
  switchOn: { backgroundColor: "#ffaa00" },
  switchOff: { backgroundColor: "#22223a", borderColor: "#3a3a5e", borderWidth: 1 },
  switchText: { color: "#0b0b13", fontWeight: "bold", fontSize: 12 },
  card: {
    backgroundColor: "#15151f",
    padding: 14,
    borderRadius: 8,
    borderColor: "#2a2a3e",
    borderWidth: 1,
    marginBottom: 16,
  },
  cardTitle: { color: "#fff", fontSize: 16, fontWeight: "bold" },
  cardSub: { color: "#a0a0a0", fontSize: 11, marginTop: 2, marginBottom: 8 },
  progressLabel: { color: "#fff", fontSize: 12, marginTop: 8 },
  progressBarBg: {
    backgroundColor: "#222234",
    height: 8,
    borderRadius: 4,
    overflow: "hidden",
    marginTop: 4,
  },
  progressBarFill: { backgroundColor: "#ffaa00", height: 8 },
  stepsBlock: { marginVertical: 8 },
  stepRow: { flexDirection: "row", alignItems: "center", marginVertical: 3 },
  stepDot: { width: 10, height: 10, borderRadius: 5, marginRight: 8 },
  stepDotOn: { backgroundColor: "#ffaa00" },
  stepDotOff: { backgroundColor: "#444455" },
  stepText: { fontSize: 13, flexShrink: 1 },
  stepTextOn: { color: "#fff" },
  stepTextOff: { color: "#777788" },
  resultBlock: {
    backgroundColor: "#0f0f18",
    padding: 12,
    borderRadius: 6,
    borderColor: "#ffaa00",
    borderWidth: 1,
    marginVertical: 8,
  },
  resultTitle: { color: "#ffaa00", fontSize: 14, fontWeight: "bold", marginBottom: 4 },
  resultLine: { color: "#fff", fontSize: 12, marginTop: 2 },
  disabledLine: { color: "#cccc66", fontSize: 12, marginTop: 4 },
  controls: { flexDirection: "row", flexWrap: "wrap", gap: 8, marginTop: 8 },
  btn: { paddingHorizontal: 12, paddingVertical: 10, borderRadius: 6, minHeight: 44 },
  btnPrimary: { backgroundColor: "#ffaa00" },
  btnSecondary: { backgroundColor: "#3a3a5e" },
  btnTertiary: { backgroundColor: "#22223a", borderColor: "#3a3a5e", borderWidth: 1 },
  btnText: { color: "#0b0b13", fontWeight: "bold", fontSize: 12, textAlign: "center" },
  guardrailBlock: {
    backgroundColor: "#0f0f18",
    padding: 12,
    borderRadius: 8,
    borderColor: "#2a2a3e",
    borderWidth: 1,
    marginTop: 8,
    marginBottom: 16,
  },
  guardrailTitle: { color: "#ffaa00", fontSize: 13, fontWeight: "bold", marginBottom: 6 },
  guardrailLine: { color: "#c0c0c0", fontSize: 11, marginTop: 2 },
  footer: { alignItems: "center", marginTop: 8 },
  footerText: { color: "#666677", fontSize: 10 },
});
