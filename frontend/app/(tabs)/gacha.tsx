import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, ActivityIndicator, Dimensions } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useAuth } from '../../context/AuthContext';
import { apiCall } from '../../utils/api';
import AnimatedHeroPortrait from '../../components/AnimatedHeroPortrait';
import ResourceBadge from '../../components/ui/ResourceBadge';
import { COLORS, RARITY } from '../../constants/theme';
import Animated, { ZoomIn, FadeIn, FadeInDown, BounceIn } from 'react-native-reanimated';

const { width: W, height: H } = Dimensions.get('window');

const BANNERS = [
  {
    id: 'standard', name: 'Standard', desc: 'Tutte le rarita', gradient: ['#FFD700', '#CC9900'] as const,
    cost1: 100, cost10: 900, guarantee: '4\u2B50+',
    rates: { '1\u2B50': '30%', '2\u2B50': '30%', '3\u2B50': '20%', '4\u2B50': '12%', '5\u2B50': '6%', '6\u2B50': '2%' },
  },
  {
    id: 'elemental', name: 'Elementale', desc: 'Eroi elementali potenziati', gradient: ['#4499FF', '#2266CC'] as const,
    cost1: 120, cost10: 1000, guarantee: '4\u2B50+',
    rates: { '1\u2B50': '15%', '2\u2B50': '25%', '3\u2B50': '28%', '4\u2B50': '18%', '5\u2B50': '10%', '6\u2B50': '4%' },
  },
  {
    id: 'premium', name: 'Premium', desc: 'Rate divine aumentate!', gradient: ['#FF4466', '#CC2244'] as const,
    cost1: 200, cost10: 1800, guarantee: '5\u2B50+',
    rates: { '1\u2B50': '5%', '2\u2B50': '15%', '3\u2B50': '25%', '4\u2B50': '25%', '5\u2B50': '20%', '6\u2B50': '10%' },
  },
  {
    id: 'selective', name: 'Selettivo', desc: 'Scegli elemento o classe', gradient: ['#44DD88', '#22AA55'] as const,
    cost1: 150, cost10: 1350, guarantee: '4\u2B50+ elemento scelto',
    rates: { '1\u2B50': '10%', '2\u2B50': '20%', '3\u2B50': '30%', '4\u2B50': '22%', '5\u2B50': '13%', '6\u2B50': '5%' },
  },
  {
    id: 'targeted', name: 'Mirato', desc: 'Rate UP su eroe specifico', gradient: ['#FF8844', '#CC6622'] as const,
    cost1: 180, cost10: 1600, guarantee: '5\u2B50+ eroe featured',
    rates: { '1\u2B50': '5%', '2\u2B50': '12%', '3\u2B50': '25%', '4\u2B50': '28%', '5\u2B50': '20%', '6\u2B50': '10%' },
  },
  {
    id: 'artifact', name: 'Artefatti', desc: 'Evoca artefatti rari', gradient: ['#AA55FF', '#7733CC'] as const,
    cost1: 160, cost10: 1400, guarantee: '4\u2B50+ artefatto',
    rates: { '1\u2B50': '20%', '2\u2B50': '25%', '3\u2B50': '25%', '4\u2B50': '16%', '5\u2B50': '10%', '6\u2B50': '4%' },
  },
  {
    id: 'constellation', name: 'Costellazioni', desc: 'Frammenti costellazione', gradient: ['#FFDD88', '#CCAA55'] as const,
    cost1: 200, cost10: 1800, guarantee: '5\u2B50+ costellazione',
    rates: { '1\u2B50': '8%', '2\u2B50': '15%', '3\u2B50': '27%', '4\u2B50': '25%', '5\u2B50': '17%', '6\u2B50': '8%' },
  },
];

export default function GachaTab() {
  const { user, refreshUser, bumpUserHeroesVersion } = useAuth();
  const [pulling, setPulling] = useState(false);
  const [results, setResults] = useState<any[]>([]);
  const [show, setShow] = useState(false);
  const [banner, setBanner] = useState('standard');

  const activeBanner = BANNERS.find(b => b.id === banner) || BANNERS[0];

  const doPull = async (type: 'single' | 'multi') => {
    setPulling(true); setResults([]); setShow(false);
    try {
      const body = JSON.stringify({ banner });
      let endpoint1 = '/api/gacha/pull';
      let endpoint10 = '/api/gacha/pull10';
      
      // Use correct endpoints based on banner type
      if (banner === 'artifact') {
        endpoint1 = '/api/artifacts/pull';
        endpoint10 = '/api/artifacts/pull10';
      } else if (banner === 'constellation') {
        endpoint1 = '/api/constellations/pull';
        endpoint10 = '/api/constellations/pull10';
      }

      if (type === 'single') {
        const r = await apiCall(endpoint1, { method: 'POST', body });
        // Normalize result format
        if (banner === 'artifact') {
          setResults([{ artifact: r.artifact || r, type: 'artifact' }]);
        } else if (banner === 'constellation') {
          setResults([{ constellation: r.constellation || r, type: 'constellation' }]);
        } else {
          setResults([r]);
        }
      } else {
        const r = await apiCall(endpoint10, { method: 'POST', body });
        if (banner === 'artifact') {
          setResults((r.results || r.artifacts || [r]).map((a: any) => ({ artifact: a.artifact || a, type: 'artifact' })));
        } else if (banner === 'constellation') {
          setResults((r.results || r.constellations || [r]).map((c: any) => ({ constellation: c.constellation || c, type: 'constellation' })));
        } else {
          setResults(r.results || [r]);
        }
      }
      setShow(true); await refreshUser();
      // RM1.16-B: invalida la cache del roster utente sulle schermate
      // Heroes / Hero Collection / Battle formation, così i nuovi eroi
      // (es. Borea pullata) appaiono senza richiedere restart dell'app.
      // I banner artifact/constellation non aggiungono eroi, ma il bump è
      // innocuo (stesso costo di un setState int).
      if (banner !== 'artifact' && banner !== 'constellation') {
        bumpUserHeroesVersion();
      }
    } catch (e: any) { setResults([{ error: e.message }]); setShow(true); }
    finally { setPulling(false); }
  };

  // Results view
  if (show && results.length > 0) {
    return (
      <LinearGradient colors={[COLORS.bgPrimary, '#1A0A2E', '#0D0D2B']} style={s.c}>
        <View style={s.resHdr}>
          <Text style={s.resTitle}>EVOCAZIONE COMPLETATA!</Text>
          <ResourceBadge icon={'\uD83D\uDC8E'} value={user?.gems || 0} compact />
        </View>
        <View style={{ flex: 1, justifyContent: 'center' }}>
          <ScrollView horizontal contentContainerStyle={s.resGrid} showsHorizontalScrollIndicator={false}>
          {results.map((r: any, i: number) => {
            if (r.error) return (
              <View key={i} style={s.resCard}>
                <Text style={{ color: COLORS.error, fontSize: 11 }}>{r.error}</Text>
              </View>
            );
            // Handle different result types
            if (r.type === 'artifact') {
              const a = r.artifact || {};
              const rar = a.rarity || 1;
              const col = RARITY.colors[Math.min(rar, 6)] || '#AA55FF';
              return (
                <Animated.View key={i} entering={BounceIn.delay(i * 100).duration(400)}>
                  <View style={s.resCardOuter}>
                    <LinearGradient colors={[col + '20', col + '08']} style={[s.resCard, { borderColor: col + '60' }]}>
                      <View style={[s.artIcon, { backgroundColor: col + '25' }]}>
                        <Text style={{ fontSize: 28 }}>{a.icon || '\uD83D\uDC8E'}</Text>
                      </View>
                      <Text style={[s.resN, { color: col }]} numberOfLines={1}>{a.name || 'Artefatto'}</Text>
                      <View style={[s.rarBadge, { backgroundColor: col + '20' }]}>
                        <Text style={[s.resR, { color: col }]}>{rar}{'\u2B50'} Artefatto</Text>
                      </View>
                    </LinearGradient>
                  </View>
                </Animated.View>
              );
            }
            if (r.type === 'constellation') {
              const c = r.constellation || {};
              const col = '#FFDD88';
              return (
                <Animated.View key={i} entering={BounceIn.delay(i * 100).duration(400)}>
                  <View style={s.resCardOuter}>
                    <LinearGradient colors={[col + '20', col + '08']} style={[s.resCard, { borderColor: col + '60' }]}>
                      <View style={[s.artIcon, { backgroundColor: col + '25' }]}>
                        <Text style={{ fontSize: 28 }}>{c.icon || '\u2B50'}</Text>
                      </View>
                      <Text style={[s.resN, { color: col }]} numberOfLines={1}>{c.name || 'Costellazione'}</Text>
                      <View style={[s.rarBadge, { backgroundColor: col + '20' }]}>
                        <Text style={[s.resR, { color: col }]}>{c.rarity || 1}{'\u2B50'} Costellazione</Text>
                      </View>
                    </LinearGradient>
                  </View>
                </Animated.View>
              );
            }
            // Hero result (default)
            const h = r.hero;
            const rar = h?.rarity || 1;
            const col = RARITY.colors[rar] || '#888';
            return (
              <Animated.View key={i} entering={BounceIn.delay(i * 100).duration(400)}>
                <View style={s.resCardOuter}>
                  <LinearGradient
                    colors={[col + '20', col + '08']}
                    style={[s.resCard, { borderColor: col + '60' }]}
                  >
                    <AnimatedHeroPortrait imageUrl={h?.image_url} name={h?.name || '?'} rarity={rar} element={h?.element} size={56} />
                    <Text style={[s.resN, { color: col }]} numberOfLines={1}>{h?.name}</Text>
                    <View style={[s.rarBadge, { backgroundColor: col + '20' }]}>
                      <Text style={[s.resR, { color: col }]}>{RARITY.names[rar]}</Text>
                    </View>
                  </LinearGradient>
                </View>
              </Animated.View>
            );
          })}
        </ScrollView>
        </View>
        <View style={s.resActs}>
          <TouchableOpacity style={s.againBtnOuter} onPress={() => setShow(false)} activeOpacity={0.7}>
            <LinearGradient
              colors={[COLORS.accent, '#FF4444']}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 0 }}
              style={s.againBtn}
            >
              <Text style={s.againTxt}>EVOCA ANCORA</Text>
            </LinearGradient>
          </TouchableOpacity>
          <TouchableOpacity style={s.backBtnOuter} onPress={() => { setShow(false); setResults([]); }} activeOpacity={0.7}>
            <View style={s.backBtn}>
              <Text style={s.backBtnTxt}>CHIUDI</Text>
            </View>
          </TouchableOpacity>
        </View>
      </LinearGradient>
    );
  }

  return (
    <LinearGradient colors={[COLORS.bgPrimary, '#1A0A2E', '#0D0D2B']} style={s.c}>
      {/* Header */}
      <LinearGradient
        colors={['rgba(255,215,0,0.08)', 'rgba(15,15,45,0.95)']}
        style={s.hdr}
      >
        <Text style={s.title}>EVOCAZIONE DIVINA</Text>
        <ResourceBadge icon={'\uD83D\uDC8E'} value={user?.gems || 0} />
      </LinearGradient>

      <View style={s.body}>
        {/* Banner Selection - Scrollable */}
        <ScrollView
          style={s.bannersScroll}
          contentContainerStyle={s.banners}
          showsVerticalScrollIndicator={false}
          nestedScrollEnabled
        >
          {BANNERS.map((b, i) => {
            const isActive = banner === b.id;
            return (
              <Animated.View key={b.id} entering={FadeInDown.delay(i * 80).duration(300)}>
                <TouchableOpacity
                  onPress={() => setBanner(b.id)}
                  activeOpacity={0.7}
                  style={s.bannerCardOuter}
                >
                  <LinearGradient
                    colors={isActive ? [b.gradient[0] + '25', b.gradient[1] + '10'] : ['rgba(255,255,255,0.03)', 'rgba(255,255,255,0.01)']}
                    style={[s.bannerCard, { borderColor: isActive ? b.gradient[0] + '80' : 'rgba(255,255,255,0.06)' }]}
                  >
                    <View style={[s.bannerDot, { backgroundColor: b.gradient[0] }]} />
                    <Text style={[s.bannerName, { color: isActive ? b.gradient[0] : COLORS.textSecondary }]}>{b.name}</Text>
                    <Text style={s.bannerDesc}>{b.desc}</Text>
                    {isActive && (
                      <View style={[s.bannerActiveBadge, { backgroundColor: b.gradient[0] + '20' }]}>
                        <Text style={[s.bannerActive, { color: b.gradient[0] }]}>ATTIVO</Text>
                      </View>
                    )}
                  </LinearGradient>
                </TouchableOpacity>
              </Animated.View>
            );
          })}
        </ScrollView>

        {/* Active Banner Info + Pull - Scrollable */}
        <ScrollView
          style={s.pullAreaScroll}
          contentContainerStyle={s.pullArea}
          showsVerticalScrollIndicator={false}
          nestedScrollEnabled
        >
          <LinearGradient
            colors={[activeBanner.gradient[0] + '10', 'rgba(10,10,40,0.6)']}
            style={s.bannerInfo}
          >
            <Text style={[s.bInfoTitle, { color: activeBanner.gradient[0] }]}>{activeBanner.name}</Text>
            <Text style={s.bInfoDesc}>{activeBanner.desc}</Text>
            <View style={s.guaranteeBadge}>
              <Text style={s.bInfoGuarantee}>Garantito x10: {activeBanner.guarantee}</Text>
            </View>
            <View style={s.rates}>
              {Object.entries(activeBanner.rates).map(([k, v]) => (
                <View key={k} style={s.rateRow}>
                  <Text style={s.rateK}>{k}</Text>
                  <View style={s.rateFill}>
                    <View style={[s.rateBar, { width: String(v) as any, backgroundColor: activeBanner.gradient[0] + '40' }]} />
                  </View>
                  <Text style={s.rateV}>{v}</Text>
                </View>
              ))}
            </View>
          </LinearGradient>

          <View style={s.pullBtns}>
            <TouchableOpacity
              style={s.pullBtnOuter}
              onPress={() => doPull('single')}
              disabled={pulling}
              activeOpacity={0.7}
            >
              <LinearGradient
                colors={['rgba(255,255,255,0.06)', 'rgba(255,255,255,0.02)']}
                style={[s.pullBtn, { borderColor: activeBanner.gradient[0] + '50' }, pulling && { opacity: 0.5 }]}
              >
                {pulling ? <ActivityIndicator color="#fff" /> : (
                  <>
                    <Text style={s.pTitle}>EVOCA x1</Text>
                    <Text style={[s.pCost, { color: activeBanner.gradient[0] }]}>{'\uD83D\uDC8E'} {activeBanner.cost1}</Text>
                  </>
                )}
              </LinearGradient>
            </TouchableOpacity>

            <TouchableOpacity
              style={s.pullBtnOuter}
              onPress={() => doPull('multi')}
              disabled={pulling}
              activeOpacity={0.7}
            >
              <LinearGradient
                colors={[activeBanner.gradient[0] + '30', activeBanner.gradient[1] + '15']}
                style={[s.pullBtn, { borderColor: activeBanner.gradient[0] + '60' }, pulling && { opacity: 0.5 }]}
              >
                {pulling ? <ActivityIndicator color="#fff" /> : (
                  <>
                    <Text style={s.pTitle}>EVOCA x10</Text>
                    <Text style={[s.pCost, { color: activeBanner.gradient[0] }]}>{'\uD83D\uDC8E'} {activeBanner.cost10}</Text>
                    <View style={s.pGuarantee}>
                      <Text style={s.pG}>Garantito {activeBanner.guarantee}</Text>
                    </View>
                  </>
                )}
              </LinearGradient>
            </TouchableOpacity>
          </View>
        </ScrollView>
      </View>
    </LinearGradient>
  );
}

const s = StyleSheet.create({
  c: { flex: 1 },
  // Header
  hdr: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,215,0,0.15)',
  },
  title: {
    color: COLORS.gold,
    fontSize: 16,
    fontWeight: '900',
    letterSpacing: 3,
    textShadowColor: 'rgba(255,215,0,0.3)',
    textShadowOffset: { width: 0, height: 0 },
    textShadowRadius: 10,
  },
  gems: { color: '#fff', fontSize: 13, fontWeight: '600' },
  body: { flex: 1, flexDirection: 'row', padding: 12, gap: 10 },
  // Banners
  bannersScroll: { width: 155, flexShrink: 0 },
  banners: { gap: 6, paddingBottom: 8 },
  bannerCardOuter: { borderRadius: 12, overflow: 'hidden' },
  bannerCard: {
    padding: 12,
    borderRadius: 12,
    borderWidth: 1.5,
  },
  bannerDot: { width: 6, height: 6, borderRadius: 3, marginBottom: 6 },
  bannerName: { fontSize: 14, fontWeight: '900', letterSpacing: 0.5 },
  bannerDesc: { color: COLORS.textMuted, fontSize: 9, marginTop: 3 },
  bannerActiveBadge: { alignSelf: 'flex-start', paddingHorizontal: 8, paddingVertical: 2, borderRadius: 6, marginTop: 6 },
  bannerActive: { fontSize: 8, fontWeight: '900', letterSpacing: 1 },
  // Pull area
  pullAreaScroll: { flex: 1 },
  pullArea: { gap: 10, paddingBottom: 8 },
  bannerInfo: {
    borderRadius: 14,
    padding: 14,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.06)',
  },
  bInfoTitle: { fontSize: 16, fontWeight: '900', letterSpacing: 1 },
  bInfoDesc: { color: COLORS.textSecondary, fontSize: 10, marginTop: 3 },
  guaranteeBadge: {
    alignSelf: 'flex-start',
    backgroundColor: 'rgba(68,221,136,0.1)',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
    marginTop: 6,
    borderWidth: 1,
    borderColor: 'rgba(68,221,136,0.2)',
  },
  bInfoGuarantee: { color: COLORS.success, fontSize: 10, fontWeight: '700' },
  rates: { marginTop: 8, gap: 3 },
  rateRow: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  rateK: { color: COLORS.textSecondary, fontSize: 10, width: 30 },
  rateFill: { flex: 1, height: 4, backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: 2, overflow: 'hidden' },
  rateBar: { height: '100%', borderRadius: 2 },
  rateV: { color: '#fff', fontSize: 10, fontWeight: '700', width: 30, textAlign: 'right' },
  // Pull buttons
  pullBtns: { flexDirection: 'row', gap: 8 },
  pullBtnOuter: { flex: 1, borderRadius: 12, overflow: 'hidden' },
  pullBtn: {
    flex: 1,
    padding: 14,
    borderRadius: 12,
    alignItems: 'center',
    borderWidth: 1.5,
  },
  pTitle: { color: '#fff', fontSize: 14, fontWeight: '900', letterSpacing: 1 },
  pCost: { fontSize: 13, fontWeight: '700', marginTop: 4 },
  pGuarantee: {
    backgroundColor: 'rgba(68,221,136,0.1)',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 6,
    marginTop: 4,
  },
  pG: { color: COLORS.success, fontSize: 9, fontWeight: '700' },
  // Results
  resHdr: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,215,0,0.2)',
  },
  resTitle: {
    color: COLORS.gold,
    fontSize: 18,
    fontWeight: '900',
    letterSpacing: 2,
    textShadowColor: 'rgba(255,215,0,0.3)',
    textShadowOffset: { width: 0, height: 0 },
    textShadowRadius: 10,
  },
  resGrid: { padding: 14, gap: 10, alignItems: 'center' },
  resCardOuter: { borderRadius: 14, overflow: 'hidden' },
  resCard: {
    width: 115,
    borderRadius: 14,
    padding: 10,
    alignItems: 'center',
    borderWidth: 1.5,
  },
  resN: { fontSize: 11, fontWeight: '800', marginTop: 6, textAlign: 'center' },
  artIcon: { width: 56, height: 56, borderRadius: 12, alignItems: 'center', justifyContent: 'center', marginBottom: 2 },
  rarBadge: { paddingHorizontal: 8, paddingVertical: 2, borderRadius: 6, marginTop: 4 },
  resR: { fontSize: 8, fontWeight: '800' },
  resActs: { flexDirection: 'row', justifyContent: 'center', paddingHorizontal: 14, paddingTop: 10, paddingBottom: 68, gap: 12 },
  againBtnOuter: { borderRadius: 12, overflow: 'hidden' },
  againBtn: { paddingHorizontal: 32, paddingVertical: 12, borderRadius: 12 },
  againTxt: { color: '#fff', fontSize: 14, fontWeight: '900', letterSpacing: 1 },
  backBtnOuter: { borderRadius: 12, overflow: 'hidden' },
  backBtn: { paddingHorizontal: 28, paddingVertical: 12, borderRadius: 12, backgroundColor: 'rgba(255,255,255,0.08)', borderWidth: 1, borderColor: 'rgba(255,255,255,0.15)' },
  backBtnTxt: { color: '#fff', fontSize: 14, fontWeight: '800', letterSpacing: 1 },
});
