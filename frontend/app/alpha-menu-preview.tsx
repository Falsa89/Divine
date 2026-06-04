// MEGA_RELEASE_ACCELERATION_23_MENU_PUBLIC_EXPOSURE_APPLY_AND_CLOSED_ALPHA_KICKOFF_GATE_PACK_v74
// Alpha Menu Preview Section (controlled menu exposure)
//
// Guardrail (assertito per design e per validator OPTIONAL):
//   - controlled alpha preview menu exposure (NON home/tab/menu pubblico)
//   - nessun fetch backend, nessun DB write
//   - nessun import da story.tsx o combat.tsx
//   - nessun battle_engine, nessun api/story/battle, nessun api/battle/simulate
//   - nessun AsyncStorage, nessun account flag write, nessun auth mutation
//   - nessun reward grant, nessun permanent progress, nessun onboarding completion
//   - nessun event currency, nessun arena ranking/MMR, nessun matchmaking live
//   - nessun inventory/wallet/premium gems/gacha/shop/VIP/Battle Pass mutation
//   - nessun asset import/copy, nessun resolver runtime change
//   - nessuna release commerciale ampia
//   - solo elenco testuale delle 7 preview con badge guardrail
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

type PreviewMenuEntry = {
  route: string;
  title: string;
  qaPriority: "P0" | "P1" | "P2" | "P3";
  exposureBadge: "ALPHA_MENU_EXPOSED";
  guardrails: string[];
};

const ENTRIES: PreviewMenuEntry[] = [
  {
    route: "alpha-preview-hub",
    title: "Alpha Preview Hub",
    qaPriority: "P0",
    exposureBadge: "ALPHA_MENU_EXPOSED",
    guardrails: ["deeplink_only_today", "db_writes=0", "no_fetch"],
  },
  {
    route: "first-session-onboarding-preview",
    title: "First Session Onboarding (hardened)",
    qaPriority: "P0",
    exposureBadge: "ALPHA_MENU_EXPOSED",
    guardrails: [
      "db_writes=0",
      "permanent_onboarding_complete=false",
      "account_flag_writes=false",
    ],
  },
  {
    route: "training-combat-onboarding-preview",
    title: "Training + Combat Onboarding",
    qaPriority: "P1",
    exposureBadge: "ALPHA_MENU_EXPOSED",
    guardrails: [
      "db_writes=0",
      "reward_grant=false",
      "permanent_progress=false",
    ],
  },
  {
    route: "story-alpha-slice-preview",
    title: "Story Alpha Slice",
    qaPriority: "P0",
    exposureBadge: "ALPHA_MENU_EXPOSED",
    guardrails: [
      "db_writes=0",
      "no_import_story_tsx",
      "no_battle_engine_runtime",
    ],
  },
  {
    route: "boss-tower-alpha-loop-preview",
    title: "Boss / Tower Alpha Loop",
    qaPriority: "P1",
    exposureBadge: "ALPHA_MENU_EXPOSED",
    guardrails: [
      "db_writes=0",
      "no_import_combat_tsx",
      "no_battle_engine_runtime",
    ],
  },
  {
    route: "event-arena-alpha-gate-preview",
    title: "Event / Arena Alpha Gate",
    qaPriority: "P2",
    exposureBadge: "ALPHA_MENU_EXPOSED",
    guardrails: [
      "db_writes=0",
      "event_currency_enabled=false",
      "arena_ranking_enabled=false",
    ],
  },
  {
    route: "event-arena-first-alpha-slice-preview",
    title: "Event / Arena First Alpha Slice",
    qaPriority: "P1",
    exposureBadge: "ALPHA_MENU_EXPOSED",
    guardrails: [
      "db_writes=0",
      "matchmaking_live=false",
      "leaderboard_writes=false",
    ],
  },
];

export default function AlphaMenuPreview() {
  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.container}>
        <View style={styles.headerBlock}>
          <Text style={styles.header}>Alpha Preview Menu</Text>
          <Text style={styles.subHeader}>
            Sezione menu controllata per le preview alpha. Non e' una release
            commerciale. Nessun progresso reale, nessuna ricompensa, nessuna
            scrittura DB. Home e tab bar pubblici NON sono modificati.
          </Text>
        </View>

        <View style={styles.banner}>
          <Text style={styles.bannerTitle}>Stato exposure</Text>
          <Text style={styles.bannerLine}>apply: APPLIED_CONTROLLED_SAFE</Text>
          <Text style={styles.bannerLine}>route esposte: 7</Text>
          <Text style={styles.bannerLine}>home_root_changed: false</Text>
          <Text style={styles.bannerLine}>tab_bar_changed: false</Text>
          <Text style={styles.bannerLine}>db_writes: 0</Text>
          <Text style={styles.bannerLine}>broad_commercial_release: false</Text>
        </View>

        {ENTRIES.map((entry) => (
          <View key={entry.route} style={styles.card}>
            <View style={styles.cardHeaderRow}>
              <Text style={styles.cardTitle}>{entry.title}</Text>
              <View style={styles.priorityPill}>
                <Text style={styles.priorityText}>{entry.qaPriority}</Text>
              </View>
            </View>
            <Text style={styles.routeText}>{entry.route}</Text>
            <View style={styles.exposurePill}>
              <Text style={styles.exposureText}>{entry.exposureBadge}</Text>
            </View>
            <View style={styles.chipsRow}>
              {entry.guardrails.map((g) => (
                <View key={g} style={styles.chip}>
                  <Text style={styles.chipText}>{g}</Text>
                </View>
              ))}
            </View>
          </View>
        ))}

        <View style={styles.footer}>
          <Text style={styles.footerTitle}>Closed Alpha Kickoff</Text>
          <Text style={styles.footerLine}>
            Stato gate: ready_v74 - reclutamento manuale only. Nessun invito
            live. Nessuna scrittura account.
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: "#0b0f17" },
  container: { padding: 16, paddingBottom: 32 },
  headerBlock: { marginBottom: 16 },
  header: { color: "#ffffff", fontSize: 22, fontWeight: "700" },
  subHeader: { color: "#c2c8d4", fontSize: 13, marginTop: 6, lineHeight: 18 },
  banner: {
    backgroundColor: "#13202e",
    borderRadius: 10,
    padding: 12,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: "#1f2f44",
  },
  bannerTitle: { color: "#9fd5ff", fontWeight: "700", marginBottom: 6 },
  bannerLine: { color: "#dde6f2", fontSize: 12, marginVertical: 1 },
  card: {
    backgroundColor: "#101824",
    borderRadius: 10,
    padding: 12,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: "#1a2636",
  },
  cardHeaderRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  cardTitle: { color: "#ffffff", fontSize: 15, fontWeight: "600", flex: 1 },
  routeText: { color: "#8ea1bd", fontSize: 11, marginTop: 2 },
  priorityPill: {
    backgroundColor: "#1f2f44",
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 999,
    marginLeft: 8,
  },
  priorityText: { color: "#9fd5ff", fontSize: 10, fontWeight: "700" },
  exposurePill: {
    alignSelf: "flex-start",
    backgroundColor: "#1a3324",
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
    marginTop: 8,
  },
  exposureText: { color: "#8aedb1", fontSize: 10, fontWeight: "700" },
  chipsRow: { flexDirection: "row", flexWrap: "wrap", marginTop: 8 },
  chip: {
    backgroundColor: "#16202e",
    borderColor: "#243349",
    borderWidth: 1,
    borderRadius: 6,
    paddingHorizontal: 6,
    paddingVertical: 2,
    marginRight: 6,
    marginBottom: 6,
  },
  chipText: { color: "#c2c8d4", fontSize: 10 },
  footer: {
    marginTop: 8,
    padding: 12,
    backgroundColor: "#0f1822",
    borderRadius: 10,
    borderWidth: 1,
    borderColor: "#1a2636",
  },
  footerTitle: { color: "#ffd58a", fontWeight: "700" },
  footerLine: { color: "#dde6f2", fontSize: 12, marginTop: 4, lineHeight: 18 },
});
