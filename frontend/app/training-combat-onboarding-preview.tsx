// MEGA_RELEASE_ACCELERATION_18_TRAINING_EVENT_ARENA_ASSET_READINESS_SUPER_PACK_v69
// TRACK B — Training + Combat Onboarding Preview (DEEPLINK-ONLY)
//
// Guardrail di sicurezza:
//   - deeplink-only, nessun routing pubblico da home/menu
//   - nessuna fetch backend, nessun api story battle, nessun api battle simulate
//   - nessun import da story.tsx o combat.tsx
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
// UI in italiano. TypeScript-only.

import React, { useCallback, useMemo, useState } from "react";
import {
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";

type StepId =
  | "team_positioning"
  | "attack_order"
  | "skill_preview"
  | "result_preview"
  | "reward_preview_disabled"
  | "preview_vs_real_battle";

type TutorialStep = {
  order: number;
  id: StepId;
  label: string;
  body: string;
};

const STEPS: TutorialStep[] = [
  {
    order: 1,
    id: "team_positioning",
    label: "Posizionamento del team",
    body:
      "Disponi gli eroi negli slot front/back. Nessuna mutazione: e' una preview, la formazione reale non viene salvata.",
  },
  {
    order: 2,
    id: "attack_order",
    label: "Ordine di attacco",
    body:
      "L'ordine dipende dallo SPEED degli eroi. In preview lo vedi come timeline locale, nessun runtime autoritativo.",
  },
  {
    order: 3,
    id: "skill_preview",
    label: "Skill in anteprima",
    body:
      "Le skill base/active/ultimate sono mostrate solo a scopo didattico. Nessun engine reale viene chiamato.",
  },
  {
    order: 4,
    id: "result_preview",
    label: "Risultato in anteprima",
    body: "Il risultato e' un esempio. result_authoritative=false, nessuna progressione viene salvata.",
  },
  {
    order: 5,
    id: "reward_preview_disabled",
    label: "Reward preview disabilitato",
    body:
      "In preview NON ricevi reward. Nessun mail reward, nessun avanzamento Battle Pass / achievement / daily quest.",
  },
  {
    order: 6,
    id: "preview_vs_real_battle",
    label: "Preview vs battle reale",
    body:
      "Quando arrivera' il runtime autoritativo i reward saranno reali. Oggi siamo in preview-only / deeplink-only.",
  },
];

const GUARDRAILS = {
  result_authoritative: false,
  db_writes: 0,
  battle_engine_runtime_used: false,
  reward_grant_enabled: false,
  permanent_progress_enabled: false,
};

export default function TrainingCombatOnboardingPreviewScreen() {
  const [stepIndex, setStepIndex] = useState<number>(0);
  const last: boolean = stepIndex >= STEPS.length - 1;
  const current: TutorialStep = STEPS[stepIndex];

  const goNext = useCallback(() => {
    if (!last) {
      setStepIndex((s: number) => s + 1);
    }
  }, [last]);

  const goPrev = useCallback(() => {
    if (stepIndex > 0) {
      setStepIndex((s: number) => s - 1);
    }
  }, [stepIndex]);

  const reset = useCallback(() => {
    setStepIndex(0);
  }, []);

  const progressPct: number = useMemo<number>(() => {
    return Math.round(((stepIndex + 1) / STEPS.length) * 100);
  }, [stepIndex]);

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.scroll}>
        <View style={styles.banner}>
          <Text style={styles.bannerText}>TRAINING + COMBAT ONBOARDING PREVIEW (DEEPLINK-ONLY)</Text>
          <Text style={styles.bannerSub}>
            Tutorial locale non autoritativo - nessun reward, nessuna progressione
          </Text>
        </View>

        <View style={styles.header}>
          <Text style={styles.title}>Tutorial di Combattimento</Text>
          <Text style={styles.subtitle}>Avanzamento preview: {progressPct}%</Text>
          <View style={styles.progressBarBg}>
            <View style={[styles.progressBarFill, { width: `${progressPct}%` }]} />
          </View>
        </View>

        <View style={styles.stepCard}>
          <Text style={styles.stepOrder}>Step {current.order} / {STEPS.length}</Text>
          <Text style={styles.stepLabel}>{current.label}</Text>
          <Text style={styles.stepBody}>{current.body}</Text>
        </View>

        <View style={styles.controls}>
          <TouchableOpacity
            style={[styles.btn, styles.btnSecondary]}
            onPress={goPrev}
            disabled={stepIndex === 0}
          >
            <Text style={styles.btnText}>Indietro</Text>
          </TouchableOpacity>
          <TouchableOpacity style={[styles.btn, styles.btnPrimary]} onPress={goNext} disabled={last}>
            <Text style={styles.btnText}>{last ? "Tutorial completato" : "Avanti"}</Text>
          </TouchableOpacity>
          <TouchableOpacity style={[styles.btn, styles.btnTertiary]} onPress={reset}>
            <Text style={styles.btnText}>Reset</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.linksBlock}>
          <Text style={styles.linksTitle}>Anteprime correlate (deeplink-only)</Text>
          <Text style={styles.linksHint}>
            story-alpha-slice-preview, boss-tower-alpha-loop-preview
          </Text>
        </View>

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
            permanent_progress_enabled: {String(GUARDRAILS.permanent_progress_enabled)}
          </Text>
        </View>

        <View style={styles.footer}>
          <Text style={styles.footerText}>
            Pack: MEGA_RELEASE_ACCELERATION_18_v69 - Training + Combat Onboarding Preview
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
    borderColor: "#44aaff",
    borderWidth: 1,
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
  },
  bannerText: { color: "#44aaff", fontWeight: "bold", fontSize: 13 },
  bannerSub: { color: "#c0c0c0", fontSize: 11, marginTop: 4 },
  header: { marginBottom: 16 },
  title: { color: "#fff", fontSize: 20, fontWeight: "bold" },
  subtitle: { color: "#fff", fontSize: 13, marginTop: 8 },
  progressBarBg: {
    backgroundColor: "#222234",
    height: 10,
    borderRadius: 5,
    overflow: "hidden",
    marginTop: 6,
  },
  progressBarFill: { backgroundColor: "#44aaff", height: 10 },
  stepCard: {
    backgroundColor: "#15151f",
    padding: 14,
    borderRadius: 8,
    borderColor: "#2a2a3e",
    borderWidth: 1,
    marginBottom: 16,
  },
  stepOrder: { color: "#a0a0a0", fontSize: 11, marginBottom: 4 },
  stepLabel: { color: "#fff", fontSize: 16, fontWeight: "bold", marginBottom: 6 },
  stepBody: { color: "#c0c0c0", fontSize: 13, lineHeight: 18 },
  controls: { flexDirection: "row", flexWrap: "wrap", gap: 8, marginBottom: 10 },
  btn: { paddingHorizontal: 12, paddingVertical: 10, borderRadius: 6, minHeight: 44 },
  btnPrimary: { backgroundColor: "#44aaff" },
  btnSecondary: { backgroundColor: "#3a3a5e" },
  btnTertiary: { backgroundColor: "#22223a", borderColor: "#3a3a5e", borderWidth: 1 },
  btnText: { color: "#0b0b13", fontWeight: "bold", fontSize: 12, textAlign: "center" },
  linksBlock: {
    backgroundColor: "#0f0f18",
    padding: 12,
    borderRadius: 8,
    borderColor: "#2a2a3e",
    borderWidth: 1,
    marginVertical: 8,
  },
  linksTitle: { color: "#44aaff", fontSize: 13, fontWeight: "bold", marginBottom: 4 },
  linksHint: { color: "#a0a0a0", fontSize: 11 },
  guardrailBlock: {
    backgroundColor: "#0f0f18",
    padding: 12,
    borderRadius: 8,
    borderColor: "#2a2a3e",
    borderWidth: 1,
    marginTop: 8,
    marginBottom: 16,
  },
  guardrailTitle: { color: "#44aaff", fontSize: 13, fontWeight: "bold", marginBottom: 6 },
  guardrailLine: { color: "#c0c0c0", fontSize: 11, marginTop: 2 },
  footer: { alignItems: "center", marginTop: 8 },
  footerText: { color: "#666677", fontSize: 10 },
});
