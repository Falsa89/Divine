import React, { useState, useEffect } from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet, ScrollView,
  ActivityIndicator, Alert, Modal,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import Animated, { FadeInDown } from 'react-native-reanimated';
import { apiCall } from '../utils/api';
import { useAuth } from '../context/AuthContext';
import useServerScope from '../src/hooks/useServerScope';
import ScreenHeader from '../components/ui/ScreenHeader';
import GradientButton from '../components/ui/GradientButton';
import TabSelector from '../components/ui/TabSelector';
import { COLORS, RARITY } from '../constants/theme';

const TABS = [
  { key: 'all', label: 'Tutti', icon: '\uD83C\uDF92' },
  { key: 'exp', label: 'EXP', icon: '\uD83E\uDDEA' },
  { key: 'skill', label: 'Skill', icon: '\uD83D\uDCDC' },
  { key: 'shards', label: 'Frammenti', icon: '\u2B50' },
];

const RARITY_COLORS: Record<number, string> = {
  1: '#8899AA', 2: '#44BB66', 3: '#4499FF', 4: '#BB55FF', 5: '#FF5544',
};

export default function InventoryScreen() {
  const router = useRouter();
  const { refreshUser } = useAuth();
  // Pack 91 — server scope canonico per inventory mutation consumer.
  const { selected_server_id, loading: scopeLoading } = useServerScope();
  const [items, setItems] = useState<any[]>([]);
  const [shards, setShards] = useState<any[]>([]);
  const [heroes, setHeroes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState('all');
  const [useModal, setUseModal] = useState(false);
  const [selectedItem, setSelectedItem] = useState<any>(null);
  const [selectedHero, setSelectedHero] = useState<any>(null);
  const [useQty, setUseQty] = useState(1);
  const [acting, setActing] = useState(false);
  const [serverBlocker, setServerBlocker] = useState<string | null>(null);

  // Pack 91 — rifetcha quando cambia il server selezionato. Niente silent s1.
  useEffect(() => { if (!scopeLoading) loadAll(); }, [scopeLoading, selected_server_id]);

  const loadAll = async () => {
    setLoading(true);
    setServerBlocker(null);
    try {
      // Pack 91 — passa server_id se disponibile. Pack 89 GET inventory è strict
      // server-scoped: se manca server_id il backend ritorna legacy non-player path.
      // Per essere consistenti col Pack 91, il frontend richiede sempre server_id.
      if (!selected_server_id) {
        setItems([]);
        setShards([]);
        setHeroes([]);
        setServerBlocker('NO_SERVER_SELECTED');
        return;
      }
      const qs = `server_id=${encodeURIComponent(selected_server_id)}`;
      const [inv, uh] = await Promise.all([
        apiCall(`/api/inventory?${qs}`),
        apiCall('/api/user/heroes'),
      ]);
      setItems(inv.items || []);
      setHeroes(uh || []);
      // Extract shards from user heroes data
      const shardList: any[] = [];
      for (const h of (uh || [])) {
        if (h.fragments && h.fragments > 0) {
          shardList.push({
            item_id: `shard_${h.hero_id}`,
            name: `Frammento ${h.hero_name}`,
            icon: '\u2B50',
            quantity: h.fragments,
            rarity: h.hero_rarity || 1,
            type: 'shard',
            hero_name: h.hero_name,
          });
        }
      }
      setShards(shardList);
    } catch (e: any) {
      const msg = e?.message || '';
      if (msg.includes('PLAYER_SERVER_PROFILE_REQUIRED')) {
        setServerBlocker('PLAYER_SERVER_PROFILE_REQUIRED');
      } else if (msg.includes('SERVER_ID_REQUIRED')) {
        setServerBlocker('SERVER_ID_REQUIRED');
      }
    } finally { setLoading(false); }
  };

  const getFiltered = () => {
    let all = [...items];
    if (tab === 'exp') return all.filter(i => i.item_id?.startsWith('exp_'));
    if (tab === 'skill') return all.filter(i => i.item_id?.startsWith('skill_') || i.item_id?.startsWith('element_'));
    if (tab === 'shards') return shards;
    return [...all, ...shards];
  };

  const openUseModal = (item: any) => {
    if (!item.item_id?.startsWith('exp_') && !item.item_id?.startsWith('skill_')) return;
    setSelectedItem(item);
    setSelectedHero(null);
    setUseQty(1);
    setUseModal(true);
  };

  const useItem = async () => {
    if (!selectedItem || !selectedHero) return;
    // Pack 91 — blocca use-exp se manca server selezionato.
    if (!selected_server_id) {
      Alert.alert('Seleziona un server', 'Devi prima entrare in un server.', [
        { text: 'Vai a Server', onPress: () => router.push('/servers' as any) },
        { text: 'Annulla', style: 'cancel' },
      ]);
      return;
    }
    setActing(true);
    try {
      if (selectedItem.item_id.startsWith('exp_')) {
        const qs = `server_id=${encodeURIComponent(selected_server_id)}`;
        const r = await apiCall(`/api/inventory/use-exp?${qs}`, {
          method: 'POST',
          body: JSON.stringify({
            user_hero_id: selectedHero.id,
            item_id: selectedItem.item_id,
            quantity: useQty,
          }),
        });
        await refreshUser();
        await loadAll();
        setUseModal(false);
        Alert.alert(
          r.leveled_up ? 'Livello Aumentato!' : 'EXP Guadagnata!',
          `${r.hero_name}: +${r.exp_gained?.toLocaleString()} EXP${r.leveled_up ? `\nLv.${r.old_level} \u2192 Lv.${r.new_level}` : ''}`
        );
      }
    } catch (e: any) {
      const msg = e?.message || '';
      if (msg.includes('SERVER_ID_REQUIRED')) {
        Alert.alert('Server richiesto', 'Operazione bloccata: server non selezionato.');
      } else if (msg.includes('PLAYER_SERVER_PROFILE_REQUIRED')) {
        Alert.alert('Profilo server mancante', 'Devi prima creare il profilo per questo server.', [
          { text: 'Vai a Server', onPress: () => router.push('/servers' as any) },
          { text: 'Annulla', style: 'cancel' },
        ]);
      } else {
        Alert.alert('Errore', msg || 'Errore di rete');
      }
    }
    finally { setActing(false); }
  };

  const filtered = getFiltered();

  if (loading) return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B']} style={s.c}>
      <ActivityIndicator size="large" color={COLORS.gold} />
    </LinearGradient>
  );

  return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={s.c}>
      <ScreenHeader title="Inventario" titleColor={COLORS.gold} showBack
        rightContent={
          <View style={s.countBadge}>
            <Text style={s.countText}>{items.length + shards.length} oggetti</Text>
          </View>
        }
      />
      <TabSelector tabs={TABS} active={tab} onChange={setTab} accentColor={COLORS.gold} />

      {/* Pack 91 — blocker UI server-scope (no silent s1, no account-wide fallback) */}
      {serverBlocker && (
        <View style={s.scopeBanner}>
          <Text style={s.scopeBannerIcon}>{'\u26A0\uFE0F'}</Text>
          <Text style={s.scopeBannerTxt}>
            {serverBlocker === 'NO_SERVER_SELECTED' && 'Nessun server selezionato — entra in un server per vedere l\'inventario.'}
            {serverBlocker === 'PLAYER_SERVER_PROFILE_REQUIRED' && 'Profilo server mancante — vai alla schermata server per crearlo.'}
            {serverBlocker === 'SERVER_ID_REQUIRED' && 'Server richiesto — operazione bloccata.'}
          </Text>
          <TouchableOpacity onPress={() => router.push('/servers' as any)} style={s.scopeBannerBtn}>
            <Text style={s.scopeBannerBtnTxt}>SERVER</Text>
          </TouchableOpacity>
        </View>
      )}

      <ScrollView contentContainerStyle={s.grid}>
        {filtered.length === 0 && (
          <View style={s.empty}>
            <Text style={s.emptyIcon}>{'\uD83C\uDF92'}</Text>
            <Text style={s.emptyText}>Inventario vuoto</Text>
            <Text style={s.emptyHint}>Compra oggetti dal Negozio Oggetti o vinci battaglie!</Text>
          </View>
        )}
        {filtered.map((item, i) => {
          const col = RARITY_COLORS[item.rarity] || '#888';
          const isExp = item.item_id?.startsWith('exp_');
          const isSkill = item.item_id?.startsWith('skill_') || item.item_id?.startsWith('element_');
          const isShard = item.type === 'shard';
          return (
            <Animated.View key={item.item_id + '_' + i} entering={FadeInDown.delay(i * 20).duration(200)}>
              <TouchableOpacity
                onPress={() => (isExp || isSkill) ? openUseModal(item) : null}
                activeOpacity={isExp || isSkill ? 0.7 : 1}
                style={s.itemOuter}
              >
                <LinearGradient
                  colors={[col + '12', 'rgba(255,255,255,0.02)']}
                  style={[s.itemCard, { borderColor: col + '30' }]}
                >
                  <View style={[s.iconWrap, { backgroundColor: col + '20' }]}>
                    <Text style={s.icon}>{item.icon}</Text>
                  </View>
                  <View style={s.itemInfo}>
                    <Text style={[s.itemName, { color: col }]} numberOfLines={1}>{item.name}</Text>
                    <Text style={s.itemMeta}>
                      {isExp ? `+${item.exp?.toLocaleString()} EXP` : ''}
                      {isShard ? `Eroe: ${item.hero_name}` : ''}
                      {isSkill ? 'Materiale Skill' : ''}
                    </Text>
                  </View>
                  <View style={s.qtyWrap}>
                    <Text style={s.qty}>x{item.quantity}</Text>
                  </View>
                  {(isExp || isSkill) && (
                    <View style={[s.useBadge, { backgroundColor: col + '20' }]}>
                      <Text style={[s.useText, { color: col }]}>USA</Text>
                    </View>
                  )}
                </LinearGradient>
              </TouchableOpacity>
            </Animated.View>
          );
        })}
      </ScrollView>

      {/* Shop Button */}
      <View style={s.shopBtnWrap}>
        <TouchableOpacity onPress={() => router.push('/item-shop' as any)} activeOpacity={0.7}>
          <LinearGradient colors={[COLORS.accent, '#FF4444']} style={s.shopBtn}>
            <Text style={s.shopBtnTxt}>{'\uD83D\uDED2'} NEGOZIO OGGETTI</Text>
          </LinearGradient>
        </TouchableOpacity>
      </View>

      {/* Use Item Modal */}
      <Modal visible={useModal} transparent animationType="fade">
        <TouchableOpacity style={s.modalBg} activeOpacity={1} onPress={() => setUseModal(false)}>
          <TouchableOpacity activeOpacity={1} onPress={(e) => e.stopPropagation()}>
            <LinearGradient colors={['rgba(15,15,45,0.98)', 'rgba(10,10,35,0.98)']} style={s.modal}>
              <Text style={s.modalTitle}>Usa {selectedItem?.name}</Text>
              <Text style={s.modalSub}>
                {selectedItem?.item_id?.startsWith('exp_') ? `+${((selectedItem?.exp || 0) * useQty).toLocaleString()} EXP` : 'Seleziona eroe'}
              </Text>

              {/* Quantity selector */}
              <View style={s.qtyRow}>
                <TouchableOpacity style={s.qtyBtn} onPress={() => setUseQty(Math.max(1, useQty - 1))}>
                  <Text style={s.qtyBtnTxt}>-</Text>
                </TouchableOpacity>
                <Text style={s.qtyNum}>{useQty}</Text>
                <TouchableOpacity style={s.qtyBtn} onPress={() => setUseQty(Math.min(selectedItem?.quantity || 1, useQty + 1))}>
                  <Text style={s.qtyBtnTxt}>+</Text>
                </TouchableOpacity>
                <TouchableOpacity style={s.qtyMaxBtn} onPress={() => setUseQty(selectedItem?.quantity || 1)}>
                  <Text style={s.qtyMaxTxt}>MAX</Text>
                </TouchableOpacity>
              </View>

              {/* Hero selector */}
              <Text style={s.heroSelTitle}>Seleziona Eroe:</Text>
              <ScrollView style={s.heroList} contentContainerStyle={s.heroListC}>
                {heroes.sort((a: any, b: any) => (a.level || 0) - (b.level || 0)).slice(0, 20).map((h: any) => (
                  <TouchableOpacity
                    key={h.id}
                    style={[s.heroOpt, selectedHero?.id === h.id && s.heroOptSel]}
                    onPress={() => setSelectedHero(h)}
                  >
                    <Text style={s.heroOptName} numberOfLines={1}>{h.hero_name || '?'}</Text>
                    <Text style={s.heroOptLvl}>Lv.{h.level || 1}</Text>
                  </TouchableOpacity>
                ))}
              </ScrollView>

              <View style={s.modalBtns}>
                <GradientButton
                  title={acting ? '...' : 'USA OGGETTO'}
                  onPress={useItem}
                  variant="gold"
                  size="lg"
                  disabled={!selectedHero || acting}
                  loading={acting}
                />
                <GradientButton title="ANNULLA" onPress={() => setUseModal(false)} variant="outline" />
              </View>
            </LinearGradient>
          </TouchableOpacity>
        </TouchableOpacity>
      </Modal>
    </LinearGradient>
  );
}

const s = StyleSheet.create({
  c: { flex: 1 },
  countBadge: { backgroundColor: 'rgba(255,215,0,0.15)', paddingHorizontal: 10, paddingVertical: 3, borderRadius: 12, borderWidth: 1, borderColor: 'rgba(255,215,0,0.25)' },
  countText: { color: COLORS.gold, fontSize: 10, fontWeight: '700' },
  grid: { padding: 8, gap: 4, paddingBottom: 80 },
  empty: { alignItems: 'center', justifyContent: 'center', paddingVertical: 50 },
  emptyIcon: { fontSize: 40 },
  emptyText: { color: COLORS.textMuted, fontSize: 14, marginTop: 8 },
  emptyHint: { color: COLORS.textDim, fontSize: 10, marginTop: 4, textAlign: 'center' },
  itemOuter: { borderRadius: 10, overflow: 'hidden' },
  itemCard: { flexDirection: 'row', alignItems: 'center', padding: 10, borderRadius: 10, borderWidth: 1, gap: 10 },
  iconWrap: { width: 40, height: 40, borderRadius: 10, alignItems: 'center', justifyContent: 'center' },
  icon: { fontSize: 22 },
  itemInfo: { flex: 1 },
  itemName: { fontSize: 12, fontWeight: '800' },
  itemMeta: { color: COLORS.textMuted, fontSize: 9, marginTop: 2 },
  qtyWrap: { alignItems: 'center' },
  qty: { color: '#fff', fontSize: 16, fontWeight: '900' },
  useBadge: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 8 },
  useText: { fontSize: 9, fontWeight: '900', letterSpacing: 0.5 },
  shopBtnWrap: { position: 'absolute', bottom: 70, right: 16 },
  shopBtn: { paddingHorizontal: 18, paddingVertical: 10, borderRadius: 12 },
  shopBtnTxt: { color: '#fff', fontSize: 12, fontWeight: '900', letterSpacing: 0.5 },
  // Modal
  modalBg: { flex: 1, backgroundColor: 'rgba(0,0,0,0.85)', justifyContent: 'center', alignItems: 'center' },
  modal: { width: 420, maxHeight: 500, borderRadius: 18, padding: 16, borderWidth: 1, borderColor: COLORS.borderAccent },
  modalTitle: { color: '#fff', fontSize: 16, fontWeight: '900', textAlign: 'center' },
  modalSub: { color: COLORS.gold, fontSize: 12, fontWeight: '700', textAlign: 'center', marginTop: 4 },
  qtyRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 12, marginTop: 12 },
  qtyBtn: { width: 36, height: 36, borderRadius: 18, backgroundColor: 'rgba(255,255,255,0.08)', alignItems: 'center', justifyContent: 'center', borderWidth: 1, borderColor: 'rgba(255,255,255,0.15)' },
  qtyBtnTxt: { color: '#fff', fontSize: 18, fontWeight: '700' },
  qtyNum: { color: COLORS.gold, fontSize: 24, fontWeight: '900', minWidth: 40, textAlign: 'center' },
  qtyMaxBtn: { paddingHorizontal: 12, paddingVertical: 6, borderRadius: 8, backgroundColor: 'rgba(255,215,0,0.12)', borderWidth: 1, borderColor: 'rgba(255,215,0,0.25)' },
  qtyMaxTxt: { color: COLORS.gold, fontSize: 10, fontWeight: '900' },
  heroSelTitle: { color: COLORS.textSecondary, fontSize: 11, fontWeight: '700', marginTop: 10, marginBottom: 4 },
  heroList: { maxHeight: 180 },
  heroListC: { flexDirection: 'row', flexWrap: 'wrap', gap: 4 },
  heroOpt: { paddingHorizontal: 10, paddingVertical: 6, borderRadius: 8, backgroundColor: 'rgba(255,255,255,0.04)', borderWidth: 1, borderColor: 'rgba(255,255,255,0.08)' },
  heroOptSel: { borderColor: COLORS.gold, backgroundColor: 'rgba(255,215,0,0.1)' },
  heroOptName: { color: '#fff', fontSize: 10, fontWeight: '700', maxWidth: 80 },
  heroOptLvl: { color: COLORS.textMuted, fontSize: 8 },
  modalBtns: { flexDirection: 'row', gap: 10, marginTop: 12, justifyContent: 'center' },
  // Pack 91 — server scope banner
  scopeBanner: { flexDirection: 'row', alignItems: 'center', gap: 8, paddingHorizontal: 12, paddingVertical: 10, marginHorizontal: 8, marginTop: 8, borderRadius: 8, backgroundColor: 'rgba(255,165,0,0.10)', borderWidth: 1, borderColor: 'rgba(255,165,0,0.45)' },
  scopeBannerIcon: { fontSize: 16 },
  scopeBannerTxt: { flex: 1, color: '#FFD089', fontSize: 11, lineHeight: 15, fontWeight: '600' },
  scopeBannerBtn: { paddingHorizontal: 12, paddingVertical: 6, borderRadius: 6, backgroundColor: 'rgba(255,215,0,0.18)', borderWidth: 1, borderColor: 'rgba(255,215,0,0.4)' },
  scopeBannerBtnTxt: { color: COLORS.gold, fontSize: 10, fontWeight: '900', letterSpacing: 0.5 },
});
