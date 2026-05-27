// artifacts-preview.tsx — PROJECT_ARTIFACT_PREVIEW_UI_POPULATION
// READ-ONLY. Nessuna API mutativa, nessuna inventory, nessuna chiamata DB.
// Dataset: data/design/artifacts/preview/artifact_preview_dataset_v1.json (snapshot
// canonico inline; importer JSON deferito a stage successivo). 10 entries safe
// (no future_reserved, no legacy placeholder names).
//
// Compat note: questa schermata sostituisce la precedente griglia SafeFeatureCard
// (Project Y) e mantiene la copy banner v2 di Project Z:
// "Artefatti in anteprima \u2014 evocazione, import e bonus non ancora attivi."
import React, { useMemo, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  SafeAreaView,
  TouchableOpacity,
  StatusBar,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import { COLORS } from '../constants/theme';

// === Snapshot canonico inline (NON modificare a mano) ===
// Sorgente: /app/data/design/artifacts/preview/artifact_preview_dataset_v1.json
type PreviewEntry = {
  artifact_id: string;
  display_name_it: string;
  category: 'divine_relic' | 'sacred_symbol' | 'pantheon_emblem' | 'world_memory';
  rarity_band: 'rare' | 'epic' | 'legendary' | 'mythic' | 'divine';
  ui_copy_short_it: string;
  visual_hint: string;
};

const PREVIEW_ENTRIES: PreviewEntry[] = [
  { artifact_id: 'relic_aurora_eterna',        display_name_it: 'Aurora Eterna',              category: 'divine_relic',    rarity_band: 'legendary', ui_copy_short_it: 'Frammento della prima alba.',           visual_hint: 'cristallo dorato pulsante con halo solare' },
  { artifact_id: 'relic_calice_vespro',        display_name_it: 'Calice del Vespro',          category: 'divine_relic',    rarity_band: 'legendary', ui_copy_short_it: "Custodisce l'ultima luce del giorno.",  visual_hint: 'calice argentato con liquido luminescente blu-viola' },
  { artifact_id: 'relic_lacrima_oceano',       display_name_it: "Lacrima dell'Oceano",        category: 'divine_relic',    rarity_band: 'epic',      ui_copy_short_it: "Lacrima dell'oceano primordiale.",       visual_hint: 'goccia turchese sospesa in cornice corallina' },
  { artifact_id: 'relic_seme_albero_mondo',    display_name_it: "Seme dell'Albero del Mondo", category: 'divine_relic',    rarity_band: 'legendary', ui_copy_short_it: "Seme dell'asse del mondo.",              visual_hint: 'ghianda dorata con radici fluttuanti' },
  { artifact_id: 'relic_pluma_fenix',          display_name_it: 'Piuma di Fenice',            category: 'divine_relic',    rarity_band: 'epic',      ui_copy_short_it: 'Piuma che non si consuma.',              visual_hint: 'piuma rosso-oro che brilla pulsando' },
  { artifact_id: 'relic_scaglia_drago_antico', display_name_it: 'Scaglia del Drago Antico',   category: 'divine_relic',    rarity_band: 'epic',      ui_copy_short_it: 'Scaglia di un drago oltre il tempo.',    visual_hint: 'scaglia verde-oro iridescente' },
  { artifact_id: 'relic_sigillo_lunare',       display_name_it: 'Sigillo Lunare',             category: 'sacred_symbol',   rarity_band: 'epic',      ui_copy_short_it: 'Lega le maree alle fasi lunari.',        visual_hint: 'disco di madreperla con incisioni a crescenti concentrici' },
  { artifact_id: 'relic_mandala_otto_porte',   display_name_it: 'Mandala delle Otto Porte',   category: 'sacred_symbol',   rarity_band: 'epic',      ui_copy_short_it: 'Otto soglie tra i piani.',               visual_hint: 'disco mandala oro su sfondo blu profondo' },
  { artifact_id: 'relic_emblema_olimpo',       display_name_it: "Emblema dell'Olimpo",        category: 'pantheon_emblem', rarity_band: 'legendary', ui_copy_short_it: 'Emblema del consiglio olimpico.',        visual_hint: 'scudo dodecagonale con 12 simboli olimpici' },
  { artifact_id: 'relic_pagina_libro_perduto', display_name_it: 'Pagina del Libro Perduto',   category: 'world_memory',    rarity_band: 'epic',      ui_copy_short_it: 'Pagina di una storia non vissuta.',      visual_hint: 'pergamena ingiallita con inchiostro che cambia leggermente quando guardata' },
];

const CATEGORY_META: Record<PreviewEntry['category'], { label: string; icon: string; tint: string }> = {
  divine_relic:    { label: 'Reliquie Divine',  icon: '\u2728', tint: '#FFD700' },
  sacred_symbol:   { label: 'Simboli Sacri',    icon: '\u269C',  tint: '#88BBFF' },
  pantheon_emblem: { label: 'Emblemi Pantheon', icon: '\u2694',  tint: '#FF8844' },
  world_memory:    { label: 'Memorie del Mondo', icon: '\uD83D\uDCDC', tint: '#BBAA66' },
};

const RARITY_META: Record<PreviewEntry['rarity_band'], { stars: number; color: string }> = {
  rare:      { stars: 3, color: '#4488ff' },
  epic:      { stars: 4, color: '#aa44ff' },
  legendary: { stars: 5, color: '#ff8844' },
  mythic:    { stars: 6, color: '#ffd700' },
  divine:    { stars: 6, color: '#ffffff' },
};

const CATEGORY_FILTERS: Array<'all' | PreviewEntry['category']> = [
  'all', 'divine_relic', 'sacred_symbol', 'pantheon_emblem', 'world_memory',
];

export default function ArtifactsPreviewScreen() {
  const router = useRouter();
  const [filter, setFilter] = useState<'all' | PreviewEntry['category']>('all');

  const visibleEntries = useMemo(
    () => (filter === 'all' ? PREVIEW_ENTRIES : PREVIEW_ENTRIES.filter(e => e.category === filter)),
    [filter]
  );

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" />
      <LinearGradient
        colors={[COLORS.bgPrimary, COLORS.bgSecondary]}
        style={StyleSheet.absoluteFill}
      />

      <View style={styles.headerBar}>
        <TouchableOpacity
          onPress={() => router.back()}
          style={styles.backBtn}
          accessibilityLabel="Indietro"
          accessibilityRole="button"
        >
          <Text style={styles.backIcon}>{'\u2190'}</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Reliquie Divine</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.banner}>
          <Text style={styles.bannerIcon}>{'\uD83D\uDD12'}</Text>
          <Text style={styles.bannerTitle}>Sistema in preparazione</Text>
          <Text style={styles.bannerSubtitle}>
            Le Reliquie sono una collezione divina d&apos;account in preparazione.
            Sono distinte da Armi Divine, Equipaggiamento, Rune e Costellazioni.
            Niente di tutto questo &egrave; attivo al momento.
          </Text>
          <View style={styles.bannerNoLiveRow}>
            <Text style={styles.bannerNoLiveText}>
              Nessuna evocazione, equipaggiamento, fusione o craft &egrave; disponibile.
            </Text>
          </View>
        </View>

        <Text style={styles.sectionTitle}>Categorie</Text>
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.chipsRow}
        >
          {CATEGORY_FILTERS.map((cat) => {
            const isActive = filter === cat;
            const label = cat === 'all' ? 'Tutte' : CATEGORY_META[cat].label;
            return (
              <TouchableOpacity
                key={cat}
                onPress={() => setFilter(cat)}
                style={[styles.chip, isActive && styles.chipActive]}
                accessibilityRole="button"
                accessibilityLabel={`Filtra ${label}`}
              >
                <Text style={[styles.chipText, isActive && styles.chipTextActive]}>
                  {label}
                </Text>
              </TouchableOpacity>
            );
          })}
        </ScrollView>

        <Text style={styles.sectionTitle}>Anteprima Reliquie ({visibleEntries.length})</Text>

        {visibleEntries.map((e) => {
          const cm = CATEGORY_META[e.category];
          const rm = RARITY_META[e.rarity_band];
          return (
            <View key={e.artifact_id} style={[styles.card, { borderColor: cm.tint + '55' }]}>
              <View style={styles.cardHeader}>
                <Text style={styles.cardIcon}>{cm.icon}</Text>
                <View style={{ flex: 1 }}>
                  <Text style={styles.cardTitle}>{e.display_name_it}</Text>
                  <Text style={[styles.cardCategory, { color: cm.tint }]}>{cm.label}</Text>
                </View>
                <View style={styles.previewBadge}>
                  <Text style={styles.previewBadgeText}>ANTEPRIMA</Text>
                </View>
              </View>
              <Text style={[styles.cardRarity, { color: rm.color }]}>
                {'\u2605'.repeat(rm.stars)}
              </Text>
              <Text style={styles.cardLore}>{e.ui_copy_short_it}</Text>
              <Text style={styles.cardVisualHint}>{e.visual_hint}</Text>
              <View style={styles.statusRow}>
                <Text style={styles.statusDot}>{'\u25CF'}</Text>
                <Text style={styles.statusText}>Non ottenibile ora</Text>
              </View>
            </View>
          );
        })}

        <View style={styles.footerNote}>
          <Text style={styles.footerNoteText}>
            Artefatti in anteprima &mdash; evocazione, import e bonus non ancora attivi.
            Anteprima statica di design. Questa schermata non effettua chiamate API,
            non legge inventari, non scrive su database. Le Reliquie verranno
            introdotte in patch dedicata, via eventi e traguardi futuri (non IAP).
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
    width: 44,
    height: 44,
    borderRadius: 22,
    alignItems: 'center',
    justifyContent: 'center',
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
    backgroundColor: 'rgba(170,68,255,0.12)',
    borderWidth: 1,
    borderColor: 'rgba(170,68,255,0.35)',
    marginBottom: 20,
  },
  bannerIcon: { fontSize: 32 },
  bannerTitle: { color: COLORS.textPrimary, fontSize: 18, fontWeight: '800', marginTop: 8 },
  bannerSubtitle: {
    color: COLORS.textSecondary,
    fontSize: 13,
    marginTop: 8,
    textAlign: 'center',
    lineHeight: 18,
  },
  bannerNoLiveRow: {
    marginTop: 12,
    paddingHorizontal: 10,
    paddingVertical: 6,
    backgroundColor: 'rgba(255,200,100,0.12)',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: 'rgba(255,200,100,0.3)',
  },
  bannerNoLiveText: { color: '#FFC864', fontSize: 12, textAlign: 'center', fontWeight: '600' },
  sectionTitle: {
    color: COLORS.gold,
    fontSize: 14,
    fontWeight: '800',
    letterSpacing: 1,
    textTransform: 'uppercase',
    marginTop: 16,
    marginBottom: 10,
  },
  chipsRow: { paddingRight: 8, gap: 8 },
  chip: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 18,
    borderWidth: 1,
    borderColor: COLORS.borderLight,
    backgroundColor: COLORS.bgGlass,
    marginRight: 8,
    minHeight: 36,
    justifyContent: 'center',
  },
  chipActive: { backgroundColor: 'rgba(255,215,0,0.18)', borderColor: COLORS.gold },
  chipText: { color: COLORS.textSecondary, fontSize: 12, fontWeight: '700' },
  chipTextActive: { color: COLORS.gold },
  card: {
    padding: 14,
    borderRadius: 14,
    borderWidth: 1,
    backgroundColor: COLORS.bgGlass,
    marginBottom: 12,
  },
  cardHeader: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  cardIcon: { fontSize: 24 },
  cardTitle: { color: COLORS.textPrimary, fontSize: 16, fontWeight: '800' },
  cardCategory: { fontSize: 11, fontWeight: '700', letterSpacing: 0.5, marginTop: 2 },
  previewBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
    backgroundColor: 'rgba(170,68,255,0.25)',
    borderWidth: 1,
    borderColor: 'rgba(170,68,255,0.55)',
  },
  previewBadgeText: { color: '#D9B3FF', fontSize: 10, fontWeight: '800', letterSpacing: 0.8 },
  cardRarity: { marginTop: 8, fontSize: 12, letterSpacing: 1 },
  cardLore: { color: COLORS.textPrimary, fontSize: 13, marginTop: 6, lineHeight: 18 },
  cardVisualHint: { color: COLORS.textMuted, fontSize: 11, fontStyle: 'italic', marginTop: 6, lineHeight: 15 },
  statusRow: { flexDirection: 'row', alignItems: 'center', marginTop: 10, gap: 6 },
  statusDot: { color: '#FFC864', fontSize: 8 },
  statusText: { color: '#FFC864', fontSize: 11, fontWeight: '700', letterSpacing: 0.5 },
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
