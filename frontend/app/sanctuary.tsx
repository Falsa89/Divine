/**
 * SANTUARIO EROE (Hero Sanctuary)
 * ==================================
 * Pagina centrale per l'interazione con l'eroe:
 *  - Panoramica (splash + identity + riepilogo)
 *  - Affinità (livello 0-10, curva lenta ~2450 battle, ricompense per livello)
 *  - Costellazione (struttura stage, boss ogni 3, frammenti, limite 3/die)
 *  - Azioni (imposta come home hero, link a enciclopedia, complete tutorial)
 */
import React, { useEffect, useState, useCallback } from 'react';
import {
  View, Text, ScrollView, TouchableOpacity, StyleSheet,
  ActivityIndicator, Image as RNImage, Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter, useLocalSearchParams } from 'expo-router';
import Animated, { FadeIn, FadeInDown } from 'react-native-reanimated';
import { apiCall } from '../utils/api';
import HeroPortrait, { isHopliteHero } from '../components/ui/HeroPortrait';

const RARITY_COLOR: Record<number, string> = {
  1: '#9AA5B1', 2: '#4ECDC4', 3: '#46A3FF',
  4: '#B05CFF', 5: '#FFB347', 6: '#FF4D6D',
};
const ELEMENT_EMOJI: Record<string, string> = {
  fire: '\uD83D\uDD25', water: '\uD83D\uDCA7', earth: '\u26F0\uFE0F',
  wind: '\uD83D\uDCA8', air: '\uD83C\uDF2C\uFE0F', thunder: '\u26A1',
  light: '\u2728', dark: '\uD83C\uDF11', neutral: '\u2694\uFE0F',
};

const STAT_LABEL: Record<string, string> = {
  hp: 'HP', physical_damage: 'ATK Fis', magic_damage: 'ATK Mag',
  physical_defense: 'DEF Fis', magic_defense: 'DEF Mag',
  crit_chance: 'CRIT%', crit_damage: 'DMG CRIT', speed: 'VEL',
  dodge: 'SCHIV%', healing_received: 'Cure Ric',
};

type Tab = 'overview' | 'affinity' | 'constellation' | 'actions';

export default function SanctuaryScreen() {
  const router = useRouter();
  const params = useLocalSearchParams();
  const heroId = params.heroId as string;
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<Tab>('overview');
  const [acting, setActing] = useState(false);

  const load = useCallback(async () => {
    try {
      const r = await apiCall(`/api/sanctuary/${heroId}`);
      setData(r);
    } catch (e: any) {
      console.warn('[sanctuary] load', e);
    } finally {
      setLoading(false);
    }
  }, [heroId]);

  useEffect(() => { if (heroId) load(); }, [heroId, load]);

  const setHomeHero = async () => {
    setActing(true);
    try {
      await apiCall('/api/sanctuary/home-hero', {
        method: 'POST',
        body: JSON.stringify({ hero_id: heroId }),
      });
      Alert.alert('\uD83C\uDFDB\uFE0F Eroe Homepage', `${data.hero.name} è ora il tuo eroe mostrato in homepage.`);
      await load();
    } catch (e: any) {
      Alert.alert('Errore', e?.message || 'Impossibile impostare home hero');
    } finally {
      setActing(false);
    }
  };

  const completeTutorial = async () => {
    Alert.alert(
      'Termina Tutorial',
      'Confermi di voler chiudere il tutorial? Dopo dovrai scegliere un tuo eroe come home hero.',
      [
        { text: 'Annulla' },
        {
          text: 'Conferma',
          onPress: async () => {
            setActing(true);
            try {
              await apiCall('/api/sanctuary/complete-tutorial', { method: 'POST' });
              Alert.alert('Tutorial Completato!', 'Ora puoi scegliere il tuo eroe homepage.');
              await load();
            } catch (e: any) {
              Alert.alert('Errore', e?.message || 'Operazione fallita');
            } finally {
              setActing(false);
            }
          },
        },
      ],
    );
  };

  if (loading) {
    return (
      <SafeAreaView style={st.root}>
        <View style={st.loading}><ActivityIndicator size="large" color="#FFD700" /></View>
      </SafeAreaView>
    );
  }
  if (!data || !data.hero) {
    return (
      <SafeAreaView style={st.root}>
        <View style={st.loading}>
          <Text style={st.err}>Eroe non trovato</Text>
          <TouchableOpacity onPress={() => router.back()} style={[st.backBtn, { marginTop: 16 }]}>
            <Text style={st.backTxt}>{'\u2190'} Indietro</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  const hero = data.hero;
  const rarity = hero.rarity || 1;
  const rarCol = RARITY_COLOR[rarity] || '#888';
  const element = (hero.element || 'neutral').toLowerCase();
  const aff = data.affinity;
  const con = data.constellation;
  const isHop = isHopliteHero(hero.id, hero.name);
  const isBorea = hero.id === 'borea';

  const TABS: Array<{ key: Tab; label: string; icon: string }> = [
    { key: 'overview',      label: 'Panoramica',   icon: '\uD83D\uDC41\uFE0F' },
    { key: 'affinity',      label: 'Affinità',     icon: '\uD83D\uDC96' },
    { key: 'constellation', label: 'Costellazione', icon: '\u2728' },
    { key: 'actions',       label: 'Azioni',       icon: '\u2699\uFE0F' },
  ];

  return (
    <SafeAreaView style={st.root} edges={['top']}>
      <LinearGradient colors={['#1a0e2e', '#0a0612']} style={st.header}>
        <View style={st.headerRow}>
          <TouchableOpacity onPress={() => router.back()} style={st.backBtn}>
            <Text style={st.backTxt}>{'\u2190'} Indietro</Text>
          </TouchableOpacity>
          <View style={{ flex: 1 }}>
            <Text style={st.title}>{'\uD83C\uDFDB\uFE0F Santuario'}</Text>
            <Text style={[st.subtitle, { color: rarCol }]} numberOfLines={1}>{hero.name}</Text>
          </View>
          {data.is_home && <Text style={st.homeChip}>{'\uD83C\uDFE0 HOME'}</Text>}
        </View>
      </LinearGradient>

      {/* Tab selector */}
      <View style={st.tabs}>
        {TABS.map(t => (
          <TouchableOpacity
            key={t.key}
            onPress={() => setTab(t.key)}
            style={[st.tabBtn, tab === t.key && st.tabBtnActive]}
          >
            <Text style={st.tabIcon}>{t.icon}</Text>
            <Text style={[st.tabLabel, tab === t.key && { color: '#FFD700' }]} numberOfLines={1}>
              {t.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <ScrollView contentContainerStyle={st.body}>
        {/* OVERVIEW */}
        {tab === 'overview' && (
          <Animated.View entering={FadeIn} style={{ gap: 12 }}>
            <View style={[st.splashBig, { borderColor: rarCol + '60' }]}>
              {isHop ? (
                <HeroPortrait heroId={hero.id} heroName={hero.name} size={280} />
              ) : hero.image_url ? (
                <RNImage source={{ uri: hero.image_url }} style={st.splashImg} resizeMode="cover" />
              ) : (
                <LinearGradient
                  colors={isBorea ? ['#4A7BFF', '#1B2A4E', '#0A1020'] : [rarCol + '80', rarCol + '20', '#0A0612']}
                  style={[st.splashImg, { justifyContent: 'center', alignItems: 'center' }]}
                >
                  <Text style={[st.splashFbIcon, { color: rarCol }]}>
                    {isBorea ? '\uD83C\uDF2C\uFE0F' : hero.name?.[0]}
                  </Text>
                  <Text style={st.splashFbName}>{hero.name}</Text>
                </LinearGradient>
              )}
            </View>

            <View style={st.identityCard}>
              <View style={st.idRow}>
                <Text style={[st.idLabel]}>Rarità</Text>
                <Text style={[st.idVal, { color: rarCol }]}>{'\u2605'.repeat(Math.min(rarity, 6))}</Text>
              </View>
              <View style={st.idRow}>
                <Text style={st.idLabel}>Elemento</Text>
                <Text style={st.idVal}>{ELEMENT_EMOJI[element] || ''} {hero.element}</Text>
              </View>
              <View style={st.idRow}>
                <Text style={st.idLabel}>Classe</Text>
                <Text style={st.idVal}>{hero.hero_class}</Text>
              </View>
              <View style={st.idRow}>
                <Text style={st.idLabel}>Fazione</Text>
                <Text style={st.idVal}>{hero.faction || '-'}</Text>
              </View>
              <View style={st.idRow}>
                <Text style={st.idLabel}>{'\uD83D\uDC96 Affinità'}</Text>
                <Text style={[st.idVal, { color: '#FF88DD' }]}>
                  Lv {aff.level} / {aff.max_level} {'\u2022'} {aff.current_title}
                </Text>
              </View>
              <View style={st.idRow}>
                <Text style={st.idLabel}>{'\u2728 Costellazione'}</Text>
                <Text style={[st.idVal, { color: '#FFD700' }]}>
                  Stage {con.highest_stage} {'\u2022'} {con.fragments} frammenti
                </Text>
              </View>
              {!data.is_owned && !isBorea && (
                <View style={st.lockedNote}>
                  <Text style={st.lockedTxt}>{'\uD83D\uDD12'} Eroe NON posseduto</Text>
                </View>
              )}
            </View>

            {hero.description && (
              <View style={st.descCard}>
                <Text style={st.descText}>{hero.description}</Text>
              </View>
            )}
          </Animated.View>
        )}

        {/* AFFINITY */}
        {tab === 'affinity' && (
          <Animated.View entering={FadeIn} style={{ gap: 12 }}>
            <LinearGradient
              colors={['rgba(255,136,221,0.15)', 'rgba(255,136,221,0.03)']}
              style={st.affHero}
            >
              <Text style={st.affBigLevel}>Lv {aff.level}</Text>
              <Text style={st.affTitle}>{aff.current_title}</Text>
              <View style={st.affBarWrap}>
                <View style={st.affBarBg}>
                  <LinearGradient
                    colors={['#FF88DD', '#8833CC']}
                    start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }}
                    style={[st.affBarFill, { width: `${(aff.progress.progress || 0) * 100}%` }]}
                  />
                </View>
                <Text style={st.affBarTxt}>
                  {aff.progress.max_reached
                    ? 'MAX'
                    : `${aff.exp} / ${aff.progress.exp_to_next} EXP`}
                </Text>
              </View>
              <Text style={st.affHint}>
                +1 Affinity EXP per ogni battaglia completata con {hero.name} nel team.
              </Text>
              <Text style={st.affHint}>
                Curva totale 0→10: circa 2.450 battaglie senza regali. Oggetti regalo (FASE 2) accelereranno.
              </Text>
            </LinearGradient>

            <Text style={st.sectionTitle}>Ricompense per Livello</Text>
            {(aff.all_rewards || []).map((data_: any) => {
              const lv = data_.level;
              const isUnlocked = lv <= aff.level;
              const isNext = lv === aff.level + 1 && lv <= aff.max_level;
              const stats = data_.bonus_stats || {};
              return (
                <View key={lv} style={[
                  st.rewardRow,
                  isUnlocked && { borderColor: '#FF88DD60', backgroundColor: 'rgba(255,136,221,0.06)' },
                  isNext && { borderColor: '#FFD70080', backgroundColor: 'rgba(255,215,0,0.04)' },
                ]}>
                  <Text style={[
                    st.rewardLevel,
                    isUnlocked && { color: '#FF88DD' },
                    isNext && { color: '#FFD700' },
                  ]}>Lv {lv}</Text>
                  <View style={{ flex: 1 }}>
                    <Text style={[st.rewardTitle, !isUnlocked && !isNext && { color: '#666' }]}>
                      {data_.title || '—'}
                    </Text>
                    {Object.keys(stats).length > 0 && (
                      <Text style={[st.rewardDetail, !isUnlocked && !isNext && { color: '#555' }]}>
                        {Object.entries(stats).map(([k, v]) => 
                          `+${Math.round((v as number) * 100)}% ${STAT_LABEL[k] || k}`
                        ).join(' · ')}
                      </Text>
                    )}
                    {data_.perk && (
                      <Text style={[st.rewardPerk, !isUnlocked && !isNext && { color: '#555' }]}>
                        {'\u2728'} {data_.perk.name}: {data_.perk.description}
                      </Text>
                    )}
                    {data_.unlock && (
                      <Text style={[st.rewardUnlock, !isUnlocked && !isNext && { color: '#555' }]}>
                        {'\uD83D\uDCDC'} Sblocca: {data_.unlock}
                      </Text>
                    )}
                  </View>
                  {isUnlocked && <Text style={st.rewardCheck}>{'\u2705'}</Text>}
                  {isNext && <Text style={st.rewardCheck}>{'\uD83D\uDD52'}</Text>}
                </View>
              );
            })}

            <View style={st.futureBlock}>
              <Text style={st.futureTitle}>{'\uD83C\uDF81'} Regali (FASE 2)</Text>
              <Text style={st.futureDesc}>
                In arrivo: catalogo regali per fazione × elemento, rarità fino a Divino,
                compatibilità (Preferito/Compatibile/Neutro/Disprezzato), e doni ristretti
                specifici per eroe (rarissimi, drop in eventi e shop).
              </Text>
            </View>
          </Animated.View>
        )}

        {/* CONSTELLATION */}
        {tab === 'constellation' && (
          <Animated.View entering={FadeIn} style={{ gap: 12 }}>
            <LinearGradient colors={['rgba(255,215,0,0.15)', 'rgba(255,215,0,0.02)']} style={st.conHero}>
              <Text style={st.conStage}>Stage {con.highest_stage}</Text>
              <Text style={st.conNext}>
                Prossimo: Stage {con.next_stage}
                {con.next_is_boss ? ' \u2620\uFE0F BOSS' : ''}
              </Text>
              <View style={st.conFragRow}>
                <Text style={st.conFrag}>{'\u2728'} {con.fragments}</Text>
                <Text style={st.conFragLabel}>{con.fragment_name}</Text>
              </View>
            </LinearGradient>

            <View style={st.dailyBox}>
              <Text style={st.dailyTitle}>Limite Giornaliero</Text>
              <Text style={st.dailyDesc}>
                Massimo {con.daily_limit} eroi diversi al giorno.{'\n'}
                Oggi: {con.daily_slots_used}/{con.daily_limit} eroi attentati.
                {con.hero_already_attempted_today
                  ? ` ${hero.name} ha già tentato oggi — puoi continuare.`
                  : ` ${con.daily_slots_left} slot rimasti.`}
              </Text>
            </View>

            <Text style={st.sectionTitle}>Struttura Sfide</Text>
            <View style={st.infoBlock}>
              <Text style={st.infoBullet}>{'\u2022'} Eroe {hero.name} OBBLIGATORIO nel team</Text>
              <Text style={st.infoBullet}>{'\u2022'} Nemici in vantaggio crescente</Text>
              <Text style={st.infoBullet}>{'\u2022'} Ogni {con.boss_every} battaglie: BOSS</Text>
              <Text style={st.infoBullet}>{'\u2022'} Drop boss: 1-3 Frammenti d'Anima</Text>
              <Text style={st.infoBullet}>{'\u2022'} Frammenti specifici per {hero.name}, usabili solo per la sua costellazione</Text>
            </View>

            {/* Preview stage list */}
            <Text style={st.sectionTitle}>Prossimi Stage</Text>
            {[1, 2, 3, 4, 5, 6].map(i => {
              const stage = con.highest_stage + i - (con.highest_stage > 0 ? 0 : 0);
              // Ma la logica: mostriamo stage current+1 ... current+6
              const s = con.highest_stage + i;
              const isBoss = s % con.boss_every === 0;
              const isNext = i === 1;
              return (
                <View key={s} style={[
                  st.stageRow,
                  isNext && { borderColor: '#FFD70080', backgroundColor: 'rgba(255,215,0,0.05)' },
                  isBoss && !isNext && { borderColor: '#FF4D6D40' },
                ]}>
                  <Text style={[st.stageNum, isBoss && { color: '#FF4D6D' }]}>
                    Stage {s}
                  </Text>
                  <Text style={[st.stageLabel, isBoss && { color: '#FF4D6D', fontWeight: '900' }]}>
                    {isBoss ? '\u2620\uFE0F BOSS \u2192 Frammenti d\u0027Anima' : 'Battaglia standard'}
                  </Text>
                  {isNext && <Text style={st.stageNext}>{'\uD83D\uDCCD'}</Text>}
                </View>
              );
            })}

            <View style={st.futureBlock}>
              <Text style={st.futureTitle}>{'\u23E9'} Skip (FASE 3)</Text>
              <Text style={st.futureDesc}>
                Una volta raggiunto un boss potrai saltare rapidamente al massimo già raggiunto
                senza rifare le battaglie manualmente. Gated da VIP1+ (da confermare).
              </Text>
            </View>
          </Animated.View>
        )}

        {/* ACTIONS */}
        {tab === 'actions' && (
          <Animated.View entering={FadeIn} style={{ gap: 12 }}>
            {data.in_tutorial ? (
              <View style={st.actionCard}>
                <Text style={st.actionTitle}>{'\uD83C\uDF93'} Tutorial in corso</Text>
                <Text style={st.actionDesc}>
                  Borea è il tuo eroe homepage durante il tutorial. Alla fine sceglierai un tuo eroe.
                </Text>
                <TouchableOpacity
                  onPress={completeTutorial}
                  disabled={acting}
                  style={st.actionBtnWrap}
                >
                  <LinearGradient
                    colors={['#44AAFF', '#2288CC']}
                    start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }}
                    style={st.actionBtn}
                  >
                    <Text style={st.actionBtnTxt}>
                      {acting ? '...' : 'Termina Tutorial'}
                    </Text>
                  </LinearGradient>
                </TouchableOpacity>
              </View>
            ) : null}

            <View style={st.actionCard}>
              <Text style={st.actionTitle}>{'\uD83C\uDFE0'} Imposta come Home Hero</Text>
              <Text style={st.actionDesc}>
                {data.is_home
                  ? `${hero.name} è già il tuo eroe mostrato in homepage.`
                  : `Mostra ${hero.name} come splash principale nella homepage.`}
              </Text>
              <TouchableOpacity
                onPress={setHomeHero}
                disabled={acting || data.is_home || (!data.is_owned && !isBorea)}
                style={st.actionBtnWrap}
              >
                <LinearGradient
                  colors={data.is_home ? ['#444', '#333'] : ['#FFD700', '#CC9900']}
                  start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }}
                  style={st.actionBtn}
                >
                  <Text style={[
                    st.actionBtnTxt,
                    { color: data.is_home ? '#888' : '#1a0e2e' },
                  ]}>
                    {data.is_home ? 'Già Home Hero' : (acting ? '...' : 'Imposta come Home')}
                  </Text>
                </LinearGradient>
              </TouchableOpacity>
              {!data.is_owned && !isBorea && (
                <Text style={st.actionWarn}>
                  {'\u26A0\uFE0F'} Devi prima possedere questo eroe.
                </Text>
              )}
            </View>

            <View style={st.actionCard}>
              <Text style={st.actionTitle}>{'\uD83D\uDCD6'} Scheda Enciclopedia</Text>
              <Text style={st.actionDesc}>
                Vedi stats Base vs Max Potenziale, skill complete e progressione.
              </Text>
              <TouchableOpacity
                onPress={() => router.push({ pathname: '/hero-encyclopedia', params: { id: hero.id } } as any)}
                style={st.actionBtnWrap}
              >
                <LinearGradient
                  colors={['#4ECDC4', '#2a8a84']}
                  start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }}
                  style={st.actionBtn}
                >
                  <Text style={[st.actionBtnTxt, { color: '#0a0612' }]}>Apri Enciclopedia</Text>
                </LinearGradient>
              </TouchableOpacity>
            </View>
          </Animated.View>
        )}

        <View style={{ height: 30 }} />
      </ScrollView>
    </SafeAreaView>
  );
}

const st = StyleSheet.create({
  root: { flex: 1, backgroundColor: '#0a0612' },
  loading: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  err: { color: '#FF4D6D', fontSize: 14, fontWeight: '700' },

  header: { paddingHorizontal: 14, paddingBottom: 12, paddingTop: 8 },
  headerRow: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  backBtn: { padding: 8, backgroundColor: 'rgba(255,255,255,0.08)', borderRadius: 8 },
  backTxt: { color: '#fff', fontSize: 13, fontWeight: '700' },
  title: { color: '#FFD700', fontSize: 18, fontWeight: '900', letterSpacing: 0.3 },
  subtitle: { fontSize: 14, fontWeight: '800', marginTop: 2 },
  homeChip: {
    color: '#FFD700', fontSize: 10, fontWeight: '900',
    backgroundColor: 'rgba(255,215,0,0.12)', paddingHorizontal: 8, paddingVertical: 3,
    borderRadius: 6, borderWidth: 1, borderColor: 'rgba(255,215,0,0.4)',
  },

  tabs: {
    flexDirection: 'row', gap: 4, paddingHorizontal: 6, paddingVertical: 8,
    borderBottomColor: 'rgba(255,255,255,0.06)', borderBottomWidth: 1,
  },
  tabBtn: {
    flex: 1, paddingVertical: 8, paddingHorizontal: 4, borderRadius: 8,
    alignItems: 'center',
    borderWidth: 1, borderColor: 'transparent',
  },
  tabBtnActive: {
    backgroundColor: 'rgba(255,215,0,0.08)', borderColor: '#FFD70040',
  },
  tabIcon: { fontSize: 16 },
  tabLabel: { color: '#BBB', fontSize: 10, fontWeight: '800', marginTop: 2 },

  body: { padding: 12 },

  splashBig: {
    width: '100%', aspectRatio: 1, borderRadius: 16, overflow: 'hidden',
    borderWidth: 2, backgroundColor: '#000', alignSelf: 'center',
    maxWidth: 360, alignItems: 'center', justifyContent: 'center',
  },
  splashImg: { width: '100%', height: '100%' },
  splashFbIcon: { fontSize: 120, fontWeight: '900' },
  splashFbName: { color: '#fff', fontSize: 30, fontWeight: '900', marginTop: 8, letterSpacing: 1 },

  identityCard: {
    backgroundColor: 'rgba(255,255,255,0.03)',
    borderRadius: 12, padding: 12, borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.06)', gap: 6,
  },
  idRow: {
    flexDirection: 'row', justifyContent: 'space-between',
    alignItems: 'center', paddingVertical: 3,
  },
  idLabel: { color: '#999', fontSize: 11, fontWeight: '700' },
  idVal: { color: '#fff', fontSize: 12, fontWeight: '900' },
  lockedNote: {
    marginTop: 6, padding: 8, backgroundColor: 'rgba(255,77,109,0.1)',
    borderRadius: 6, borderWidth: 1, borderColor: 'rgba(255,77,109,0.3)',
  },
  lockedTxt: { color: '#FF4D6D', fontSize: 11, fontWeight: '700', textAlign: 'center' },

  descCard: {
    padding: 12, backgroundColor: 'rgba(255,255,255,0.02)',
    borderRadius: 10, borderWidth: 1, borderColor: 'rgba(255,255,255,0.06)',
  },
  descText: { color: '#CCC', fontSize: 12, fontStyle: 'italic', lineHeight: 17 },

  affHero: {
    padding: 16, borderRadius: 14, borderWidth: 1,
    borderColor: 'rgba(255,136,221,0.3)', alignItems: 'center',
  },
  affBigLevel: { color: '#FF88DD', fontSize: 52, fontWeight: '900', letterSpacing: 1 },
  affTitle: { color: '#fff', fontSize: 14, fontWeight: '800', marginTop: -4 },
  affBarWrap: { width: '100%', marginTop: 12, gap: 4 },
  affBarBg: {
    height: 10, backgroundColor: 'rgba(255,255,255,0.08)',
    borderRadius: 5, overflow: 'hidden',
  },
  affBarFill: { height: '100%' },
  affBarTxt: { color: '#FF88DD', fontSize: 11, textAlign: 'center', fontWeight: '800' },
  affHint: { color: '#BBB', fontSize: 10, textAlign: 'center', marginTop: 8 },

  sectionTitle: { color: '#FFD700', fontSize: 13, fontWeight: '900', marginTop: 8 },

  rewardRow: {
    flexDirection: 'row', alignItems: 'center', gap: 10,
    padding: 10, borderRadius: 8, borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.06)',
    backgroundColor: 'rgba(255,255,255,0.02)',
  },
  rewardLevel: {
    color: '#999', fontSize: 13, fontWeight: '900',
    minWidth: 40,
  },
  rewardTitle: { color: '#FFF', fontSize: 12, fontWeight: '800' },
  rewardDetail: { color: '#44DD88', fontSize: 10, marginTop: 2 },
  rewardPerk: { color: '#FFC629', fontSize: 10, marginTop: 2 },
  rewardUnlock: { color: '#AEC6FF', fontSize: 10, marginTop: 2 },
  rewardCheck: { fontSize: 18 },

  futureBlock: {
    marginTop: 10, padding: 12,
    backgroundColor: 'rgba(255,255,255,0.03)',
    borderRadius: 10, borderWidth: 1, borderColor: 'rgba(255,215,0,0.2)',
    borderStyle: 'dashed',
  },
  futureTitle: { color: '#FFD700', fontSize: 12, fontWeight: '900' },
  futureDesc: { color: '#CCC', fontSize: 11, marginTop: 6, lineHeight: 16 },

  conHero: {
    padding: 16, borderRadius: 14, borderWidth: 1,
    borderColor: 'rgba(255,215,0,0.3)', alignItems: 'center',
  },
  conStage: { color: '#FFD700', fontSize: 44, fontWeight: '900', letterSpacing: 1 },
  conNext: { color: '#fff', fontSize: 13, fontWeight: '800', marginTop: -4 },
  conFragRow: { flexDirection: 'row', alignItems: 'center', gap: 8, marginTop: 10 },
  conFrag: { color: '#FFD700', fontSize: 20, fontWeight: '900' },
  conFragLabel: { color: '#DDD', fontSize: 10, fontStyle: 'italic' },

  dailyBox: {
    padding: 12, backgroundColor: 'rgba(68,170,255,0.06)',
    borderRadius: 10, borderWidth: 1, borderColor: 'rgba(68,170,255,0.3)',
  },
  dailyTitle: { color: '#44AAFF', fontSize: 12, fontWeight: '900' },
  dailyDesc: { color: '#CCC', fontSize: 11, marginTop: 5, lineHeight: 16 },

  infoBlock: {
    padding: 12, backgroundColor: 'rgba(255,255,255,0.02)',
    borderRadius: 10, borderWidth: 1, borderColor: 'rgba(255,255,255,0.06)', gap: 4,
  },
  infoBullet: { color: '#DDD', fontSize: 11, lineHeight: 16 },

  stageRow: {
    flexDirection: 'row', alignItems: 'center', gap: 10,
    padding: 10, borderRadius: 8, borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.06)',
    backgroundColor: 'rgba(255,255,255,0.02)',
  },
  stageNum: { color: '#fff', fontSize: 12, fontWeight: '900', minWidth: 70 },
  stageLabel: { flex: 1, color: '#CCC', fontSize: 11 },
  stageNext: { fontSize: 14 },

  actionCard: {
    padding: 14, backgroundColor: 'rgba(255,255,255,0.03)',
    borderRadius: 12, borderWidth: 1, borderColor: 'rgba(255,255,255,0.06)',
  },
  actionTitle: { color: '#FFD700', fontSize: 14, fontWeight: '900' },
  actionDesc: { color: '#CCC', fontSize: 11, marginTop: 6, lineHeight: 16 },
  actionBtnWrap: { marginTop: 10, borderRadius: 10, overflow: 'hidden' },
  actionBtn: { paddingVertical: 12, alignItems: 'center' },
  actionBtnTxt: { fontSize: 13, fontWeight: '900', letterSpacing: 0.5 },
  actionWarn: { color: '#FFB347', fontSize: 10, marginTop: 6, textAlign: 'center' },
});
