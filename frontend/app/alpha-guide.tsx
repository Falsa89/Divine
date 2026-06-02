/**
 * frontend/app/alpha-guide.tsx
 *
 * v51 MEGA_RELEASE_ACCELERATION_1_PLAYABLE_ALPHA_FOUNDATION_PACK
 * Track E — Guide/Codex/Onboarding Alpha (static, deeplink-only).
 *
 * Static local content. No backend dependency. No home menu wiring.
 * No mutation. Italian text only. Clearly labeled alpha guide.
 */
import React from 'react';
import { View, Text, ScrollView, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

type Entry = { title: string; body: string };

const ENTRIES: Entry[] = [
  {
    title: 'Material Raid (Alpha)',
    body:
      'Modalità PvE pilota per il farming di materiali. In v51 è disponibile come slice alpha giocabile in sola preview: nessun reward viene effettivamente assegnato e nessun materiale viene aggiunto al tuo inventario.',
  },
  {
    title: 'Reward preview vs claim reale',
    body:
      "Le ricompense mostrate sono solo un'anteprima del design. Il claim reale arriverà con un pack dedicato di safety hardening (idempotency ledger, audit, rollback). Nessun reward live in questa fase.",
  },
  {
    title: 'Visual Battle policy',
    body:
      'Tutte le battaglie utente-visibili devono mostrare la battaglia visiva. La Guild War è l\'unica eccezione: autoresolve consentito ma con replay link obbligatorio. In Material Raid alpha la visual battle è required.',
  },
  {
    title: 'Asset placeholder vs final art',
    body:
      "Gli eroi mostrati in alpha possono usare placeholder grafici. L'import dell'art finale degli ~40 eroi seguirà lo schema di asset readiness definito in v51 (Track D).",
  },
  {
    title: 'Istruzioni per QA tester',
    body:
      "Esegui i flussi: boot, home, eroi, storia, battaglia visiva, report post-battle, Material Raid alpha, reward preview, guide/codex, navigazione/back/rotazione, performance. Segnala bug con severità P0/P1/P2/P3, evidenza screenshot/video, passi di riproduzione, info dispositivo.",
  },
  {
    title: 'Severità bug',
    body:
      'P0: crash o blocco totale. P1: feature core compromessa. P2: bug significativo aggirabile. P3: rifinitura/cosmetico.',
  },
  {
    title: 'Economy safety: dry-run vs live',
    body:
      "L'economia live (gacha rate, shop IAP, Battle Pass, VIP, claim materiali, BP Delta) resta bloccata. Tutto ciò che vedi in alpha è dry-run / preview. La promozione live richiede approvazione manuale esplicita dell'utente con frase di sign-off e checksum.",
  },
];

export default function AlphaGuideScreen() {
  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.headerCard}>
          <Text style={styles.title}>Guida Alpha</Text>
          <Text style={styles.subtitle}>v51 · GUIDE_CODEX_ONBOARDING_ALPHA_FOUNDATION</Text>
          <Text style={styles.warningText}>
            Questa è una guida statica per tester alpha. Nessun reward, nessuna mutazione.
          </Text>
        </View>
        {ENTRIES.map((e) => (
          <View key={e.title} style={styles.entryCard}>
            <Text style={styles.entryTitle}>{e.title}</Text>
            <Text style={styles.entryBody}>{e.body}</Text>
          </View>
        ))}
        <View style={styles.footerBox}>
          <Text style={styles.footerText}>
            v51 MEGA_RELEASE_ACCELERATION_1_PLAYABLE_ALPHA_FOUNDATION · deeplink-only
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
  title: { color: '#fff', fontSize: 22, fontWeight: '700' },
  subtitle: { color: '#9aa4b2', fontSize: 12, marginTop: 4, marginBottom: 8 },
  warningText: { color: '#e8c884', fontSize: 12 },
  entryCard: {
    backgroundColor: '#141a22',
    borderRadius: 12,
    padding: 14,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#222b36',
  },
  entryTitle: { color: '#fff', fontSize: 16, fontWeight: '700', marginBottom: 6 },
  entryBody: { color: '#cdd6e0', fontSize: 13, lineHeight: 19 },
  footerBox: { marginTop: 16, alignItems: 'center' },
  footerText: { color: '#5a6473', fontSize: 11 },
});
