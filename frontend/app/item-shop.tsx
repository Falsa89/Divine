import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, ActivityIndicator, Alert } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import Animated, { FadeInDown } from 'react-native-reanimated';
import { apiCall } from '../utils/api';
import { useAuth } from '../context/AuthContext';
import useServerScope from '../src/hooks/useServerScope';
import ScreenHeader from '../components/ui/ScreenHeader';
import ResourceBadge from '../components/ui/ResourceBadge';
import { COLORS } from '../constants/theme';

// Pre-QA Stabilization 115D — screen-entry/deeplink guard.
import PreQaScreenGate, { isScreenGated } from '../src/components/PreQaScreenGate';
const RARITY_COL: Record<number, string> = { 1: '#8899AA', 2: '#44BB66', 3: '#4499FF', 4: '#BB55FF', 5: '#FF5544' };

export default function ItemShopScreen() {
  // Pre-QA Stabilization 115D — fail-closed screen-entry/deeplink guard.
  if (isScreenGated('/item-shop')) return <PreQaScreenGate route="/item-shop" />;
  const router = useRouter();
  const { refreshUser } = useAuth();
  // Pack 91 — adozione canonical server scope sui frontend mutation consumer.
  // Nessun silent "s1": se manca selected_server_id, l'acquisto è bloccato
  // e l'utente è rimandato alla selezione server.
  const { selected_server_id, loading: scopeLoading } = useServerScope();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [buying, setBuying] = useState('');
  const [filter, setFilter] = useState('all');

  // BATCH_1_V2 Track E \u2014 lock acquisti item-shop. Nessun cambio prezzi/item.
  const ITEM_SHOP_LOCKED_V2 = true;

  useEffect(() => { load(); }, []);
  const load = async () => {
    try { const d = await apiCall('/api/item-shop'); setData(d); }
    catch (e) {} finally { setLoading(false); }
  };

  const buy = async (itemId: string, name: string, qty: number = 1) => {
    if (ITEM_SHOP_LOCKED_V2) return; // lock UI safe
    // Pack 91 — server_id REQUIRED, no silent s1, no account-wide fallback.
    if (!selected_server_id) {
      Alert.alert(
        'Seleziona un server',
        'Devi prima entrare in un server prima di acquistare. Vai alla schermata server.',
        [
          { text: 'Vai a Server', onPress: () => router.push('/servers' as any) },
          { text: 'Annulla', style: 'cancel' },
        ]
      );
      return;
    }
    setBuying(itemId);
    try {
      const qs = `server_id=${encodeURIComponent(selected_server_id)}`;
      await apiCall(`/api/item-shop/buy?${qs}`, { method: 'POST', body: JSON.stringify({ item_id: itemId, quantity: qty }) });
      await refreshUser(); await load();
      Alert.alert('Acquistato!', `${qty}x ${name}`);
    } catch (e: any) {
      // Pack 91 — gestione esplicita dei blocker server-scope.
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
    finally { setBuying(''); }
  };

  const buyMulti = (item: any) => {
    if (ITEM_SHOP_LOCKED_V2) return; // lock UI safe
    Alert.alert(`Compra ${item.name}`, 'Quanti?', [
      { text: '1', onPress: () => buy(item.item_id, item.name, 1) },
      { text: '5', onPress: () => buy(item.item_id, item.name, 5) },
      { text: '10', onPress: () => buy(item.item_id, item.name, 10) },
      { text: '50', onPress: () => buy(item.item_id, item.name, 50) },
      { text: 'Annulla', style: 'cancel' },
    ]);
  };

  if (loading) return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B']} style={s.c}>
      <ActivityIndicator size="large" color={COLORS.gold} />
    </LinearGradient>
  );

  const items = data?.items || [];
  const filtered = filter === 'all' ? items : items.filter((i: any) => {
    if (filter === 'exp') return i.item_id?.startsWith('exp_');
    if (filter === 'skill') return i.item_id?.startsWith('skill_') || i.item_id?.startsWith('element_');
    return true;
  });

  return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={s.c}>
      <ScreenHeader title="Negozio Oggetti" titleColor={COLORS.gold} showBack
        rightContent={
          <View style={s.resRow}>
            <ResourceBadge icon={'\uD83D\uDCB0'} value={data?.gold || 0} compact />
            <ResourceBadge icon={'\uD83D\uDC8E'} value={data?.gems || 0} compact />
          </View>
        }
      />

      {/* Filter */}
      <View style={s.filterRow}>
        {[{ k: 'all', l: 'Tutti' }, { k: 'exp', l: 'EXP' }, { k: 'skill', l: 'Skill' }].map(f => (
          <TouchableOpacity key={f.k} style={[s.fBtn, filter === f.k && s.fBtnA]} onPress={() => setFilter(f.k)}>
            <Text style={[s.fTxt, filter === f.k && s.fTxtA]}>{f.l}</Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* BATCH_1_V2 Track E \u2014 banner lock item shop */}
      {ITEM_SHOP_LOCKED_V2 && (
        <View style={s.lockBannerV2}>
          <Text style={s.lockBannerIconV2}>{'\uD83D\uDD12'}</Text>
          <Text style={s.lockBannerTxtV2}>
            Negozio oggetti in revisione \u2014 acquisti temporaneamente disabilitati.
            Listino visibile in anteprima informativa.
          </Text>
        </View>
      )}

      <ScrollView contentContainerStyle={s.list}>
        {filtered.map((item: any, i: number) => {
          const col = RARITY_COL[item.rarity] || '#888';
          const isGems = item.currency === 'gems';
          const disabledByLock = ITEM_SHOP_LOCKED_V2;
          return (
            <Animated.View key={item.item_id} entering={FadeInDown.delay(i * 25).duration(200)}>
              <TouchableOpacity onPress={() => !disabledByLock && buyMulti(item)} activeOpacity={disabledByLock ? 1 : 0.7} disabled={disabledByLock}>
                <LinearGradient
                  colors={[col + '10', 'rgba(255,255,255,0.02)']}
                  style={[s.card, { borderColor: col + '25' }, (!item.can_afford || disabledByLock) && { opacity: 0.5 }]}
                >
                  <View style={[s.cardIcon, { backgroundColor: col + '18' }]}>
                    <Text style={s.cardIconTxt}>{item.icon}</Text>
                  </View>
                  <View style={s.cardInfo}>
                    <Text style={[s.cardName, { color: col }]}>{item.name}</Text>
                    <Text style={s.cardDesc}>
                      {item.exp ? `+${item.exp.toLocaleString()} EXP` : 'Materiale potenziamento'}
                    </Text>
                  </View>
                  <View style={s.cardPrice}>
                    <Text style={s.priceIcon}>{isGems ? '\uD83D\uDC8E' : '\uD83D\uDCB0'}</Text>
                    <Text style={[s.priceTxt, { color: item.can_afford ? COLORS.gold : COLORS.error }]}>
                      {item.shop_price.toLocaleString()}
                    </Text>
                  </View>
                  <View style={[s.buyBadge, { backgroundColor: disabledByLock ? 'rgba(255,165,0,0.18)' : item.can_afford ? COLORS.success + '20' : 'rgba(255,255,255,0.04)' }]}>
                    <Text style={[s.buyTxt, { color: disabledByLock ? '#FFB347' : item.can_afford ? COLORS.success : COLORS.textDim }]}>
                      {disabledByLock ? '\uD83D\uDD12' : buying === item.item_id ? '...' : 'COMPRA'}
                    </Text>
                  </View>
                </LinearGradient>
              </TouchableOpacity>
            </Animated.View>
          );
        })}
      </ScrollView>

      {/* Inventory Link */}
      <View style={s.invBtnWrap}>
        <TouchableOpacity onPress={() => router.push('/inventory' as any)} activeOpacity={0.7}>
          <LinearGradient colors={['rgba(255,215,0,0.15)', 'rgba(255,215,0,0.05)']} style={s.invBtn}>
            <Text style={s.invBtnTxt}>{'\uD83C\uDF92'} INVENTARIO</Text>
          </LinearGradient>
        </TouchableOpacity>
      </View>
    </LinearGradient>
  );
}

const s = StyleSheet.create({
  c: { flex: 1 },
  resRow: { flexDirection: 'row', gap: 6 },
  filterRow: { flexDirection: 'row', gap: 6, paddingHorizontal: 10, paddingVertical: 6 },
  fBtn: { paddingHorizontal: 14, paddingVertical: 5, borderRadius: 8, backgroundColor: 'rgba(255,255,255,0.04)', borderWidth: 1, borderColor: 'rgba(255,255,255,0.06)' },
  fBtnA: { backgroundColor: 'rgba(255,215,0,0.12)', borderColor: 'rgba(255,215,0,0.25)' },
  fTxt: { color: COLORS.textDim, fontSize: 10, fontWeight: '700' },
  fTxtA: { color: COLORS.gold },
  list: { padding: 8, gap: 4, paddingBottom: 80 },
  card: { flexDirection: 'row', alignItems: 'center', padding: 10, borderRadius: 10, borderWidth: 1, gap: 10 },
  cardIcon: { width: 42, height: 42, borderRadius: 10, alignItems: 'center', justifyContent: 'center' },
  cardIconTxt: { fontSize: 24 },
  cardInfo: { flex: 1 },
  cardName: { fontSize: 12, fontWeight: '800' },
  cardDesc: { color: COLORS.textMuted, fontSize: 9, marginTop: 2 },
  cardPrice: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  priceIcon: { fontSize: 14 },
  priceTxt: { fontSize: 13, fontWeight: '900' },
  buyBadge: { paddingHorizontal: 14, paddingVertical: 6, borderRadius: 8, borderWidth: 1, borderColor: 'rgba(68,221,136,0.2)' },
  buyTxt: { fontSize: 10, fontWeight: '900', letterSpacing: 0.5 },
  invBtnWrap: { position: 'absolute', bottom: 70, left: 16 },
  invBtn: { paddingHorizontal: 18, paddingVertical: 10, borderRadius: 12, borderWidth: 1, borderColor: 'rgba(255,215,0,0.2)' },
  invBtnTxt: { color: COLORS.gold, fontSize: 12, fontWeight: '900' },
  // BATCH_1_V2 Track E
  lockBannerV2: { flexDirection: 'row', gap: 8, alignItems: 'center', paddingHorizontal: 12, paddingVertical: 10, marginHorizontal: 8, marginTop: 8, marginBottom: 4, borderRadius: 8, backgroundColor: 'rgba(255,165,0,0.10)', borderWidth: 1, borderColor: 'rgba(255,165,0,0.45)' },
  lockBannerIconV2: { fontSize: 18 },
  lockBannerTxtV2: { flex: 1, color: '#FFD089', fontSize: 11, lineHeight: 16, fontWeight: '600' },
});
