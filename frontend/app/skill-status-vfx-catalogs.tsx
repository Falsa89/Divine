/**
 * RM1.25-D — Skill / Status / Icon / VFX Internal Catalog Browser UI
 * ─────────────────────────────────────────────────────────────────────────
 * Schermata mobile-first read-only per browser interno dei cataloghi
 * Skill/Status/Icon/VFX esposti dalla Read-Only Catalog API (RM1.25-C).
 *
 *  ⚠️ Cataloghi NON collegati al battle runtime. Nessuna attivazione
 *     skill/status/VFX/icone HP bar. Solo GET API, mai POST/PUT/PATCH/DELETE.
 *
 * 6 sezioni / tab:
 *   1. Summary           → counts + runtime flags=false
 *   2. Progressione Skill → 1★…6★ slot progression
 *   3. Status Effect     → 40 status, search locale
 *   4. Icone Status      → 40 icon metadata, search locale
 *   5. VFX Modulari      → 12 types + 163 entries, filter type + search
 *   6. Esempi Skill      → 4 examples, espandibili
 */
import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  Pressable,
  TextInput,
  TouchableOpacity,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Stack, useRouter } from 'expo-router';
import { apiCall } from '../utils/api';

const COLORS = {
  bg: '#0A0918',
  panel: '#16102E',
  panel2: '#1F1640',
  border: '#2A1F4E',
  text: '#F0E6FF',
  textMuted: '#88799A',
  textDim: '#6A5C82',
  gold: '#FFD700',
  blue: '#3D5AFE',
  green: '#44DD88',
  red: '#FF4466',
  orange: '#FF9E44',
  cyan: '#26C6DA',
  purple: '#AB47BC',
  yellow: '#FFE082',
};

const POLARITY_COLOR: Record<string, string> = {
  debuff: COLORS.red,
  buff: COLORS.green,
  control: COLORS.orange,
  neutral: COLORS.textMuted,
};

const CATEGORY_COLOR: Record<string, string> = {
  control: COLORS.orange,
  damage_over_time: COLORS.red,
  cleanse: COLORS.cyan,
  buff_offensive: COLORS.green,
  buff_defensive: COLORS.blue,
  debuff_defensive: COLORS.purple,
  utility: COLORS.gold,
};

const PRIORITY_COLOR: Record<string, string> = {
  critical: COLORS.red,
  high: COLORS.orange,
  medium: COLORS.gold,
  low: COLORS.textMuted,
};

type TabKey = 'summary' | 'progression' | 'status' | 'icons' | 'vfx' | 'examples';

const TABS: Array<{ key: TabKey; label: string; icon: string }> = [
  { key: 'summary',     label: 'Summary',     icon: '📊' },
  { key: 'progression', label: 'Skill',       icon: '⭐' },
  { key: 'status',      label: 'Status',      icon: '🌀' },
  { key: 'icons',       label: 'Icone',       icon: '🎯' },
  { key: 'vfx',         label: 'VFX',         icon: '✨' },
  { key: 'examples',    label: 'Esempi',      icon: '📜' },
];

type SummaryResp = {
  version?: string;
  official_elements?: string[];
  official_elements_count: number;
  core_statuses_count: number;
  status_icons_count: number;
  vfx_types_count: number;
  vfx_entries_count: number;
  skill_examples_count: number;
  battle_runtime_attached: boolean;
  ui_runtime_attached: boolean;
  source?: string;
  notes?: string;
};

type CatalogWrap<T> = { version?: string; name?: string; data: T;
  battle_runtime_attached?: boolean; ui_runtime_attached?: boolean; vfx_runtime_attached?: boolean };

export default function SkillStatusVfxCatalogsScreen() {
  const router = useRouter();
  const [tab, setTab] = useState<TabKey>('summary');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Cached responses (lazy per tab)
  const [summary, setSummary] = useState<SummaryResp | null>(null);
  const [progression, setProgression] = useState<any | null>(null);
  const [statuses, setStatuses] = useState<any | null>(null);
  const [icons, setIcons] = useState<any | null>(null);
  const [vfx, setVfx] = useState<any | null>(null);
  const [examples, setExamples] = useState<any | null>(null);

  // Search filters (per-tab local)
  const [qStatus, setQStatus] = useState('');
  const [qIcons, setQIcons] = useState('');
  const [qVfx, setQVfx] = useState('');
  const [vfxTypeFilter, setVfxTypeFilter] = useState<string | null>(null);
  const [expandedExample, setExpandedExample] = useState<string | null>(null);

  // Load summary once
  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        setLoading(true);
        const sum = await apiCall('/api/skill-status-vfx/catalogs/summary');
        if (!alive) return;
        setSummary(sum);
      } catch (e: any) {
        if (alive) setError(e?.message || 'Errore summary');
      } finally {
        if (alive) setLoading(false);
      }
    })();
    return () => { alive = false; };
  }, []);

  // Lazy-load per tab
  const ensureLoaded = useCallback(async (target: TabKey) => {
    try {
      if (target === 'progression' && !progression) {
        const r = await apiCall('/api/skill-status-vfx/catalogs/skill-progression');
        setProgression(r);
      } else if (target === 'status' && !statuses) {
        const r = await apiCall('/api/skill-status-vfx/catalogs/status-effects');
        setStatuses(r);
      } else if (target === 'icons' && !icons) {
        const r = await apiCall('/api/skill-status-vfx/catalogs/status-icons');
        setIcons(r);
      } else if (target === 'vfx' && !vfx) {
        const r = await apiCall('/api/skill-status-vfx/catalogs/vfx');
        setVfx(r);
      } else if (target === 'examples' && !examples) {
        const r = await apiCall('/api/skill-status-vfx/catalogs/skill-examples');
        setExamples(r);
      }
    } catch (e: any) {
      setError(e?.message || 'Errore caricamento sezione');
    }
  }, [progression, statuses, icons, vfx, examples]);

  useEffect(() => {
    if (tab !== 'summary') ensureLoaded(tab);
  }, [tab, ensureLoaded]);

  // ── Filtered slices (local search) ─────────────────────────────────
  const statusList = useMemo<any[]>(() => {
    const arr: any[] = statuses?.data?.statuses || [];
    const q = qStatus.trim().toLowerCase();
    if (!q) return arr;
    return arr.filter((s) =>
      String(s.status_id || '').toLowerCase().includes(q) ||
      String(s.display_name || '').toLowerCase().includes(q) ||
      String(s.category || '').toLowerCase().includes(q),
    );
  }, [statuses, qStatus]);

  const iconList = useMemo<any[]>(() => {
    const arr: any[] = icons?.data?.icons || [];
    const q = qIcons.trim().toLowerCase();
    if (!q) return arr;
    return arr.filter((i) =>
      String(i.status_id || '').toLowerCase().includes(q) ||
      String(i.icon_key || '').toLowerCase().includes(q) ||
      String(i.color_family || '').toLowerCase().includes(q) ||
      String(i.hp_bar_priority || '').toLowerCase().includes(q),
    );
  }, [icons, qIcons]);

  const vfxTypes: string[] = vfx?.data?.vfx_types || [];
  const vfxEntries = useMemo<any[]>(() => {
    const arr: any[] = vfx?.data?.vfx_entries || [];
    const q = qVfx.trim().toLowerCase();
    const filtered = vfxTypeFilter
      ? arr.filter((e) => e.type === vfxTypeFilter)
      : arr;
    if (!q) return filtered;
    return filtered.filter((e) =>
      String(e.vfx_id || '').toLowerCase().includes(q) ||
      String(e.type || '').toLowerCase().includes(q) ||
      String(e.status_id || '').toLowerCase().includes(q),
    );
  }, [vfx, qVfx, vfxTypeFilter]);

  // ── Render ─────────────────────────────────────────────────────────
  return (
    <SafeAreaView style={s.root}>
      <Stack.Screen options={{ title: 'Catalogo Skill & Status', headerShown: false }} />

      {/* Header */}
      <View style={s.header}>
        <Pressable onPress={() => router.back()} style={s.backBtn}>
          <Text style={s.backTxt}>← Indietro</Text>
        </Pressable>
        <Text style={s.title}>📚 Catalogo Skill & Status</Text>
        <View style={{ width: 70 }} />
      </View>

      {/* Banner read-only */}
      <View style={s.readonlyBanner}>
        <Text style={s.readonlyText}>
          ✦ Cataloghi <Text style={{ color: COLORS.gold, fontWeight: '900' }}>read-only</Text>,
          non collegati al runtime battaglia. UI di sola consultazione.
        </Text>
      </View>

      {/* Tab bar */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        style={s.tabBar}
        contentContainerStyle={s.tabBarContent}
      >
        {TABS.map((t) => (
          <TouchableOpacity
            key={t.key}
            onPress={() => setTab(t.key)}
            style={[s.tab, tab === t.key && s.tabActive]}
          >
            <Text style={[s.tabIcon]}>{t.icon}</Text>
            <Text style={[s.tabText, tab === t.key && s.tabTextActive]}>
              {t.label}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Content */}
      <ScrollView style={s.scroll} contentContainerStyle={s.scrollContent}>
        {error && (
          <View style={s.errorBox}>
            <Text style={s.errorTxt}>{error}</Text>
            <TouchableOpacity onPress={() => setError(null)} style={s.errorDismiss}>
              <Text style={{ color: COLORS.gold }}>Chiudi</Text>
            </TouchableOpacity>
          </View>
        )}

        {tab === 'summary' && (
          loading
            ? <Loader />
            : summary
              ? <SummaryView summary={summary} />
              : <Empty msg="Summary non disponibile" />
        )}

        {tab === 'progression' && (
          progression
            ? <ProgressionView data={progression?.data} />
            : <Loader />
        )}

        {tab === 'status' && (
          statuses
            ? (
              <>
                <SearchBar
                  placeholder="Cerca status (id, nome, categoria)…"
                  value={qStatus}
                  onChange={setQStatus}
                  count={statusList.length}
                  total={statuses?.data?.statuses?.length || 0}
                />
                {statusList.length === 0
                  ? <Empty msg="Nessuno status corrisponde alla ricerca" />
                  : statusList.map((st) => <StatusCard key={st.status_id} st={st} />)
                }
              </>
            )
            : <Loader />
        )}

        {tab === 'icons' && (
          icons
            ? (
              <>
                <SearchBar
                  placeholder="Cerca icone (id, key, color, priority)…"
                  value={qIcons}
                  onChange={setQIcons}
                  count={iconList.length}
                  total={icons?.data?.icons?.length || 0}
                />
                {iconList.length === 0
                  ? <Empty msg="Nessuna icona corrisponde alla ricerca" />
                  : iconList.map((ic) => <IconCard key={ic.icon_key} ic={ic} />)
                }
              </>
            )
            : <Loader />
        )}

        {tab === 'vfx' && (
          vfx
            ? (
              <>
                <View style={s.vfxTypesRow}>
                  <Text style={s.vfxTypesLabel}>VFX Types ({vfxTypes.length}):</Text>
                  <View style={s.vfxChipsRow}>
                    <TouchableOpacity
                      onPress={() => setVfxTypeFilter(null)}
                      style={[s.vfxChip, !vfxTypeFilter && s.vfxChipActive]}
                    >
                      <Text style={[s.vfxChipTxt, !vfxTypeFilter && s.vfxChipTxtActive]}>tutti</Text>
                    </TouchableOpacity>
                    {vfxTypes.map((t) => (
                      <TouchableOpacity
                        key={t}
                        onPress={() => setVfxTypeFilter(t)}
                        style={[s.vfxChip, vfxTypeFilter === t && s.vfxChipActive]}
                      >
                        <Text style={[s.vfxChipTxt, vfxTypeFilter === t && s.vfxChipTxtActive]}>
                          {t.replace('_vfx', '')}
                        </Text>
                      </TouchableOpacity>
                    ))}
                  </View>
                </View>
                <SearchBar
                  placeholder="Cerca VFX (id, type, status_id)…"
                  value={qVfx}
                  onChange={setQVfx}
                  count={vfxEntries.length}
                  total={vfx?.data?.vfx_entries?.length || 0}
                />
                {vfxEntries.length === 0
                  ? <Empty msg="Nessun VFX corrisponde al filtro" />
                  : vfxEntries.slice(0, 80).map((v, i) => (
                    <VfxCard key={(v.vfx_id || '') + '_' + i} v={v} />
                  ))
                }
                {vfxEntries.length > 80 && (
                  <Text style={s.truncateNote}>
                    Mostrati 80/{vfxEntries.length} risultati. Affina la ricerca per vedere altri.
                  </Text>
                )}
              </>
            )
            : <Loader />
        )}

        {tab === 'examples' && (
          examples
            ? ((examples?.data?.examples || []).length === 0
              ? <Empty msg="Nessun esempio disponibile" />
              : (examples?.data?.examples || []).map((ex: any) => (
                <ExampleCard
                  key={ex.example_id || ex.skill_id}
                  ex={ex}
                  expanded={expandedExample === (ex.example_id || ex.skill_id)}
                  onToggle={() => setExpandedExample(
                    expandedExample === (ex.example_id || ex.skill_id) ? null : (ex.example_id || ex.skill_id),
                  )}
                />
              ))
            )
            : <Loader />
        )}

        <View style={{ height: 40 }} />
      </ScrollView>
    </SafeAreaView>
  );
}

// ──────────────────────────────────────────────────────────────────────
// Subcomponents
// ──────────────────────────────────────────────────────────────────────
function Loader() {
  return (
    <View style={s.loaderWrap}>
      <ActivityIndicator color={COLORS.gold} />
      <Text style={s.loaderText}>Caricamento…</Text>
    </View>
  );
}

function Empty({ msg }: { msg: string }) {
  return (
    <View style={s.emptyWrap}>
      <Text style={s.emptyText}>{msg}</Text>
    </View>
  );
}

function SearchBar({
  placeholder, value, onChange, count, total,
}: {
  placeholder: string;
  value: string;
  onChange: (v: string) => void;
  count: number;
  total: number;
}) {
  return (
    <View style={s.searchWrap}>
      <TextInput
        value={value}
        onChangeText={onChange}
        placeholder={placeholder}
        placeholderTextColor={COLORS.textDim}
        style={s.searchInput}
        autoCorrect={false}
        autoCapitalize="none"
      />
      <Text style={s.searchCount}>{count}/{total}</Text>
    </View>
  );
}

function SummaryView({ summary }: { summary: SummaryResp }) {
  const items: Array<{ label: string; value: string | number; tone?: string }> = [
    { label: 'Elementi ufficiali', value: summary.official_elements_count },
    { label: 'Status core', value: summary.core_statuses_count },
    { label: 'Icone status', value: summary.status_icons_count },
    { label: 'VFX types', value: summary.vfx_types_count },
    { label: 'VFX entries', value: summary.vfx_entries_count },
    { label: 'Skill examples', value: summary.skill_examples_count },
  ];
  return (
    <>
      {!!summary.official_elements?.length && (
        <View style={s.elementsRow}>
          {summary.official_elements.map((el) => (
            <View key={el} style={s.elementChip}>
              <Text style={s.elementChipTxt}>{el}</Text>
            </View>
          ))}
        </View>
      )}
      <View style={s.summaryGrid}>
        {items.map((it) => (
          <View key={it.label} style={s.summaryCard}>
            <Text style={s.summaryValue}>{it.value}</Text>
            <Text style={s.summaryLabel}>{it.label}</Text>
          </View>
        ))}
      </View>

      <View style={s.runtimeFlagsBox}>
        <Text style={s.runtimeFlagsTitle}>Runtime flags</Text>
        <FlagRow label="battle_runtime_attached" value={summary.battle_runtime_attached} />
        <FlagRow label="ui_runtime_attached" value={summary.ui_runtime_attached} />
        <FlagRow label="vfx_runtime_attached" value={(summary as any).vfx_runtime_attached ?? false} />
        <Text style={s.runtimeFlagsNote}>
          Tutti i flag false: cataloghi non collegati al battle/UI/VFX runtime.
        </Text>
      </View>

      {!!summary.notes && (
        <View style={s.notesBox}>
          <Text style={s.notesTxt}>📌 {summary.notes}</Text>
        </View>
      )}
      {!!summary.source && (
        <Text style={s.sourceTxt}>Source: {summary.source}</Text>
      )}
    </>
  );
}

function FlagRow({ label, value }: { label: string; value: boolean }) {
  return (
    <View style={s.flagRow}>
      <Text style={s.flagLabel}>{label}</Text>
      <View style={[s.flagPill, { backgroundColor: value ? COLORS.green + '33' : COLORS.textDim + '22', borderColor: value ? COLORS.green : COLORS.textDim }]}>
        <Text style={[s.flagPillTxt, { color: value ? COLORS.green : COLORS.textDim }]}>
          {value ? 'true' : 'false'}
        </Text>
      </View>
    </View>
  );
}

function ProgressionView({ data }: { data: any }) {
  const byRarity: Record<string, string[]> = data?.official_skill_slots_by_native_rarity || {};
  const slotDefs: Record<string, any> = data?.slot_definitions || {};
  return (
    <View>
      <Text style={s.sectionHint}>
        Progressione slot skill per rarità nativa dell'eroe.
      </Text>
      {[1, 2, 3, 4, 5, 6].map((r) => {
        const slots = byRarity[String(r)] || [];
        return (
          <View key={r} style={s.rarityRow}>
            <View style={[s.rarityBadge, { borderColor: RARITY_COLORS[r] || COLORS.gold }]}>
              <Text style={[s.rarityBadgeTxt, { color: RARITY_COLORS[r] || COLORS.gold }]}>{r}★</Text>
            </View>
            <View style={s.slotsCol}>
              {slots.map((slot) => {
                const def = slotDefs[slot] || {};
                return (
                  <View key={slot} style={s.slotPill}>
                    <Text style={s.slotName}>{slot}</Text>
                    <Text style={s.slotType}>[{def.type || '?'}]</Text>
                    {!!def.description && (
                      <Text style={s.slotDesc} numberOfLines={2}>{def.description}</Text>
                    )}
                  </View>
                );
              })}
            </View>
          </View>
        );
      })}
      {!!data?.validator_rules?.length && (
        <View style={s.validatorBox}>
          <Text style={s.validatorTitle}>Validator rules ({data.validator_rules.length})</Text>
          {data.validator_rules.map((r: string, i: number) => (
            <Text key={i} style={s.validatorRule}>• {r}</Text>
          ))}
        </View>
      )}
    </View>
  );
}

const RARITY_COLORS: Record<number, string> = {
  1: '#88CC88', 2: '#44AAFF', 3: '#9966FF', 4: '#FFB347', 5: '#FF44CC', 6: '#FFD700',
};

function StatusCard({ st }: { st: any }) {
  const polColor = POLARITY_COLOR[st.polarity] || COLORS.textMuted;
  const catColor = CATEGORY_COLOR[st.category] || COLORS.textMuted;
  const isStackable = st.stacking?.is_stackable;
  const cleansable = st.cleanse_rules?.is_cleansable;
  const bossImmune = st.cleanse_rules?.boss_immune_to_apply ?? st.cleanse_rules?.boss_default_immunity;
  return (
    <View style={[s.card, { borderColor: polColor + '88' }]}>
      <View style={s.cardHeader}>
        <Text style={s.cardTitle}>{st.display_name || st.status_id}</Text>
        <Text style={s.cardId}>{st.status_id}</Text>
      </View>
      <View style={s.tagsRow}>
        <Tag label={st.polarity || 'n/a'} color={polColor} />
        <Tag label={st.category || 'n/a'} color={catColor} />
        {isStackable && <Tag label="stackable" color={COLORS.cyan} />}
        {cleansable === false && <Tag label="non-cleansable" color={COLORS.red} />}
        {cleansable === true && <Tag label="cleansable" color={COLORS.green} />}
        {bossImmune && <Tag label="boss-immune" color={COLORS.orange} />}
      </View>
      {!!st.runtime?.duration_type && (
        <Text style={s.cardSub}>
          Durata: {st.runtime.duration_type}{
            st.runtime.duration_turns ? ` (${st.runtime.duration_turns}t)` : ''
          }
          {st.runtime.tick_timing && st.runtime.tick_timing !== 'none'
            ? ` · tick: ${st.runtime.tick_timing}` : ''}
        </Text>
      )}
    </View>
  );
}

function IconCard({ ic }: { ic: any }) {
  const prio = ic.hp_bar_priority || 'medium';
  return (
    <View style={[s.card, { borderColor: (PRIORITY_COLOR[prio] || COLORS.textMuted) + '88' }]}>
      <View style={s.cardHeader}>
        <Text style={s.cardTitle}>{ic.status_id}</Text>
        <Text style={s.cardId}>{ic.icon_key}</Text>
      </View>
      <View style={s.tagsRow}>
        <Tag label={`prio: ${prio}`} color={PRIORITY_COLOR[prio] || COLORS.textMuted} />
        {!!ic.color_family && <Tag label={ic.color_family} color={COLORS.gold} />}
        {ic.show_stack_count && <Tag label="stack count" color={COLORS.cyan} />}
        {ic.show_duration && <Tag label="duration" color={COLORS.blue} />}
        {ic.no_text && <Tag label="no-text" color={COLORS.textMuted} />}
      </View>
      <Text style={s.cardSub}>
        {ic.master_size_px ? `${ic.master_size_px}px master` : ''}
        {ic.export_sizes_px ? ` · sizes: ${ic.export_sizes_px.join('/')}` : ''}
      </Text>
    </View>
  );
}

function VfxCard({ v }: { v: any }) {
  return (
    <View style={[s.card, { borderColor: COLORS.purple + '88' }]}>
      <View style={s.cardHeader}>
        <Text style={s.cardTitle}>{v.vfx_id}</Text>
        <Text style={s.cardId}>{v.type}</Text>
      </View>
      <View style={s.tagsRow}>
        {!!v.status_id && <Tag label={`→ ${v.status_id}`} color={COLORS.gold} />}
        {!!v.owner_scope && <Tag label={v.owner_scope} color={COLORS.blue} />}
        {!!v.duration_rule && <Tag label={v.duration_rule} color={COLORS.cyan} />}
        {!!v.intensity && <Tag label={`int: ${v.intensity}`} color={COLORS.orange} />}
      </View>
      {!!v.mobile_readability && (
        <Text style={s.cardSub}>
          📱 {v.mobile_readability.must_not_obscure_hp_bar ? 'no-obscure HP' : ''}
          {v.mobile_readability.must_not_obscure_status_icons ? ' · no-obscure icons' : ''}
        </Text>
      )}
    </View>
  );
}

function Tag({ label, color }: { label: string; color: string }) {
  return (
    <View style={[s.tag, { backgroundColor: color + '22', borderColor: color + '88' }]}>
      <Text style={[s.tagTxt, { color }]}>{label}</Text>
    </View>
  );
}

function ExampleCard({
  ex, expanded, onToggle,
}: { ex: any; expanded: boolean; onToggle: () => void }) {
  return (
    <Pressable onPress={onToggle} style={[s.card, { borderColor: COLORS.gold + '88' }]}>
      <View style={s.cardHeader}>
        <Text style={s.cardTitle}>{ex.display_name || ex.example_id}</Text>
        <Text style={s.cardId}>{ex.slot || '?'}</Text>
      </View>
      <View style={s.tagsRow}>
        {!!ex.hero_id && <Tag label={ex.hero_id} color={COLORS.cyan} />}
        {!!ex.element && <Tag label={ex.element} color={COLORS.orange} />}
        {!!ex.targeting?.side && <Tag label={ex.targeting.side} color={COLORS.gold} />}
      </View>
      <Text style={s.cardSub}>
        Target: {ex.targeting?.target_type || '?'} · {ex.targeting?.area_shape || '?'}
      </Text>
      {expanded && (
        <View style={s.expandedBox}>
          {!!ex.effects?.length && (
            <Text style={s.expandedLabel}>Effects ({ex.effects.length}):</Text>
          )}
          {(ex.effects || []).map((eff: any, i: number) => (
            <Text key={i} style={s.expandedLine}>
              • {eff.effect_type}{eff.status_id ? ` → ${eff.status_id}` : ''}{eff.target ? ` @${eff.target}` : ''}
            </Text>
          ))}
          {!!ex.presentation_flow && (
            <>
              <Text style={s.expandedLabel}>Presentation flow:</Text>
              {Object.keys(ex.presentation_flow).slice(0, 6).map((k) => (
                <Text key={k} style={s.expandedLine}>• {k}</Text>
              ))}
            </>
          )}
        </View>
      )}
      <Text style={s.expandHint}>{expanded ? '▼ Comprimi' : '▶ Espandi dettagli'}</Text>
    </Pressable>
  );
}

const s = StyleSheet.create({
  root: { flex: 1, backgroundColor: COLORS.bg },
  header: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    padding: 10, borderBottomWidth: 1, borderBottomColor: COLORS.border,
  },
  backBtn: { paddingVertical: 6, paddingHorizontal: 8 },
  backTxt: { color: COLORS.gold, fontSize: 13, fontWeight: '700' },
  title: { color: COLORS.gold, fontSize: 15, fontWeight: '900', letterSpacing: 0.3 },

  readonlyBanner: {
    backgroundColor: '#FFD70010',
    borderBottomWidth: 1,
    borderBottomColor: COLORS.gold + '40',
    paddingVertical: 6,
    paddingHorizontal: 12,
  },
  readonlyText: { color: COLORS.textMuted, fontSize: 11, lineHeight: 14 },

  tabBar: { maxHeight: 56, borderBottomWidth: 1, borderBottomColor: COLORS.border, flexGrow: 0 },
  tabBarContent: { paddingHorizontal: 8, paddingVertical: 6, gap: 6, alignItems: 'center' },
  tab: {
    flexDirection: 'row', alignItems: 'center', gap: 4,
    paddingHorizontal: 10, paddingVertical: 6, borderRadius: 18,
    backgroundColor: COLORS.panel, borderWidth: 1, borderColor: COLORS.border,
  },
  tabActive: { backgroundColor: COLORS.gold + '22', borderColor: COLORS.gold },
  tabIcon: { fontSize: 13 },
  tabText: { color: COLORS.textMuted, fontSize: 11, fontWeight: '700' },
  tabTextActive: { color: COLORS.gold },

  scroll: { flex: 1 },
  scrollContent: { padding: 12, gap: 8 },

  errorBox: { backgroundColor: '#FF000020', borderColor: '#FF0000', borderWidth: 1, borderRadius: 8, padding: 10, marginBottom: 10, flexDirection: 'row', justifyContent: 'space-between' },
  errorTxt: { color: '#FF8888', flex: 1 },
  errorDismiss: { padding: 4 },

  loaderWrap: { padding: 30, alignItems: 'center', gap: 8 },
  loaderText: { color: COLORS.textMuted },

  emptyWrap: { padding: 24, alignItems: 'center' },
  emptyText: { color: COLORS.textDim, fontStyle: 'italic' },

  // Summary
  elementsRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 6, marginBottom: 10 },
  elementChip: { backgroundColor: COLORS.gold + '15', borderColor: COLORS.gold + '50', borderWidth: 1, paddingHorizontal: 8, paddingVertical: 3, borderRadius: 12 },
  elementChipTxt: { color: COLORS.gold, fontSize: 10, fontWeight: '800' },
  summaryGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  summaryCard: {
    flexBasis: '47%', flexGrow: 1,
    backgroundColor: COLORS.panel, borderColor: COLORS.border, borderWidth: 1,
    borderRadius: 10, padding: 12, alignItems: 'center',
  },
  summaryValue: { color: COLORS.gold, fontSize: 24, fontWeight: '900' },
  summaryLabel: { color: COLORS.textMuted, fontSize: 11, marginTop: 4, textAlign: 'center' },

  runtimeFlagsBox: { backgroundColor: COLORS.panel2, borderRadius: 10, padding: 12, marginTop: 10, borderColor: COLORS.border, borderWidth: 1 },
  runtimeFlagsTitle: { color: COLORS.text, fontSize: 12, fontWeight: '900', marginBottom: 8, letterSpacing: 0.5 },
  flagRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginVertical: 3 },
  flagLabel: { color: COLORS.textMuted, fontSize: 11 },
  flagPill: { paddingHorizontal: 8, paddingVertical: 2, borderRadius: 8, borderWidth: 1 },
  flagPillTxt: { fontSize: 10, fontWeight: '800' },
  runtimeFlagsNote: { color: COLORS.textDim, fontSize: 10, marginTop: 8, fontStyle: 'italic' },

  notesBox: { backgroundColor: COLORS.panel, borderRadius: 8, padding: 10, marginTop: 8, borderColor: COLORS.border, borderWidth: 1 },
  notesTxt: { color: COLORS.textMuted, fontSize: 10, lineHeight: 14 },
  sourceTxt: { color: COLORS.textDim, fontSize: 9, marginTop: 6, fontStyle: 'italic' },

  // Search
  searchWrap: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 8 },
  searchInput: {
    flex: 1, backgroundColor: COLORS.panel, borderColor: COLORS.border, borderWidth: 1,
    borderRadius: 8, paddingHorizontal: 12, paddingVertical: 8, color: COLORS.text, fontSize: 13,
  },
  searchCount: { color: COLORS.textMuted, fontSize: 11, fontWeight: '700', minWidth: 50, textAlign: 'right' },

  // Generic card
  card: {
    backgroundColor: COLORS.panel, borderRadius: 10, padding: 10,
    borderWidth: 1, marginBottom: 6,
  },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 },
  cardTitle: { color: COLORS.text, fontSize: 13, fontWeight: '800', flex: 1 },
  cardId: { color: COLORS.textDim, fontSize: 10, fontFamily: 'monospace' },
  cardSub: { color: COLORS.textMuted, fontSize: 11, marginTop: 4 },
  tagsRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 4, marginTop: 2 },
  tag: { paddingHorizontal: 6, paddingVertical: 2, borderRadius: 6, borderWidth: 1 },
  tagTxt: { fontSize: 9, fontWeight: '700' },

  // VFX
  vfxTypesRow: { marginBottom: 6 },
  vfxTypesLabel: { color: COLORS.textMuted, fontSize: 11, marginBottom: 6 },
  vfxChipsRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 4 },
  vfxChip: { paddingHorizontal: 7, paddingVertical: 3, borderRadius: 12, backgroundColor: COLORS.panel, borderWidth: 1, borderColor: COLORS.border },
  vfxChipActive: { backgroundColor: COLORS.gold + '22', borderColor: COLORS.gold },
  vfxChipTxt: { color: COLORS.textMuted, fontSize: 9, fontWeight: '700' },
  vfxChipTxtActive: { color: COLORS.gold },
  truncateNote: { color: COLORS.textDim, fontSize: 10, textAlign: 'center', marginTop: 8, fontStyle: 'italic' },

  // Progression
  sectionHint: { color: COLORS.textMuted, fontSize: 11, marginBottom: 8 },
  rarityRow: { flexDirection: 'row', gap: 10, marginBottom: 10, alignItems: 'flex-start' },
  rarityBadge: { borderWidth: 2, borderRadius: 20, paddingHorizontal: 10, paddingVertical: 6, minWidth: 40, alignItems: 'center' },
  rarityBadgeTxt: { fontSize: 13, fontWeight: '900' },
  slotsCol: { flex: 1, gap: 4 },
  slotPill: { backgroundColor: COLORS.panel, borderColor: COLORS.border, borderWidth: 1, borderRadius: 8, padding: 8 },
  slotName: { color: COLORS.gold, fontSize: 12, fontWeight: '800' },
  slotType: { color: COLORS.cyan, fontSize: 9, fontFamily: 'monospace' },
  slotDesc: { color: COLORS.textMuted, fontSize: 10, marginTop: 2 },
  validatorBox: { backgroundColor: COLORS.panel2, borderColor: COLORS.border, borderWidth: 1, borderRadius: 8, padding: 10, marginTop: 8 },
  validatorTitle: { color: COLORS.text, fontSize: 11, fontWeight: '800', marginBottom: 6 },
  validatorRule: { color: COLORS.textMuted, fontSize: 10, lineHeight: 14 },

  // Examples
  expandedBox: { marginTop: 8, paddingTop: 8, borderTopColor: COLORS.border, borderTopWidth: 1 },
  expandedLabel: { color: COLORS.text, fontSize: 11, fontWeight: '800', marginTop: 4, marginBottom: 2 },
  expandedLine: { color: COLORS.textMuted, fontSize: 10, lineHeight: 14 },
  expandHint: { color: COLORS.gold, fontSize: 10, marginTop: 8, textAlign: 'right' },
});
