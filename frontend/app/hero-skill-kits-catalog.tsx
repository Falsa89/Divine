/**
 * RM1.26-D — Hero Skill Kit Browser UI Extension
 * ─────────────────────────────────────────────────────────────────────────
 * Schermata mobile-first read-only per browser interno dei cataloghi
 * Hero Skill Kit 5★/6★ esposti dalla Read-Only API (RM1.26-C).
 *
 * ⚠️ Cataloghi NON collegati al battle runtime / HP bar / VFX runtime.
 *    Solo GET API, mai POST/PUT/PATCH/DELETE.
 *    Solo lookup remoti via /api/hero-skill-kits/catalogs/*.
 *
 * 5 sezioni / tab:
 *   1. Summary    → counts + runtime flags=false
 *   2. 5★         → 20 entries, evidenzia legacy_ultimate→skill_2 + passive_advanced TODO
 *   3. 6★         → 13 entries (12 launch_base + 1 Borea extra_premium)
 *   4. Cerca      → input by-hero lookup con submit manuale
 *   5. Schema     → metadata + slot progression + final_numbers note
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
  magenta: '#FF44CC',
};

const ELEMENT_COLOR: Record<string, string> = {
  fire: '#FF6B55', water: '#3FA9F5', earth: '#A37A44', wind: '#7BD3FA', air: '#7BD3FA',
  lightning: '#FFD93D', light: '#FFE9A0', dark: '#7B5BC0', ice: '#9FE6FF',
  nature: '#7CD68A', arcane: '#C285FF',
};

type TabKey = 'summary' | '5star' | '6star' | 'search' | 'schema';
const TABS: Array<{ key: TabKey; label: string; icon: string }> = [
  { key: 'summary', label: 'Summary', icon: '📊' },
  { key: '5star',   label: '5★',      icon: '⭐' },
  { key: '6star',   label: '6★',      icon: '✨' },
  { key: 'search',  label: 'Cerca',   icon: '🔎' },
  { key: 'schema',  label: 'Schema',  icon: '📋' },
];

type Summary = {
  five_star_entries_count: number;
  six_star_launch_base_entries_count: number;
  six_star_extra_premium_entries_count: number;
  six_star_total_entries_count: number;
  total_catalog_entries_count: number;
  runtime_attached: boolean;
  battle_runtime_attached: boolean;
  ui_runtime_attached: boolean;
  hp_bar_runtime_attached: boolean;
  balance_values_finalized: boolean;
  do_not_treat_as_live_kit: boolean;
  notes?: string;
  source_directory?: string;
  catalog_metadata?: any;
};

export default function HeroSkillKitsCatalogScreen() {
  const router = useRouter();
  const [tab, setTab] = useState<TabKey>('summary');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [summary, setSummary] = useState<Summary | null>(null);
  const [fiveStar, setFiveStar] = useState<any | null>(null);
  const [sixStar, setSixStar] = useState<any | null>(null);
  const [schema, setSchema] = useState<any | null>(null);

  // Search local-only filter on 5★/6★ lists
  const [q5, setQ5] = useState('');
  const [q6, setQ6] = useState('');

  // By-hero remote lookup (manual submit, no spam)
  const [byHeroInput, setByHeroInput] = useState('');
  const [byHeroResult, setByHeroResult] = useState<any | null>(null);
  const [byHeroError, setByHeroError] = useState<string | null>(null);
  const [byHeroLoading, setByHeroLoading] = useState(false);

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        setLoading(true);
        const s = await apiCall('/api/hero-skill-kits/catalogs/summary');
        if (alive) setSummary(s);
      } catch (e: any) {
        if (alive) setError(e?.message || 'Errore summary');
      } finally {
        if (alive) setLoading(false);
      }
    })();
    return () => { alive = false; };
  }, []);

  const ensure = useCallback(async (target: TabKey) => {
    try {
      if (target === '5star' && !fiveStar) {
        setFiveStar(await apiCall('/api/hero-skill-kits/catalogs/5star'));
      } else if (target === '6star' && !sixStar) {
        setSixStar(await apiCall('/api/hero-skill-kits/catalogs/6star'));
      } else if (target === 'schema' && !schema) {
        setSchema(await apiCall('/api/hero-skill-kits/catalogs/schema'));
      }
    } catch (e: any) {
      setError(e?.message || 'Errore caricamento sezione');
    }
  }, [fiveStar, sixStar, schema]);

  useEffect(() => {
    if (tab !== 'summary' && tab !== 'search') ensure(tab);
  }, [tab, ensure]);

  // Filtered lists
  const fiveStarFiltered = useMemo<any[]>(() => {
    const arr: any[] = fiveStar?.entries || [];
    const q = q5.trim().toLowerCase();
    if (!q) return arr;
    return arr.filter((e) =>
      String(e.hero_id || '').toLowerCase().includes(q) ||
      String(e.display_name || '').toLowerCase().includes(q) ||
      String(e.element || '').toLowerCase().includes(q) ||
      String(e.role || '').toLowerCase().includes(q),
    );
  }, [fiveStar, q5]);

  const sixStarFiltered = useMemo<any[]>(() => {
    const arr: any[] = sixStar?.entries || [];
    const q = q6.trim().toLowerCase();
    if (!q) return arr;
    return arr.filter((e) =>
      String(e.hero_id || '').toLowerCase().includes(q) ||
      String(e.display_name || '').toLowerCase().includes(q) ||
      String(e.element || '').toLowerCase().includes(q) ||
      String(e.role || '').toLowerCase().includes(q) ||
      String(e.divine_weapon_id || '').toLowerCase().includes(q),
    );
  }, [sixStar, q6]);

  const submitByHero = useCallback(async () => {
    const id = byHeroInput.trim();
    if (!id) return;
    setByHeroLoading(true);
    setByHeroError(null);
    setByHeroResult(null);
    try {
      const r = await apiCall(`/api/hero-skill-kits/catalogs/by-hero/${encodeURIComponent(id)}`);
      setByHeroResult(r);
    } catch (e: any) {
      const msg = e?.message || 'Errore lookup';
      // 404 = no match → empty state pulito
      setByHeroError(msg);
    } finally {
      setByHeroLoading(false);
    }
  }, [byHeroInput]);

  return (
    <SafeAreaView style={s.root}>
      <Stack.Screen options={{ title: 'Kit Skill Eroi', headerShown: false }} />

      <View style={s.header}>
        <Pressable onPress={() => router.back()} style={s.backBtn}>
          <Text style={s.backTxt}>← Indietro</Text>
        </Pressable>
        <Text style={s.title}>📖 Kit Skill Eroi</Text>
        <View style={{ width: 70 }} />
      </View>

      <View style={s.banner}>
        <Text style={s.bannerTxt}>
          ✦ Cataloghi <Text style={{ color: COLORS.gold, fontWeight: '900' }}>read-only</Text>,
          non collegati al runtime battaglia / HP bar.
        </Text>
      </View>

      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        style={s.tabBar}
        contentContainerStyle={s.tabBarContent}
      >
        {TABS.map((t) => (
          <TouchableOpacity key={t.key} onPress={() => setTab(t.key)}
            style={[s.tab, tab === t.key && s.tabActive]}>
            <Text style={s.tabIcon}>{t.icon}</Text>
            <Text style={[s.tabText, tab === t.key && s.tabTextActive]}>{t.label}</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      <ScrollView style={s.scroll} contentContainerStyle={s.scrollContent}>
        {error && (
          <View style={s.errorBox}>
            <Text style={s.errorTxt}>{error}</Text>
            <TouchableOpacity onPress={() => setError(null)}>
              <Text style={{ color: COLORS.gold }}>Chiudi</Text>
            </TouchableOpacity>
          </View>
        )}

        {tab === 'summary' && (
          loading ? <Loader /> : summary ? <SummaryView summary={summary} /> : <Empty msg="Summary non disponibile" />
        )}

        {tab === '5star' && (
          fiveStar
            ? <>
                <SearchBar placeholder="Cerca 5★ (hero_id, nome, elemento)…"
                  value={q5} onChange={setQ5}
                  count={fiveStarFiltered.length} total={fiveStar?.entries?.length || 0} />
                {fiveStarFiltered.length === 0
                  ? <Empty msg="Nessun 5★ corrisponde alla ricerca" />
                  : fiveStarFiltered.map((e) => <FiveStarCard key={e.hero_id} e={e} />)
                }
              </>
            : <Loader />
        )}

        {tab === '6star' && (
          sixStar
            ? <>
                <SearchBar placeholder="Cerca 6★ (hero_id, nome, arma divina)…"
                  value={q6} onChange={setQ6}
                  count={sixStarFiltered.length} total={sixStar?.entries?.length || 0} />
                {sixStarFiltered.length === 0
                  ? <Empty msg="Nessun 6★ corrisponde alla ricerca" />
                  : sixStarFiltered.map((e) => <SixStarCard key={e.hero_id} e={e} />)
                }
              </>
            : <Loader />
        )}

        {tab === 'search' && (
          <SearchByHeroView
            input={byHeroInput} setInput={setByHeroInput}
            onSubmit={submitByHero}
            loading={byHeroLoading} error={byHeroError} result={byHeroResult}
          />
        )}

        {tab === 'schema' && (
          schema ? <SchemaView schema={schema} /> : <Loader />
        )}

        <View style={{ height: 32 }} />
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
  return <View style={s.emptyWrap}><Text style={s.emptyText}>{msg}</Text></View>;
}

function SearchBar({ placeholder, value, onChange, count, total }: {
  placeholder: string; value: string; onChange: (v: string) => void;
  count: number; total: number;
}) {
  return (
    <View style={s.searchWrap}>
      <TextInput value={value} onChangeText={onChange} placeholder={placeholder}
        placeholderTextColor={COLORS.textDim} style={s.searchInput}
        autoCorrect={false} autoCapitalize="none" />
      <Text style={s.searchCount}>{count}/{total}</Text>
    </View>
  );
}

function FlagPill({ value }: { value: boolean }) {
  return (
    <View style={[s.flagPill, {
      backgroundColor: value ? COLORS.green + '33' : COLORS.textDim + '22',
      borderColor: value ? COLORS.green : COLORS.textDim,
    }]}>
      <Text style={[s.flagPillTxt, { color: value ? COLORS.green : COLORS.textDim }]}>
        {value ? 'true' : 'false'}
      </Text>
    </View>
  );
}

function SummaryView({ summary }: { summary: Summary }) {
  const cards = [
    { label: '5★ entries', value: summary.five_star_entries_count },
    { label: '6★ launch_base', value: summary.six_star_launch_base_entries_count },
    { label: '6★ extra premium', value: summary.six_star_extra_premium_entries_count },
    { label: 'Totale cataloghi', value: summary.total_catalog_entries_count },
  ];
  const flags = [
    { k: 'runtime_attached', v: summary.runtime_attached },
    { k: 'battle_runtime_attached', v: summary.battle_runtime_attached },
    { k: 'ui_runtime_attached', v: summary.ui_runtime_attached },
    { k: 'hp_bar_runtime_attached', v: summary.hp_bar_runtime_attached },
    { k: 'balance_values_finalized', v: summary.balance_values_finalized },
    { k: 'do_not_treat_as_live_kit', v: summary.do_not_treat_as_live_kit },
  ];
  return (
    <>
      <View style={s.grid}>
        {cards.map((c) => (
          <View key={c.label} style={s.summaryCard}>
            <Text style={s.summaryValue}>{c.value}</Text>
            <Text style={s.summaryLabel}>{c.label}</Text>
          </View>
        ))}
      </View>
      <View style={s.runtimeFlagsBox}>
        <Text style={s.runtimeFlagsTitle}>Runtime flags</Text>
        {flags.map((f) => (
          <View key={f.k} style={s.flagRow}>
            <Text style={s.flagLabel}>{f.k}</Text>
            <FlagPill value={f.v} />
          </View>
        ))}
        <Text style={s.runtimeFlagsNote}>
          Cataloghi NON collegati a battle/UI/HP bar runtime. Solo design data.
        </Text>
      </View>
      {!!summary.notes && (
        <View style={s.notesBox}><Text style={s.notesTxt}>📌 {summary.notes}</Text></View>
      )}
      {!!summary.source_directory && (
        <Text style={s.sourceTxt}>Source: {summary.source_directory}</Text>
      )}
    </>
  );
}

// ── 5★ card ───────────────────────────────────────────────────────────
const SLOTS_5STAR = ['basic', 'passive_base', 'skill_1', 'passive_advanced', 'skill_2'];

function FiveStarCard({ e }: { e: any }) {
  const sp = e.skill_package || {};
  const pa = sp.passive_advanced || {};
  const sk2 = sp.skill_2 || {};
  const paIsTodo = pa.design_status === 'missing_from_approved_source' ||
                   pa.source_status === 'TODO_SOURCE_REQUIRED';
  const sk2IsLegacyUlt = sk2.legacy_source_slot === 'ultimate_or_special' ||
                         sk2.legacy_source_slot === 'ultimate';
  const elemColor = ELEMENT_COLOR[String(e.element || '').toLowerCase()] || COLORS.gold;
  return (
    <View style={[s.card, { borderColor: elemColor + '99' }]}>
      <View style={s.cardHeader}>
        <Text style={s.cardTitle}>{e.display_name || e.hero_id}</Text>
        <Text style={s.cardId}>{e.hero_id}</Text>
      </View>
      <View style={s.tagsRow}>
        {!!e.element && <Tag label={e.element} color={elemColor} />}
        {!!e.role && <Tag label={e.role} color={COLORS.cyan} />}
        {!!e.faction && <Tag label={e.faction} color={COLORS.purple} />}
        <Tag label={`NR${e.native_rarity || 5}`} color={COLORS.magenta} />
      </View>
      <View style={s.slotsRow}>
        {SLOTS_5STAR.map((slot) => {
          const isMissing = slot === 'passive_advanced' && paIsTodo;
          const isLegacy = slot === 'skill_2' && sk2IsLegacyUlt;
          const color = isMissing ? COLORS.red : isLegacy ? COLORS.orange : COLORS.gold;
          return (
            <View key={slot} style={[s.slotChip, { borderColor: color + '88', backgroundColor: color + '15' }]}>
              <Text style={[s.slotChipTxt, { color }]}>{slot}</Text>
            </View>
          );
        })}
      </View>
      {paIsTodo && (
        <View style={s.warnRow}>
          <Text style={[s.warnTxt, { color: COLORS.red }]}>
            ⚠️ passive_advanced: <Text style={{ fontWeight: '900' }}>TODO_SOURCE_REQUIRED</Text> · missing dalla fonte approvata.
          </Text>
        </View>
      )}
      {sk2IsLegacyUlt && (
        <View style={s.warnRow}>
          <Text style={[s.warnTxt, { color: COLORS.orange }]}>
            ⓘ skill_2 ← legacy <Text style={{ fontWeight: '900' }}>{sk2.legacy_source_slot}</Text> · is_true_ultimate=false (i 5★ non hanno vera Ultimate).
          </Text>
        </View>
      )}
    </View>
  );
}

// ── 6★ card ───────────────────────────────────────────────────────────
const SLOTS_6STAR = ['basic', 'passive_base', 'skill_1', 'passive_advanced', 'skill_2', 'ultimate'];

function SixStarCard({ e }: { e: any }) {
  const isExtraPremium = String(e.release_group || '').toLowerCase() === 'launch_extra_premium';
  const elemColor = ELEMENT_COLOR[String(e.element || '').toLowerCase()] || COLORS.gold;
  const expected = (e.expected_slots && e.expected_slots.length) ? e.expected_slots : SLOTS_6STAR;
  const sp = e.skill_package || {};
  return (
    <View style={[s.card, { borderColor: (isExtraPremium ? COLORS.magenta : elemColor) + '99' }]}>
      <View style={s.cardHeader}>
        <Text style={s.cardTitle}>{e.display_name || e.hero_id}</Text>
        <Text style={s.cardId}>{e.hero_id}</Text>
      </View>
      <View style={s.tagsRow}>
        {!!e.element && <Tag label={e.element} color={elemColor} />}
        {!!e.role && <Tag label={e.role} color={COLORS.cyan} />}
        {!!e.faction && <Tag label={e.faction} color={COLORS.purple} />}
        <Tag label="NR6" color={COLORS.gold} />
        {isExtraPremium
          ? <Tag label="launch_extra_premium" color={COLORS.magenta} />
          : <Tag label="launch_base" color={COLORS.blue} />
        }
      </View>
      {!!e.divine_weapon_id && (
        <Text style={s.cardSub}>
          ⚔️ {e.divine_weapon_name || e.divine_weapon_id} <Text style={{ color: COLORS.textDim }}>({e.divine_weapon_id})</Text>
        </Text>
      )}
      <View style={s.slotsRow}>
        {expected.map((slot: string) => {
          const present = !!sp[slot];
          return (
            <View key={slot} style={[s.slotChip, {
              borderColor: (present ? COLORS.gold : COLORS.textDim) + '88',
              backgroundColor: (present ? COLORS.gold : COLORS.textDim) + '15',
            }]}>
              <Text style={[s.slotChipTxt, { color: present ? COLORS.gold : COLORS.textDim }]}>
                {slot}
              </Text>
            </View>
          );
        })}
      </View>
      {isExtraPremium && (
        <View style={[s.warnRow, { backgroundColor: COLORS.magenta + '15', borderColor: COLORS.magenta + '50', borderWidth: 1, borderRadius: 6, padding: 6, marginTop: 6 }]}>
          <Text style={[s.warnTxt, { color: COLORS.magenta }]}>
            🛡 Catalog design only: roster / gacha / battle availability <Text style={{ fontWeight: '900' }}>NOT affected</Text>.
          </Text>
        </View>
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

// ── By-hero search ────────────────────────────────────────────────────
function SearchByHeroView({ input, setInput, onSubmit, loading, error, result }: {
  input: string; setInput: (v: string) => void;
  onSubmit: () => void;
  loading: boolean; error: string | null; result: any | null;
}) {
  return (
    <View>
      <Text style={s.sectionHint}>
        Inserisci un hero_id (es. <Text style={{ color: COLORS.gold }}>greek_atalanta</Text>,
        <Text style={{ color: COLORS.gold }}> greek_athena</Text>,
        <Text style={{ color: COLORS.gold }}> greek_borea</Text>) e premi Cerca.
      </Text>
      <View style={s.searchByHeroRow}>
        <TextInput value={input} onChangeText={setInput}
          placeholder="hero_id…"
          placeholderTextColor={COLORS.textDim}
          style={[s.searchInput, { flex: 1 }]}
          autoCapitalize="none" autoCorrect={false}
          onSubmitEditing={onSubmit} returnKeyType="search" />
        <TouchableOpacity onPress={onSubmit} disabled={loading || !input.trim()}
          style={[s.searchBtn, (loading || !input.trim()) && { opacity: 0.5 }]}>
          <Text style={s.searchBtnTxt}>{loading ? '…' : 'Cerca'}</Text>
        </TouchableOpacity>
      </View>
      {!!error && (
        <View style={s.byHeroEmpty}>
          <Text style={s.byHeroEmptyTitle}>Nessun risultato</Text>
          <Text style={s.byHeroEmptyMsg}>{error}</Text>
          <Text style={s.byHeroEmptyHint}>
            Suggerimento: prova hero_id canonical (Bible-confirmed).
          </Text>
        </View>
      )}
      {!!result && (
        <View style={s.byHeroResult}>
          <View style={s.cardHeader}>
            <Text style={s.cardTitle}>
              {result.entry?.display_name || result.entry?.hero_id}
            </Text>
            <Text style={s.cardId}>{result.entry?.hero_id}</Text>
          </View>
          <View style={s.tagsRow}>
            <Tag label={result.found_in} color={
              result.found_in === '5star' ? COLORS.gold
              : result.found_in === '6star_launch_base' ? COLORS.blue
              : COLORS.magenta
            } />
            {!!result.entry?.element && <Tag label={result.entry.element} color={ELEMENT_COLOR[String(result.entry.element).toLowerCase()] || COLORS.gold} />}
            {!!result.entry?.role && <Tag label={result.entry.role} color={COLORS.cyan} />}
            {!!result.entry?.divine_weapon_id && <Tag label={`⚔️ ${result.entry.divine_weapon_id}`} color={COLORS.purple} />}
          </View>
          {!!result.entry?.skill_package && (
            <View style={s.slotsRow}>
              {Object.keys(result.entry.skill_package).map((slot) => (
                <View key={slot} style={[s.slotChip, { borderColor: COLORS.gold + '88', backgroundColor: COLORS.gold + '15' }]}>
                  <Text style={[s.slotChipTxt, { color: COLORS.gold }]}>{slot}</Text>
                </View>
              ))}
            </View>
          )}
          <Text style={s.byHeroNote}>
            runtime_attached: <Text style={{ color: COLORS.textDim }}>false</Text> · battle_runtime_attached: <Text style={{ color: COLORS.textDim }}>false</Text>
          </Text>
        </View>
      )}
    </View>
  );
}

// ── Schema view ───────────────────────────────────────────────────────
function SchemaView({ schema }: { schema: any }) {
  const data = schema?.data || {};
  return (
    <View>
      <Text style={s.sectionHint}>Schema metadata (read-only, design contract).</Text>
      <View style={[s.card, { borderColor: COLORS.blue + '88' }]}>
        <Text style={s.cardTitle}>{schema?.name || 'hero_skill_kit_schema_v1'}</Text>
        {!!data.schema_version && <Text style={s.cardSub}>schema_version: {data.schema_version}</Text>}
        {!!data.source && <Text style={s.cardSub}>source: {data.source}</Text>}
        {!!data.scope && <Text style={s.cardSub}>scope: {JSON.stringify(data.scope)}</Text>}
      </View>
      {!!data.official_skill_slots_by_native_rarity && (
        <View style={[s.card, { borderColor: COLORS.gold + '88' }]}>
          <Text style={s.cardTitle}>Slot progression</Text>
          {Object.entries(data.official_skill_slots_by_native_rarity).map(([r, slots]: any) => (
            <Text key={r} style={s.cardSub}>
              <Text style={{ color: COLORS.magenta, fontWeight: '900' }}>{r}★</Text>{' '}
              {(slots as string[]).join(' · ')}
            </Text>
          ))}
        </View>
      )}
      <View style={[s.card, { borderColor: COLORS.red + '88' }]}>
        <Text style={s.cardTitle}>Stato bilanciamento</Text>
        <Text style={s.cardSub}>• final_numbers: <Text style={{ color: COLORS.textDim }}>null</Text> su tutte le skill</Text>
        <Text style={s.cardSub}>• balance_values_finalized: <Text style={{ color: COLORS.red }}>false</Text></Text>
        <Text style={s.cardSub}>• runtime_attached: <Text style={{ color: COLORS.red }}>false</Text></Text>
        <Text style={s.cardSub}>• do_not_treat_as_live_kit: <Text style={{ color: COLORS.green }}>true</Text></Text>
      </View>
    </View>
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
  banner: { backgroundColor: '#FFD70010', borderBottomWidth: 1, borderBottomColor: COLORS.gold + '40', paddingVertical: 6, paddingHorizontal: 12 },
  bannerTxt: { color: COLORS.textMuted, fontSize: 11, lineHeight: 14 },
  tabBar: { maxHeight: 56, borderBottomWidth: 1, borderBottomColor: COLORS.border, flexGrow: 0 },
  tabBarContent: { paddingHorizontal: 8, paddingVertical: 6, gap: 6, alignItems: 'center' },
  tab: { flexDirection: 'row', alignItems: 'center', gap: 4, paddingHorizontal: 10, paddingVertical: 6, borderRadius: 18, backgroundColor: COLORS.panel, borderWidth: 1, borderColor: COLORS.border },
  tabActive: { backgroundColor: COLORS.gold + '22', borderColor: COLORS.gold },
  tabIcon: { fontSize: 13 },
  tabText: { color: COLORS.textMuted, fontSize: 11, fontWeight: '700' },
  tabTextActive: { color: COLORS.gold },
  scroll: { flex: 1 },
  scrollContent: { padding: 12, gap: 8 },
  errorBox: { backgroundColor: '#FF000020', borderColor: '#FF0000', borderWidth: 1, borderRadius: 8, padding: 10, marginBottom: 10, flexDirection: 'row', justifyContent: 'space-between' },
  errorTxt: { color: '#FF8888', flex: 1 },
  loaderWrap: { padding: 30, alignItems: 'center', gap: 8 },
  loaderText: { color: COLORS.textMuted },
  emptyWrap: { padding: 24, alignItems: 'center' },
  emptyText: { color: COLORS.textDim, fontStyle: 'italic' },

  // Summary
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  summaryCard: { flexBasis: '47%', flexGrow: 1, backgroundColor: COLORS.panel, borderColor: COLORS.border, borderWidth: 1, borderRadius: 10, padding: 12, alignItems: 'center' },
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
  searchInput: { flex: 1, backgroundColor: COLORS.panel, borderColor: COLORS.border, borderWidth: 1, borderRadius: 8, paddingHorizontal: 12, paddingVertical: 8, color: COLORS.text, fontSize: 13 },
  searchCount: { color: COLORS.textMuted, fontSize: 11, fontWeight: '700', minWidth: 50, textAlign: 'right' },

  // Cards
  card: { backgroundColor: COLORS.panel, borderRadius: 10, padding: 10, borderWidth: 1, marginBottom: 6 },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 },
  cardTitle: { color: COLORS.text, fontSize: 13, fontWeight: '800', flex: 1 },
  cardId: { color: COLORS.textDim, fontSize: 10, fontFamily: 'monospace' },
  cardSub: { color: COLORS.textMuted, fontSize: 11, marginTop: 3 },
  tagsRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 4, marginTop: 2 },
  tag: { paddingHorizontal: 6, paddingVertical: 2, borderRadius: 6, borderWidth: 1 },
  tagTxt: { fontSize: 9, fontWeight: '700' },

  // Slots
  slotsRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 4, marginTop: 6 },
  slotChip: { paddingHorizontal: 7, paddingVertical: 3, borderRadius: 8, borderWidth: 1 },
  slotChipTxt: { fontSize: 9, fontWeight: '800', letterSpacing: 0.2 },
  warnRow: { marginTop: 6 },
  warnTxt: { fontSize: 10, lineHeight: 13 },

  // By-hero search
  sectionHint: { color: COLORS.textMuted, fontSize: 11, marginBottom: 8 },
  searchByHeroRow: { flexDirection: 'row', gap: 8, marginBottom: 10 },
  searchBtn: { backgroundColor: COLORS.gold + '22', borderColor: COLORS.gold, borderWidth: 1, paddingHorizontal: 14, justifyContent: 'center', borderRadius: 8 },
  searchBtnTxt: { color: COLORS.gold, fontWeight: '900', fontSize: 12 },
  byHeroEmpty: { backgroundColor: COLORS.panel2, borderRadius: 10, padding: 12, borderColor: COLORS.border, borderWidth: 1, marginTop: 4 },
  byHeroEmptyTitle: { color: COLORS.textMuted, fontSize: 12, fontWeight: '900' },
  byHeroEmptyMsg: { color: COLORS.textDim, fontSize: 11, marginTop: 4 },
  byHeroEmptyHint: { color: COLORS.textDim, fontSize: 10, marginTop: 6, fontStyle: 'italic' },
  byHeroResult: { backgroundColor: COLORS.panel, borderRadius: 10, padding: 10, borderWidth: 1, borderColor: COLORS.gold + '66', marginTop: 4 },
  byHeroNote: { color: COLORS.textDim, fontSize: 9, marginTop: 6, fontStyle: 'italic' },
});
