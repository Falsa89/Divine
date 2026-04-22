/**
 * AvatarFrameSelector — Modal placeholder per futura selezione avatar / cornice.
 *
 * Scope di questo stub (Pack A test-base):
 *  - struttura tecnica minima (tabs Avatar | Frames)
 *  - interazione base (apri/chiudi)
 *  - nessun sistema di collezione vero (verrà nelle prossime iterations)
 *
 * Può essere esteso in futuro con:
 *  - lista avatar (per rarità / fazione / hero-specific)
 *  - lista frames (standard / premium / faction / hero-bundle)
 *  - preview live del panel composito
 *  - API backend per save selection
 */
import React, { useState } from 'react';
import {
  View, Text, Modal, TouchableOpacity, StyleSheet,
  ScrollView, useWindowDimensions,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

type Tab = 'avatar' | 'frame';

export type AvatarFrameSelectorProps = {
  visible: boolean;
  onClose: () => void;
  /** Tab iniziale (default: 'avatar') */
  initialTab?: Tab;
};

const GOLD = '#F1C76A';
const GOLD_PALE = '#F7D98A';
const NIGHT_0 = '#070B1B';
const NIGHT_1 = '#0D1530';

export function AvatarFrameSelector({
  visible, onClose, initialTab = 'avatar',
}: AvatarFrameSelectorProps) {
  const [tab, setTab] = useState<Tab>(initialTab);
  const { width: vw, height: vh } = useWindowDimensions();

  // Responsive dialog size
  const dialogW = Math.min(vw * 0.82, 520);
  const dialogH = Math.min(vh * 0.80, 360);

  return (
    <Modal
      visible={visible}
      transparent
      animationType="fade"
      onRequestClose={onClose}
      statusBarTranslucent
    >
      <TouchableOpacity
        style={s.backdrop}
        activeOpacity={1}
        onPress={onClose}
      >
        <TouchableOpacity
          activeOpacity={1}
          onPress={(e) => e.stopPropagation()}
          style={[s.dialog, { width: dialogW, height: dialogH }]}
        >
          <LinearGradient
            colors={['rgba(16,28,72,0.98)', 'rgba(8,15,40,0.98)']}
            style={s.dialogBg}
          >
            {/* Header */}
            <View style={s.header}>
              <Text style={s.title}>Personalizza profilo</Text>
              <TouchableOpacity onPress={onClose} hitSlop={{ top: 8, left: 8, right: 8, bottom: 8 }}>
                <Text style={s.closeBtn}>✕</Text>
              </TouchableOpacity>
            </View>

            {/* Tabs */}
            <View style={s.tabs}>
              {(['avatar', 'frame'] as Tab[]).map(t => (
                <TouchableOpacity
                  key={t}
                  onPress={() => setTab(t)}
                  style={[s.tab, tab === t && s.tabActive]}
                  activeOpacity={0.8}
                >
                  <Text style={[s.tabTxt, tab === t && s.tabTxtActive]}>
                    {t === 'avatar' ? 'Avatar' : 'Cornici'}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>

            {/* Content */}
            <ScrollView style={s.content} contentContainerStyle={s.contentInner}>
              {tab === 'avatar' ? (
                <View style={s.placeholderBox}>
                  <Text style={s.placeholderTitle}>Galleria Avatar</Text>
                  <Text style={s.placeholderSub}>
                    Qui comparirà la collezione di ritratti sbloccati{'\n'}
                    (standard · fazione · hero-specific · premium).
                  </Text>
                  <View style={s.grid}>
                    {[1,2,3,4,5,6].map(i => (
                      <View key={i} style={s.avatarSlot}>
                        <Text style={s.slotInitial}>{String.fromCharCode(64 + i)}</Text>
                        {i > 2 ? <View style={s.lockOverlay}><Text style={s.lockTxt}>🔒</Text></View> : null}
                      </View>
                    ))}
                  </View>
                </View>
              ) : (
                <View style={s.placeholderBox}>
                  <Text style={s.placeholderTitle}>Galleria Cornici</Text>
                  <Text style={s.placeholderSub}>
                    Qui comparirà la collezione di frames sbloccati{'\n'}
                    (standard · premium · fazione · achievement · hero-bundle).
                  </Text>
                  <View style={s.grid}>
                    {[1,2,3,4,5,6].map(i => (
                      <View key={i} style={s.frameSlot}>
                        <Text style={s.slotInitial}>F{i}</Text>
                        {i > 2 ? <View style={s.lockOverlay}><Text style={s.lockTxt}>🔒</Text></View> : null}
                      </View>
                    ))}
                  </View>
                </View>
              )}
            </ScrollView>

            <View style={s.footer}>
              <Text style={s.footerHint}>Sistema di collezione in arrivo</Text>
            </View>
          </LinearGradient>
        </TouchableOpacity>
      </TouchableOpacity>
    </Modal>
  );
}

const s = StyleSheet.create({
  backdrop: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.65)',
    alignItems: 'center', justifyContent: 'center',
    paddingHorizontal: 16,
  },
  dialog: {
    borderRadius: 14,
    overflow: 'hidden',
    borderWidth: 1.5, borderColor: GOLD,
    shadowColor: '#000', shadowOpacity: 0.6, shadowRadius: 10,
    elevation: 14,
  },
  dialogBg: { flex: 1 },
  header: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    paddingHorizontal: 14, paddingVertical: 10,
    borderBottomWidth: 1, borderBottomColor: 'rgba(255,215,0,0.18)',
  },
  title: { color: GOLD, fontSize: 14, fontWeight: '900', letterSpacing: 0.6 },
  closeBtn: { color: GOLD_PALE, fontSize: 16, fontWeight: '900' },
  tabs: {
    flexDirection: 'row',
    paddingHorizontal: 10, paddingTop: 8, gap: 6,
  },
  tab: {
    paddingHorizontal: 12, paddingVertical: 6,
    borderRadius: 4,
    backgroundColor: 'rgba(255,215,0,0.08)',
    borderWidth: 1, borderColor: 'rgba(255,215,0,0.18)',
  },
  tabActive: {
    backgroundColor: 'rgba(255,215,0,0.22)',
    borderColor: GOLD,
  },
  tabTxt: { color: '#C8C8E0', fontSize: 11, fontWeight: '800', letterSpacing: 0.4 },
  tabTxtActive: { color: GOLD },
  content: { flex: 1, paddingHorizontal: 12, paddingTop: 10 },
  contentInner: { paddingBottom: 12 },
  placeholderBox: { gap: 8 },
  placeholderTitle: { color: GOLD_PALE, fontSize: 12, fontWeight: '900', letterSpacing: 0.5 },
  placeholderSub: { color: '#A8B0D0', fontSize: 10, lineHeight: 14 },
  grid: {
    flexDirection: 'row', flexWrap: 'wrap', gap: 8,
    marginTop: 6,
  },
  avatarSlot: {
    width: 54, height: 54, borderRadius: 27,
    backgroundColor: NIGHT_1,
    borderWidth: 2, borderColor: GOLD,
    alignItems: 'center', justifyContent: 'center',
    overflow: 'hidden',
  },
  frameSlot: {
    width: 54, height: 54, borderRadius: 4,
    backgroundColor: NIGHT_1,
    borderWidth: 2, borderColor: GOLD_PALE,
    alignItems: 'center', justifyContent: 'center',
  },
  slotInitial: { color: GOLD, fontSize: 14, fontWeight: '900' },
  lockOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0,0,0,0.6)',
    alignItems: 'center', justifyContent: 'center',
  },
  lockTxt: { fontSize: 14 },
  footer: {
    paddingHorizontal: 14, paddingVertical: 8,
    borderTopWidth: 1, borderTopColor: 'rgba(255,215,0,0.14)',
    alignItems: 'center',
  },
  footerHint: { color: '#8890B8', fontSize: 9, fontStyle: 'italic' },
});
