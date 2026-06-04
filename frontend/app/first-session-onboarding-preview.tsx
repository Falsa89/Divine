// MEGA_RELEASE_ACCELERATION_19_EVENT_ARENA_FIRST_ALPHA_AND_FIRST_SESSION_ONBOARDING_SUPER_PACK_v70
// TRACK D - First Session Onboarding Preview (DEEPLINK-ONLY)
//
// Guardrail:
//   - deeplink-only, no public menu routing
//   - no backend fetch, no auth/account mutation
//   - no AsyncStorage persistence
//   - no DB writes
//   - no battle_engine, no api story battle, no api battle simulate
//   - no import da story.tsx o combat.tsx
//   - no reward grant, no permanent progress
//   - no tutorial completion write
//   - no Reanimated
//
// I "link" sono solo testuali / hint informativi - non navigano via router pubblico.
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
  | "welcome"
  | "training_combat_onboarding_preview"
  | "story_alpha_slice_preview"
  | "event_arena_gate_or_alpha_preview"
  | "hero_asset_status_explainer"
  | "next_steps_summary";

type SessionStep = {
  order: number;
  id: StepId;
  label: string;
  body: string;
  deeplinkHint: string | null;
};

const STATE_MACHINE_LABEL: Record<StepId, string> = {
  welcome: "intro",
  training_combat_onboarding_preview: "training_preview",
  story_alpha_slice_preview: "story_alpha_preview",
  event_arena_gate_or_alpha_preview: "event_arena_preview",
  hero_asset_status_explainer: "asset_status_explainer",
  next_steps_summary: "qa_ready_summary",
};

const STEPS: SessionStep[] = [
  {
    order: 1,
    id: "welcome",
    label: "Benvenuto",
    body:
      "Anteprima locale della prima sessione. Nessun account viene creato o modificato. Nessuna persistenza viene scritta. Tutto rimane in memoria del client.",
    deeplinkHint: null,
  },
  {
    order: 2,
    id: "training_combat_onboarding_preview",
    label: "Training di combattimento",
    body:
      "Hint deeplink: training-combat-onboarding-preview - 6 step tutorial in preview locale, non autoritativi, no reward grant.",
    deeplinkHint: "training-combat-onboarding-preview",
  },
  {
    order: 3,
    id: "story_alpha_slice_preview",
    label: "Story alpha slice",
    body:
      "Hint deeplink: story-alpha-slice-preview - mini-loop su nodi 001/002/003, no reward grant, no permanent progress.",
    deeplinkHint: "story-alpha-slice-preview",
  },
  {
    order: 4,
    id: "event_arena_gate_or_alpha_preview",
    label: "Event/Arena gate o alpha",
    body:
      "Hint deeplink: event-arena-alpha-gate-preview (design) oppure event-arena-first-alpha-slice-preview (mini slice locale). Nessuna currency, nessun ranking, nessun matchmaking live.",
    deeplinkHint: "event-arena-first-alpha-slice-preview",
  },
  {
    order: 5,
    id: "hero_asset_status_explainer",
    label: "Stato Hero Asset",
    body:
      "Gli asset reali degli eroi restano deferred fino a quando l'utente fornisce il pack asset reale. Nessuna copia, nessun import, nessun overwrite, nessun runtime resolver cambiato.",
    deeplinkHint: null,
  },
  {
    order: 6,
    id: "next_steps_summary",
    label: "Prossimi passi",
    body:
      "Riepilogo locale: niente onboarding completion write, niente reward, niente persistenza account. Il flusso reale richiede manual approval pre-live.",
    deeplinkHint: null,
  },
];

const GUARDRAILS = {
  db_writes: 0,
  permanent_onboarding_complete: false,
  reward_grant_enabled: false,
  account_mutation: false,
  async_storage_persistence: false,
  battle_engine_runtime_used: false,
};

export default function FirstSessionOnboardingPreviewScreen() {
  const [stepIndex, setStepIndex] = useState<number>(0);
  const last: boolean = stepIndex >= STEPS.length - 1;
  const current: SessionStep = STEPS[stepIndex];

  const goNext = useCallback(() => {
    if (!last) setStepIndex((s: number) => s + 1);
  }, [last]);

  const goPrev = useCallback(() => {
    if (stepIndex > 0) setStepIndex((s: number) => s - 1);
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
          <Text style={styles.bannerText}>FIRST SESSION ONBOARDING PREVIEW (DEEPLINK-ONLY) - HARDENED v71</Text>
          <Text style={styles.bannerSub}>
            Anteprima locale - nessuna scrittura su account/DB, nessun reward, nessuna persistenza
          </Text>
        </View>

        <View style={styles.hardeningBlock}>
          <Text style={styles.hardeningTitle}>Hardening Panel (v71)</Text>
          <Text style={styles.hardeningLine}>account_mutation: false</Text>
          <Text style={styles.hardeningLine}>async_storage_persistence: false</Text>
          <Text style={styles.hardeningLine}>permanent_onboarding_complete: false</Text>
          <Text style={styles.hardeningLine}>db_writes: 0</Text>
          <Text style={styles.hardeningLine}>reward_grant_enabled: false</Text>
          <Text style={styles.hardeningLine}>state_machine: preview_only_local</Text>
          <View style={styles.completeIndicator}>
            <Text style={styles.completeIndicatorText}>
              Completa onboarding: DISABILITATO (preview, nessuna scrittura)
            </Text>
          </View>
        </View>

        <View style={styles.header}>
          <Text style={styles.title}>Prima Sessione (anteprima)</Text>
          <Text style={styles.subtitle}>Avanzamento preview: {progressPct}%</Text>
          <View style={styles.progressBarBg}>
            <View style={[styles.progressBarFill, { width: `${progressPct}%` }]} />
          </View>
        </View>

        <View style={styles.stepCard}>
          <Text style={styles.stepOrder}>Step {current.order} / {STEPS.length}</Text>
          <Text style={styles.stepLabel}>{current.label}</Text>
          <Text style={styles.stateMachineLabel}>
            state machine (preview): {STATE_MACHINE_LABEL[current.id]} - persists=false
          </Text>
          <Text style={styles.stepBody}>{current.body}</Text>
          {current.deeplinkHint ? (
            <Text style={styles.deeplinkHint}>Deeplink hint: {current.deeplinkHint}</Text>
          ) : null}
        </View>

        <View style={styles.controls}>
          <TouchableOpacity
            style={[styles.btn, styles.btnSecondary]}
            onPress={goPrev}
            disabled={stepIndex === 0}
          >
            <Text style={styles.btnText}>Step precedente</Text>
          </TouchableOpacity>
          <TouchableOpacity style={[styles.btn, styles.btnPrimary]} onPress={goNext} disabled={last}>
            <Text style={styles.btnText}>{last ? "Anteprima completata" : "Step successivo"}</Text>
          </TouchableOpacity>
          <TouchableOpacity style={[styles.btn, styles.btnTertiary]} onPress={reset}>
            <Text style={styles.btnText}>Reset preview</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.linksBlock}>
          <Text style={styles.linksTitle}>Schermate anteprime collegate (deeplink-only)</Text>
          <Text style={styles.linksItem}>- training-combat-onboarding-preview</Text>
          <Text style={styles.linksItem}>- story-alpha-slice-preview</Text>
          <Text style={styles.linksItem}>- event-arena-alpha-gate-preview</Text>
          <Text style={styles.linksItem}>- event-arena-first-alpha-slice-preview</Text>
          <Text style={styles.linksItem}>- boss-tower-alpha-loop-preview</Text>
        </View>

        <View style={styles.guardrailBlock}>
          <Text style={styles.guardrailTitle}>Guardrail preview</Text>
          <Text style={styles.guardrailLine}>db_writes: {GUARDRAILS.db_writes}</Text>
          <Text style={styles.guardrailLine}>
            permanent_onboarding_complete: {String(GUARDRAILS.permanent_onboarding_complete)}
          </Text>
          <Text style={styles.guardrailLine}>
            reward_grant_enabled: {String(GUARDRAILS.reward_grant_enabled)}
          </Text>
          <Text style={styles.guardrailLine}>
            account_mutation: {String(GUARDRAILS.account_mutation)}
          </Text>
          <Text style={styles.guardrailLine}>
            async_storage_persistence: {String(GUARDRAILS.async_storage_persistence)}
          </Text>
          <Text style={styles.guardrailLine}>
            battle_engine_runtime_used: {String(GUARDRAILS.battle_engine_runtime_used)}
          </Text>
        </View>

        <View style={styles.footer}>
          <Text style={styles.footerText}>
            Pack: MEGA_RELEASE_ACCELERATION_19_v70 - First Session Onboarding Preview
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
    borderColor: "#66ddaa",
    borderWidth: 1,
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
  },
  bannerText: { color: "#66ddaa", fontWeight: "bold", fontSize: 13 },
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
  progressBarFill: { backgroundColor: "#66ddaa", height: 10 },
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
  deeplinkHint: { color: "#66ddaa", fontSize: 11, marginTop: 8 },
  stateMachineLabel: { color: "#88aabb", fontSize: 10, marginTop: 6, marginBottom: 6, lineHeight: 14, fontStyle: "italic" },
  hardeningBlock: {
    backgroundColor: "#0f0f18",
    padding: 12,
    borderRadius: 8,
    borderColor: "#66ddaa",
    borderWidth: 1,
    marginBottom: 12,
  },
  hardeningTitle: { color: "#66ddaa", fontSize: 13, fontWeight: "bold", marginBottom: 6 },
  hardeningLine: { color: "#c0c0c0", fontSize: 11, marginTop: 2 },
  completeIndicator: {
    backgroundColor: "#22223a",
    borderColor: "#444466",
    borderWidth: 1,
    borderRadius: 6,
    padding: 8,
    marginTop: 8,
    opacity: 0.6,
  },
  completeIndicatorText: { color: "#cccc66", fontSize: 11, textAlign: "center" },
  controls: { flexDirection: "row", flexWrap: "wrap", gap: 8, marginBottom: 10 },
  btn: { paddingHorizontal: 12, paddingVertical: 10, borderRadius: 6, minHeight: 44 },
  btnPrimary: { backgroundColor: "#66ddaa" },
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
  linksTitle: { color: "#66ddaa", fontSize: 13, fontWeight: "bold", marginBottom: 6 },
  linksItem: { color: "#c0c0c0", fontSize: 11, marginTop: 2 },
  guardrailBlock: {
    backgroundColor: "#0f0f18",
    padding: 12,
    borderRadius: 8,
    borderColor: "#2a2a3e",
    borderWidth: 1,
    marginTop: 8,
    marginBottom: 16,
  },
  guardrailTitle: { color: "#66ddaa", fontSize: 13, fontWeight: "bold", marginBottom: 6 },
  guardrailLine: { color: "#c0c0c0", fontSize: 11, marginTop: 2 },
  footer: { alignItems: "center", marginTop: 8 },
  footerText: { color: "#666677", fontSize: 10 },
});
