// daily-hub.tsx — PROJECT_FRONTEND_C Track B
// Daily Hub / Guida Giornaliera: aggregatore SAFE che mostra link a sezioni
// esistenti (mail, eventi, achievement, battle pass). NESSUN claim diretto.
// Nessun endpoint mutativo. Solo router.push verso route esistenti.
import React from 'react';
import { View, Text, StyleSheet, ScrollView, SafeAreaView, TouchableOpacity, StatusBar } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import { COLORS } from '../constants/theme';

type DailyEntry = {
  id: string;
  title: string;
  subtitle: string;
  icon: string;
  route: string | null;
  status: 'link_ready' | 'read_only_status' | 'disabled_locked';
  badge: string;
};

const ENTRIES: DailyEntry[] = [
  {
    id: 'mail',
    title: 'Posta',
    subtitle: 'Apri la posta per visualizzare e gestire i messaggi e le ricompense in arrivo.',
    icon: '\u2709\uFE0F',
    route: '/mail',
    status: 'link_ready',
    badge: 'Apri',
  },
  {
    id: 'events',
    title: 'Eventi Giornalieri',
    subtitle: 'Sfide e attivit\u00e0 a tempo. Apri la sezione eventi per vedere lo stato.',
    icon: '\uD83D\uDCC5',
    route: '/events',
    status: 'link_ready',
    badge: 'Apri',
  },
  {
    id: 'achievements',
    title: 'Achievement',
    subtitle: 'Traguardi a lungo termine. Apri la sezione per consultare il progresso.',
    icon: '\uD83C\uDFC6',
    route: '/achievements',
    status: 'link_ready',
    badge: 'Apri',
  },
  {
    id: 'battlepass',
    title: 'Battle Pass',
    subtitle: 'Progressione stagionale. Apri il Battle Pass per i tier sbloccati.',
    icon: '\uD83C\uDF96\uFE0F',
    route: '/battlepass',
    status: 'link_ready',
    badge: 'Apri',
  },
  {
    id: 'shop',
    title: 'Negozio',
    subtitle: 'Bundle e offerte. Le ricompense giornaliere gratuite si trovano nel negozio.',
    icon: '\uD83D\uDED2',
    route: '/shop',
    status: 'link_ready',
    badge: 'Apri',
  },
];

export default function DailyHubScreen() {
  const router = useRouter();

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" />
      <LinearGradient colors={[COLORS.bgPrimary, COLORS.bgSecondary]} style={StyleSheet.absoluteFill} />
      <View style={styles.headerBar}>
        <TouchableOpacity
          onPress={() => router.back()}
          style={styles.backBtn}
          accessibilityLabel="Indietro"
          accessibilityRole="button"
        >
          <Text style={styles.backIcon}>{'\u2190'}</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Guida Giornaliera</Text>
        <View style={{ width: 40 }} />
      </View>
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.banner}>
          <Text style={styles.bannerIcon}>{'\uD83D\uDCCB'}</Text>
          <Text style={styles.bannerTitle}>La tua giornata in un colpo d'occhio</Text>
          <Text style={styles.bannerSubtitle}>
            Apri le sezioni per consultare e gestire le tue attivit\u00e0 quotidiane. Nessuna ricompensa viene riscattata da qui.
          </Text>
        </View>

        {ENTRIES.map((e) => {
          const disabled = e.status === 'disabled_locked' || !e.route;
          const Wrapper: any = disabled ? View : TouchableOpacity;
          const wrapProps: any = disabled
            ? {}
            : {
                activeOpacity: 0.85,
                onPress: () => router.push(e.route as any),
                accessibilityRole: 'link',
                accessibilityLabel: `${e.title}: apri sezione`,
                accessibilityHint: 'Apre la pagina dedicata',
              };
          return (
            <Wrapper key={e.id} style={[styles.card, disabled && styles.cardDisabled]} {...wrapProps}>
              <View style={styles.cardRow}>
                <Text style={styles.cardIcon}>{e.icon}</Text>
                <View style={styles.cardBody}>
                  <Text style={styles.cardTitle}>{e.title}</Text>
                  <Text style={styles.cardSubtitle} numberOfLines={3}>
                    {e.subtitle}
                  </Text>
                </View>
                <View style={[styles.badge, disabled && styles.badgeDisabled]}>
                  <Text style={styles.badgeText}>{e.badge}</Text>
                </View>
              </View>
            </Wrapper>
          );
        })}

        <View style={styles.footerNote}>
          <Text style={styles.footerNoteText}>
            Questa schermata \u00e8 un aggregatore. Nessun claim avviene qui: per riscattare ricompense
            usa direttamente la sezione dedicata (Posta, Eventi, Achievement, Battle Pass, Negozio).
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.bgPrimary },
  headerBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 12,
    paddingTop: 8,
    paddingBottom: 12,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.borderLight,
  },
  backBtn: {
    width: 40, height: 40, borderRadius: 20,
    alignItems: 'center', justifyContent: 'center',
    backgroundColor: COLORS.bgGlass,
  },
  backIcon: { color: COLORS.textPrimary, fontSize: 22, fontWeight: '700' },
  headerTitle: { color: COLORS.textPrimary, fontSize: 18, fontWeight: '800', letterSpacing: 0.5 },
  scroll: { flex: 1 },
  scrollContent: { padding: 16, paddingBottom: 80 },
  banner: {
    alignItems: 'center',
    padding: 20,
    borderRadius: 16,
    backgroundColor: 'rgba(61,90,254,0.10)',
    borderWidth: 1,
    borderColor: 'rgba(61,90,254,0.35)',
    marginBottom: 16,
  },
  bannerIcon: { fontSize: 36 },
  bannerTitle: { color: COLORS.textPrimary, fontSize: 18, fontWeight: '800', marginTop: 8, textAlign: 'center' },
  bannerSubtitle: { color: COLORS.textSecondary, fontSize: 13, marginTop: 6, textAlign: 'center', lineHeight: 18 },
  card: {
    borderRadius: 14,
    padding: 14,
    marginBottom: 10,
    backgroundColor: COLORS.bgGlass,
    borderWidth: 1,
    borderColor: COLORS.borderLight,
    minHeight: 92,
  },
  cardDisabled: { opacity: 0.55 },
  cardRow: { flexDirection: 'row', alignItems: 'center' },
  cardIcon: { fontSize: 28, marginRight: 12, width: 36, textAlign: 'center' },
  cardBody: { flex: 1, paddingRight: 8 },
  cardTitle: { color: COLORS.textPrimary, fontSize: 16, fontWeight: '700' },
  cardSubtitle: { color: COLORS.textSecondary, fontSize: 12, marginTop: 4, lineHeight: 17 },
  badge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 999,
    backgroundColor: COLORS.accent,
  },
  badgeDisabled: { backgroundColor: COLORS.bgGlass, borderWidth: 1, borderColor: COLORS.borderLight },
  badgeText: { color: '#1a1a1a', fontSize: 11, fontWeight: '800', letterSpacing: 0.5 },
  footerNote: {
    marginTop: 16,
    padding: 14,
    borderRadius: 12,
    backgroundColor: COLORS.bgGlass,
    borderWidth: 1,
    borderColor: COLORS.borderLight,
  },
  footerNoteText: { color: COLORS.textMuted, fontSize: 12, fontStyle: 'italic', lineHeight: 16 },
});
