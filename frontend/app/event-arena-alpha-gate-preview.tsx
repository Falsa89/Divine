// MEGA_RELEASE_ACCELERATION_18_TRAINING_EVENT_ARENA_ASSET_READINESS_SUPER_PACK_v69
// TRACK D — Event + Arena Alpha Gate Preview (DEEPLINK-ONLY)
//
// Guardrail di sicurezza:
//   - deeplink-only, nessun routing pubblico da home/menu
//   - nessuna fetch backend, nessun api story battle, nessun api battle simulate
//   - nessun import da story.tsx o combat.tsx
//   - nessun uso di battle_engine
//   - nessun pulsante claim/reward
//   - nessuna mutazione di ranking/leaderboard
//   - nessuna event currency
//   - nessun matchmaking live
//   - nessun pvp pubblico
//   - nessun uso di Reanimated/AsyncStorage
//   - db_writes=0
//   - reward_grant_enabled=false
//   - arena_ranking_enabled=false
//   - event_currency_enabled=false
//
// UI in italiano. TypeScript-only.

import React from "react";
import {
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";

type GateItem = {
  id: string;
  label: string;
  status: "design_required" | "design_locked";
};

const EVENT_GATES: GateItem[] = [
  { id: "event_design_contract_signed", label: "Contratto design Event firmato", status: "design_required" },
  { id: "event_currency_design_locked", label: "Design Event Currency bloccato", status: "design_required" },
  { id: "event_reward_table_design_locked", label: "Reward table Event bloccata (design)", status: "design_required" },
  { id: "event_idempotency_design_locked", label: "Idempotenza Event bloccata (design)", status: "design_required" },
  { id: "event_rollback_design_locked", label: "Rollback Event bloccato (design)", status: "design_required" },
  { id: "event_observation_plan_signed", label: "Observation plan Event firmato", status: "design_required" },
  { id: "event_anti_abuse_design_locked", label: "Anti-abuse Event bloccato (design)", status: "design_required" },
  { id: "manual_approval_pre_live", label: "Manual approval pre-live", status: "design_required" },
];

const ARENA_GATES: GateItem[] = [
  { id: "arena_design_contract_signed", label: "Contratto design Arena firmato", status: "design_required" },
  { id: "arena_ranking_design_locked", label: "Ranking Arena bloccato (design)", status: "design_required" },
  { id: "arena_mmr_design_locked", label: "MMR Arena bloccato (design)", status: "design_required" },
  { id: "arena_match_idempotency_design_locked", label: "Match idempotency bloccato (design)", status: "design_required" },
  { id: "arena_rollback_design_locked", label: "Rollback Arena bloccato (design)", status: "design_required" },
  { id: "arena_observation_plan_signed", label: "Observation plan Arena firmato", status: "design_required" },
  { id: "arena_anti_abuse_design_locked", label: "Anti-abuse Arena bloccato (design)", status: "design_required" },
  { id: "manual_approval_pre_live", label: "Manual approval pre-live", status: "design_required" },
];

const GUARDRAILS = {
  db_writes: 0,
  reward_grant_enabled: false,
  arena_ranking_enabled: false,
  event_currency_enabled: false,
  matchmaking_live: false,
  public_pvp_enabled: false,
  battle_engine_runtime_used: false,
};

function GateCard({ title, subtitle, gates }: { title: string; subtitle: string; gates: GateItem[] }) {
  return (
    <View style={styles.card}>
      <Text style={styles.cardTitle}>{title}</Text>
      <Text style={styles.cardSub}>{subtitle}</Text>
      <View style={styles.gateList}>
        {gates.map((g: GateItem) => (
          <View key={g.id} style={styles.gateRow}>
            <View style={styles.gateDot} />
            <Text style={styles.gateLabel}>{g.label}</Text>
          </View>
        ))}
      </View>
      <View style={styles.disabledBlock}>
        <Text style={styles.disabledLine}>Rewards: DISABILITATI (preview)</Text>
        <Text style={styles.disabledLine}>Ranking / Leaderboard: DISABILITATI (preview)</Text>
        <Text style={styles.disabledLine}>Currency: DISABILITATA (preview)</Text>
      </View>
    </View>
  );
}

export default function EventArenaAlphaGatePreviewScreen() {
  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.scroll}>
        <View style={styles.banner}>
          <Text style={styles.bannerText}>EVENT + ARENA ALPHA GATE PREVIEW (DEEPLINK-ONLY)</Text>
          <Text style={styles.bannerSub}>
            Anteprima di design - tutti i gate richiedono manual approval prima del live
          </Text>
        </View>

        <GateCard
          title="Event Alpha Gate"
          subtitle="Design pre-live - nessun runtime, nessuna currency, nessun reward claim"
          gates={EVENT_GATES}
        />

        <GateCard
          title="Arena Alpha Gate"
          subtitle="Design pre-live - nessun ranking live, nessun MMR live, nessun matchmaking live"
          gates={ARENA_GATES}
        />

        <View style={styles.guardrailBlock}>
          <Text style={styles.guardrailTitle}>Guardrail preview</Text>
          <Text style={styles.guardrailLine}>db_writes: {GUARDRAILS.db_writes}</Text>
          <Text style={styles.guardrailLine}>
            reward_grant_enabled: {String(GUARDRAILS.reward_grant_enabled)}
          </Text>
          <Text style={styles.guardrailLine}>
            arena_ranking_enabled: {String(GUARDRAILS.arena_ranking_enabled)}
          </Text>
          <Text style={styles.guardrailLine}>
            event_currency_enabled: {String(GUARDRAILS.event_currency_enabled)}
          </Text>
          <Text style={styles.guardrailLine}>
            matchmaking_live: {String(GUARDRAILS.matchmaking_live)}
          </Text>
          <Text style={styles.guardrailLine}>
            public_pvp_enabled: {String(GUARDRAILS.public_pvp_enabled)}
          </Text>
          <Text style={styles.guardrailLine}>
            battle_engine_runtime_used: {String(GUARDRAILS.battle_engine_runtime_used)}
          </Text>
        </View>

        <View style={styles.footer}>
          <Text style={styles.footerText}>
            Pack: MEGA_RELEASE_ACCELERATION_18_v69 - Event/Arena Alpha Gate Preview
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
    borderColor: "#aa66ff",
    borderWidth: 1,
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
  },
  bannerText: { color: "#aa66ff", fontWeight: "bold", fontSize: 13 },
  bannerSub: { color: "#c0c0c0", fontSize: 11, marginTop: 4 },
  card: {
    backgroundColor: "#15151f",
    padding: 14,
    borderRadius: 8,
    borderColor: "#2a2a3e",
    borderWidth: 1,
    marginBottom: 16,
  },
  cardTitle: { color: "#fff", fontSize: 16, fontWeight: "bold" },
  cardSub: { color: "#a0a0a0", fontSize: 11, marginTop: 4, marginBottom: 8 },
  gateList: { marginTop: 4 },
  gateRow: { flexDirection: "row", alignItems: "center", marginVertical: 3 },
  gateDot: { width: 8, height: 8, borderRadius: 4, marginRight: 8, backgroundColor: "#aa66ff" },
  gateLabel: { color: "#fff", fontSize: 12, flexShrink: 1 },
  disabledBlock: { marginTop: 10, paddingTop: 8, borderTopColor: "#2a2a3e", borderTopWidth: 1 },
  disabledLine: { color: "#cccc66", fontSize: 11, marginTop: 2 },
  guardrailBlock: {
    backgroundColor: "#0f0f18",
    padding: 12,
    borderRadius: 8,
    borderColor: "#2a2a3e",
    borderWidth: 1,
    marginTop: 8,
    marginBottom: 16,
  },
  guardrailTitle: { color: "#aa66ff", fontSize: 13, fontWeight: "bold", marginBottom: 6 },
  guardrailLine: { color: "#c0c0c0", fontSize: 11, marginTop: 2 },
  footer: { alignItems: "center", marginTop: 8 },
  footerText: { color: "#666677", fontSize: 10 },
});
