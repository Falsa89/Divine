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
      { label: 'Torre', icon: '\uD83C\uDFEF', route: '/tower', gradient: ['#8844FF', '#5522CC'] as const },
      { label: 'Arena PvP', icon: '\uD83E\uDD4A', route: '/pvp', gradient: ['#FF4444', '#CC2222'] as const },
      { label: 'Fucina di Efesto', icon: '\u2692\uFE0F', route: '/equipment', gradient: ['#FFAA44', '#CC6622'] as const },
      { label: 'Oggetti Esclusivi', icon: '\uD83D\uDC51', route: '/exclusive', gradient: ['#FFD700', '#CC9900'] as const },
    ],
  },
  {
    title: 'Progressione',
    items: [
      { label: 'Addestramento Eroico', icon: '\u2694\uFE0F', route: '/hero-training', gradient: ['#FFD700', '#BB55FF'] as const },
      { label: 'Santuario', icon: '\u26E9\uFE0F', route: '/sanctuary', gradient: ['#FF77CC', '#CC5599'] as const },
      { label: 'Artefatti & Costellazioni', icon: '\uD83D\uDC8E', route: '/artifacts', gradient: ['#BB55FF', '#8833CC'] as const },
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
      { label: 'Economia & Negozi', icon: '\uD83D\uDCB0', route: '/economy', gradient: ['#FFD700', '#CC9900'] as const },
      { label: 'Inventario', icon: '\uD83C\uDF92', route: '/inventory', gradient: ['#FF8844', '#CC6622'] as const },
      { label: 'Negozio Oggetti', icon: '\uD83D\uDED2', route: '/item-shop', gradient: ['#44DD88', '#22AA66'] as const },
      { label: 'Negozio', icon: '\uD83C\uDFEA', route: '/shop', gradient: ['#44AAFF', '#2288CC'] as const },
      { label: 'VIP', icon: '\uD83D\uDC51', route: '/vip', gradient: ['#FFD700', '#DD9900'] as const },
      { label: 'Sprite Test', icon: '\uD83C\uDFAC', route: '/sprite-test', gradient: ['#FF6B35', '#CC4400'] as const },
    ],
  },
  {
    title: 'Sociale',
    items: [
      { label: 'Gilda & Fazioni', icon: '\uD83C\uDFDB\uFE0F', route: '/guild', gradient: ['#6644FF', '#4422CC'] as const },
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
      { label: 'Classifiche', icon: '\uD83C\uDFC6', route: '/rankings', gradient: ['#FFD700', '#CC9900'] as const },
      { label: 'Posta', icon: '\uD83D\uDCE9', route: '/mail', gradient: ['#4499FF', '#2277CC'] as const },
      { label: 'Amici', icon: '\uD83D\uDC65', route: '/friends', gradient: ['#4499FF', '#2277CC'] as const },
      { label: 'Seleziona Server', icon: '\uD83C\uDF10', route: '/servers', gradient: ['#44CC88', '#229966'] as const },
      { label: 'Eventi Giornalieri', icon: '\uD83C\uDF89', route: '/events', gradient: ['#44AAFF', '#2288CC'] as const },
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
            <ResourceBadge icon={'\u26A1'} value={`${user?.stamina || 0}/${user?.max_stamina || 100}`} compact />
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

        <TouchableOpacity style={s.logoutBtnOuter} onPress={logout} activeOpacity={0.7}>
          <LinearGradient
            colors={['rgba(255,68,68,0.12)', 'rgba(255,68,68,0.05)']}
            style={s.logoutBtn}
          >
            <Text style={s.logoutTxt}>ESCI DAL GIOCO</Text>
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
  logoutBtn: {
    padding: 12,
    alignItems: 'center',
    borderRadius: 10,
    borderWidth: 1,
    borderColor: 'rgba(255,68,68,0.2)',
  },
  logoutTxt: { color: COLORS.error, fontSize: 12, fontWeight: '900', letterSpacing: 2 },
});
