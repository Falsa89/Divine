// MEGA_RELEASE_ACCELERATION_20_ONBOARDING_MENU_GATE_AND_ALPHA_INTERNAL_QA_SUPER_PACK_v71
// TRACK D - Alpha Preview Hub (DEEPLINK-ONLY)
//
// Guardrail:
//   - deeplink-only, no public menu/home routing
//   - no backend fetch, no DB writes
//   - no auth/account mutation, no AsyncStorage
//   - no reward grant, no permanent progress
//   - no import da story.tsx o combat.tsx, no battle_engine
//   - no api story battle, no api battle simulate
//   - solo elenco testuale delle preview con guardrail chips
//   - tutti i deeplink sono indicati come hint testuali (non navigano via router pubblico)
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

type PreviewEntry = {
  route: string;
  title: string;
  status: string;
  guardrails: string[];
  publicReleaseBadge: "DISABLED" | "DEEPLINK_ONLY";
  qaPriority: "P0" | "P1" | "P2" | "P3";
};

const ENTRIES: PreviewEntry[] = [
  {
    route: "first-session-onboarding-preview",
    title: "First Session Onboarding (hardened v71)",
    status: "preview_hardened_v71",
    guardrails: [
      "db_writes=0",
      "permanent_onboarding_complete=false",
      "account_flag_writes=false",
      "async_storage_persistence=false",
    ],
    publicReleaseBadge: "DEEPLINK_ONLY",
    qaPriority: "P0",
  },
  {
    route: "training-combat-onboarding-preview",
    title: "Training + Combat Onboarding",
    status: "preview_ready_v69",
    guardrails: ["db_writes=0", "reward_grant=false", "permanent_progress=false"],
    publicReleaseBadge: "DEEPLINK_ONLY",
    qaPriority: "P1",
  },
  {
    route: "story-alpha-slice-preview",
    title: "Story Alpha Slice (nodi 001/002/003)",
    status: "preview_ready_v68",
    guardrails: ["db_writes=0", "result_authoritative=false", "reward_grant=false"],
    publicReleaseBadge: "DEEPLINK_ONLY",
    qaPriority: "P1",
  },
  {
    route: "boss-tower-alpha-loop-preview",
    title: "Boss + Tower Alpha Loop",
    status: "preview_ready_v68",
    guardrails: ["db_writes=0", "leaderboard_writes=false", "reward_grant=false"],
    publicReleaseBadge: "DEEPLINK_ONLY",
    qaPriority: "P1",
  },
  {
    route: "event-arena-alpha-gate-preview",
    title: "Event + Arena Alpha Gate (design)",
    status: "design_ready_v69",
    guardrails: [
      "db_writes=0",
      "event_currency_enabled=false",
      "arena_ranking_enabled=false",
      "matchmaking_live=false",
    ],
    publicReleaseBadge: "DEEPLINK_ONLY",
    qaPriority: "P1",
  },
  {
    route: "event-arena-first-alpha-slice-preview",
    title: "Event + Arena First Alpha Slice",
    status: "preview_ready_v70",
    guardrails: [
      "db_writes=0",
      "event_currency_enabled=false",
      "arena_ranking_enabled=false",
      "reward_grant=false",
    ],
    publicReleaseBadge: "DEEPLINK_ONLY",
    qaPriority: "P1",
  },
  {
    route: "visual-battle-preview-router",
    title: "Visual Battle Preview Router (legacy)",
    status: "design_ready_legacy",
    guardrails: ["db_writes=0", "result_authoritative=false"],
    publicReleaseBadge: "DEEPLINK_ONLY",
    qaPriority: "P2",
  },
];

const GUARDRAILS = {
  db_writes: 0,
  reward_grant_enabled: false,
  permanent_progress_enabled: false,
  account_mutation: false,
  async_storage_persistence: false,
  battle_engine_runtime_used: false,
  public_menu_routing_enabled: false,
};

export default function AlphaPreviewHubScreen() {
  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.scroll}>
        <View style={styles.banner}>
          <Text style={styles.bannerText}>ALPHA PREVIEW HUB (DEEPLINK-ONLY)</Text>
          <Text style={styles.bannerSub}>
            Mappa locale anteprime alpha. No routing pubblico, no reward, no writes.
          </Text>
        </View>

        {ENTRIES.map((e: PreviewEntry) => (
          <View key={e.route} style={styles.entryCard}>
            <Text style={styles.entryTitle}>{e.title}</Text>
            <Text style={styles.entryRoute}>route hint: {e.route}</Text>
            <Text style={styles.entryStatus}>status: {e.status}</Text>
            <View style={styles.chipsRow}>
              {e.guardrails.map((g: string) => (
                <View key={g} style={styles.chip}>
                  <Text style={styles.chipText}>{g}</Text>
                </View>
              ))}
            </View>
            <View style={styles.badgeRow}>
              <View style={styles.releaseBadge}>
                <Text style={styles.releaseBadgeText}>
                  public release: {e.publicReleaseBadge === "DEEPLINK_ONLY" ? "DEEPLINK-ONLY (disabled)" : "DISABLED"}
                </Text>
              </View>
              <View style={styles.qaBadge}>
                <Text style={styles.qaBadgeText}>QA: {e.qaPriority}</Text>
              </View>
            </View>
          </View>
        ))}

        <View style={styles.guardrailBlock}>
          <Text style={styles.guardrailTitle}>Guardrail hub</Text>
          <Text style={styles.guardrailLine}>db_writes: {GUARDRAILS.db_writes}</Text>
          <Text style={styles.guardrailLine}>
            reward_grant_enabled: {String(GUARDRAILS.reward_grant_enabled)}
          </Text>
          <Text style={styles.guardrailLine}>
            permanent_progress_enabled: {String(GUARDRAILS.permanent_progress_enabled)}
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
          <Text style={styles.guardrailLine}>
            public_menu_routing_enabled: {String(GUARDRAILS.public_menu_routing_enabled)}
          </Text>
        </View>

        <View style={styles.footer}>
          <Text style={styles.footerText}>
            Pack: MEGA_RELEASE_ACCELERATION_20_v71 - Alpha Preview Hub (deeplink-only)
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
    borderColor: "#88ccff",
    borderWidth: 1,
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
  },
  bannerText: { color: "#88ccff", fontWeight: "bold", fontSize: 13 },
  bannerSub: { color: "#c0c0c0", fontSize: 11, marginTop: 4 },
  entryCard: {
    backgroundColor: "#15151f",
    padding: 14,
    borderRadius: 8,
    borderColor: "#2a2a3e",
    borderWidth: 1,
    marginBottom: 12,
  },
  entryTitle: { color: "#fff", fontSize: 14, fontWeight: "bold" },
  entryRoute: { color: "#88ccff", fontSize: 11, marginTop: 4 },
  entryStatus: { color: "#a0a0a0", fontSize: 11, marginTop: 2 },
  chipsRow: { flexDirection: "row", flexWrap: "wrap", gap: 6, marginTop: 8 },
  chip: {
    backgroundColor: "#22223a",
    borderColor: "#3a3a5e",
    borderWidth: 1,
    borderRadius: 4,
    paddingHorizontal: 6,
    paddingVertical: 3,
  },
  chipText: { color: "#c0c0c0", fontSize: 10 },
  badgeRow: { flexDirection: "row", flexWrap: "wrap", gap: 8, marginTop: 8 },
  releaseBadge: {
    backgroundColor: "#3a1a1a",
    borderColor: "#aa4444",
    borderWidth: 1,
    borderRadius: 4,
    paddingHorizontal: 8,
    paddingVertical: 4,
  },
  releaseBadgeText: { color: "#ffaaaa", fontSize: 10, fontWeight: "bold" },
  qaBadge: {
    backgroundColor: "#1a3a1a",
    borderColor: "#44aa44",
    borderWidth: 1,
    borderRadius: 4,
    paddingHorizontal: 8,
    paddingVertical: 4,
  },
  qaBadgeText: { color: "#aaffaa", fontSize: 10, fontWeight: "bold" },
  guardrailBlock: {
    backgroundColor: "#0f0f18",
    padding: 12,
    borderRadius: 8,
    borderColor: "#2a2a3e",
    borderWidth: 1,
    marginTop: 8,
    marginBottom: 16,
  },
  guardrailTitle: { color: "#88ccff", fontSize: 13, fontWeight: "bold", marginBottom: 6 },
  guardrailLine: { color: "#c0c0c0", fontSize: 11, marginTop: 2 },
  footer: { alignItems: "center", marginTop: 8 },
  footerText: { color: "#666677", fontSize: 10 },
});
