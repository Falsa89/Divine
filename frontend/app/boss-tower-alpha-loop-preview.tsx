// MEGA_RELEASE_ACCELERATION_17_STORY_PLAYABLE_ALPHA_AND_BOSS_TOWER_ALPHA_LOOP_SUPER_PACK_v68
// TRACK D — Boss + Tower Alpha Loop Preview (DEEPLINK-ONLY)
//
// Guardrail di sicurezza (allineati al contratto v1):
//   - deeplink-only: nessun link da home/menu pubblico
//   - nessuna fetch backend, nessun /api/story/battle, nessun /api/battle/simulate
//   - nessun import da frontend/app/story.tsx
//   - nessun import da frontend/app/combat.tsx
//   - nessun uso di battle_engine
//   - nessun pulsante claim/reward
//   - nessun reward grant
//   - nessuna progressione permanente
//   - nessuna mutazione di stato persistente
//   - nessun uso di Reanimated/AsyncStorage
//   - result_authoritative=false
//   - db_writes=0
//   - battle_engine_runtime_used=false
//
// Mostra in-place sia il loop Boss alpha sia il loop Tower alpha con
// timeline 5-7 step deterministica e result preview disabilitata.
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

type ModeId = "boss" | "tower";

type AlphaLoopFixture = {
  mode: ModeId;
  title: string;
  subtitle: string;
  steps: string[];
  resultLabel: string;
};

const BOSS_FIXTURE: AlphaLoopFixture = {
  mode: "boss",
  title: "Boss Alpha Loop (preview)",
  subtitle: "family_alpha_titan_preview - phase_1 -> phase_3",
  steps: [
    "Spawn boss alpha (preview)",
    "Skill base alleato (preview)",
    "Attacco area boss (preview)",
    "Burst combo team (preview)",
    "Enrage hint preview (non autoritativa)",
    "Fase decisiva (preview)",
    "Esito boss preview (non autoritativo)",
  ],
  resultLabel: "victory_preview",
};

const TOWER_FIXTURE: AlphaLoopFixture = {
  mode: "tower",
  title: "Tower Alpha Loop (preview)",
  subtitle: "tower_alpha_preview / floor_alpha_001",
  steps: [
    "Spawn ondata 1 (preview)",
    "Skill alleato base (preview)",
    "Attacco coordinato nemico (preview)",
    "Spawn ondata 2 (preview)",
    "Burst combo team (preview)",
    "Esito floor preview (non autoritativo)",
  ],
  resultLabel: "floor_clear_preview",
};

const GUARDRAILS = {
  result_authoritative: false,
  db_writes: 0,
  battle_engine_runtime_used: false,
  reward_grant_enabled: false,
};

function AlphaLoopCard({
  fixture,
}: {
  fixture: AlphaLoopFixture;
}) {
  const [stepIndex, setStepIndex] = useState<number>(0);
  const [complete, setComplete] = useState<boolean>(false);
  const [autoplay, setAutoplay] = useState<boolean>(false);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const lastStep: boolean = stepIndex >= fixture.steps.length - 1;

  const stopAutoplay = useCallback(() => {
    if (timerRef.current !== null) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    setAutoplay(false);
  }, []);

  const goNext = useCallback(() => {
    if (complete) {
      return;
    }
    if (!lastStep) {
      setStepIndex((s: number) => s + 1);
    } else {
      setComplete(true);
      stopAutoplay();
    }
  }, [complete, lastStep, stopAutoplay]);

  const reset = useCallback(() => {
    setStepIndex(0);
    setComplete(false);
    stopAutoplay();
  }, [stopAutoplay]);

  const togglePlay = useCallback(() => {
    if (autoplay) {
      stopAutoplay();
    } else {
      setAutoplay(true);
    }
  }, [autoplay, stopAutoplay]);

  useEffect(() => {
    if (!autoplay || complete) {
      if (timerRef.current !== null) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
      return;
    }
    timerRef.current = setInterval(() => {
      goNext();
    }, 900);
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
    return Math.min(100, Math.round((done / fixture.steps.length) * 100));
  }, [stepIndex, complete, fixture.steps.length]);

  return (
    <View style={styles.modeCard}>
      <View style={styles.modeHeader}>
        <Text style={styles.modeTitle}>{fixture.title}</Text>
        <Text style={styles.modeSub}>{fixture.subtitle}</Text>
        <Text style={styles.progressLabel}>Avanzamento preview: {progressPct}%</Text>
        <View style={styles.progressBarBg}>
          <View style={[styles.progressBarFill, { width: `${progressPct}%` }]} />
        </View>
      </View>

      <View style={styles.stepsBlock}>
        {fixture.steps.map((label: string, i: number) => {
          const reached: boolean = i <= stepIndex;
          return (
            <View key={`${fixture.mode}-${i}`} style={styles.stepRow}>
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
          <Text style={styles.resultTitle}>Risultato {fixture.mode.toUpperCase()} (PREVIEW)</Text>
          <Text style={styles.resultLine}>outcome_preview: {fixture.resultLabel}</Text>
          <Text style={styles.resultLine}>result_authoritative: false</Text>
          <Text style={styles.rewardDisabled}>Reward preview: DISABILITATA</Text>
          <Text style={styles.rewardDisabled}>Progress preview: DISABILITATA</Text>
        </View>
      ) : null}

      <View style={styles.controls}>
        <TouchableOpacity style={[styles.btn, styles.btnPrimary]} onPress={goNext}>
          <Text style={styles.btnText}>
            {complete ? "Loop completato" : "Step successivo"}
          </Text>
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

export default function BossTowerAlphaLoopPreviewScreen() {
  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.scroll}>
        <View style={styles.bannerPreview}>
          <Text style={styles.bannerText}>
            BOSS + TOWER ALPHA LOOP PREVIEW (DEEPLINK-ONLY)
          </Text>
          <Text style={styles.bannerSub}>
            Anteprima locale non autoritativa - nessun reward, nessun ranking, nessuna progressione
          </Text>
        </View>

        <AlphaLoopCard fixture={BOSS_FIXTURE} />
        <AlphaLoopCard fixture={TOWER_FIXTURE} />

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
        </View>

        <View style={styles.footer}>
          <Text style={styles.footerText}>
            Pack: MEGA_RELEASE_ACCELERATION_17_v68 - Boss/Tower Alpha Loop Preview
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: "#0b0b13" },
  scroll: { padding: 16, paddingBottom: 48 },
  bannerPreview: {
    backgroundColor: "#1a1a2e",
    borderColor: "#ff6644",
    borderWidth: 1,
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
  },
  bannerText: { color: "#ff6644", fontWeight: "bold", fontSize: 13 },
  bannerSub: { color: "#c0c0c0", fontSize: 11, marginTop: 4 },
  modeCard: {
    backgroundColor: "#15151f",
    padding: 14,
    borderRadius: 8,
    borderColor: "#2a2a3e",
    borderWidth: 1,
    marginBottom: 16,
  },
  modeHeader: { marginBottom: 10 },
  modeTitle: { color: "#fff", fontSize: 16, fontWeight: "bold" },
  modeSub: { color: "#a0a0a0", fontSize: 11, marginTop: 2 },
  progressLabel: { color: "#fff", fontSize: 12, marginTop: 8 },
  progressBarBg: {
    backgroundColor: "#222234",
    height: 8,
    borderRadius: 4,
    overflow: "hidden",
    marginTop: 4,
  },
  progressBarFill: { backgroundColor: "#ff6644", height: 8 },
  stepsBlock: { marginVertical: 8 },
  stepRow: { flexDirection: "row", alignItems: "center", marginVertical: 3 },
  stepDot: { width: 10, height: 10, borderRadius: 5, marginRight: 8 },
  stepDotOn: { backgroundColor: "#ff6644" },
  stepDotOff: { backgroundColor: "#444455" },
  stepText: { fontSize: 13 },
  stepTextOn: { color: "#fff" },
  stepTextOff: { color: "#777788" },
  resultBlock: {
    backgroundColor: "#0f0f18",
    padding: 12,
    borderRadius: 6,
    borderColor: "#ff6644",
    borderWidth: 1,
    marginVertical: 8,
  },
  resultTitle: { color: "#ff6644", fontSize: 14, fontWeight: "bold", marginBottom: 4 },
  resultLine: { color: "#fff", fontSize: 12, marginTop: 2 },
  rewardDisabled: { color: "#cccc66", fontSize: 12, marginTop: 4 },
  controls: { flexDirection: "row", flexWrap: "wrap", gap: 8, marginTop: 8 },
  btn: { paddingHorizontal: 12, paddingVertical: 10, borderRadius: 6, minHeight: 44 },
  btnPrimary: { backgroundColor: "#ff6644" },
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
  guardrailTitle: { color: "#ff6644", fontSize: 13, fontWeight: "bold", marginBottom: 6 },
  guardrailLine: { color: "#c0c0c0", fontSize: 11, marginTop: 2 },
  footer: { alignItems: "center", marginTop: 8 },
  footerText: { color: "#666677", fontSize: 10 },
});
