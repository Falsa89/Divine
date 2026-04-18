import React, { useState } from 'react';
import { View, Text, ScrollView, StyleSheet, Image, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { router } from 'expo-router';
import HeroHopliteIdle from '../components/ui/HeroHopliteIdle';

const LAYERS = [
  { key: 'hair', src: require('../assets/heroes/greek_hoplite/rig/hair.png') },
  { key: 'head_helmet', src: require('../assets/heroes/greek_hoplite/rig/head_helmet.png') },
  { key: 'torso', src: require('../assets/heroes/greek_hoplite/rig/torso.png') },
  { key: 'spear_arm', src: require('../assets/heroes/greek_hoplite/rig/spear_arm.png') },
  { key: 'shield_arm', src: require('../assets/heroes/greek_hoplite/rig/shield_arm.png') },
  { key: 'skirt', src: require('../assets/heroes/greek_hoplite/rig/skirt.png') },
  { key: 'legs', src: require('../assets/heroes/greek_hoplite/rig/legs.png') },
];

const COMBAT_BASE = require('../assets/heroes/greek_hoplite/combat_base.png');

export default function HopliteRigPreview() {
  const [animated, setAnimated] = useState(true);
  const [size, setSize] = useState(320);

  return (
    <SafeAreaView style={styles.root}>
      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
            <Text style={styles.backTxt}>{'<'} Back</Text>
          </TouchableOpacity>
          <Text style={styles.title}>Greek Hoplite — Rig Idle (layer separati)</Text>
        </View>

        {/* Hero row: original vs animated rig */}
        <View style={styles.heroRow}>
          <View style={styles.heroCard}>
            <Text style={styles.cardTitle}>combat_base.png</Text>
            <View style={styles.heroFrame}>
              <Image source={COMBAT_BASE} style={{ width: size, height: size }} resizeMode="contain" />
            </View>
          </View>
          <View style={styles.heroCard}>
            <Text style={styles.cardTitle}>
              Rig Idle {animated ? 'LIVE' : 'PAUSED'} · size {size}px
            </Text>
            <View style={styles.heroFrame}>
              <HeroHopliteIdle size={size} animated={animated} />
            </View>
          </View>
        </View>

        {/* Controls */}
        <View style={styles.controls}>
          <TouchableOpacity
            onPress={() => setAnimated(a => !a)}
            style={[styles.ctrlBtn, animated && styles.ctrlBtnOn]}
          >
            <Text style={styles.ctrlTxt}>{animated ? 'PAUSE' : 'PLAY'}</Text>
          </TouchableOpacity>
          {[128, 256, 320, 512].map(s => (
            <TouchableOpacity
              key={s}
              onPress={() => setSize(s)}
              style={[styles.ctrlBtn, size === s && styles.ctrlBtnOn]}
            >
              <Text style={styles.ctrlTxt}>{s}px</Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Layer grid */}
        <Text style={styles.section}>Layer PNG singoli (7 files)</Text>
        <View style={styles.grid}>
          {LAYERS.map(l => (
            <View key={l.key} style={styles.layerCard}>
              <Text style={styles.layerLabel}>{l.key}</Text>
              <View style={styles.layerFrame}>
                <Image source={l.src} style={styles.layerImg} resizeMode="contain" />
              </View>
            </View>
          ))}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: '#0c0f17' },
  content: { padding: 12, paddingBottom: 40 },
  header: { flexDirection: 'row', alignItems: 'center', marginBottom: 12, gap: 12 },
  backBtn: { paddingHorizontal: 10, paddingVertical: 6, backgroundColor: '#222838', borderRadius: 6 },
  backTxt: { color: '#cfd6e6', fontWeight: '600' },
  title: { color: '#e8ecf6', fontSize: 16, fontWeight: '700' },

  heroRow: { flexDirection: 'row', gap: 12 },
  heroCard: {
    flex: 1,
    backgroundColor: '#151a26',
    borderRadius: 10,
    padding: 10,
    borderWidth: 1,
    borderColor: '#232a3b',
  },
  cardTitle: { color: '#bac3d6', marginBottom: 8, fontSize: 12, fontWeight: '600' },
  heroFrame: {
    backgroundColor: '#0a0d14',
    borderRadius: 6,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 8,
    minHeight: 340,
  },

  controls: { flexDirection: 'row', gap: 8, marginTop: 12, flexWrap: 'wrap' },
  ctrlBtn: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
    backgroundColor: '#232a3b',
  },
  ctrlBtnOn: { backgroundColor: '#3b82f6' },
  ctrlTxt: { color: '#cfd6e6', fontWeight: '600', fontSize: 12 },

  section: { color: '#e8ecf6', fontSize: 14, fontWeight: '700', marginTop: 18, marginBottom: 8 },
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  layerCard: {
    backgroundColor: '#151a26',
    borderRadius: 8,
    padding: 6,
    borderWidth: 1,
    borderColor: '#232a3b',
    width: 180,
  },
  layerLabel: { color: '#8a95ad', fontSize: 11, marginBottom: 4, fontWeight: '600' },
  layerFrame: {
    backgroundColor: '#0a0d14',
    borderRadius: 4,
    padding: 4,
    alignItems: 'center',
    justifyContent: 'center',
  },
  layerImg: { width: 160, height: 160 },
});
