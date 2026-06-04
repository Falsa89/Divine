// MEGA_RELEASE_ACCELERATION_36 v87 — Mobile QA Battle Preview Hub
//
// Scopo: punto di accesso DIRETTO da mobile (root-level: /mobile-qa-battle-preview)
// che fornisce 6 link diretti ai 6 mode preview, senza dover passare dall'alpha menu.
//
// Guardrail (assertito per design e per validator):
//   - preview-only, deterministic, NON authoritative
//   - nessun fetch backend, nessun DB write, nessun endpoint live
//   - nessun import del modulo di combattimento autoritativo
//   - nessun reward live, nessuna mutazione di account/inventory/MMR/tower-completion
//   - nessun bottone di claim reale
//   - label UI obbligatorie: QA ACCESS, PREVIEW ONLY, LOCAL PAYLOAD, NO LIVE REWARD, NON AUTHORITATIVE
//   - schermata NON esposta a produzione (deeplink-only, ma deeplink "corto" per mobile QA)
//
// UI in italiano. TypeScript-only.

import React from "react";
import {
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import { Link } from "expo-router";

type Mode = "training" | "story" | "boss" | "tower" | "event" | "arena";

const MODES: { mode: Mode; label: string; emoji: string; subtitle: string }[] = [
  { mode: "training", label: "Training", emoji: "🥋", subtitle: "Tank + healer + DPS vs 2 dummies (5 azioni)" },
  { mode: "story",    label: "Story",    emoji: "📖", subtitle: "3 eroi vs 2 grunt + 1 lieutenant (5 azioni)" },
  { mode: "boss",     label: "Boss",     emoji: "👹", subtitle: "4 eroi vs raid boss placeholder (6 azioni)" },
  { mode: "tower",    label: "Tower",    emoji: "🗼", subtitle: "3 eroi vs 3 minion piano demo (5 azioni)" },
  { mode: "event",    label: "Event",    emoji: "🎪", subtitle: "3 eroi vs 1 mob + 1 elite (5 azioni)" },
  { mode: "arena",    label: "Arena",    emoji: "⚔️", subtitle: "3 eroi vs 3 dummy PvP (5 azioni)" },
];

const REQUIRED_LABELS = ["QA ACCESS", "PREVIEW ONLY", "LOCAL PAYLOAD", "NO LIVE REWARD", "NON AUTHORITATIVE"];

export default function MobileQaBattlePreview() {
  return (
    <SafeAreaView style={styles.screen}>
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.h1}>Mobile QA · Battle Preview Hub</Text>
        <Text style={styles.subtitle}>
          Accesso rapido da mobile alle 6 modalità della Visual Battle Preview v86.
          Nessuna route reale, nessun reward, nessuna mutazione.
        </Text>

        <View style={styles.badgesRow}>
          {REQUIRED_LABELS.map((b) => (
            <View key={b} style={styles.badge}>
              <Text style={styles.badgeText}>{b}</Text>
            </View>
          ))}
        </View>

        <Text style={styles.sectionTitle}>Percorso mobile diretto</Text>
        <View style={styles.pathCard}>
          <Text style={styles.pathLine}>1. Apri l'app sul dispositivo (Expo Go o web preview)</Text>
          <Text style={styles.pathLine}>2. Vai a: <Text style={styles.mono}>/mobile-qa-battle-preview</Text></Text>
          <Text style={styles.pathLine}>3. Tocca una delle 6 modalità qui sotto</Text>
          <Text style={styles.pathLine}>4. Premi "Avvia battaglia preview ›" per la timeline turni</Text>
        </View>

        <Text style={styles.sectionTitle}>Modalità (preview locale deterministica)</Text>
        {MODES.map(({ mode, label, emoji, subtitle }) => (
          <Link
            key={mode}
            href={{ pathname: "/playable-mode-battle-preview", params: { mode } }}
            asChild
          >
            <TouchableOpacity style={styles.modeCard}>
              <Text style={styles.modeEmoji}>{emoji}</Text>
              <View style={styles.modeBody}>
                <Text style={styles.modeLabel}>{label}</Text>
                <Text style={styles.modeSubtitle}>{subtitle}</Text>
                <Text style={styles.modeRoute}>/playable-mode-battle-preview?mode={mode}</Text>
              </View>
              <Text style={styles.modeArrow}>›</Text>
            </TouchableOpacity>
          </Link>
        ))}

        <View style={styles.warnCard}>
          <Text style={styles.warnTitle}>Vincoli locali</Text>
          <Text style={styles.warnLine}>preview_only=true · deterministic=true · authoritative=false</Text>
          <Text style={styles.warnLine}>reward_grant=false · db_write=false · account_mutation=false</Text>
          <Text style={styles.warnLine}>inventory_mutation=false · battle_engine_attached=false</Text>
          <Text style={styles.warnLine}>NESSUN claim reale, NESSUN endpoint live, NESSUNA progressione.</Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: "#0d1117" },
  content: { padding: 16, paddingBottom: 48 },
  h1: { color: "#fff", fontSize: 22, fontWeight: "700", marginBottom: 6 },
  subtitle: { color: "#94a3b8", fontSize: 13, marginBottom: 12, lineHeight: 18 },
  sectionTitle: {
    color: "#cbd5e1",
    fontSize: 14,
    fontWeight: "700",
    marginTop: 18,
    marginBottom: 8,
    letterSpacing: 0.4,
    textTransform: "uppercase",
  },
  badgesRow: { flexDirection: "row", flexWrap: "wrap", marginBottom: 8 },
  badge: {
    backgroundColor: "#1f2937",
    borderColor: "#22d3ee",
    borderWidth: 1,
    borderRadius: 6,
    paddingHorizontal: 8,
    paddingVertical: 4,
    marginRight: 6,
    marginBottom: 6,
  },
  badgeText: { color: "#22d3ee", fontSize: 11, fontWeight: "700", letterSpacing: 0.6 },
  pathCard: {
    backgroundColor: "#0b1220",
    borderColor: "#1f2937",
    borderWidth: 1,
    borderRadius: 10,
    padding: 12,
    marginBottom: 4,
  },
  pathLine: { color: "#cbd5e1", fontSize: 13, marginBottom: 4 },
  mono: { color: "#a5f3fc", fontFamily: "Menlo", fontSize: 12 },
  modeCard: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#111827",
    borderColor: "#1f2937",
    borderWidth: 1,
    borderRadius: 12,
    paddingVertical: 14,
    paddingHorizontal: 14,
    marginBottom: 10,
    minHeight: 64, // touch target friendly
  },
  modeEmoji: { fontSize: 26, marginRight: 12 },
  modeBody: { flex: 1 },
  modeLabel: { color: "#fff", fontSize: 16, fontWeight: "700" },
  modeSubtitle: { color: "#94a3b8", fontSize: 12, marginTop: 2 },
  modeRoute: { color: "#22d3ee", fontSize: 11, fontFamily: "Menlo", marginTop: 4 },
  modeArrow: { color: "#94a3b8", fontSize: 28, marginLeft: 8 },
  warnCard: {
    backgroundColor: "#1c1917",
    borderColor: "#f97316",
    borderWidth: 1,
    borderRadius: 10,
    padding: 12,
    marginTop: 12,
    marginBottom: 4,
  },
  warnTitle: { color: "#fb923c", fontWeight: "700", marginBottom: 4 },
  warnLine: { color: "#fed7aa", fontSize: 12, marginBottom: 2 },
});
