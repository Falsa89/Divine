// BATCH_1_V2 Track C \u2014 Artifact/Constellation Surface Lock
//
// La schermata legacy /artifacts esponeva pull/pull10/fuse/equip live senza
// gate. Finch\u00e9 l'Artifact Bible canonica + il gate di import non sono firmati,
// l'unica esperienza giocatore per artefatti/costellazioni deve essere la
// preview safe (read-only) gi\u00e0 esistente in /artifacts-preview.
//
// Comportamento: redirect immediato a /artifacts-preview.
// Nessuna API call, nessuna mutazione, nessun bottone live.
// Il file rimane in repo per coerenza con la cronologia; tutta la logica
// originale (pull/fuse/equip) viene resa irraggiungibile dal frontend.
//
// Backend route /api/artifacts/* invariati: nessuna API rimossa.
import React, { useEffect } from 'react';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import { COLORS } from '../constants/theme';

export default function ArtifactsLockedRedirectV2() {
  const router = useRouter();

  useEffect(() => {
    // Redirect non bloccante a preview safe.
    const t = setTimeout(() => {
      router.replace('/artifacts-preview');
    }, 50);
    return () => clearTimeout(t);
  }, [router]);

  return (
    <LinearGradient
      colors={[COLORS.bgPrimary, '#1A0A2E', '#0D0820']}
      style={styles.container}
    >
      <View style={styles.center}>
        <Text style={styles.icon}>{'\uD83D\uDD12'}</Text>
        <Text style={styles.title}>Artefatti & Costellazioni</Text>
        <Text style={styles.subtitle}>
          Apertura anteprima sicura\u2026
        </Text>
        <ActivityIndicator color={COLORS.accent} style={{ marginTop: 16 }} />
        <Text style={styles.note}>
          La schermata live legacy \u00e8 in revisione. Reindirizzamento a
          /artifacts-preview.
        </Text>
      </View>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  center: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 32,
  },
  icon: { fontSize: 48, marginBottom: 16 },
  title: {
    color: COLORS.textPrimary,
    fontSize: 18,
    fontWeight: '800',
    textAlign: 'center',
  },
  subtitle: {
    color: COLORS.textSecondary,
    fontSize: 14,
    marginTop: 8,
    textAlign: 'center',
  },
  note: {
    color: COLORS.textMuted,
    fontSize: 11,
    marginTop: 18,
    textAlign: 'center',
    fontStyle: 'italic',
    lineHeight: 16,
  },
});
