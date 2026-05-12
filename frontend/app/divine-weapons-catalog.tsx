/**
 * RM1.27-C — Divine Weapon Internal Catalog Browser UI
 * ─────────────────────────────────────────────────────────────────────────
 * Schermata mobile-first read-only per browser interno dei cataloghi
 * Armi Divine 6★ esposti via Read-Only API RM1.27-B.
 *
 * ⚠️ Cataloghi NON collegati al battle runtime / HP bar / VFX runtime /
 *    status runtime / gacha / roster. Solo GET API, mai mutation.
 *
 * 5 sezioni / tab:
 *   1. Summary     → counts + runtime flags=false + Borea safety block
 *   2. Catalogo    → 13 record (12 launch_base + 1 Borea extra premium)
 *   3. Cerca       → lookup by hero_id OR by divine_weapon_id (toggle)
 *   4. Schema      → schema/contract leggibile + JSON preview
 *   5. Requisiti   → unlock requirements + safety checklist visuale
 *
 * Borea:
 *   - greek_borea visibile SOLO come catalog design data, mai attivata.
 *   - legacy `borea` → 404 esplicito (alias rifiutato).
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

type TabKey = 'summary' | 'catalog' | 'search' | 'schema' | 'requirements';
const TABS: Array<{ key: TabKey; label: string; icon: string }> = [
  { key: 'summary',      label: 'Summary',    icon: '📊' },
  { key: 'catalog',      label: 'Catalogo',   icon: '⚔️' },
  { key: 'search',       label: 'Cerca',      icon: '🔎' },
  { key: 'schema',       label: 'Schema',     icon: '📋' },
  { key: 'requirements', label: 'Requisiti',  icon: '🛡' },
];

// State labels in Italian
const STATE_LABELS_IT: Record<string, string> = {
  sealed: 'Sigillata',
  dormant: 'Dormiente',
  awakened: 'Risvegliata',
  empowered: 'Rafforzata',
  blessed: 'Benedetta',
  ascendant: 'Ascendente',
  divine: 'Divina',
};

export default function DivineWeaponsCatalogScreen() {
  const router = useRouter();
  const [tab, setTab] = useState<TabKey>('summary');
  const [error, setError] = useState<string | null>(null);

  const [summary, setSummary] = useState<any | null>(null);
  const [allCatalog, setAllCatalog] = useState<any | null>(null);
  const [schema, setSchema] = useState<any | null>(null);
  const [requirements, setRequirements] = useState<any | null>(null);

  // Local filter on catalog tab
  const [qCat, setQCat] = useState('');

  // Search tab: by-hero OR by-weapon (manual submit)
  const [searchMode, setSearchMode] = useState<'hero' | 'weapon'>('hero');
  const [searchInput, setSearchInput] = useState('');
  const [searchResult, setSearchResult] = useState<any | null>(null);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [searchLoading, setSearchLoading] = useState(false);

  // Initial summary fetch
  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const s = await apiCall('/api/divine-weapons/catalogs/summary');
        if (alive) setSummary(s);
      } catch (e: any) {
        if (alive) setError(e?.message || 'Errore summary');
      }
    })();
    return () => { alive = false; };
  }, []);

  const ensure = useCallback(async (target: TabKey) => {
    try {
      if (target === 'catalog' && !allCatalog) {
        setAllCatalog(await apiCall('/api/divine-weapons/catalogs/all'));
      } else if (target === 'schema' && !schema) {
        setSchema(await apiCall('/api/divine-weapons/catalogs/schema'));
      } else if (target === 'requirements' && !requirements) {
        setRequirements(await apiCall('/api/divine-weapons/catalogs/requirements'));
      }
    } catch (e: any) {
      setError(e?.message || 'Errore caricamento sezione');
    }
  }, [allCatalog, schema, requirements]);

  useEffect(() => {
    if (tab !== 'summary' && tab !== 'search') ensure(tab);
  }, [tab, ensure]);

  // Catalog filter
  const catalogFiltered = useMemo<any[]>(() => {
    const arr: any[] = allCatalog?.records || [];
    const q = qCat.trim().toLowerCase();
    if (!q) return arr;
    return arr.filter((r) =>
      String(r.hero_id || '').toLowerCase().includes(q) ||
      String(r.display_name || '').toLowerCase().includes(q) ||
      String(r.divine_weapon_id || '').toLowerCase().includes(q) ||
      String(r.element || '').toLowerCase().includes(q) ||
      String(r.release_group || '').toLowerCase().includes(q),
    );
  }, [allCatalog, qCat]);

  const submitSearch = useCallback(async () => {
    const id = searchInput.trim();
    if (!id) return;
    setSearchLoading(true);
    setSearchError(null);
    setSearchResult(null);
    try {
      const path = searchMode === 'hero'
        ? `/api/divine-weapons/catalogs/by-hero/${encodeURIComponent(id)}`
        : `/api/divine-weapons/catalogs/by-weapon/${encodeURIComponent(id)}`;
      const r = await apiCall(path);
      setSearchResult(r);
    } catch (e: any) {
      setSearchError(e?.message || 'Errore lookup');
    } finally {
      setSearchLoading(false);
    }
  }, [searchInput, searchMode]);

  return (
    <SafeAreaView style={s.root}>
      <Stack.Screen options={{ title: 'Armi Divine', headerShown: false }} />

      <View style={s.header}>
        <Pressable onPress={() => router.back()} style={s.backBtn}>
          <Text style={s.backTxt}>← Indietro</Text>
        </Pressable>
        <Text style={s.title}>⚔️ Armi Divine</Text>
        <View style={{ width: 70 }} />
      </View>

      <View style={s.banner}>
        <Text style={s.bannerTxt}>
          ✦ Catalogo interno <Text style={{ color: COLORS.gold, fontWeight: '900' }}>read-only</Text>.
          Non attiva runtime, battle, HP bar, VFX, gacha, roster o Borea.
        </Text>
      </View>

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
          summary ? <SummaryView summary={summary} /> : <Loader />
        )}

        {tab === 'catalog' && (
          allCatalog
            ? <>
                <SearchBar
                  placeholder="Filtra (hero_id, weapon_id, elemento, release_group)…"
                  value={qCat} onChange={setQCat}
                  count={catalogFiltered.length}
                  total={allCatalog?.records?.length || 0}
                />
                {catalogFiltered.length === 0
                  ? <Empty msg="Nessuna Arma Divina corrisponde al filtro" />
                  : catalogFiltered.map((r) => <WeaponCard key={r.divine_weapon_id} r={r} />)
                }
              </>
            : <Loader />
        )}

        {tab === 'search' && (
          <SearchView
            mode={searchMode} setMode={setSearchMode}
            input={searchInput} setInput={setSearchInput}
            onSubmit={submitSearch}
            loading={searchLoading} error={searchError} result={searchResult}
          />
        )}

        {tab === 'schema' && (
          schema ? <SchemaView schema={schema} /> : <Loader />
        )}

        {tab === 'requirements' && (
          requirements ? <RequirementsView reqs={requirements} /> : <Loader />
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
      <TextInput
        value={value} onChangeText={onChange} placeholder={placeholder}
        placeholderTextColor={COLORS.textDim} style={s.searchInput}
        autoCorrect={false} autoCapitalize="none"
      />
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

function Tag({ label, color }: { label: string; color: string }) {
  return (
    <View style={[s.tag, { backgroundColor: color + '22', borderColor: color + '88' }]}>
      <Text style={[s.tagTxt, { color }]}>{label}</Text>
    </View>
  );
}

// ── Summary ───────────────────────────────────────────────────────────
function SummaryView({ summary }: { summary: any }) {
  const cards = [
    { label: 'Totale Armi Divine', value: summary.total_divine_weapons },
    { label: 'launch_base', value: summary.launch_base_count },
    { label: 'launch_extra_premium', value: summary.launch_extra_premium_count },
    { label: 'native_rarity_required', value: `${summary.native_rarity_required}★` },
  ];
  const flags = [
    { k: 'runtime_attached', v: !!summary.runtime_attached },
    { k: 'battle_runtime_attached', v: !!summary.battle_runtime_attached },
    { k: 'hp_bar_runtime_attached', v: !!summary.hp_bar_runtime_attached },
    { k: 'vfx_runtime_attached', v: !!summary.vfx_runtime_attached },
    { k: 'gacha_attached', v: !!summary.gacha_attached },
    { k: 'roster_activation_attached', v: !!summary.roster_activation_attached },
    { k: 'balance_values_finalized', v: !!summary.balance_values_finalized },
    { k: 'do_not_treat_as_live_power', v: !!summary.do_not_treat_as_live_power },
  ];
  const progression: string[] = summary.progression_states || [];
  const bs = summary.borea_safety || {};
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

      <View style={[s.notesBox, { borderColor: COLORS.gold + '50' }]}>
        <Text style={[s.notesTxt, { color: COLORS.gold }]}>
          🔒 Rompere il sigillo richiede l'eroe a{' '}
          <Text style={{ fontWeight: '900' }}>{summary.required_hero_star_level_to_break_seal}★</Text>
          {' '}e materiali dedicati.
        </Text>
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
          Catalogo NON collegato a battle/HP bar/VFX/status/gacha/roster runtime. Solo design data.
        </Text>
      </View>

      <View style={[s.card, { borderColor: COLORS.purple + '88' }]}>
        <Text style={s.cardTitle}>Progressione stati</Text>
        <View style={s.slotsRow}>
          {progression.map((sk) => (
            <View key={sk} style={[s.slotChip, {
              borderColor: COLORS.purple + '88',
              backgroundColor: COLORS.purple + '15',
            }]}>
              <Text style={[s.slotChipTxt, { color: COLORS.purple }]}>
                {STATE_LABELS_IT[sk] || sk}
              </Text>
            </View>
          ))}
        </View>
        <Text style={s.cardSub}>
          • sealed = nessun bonus, nessuna Presenza Divina
        </Text>
        <Text style={s.cardSub}>
          • dormant+ = hook design attivi + Presenza Divina (metadata)
        </Text>
      </View>

      <View style={[s.card, { borderColor: COLORS.magenta + '88', backgroundColor: COLORS.magenta + '10' }]}>
        <Text style={[s.cardTitle, { color: COLORS.magenta }]}>🛡 Borea safety</Text>
        <Text style={s.cardSub}>hero_id: <Text style={{ color: COLORS.gold }}>{bs.hero_id}</Text></Text>
        <Text style={s.cardSub}>release_group: <Text style={{ color: COLORS.magenta }}>{bs.release_group}</Text></Text>
        <Text style={s.cardSub}>catalog_status: <Text style={{ color: COLORS.cyan }}>{bs.catalog_status}</Text></Text>
        <Text style={s.cardSub}>divine_weapon_id: <Text style={{ color: COLORS.textMuted, fontFamily: 'monospace' }}>{bs.divine_weapon_id}</Text></Text>
        <View style={[s.flagRow, { marginTop: 6 }]}>
          <Text style={s.flagLabel}>borea_activation_allowed</Text>
          <FlagPill value={!!bs.borea_activation_allowed} />
        </View>
        <View style={s.flagRow}>
          <Text style={s.flagLabel}>legacy_borea_allowed</Text>
          <FlagPill value={!!bs.legacy_borea_allowed} />
        </View>
        <Text style={[s.runtimeFlagsNote, { marginTop: 6 }]}>
          {bs.note} Borea NON è visibile in /api/heroes.
        </Text>
      </View>

      {!!summary.notes && (
        <View style={s.notesBox}>
          <Text style={s.notesTxt}>📌 {summary.notes}</Text>
        </View>
      )}
      {!!summary.source_directory && (
        <Text style={s.sourceTxt}>Source: {summary.source_directory}</Text>
      )}
    </>
  );
}

// ── Weapon Card (catalog list) ────────────────────────────────────────
const PROGRESSION_ORDER = ['sealed', 'dormant', 'awakened', 'empowered', 'blessed', 'ascendant', 'divine'];

function WeaponCard({ r }: { r: any }) {
  const isExtra = String(r.release_group || '').toLowerCase() === 'launch_extra_premium';
  const elemColor = ELEMENT_COLOR[String(r.element || '').toLowerCase()] || COLORS.gold;
  const borderColor = isExtra ? COLORS.magenta : elemColor;
  const sf = r.safety_flags || {};
  const ur = r.unlock_requirements || {};
  const dpl = r.divine_presence_layer || {};
  const states: any[] = r.progression_states || [];
  return (
    <View style={[s.card, { borderColor: borderColor + 'AA', borderWidth: 1.5 }]}>
      <View style={s.cardHeader}>
        <Text style={s.cardTitle}>{r.display_name || r.hero_id}</Text>
        <Text style={s.cardId}>{r.hero_id}</Text>
      </View>
      <Text style={s.cardSub}>
        ⚔️ <Text style={{ color: COLORS.gold, fontWeight: '700' }}>{r.divine_weapon_id}</Text>
      </Text>

      <View style={s.tagsRow}>
        {!!r.element && <Tag label={r.element} color={elemColor} />}
        <Tag label={`NR${r.native_rarity_required || 6}`} color={COLORS.gold} />
        <Tag label={r.catalog_status || 'catalog_only'} color={COLORS.cyan} />
        {isExtra
          ? <Tag label="launch_extra_premium" color={COLORS.magenta} />
          : <Tag label="launch_base" color={COLORS.blue} />
        }
        {!!ur.required_hero_star_level && <Tag label={`Seal break: ${ur.required_hero_star_level}★`} color={COLORS.orange} />}
      </View>

      <Text style={[s.cardSub, { marginTop: 6 }]}>Progressione</Text>
      <View style={s.slotsRow}>
        {(states.length ? states.map((p: any) => p.state_key) : PROGRESSION_ORDER).map((sk: string) => {
          const isSealed = sk === 'sealed';
          const color = isSealed ? COLORS.textDim : COLORS.purple;
          return (
            <View key={sk} style={[s.slotChip, {
              borderColor: color + '88',
              backgroundColor: color + '15',
            }]}>
              <Text style={[s.slotChipTxt, { color }]}>
                {STATE_LABELS_IT[sk] || sk}
              </Text>
            </View>
          );
        })}
      </View>

      {!!dpl?.enabled_from_state && (
        <Text style={s.cardSub}>
          🌟 Divine Presence Layer: enabled_from_state =
          <Text style={{ color: COLORS.gold }}> {STATE_LABELS_IT[dpl.enabled_from_state] || dpl.enabled_from_state}</Text>
          {' '}· disabled_in_state =
          <Text style={{ color: COLORS.textDim }}> {STATE_LABELS_IT[dpl.disabled_in_state] || dpl.disabled_in_state}</Text>
        </Text>
      )}

      <View style={[s.tagsRow, { marginTop: 6 }]}>
        <Tag label={`runtime: ${sf.runtime_attached ? 'true' : 'false'}`} color={sf.runtime_attached ? COLORS.red : COLORS.green} />
        <Tag label={`battle: ${sf.battle_runtime_attached ? 'true' : 'false'}`} color={sf.battle_runtime_attached ? COLORS.red : COLORS.green} />
        <Tag label={`vfx: ${sf.vfx_runtime_attached ? 'true' : 'false'}`} color={sf.vfx_runtime_attached ? COLORS.red : COLORS.green} />
        <Tag label={`gacha: ${sf.gacha_attached ? 'true' : 'false'}`} color={sf.gacha_attached ? COLORS.red : COLORS.green} />
      </View>

      {isExtra && (
        <View style={[s.warnRow, {
          backgroundColor: COLORS.magenta + '18',
          borderColor: COLORS.magenta + '60',
          borderWidth: 1, borderRadius: 6, padding: 8, marginTop: 8,
        }]}>
          <Text style={[s.warnTxt, { color: COLORS.magenta, fontWeight: '900' }]}>
            🛡 Extra Premium — Borea NON attivata
          </Text>
          <Text style={[s.warnTxt, { color: COLORS.textMuted, marginTop: 4 }]}>
            Solo design data. legacy <Text style={{ fontFamily: 'monospace', color: COLORS.red }}>borea</Text> non valido (alias rifiutato dall'API).
          </Text>
          <Text style={[s.warnTxt, { color: COLORS.textMuted, marginTop: 2 }]}>
            Roster / gacha / battle visibility NOT affected.
          </Text>
        </View>
      )}
    </View>
  );
}

// ── Search view ───────────────────────────────────────────────────────
function SearchView({ mode, setMode, input, setInput, onSubmit, loading, error, result }: {
  mode: 'hero' | 'weapon';
  setMode: (m: 'hero' | 'weapon') => void;
  input: string; setInput: (v: string) => void;
  onSubmit: () => void;
  loading: boolean; error: string | null; result: any | null;
}) {
  const isLegacyBorea = input.trim().toLowerCase() === 'borea' && mode === 'hero';
  return (
    <View>
      <Text style={s.sectionHint}>
        Cerca per <Text style={{ color: COLORS.gold }}>hero_id</Text> o{' '}
        <Text style={{ color: COLORS.gold }}>divine_weapon_id</Text>. Submit manuale.
      </Text>

      <View style={s.modeRow}>
        <TouchableOpacity
          onPress={() => setMode('hero')}
          style={[s.modeBtn, mode === 'hero' && s.modeBtnActive]}
        >
          <Text style={[s.modeBtnTxt, mode === 'hero' && s.modeBtnTxtActive]}>by hero_id</Text>
        </TouchableOpacity>
        <TouchableOpacity
          onPress={() => setMode('weapon')}
          style={[s.modeBtn, mode === 'weapon' && s.modeBtnActive]}
        >
          <Text style={[s.modeBtnTxt, mode === 'weapon' && s.modeBtnTxtActive]}>by divine_weapon_id</Text>
        </TouchableOpacity>
      </View>

      <Text style={s.sectionHint}>
        Esempi:{' '}
        <Text style={{ color: COLORS.gold }}>greek_athena</Text>,{' '}
        <Text style={{ color: COLORS.gold }}>greek_borea</Text>,{' '}
        <Text style={{ color: COLORS.gold }}>aegis_of_athena</Text>,{' '}
        <Text style={{ color: COLORS.gold }}>borea_wings_of_the_north_wind</Text>.
      </Text>

      <View style={s.searchByHeroRow}>
        <TextInput
          value={input} onChangeText={setInput}
          placeholder={mode === 'hero' ? 'hero_id…' : 'divine_weapon_id…'}
          placeholderTextColor={COLORS.textDim}
          style={[s.searchInput, { flex: 1 }]}
          autoCapitalize="none" autoCorrect={false}
          onSubmitEditing={onSubmit} returnKeyType="search"
        />
        <TouchableOpacity
          onPress={onSubmit}
          disabled={loading || !input.trim()}
          style={[s.searchBtn, (loading || !input.trim()) && { opacity: 0.5 }]}
        >
          <Text style={s.searchBtnTxt}>{loading ? '…' : 'Cerca'}</Text>
        </TouchableOpacity>
      </View>

      {isLegacyBorea && !error && !result && (
        <View style={[s.byHeroEmpty, { borderColor: COLORS.red + '66', backgroundColor: COLORS.red + '10' }]}>
          <Text style={[s.byHeroEmptyTitle, { color: COLORS.red }]}>⚠️ Alias legacy</Text>
          <Text style={s.byHeroEmptyMsg}>
            <Text style={{ fontFamily: 'monospace', color: COLORS.red }}>borea</Text> è un alias legacy non canonico.
            Premi Cerca per vedere la risposta 404 esplicita dell'API.
          </Text>
          <Text style={s.byHeroEmptyHint}>
            Usa <Text style={{ color: COLORS.gold }}>greek_borea</Text> come hero_id canonico.
          </Text>
        </View>
      )}

      {!!error && (
        <View style={s.byHeroEmpty}>
          <Text style={s.byHeroEmptyTitle}>Nessun risultato</Text>
          <Text style={s.byHeroEmptyMsg}>{error}</Text>
          <Text style={s.byHeroEmptyHint}>
            Suggerimento: usa hero_id o divine_weapon_id canonical.
            Lookup read-only, non modifica DB.
          </Text>
        </View>
      )}

      {!!result && result.record && (
        <View style={s.byHeroResult}>
          <Text style={s.cardTitle}>{result.record.display_name || result.record.hero_id}</Text>
          <Text style={s.cardId}>{result.record.hero_id}</Text>
          <Text style={s.cardSub}>
            ⚔️ <Text style={{ color: COLORS.gold }}>{result.record.divine_weapon_id}</Text>
          </Text>
          <View style={[s.tagsRow, { marginTop: 6 }]}>
            {!!result.record.element && (
              <Tag label={result.record.element}
                color={ELEMENT_COLOR[String(result.record.element).toLowerCase()] || COLORS.gold} />
            )}
            <Tag label={`NR${result.record.native_rarity_required || 6}`} color={COLORS.gold} />
            <Tag label={result.record.catalog_status} color={COLORS.cyan} />
            <Tag label={result.record.release_group} color={
              String(result.record.release_group).toLowerCase() === 'launch_extra_premium'
                ? COLORS.magenta : COLORS.blue
            } />
          </View>
          <Text style={s.byHeroNote}>
            runtime_attached: <Text style={{ color: COLORS.textDim }}>false</Text>{' '}
            · battle_runtime_attached: <Text style={{ color: COLORS.textDim }}>false</Text>{' '}
            · borea_activation_allowed: <Text style={{ color: COLORS.textDim }}>false</Text>
          </Text>
          {!!result.catalog_only_note && (
            <Text style={[s.byHeroNote, { color: COLORS.textMuted, marginTop: 4 }]}>
              📌 {result.catalog_only_note}
            </Text>
          )}
        </View>
      )}
    </View>
  );
}

// ── Schema view ───────────────────────────────────────────────────────
function SchemaView({ schema }: { schema: any }) {
  const data = schema?.data || {};
  const psd = data.progression_state_definition || {};
  const urd = data.unlock_requirements_definition || {};
  const mrd = data.material_requirements_definition || {};
  const hd = data.hooks_definition || {};
  const dpld = data.divine_presence_layer_definition || {};
  const sfd = data.safety_flags_definition || {};
  return (
    <View>
      <Text style={s.sectionHint}>Schema metadata (read-only, design contract).</Text>

      <View style={[s.card, { borderColor: COLORS.blue + '88' }]}>
        <Text style={s.cardTitle}>{schema?.name || 'divine_weapon_schema_v1'}</Text>
        {!!data.schema_id && <Text style={s.cardSub}>schema_id: {data.schema_id}</Text>}
        {!!data.version && <Text style={s.cardSub}>version: {data.version}</Text>}
        {!!data.task_origin && <Text style={s.cardSub}>task_origin: {data.task_origin}</Text>}
      </View>

      {!!data.record_required_fields?.length && (
        <View style={[s.card, { borderColor: COLORS.gold + '88' }]}>
          <Text style={s.cardTitle}>Identity / Required fields</Text>
          <View style={s.slotsRow}>
            {data.record_required_fields.map((f: string) => (
              <View key={f} style={[s.slotChip, { borderColor: COLORS.gold + '66', backgroundColor: COLORS.gold + '12' }]}>
                <Text style={[s.slotChipTxt, { color: COLORS.gold }]}>{f}</Text>
              </View>
            ))}
          </View>
        </View>
      )}

      {!!psd.required_state_keys_in_order?.length && (
        <View style={[s.card, { borderColor: COLORS.purple + '88' }]}>
          <Text style={s.cardTitle}>progression_states</Text>
          <View style={s.slotsRow}>
            {psd.required_state_keys_in_order.map((sk: string) => (
              <View key={sk} style={[s.slotChip, { borderColor: COLORS.purple + '88', backgroundColor: COLORS.purple + '15' }]}>
                <Text style={[s.slotChipTxt, { color: COLORS.purple }]}>{STATE_LABELS_IT[sk] || sk}</Text>
              </View>
            ))}
          </View>
          <Text style={s.cardSub}>• sealed: has_gameplay_bonus=false, has_battle_presence_layer=false</Text>
          <Text style={s.cardSub}>• dormant+: has_gameplay_bonus=true, has_battle_presence_layer=true</Text>
        </View>
      )}

      {!!Object.keys(urd).length && (
        <View style={[s.card, { borderColor: COLORS.orange + '88' }]}>
          <Text style={s.cardTitle}>unlock_requirements</Text>
          <Text style={s.cardSub}>initial_state: <Text style={{ color: COLORS.gold }}>{urd.hard_rules?.initial_state}</Text></Text>
          <Text style={s.cardSub}>break_seal_required: <Text style={{ color: COLORS.green }}>true</Text></Text>
          <Text style={s.cardSub}>required_hero_star_level: <Text style={{ color: COLORS.gold }}>{urd.hard_rules?.required_hero_star_level}★</Text></Text>
          <Text style={s.cardSub}>requires_dedicated_materials: true</Text>
          <Text style={s.cardSub}>requires_gold: true</Text>
          <Text style={s.cardSub}>requires_duplicate_materials: true</Text>
        </View>
      )}

      {!!mrd.supported_material_types?.length && (
        <View style={[s.card, { borderColor: COLORS.cyan + '88' }]}>
          <Text style={s.cardTitle}>material_requirements</Text>
          <View style={s.slotsRow}>
            {mrd.supported_material_types.map((mt: string) => (
              <View key={mt} style={[s.slotChip, { borderColor: COLORS.cyan + '66', backgroundColor: COLORS.cyan + '12' }]}>
                <Text style={[s.slotChipTxt, { color: COLORS.cyan }]}>{mt}</Text>
              </View>
            ))}
          </View>
          <Text style={s.cardSub}>• quantity: <Text style={{ color: COLORS.textDim }}>null</Text></Text>
          <Text style={s.cardSub}>• min_native_rarity: <Text style={{ color: COLORS.textDim }}>null</Text></Text>
          <Text style={s.cardSub}>• final_numbers: <Text style={{ color: COLORS.textDim }}>null</Text></Text>
        </View>
      )}

      {!!Object.keys(hd).length && (
        <View style={[s.card, { borderColor: COLORS.magenta + '88' }]}>
          <Text style={s.cardTitle}>effect_tracks / skill_hooks / status_hooks / vfx_hooks</Text>
          <Text style={s.cardSub}>• final_numbers: null</Text>
          <Text style={s.cardSub}>• runtime_attached: false</Text>
          <Text style={s.cardSub}>• ultimate_signature_upgrade: solo ascendant/divine</Text>
          <Text style={s.cardSub}>• domain_interaction: solo ascendant/divine</Text>
          <Text style={s.cardSub}>• personal statuses: source_locked=true</Text>
        </View>
      )}

      {!!Object.keys(dpld).length && (
        <View style={[s.card, { borderColor: COLORS.green + '88' }]}>
          <Text style={s.cardTitle}>divine_presence_layer</Text>
          <Text style={s.cardSub}>enabled_from_state: <Text style={{ color: COLORS.gold }}>dormant</Text></Text>
          <Text style={s.cardSub}>disabled_in_state: <Text style={{ color: COLORS.textDim }}>sealed</Text></Text>
          <Text style={s.cardSub}>layer_type: persistent_lightweight_battle_vfx</Text>
          <Text style={s.cardSub}>is_physical_weapon_animation: <Text style={{ color: COLORS.red }}>false</Text></Text>
          <Text style={s.cardSub}>requires_new_sprite_sheet: <Text style={{ color: COLORS.red }}>false</Text></Text>
          <Text style={s.cardSub}>runtime_attached: <Text style={{ color: COLORS.red }}>false</Text></Text>
        </View>
      )}

      {!!Object.keys(sfd).length && (
        <View style={[s.card, { borderColor: COLORS.red + '88' }]}>
          <Text style={s.cardTitle}>safety_flags</Text>
          <Text style={s.cardSub}>• catalog_only: <Text style={{ color: COLORS.green }}>true</Text></Text>
          <Text style={s.cardSub}>• runtime_attached / battle_runtime_attached / hp_bar_runtime_attached / vfx_runtime_attached: <Text style={{ color: COLORS.red }}>false</Text></Text>
          <Text style={s.cardSub}>• gacha_attached / roster_activation_attached: <Text style={{ color: COLORS.red }}>false</Text></Text>
          <Text style={s.cardSub}>• borea_activation_allowed: <Text style={{ color: COLORS.red }}>false</Text></Text>
          <Text style={s.cardSub}>• balance_values_finalized: <Text style={{ color: COLORS.red }}>false</Text></Text>
          <Text style={s.cardSub}>• do_not_treat_as_live_power: <Text style={{ color: COLORS.green }}>true</Text></Text>
        </View>
      )}
    </View>
  );
}

// ── Requirements / Safety view ────────────────────────────────────────
function RequirementsView({ reqs }: { reqs: any }) {
  const data = reqs?.data || {};
  const urc = data.unlock_requirements_contract || {};
  const dplc = data.divine_presence_layer_contract || {};
  const counts = data.counts || {};
  const safetyChecks = [
    { label: 'DB writes', value: false, ok: 'no', ko: 'YES' },
    { label: 'runtime activation', value: false, ok: 'no', ko: 'YES' },
    { label: 'battle hooks', value: false, ok: 'no', ko: 'YES' },
    { label: 'HP bar hooks', value: false, ok: 'no', ko: 'YES' },
    { label: 'VFX runtime hooks', value: false, ok: 'no', ko: 'YES' },
    { label: 'gacha hooks', value: false, ok: 'no', ko: 'YES' },
    { label: 'roster hooks', value: false, ok: 'no', ko: 'YES' },
    { label: 'Borea activation', value: false, ok: 'no', ko: 'YES' },
  ];
  const uiMessages = [
    'Effetti attivi: nessuno.',
    'Presenza Divina in battaglia: non attiva.',
    'Richiede eroe a 10★ e materiali dedicati per rompere il sigillo.',
  ];
  return (
    <View>
      <Text style={s.sectionHint}>Contratto di unlock + safety checklist (read-only).</Text>

      <View style={[s.card, { borderColor: COLORS.gold + '88' }]}>
        <Text style={s.cardTitle}>Counts attesi</Text>
        <Text style={s.cardSub}>total_divine_weapons: <Text style={{ color: COLORS.gold }}>{counts.total_divine_weapons || 13}</Text></Text>
        <Text style={s.cardSub}>launch_base: <Text style={{ color: COLORS.blue }}>{counts.launch_base || 12}</Text></Text>
        <Text style={s.cardSub}>launch_extra_premium: <Text style={{ color: COLORS.magenta }}>{counts.launch_extra_premium || 1}</Text></Text>
      </View>

      <View style={[s.card, { borderColor: COLORS.orange + '88' }]}>
        <Text style={s.cardTitle}>unlock_requirements_contract</Text>
        <Text style={s.cardSub}>initial_state: <Text style={{ color: COLORS.gold }}>{urc.initial_state}</Text></Text>
        <Text style={s.cardSub}>break_seal_required: <Text style={{ color: COLORS.green }}>{String(urc.break_seal_required)}</Text></Text>
        <Text style={s.cardSub}>required_hero_star_level: <Text style={{ color: COLORS.gold, fontWeight: '900' }}>{urc.required_hero_star_level}★</Text></Text>
        <Text style={s.cardSub}>requires_dedicated_materials: {String(urc.requires_dedicated_materials)}</Text>
        <Text style={s.cardSub}>requires_gold: {String(urc.requires_gold)}</Text>
        <Text style={s.cardSub}>requires_duplicate_materials: {String(urc.requires_duplicate_materials)}</Text>
      </View>

      <View style={[s.card, { borderColor: COLORS.cyan + '88' }]}>
        <Text style={s.cardTitle}>Duplicate requirement types</Text>
        <View style={s.slotsRow}>
          {['same_element_copy', 'specific_hero_copy', 'event_limited_substitute'].map((t) => (
            <View key={t} style={[s.slotChip, { borderColor: COLORS.cyan + '88', backgroundColor: COLORS.cyan + '15' }]}>
              <Text style={[s.slotChipTxt, { color: COLORS.cyan }]}>{t}</Text>
            </View>
          ))}
        </View>
        <Text style={s.cardSub}>• final_numbers policy: <Text style={{ color: COLORS.textDim }}>null</Text></Text>
      </View>

      <View style={[s.card, { borderColor: COLORS.green + '88' }]}>
        <Text style={s.cardTitle}>divine_presence_layer_contract</Text>
        <Text style={s.cardSub}>enabled: <Text style={{ color: COLORS.green }}>{String(dplc.enabled)}</Text></Text>
        <Text style={s.cardSub}>enabled_from_state: <Text style={{ color: COLORS.gold }}>{dplc.enabled_from_state}</Text></Text>
        <Text style={s.cardSub}>disabled_in_state: <Text style={{ color: COLORS.textDim }}>{dplc.disabled_in_state}</Text></Text>
        <Text style={s.cardSub}>layer_type: {dplc.layer_type}</Text>
        <Text style={s.cardSub}>is_physical_weapon_animation: <Text style={{ color: COLORS.red }}>{String(dplc.is_physical_weapon_animation)}</Text></Text>
        <Text style={s.cardSub}>requires_new_sprite_sheet: <Text style={{ color: COLORS.red }}>{String(dplc.requires_new_sprite_sheet)}</Text></Text>
        <Text style={s.cardSub}>sprite_sheet_count_required: <Text style={{ color: COLORS.red }}>{dplc.sprite_sheet_count_required ?? 0}</Text></Text>
        <Text style={s.cardSub}>runtime_attached: <Text style={{ color: COLORS.red }}>{String(dplc.runtime_attached)}</Text></Text>
      </View>

      <View style={[s.card, { borderColor: COLORS.red + '88' }]}>
        <Text style={s.cardTitle}>🛡 Safety checklist</Text>
        {safetyChecks.map((c) => (
          <View key={c.label} style={s.flagRow}>
            <Text style={s.flagLabel}>{c.label}</Text>
            <View style={[s.flagPill, {
              backgroundColor: c.value ? COLORS.red + '33' : COLORS.green + '33',
              borderColor: c.value ? COLORS.red : COLORS.green,
            }]}>
              <Text style={[s.flagPillTxt, { color: c.value ? COLORS.red : COLORS.green }]}>
                {c.value ? c.ko : c.ok}
              </Text>
            </View>
          </View>
        ))}
      </View>

      <View style={[s.card, { borderColor: COLORS.gold + '88' }]}>
        <Text style={s.cardTitle}>UI messages (read-only)</Text>
        {uiMessages.map((m, i) => (
          <Text key={i} style={s.cardSub}>• {m}</Text>
        ))}
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

  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  summaryCard: { flexBasis: '47%', flexGrow: 1, backgroundColor: COLORS.panel, borderColor: COLORS.border, borderWidth: 1, borderRadius: 10, padding: 12, alignItems: 'center' },
  summaryValue: { color: COLORS.gold, fontSize: 22, fontWeight: '900' },
  summaryLabel: { color: COLORS.textMuted, fontSize: 11, marginTop: 4, textAlign: 'center' },
  runtimeFlagsBox: { backgroundColor: COLORS.panel2, borderRadius: 10, padding: 12, marginTop: 10, borderColor: COLORS.border, borderWidth: 1 },
  runtimeFlagsTitle: { color: COLORS.text, fontSize: 12, fontWeight: '900', marginBottom: 8, letterSpacing: 0.5 },
  flagRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginVertical: 3 },
  flagLabel: { color: COLORS.textMuted, fontSize: 11 },
  flagPill: { paddingHorizontal: 8, paddingVertical: 2, borderRadius: 8, borderWidth: 1 },
  flagPillTxt: { fontSize: 10, fontWeight: '800' },
  runtimeFlagsNote: { color: COLORS.textDim, fontSize: 10, marginTop: 8, fontStyle: 'italic' },
  notesBox: { backgroundColor: COLORS.panel, borderRadius: 8, padding: 10, marginTop: 8, borderColor: COLORS.border, borderWidth: 1 },
  notesTxt: { color: COLORS.textMuted, fontSize: 11, lineHeight: 15 },
  sourceTxt: { color: COLORS.textDim, fontSize: 9, marginTop: 6, fontStyle: 'italic' },

  searchWrap: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 8 },
  searchInput: { flex: 1, backgroundColor: COLORS.panel, borderColor: COLORS.border, borderWidth: 1, borderRadius: 8, paddingHorizontal: 12, paddingVertical: 8, color: COLORS.text, fontSize: 13 },
  searchCount: { color: COLORS.textMuted, fontSize: 11, fontWeight: '700', minWidth: 50, textAlign: 'right' },

  card: { backgroundColor: COLORS.panel, borderRadius: 10, padding: 10, borderWidth: 1, marginBottom: 6 },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 },
  cardTitle: { color: COLORS.text, fontSize: 13, fontWeight: '800', flex: 1 },
  cardId: { color: COLORS.textDim, fontSize: 10, fontFamily: 'monospace' },
  cardSub: { color: COLORS.textMuted, fontSize: 11, marginTop: 3 },
  tagsRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 4, marginTop: 4 },
  tag: { paddingHorizontal: 6, paddingVertical: 2, borderRadius: 6, borderWidth: 1 },
  tagTxt: { fontSize: 9, fontWeight: '700' },

  slotsRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 4, marginTop: 6 },
  slotChip: { paddingHorizontal: 7, paddingVertical: 3, borderRadius: 8, borderWidth: 1 },
  slotChipTxt: { fontSize: 9, fontWeight: '800', letterSpacing: 0.2 },
  warnRow: { marginTop: 6 },
  warnTxt: { fontSize: 10, lineHeight: 13 },

  sectionHint: { color: COLORS.textMuted, fontSize: 11, marginBottom: 8 },
  searchByHeroRow: { flexDirection: 'row', gap: 8, marginBottom: 10 },
  searchBtn: { backgroundColor: COLORS.gold + '22', borderColor: COLORS.gold, borderWidth: 1, paddingHorizontal: 14, justifyContent: 'center', borderRadius: 8 },
  searchBtnTxt: { color: COLORS.gold, fontWeight: '900', fontSize: 12 },

  modeRow: { flexDirection: 'row', gap: 8, marginBottom: 8 },
  modeBtn: { flex: 1, paddingVertical: 6, borderRadius: 8, borderWidth: 1, borderColor: COLORS.border, alignItems: 'center', backgroundColor: COLORS.panel },
  modeBtnActive: { backgroundColor: COLORS.gold + '22', borderColor: COLORS.gold },
  modeBtnTxt: { color: COLORS.textMuted, fontSize: 11, fontWeight: '700' },
  modeBtnTxtActive: { color: COLORS.gold },

  byHeroEmpty: { backgroundColor: COLORS.panel2, borderRadius: 10, padding: 12, borderColor: COLORS.border, borderWidth: 1, marginTop: 4 },
  byHeroEmptyTitle: { color: COLORS.textMuted, fontSize: 12, fontWeight: '900' },
  byHeroEmptyMsg: { color: COLORS.textDim, fontSize: 11, marginTop: 4 },
  byHeroEmptyHint: { color: COLORS.textDim, fontSize: 10, marginTop: 6, fontStyle: 'italic' },
  byHeroResult: { backgroundColor: COLORS.panel, borderRadius: 10, padding: 10, borderWidth: 1, borderColor: COLORS.gold + '66', marginTop: 4 },
  byHeroNote: { color: COLORS.textDim, fontSize: 9, marginTop: 6, fontStyle: 'italic' },
});
