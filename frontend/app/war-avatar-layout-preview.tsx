/**
 * v93 — War Avatar Layout Preview (DEV PLACEHOLDER).
 * Layout-only test screen per posizionamento war avatar.
 * NO cosmetic unlock, NO inventory, NO monetization, NO DB writes.
 */
import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, SafeAreaView } from 'react-native';
import { useRouter } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { AvatarPlaceholderWarMini } from '../components/avatarPlaceholders/AvatarPlaceholderDev';

const LANES = [
  { id: 'lane_north', label: 'Corsia Nord', x: 1 },
  { id: 'lane_center', label: 'Corsia Centrale', x: 2 },
  { id: 'lane_south', label: 'Corsia Sud', x: 3 },
];

export default function WarAvatarLayoutPreview() {
  const router = useRouter();
  const goBack = () => {
    if (router.canGoBack()) router.back();
    else router.push('/live-guild-qa-hub' as any);
  };

  return (
    <SafeAreaView style={s.safe}>
      <LinearGradient colors={['#1A0F30', '#3A1F60']} style={s.bg}>
        <ScrollView contentContainerStyle={s.scroll}>
          <TouchableOpacity onPress={goBack} style={s.backBtn}>
            <Text style={s.backTxt}>← Indietro</Text>
          </TouchableOpacity>
          <Text style={s.title}>War Avatar Layout Preview</Text>
          <Text style={s.subtitle}>v93 · DEV PLACEHOLDER · NO COSMETIC UNLOCK · NO INVENTORY</Text>

          <View style={s.banner}>
            <Text style={s.bannerTxt}>
              QA layout preview con avatar war mini DEV. Asset placeholder, NON canonical,
              NON finale. Nessuna mutazione di cosmetici/inventario/account.
            </Text>
          </View>

          <Text style={s.section}>Mappa corsie (war territory mock)</Text>
          <View style={s.lanesRow}>
            {LANES.map((l) => (
              <View key={l.id} style={s.lane}>
                <Text style={s.laneLabel}>{l.label}</Text>
                <AvatarPlaceholderWarMini size={70} />
                <Text style={s.laneSub}>alias: qa_alias_player_{l.x.toString().padStart(3, '0')}</Text>
              </View>
            ))}
          </View>

          <Text style={s.section}>Selection panel</Text>
          <View style={s.selectionRow}>
            {[1, 2, 3, 4].map((i) => (
              <View key={i} style={s.selectionCell}>
                <AvatarPlaceholderWarMini size={48} label={`SLOT ${i}`} />
              </View>
            ))}
          </View>

          <View style={s.flagsBox}>
            <Text style={s.flagsTxt}>DEV PLACEHOLDER</Text>
            <Text style={s.flagsTxt}>NO COSMETIC UNLOCK</Text>
            <Text style={s.flagsTxt}>NO INVENTORY</Text>
            <Text style={s.flagsTxt}>NO MONETIZATION</Text>
            <Text style={s.flagsTxt}>NO FINAL ASSET</Text>
          </View>

          <View style={s.footer}>
            <Text style={s.footerTxt}>
              v93 · db_writes=0 · cosmetic_unlock=false · inventory_grant=false ·
              final_asset_import=false · production_exposure=false
            </Text>
          </View>
        </ScrollView>
      </LinearGradient>
    </SafeAreaView>
  );
}

const s = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#1A0F30' },
  bg: { flex: 1 },
  scroll: { padding: 16, paddingBottom: 48 },
  backBtn: { alignSelf: 'flex-start', paddingVertical: 6, paddingHorizontal: 12, marginBottom: 8 },
  backTxt: { color: '#AA88FF', fontSize: 14 },
  title: { color: '#FFAA22', fontSize: 22, fontWeight: '800', textAlign: 'center' },
  subtitle: { color: '#AABBDD', fontSize: 11, textAlign: 'center', marginTop: 4, marginBottom: 12 },
  banner: { backgroundColor: 'rgba(60,30,0,0.5)', borderColor: '#FFAA22', borderWidth: 1, borderRadius: 8, padding: 10, marginBottom: 12 },
  bannerTxt: { color: '#FFDDAA', fontSize: 11, lineHeight: 16 },
  section: { color: '#FFD700', fontSize: 14, fontWeight: '700', marginTop: 12, marginBottom: 8 },
  lanesRow: { flexDirection: 'row', justifyContent: 'space-around', marginBottom: 12 },
  lane: { alignItems: 'center' },
  laneLabel: { color: '#FFFFFF', fontSize: 11, fontWeight: '600', marginBottom: 4 },
  laneSub: { color: '#AABBDD', fontSize: 9, marginTop: 4 },
  selectionRow: { flexDirection: 'row', justifyContent: 'space-around', marginBottom: 12 },
  selectionCell: { alignItems: 'center' },
  flagsBox: { flexDirection: 'row', flexWrap: 'wrap', gap: 4, marginBottom: 12 },
  flagsTxt: { color: '#FFFFFF', backgroundColor: '#774444', paddingHorizontal: 4, paddingVertical: 2, borderRadius: 3, fontSize: 9, fontWeight: '700' },
  footer: { padding: 8, backgroundColor: 'rgba(0,0,0,0.3)', borderRadius: 6 },
  footerTxt: { color: '#88AAAA', fontSize: 9, textAlign: 'center' },
});
