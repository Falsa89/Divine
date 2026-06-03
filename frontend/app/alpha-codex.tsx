/**
 * frontend/app/alpha-codex.tsx
 *
 * v54 MEGA_RELEASE_ACCELERATION_MASTER_BATCH_EXECUTION_PLAN — Track E (Guide/Codex runtime plan)
 * STATIC, deeplink-only, NO backend, NO mutation, NO home menu mandatory routing.
 * Tutto il testo è in italiano.
 */
import React from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';

type CodexEntry = { id: string; title: string; body: string };

const ENTRIES: CodexEntry[] = [
  {
    id: 'material_raid_alpha_loop',
    title: 'Material Raid · Alpha Loop',
    body:
      "Material Raid Alpha è un loop preview-only. Apri Material Raid Alpha, esegui alpha_battle_preview, passa al Visual Preview e poi al Reward Summary Preview. Nessun materiale viene assegnato.",
  },
  {
    id: 'visual_preview',
    title: 'Visual Preview',
    body:
      "Il Visual Preview mostra l'esito della battaglia in modo non autoritativo: il risultato è solo illustrativo, nessuna scrittura su DB.",
  },
  {
    id: 'reward_preview_no_claim',
    title: 'Reward Preview senza riscossione',
    body:
      "La Reward Preview elenca i materiali potenziali. La riscossione live è disabilitata: nessun materiale viene aggiunto all'inventario. Il claim live arriverà con un pack futuro di safety hardening.",
  },
  {
    id: 'bug_reporting',
    title: 'Segnalazione bug',
    body:
      "Usa il template del Beta Tester Execution Kit: titolo, severity P0-P3, passi, atteso vs reale, device, screenshot. Per P0/P1 allega anche un breve video.",
  },
  {
    id: 'asset_placeholder_vs_final_art',
    title: 'Placeholder vs Final Art',
    body:
      "Alcune immagini eroe sono ancora placeholder. Lo scanner di import manifest segnala lo stato di ogni hero (ready_to_import, missing_required_asset, missing_optional_asset, needs_manual_review, rejected_wrong_contract). Nessuna copia di asset avviene a runtime.",
  },
];

export default function AlphaCodexScreen() {
  const router = useRouter();

  const onBack = () => {
    try {
      router.back();
    } catch {
      // noop fallback
    }
  };

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.headerCard}>
          <Text style={styles.title}>Alpha Codex</Text>
          <Text style={styles.subtitle}>
            v54 · Guida statica deeplink-only · Nessuna chiamata backend
          </Text>
        </View>

        {ENTRIES.map((e) => (
          <View key={e.id} style={styles.entryCard}>
            <Text style={styles.entryTitle}>{e.title}</Text>
            <Text style={styles.entryBody}>{e.body}</Text>
          </View>
        ))}

        <TouchableOpacity style={styles.primaryBtn} onPress={onBack}>
          <Text style={styles.primaryBtnText}>Indietro</Text>
        </TouchableOpacity>

        <View style={styles.footerBox}>
          <Text style={styles.footerText}>
            v54 MEGA_RELEASE_ACCELERATION_MASTER · deeplink-only · read-only · no claim
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#0c0f14' },
  scrollContent: { padding: 16, paddingBottom: 48 },
  headerCard: {
    backgroundColor: '#141a22',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#222b36',
  },
  title: { color: '#fff', fontSize: 20, fontWeight: '700' },
  subtitle: { color: '#9aa4b2', fontSize: 12, marginTop: 4 },
  entryCard: {
    backgroundColor: '#141a22',
    borderRadius: 12,
    padding: 14,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#222b36',
  },
  entryTitle: { color: '#fff', fontSize: 15, fontWeight: '700', marginBottom: 6 },
  entryBody: { color: '#cdd6e0', fontSize: 13, lineHeight: 19 },
  primaryBtn: {
    backgroundColor: '#3b6db5',
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: 'center',
    marginTop: 8,
    minHeight: 48,
  },
  primaryBtnText: { color: '#fff', fontSize: 16, fontWeight: '700' },
  footerBox: { marginTop: 24, alignItems: 'center' },
  footerText: { color: '#5a6473', fontSize: 11 },
});
