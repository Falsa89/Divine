import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert, ActivityIndicator } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import Animated, { FadeIn, FadeInDown } from 'react-native-reanimated';
import { apiCall } from '../utils/api';
import { useAuth } from '../context/AuthContext';
import ScreenHeader from '../components/ui/ScreenHeader';
import TabSelector from '../components/ui/TabSelector';
import GradientButton from '../components/ui/GradientButton';
import StarDisplay from '../components/ui/StarDisplay';
import TranscendenceStars from '../components/ui/TranscendenceStars';
import { COLORS } from '../constants/theme';

// NOTE: 'wallet' tab removed in TASK 4.5-B2 — replaced by /treasury (Tesoreria)
type Tab = 'soul_forge' | 'shops';
const TABS = [
  { key: 'soul_forge', label: 'Anime', icon: '\uD83D\uDD25' },
  { key: 'shops', label: 'Negozi', icon: '\uD83D\uDED2' },
];

export default function EconomyScreen() {
  const router = useRouter();
  const { refreshUser } = useAuth();
  const [tab, setTab] = useState<Tab>('soul_forge');
  const [wallet, setWallet] = useState<any>(null);
  const [shops, setShops] = useState<any>(null);
  const [soulForge, setSoulForge] = useState<any>(null);
  const [heroes, setHeroes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [acting, setActing] = useState('');
  const [selectedShop, setSelectedShop] = useState('');

  useEffect(() => { loadAll(); }, []);

  const loadAll = async () => {
    try {
      const [w, s, sf, h] = await Promise.all([
        apiCall('/api/wallet'), apiCall('/api/shops'),
        apiCall('/api/soul-forge'), apiCall('/api/user/heroes'),
      ]);
      setWallet(w); setShops(s); setSoulForge(sf); setHeroes(h || []);
    } catch (e) {} finally { setLoading(false); }
  };

  const retireHero = async (uhid: string, name: string) => {
    Alert.alert('Ritiro Eroe', `Ritirare ${name}? Eliminazione permanente!`, [
      { text: 'Annulla' },
      {
        text: 'RITIRA', style: 'destructive', onPress: async () => {
          setActing('retire');
          try {
            const r = await apiCall('/api/soul-forge/retire', { method: 'POST', body: JSON.stringify({ user_hero_ids: [uhid] }) });
            await refreshUser(); await loadAll();
            const rw = r.rewards || {};
            Alert.alert('Eroe Ritirato!', `${r.retired_heroes?.join(', ')}\nPrana: +${rw.prana}\nSigilli: +${rw.soul_seals}\nPolvere: +${rw.star_dust}`);
          } catch (e: any) { Alert.alert('Errore', e.message); }
          finally { setActing(''); }
        }
      },
    ]);
  };

  const buyItem = async (shopId: string, itemId: string) => {
    setActing(itemId);
    try {
      const r = await apiCall('/api/shops/buy', { method: 'POST', body: JSON.stringify({ shop_id: shopId, item_id: itemId }) });
      await refreshUser(); await loadAll();
      Alert.alert('Acquistato!', r.item);
    } catch (e: any) { Alert.alert('Errore', e.message); }
    finally { setActing(''); }
  };

  if (loading) return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B']} style={st.c}>
      <ActivityIndicator size="large" color={COLORS.gold} />
    </LinearGradient>
  );
  const currencies = wallet?.currencies || {};
  const shopData = shops?.shops || {};

  return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={st.c}>
      <ScreenHeader title="Economia" titleColor={COLORS.gold} showBack />
      <TabSelector tabs={TABS} active={tab} onChange={(t) => setTab(t as Tab)} accentColor={COLORS.gold} />

      <ScrollView contentContainerStyle={st.body}>
        {/* Treasury CTA banner — replaces obsolete Wallet tab */}
        <Animated.View entering={FadeIn} style={st.treasuryCtaOuter}>
          <TouchableOpacity
            onPress={() => router.push('/treasury')}
            activeOpacity={0.8}
          >
            <LinearGradient
              colors={['rgba(255, 215, 0, 0.14)', 'rgba(68, 153, 255, 0.08)']}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 1 }}
              style={st.treasuryCta}
            >
              <View style={st.treasuryCtaIconWrap}>
                <Text style={st.treasuryCtaIcon}>{'\uD83C\uDFE6'}</Text>
              </View>
              <View style={st.treasuryCtaInfo}>
                <Text style={st.treasuryCtaTitle}>Tesoreria</Text>
                <Text style={st.treasuryCtaDesc}>
                  Catalogo completo delle valute del regno
                </Text>
              </View>
              <Text style={st.treasuryCtaArrow}>{'\u203A'}</Text>
            </LinearGradient>
          </TouchableOpacity>
        </Animated.View>

        {tab === 'soul_forge' && (
          <Animated.View entering={FadeIn}>
            <Text style={st.sec}>Fucina delle Anime</Text>
            <Text style={st.sfDesc}>Ritira eroi per ottenere Prana, Sigilli e Polvere Stellare.</Text>
            <View style={st.sfBals}>
              <LinearGradient colors={['rgba(255,107,53,0.08)', 'transparent']} style={st.sfBalCard}>
                <Text style={st.sfBalLabel}>Prana</Text>
                <Text style={st.sfBalVal}>{soulForge?.prana || 0}</Text>
              </LinearGradient>
              <LinearGradient colors={['rgba(136,68,255,0.08)', 'transparent']} style={st.sfBalCard}>
                <Text style={st.sfBalLabel}>Sigilli</Text>
                <Text style={st.sfBalVal}>{soulForge?.soul_seals || 0}</Text>
              </LinearGradient>
              <LinearGradient colors={['rgba(255,215,0,0.08)', 'transparent']} style={st.sfBalCard}>
                <Text style={st.sfBalLabel}>Polvere</Text>
                <Text style={st.sfBalVal}>{soulForge?.star_dust || 0}</Text>
              </LinearGradient>
            </View>
            <Text style={st.sub}>Eroi per Ritiro</Text>
            <View style={st.heroGrid}>
              {heroes.filter((h: any) => (h.hero_rarity || h.stars || 1) <= 3).slice(0, 12).map((h: any) => (
                <TouchableOpacity
                  key={h.id}
                  style={st.heroR}
                  onPress={() => retireHero(h.id, h.hero_name || '?')}
                  disabled={acting === 'retire'}
                  activeOpacity={0.7}
                >
                  <LinearGradient colors={['rgba(255,68,68,0.08)', 'transparent']} style={st.heroRInner}>
                    <Text style={st.heroRN} numberOfLines={1}>{h.hero_name}</Text>
                    <View style={st.heroRS}>
                      {(h.stars || h.hero_rarity || 1) <= 12
                        ? <StarDisplay stars={h.stars || h.hero_rarity || 1} size={8} />
                        : <TranscendenceStars stars={h.stars || h.hero_rarity || 1} size={8} />}
                    </View>
                  </LinearGradient>
                </TouchableOpacity>
              ))}
            </View>
          </Animated.View>
        )}

        {tab === 'shops' && !selectedShop && (
          <Animated.View entering={FadeIn}>
            <Text style={st.sec}>Negozi Specializzati</Text>
            {Object.entries(shopData).map(([sid, shop]: [string, any], i) => (
              <Animated.View key={sid} entering={FadeInDown.delay(i * 50)}>
                <TouchableOpacity onPress={() => setSelectedShop(sid)} activeOpacity={0.7}>
                  <LinearGradient
                    colors={[(shop.color || '#888') + '12', 'transparent']}
                    style={[st.shopCard, { borderColor: (shop.color || '#888') + '30' }]}
                  >
                    <View style={[st.shopIconWrap, { backgroundColor: (shop.color || '#888') + '15' }]}>
                      <Text style={st.shopIcon}>{shop.icon}</Text>
                    </View>
                    <View style={st.shopInfo}>
                      <Text style={[st.shopName, { color: shop.color }]}>{shop.name}</Text>
                      <Text style={st.shopItems}>{shop.items?.length || 0} oggetti</Text>
                    </View>
                    <Text style={[st.arrow, { color: shop.color }]}>{'\u203A'}</Text>
                  </LinearGradient>
                </TouchableOpacity>
              </Animated.View>
            ))}
          </Animated.View>
        )}

        {tab === 'shops' && selectedShop && shopData[selectedShop] && (
          <Animated.View entering={FadeIn}>
            <TouchableOpacity onPress={() => setSelectedShop('')}>
              <Text style={st.backShop}>{'\u2190'} Torna ai Negozi</Text>
            </TouchableOpacity>
            <Text style={[st.sec, { color: shopData[selectedShop].color }]}>
              {shopData[selectedShop].icon} {shopData[selectedShop].name}
            </Text>
            {shopData[selectedShop].items?.map((item: any, i: number) => (
              <Animated.View key={item.id} entering={FadeInDown.delay(i * 35)}>
                <LinearGradient
                  colors={['rgba(255,255,255,0.03)', 'transparent']}
                  style={[st.itemCard, item.remaining_stock <= 0 && { opacity: 0.4 }]}
                >
                  <View style={st.itemIconWrap}>
                    <Text style={st.itemIcon}>{item.icon}</Text>
                  </View>
                  <View style={st.itemInfo}>
                    <Text style={st.itemName}>{item.name}</Text>
                    <Text style={st.itemDesc}>{item.description}</Text>
                    <Text style={st.itemCost}>
                      {Object.entries(item.cost).map(([c, v]) => `${currencies[c]?.icon || c} ${(v as number).toLocaleString()}`).join(' + ')}
                    </Text>
                  </View>
                  <View style={st.itemRight}>
                    <Text style={st.itemStock}>{item.remaining_stock}/{item.stock}</Text>
                    <TouchableOpacity
                      onPress={() => buyItem(selectedShop, item.id)}
                      disabled={!item.can_afford || item.remaining_stock <= 0 || acting === item.id}
                      activeOpacity={0.7}
                    >
                      <LinearGradient
                        colors={item.remaining_stock <= 0 ? ['rgba(255,255,255,0.05)', 'rgba(255,255,255,0.02)'] : [COLORS.success + '20', COLORS.success + '10']}
                        style={[st.buyBtn, (!item.can_afford || item.remaining_stock <= 0) && { opacity: 0.3 }]}
                      >
                        <Text style={st.buyTxt}>{item.remaining_stock <= 0 ? 'ESAURITO' : 'COMPRA'}</Text>
                      </LinearGradient>
                    </TouchableOpacity>
                  </View>
                </LinearGradient>
              </Animated.View>
            ))}
          </Animated.View>
        )}
      </ScrollView>
    </LinearGradient>
  );
}

const st = StyleSheet.create({
  c: { flex: 1 },
  body: { padding: 10, gap: 6, paddingBottom: 70 },
  sec: { color: '#fff', fontSize: 15, fontWeight: '900', marginBottom: 8 },
  sub: { color: COLORS.textSecondary, fontSize: 12, fontWeight: '700', marginTop: 10, marginBottom: 6 },
  // Treasury CTA banner (TASK 4.5-B2 — replaces obsolete Wallet tab)
  treasuryCtaOuter: {
    borderRadius: 12,
    overflow: 'hidden',
    marginBottom: 6,
  },
  treasuryCta: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: 'rgba(255, 215, 0, 0.35)',
    gap: 12,
  },
  treasuryCtaIconWrap: {
    width: 42,
    height: 42,
    borderRadius: 10,
    backgroundColor: 'rgba(255, 215, 0, 0.15)',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255, 215, 0, 0.4)',
  },
  treasuryCtaIcon: { fontSize: 22 },
  treasuryCtaInfo: { flex: 1 },
  treasuryCtaTitle: {
    color: COLORS.gold,
    fontSize: 14,
    fontWeight: '900',
    letterSpacing: 1,
  },
  treasuryCtaDesc: {
    color: COLORS.textSecondary,
    fontSize: 10,
    marginTop: 2,
  },
  treasuryCtaArrow: {
    color: COLORS.gold,
    fontSize: 22,
    fontWeight: '700',
  },
  // Wallet
  currCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 10,
    borderRadius: 10,
    borderWidth: 1,
    gap: 10,
    marginBottom: 4,
  },
  currIconWrap: { width: 36, height: 36, borderRadius: 10, alignItems: 'center', justifyContent: 'center' },
  currIcon: { fontSize: 20 },
  currInfo: { flex: 1 },
  currName: { fontSize: 12, fontWeight: '800' },
  currAmt: { color: '#fff', fontSize: 15, fontWeight: '900' },
  // Soul Forge
  sfDesc: { color: COLORS.textMuted, fontSize: 10, marginBottom: 8 },
  sfBals: { flexDirection: 'row', gap: 6, marginBottom: 8 },
  sfBalCard: {
    flex: 1,
    padding: 10,
    borderRadius: 10,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.06)',
  },
  sfBalLabel: { color: COLORS.textMuted, fontSize: 9, fontWeight: '700', letterSpacing: 0.5 },
  sfBalVal: { color: '#fff', fontSize: 16, fontWeight: '900', marginTop: 2 },
  heroGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 4 },
  heroR: {
    width: '23.5%',
    borderRadius: 8,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: 'rgba(255,68,68,0.2)',
  },
  heroRInner: { padding: 6, alignItems: 'center' },
  heroRN: { color: COLORS.textSecondary, fontSize: 8, fontWeight: '700' },
  heroRS: { color: COLORS.gold, fontSize: 8, marginTop: 1 },
  // Shops
  shopCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    borderRadius: 12,
    borderWidth: 1,
    marginBottom: 6,
    gap: 10,
  },
  shopIconWrap: { width: 40, height: 40, borderRadius: 10, alignItems: 'center', justifyContent: 'center' },
  shopIcon: { fontSize: 24 },
  shopInfo: { flex: 1 },
  shopName: { fontSize: 13, fontWeight: '900' },
  shopItems: { color: COLORS.textMuted, fontSize: 9, marginTop: 1 },
  arrow: { fontSize: 24, fontWeight: '700' },
  backShop: { color: COLORS.gold, fontSize: 12, fontWeight: '700', paddingVertical: 6 },
  // Items
  itemCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 10,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.06)',
    marginBottom: 4,
    gap: 8,
  },
  itemIconWrap: {
    width: 32,
    height: 32,
    borderRadius: 8,
    backgroundColor: 'rgba(255,255,255,0.05)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  itemIcon: { fontSize: 20 },
  itemInfo: { flex: 1 },
  itemName: { color: '#fff', fontSize: 11, fontWeight: '800' },
  itemDesc: { color: COLORS.textMuted, fontSize: 8, marginTop: 1 },
  itemCost: { color: COLORS.gold, fontSize: 9, fontWeight: '700', marginTop: 2 },
  itemRight: { alignItems: 'center', gap: 4 },
  itemStock: { color: COLORS.textMuted, fontSize: 8 },
  buyBtn: {
    paddingHorizontal: 14,
    paddingVertical: 5,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: COLORS.success + '40',
  },
  buyTxt: { color: COLORS.success, fontSize: 9, fontWeight: '800' },
});
