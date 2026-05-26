// SF_MERGE Track D \u2014 /economy retired as canonical surface.
//
// La logica utile (materiali, soul essence, anteprima negozio anime, regole)
// \u00e8 stata assorbita dentro la Soul Forge (\"Anime Hub\"). Questo file diventa
// una pagina informativa che reindirizza automaticamente a /soul-forge.
// Backend invariato. Nessuna chiamata mutativa.
import React, { useEffect } from 'react';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import { COLORS } from '../constants/theme';

export default function EconomyRetiredRedirect() {
  const router = useRouter();
  useEffect(() => {
    const t = setTimeout(() => router.replace('/soul-forge'), 50);
    return () => clearTimeout(t);
  }, [router]);
  return (
    <LinearGradient colors={[COLORS.bgPrimary, '#1A0A2E', '#0D0820']} style={styles.container}>
      <View style={styles.center}>
        <Text style={styles.icon}>{'\uD83D\uDD04'}</Text>
        <Text style={styles.title}>Economia trasferita</Text>
        <Text style={styles.subtitle}>
          La gestione di materiali Soul e anteprima negozio anime ora vive
          dentro la <Text style={styles.b}>Soul Forge</Text>.
        </Text>
        <ActivityIndicator color={COLORS.accent} style={{ marginTop: 14 }} />
        <Text style={styles.note}>Reindirizzamento a /soul-forge\u2026</Text>
      </View>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center', paddingHorizontal: 32 },
  icon: { fontSize: 48, marginBottom: 16 },
  title: { color: COLORS.textPrimary, fontSize: 18, fontWeight: '800', textAlign: 'center' },
  subtitle: { color: COLORS.textSecondary, fontSize: 13, marginTop: 8, textAlign: 'center', lineHeight: 20 },
  b: { color: '#C877FF', fontWeight: '800' },
  note: { color: COLORS.textMuted, fontSize: 11, marginTop: 16, textAlign: 'center', fontStyle: 'italic' },
});
