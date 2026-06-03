/**
 * frontend/app/training-visual-preview.tsx
 *
 * v55 MEGA_RELEASE_ACCELERATION_4_VISUAL_BATTLE_ROUTING_EXPANSION_PREVIEW — Track C
 * Training Visual Preview deeplink shell (STATIC + DEEPLINK-ONLY).
 *
 * NO home menu mandatory routing. NO backend. NO battle_engine.
 * NO reward. NO mutation. Safe sandbox.
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

export default function TrainingVisualPreviewScreen() {
  const router = useRouter();

  const openRouter = () => {
    try {
      router.push(
        '/visual-battle-preview-router?mode=training&source_route=training_visual_preview&battle_seed_preview=training-alpha-v55',
      );
    } catch {
      // noop fallback
    }
  };

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
          <Text style={styles.title}>Training Visual Preview</Text>
          <Text style={styles.subtitle}>v55 · safe sandbox · deeplink-only · static</Text>
          <View style={styles.warningBox}>
            <Text style={styles.warningText}>Preview visuale non autoritativa.</Text>
            <Text style={styles.warningText}>Nessun reward verrà assegnato.</Text>
            <Text style={styles.warningText}>Routing preview only.</Text>
          </View>
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Squadra (placeholder)</Text>
          <View style={styles.row}>
            {['A', 'B', 'C'].map((h) => (
              <View key={h} style={styles.slot}>
                <Text style={styles.slotText}>Eroe {h}</Text>
                <Text style={styles.slotSub}>placeholder</Text>
              </View>
            ))}
          </View>
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Nemico (placeholder)</Text>
          <View style={styles.row}>
            <View style={styles.slot}>
              <Text style={styles.slotText}>Bersaglio</Text>
              <Text style={styles.slotSub}>training_dummy</Text>
            </View>
          </View>
        </View>

        <View style={styles.guardsBox}>
          <Text style={styles.guardLine}>safe_sandbox = true</Text>
          <Text style={styles.guardLine}>result_authoritative = false</Text>
          <Text style={styles.guardLine}>reward_claim_enabled = false</Text>
          <Text style={styles.guardLine}>battle_engine_runtime_used = false</Text>
          <Text style={styles.guardLine}>db_writes = 0</Text>
        </View>

        <TouchableOpacity style={styles.primaryBtn} onPress={openRouter}>
          <Text style={styles.primaryBtnText}>Apri Visual Battle Preview Router</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.secondaryBtn} onPress={onBack}>
          <Text style={styles.secondaryBtnText}>Indietro</Text>
        </TouchableOpacity>

        <View style={styles.footerBox}>
          <Text style={styles.footerText}>
            v55 MEGA_RELEASE_ACCELERATION_4 · training preview · no claim · deeplink-only
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
  warningBox: {
    backgroundColor: '#3a2a14',
    borderRadius: 8,
    padding: 12,
    marginTop: 12,
    borderWidth: 1,
    borderColor: '#a07020',
  },
  warningText: { color: '#e8c884', fontSize: 12 },
  card: {
    backgroundColor: '#141a22',
    borderRadius: 12,
    padding: 14,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#222b36',
  },
  sectionTitle: { color: '#fff', fontSize: 15, fontWeight: '700', marginBottom: 8 },
  row: { flexDirection: 'row', justifyContent: 'space-between' },
  slot: {
    flex: 1,
    backgroundColor: '#1a212b',
    borderRadius: 8,
    padding: 12,
    marginRight: 8,
    borderWidth: 1,
    borderColor: '#2a3340',
    alignItems: 'center',
  },
  slotText: { color: '#cdd6e0', fontSize: 13, fontWeight: '600' },
  slotSub: { color: '#5a6473', fontSize: 11, marginTop: 2 },
  guardsBox: {
    backgroundColor: '#1a212b',
    borderRadius: 8,
    padding: 10,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#2a3340',
  },
  guardLine: { color: '#9aa4b2', fontSize: 12, marginBottom: 2 },
  primaryBtn: {
    backgroundColor: '#3b6db5',
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: 'center',
    marginTop: 4,
    minHeight: 48,
  },
  primaryBtnText: { color: '#fff', fontSize: 16, fontWeight: '700' },
  secondaryBtn: {
    backgroundColor: '#222b36',
    paddingVertical: 12,
    borderRadius: 10,
    alignItems: 'center',
    marginTop: 10,
    minHeight: 44,
  },
  secondaryBtnText: { color: '#cdd6e0', fontSize: 14, fontWeight: '600' },
  footerBox: { marginTop: 24, alignItems: 'center' },
  footerText: { color: '#5a6473', fontSize: 11 },
});
