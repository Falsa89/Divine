import React, { useState, useEffect, useMemo } from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet, ScrollView,
  ActivityIndicator, Alert, Image, Dimensions,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import { apiCall } from '../../utils/api';
import { useAuth } from '../../context/AuthContext';
import AnimatedHeroPortrait from '../../components/AnimatedHeroPortrait';
import StarDisplay from '../../components/ui/StarDisplay';
import TranscendenceStars from '../../components/ui/TranscendenceStars';
import { heroImageSource } from '../../components/ui/hopliteAssets';
import { COLORS, RARITY, ELEMENTS, CLASSES } from '../../constants/theme';

const COLUMNS = [
  { role: 'Support', label: 'SUPPORTO', icon: '\u2764\uFE0F', bonus: 'CURE+15% VEL+10%', color: '#44DD99', x: 1 },
  { role: 'DPS', label: 'DPS', icon: '\u2694\uFE0F', bonus: 'ATK+15% CRIT+15%', color: '#FF5544', x: 4 },
  { role: 'Tank', label: 'TANK', icon: '\uD83D\uDEE1\uFE0F', bonus: 'DEF+20% HP+15%', color: '#4499FF', x: 7 },
];
const ROW_YS = [1, 4, 7];

const ELEM_FILTERS = [
  { key: 'all', icon: '\u2605' },
  { key: 'fire', icon: '\uD83D\uDD25' },
  { key: 'water', icon: '\uD83D\uDCA7' },
  { key: 'earth', icon: '\uD83E\uDEA8' },
  { key: 'wind', icon: '\uD83D\uDCA8' },
  { key: 'thunder', icon: '\u26A1' },
  { key: 'light', icon: '\u2728' },
  { key: 'shadow', icon: '\uD83C\uDF11' },
];

type SortKey = 'rarity' | 'level' | 'power' | 'name';

export default function BattleTab() {
  const router = useRouter();
  const { refreshUser } = useAuth();
  const [heroes, setHeroes] = useState<any[]>([]);
  // grid[col][row] = hero | null  (col: 0=Support, 1=DPS, 2=Tank; row: 0,1,2)
  const [grid, setGrid] = useState<(any | null)[][]>([[null, null, null], [null, null, null], [null, null, null]]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [power, setPower] = useState(0);
  const [activeCell, setActiveCell] = useState<{ col: number; row: number } | null>(null);
  const [elemFilter, setElemFilter] = useState('all');
  const [sortBy, setSortBy] = useState<SortKey>('rarity');
  const [constellations, setConstellations] = useState<any[]>([]);
  const [selectedConstellation, setSelectedConstellation] = useState<string | null>(null);
  const [showConstellations, setShowConstellations] = useState(false);
  const [synergies, setSynergies] = useState<any[]>([]);

  useEffect(() => { loadData(); }, []);

  // Load synergies whenever grid changes
  useEffect(() => {
    const loadSynergies = async () => {
      try {
        const syn = await apiCall('/api/synergies/team');
        setSynergies(syn.active_synergies || []);
      } catch (e) {
        setSynergies([]);
      }
    };
    if (filledCount > 0) loadSynergies();
    else setSynergies([]);
  }, [grid]);

  const loadData = async () => {
    try {
      const [uh, team, constData] = await Promise.all([
        apiCall('/api/user/heroes'),
        apiCall('/api/team'),
        apiCall('/api/constellations').catch(() => ({ constellations: [] })),
      ]);
      setHeroes(uh);
      const owned = (constData.constellations || []).filter((c: any) => c.owned);
      setConstellations(owned);
      if (team?.constellation_id) setSelectedConstellation(team.constellation_id);

      if (team?.formation?.length) {
        const ng: (any | null)[][] = [[null, null, null], [null, null, null], [null, null, null]];
        team.formation.forEach((f: any) => {
          if (!f.user_hero_id) return;
          const h = uh.find((x: any) => x.id === f.user_hero_id);
          if (!h) return;
          // Map x to column: x<=2 → 0 (Support), x<=5 → 1 (DPS), x<=8 → 2 (Tank)
          const ci = (f.x || 0) <= 2 ? 0 : (f.x || 0) <= 5 ? 1 : 2;
          const ri = (f.y || 0) <= 2 ? 0 : (f.y || 0) <= 5 ? 1 : 2;
          if (!ng[ci][ri]) ng[ci][ri] = h;
        });
        setGrid(ng);
        setPower(team.total_power || 0);
      }
    } catch (e) {} finally { setLoading(false); }
  };

  const placedIds = useMemo(() => {
    const ids: string[] = [];
    grid.forEach(col => col.forEach(h => { if (h) ids.push(h.id); }));
    return ids;
  }, [grid]);

  const filledCount = placedIds.length;

  // Auto-filter by class based on active column
  const activeClassFilter = activeCell !== null ? COLUMNS[activeCell.col].role : null;

  const filteredHeroes = useMemo(() => {
    let list = heroes.filter((h: any) => !placedIds.includes(h.id));
    // Filter by column class when a slot is selected
    if (activeClassFilter) {
      list = list.filter((h: any) => h.hero_class === activeClassFilter);
    }
    if (elemFilter !== 'all') {
      list = list.filter((h: any) => h.hero_element === elemFilter);
    }
    list.sort((a: any, b: any) => {
      switch (sortBy) {
        case 'rarity': return (b.hero_rarity || 0) - (a.hero_rarity || 0) || (b.stars || 0) - (a.stars || 0);
        case 'level': return (b.level || 0) - (a.level || 0);
        case 'power': return ((b.hero_stats?.hp || 0) + (b.hero_stats?.physical_damage || 0)) - ((a.hero_stats?.hp || 0) + (a.hero_stats?.physical_damage || 0));
        case 'name': return (a.hero_name || '').localeCompare(b.hero_name || '');
        default: return 0;
      }
    });
    return list;
  }, [heroes, placedIds, activeClassFilter, elemFilter, sortBy]);

  const onCellPress = (col: number, row: number) => {
    if (grid[col][row]) {
      // Remove hero
      const ng = grid.map(c => [...c]);
      ng[col][row] = null;
      setGrid(ng);
      setActiveCell(null);
    } else {
      // Select this cell
      setActiveCell(activeCell?.col === col && activeCell?.row === row ? null : { col, row });
    }
  };

  const onHeroSelect = (hero: any) => {
    if (activeCell && !grid[activeCell.col][activeCell.row]) {
      const ng = grid.map(c => [...c]);
      ng[activeCell.col][activeCell.row] = hero;
      setGrid(ng);
      // Find next empty slot in same column first, then other columns
      let next: { col: number; row: number } | null = null;
      for (let r = activeCell.row + 1; r < 3; r++) {
        if (!ng[activeCell.col][r]) { next = { col: activeCell.col, row: r }; break; }
      }
      if (!next) {
        outer: for (let c = 0; c < 3; c++) {
          for (let r = 0; r < 3; r++) {
            if (!ng[c][r]) { next = { col: c, row: r }; break outer; }
          }
        }
      }
      setActiveCell(next);
    } else {
      // Find first empty slot
      for (let c = 0; c < 3; c++) {
        for (let r = 0; r < 3; r++) {
          if (!grid[c][r]) {
            const ng = grid.map(col => [...col]);
            ng[c][r] = hero;
            setGrid(ng);
            return;
          }
        }
      }
      Alert.alert('Squadra piena', 'Rimuovi un eroe prima.');
    }
  };

  const saveTeam = async () => {
    setSaving(true);
    try {
      const formation: any[] = [];
      grid.forEach((col, ci) => {
        col.forEach((h, ri) => {
          if (!h) return;
          formation.push({ x: COLUMNS[ci].x, y: ROW_YS[ri], user_hero_id: h.id });
        });
      });
      const body: any = { formation };
      if (selectedConstellation) body.constellation_id = selectedConstellation;
      const r = await apiCall('/api/team/update-formation', {
        method: 'POST',
        body: JSON.stringify(body),
      });
      setPower(r.total_power || 0);
      await refreshUser();
      Alert.alert('Squadra Salvata!', `Potenza: ${r.total_power?.toLocaleString()}`);
    } catch (e: any) { Alert.alert('Errore', e.message); } finally { setSaving(false); }
  };

  const clearAll = () => { setGrid([[null, null, null], [null, null, null], [null, null, null]]); setActiveCell({ col: 0, row: 0 }); };

  const selConst = constellations.find(c => c.id === selectedConstellation);

  if (loading) return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B']} style={s.container}>
      <ActivityIndicator size="large" color={COLORS.accent} />
    </LinearGradient>
  );

  return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={s.container}>
      {/* Header */}
      <View style={s.header}>
        <Text style={s.title}>FORMAZIONE SQUADRA</Text>
        <View style={s.headerMid}>
          <View style={s.powerBadge}>
            <Text style={s.powerIcon}>{'\u26A1'}</Text>
            <Text style={s.powerVal}>{power.toLocaleString()}</Text>
          </View>
          <Text style={s.teamCount}>{filledCount}/9</Text>
        </View>
        <View style={s.headerRight}>
          <TouchableOpacity onPress={clearAll} style={s.clearBtn}>
            <Text style={s.clearTxt}>SVUOTA</Text>
          </TouchableOpacity>
          <TouchableOpacity onPress={saveTeam} disabled={saving} activeOpacity={0.7}>
            <LinearGradient colors={filledCount > 0 ? [COLORS.accent, '#FF4444'] : ['#333', '#222']} style={[s.saveBtn, saving && { opacity: 0.5 }]}>
              <Text style={s.saveTxt}>{saving ? '...' : '\u2714 SALVA'}</Text>
            </LinearGradient>
          </TouchableOpacity>
        </View>
      </View>

      <View style={s.body}>
        {/* LEFT: 3x3 Grid */}
        <View style={s.gridPanel}>
          {/* Column headers */}
          <View style={s.colHeaders}>
            {COLUMNS.map((col, ci) => (
              <View key={col.role} style={[s.colHeader, { borderBottomColor: col.color }]}>
                <Text style={[s.colIcon]}>{col.icon}</Text>
                <Text style={[s.colLabel, { color: col.color }]}>{col.label}</Text>
                <Text style={s.colBonus}>{col.bonus}</Text>
              </View>
            ))}
          </View>

          {/* Grid rows */}
          {[0, 1, 2].map(row => (
            <View key={row} style={s.gridRow}>
              {COLUMNS.map((col, ci) => {
                const hero = grid[ci][row];
                const isActive = activeCell?.col === ci && activeCell?.row === row;
                const rarCol = hero ? RARITY.colors[Math.min(hero.hero_rarity || 1, 6)] || '#888' : 'transparent';

                return (
                  <TouchableOpacity
                    key={ci}
                    style={[
                      s.cell,
                      hero && { borderColor: rarCol + '80', backgroundColor: (ELEMENTS.colors[hero.hero_element] || '#888') + '06' },
                      isActive && !hero && { borderColor: col.color, backgroundColor: col.color + '0A' },
                    ]}
                    onPress={() => onCellPress(ci, row)}
                    activeOpacity={0.7}
                  >
                    {hero ? (
                      <View style={s.cellFilled}>
                        {hero.hero_image ? (
                          <View style={[s.cellImg, { borderColor: rarCol }]}>
                            <Image source={heroImageSource(hero.hero_image, hero.hero_id, hero.hero_name)} style={s.cellImgInner} />
                          </View>
                        ) : (
                          <AnimatedHeroPortrait imageUrl={null} name={hero.hero_name || '?'} rarity={hero.hero_rarity || 1} element={hero.hero_element} size={36} />
                        )}
                        <View style={s.cellInfo}>
                          <Text style={[s.cellName, { color: rarCol }]} numberOfLines={1}>{hero.hero_name}</Text>
                          <Text style={s.cellMeta}>{ELEMENTS.icons[hero.hero_element] || ''} {CLASSES.icons[hero.hero_class] || ''} Lv.{hero.level}</Text>
                          <View style={s.cellStars}>
                            {(hero.stars || hero.hero_rarity || 1) <= 12
                              ? <StarDisplay stars={hero.stars || hero.hero_rarity || 1} size={6} />
                              : <TranscendenceStars stars={hero.stars || hero.hero_rarity || 1} size={6} />}
                          </View>
                        </View>
                        <View style={s.removeBtn}><Text style={s.removeX}>{'\u00D7'}</Text></View>
                      </View>
                    ) : (
                      <View style={s.cellEmpty}>
                        <View style={[s.emptyCircle, isActive && { borderColor: col.color, backgroundColor: col.color + '15' }]}>
                          <Text style={[s.emptyPlus, isActive && { color: col.color }]}>+</Text>
                        </View>
                        <Text style={[s.emptyLabel, isActive && { color: col.color }]}>
                          {isActive ? 'SCEGLI' : col.role}
                        </Text>
                      </View>
                    )}
                  </TouchableOpacity>
                );
              })}
            </View>
          ))}

          {/* Constellation selector */}
          <TouchableOpacity style={s.constBar} onPress={() => setShowConstellations(!showConstellations)} activeOpacity={0.7}>
            <Text style={s.constLabel}>{'\u264C'} Costellazione:</Text>
            {selConst ? (
              <View style={s.constSelected}>
                <Text style={s.constIcon}>{selConst.icon}</Text>
                <Text style={[s.constName, { color: selConst.color || COLORS.gold }]}>{selConst.name}</Text>
                <Text style={s.constBuff}>
                  {Object.entries(selConst.buff || {}).map(([k, v]: [string, any]) => `${k}+${Math.round(v * 100)}%`).join(' ')}
                </Text>
              </View>
            ) : (
              <Text style={s.constNone}>Nessuna - Tocca per scegliere</Text>
            )}
            <Text style={s.constArrow}>{showConstellations ? '\u25B2' : '\u25BC'}</Text>
          </TouchableOpacity>
          {showConstellations && (
            <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={s.constList}>
              {constellations.map(c => (
                <TouchableOpacity
                  key={c.id}
                  style={[s.constItem, selectedConstellation === c.id && { borderColor: c.color || COLORS.gold, backgroundColor: (c.color || COLORS.gold) + '10' }]}
                  onPress={() => { setSelectedConstellation(c.id); setShowConstellations(false); }}
                >
                  <Text style={s.constItemIcon}>{c.icon}</Text>
                  <Text style={[s.constItemName, { color: c.color || COLORS.gold }]}>{c.name}</Text>
                </TouchableOpacity>
              ))}
            </ScrollView>
          )}

          {/* Active Synergies Display */}
          {synergies.length > 0 && (
            <View style={s.synergiesBar}>
              <Text style={s.synergiesTitle}>{'\u2728'} SINERGIE ATTIVE ({synergies.length})</Text>
              <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={s.synergiesList}>
                {synergies.map((syn: any, i: number) => {
                  const catColor = syn.category === 'mythological' ? '#FFD700' : syn.category === 'elemental' ? '#44AAFF' : '#44DD88';
                  return (
                    <View key={syn.id || i} style={[s.synergyChip, { borderColor: catColor + '50', backgroundColor: catColor + '08' }]}>
                      <Text style={s.synergyIcon}>{syn.icon}</Text>
                      <View>
                        <Text style={[s.synergyName, { color: catColor }]} numberOfLines={1}>{syn.name}</Text>
                        <Text style={s.synergyBuffs} numberOfLines={1}>
                          {Object.entries(syn.buffs || {}).map(([k, v]: [string, any]) => `${k}+${Math.round(v * 100)}%`).join(' ')}
                        </Text>
                      </View>
                    </View>
                  );
                })}
              </ScrollView>
            </View>
          )}
        </View>

        {/* RIGHT: Hero Roster */}
        <View style={s.rosterPanel}>
          {activeClassFilter && (
            <View style={[s.classIndicator, { backgroundColor: CLASSES.colors[activeClassFilter] + '15', borderColor: CLASSES.colors[activeClassFilter] + '40' }]}>
              <Text style={[s.classIndicatorTxt, { color: CLASSES.colors[activeClassFilter] }]}>
                {CLASSES.icons[activeClassFilter]} Solo {activeClassFilter}
              </Text>
            </View>
          )}
          {/* Element filter */}
          <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={s.filterRow}>
            {ELEM_FILTERS.map(f => (
              <TouchableOpacity
                key={f.key}
                style={[s.filterBtn, elemFilter === f.key && { backgroundColor: (ELEMENTS.colors[f.key] || COLORS.accent) + '20', borderColor: (ELEMENTS.colors[f.key] || COLORS.accent) + '60' }]}
                onPress={() => setElemFilter(f.key)}
              >
                <Text style={s.filterIcon}>{f.icon}</Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
          {/* Sort */}
          <View style={s.sortRow}>
            {([['rarity', 'Rarita'], ['level', 'Livello'], ['power', 'Potenza'], ['name', 'Nome']] as [SortKey, string][]).map(([key, label]) => (
              <TouchableOpacity key={key} style={[s.sortBtn, sortBy === key && s.sortActive]} onPress={() => setSortBy(key)}>
                <Text style={[s.sortTxt, sortBy === key && { color: COLORS.accent }]}>{label}</Text>
              </TouchableOpacity>
            ))}
            <Text style={s.rosterCount}>{filteredHeroes.length}</Text>
          </View>
          {/* Hero list */}
          <ScrollView style={s.heroScroll} contentContainerStyle={s.heroScrollContent} showsVerticalScrollIndicator={false}>
            {filteredHeroes.length === 0 ? (
              <Text style={s.noHeroes}>
                {activeClassFilter ? `Nessun ${activeClassFilter} disponibile` : 'Nessun eroe disponibile'}
              </Text>
            ) : (
              <View style={s.heroGrid}>
                {filteredHeroes.map((h: any) => {
                  const rarCol = RARITY.colors[Math.min(h.hero_rarity || 1, 6)] || '#888';
                  const elemCol = ELEMENTS.colors[h.hero_element] || '#888';
                  return (
                    <TouchableOpacity
                      key={h.id}
                      style={[s.heroCard, { borderColor: rarCol + '40' }]}
                      onPress={() => onHeroSelect(h)}
                      activeOpacity={0.7}
                    >
                      {h.hero_image ? (
                        <View style={[s.heroImg, { borderColor: rarCol }]}>
                          <Image source={heroImageSource(h.hero_image, h.hero_id, h.hero_name)} style={s.heroImgInner} />
                        </View>
                      ) : (
                        <View style={[s.heroImgPh, { backgroundColor: elemCol + '15', borderColor: rarCol }]}>
                          <Text style={[s.heroInit, { color: elemCol }]}>{(h.hero_name || '?')[0]}</Text>
                        </View>
                      )}
                      <View style={s.heroInfo}>
                        <Text style={[s.heroName, { color: rarCol }]} numberOfLines={1}>{h.hero_name}</Text>
                        <Text style={s.heroMeta}>{ELEMENTS.icons[h.hero_element] || ''} {CLASSES.icons[h.hero_class] || ''} Lv.{h.level}</Text>
                        <View style={s.heroStars}>
                          {(h.stars || h.hero_rarity || 1) <= 12
                            ? <StarDisplay stars={h.stars || h.hero_rarity || 1} size={6} />
                            : <TranscendenceStars stars={h.stars || h.hero_rarity || 1} size={6} />}
                        </View>
                      </View>
                    </TouchableOpacity>
                  );
                })}
              </View>
            )}
          </ScrollView>
        </View>
      </View>
    </LinearGradient>
  );
}

const s = StyleSheet.create({
  container: { flex: 1 },
  header: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    paddingHorizontal: 12, paddingVertical: 5,
    borderBottomWidth: 1, borderBottomColor: 'rgba(255,107,53,0.15)',
    backgroundColor: 'rgba(7,7,26,0.95)',
  },
  title: { color: '#fff', fontSize: 13, fontWeight: '900', letterSpacing: 1.5 },
  headerMid: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  headerRight: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  powerBadge: {
    flexDirection: 'row', alignItems: 'center', gap: 3,
    backgroundColor: 'rgba(255,215,0,0.1)', paddingHorizontal: 8, paddingVertical: 3,
    borderRadius: 6, borderWidth: 1, borderColor: 'rgba(255,215,0,0.2)',
  },
  powerIcon: { fontSize: 10 },
  powerVal: { color: COLORS.gold, fontSize: 11, fontWeight: '800' },
  teamCount: { color: COLORS.textMuted, fontSize: 10, fontWeight: '700' },
  clearBtn: {
    paddingHorizontal: 8, paddingVertical: 4, borderRadius: 6,
    backgroundColor: 'rgba(255,68,68,0.08)', borderWidth: 1, borderColor: 'rgba(255,68,68,0.2)',
  },
  clearTxt: { color: COLORS.error, fontSize: 8, fontWeight: '800' },
  saveBtn: { paddingHorizontal: 14, paddingVertical: 6, borderRadius: 8 },
  saveTxt: { color: '#fff', fontSize: 10, fontWeight: '900' },
  // Body
  body: { flex: 1, flexDirection: 'row', padding: 6, gap: 6 },
  // Grid Panel
  gridPanel: { width: 340, gap: 3 },
  colHeaders: { flexDirection: 'row', gap: 3, marginBottom: 2 },
  colHeader: { flex: 1, alignItems: 'center', paddingVertical: 3, borderBottomWidth: 2, backgroundColor: 'rgba(255,255,255,0.02)', borderRadius: 4 },
  colIcon: { fontSize: 14 },
  colLabel: { fontSize: 9, fontWeight: '900', letterSpacing: 0.5 },
  colBonus: { fontSize: 6, color: COLORS.textDim, marginTop: 1 },
  // Grid
  gridRow: { flexDirection: 'row', gap: 3 },
  cell: {
    flex: 1, minHeight: 58, borderRadius: 8, borderWidth: 1.5,
    borderColor: 'rgba(255,255,255,0.08)', borderStyle: 'dashed',
    backgroundColor: 'rgba(255,255,255,0.01)', overflow: 'hidden',
  },
  cellFilled: { flex: 1, flexDirection: 'row', alignItems: 'center', padding: 4, gap: 5 },
  cellImg: { width: 38, height: 38, borderRadius: 7, borderWidth: 1.5, overflow: 'hidden', backgroundColor: '#0A0A20' },
  cellImgInner: { width: '100%', height: '100%' },
  cellInfo: { flex: 1 },
  cellName: { fontSize: 8, fontWeight: '900' },
  cellMeta: { fontSize: 7, color: COLORS.textMuted, marginTop: 1 },
  cellStars: { fontSize: 6, color: COLORS.gold, marginTop: 1 },
  removeBtn: {
    position: 'absolute', top: 1, right: 1, width: 14, height: 14, borderRadius: 7,
    backgroundColor: 'rgba(255,68,68,0.8)', alignItems: 'center', justifyContent: 'center',
  },
  removeX: { color: '#fff', fontSize: 9, fontWeight: '900', lineHeight: 11 },
  cellEmpty: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 4 },
  emptyCircle: {
    width: 28, height: 28, borderRadius: 6, backgroundColor: 'rgba(255,255,255,0.03)',
    borderWidth: 1, borderColor: 'rgba(255,255,255,0.08)', borderStyle: 'dashed',
    alignItems: 'center', justifyContent: 'center',
  },
  emptyPlus: { color: COLORS.textDim, fontSize: 16, fontWeight: '300' },
  emptyLabel: { color: COLORS.textDim, fontSize: 6, marginTop: 2, fontWeight: '700' },
  // Constellation
  constBar: {
    flexDirection: 'row', alignItems: 'center', gap: 6,
    padding: 6, borderRadius: 6, backgroundColor: 'rgba(255,215,0,0.04)',
    borderWidth: 1, borderColor: 'rgba(255,215,0,0.15)', marginTop: 2,
  },
  constLabel: { color: COLORS.textMuted, fontSize: 8, fontWeight: '700' },
  constSelected: { flex: 1, flexDirection: 'row', alignItems: 'center', gap: 4 },
  constIcon: { fontSize: 14 },
  constName: { fontSize: 9, fontWeight: '900' },
  constBuff: { fontSize: 7, color: COLORS.textMuted },
  constNone: { flex: 1, color: COLORS.textDim, fontSize: 8, fontStyle: 'italic' },
  constArrow: { color: COLORS.textMuted, fontSize: 8 },
  constList: { gap: 4, paddingVertical: 4 },
  constItem: {
    alignItems: 'center', paddingHorizontal: 8, paddingVertical: 4,
    borderRadius: 6, borderWidth: 1, borderColor: 'rgba(255,255,255,0.08)',
    backgroundColor: 'rgba(255,255,255,0.02)', gap: 2,
  },
  constItemIcon: { fontSize: 16 },
  constItemName: { fontSize: 7, fontWeight: '800' },
  // Synergies
  synergiesBar: {
    backgroundColor: 'rgba(255,215,0,0.04)', borderRadius: 6, padding: 5,
    borderWidth: 1, borderColor: 'rgba(255,215,0,0.12)', marginTop: 2,
  },
  synergiesTitle: { color: COLORS.gold, fontSize: 7, fontWeight: '900', letterSpacing: 0.5, marginBottom: 3 },
  synergiesList: { gap: 4 },
  synergyChip: {
    flexDirection: 'row', alignItems: 'center', gap: 4,
    paddingHorizontal: 6, paddingVertical: 3, borderRadius: 5, borderWidth: 1,
  },
  synergyIcon: { fontSize: 12 },
  synergyName: { fontSize: 7, fontWeight: '800' },
  synergyBuffs: { fontSize: 6, color: COLORS.textMuted },
  // Roster Panel
  rosterPanel: { flex: 1, gap: 3 },
  classIndicator: {
    paddingHorizontal: 8, paddingVertical: 3, borderRadius: 6, borderWidth: 1,
    alignSelf: 'flex-start',
  },
  classIndicatorTxt: { fontSize: 9, fontWeight: '800' },
  filterRow: { gap: 3, paddingBottom: 1 },
  filterBtn: {
    paddingHorizontal: 7, paddingVertical: 3, borderRadius: 5,
    borderWidth: 1, borderColor: 'rgba(255,255,255,0.08)',
    backgroundColor: 'rgba(255,255,255,0.02)',
  },
  filterIcon: { fontSize: 11 },
  sortRow: { flexDirection: 'row', alignItems: 'center', gap: 3 },
  sortBtn: { paddingHorizontal: 6, paddingVertical: 2, borderRadius: 4, backgroundColor: 'rgba(255,255,255,0.02)' },
  sortActive: { backgroundColor: 'rgba(255,107,53,0.1)' },
  sortTxt: { color: COLORS.textMuted, fontSize: 8, fontWeight: '700' },
  rosterCount: { color: COLORS.textDim, fontSize: 8, marginLeft: 'auto', fontWeight: '600' },
  heroScroll: { flex: 1 },
  heroScrollContent: { paddingBottom: 8 },
  heroGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 3 },
  noHeroes: { color: COLORS.textDim, fontSize: 9, textAlign: 'center', padding: 16 },
  heroCard: {
    width: 105, flexDirection: 'row', alignItems: 'center', gap: 4,
    padding: 4, borderRadius: 6, borderWidth: 1, backgroundColor: 'rgba(255,255,255,0.02)',
  },
  heroImg: { width: 32, height: 32, borderRadius: 5, borderWidth: 1.5, overflow: 'hidden', backgroundColor: '#0A0A20' },
  heroImgInner: { width: '100%', height: '100%' },
  heroImgPh: { width: 32, height: 32, borderRadius: 5, borderWidth: 1.5, alignItems: 'center', justifyContent: 'center' },
  heroInit: { fontSize: 14, fontWeight: '900' },
  heroInfo: { flex: 1 },
  heroName: { fontSize: 7, fontWeight: '900' },
  heroMeta: { fontSize: 7, color: COLORS.textMuted, marginTop: 1 },
  heroStars: { fontSize: 6, color: COLORS.gold, marginTop: 1 },
});
