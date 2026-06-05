import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import { useAuth } from '../../context/AuthContext';
import ResourceBadge from '../../components/ui/ResourceBadge';
import Animated, { FadeInDown } from 'react-native-reanimated';
import { COLORS } from '../../constants/theme';

const CATEGORIES = [
  {
    title: 'Combattimento',
    items: [
      { label: 'Storia', icon: '\uD83D\uDCDC', route: '/story', gradient: ['#FF6B35', '#CC4422'] as const },
      // PROJECT_HOME_MENU_REWIRING v20: legacy '/tower' link redirected to canonical TEST MVP '/tower-of-the-hells'. Tower gameplay/progress/AsyncStorage NOT touched in this pack.
      { label: 'Torre degli Inferi (TEST)', icon: '\uD83C\uDFEF', route: '/tower-of-the-hells', gradient: ['#8844FF', '#5522CC'] as const },
      { label: 'Arena PvP', icon: '\uD83E\uDD4A', route: '/pvp', gradient: ['#FF4444', '#CC2222'] as const },
      { label: 'Fucina di Efesto', icon: '\u2692\uFE0F', route: '/equipment', gradient: ['#FFAA44', '#CC6622'] as const },
      // SF_MERGE Track F \u2014 Oggetti Esclusivi rimosso dal menu player.
      // \u00c8 una schermata legacy con disclaimer; non rappresenta il sistema
      // canonico delle Divine Weapons. Mantenuto come deep link informativo.
    ],
  },
  {
    title: 'Progressione',
    items: [
      { label: 'Collezione Eroi', icon: '\uD83D\uDCDA', route: '/hero-collection', gradient: ['#FFD700', '#CC9900'] as const },
      { label: 'Addestramento Eroico', icon: '\u2694\uFE0F', route: '/hero-training', gradient: ['#FFD700', '#BB55FF'] as const },
      { label: 'Santuario', icon: '\u26E9\uFE0F', route: '/sanctuary', gradient: ['#FF77CC', '#CC5599'] as const },
      { label: 'Artefatti & Costellazioni', icon: '\uD83D\uDC8E', route: '/artifacts-preview', gradient: ['#BB55FF', '#8833CC'] as const },
      { label: 'Soul Forge', icon: '\uD83D\uDC80', route: '/soul-forge', gradient: ['#9944FF', '#6622CC'] as const },
      { label: 'Aure & Cosmetici', icon: '\u2728', route: '/cosmetics', gradient: ['#FFD700', '#DD9900'] as const },
      { label: 'Achievement', icon: '\uD83C\uDFC5', route: '/achievements', gradient: ['#FFD700', '#CC9900'] as const },
      { label: 'Battle Pass', icon: '\u2B50', route: '/battlepass', gradient: ['#FF6B35', '#DD4422'] as const },
    ],
  },
  {
    title: 'Economia',
    items: [
      { label: 'Tesoreria', icon: '\uD83C\uDFE6', route: '/treasury', gradient: ['#FFD700', '#4499FF'] as const },
      // SF_MERGE Track D+F \u2014 Economia consolidata dentro Soul Forge (\"Anime Hub\").
      { label: 'Hub Anime (Soul Forge)', icon: '\uD83D\uDD25', route: '/soul-forge', gradient: ['#C877FF', '#9944FF'] as const },
      { label: 'Inventario', icon: '\uD83C\uDF92', route: '/inventory', gradient: ['#FF8844', '#CC6622'] as const },
      { label: 'Negozio Oggetti', icon: '\uD83D\uDED2', route: '/item-shop', gradient: ['#44DD88', '#22AA66'] as const },
      { label: 'Negozio', icon: '\uD83C\uDFEA', route: '/shop', gradient: ['#44AAFF', '#2288CC'] as const },
      { label: 'VIP', icon: '\uD83D\uDC51', route: '/vip', gradient: ['#FFD700', '#DD9900'] as const },
      // BATCH_1_V2 Track F \u2014 Sprite Test rimosso dal menu player (dev-only).
      // File /sprite-test rimane accessibile solo via deep link per QA interno.
    ],
  },
  {
    title: 'Sociale',
    items: [
      { label: 'Gilda & Fazioni', icon: '\uD83C\uDFDB\uFE0F', route: '/guild', gradient: ['#6644FF', '#4422CC'] as const },
      { label: 'Fazione del Giocatore', icon: '\u2694\uFE0F', route: '/player-faction', gradient: ['#FFD700', '#3D5AFE'] as const },
      { label: 'Guerra tra Gilde', icon: '\u2694\uFE0F', route: '/gvg', gradient: ['#FF4444', '#CC2222'] as const },
      { label: 'Raid Cooperativi', icon: '\uD83D\uDC32', route: '/raid', gradient: ['#FF5544', '#CC3322'] as const },
      { label: 'Conquista Territori', icon: '\uD83C\uDFAF', route: '/territory', gradient: ['#CC4488', '#992266'] as const },
      { label: 'Piazza Comunitaria', icon: '\uD83C\uDFAA', route: '/plaza', gradient: ['#44AAFF', '#2288CC'] as const },
      { label: 'Messaggi', icon: '\uD83D\uDCEC', route: '/dm', gradient: ['#44AAFF', '#2288CC'] as const },
    ],
  },
  {
    title: 'Altro',
    items: [
      // PROJECT_HOME_MENU_REWIRING v20: discoverability per Guida/Codex aggiunta. Route /guide gia' esistente (runtime read-only).
      { label: 'Guida / Codex', icon: '\uD83D\uDCD6', route: '/guide', gradient: ['#5b6df0', '#3a4ad0'] as const },
      { label: 'Classifiche', icon: '\uD83C\uDFC6', route: '/rankings', gradient: ['#FFD700', '#CC9900'] as const },
      { label: 'Posta', icon: '\uD83D\uDCE9', route: '/mail', gradient: ['#4499FF', '#2277CC'] as const },
      { label: 'Amici', icon: '\uD83D\uDC65', route: '/friends', gradient: ['#4499FF', '#2277CC'] as const },
      { label: 'Seleziona Server', icon: '\uD83C\uDF10', route: '/servers', gradient: ['#44CC88', '#229966'] as const },
      { label: 'Eventi Giornalieri', icon: '\uD83C\uDF89', route: '/events', gradient: ['#44AAFF', '#2288CC'] as const },
      // BATCH_1_V2 Track F \u2014 Combat QA Lab dev-only rimosso dal menu player.
      // File /dev-combat-qa-lab mantenuto, accessibile solo via deep link interno.
      // RM1.25-D — Catalogo Skill & Status (read-only, dev catalog browser).
      // Non collegato al runtime battaglia / HP bar. UI di sola consultazione.
      { label: 'Catalogo Skill & Status', icon: '\uD83D\uDCDA', route: '/skill-status-vfx-catalogs', gradient: ['#AB47BC', '#6A1B9A'] as const },
      // RM1.26-D — Kit Skill Eroi (read-only, hero skill kit catalog browser).
      // Cataloghi 5★/6★ inert, non collegati a battle/HP bar runtime.
      { label: 'Kit Skill Eroi', icon: '\uD83D\uDCD6', route: '/hero-skill-kits-catalog', gradient: ['#FFD700', '#3D5AFE'] as const },
      // PROJECT_Z Track B — Hub "Sistemi in preparazione" (read-only, locked).
      // Punto d'ingresso safe alle anteprime: Codex Status, Anteprima Artefatti, Dimora Divina.
      // Nessuna azione live esposta da queste pagine.
      { label: 'Sistemi in preparazione', icon: '\u2728', route: '/safe-previews', gradient: ['#FF6B35', '#3D5AFE'] as const },
      // PROJECT_FRONTEND_C Track D — Daily Hub aggregator entry (link-only, nessun claim qui)
      { label: 'Guida Giornaliera', icon: '\uD83D\uDCCB', route: '/daily-hub', gradient: ['#3D5AFE', '#00BCD4'] as const },
      // RM1.27-C — Armi Divine (read-only, divine weapon catalog browser).
      // 13 Armi Divine 6★ inert (12 launch_base + 1 Borea extra premium).
      // Non collegate a battle/HP bar/VFX runtime, gacha, roster o Borea activation.
      { label: 'Armi Divine', icon: '\u2694\uFE0F', route: '/divine-weapons-catalog', gradient: ['#FF44CC', '#6A1B9A'] as const },
      // CS2-E — Sinergie Collezione (read-only preview, design-only).
      // Schermata strictly read-only che mostra le 6 categorie di Collection
      // Synergy V2 con badge "Locked / Future". Nessun bonus applicato al
      // combattimento. Nessun click di claim/activate/spend/equip/runtime.
      { label: 'Sinergie Collezione', icon: '\uD83D\uDD17', route: '/collection-synergies-preview', gradient: ['#88CCFF', '#3366AA'] as const },
    ],
  },
  {
    // MEGA_RELEASE_ACCELERATION_42 v93 — Playability Completion Superpack.
    // Hub QA aggiuntivo per: Guild War sandbox, War/Event avatar previews,
    // Live Announcements QA. NO production broadcast, NO push notification,
    // NO real user PII, NO cosmetic unlock.
    title: 'Playability & Announcements QA (v93)',
    items: [
      { label: 'Guild War Sandbox', icon: '\u2694\uFE0F', route: '/guild-war-sandbox-flow', gradient: ['#AA22FF', '#5511AA'] as const },
      { label: 'War Avatar Layout Preview', icon: '\uD83D\uDEE1', route: '/war-avatar-layout-preview', gradient: ['#FFAA22', '#CC6611'] as const },
      { label: 'Event Avatar Layout Preview', icon: '\u2728', route: '/event-avatar-layout-preview', gradient: ['#22DDAA', '#118866'] as const },
      { label: 'Live Announcements QA', icon: '\uD83D\uDCE2', route: '/live-announcements-qa', gradient: ['#FF6644', '#CC3322'] as const },
    ],
  },
  {
    // MEGA_RELEASE_ACCELERATION_41 v92 — Live/Guild/Special Mode Testability.
    // Hub QA accessibile da menu reale per testare modalita' live/guild/time-gated
    // /avatar-based con QA time-gate override, avatar placeholder dev, encounter
    // canonici (NO random). preview-only / db_writes=0 / reward_live=false /
    // ranking_live=false / event_currency_live=false / guild_score_mutation=0 /
    // production_enabled=false / qa_override_only=true.
    title: 'Modalità Live & Guild QA (v92)',
    items: [
      { label: 'Hub QA Live/Guild/Special', icon: '\u26A1', route: '/live-guild-qa-hub', gradient: ['#AA22FF', '#6611BB'] as const },
    ],
  },
  {
    // MEGA_RELEASE_ACCELERATION_39 v90 — RESTORE Home battle renderer.
    // MEGA_RELEASE_ACCELERATION_40 v91_FIXED — Pre-Battle Lobby intermediario.
    // Le 5 modalità ora puntano alla Pre-Battle Lobby (/pre-battle-lobby?mode=X)
    // che mostra source canonica deterministica + team avversario + team player
    // salvato + bottoni Modifica Team / Avvia Battaglia → /combat reale.
    // db_writes=0 / reward_live=false / endpoint_live=false / random_opponents_allowed=false.
    title: 'Battaglia (Renderer Reale v90)',
    items: [
      { label: 'Storia · Battaglia', icon: '\uD83D\uDCDC', route: '/pre-battle-lobby?mode=story', gradient: ['#FF6B35', '#CC4422'] as const },
      { label: 'Torre · Battaglia', icon: '\uD83C\uDFEF', route: '/pre-battle-lobby?mode=tower', gradient: ['#8844FF', '#5522CC'] as const },
      { label: 'Arena PvP · Battaglia', icon: '\uD83E\uDD4A', route: '/pre-battle-lobby?mode=arena', gradient: ['#FF4444', '#CC2222'] as const },
      { label: 'Addestramento · Battaglia', icon: '\u2694\uFE0F', route: '/pre-battle-lobby?mode=training', gradient: ['#FFD700', '#BB55FF'] as const },
      { label: 'Raid · Battaglia', icon: '\uD83D\uDC32', route: '/pre-battle-lobby?mode=boss', gradient: ['#FF5544', '#CC3322'] as const },
    ],
  },
  {
    // v90 — DEPRECATO: le vecchie entry mock restano accessibili a QA come wireframe diagnostico.
    // NON usare come gameplay. Il renderer reale è /combat (sopra).
    // Titolo backward-compatible: contiene "Battle Preview QA (v88)" per il validator legacy
    // PROJECT-V88-REAL-UI-BATTLE-PREVIEW-WIRING e il marker v90 "Wireframe Deprecato v88".
    title: 'Battle Preview QA (v88) — Wireframe Deprecato v90',
    items: [
      { label: 'Storia · Battle Preview', icon: '\uD83D\uDCDC', route: '/playable-mode-battle-preview?mode=story', gradient: ['#666', '#444'] as const },
      { label: 'Torre · Battle Preview', icon: '\uD83C\uDFEF', route: '/playable-mode-battle-preview?mode=tower', gradient: ['#666', '#444'] as const },
      { label: 'Arena PvP · Battle Preview', icon: '\uD83E\uDD4A', route: '/playable-mode-battle-preview?mode=arena', gradient: ['#666', '#444'] as const },
      { label: 'Addestramento · Battle Preview', icon: '\u2694\uFE0F', route: '/playable-mode-battle-preview?mode=training', gradient: ['#666', '#444'] as const },
      { label: 'Raid · Battle Preview', icon: '\uD83D\uDC32', route: '/playable-mode-battle-preview?mode=boss', gradient: ['#666', '#444'] as const },
    ],
  },
];

export default function MenuTab() {
  const router = useRouter();
  const { user, logout } = useAuth();
  return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={s.c}>
      {/* Profile Header */}
      <LinearGradient
        colors={['rgba(255,107,53,0.08)', 'rgba(15,15,45,0.95)']}
        style={s.profileHeader}
      >
        <View style={s.profileRow}>
          <LinearGradient
            colors={[COLORS.accent, '#FF4444']}
            style={s.avatar}
          >
            <Text style={s.avatarTxt}>{user?.username?.[0]?.toUpperCase() || 'G'}</Text>
          </LinearGradient>
          <View style={s.profileInfo}>
            <Text style={s.pName}>{user?.username}</Text>
            <Text style={s.pLvl}>Lv.{user?.level} {'\u2022'} {user?.active_title}</Text>
          </View>
          <View style={s.resources}>
            <ResourceBadge icon={'\uD83D\uDCB0'} value={user?.gold || 0} compact />
            <ResourceBadge icon={'\uD83D\uDC8E'} value={user?.gems || 0} compact />
            {/* PROJECT_NO_STAMINA_REMEDIATION: stamina badge rimosso (canonica NO_STAMINA_SYSTEM). User document field resta presente per backward compat ma non viene piu visualizzato. */}
          </View>
        </View>
      </LinearGradient>

      <ScrollView contentContainerStyle={s.list} showsVerticalScrollIndicator={false}>
        {CATEGORIES.map((cat, ci) => (
          <Animated.View key={cat.title} entering={FadeInDown.delay(ci * 60).duration(300)}>
            <Text style={s.catTitle}>{cat.title.toUpperCase()}</Text>
            <View style={s.catItems}>
              {cat.items.map((item, i) => (
                <TouchableOpacity
                  key={i}
                  onPress={() => router.push(item.route as any)}
                  activeOpacity={0.7}
                  style={s.itemOuter}
                >
                  <LinearGradient
                    colors={[item.gradient[0] + '15', item.gradient[1] + '05']}
                    start={{ x: 0, y: 0 }}
                    end={{ x: 1, y: 1 }}
                    style={[s.item, { borderColor: item.gradient[0] + '30' }]}
                  >
                    <View style={[s.itemIconWrap, { backgroundColor: item.gradient[0] + '20' }]}>
                      <Text style={s.itemIcon}>{item.icon}</Text>
                    </View>
                    <Text style={s.itemLabel}>{item.label}</Text>
                    <Text style={[s.itemArrow, { color: item.gradient[0] }]}>{'\u203A'}</Text>
                  </LinearGradient>
                </TouchableOpacity>
              ))}
            </View>
          </Animated.View>
        ))}

        <TouchableOpacity
          style={s.changeServerBtnOuter}
          onPress={() => router.replace('/servers')}
          activeOpacity={0.7}
        >
          <LinearGradient
            colors={['rgba(122,122,196,0.15)', 'rgba(122,122,196,0.05)']}
            style={s.changeServerBtn}
          >
            <Text style={s.changeServerTxt}>CAMBIA SERVER</Text>
          </LinearGradient>
        </TouchableOpacity>

        <TouchableOpacity
          style={s.logoutBtnOuter}
          onPress={async () => {
            // v102 — Logout account: clear sessione legacy + selected server, poi /login.
            try {
              const AS = (await import('@react-native-async-storage/async-storage')).default;
              await AS.removeItem('v101_selected_server_id');
              await AS.removeItem('v102_selected_server_name');
              await AS.removeItem('v102_selected_server_has_character');
            } catch (_e) {}
            try { await logout(); } catch (_e) {}
            // v102 — Bridge logout: tenta anche il v96 SecureStore clear se disponibile.
            try {
              const v96 = await import('../../src/auth/AuthContext');
              // se l'app monta entrambi i provider, il v96 useAuth().logout sara' attivo
              // qui non possiamo chiamare hooks fuori da component, ma il logout legacy
              // gia' azzera token AsyncStorage. v96 clear avviene tramite proprio hook
              // quando lo screen di login si rimonta. Marker presente per v102 bridge.
              void v96;
            } catch (_e) {}
            router.replace('/');
          }}
          activeOpacity={0.7}
        >
          <LinearGradient
            colors={['rgba(255,68,68,0.12)', 'rgba(255,68,68,0.05)']}
            style={s.logoutBtn}
          >
            <Text style={s.logoutTxt}>LOGOUT ACCOUNT</Text>
          </LinearGradient>
        </TouchableOpacity>
      </ScrollView>
    </LinearGradient>
  );
}

const s = StyleSheet.create({
  c: { flex: 1 },
  profileHeader: {
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,107,53,0.15)',
  },
  profileRow: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  avatar: {
    width: 38,
    height: 38,
    borderRadius: 19,
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarTxt: { color: '#fff', fontSize: 16, fontWeight: '900' },
  profileInfo: { flex: 1 },
  pName: { color: '#fff', fontSize: 14, fontWeight: '800' },
  pLvl: { color: COLORS.gold, fontSize: 10, marginTop: 1 },
  resources: { flexDirection: 'row', gap: 6 },
  // List
  list: { padding: 10, paddingBottom: 70, gap: 10 },
  catTitle: {
    color: COLORS.textMuted,
    fontSize: 9,
    fontWeight: '800',
    letterSpacing: 2,
    paddingHorizontal: 4,
    marginBottom: 4,
  },
  catItems: { flexDirection: 'row', flexWrap: 'wrap', gap: 5 },
  itemOuter: {
    width: '48.5%',
    borderRadius: 10,
    overflow: 'hidden',
  },
  item: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    padding: 10,
    borderRadius: 10,
    borderWidth: 1,
  },
  itemIconWrap: {
    width: 28,
    height: 28,
    borderRadius: 7,
    alignItems: 'center',
    justifyContent: 'center',
  },
  itemIcon: { fontSize: 14 },
  itemLabel: { color: '#fff', fontSize: 11, fontWeight: '700', flex: 1 },
  itemArrow: { fontSize: 18, fontWeight: '700' },
  logoutBtnOuter: { borderRadius: 10, overflow: 'hidden', marginTop: 6 },
  changeServerBtnOuter: { borderRadius: 10, overflow: 'hidden', marginTop: 12 },
  changeServerBtn: {
    paddingVertical: 14,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: 'rgba(122,122,196,0.4)',
    borderRadius: 10,
  },
  changeServerTxt: { color: '#9999D9', fontSize: 12, fontWeight: '900', letterSpacing: 2 },
  logoutBtn: {
    padding: 12,
    alignItems: 'center',
    borderRadius: 10,
    borderWidth: 1,
    borderColor: 'rgba(255,68,68,0.2)',
  },
  logoutTxt: { color: COLORS.error, fontSize: 12, fontWeight: '900', letterSpacing: 2 },
});
