/**
 * v93 — Event Avatar Layout Preview (DEV PLACEHOLDER).
 * Layout-only test screen per posizionamento event avatar.
 * NO cosmetic unlock, NO inventory, NO monetization, NO DB writes.
 */
import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, SafeAreaView } from 'react-native';
import { useRouter } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { AvatarPlaceholderEvent } from '../components/avatarPlaceholders/AvatarPlaceholderDev';

const EVENT_SLOTS = [
  { id: 'slot_a', label: 'Slot A' },
  { id: 'slot_b', label: 'Slot B' },
  { id: 'slot_c', label: 'Slot C' },
];

export default function EventAvatarLayoutPreview() {
  const router = useRouter();
  const goBack = () => {
    if (router.canGoBack()) router.back();
    else router.push('/live-guild-qa-hub' as any);
  };

  return (
    <SafeAreaView style={s.safe}>
      <LinearGradient colors={['#0F2A1A', '#1F4A3A']} style={s.bg}>
        <ScrollView contentContainerStyle={s.scroll}>
          <TouchableOpacity onPress={goBack} style={s.backBtn}>
            <Text style={s.backTxt}>← Indietro</Text>
          </TouchableOpacity>
          <Text style={s.title}>Event Avatar Layout Preview</Text>
          <Text style={s.subtitle}>v93 · DEV PLACEHOLDER · NO COSMETIC UNLOCK · NO INVENTORY</Text>

          <View style={s.banner}>
            <Text style={s.bannerTxt}>
              QA layout preview con event avatar DEV. Asset placeholder, NON canonical.
              Nessuna mutazione di cosmetici/inventario/account.
            </Text>
          </View>

          <Text style={s.section}>Event stage layout (mock)</Text>
          <View style={s.stageBox}>
            <View style={s.stageInner}>
              {EVENT_SLOTS.map((slot, i) => (
                <View key={slot.id} style={s.stageSlot}>
                  <AvatarPlaceholderEvent size={72} label={slot.label} />
                </View>
              ))}
            </View>
          </View>

          <Text style={s.section}>Movement mock</Text>
          <View style={s.movementRow}>
            <AvatarPlaceholderEvent size={48} label="START" />
            <Text style={s.arrow}>→</Text>
            <AvatarPlaceholderEvent size={48} label="MID" />
            <Text style={s.arrow}>→</Text>
            <AvatarPlaceholderEvent size={48} label="END" />
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
  safe: { flex: 1, backgroundColor: '#0F2A1A' },
  bg: { flex: 1 },
  scroll: { padding: 16, paddingBottom: 48 },
  backBtn: { alignSelf: 'flex-start', paddingVertical: 6, paddingHorizontal: 12, marginBottom: 8 },
  backTxt: { color: '#88FFCC', fontSize: 14 },
  title: { color: '#22DDAA', fontSize: 22, fontWeight: '800', textAlign: 'center' },
  subtitle: { color: '#AABBDD', fontSize: 11, textAlign: 'center', marginTop: 4, marginBottom: 12 },
  banner: { backgroundColor: 'rgba(0,40,30,0.6)', borderColor: '#22DDAA', borderWidth: 1, borderRadius: 8, padding: 10, marginBottom: 12 },
  bannerTxt: { color: '#AAFFDD', fontSize: 11, lineHeight: 16 },
  section: { color: '#FFD700', fontSize: 14, fontWeight: '700', marginTop: 12, marginBottom: 8 },
  stageBox: { backgroundColor: 'rgba(0,40,30,0.4)', borderRadius: 8, padding: 12, marginBottom: 12 },
  stageInner: { flexDirection: 'row', justifyContent: 'space-around' },
  stageSlot: { alignItems: 'center' },
  movementRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-around', marginBottom: 12 },
  arrow: { color: '#22DDAA', fontSize: 24, fontWeight: '800' },
  flagsBox: { flexDirection: 'row', flexWrap: 'wrap', gap: 4, marginBottom: 12 },
  flagsTxt: { color: '#FFFFFF', backgroundColor: '#774444', paddingHorizontal: 4, paddingVertical: 2, borderRadius: 3, fontSize: 9, fontWeight: '700' },
  footer: { padding: 8, backgroundColor: 'rgba(0,0,0,0.3)', borderRadius: 6 },
  footerTxt: { color: '#88AAAA', fontSize: 9, textAlign: 'center' },
});
