// SF_MERGE Track E \u2014 /exclusive route legacy lock notice.
//
// La schermata /exclusive era stata creata in passato pensando erroneamente che
// le armi esclusive / Divine Weapons fossero craftabili da un'interfaccia
// generica di crafting. Questo NON \u00e8 corretto: le Divine Weapons sono
// character-bound (soprattutto nativi 6\u2605) e gestite da un sistema dedicato
// completamente separato dal vecchio /exclusive.
//
// Questo file diventa una pagina locked legacy con disclaimer chiaro.
// Nessuna chiamata API mutativa, nessun bottone craft.
import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import { COLORS } from '../constants/theme';

export default function ExclusiveLegacyLocked() {
  const router = useRouter();
  return (
    <LinearGradient colors={[COLORS.bgPrimary, '#1A0A2E', '#0D0820']} style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn} activeOpacity={0.7}>
          <Text style={styles.back}>{'\u2190'}</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Oggetti Esclusivi</Text>
      </View>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.lockCard}>
          <Text style={styles.lockIcon}>{'\uD83D\uDD12'}</Text>
          <Text style={styles.lockTitle}>Schermata legacy archiviata</Text>
          <Text style={styles.lockSubtitle}>
            La vecchia funzione \u201cOggetti Esclusivi\u201d non riflette pi{'\u00f9'} il design
            corrente. La modalit{'\u00e0'} \u00e8 disabilitata e non rappresenta lo stato
            canonico delle armi del gioco.
          </Text>

          <View style={styles.divider} />

          <Text style={styles.sectionTitle}>{'\u2728'} Cosa sono davvero le Divine Weapons</Text>
          <Text style={styles.bodyTxt}>
            Le <Text style={styles.b}>Divine Weapons</Text> sono armi
            <Text style={styles.b}> character-bound</Text>, legate stabilmente a un
            eroe specifico (in particolare ai <Text style={styles.b}>nativi 6{'\u2605'}</Text>).
          </Text>
          <Text style={styles.bodyTxt}>
            Non vengono <Text style={styles.b}>craftate</Text> da una schermata generica:
            sono gestite da un <Text style={styles.b}>sistema dedicato separato</Text>,
            allineato al Character Bible.
          </Text>

          <View style={styles.divider} />

          <Text style={styles.sectionTitle}>{'\uD83D\uDDFA\uFE0F'} Dove guardare invece</Text>
          <TouchableOpacity
            style={styles.cta}
            onPress={() => router.push('/divine-weapons-catalog')}
            activeOpacity={0.7}
          >
            <Text style={styles.ctaIcon}>{'\u2694\uFE0F'}</Text>
            <View style={{ flex: 1 }}>
              <Text style={styles.ctaTitle}>Catalogo Armi Divine</Text>
              <Text style={styles.ctaDesc}>Anteprima read-only delle armi attualmente progettate</Text>
            </View>
            <Text style={styles.ctaArrow}>{'\u203A'}</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.cta, { backgroundColor: 'rgba(153,68,255,0.10)', borderColor: 'rgba(153,68,255,0.45)' }]}
            onPress={() => router.push('/soul-forge')}
            activeOpacity={0.7}
          >
            <Text style={styles.ctaIcon}>{'\uD83D\uDD25'}</Text>
            <View style={{ flex: 1 }}>
              <Text style={[styles.ctaTitle, { color: '#C877FF' }]}>Soul Forge</Text>
              <Text style={[styles.ctaDesc, { color: 'rgba(200,119,255,0.7)' }]}>
                Sacrificio eroi + materiali anime canonici
              </Text>
            </View>
            <Text style={[styles.ctaArrow, { color: '#C877FF' }]}>{'\u203A'}</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  header: {
    flexDirection: 'row', alignItems: 'center',
    paddingHorizontal: 12, paddingTop: 12, paddingBottom: 8,
  },
  backBtn: { padding: 4 },
  back: { color: COLORS.textPrimary, fontSize: 22 },
  headerTitle: {
    flex: 1, textAlign: 'center', color: COLORS.textPrimary,
    fontSize: 16, fontWeight: '800', marginRight: 28,
  },
  scrollContent: { paddingHorizontal: 12, paddingBottom: 40 },
  lockCard: {
    padding: 16, borderRadius: 14,
    backgroundColor: 'rgba(0,0,0,0.30)',
    borderWidth: 1, borderColor: 'rgba(255,165,0,0.45)',
    gap: 6,
  },
  lockIcon: { fontSize: 36, textAlign: 'center', marginBottom: 4 },
  lockTitle: { color: '#FFB347', fontSize: 16, fontWeight: '900', textAlign: 'center' },
  lockSubtitle: {
    color: 'rgba(255,210,150,0.85)', fontSize: 12, lineHeight: 18,
    textAlign: 'center', marginTop: 4,
  },
  divider: { height: 1, backgroundColor: 'rgba(255,255,255,0.10)', marginVertical: 10 },
  sectionTitle: { color: COLORS.accent, fontSize: 12, fontWeight: '800', marginBottom: 4 },
  bodyTxt: { color: 'rgba(255,255,255,0.78)', fontSize: 11, lineHeight: 17, marginBottom: 6 },
  b: { color: '#fff', fontWeight: '800' },
  cta: {
    flexDirection: 'row', alignItems: 'center', gap: 10,
    padding: 12, borderRadius: 10, marginTop: 8,
    backgroundColor: 'rgba(255,215,0,0.08)',
    borderWidth: 1, borderColor: 'rgba(255,215,0,0.4)',
  },
  ctaIcon: { fontSize: 20 },
  ctaTitle: { color: '#FFD700', fontSize: 12, fontWeight: '900' },
  ctaDesc: { color: 'rgba(255,215,0,0.7)', fontSize: 9, marginTop: 2 },
  ctaArrow: { color: '#FFD700', fontSize: 20, fontWeight: '900' },
});
