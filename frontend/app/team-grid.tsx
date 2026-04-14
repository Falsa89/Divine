import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert, ActivityIndicator, Image } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { COLORS } from '../constants/theme';
import { useRouter } from 'expo-router';
import Animated, { FadeIn, FadeInDown } from 'react-native-reanimated';
import { apiCall } from '../utils/api';
import { useAuth } from '../context/AuthContext';
import { useNotification } from '../context/NotificationContext';

const COLUMNS = [
  { id: 0, name: 'SUPPORTO', color: '#44cc88', buffs: '+15% VEL, +20% Cure', icon: '\u2764\uFE0F' },
  { id: 1, name: 'DPS', color: '#ff4444', buffs: '+15% DMG, +20% CRIT DMG', icon: '\u2694\uFE0F' },
  { id: 2, name: 'TANK', color: '#4488ff', buffs: '+20% HP, +15% DEF', icon: '\u26E8\uFE0F' },
];
const ROWS = [0, 1, 2];

export default function TeamGridScreen() {
  const router = useRouter();
  const { refreshUser } = useAuth();
  const { showNotification } = useNotification();
  const [heroes, setHeroes] = useState<any[]>([]);
  const [team, setTeam] = useState<any>(null);
  const [formation, setFormation] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);
  const [selectedSlot, setSelectedSlot] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => { load(); }, []);

  const load = async () => {
    try {
      const [h, t] = await Promise.all([
        apiCall('/api/user/heroes'),
        apiCall('/api/team'),
      ]);
      setHeroes(h || []);
      setTeam(t);
      // Parse existing formation into grid
      const grid: Record<string, any> = {};
      if (t?.formation) {
        for (const pos of t.formation) {
          if (pos.user_hero_id) {
            const key = `${pos.x}_${pos.y}`;
            const hero = (h || []).find((he: any) => he.id === pos.user_hero_id);
            grid[key] = { ...pos, hero };
          }
        }
      }
      setFormation(grid);
    } catch (e) {}
    finally { setLoading(false); }
  };

  const placeHero = (heroData: any) => {
    if (!selectedSlot) return;
    // Check max 6
    const currentCount = Object.keys(formation).length;
    if (currentCount >= 6 && !formation[selectedSlot]) {
      Alert.alert('Limite', 'Massimo 6 eroi nel team!');
      return;
    }
    // Remove hero from other slot if already placed
    const newForm = { ...formation };
    for (const [key, val] of Object.entries(newForm)) {
      if (val?.user_hero_id === heroData.id) {
        delete newForm[key];
      }
    }
    const [x, y] = selectedSlot.split('_').map(Number);
    newForm[selectedSlot] = { x, y, user_hero_id: heroData.id, hero: heroData };
    setFormation(newForm);
    setSelectedSlot(null);
  };

  const removeHero = (key: string) => {
    const newForm = { ...formation };
    delete newForm[key];
    setFormation(newForm);
  };

  const saveFormation = async () => {
    setSaving(true);
    try {
      const formationArr = Object.values(formation).map((v: any) => ({
        x: v.x, y: v.y, user_hero_id: v.user_hero_id,
      }));
      const r = await apiCall('/api/team/update-formation', {
        method: 'POST',
        body: JSON.stringify({ formation: formationArr }),
      });
      await refreshUser();
      showNotification({
        type: 'success',
        title: 'Team Salvato!',
        message: `Potenza: ${r.total_power?.toLocaleString()} | Formazioni: ${r.active_formations?.length || 0}`,
      });
    } catch (e: any) { Alert.alert('Errore', e.message); }
    finally { setSaving(false); }
  };

  if (loading) return <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}><ActivityIndicator size="large" color="#ff6b35" /></LinearGradient>;

  const placedIds = new Set(Object.values(formation).map((v: any) => v.user_hero_id));
  const available = heroes.filter((h: any) => !placedIds.has(h.id));
  const heroCount = Object.keys(formation).length;

  return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}>
      <View style={s.hdr}>
        <TouchableOpacity onPress={() => router.back()}>
          <Text style={s.back}>{'\u2190'}</Text>
        </TouchableOpacity>
        <Text style={s.title}>FORMAZIONE TEAM</Text>
        <Text style={s.heroCountTxt}>{heroCount}/6</Text>
        <TouchableOpacity style={[s.saveBtn, saving && { opacity: 0.5 }]} onPress={saveFormation} disabled={saving}>
          <Text style={s.saveTxt}>{saving ? '...' : 'SALVA'}</Text>
        </TouchableOpacity>
      </View>

      <View style={s.main}>
        {/* Grid */}
        <View style={s.gridWrap}>
          {/* Column headers */}
          <View style={s.colHeaders}>
            {COLUMNS.map(col => (
              <View key={col.id} style={[s.colHeader, { borderBottomColor: col.color }]}>
                <Text style={[s.colName, { color: col.color }]}>{col.icon} {col.name}</Text>
                <Text style={s.colBuffs}>{col.buffs}</Text>
              </View>
            ))}
          </View>
          {/* Grid cells */}
          {ROWS.map(row => (
            <View key={row} style={s.gridRow}>
              {COLUMNS.map(col => {
                const key = `${col.id}_${row}`;
                const cell = formation[key];
                const isSelected = selectedSlot === key;
                return (
                  <TouchableOpacity
                    key={key}
                    style={[
                      s.cell,
                      { borderColor: col.color + (cell ? 'aa' : '30') },
                      isSelected && { borderColor: '#fff', backgroundColor: 'rgba(255,255,255,0.08)' },
                      cell && { backgroundColor: col.color + '10' },
                    ]}
                    onPress={() => cell ? removeHero(key) : setSelectedSlot(isSelected ? null : key)}
                    onLongPress={() => cell && removeHero(key)}
                  >
                    {cell?.hero ? (
                      <View style={s.cellHero}>
                        {cell.hero.hero_image && (
                          <Image source={{ uri: cell.hero.hero_image }} style={s.cellImg} />
                        )}
                        <Text style={s.cellName} numberOfLines={1}>{cell.hero.hero_name}</Text>
                        <Text style={s.cellStars}>{cell.hero.stars || cell.hero.hero_rarity}\u2B50</Text>
                      </View>
                    ) : (
                      <Text style={[s.cellEmpty, isSelected && { color: '#fff' }]}>
                        {isSelected ? 'Seleziona\neroe \u2193' : '+'}
                      </Text>
                    )}
                  </TouchableOpacity>
                );
              })}
            </View>
          ))}
        </View>

        {/* Hero selector */}
        <ScrollView style={s.selector} contentContainerStyle={s.selectorContent}>
          <Text style={s.selTitle}>{selectedSlot ? 'Scegli un eroe:' : 'Tocca uno slot vuoto'}</Text>
          {selectedSlot && available.map((h: any) => (
            <TouchableOpacity key={h.id} style={s.selHero} onPress={() => placeHero(h)}>
              {h.hero_image && <Image source={{ uri: h.hero_image }} style={s.selImg} />}
              <View style={s.selInfo}>
                <Text style={s.selName}>{h.hero_name}</Text>
                <Text style={s.selMeta}>{h.stars || h.hero_rarity}\u2B50 Lv.{h.level || 1} | {h.hero_class}</Text>
              </View>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>
    </LinearGradient>
  );
}

const s = StyleSheet.create({
  c: { flex: 1, backgroundColor:'transparent' },
  hdr: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 10, paddingVertical: 5, borderBottomWidth: 1, borderBottomColor: 'rgba(255,107,53,0.2)', gap: 8 },
  back: { color: '#ff6b35', fontSize: 20, fontWeight: '700' },
  title: { color: '#fff', fontSize: 13, fontWeight: '800', letterSpacing: 1, flex: 1 },
  heroCountTxt: { color: '#ffd700', fontSize: 12, fontWeight: '800' },
  saveBtn: { paddingHorizontal: 14, paddingVertical: 5, borderRadius: 6, backgroundColor: 'rgba(68,204,68,0.15)', borderWidth: 1, borderColor: '#44cc44' },
  saveTxt: { color: '#44cc44', fontSize: 11, fontWeight: '900' },
  main: { flex: 1, flexDirection: 'row' },
  // Grid
  gridWrap: { flex: 2, padding: 6, gap: 3 },
  colHeaders: { flexDirection: 'row', gap: 3 },
  colHeader: { flex: 1, alignItems: 'center', paddingVertical: 3, borderBottomWidth: 2 },
  colName: { fontSize: 9, fontWeight: '900', letterSpacing: 0.5 },
  colBuffs: { color: '#888', fontSize: 6, textAlign: 'center' },
  gridRow: { flexDirection: 'row', gap: 3, flex: 1 },
  cell: {
    flex: 1, borderRadius: 8, borderWidth: 1.5,
    backgroundColor: 'rgba(255,255,255,0.02)',
    alignItems: 'center', justifyContent: 'center',
    minHeight: 60,
  },
  cellHero: { alignItems: 'center', gap: 1, padding: 2 },
  cellImg: { width: 32, height: 32, borderRadius: 6 },
  cellName: { color: '#fff', fontSize: 7, fontWeight: '700', textAlign: 'center' },
  cellStars: { color: '#ffd700', fontSize: 7 },
  cellEmpty: { color: '#444', fontSize: 18, textAlign: 'center' },
  // Selector
  selector: { flex: 1, borderLeftWidth: 1, borderLeftColor: 'rgba(255,255,255,0.05)' },
  selectorContent: { padding: 4, gap: 3 },
  selTitle: { color: '#888', fontSize: 9, fontWeight: '700', textAlign: 'center', paddingVertical: 3 },
  selHero: { flexDirection: 'row', alignItems: 'center', padding: 4, borderRadius: 6, backgroundColor: 'rgba(255,255,255,0.03)', borderWidth: 1, borderColor: 'rgba(255,255,255,0.06)', gap: 4 },
  selImg: { width: 26, height: 26, borderRadius: 4 },
  selInfo: { flex: 1 },
  selName: { color: '#fff', fontSize: 9, fontWeight: '700' },
  selMeta: { color: '#888', fontSize: 7 },
});
