// MEGA_RELEASE_ACCELERATION_17_STORY_PLAYABLE_ALPHA_AND_BOSS_TOWER_ALPHA_LOOP_SUPER_PACK_v68
// TRACK B — Story First Playable Alpha Slice Preview (DEEPLINK-ONLY)
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
// Loop mini-alpha locale: nodo 001 -> nodo 002 -> nodo 003 -> result preview.
// UI in italiano. TypeScript-only (no JSX runtime esoteric, no native deps).

import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";

type NodeId = "story_alpha_node_001" | "story_alpha_node_002" | "story_alpha_node_003";

type AlphaNode = {
  order: number;
  node_id: NodeId;
  label: string;
  steps: string[];
};

const CHAPTER_ID = "chapter_alpha";
const CHAPTER_LABEL = "Capitolo Alpha";

const NODES: AlphaNode[] = [
  {
    order: 1,
    node_id: "story_alpha_node_001",
    label: "Nodo Alpha 001 — Apertura",
    steps: [
      "Intro narrativa preview",
      "Spawn eroe alleato (preview)",
      "Spawn avversario alpha (preview)",
      "Scambio colpi preview",
      "Esito nodo preview (non autoritativo)",
    ],
  },
  {
    order: 2,
    node_id: "story_alpha_node_002",
    label: "Nodo Alpha 002 — Scontro Intermedio",
    steps: [
      "Transizione narrativa preview",
      "Spawn rinforzi alpha (preview)",
      "Combo skill preview",
      "Fase difensiva preview",
      "Esito nodo preview (non autoritativo)",
    ],
  },
  {
    order: 3,
    node_id: "story_alpha_node_003",
    label: "Nodo Alpha 003 — Chiusura",
    steps: [
      "Fase decisiva preview",
      "Skill ultimate preview (non autoritativa)",
      "Sequenza chiusura preview",
      "Esito nodo preview (non autoritativo)",
      "Capitolo alpha completato (anteprima)",
    ],
  },
];

const GUARDRAILS = {
  result_authoritative: false,
  db_writes: 0,
  battle_engine_runtime_used: false,
  reward_grant_enabled: false,
  permanent_progress_enabled: false,
};

export default function StoryAlphaSlicePreviewScreen() {
  const [nodeIndex, setNodeIndex] = useState<number>(0);
  const [stepIndex, setStepIndex] = useState<number>(0);
  const [chapterComplete, setChapterComplete] = useState<boolean>(false);
  const [autoplay, setAutoplay] = useState<boolean>(false);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const currentNode: AlphaNode = NODES[nodeIndex];
  const currentSteps: string[] = currentNode.steps;
  const lastStep: boolean = stepIndex >= currentSteps.length - 1;
  const lastNode: boolean = nodeIndex >= NODES.length - 1;

  const stopAutoplay = useCallback(() => {
    if (timerRef.current !== null) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    setAutoplay(false);
  }, []);

  const goNextStep = useCallback(() => {
    if (chapterComplete) {
      return;
    }
    if (!lastStep) {
      setStepIndex((s: number) => s + 1);
      return;
    }
    // Fine step del nodo: avanza al nodo successivo o completa capitolo
    if (!lastNode) {
      setNodeIndex((n: number) => n + 1);
      setStepIndex(0);
    } else {
      setChapterComplete(true);
      stopAutoplay();
    }
  }, [chapterComplete, lastNode, lastStep, stopAutoplay]);

  const goPrevNode = useCallback(() => {
    if (nodeIndex > 0) {
      setNodeIndex((n: number) => n - 1);
      setStepIndex(0);
      setChapterComplete(false);
    }
  }, [nodeIndex]);

  const goNextNode = useCallback(() => {
    if (nodeIndex < NODES.length - 1) {
      setNodeIndex((n: number) => n + 1);
      setStepIndex(0);
      setChapterComplete(false);
    }
  }, [nodeIndex]);

  const resetChapter = useCallback(() => {
    setNodeIndex(0);
    setStepIndex(0);
    setChapterComplete(false);
    stopAutoplay();
  }, [stopAutoplay]);

  const togglePlay = useCallback(() => {
    if (autoplay) {
      stopAutoplay();
    } else {
      setAutoplay(true);
    }
  }, [autoplay, stopAutoplay]);

  // Autoplay: avanza uno step ogni 900ms con cleanup
  useEffect(() => {
    if (!autoplay || chapterComplete) {
      if (timerRef.current !== null) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
      return;
    }
    timerRef.current = setInterval(() => {
      goNextStep();
    }, 900);
    return () => {
      if (timerRef.current !== null) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    };
  }, [autoplay, chapterComplete, goNextStep]);

  // Cleanup globale a smontaggio
  useEffect(() => {
    return () => {
      if (timerRef.current !== null) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    };
  }, []);

  const progressPct: number = useMemo<number>(() => {
    const totalSteps: number = NODES.reduce((acc: number, n: AlphaNode) => acc + n.steps.length, 0);
    let done: number = 0;
    for (let i = 0; i < nodeIndex; i++) {
      done += NODES[i].steps.length;
    }
    done += stepIndex + (chapterComplete ? 1 : 0);
    const pct: number = Math.min(100, Math.round((done / totalSteps) * 100));
    return pct;
  }, [nodeIndex, stepIndex, chapterComplete]);

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.scroll}>
        <View style={styles.bannerPreview}>
          <Text style={styles.bannerText}>STORY ALPHA SLICE PREVIEW (DEEPLINK-ONLY)</Text>
          <Text style={styles.bannerSub}>
            Anteprima locale non autoritativa - nessun reward, nessuna progressione
          </Text>
        </View>

        <View style={styles.headerBlock}>
          <Text style={styles.chapter}>{CHAPTER_LABEL}</Text>
          <Text style={styles.chapterId}>chapter_id: {CHAPTER_ID}</Text>
          <Text style={styles.progressLabel}>
            Avanzamento preview: {progressPct}% ({nodeIndex + 1}/{NODES.length} nodi)
          </Text>
          <View style={styles.progressBarBg}>
            <View style={[styles.progressBarFill, { width: `${progressPct}%` }]} />
          </View>
        </View>

        <View style={styles.nodeBlock}>
          <Text style={styles.nodeLabel}>{currentNode.label}</Text>
          <Text style={styles.nodeId}>node_id: {currentNode.node_id}</Text>
          <Text style={styles.stepHeader}>Timeline step preview:</Text>
          {currentSteps.map((label: string, i: number) => {
            const reached: boolean = i <= stepIndex;
            return (
              <View key={`${currentNode.node_id}-${i}`} style={styles.stepRow}>
                <View style={[styles.stepDot, reached ? styles.stepDotOn : styles.stepDotOff]} />
                <Text style={[styles.stepText, reached ? styles.stepTextOn : styles.stepTextOff]}>
                  {i + 1}. {label}
                </Text>
              </View>
            );
          })}
        </View>

        {chapterComplete ? (
          <View style={styles.resultBlock}>
            <Text style={styles.resultTitle}>Risultato Capitolo (PREVIEW)</Text>
            <Text style={styles.resultLine}>chapter_complete_preview_only: true</Text>
            <Text style={styles.resultLine}>result_authoritative: false</Text>
            <View style={styles.rewardPreviewBlock}>
              <Text style={styles.rewardDisabled}>Reward preview: DISABILITATA</Text>
              <Text style={styles.rewardDisabled}>Progress preview: DISABILITATA</Text>
            </View>
          </View>
        ) : null}

        <View style={styles.controls}>
          <TouchableOpacity
            style={[styles.btn, styles.btnSecondary]}
            onPress={goPrevNode}
            disabled={nodeIndex === 0}
          >
            <Text style={styles.btnText}>Nodo precedente</Text>
          </TouchableOpacity>
          <TouchableOpacity style={[styles.btn, styles.btnPrimary]} onPress={goNextStep}>
            <Text style={styles.btnText}>
              {chapterComplete ? "Capitolo completato" : "Step successivo"}
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.btn, styles.btnSecondary]}
            onPress={goNextNode}
            disabled={nodeIndex >= NODES.length - 1}
          >
            <Text style={styles.btnText}>Nodo successivo</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.controls}>
          <TouchableOpacity style={[styles.btn, styles.btnTertiary]} onPress={togglePlay}>
            <Text style={styles.btnText}>{autoplay ? "Pausa" : "Play"}</Text>
          </TouchableOpacity>
          <TouchableOpacity style={[styles.btn, styles.btnTertiary]} onPress={resetChapter}>
            <Text style={styles.btnText}>Reset capitolo</Text>
          </TouchableOpacity>
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
            Pack: MEGA_RELEASE_ACCELERATION_17_v68 - Story Playable Alpha Slice
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
    borderColor: "#ffaa00",
    borderWidth: 1,
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
  },
  bannerText: { color: "#ffaa00", fontWeight: "bold", fontSize: 13 },
  bannerSub: { color: "#c0c0c0", fontSize: 11, marginTop: 4 },
  headerBlock: { marginBottom: 16 },
  chapter: { color: "#fff", fontSize: 20, fontWeight: "bold" },
  chapterId: { color: "#a0a0a0", fontSize: 11, marginTop: 2 },
  progressLabel: { color: "#fff", fontSize: 13, marginTop: 10 },
  progressBarBg: {
    backgroundColor: "#222234",
    height: 10,
    borderRadius: 5,
    overflow: "hidden",
    marginTop: 6,
  },
  progressBarFill: { backgroundColor: "#ffaa00", height: 10 },
  nodeBlock: {
    backgroundColor: "#15151f",
    padding: 14,
    borderRadius: 8,
    borderColor: "#2a2a3e",
    borderWidth: 1,
    marginBottom: 16,
  },
  nodeLabel: { color: "#fff", fontSize: 16, fontWeight: "bold" },
  nodeId: { color: "#a0a0a0", fontSize: 11, marginTop: 2, marginBottom: 8 },
  stepHeader: { color: "#fff", fontSize: 13, marginBottom: 6, fontWeight: "600" },
  stepRow: { flexDirection: "row", alignItems: "center", marginVertical: 3 },
  stepDot: { width: 10, height: 10, borderRadius: 5, marginRight: 8 },
  stepDotOn: { backgroundColor: "#ffaa00" },
  stepDotOff: { backgroundColor: "#444455" },
  stepText: { fontSize: 13 },
  stepTextOn: { color: "#fff" },
  stepTextOff: { color: "#777788" },
  resultBlock: {
    backgroundColor: "#15151f",
    padding: 14,
    borderRadius: 8,
    borderColor: "#ffaa00",
    borderWidth: 1,
    marginBottom: 16,
  },
  resultTitle: { color: "#ffaa00", fontSize: 15, fontWeight: "bold", marginBottom: 6 },
  resultLine: { color: "#fff", fontSize: 12, marginTop: 2 },
  rewardPreviewBlock: { marginTop: 8 },
  rewardDisabled: { color: "#cccc66", fontSize: 12, marginTop: 2 },
  controls: { flexDirection: "row", flexWrap: "wrap", gap: 8, marginBottom: 10 },
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
