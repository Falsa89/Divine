/**
 * frontend/app/guide.tsx
 *
 * PROJECT_GUIDE_CODEX_AND_TUTORIAL_FOUNDATION_PACK
 * Sentinella: v19 PUBLIC_SYNC_TAG_RESYNC_v19_GUIDE_CODEX_AND_TUTORIAL
 *
 * Schermata Guida/Codex read-only.
 *  - lista categorie
 *  - filtro per categoria selezionata
 *  - lista entries della categoria con titolo + summary + sections
 *  - content_status: test_content
 *  - replace_before_release: true
 *
 * Vincoli:
 *  - read-only: NESSUNA mutation di gameplay/economy/server.
 *  - NO toccare _layout.tsx (route auto-rilevata da expo-router file-based).
 *  - NO toccare home menu in questo pack.
 *  - NO toccare Tower gameplay.
 *  - touch target >= 44pt.
 *  - safe area aware.
 */
import React, { useMemo, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  FlatList,
  Platform,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { router } from 'expo-router';
import {
  GUIDE_CATEGORIES,
  GUIDE_ENTRIES,
  GUIDE_CONTENT_STATUS,
  GUIDE_REPLACE_BEFORE_RELEASE,
  type GuideEntry,
} from '../constants/guideCodex';

// PROJECT_GUIDE_CODEX_AND_TUTORIAL_FOUNDATION marker:
// asset_status=test_content, audio_status=test_placeholder, replace_before_release=true.
const SCREEN_TAG = 'PROJECT_GUIDE_CODEX_AND_TUTORIAL_FOUNDATION/v19';

export default function GuideScreen() {
  const insets = useSafeAreaInsets();
  const [activeCategory, setActiveCategory] = useState<string>('getting_started');

  const visibleEntries = useMemo<GuideEntry[]>(
    () => GUIDE_ENTRIES.filter((e) => e.category === activeCategory).sort((a, b) => a.order - b.order),
    [activeCategory],
  );

  return (
    <View style={[styles.container, { paddingTop: insets.top, paddingBottom: insets.bottom }]}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity
          onPress={() => router.back()}
          style={styles.backBtn}
          accessibilityRole="button"
          accessibilityLabel="Torna indietro"
          hitSlop={{ top: 12, bottom: 12, left: 12, right: 12 }}
        >
          <Text style={styles.backText}>‹ Indietro</Text>
        </TouchableOpacity>
        <Text style={styles.title}>Guida / Codex</Text>
        <View style={styles.headerSpacer} />
      </View>

      {/* TEST badge */}
      <View style={styles.badgeRow}>
        <View style={styles.badge}>
          <Text style={styles.badgeText}>CONTENUTO DI TEST</Text>
        </View>
        {GUIDE_REPLACE_BEFORE_RELEASE ? (
          <View style={[styles.badge, styles.badgeWarn]}>
            <Text style={styles.badgeText}>SOSTITUIRE PRIMA DEL RILASCIO</Text>
          </View>
        ) : null}
      </View>

      <View style={styles.body}>
        {/* Sidebar categorie */}
        <ScrollView style={styles.sidebar} contentContainerStyle={styles.sidebarContent}>
          {GUIDE_CATEGORIES.map((cat) => {
            const active = cat.id === activeCategory;
            return (
              <TouchableOpacity
                key={cat.id}
                onPress={() => setActiveCategory(cat.id)}
                style={[styles.catBtn, active && styles.catBtnActive]}
                accessibilityRole="button"
                accessibilityLabel={`Categoria ${cat.label_it}`}
              >
                <Text style={[styles.catText, active && styles.catTextActive]}>{cat.label_it}</Text>
              </TouchableOpacity>
            );
          })}
        </ScrollView>

        {/* Lista entries della categoria */}
        <View style={styles.entriesPane}>
          <FlatList
            data={visibleEntries}
            keyExtractor={(it) => it.id}
            contentContainerStyle={styles.entriesContent}
            ListEmptyComponent={
              <View style={styles.emptyBox}>
                <Text style={styles.emptyText}>Nessuna voce in questa categoria (PLACEHOLDER).</Text>
              </View>
            }
            renderItem={({ item }) => (
              <View style={styles.entryCard}>
                <Text style={styles.entryTitle}>{item.title_it}</Text>
                <Text style={styles.entrySummary}>{item.summary_it}</Text>
                {item.sections.map((sec, idx) => (
                  <View key={`${item.id}-${idx}`} style={styles.entrySection}>
                    <Text style={styles.entrySectionHeading}>{sec.heading_it}</Text>
                    <Text style={styles.entrySectionBody}>{sec.body_it}</Text>
                  </View>
                ))}
              </View>
            )}
          />
        </View>
      </View>

      {/* Footer metadata (debug-friendly) */}
      <View style={styles.footer}>
        <Text style={styles.footerText}>
          {`tag=${SCREEN_TAG} | status=${GUIDE_CONTENT_STATUS}`}
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#080816' },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#1f1f33',
  },
  backBtn: { minHeight: 44, minWidth: 88, justifyContent: 'center' },
  backText: { color: '#9ea0c8', fontSize: 16, fontWeight: '600' },
  title: { color: '#fff', fontSize: 18, fontWeight: '700' },
  headerSpacer: { width: 88 },
  badgeRow: { flexDirection: 'row', gap: 8, paddingHorizontal: 16, paddingTop: 10 },
  badge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    backgroundColor: '#252540',
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#3a3a55',
  },
  badgeWarn: { backgroundColor: '#3a2a16', borderColor: '#6b4a1f' },
  badgeText: { color: '#d8d8f0', fontSize: 10, fontWeight: '700', letterSpacing: 0.5 },
  body: { flex: 1, flexDirection: 'row', paddingHorizontal: 12, paddingTop: 12 },
  sidebar: { width: 200, marginRight: 12 },
  sidebarContent: { paddingBottom: 24 },
  catBtn: {
    minHeight: 44,
    paddingHorizontal: 12,
    paddingVertical: 10,
    borderRadius: 8,
    marginBottom: 6,
    backgroundColor: '#141425',
    borderWidth: 1,
    borderColor: '#1f1f33',
  },
  catBtnActive: { backgroundColor: '#2a3070', borderColor: '#5b6df0' },
  catText: { color: '#a8aacc', fontSize: 14, fontWeight: '600' },
  catTextActive: { color: '#fff' },
  entriesPane: { flex: 1 },
  entriesContent: { paddingBottom: 32 },
  emptyBox: { padding: 24, alignItems: 'center' },
  emptyText: { color: '#7a7c9a', fontSize: 14 },
  entryCard: {
    backgroundColor: '#141425',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#2a2a44',
    padding: 16,
    marginBottom: 12,
  },
  entryTitle: { color: '#fff', fontSize: 18, fontWeight: '700', marginBottom: 4 },
  entrySummary: { color: '#bcbcd8', fontSize: 13, marginBottom: 10 },
  entrySection: { marginTop: 8, paddingTop: 8, borderTopWidth: 1, borderTopColor: '#22223a' },
  entrySectionHeading: { color: '#9eb0ff', fontSize: 14, fontWeight: '700', marginBottom: 4 },
  entrySectionBody: { color: '#dcdcef', fontSize: 13, lineHeight: 19 },
  footer: { paddingHorizontal: 16, paddingVertical: 8, borderTopWidth: 1, borderTopColor: '#1f1f33' },
  footerText: { color: '#5a5c7a', fontSize: 10, fontFamily: Platform.select({ ios: 'Menlo', android: 'monospace' }) },
});
