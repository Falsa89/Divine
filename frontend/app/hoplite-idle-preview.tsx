import React, { useEffect, useState } from 'react';
import { View, Text, Image, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { router } from 'expo-router';

const FRAMES = [
  require('../assets/heroes/greek_hoplite/idle/idle_01.png'),
  require('../assets/heroes/greek_hoplite/idle/idle_02.png'),
  require('../assets/heroes/greek_hoplite/idle/idle_03.png'),
  require('../assets/heroes/greek_hoplite/idle/idle_04.png'),
  require('../assets/heroes/greek_hoplite/idle/idle_05.png'),
  require('../assets/heroes/greek_hoplite/idle/idle_06.png'),
];

const BASE = require('../assets/heroes/greek_hoplite/base.png');

export default function HopliteIdlePreview() {
  const [frame, setFrame] = useState(0);
  const [fps, setFps] = useState(8);

  useEffect(() => {
    const id = setInterval(() => setFrame(f => (f + 1) % 6), 1000 / fps);
    return () => clearInterval(id);
  }, [fps]);

  return (
    <SafeAreaView style={styles.root}>
      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
            <Text style={styles.backTxt}>{'<'} Back</Text>
          </TouchableOpacity>
          <Text style={styles.title}>Greek Hoplite — Idle (mesh warping PIL)</Text>
        </View>

        <View style={styles.row}>
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Base (riferimento)</Text>
            <Image source={BASE} style={styles.bigImg} resizeMode="contain" />
          </View>
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Animazione live · frame {frame + 1}/6 · {fps} fps</Text>
            <Image source={FRAMES[frame]} style={styles.bigImg} resizeMode="contain" />
            <View style={styles.speedRow}>
              {[4, 6, 8, 12].map(v => (
                <TouchableOpacity key={v} onPress={() => setFps(v)} style={[styles.speedBtn, fps === v && styles.speedOn]}>
                  <Text style={[styles.speedTxt, fps === v && styles.speedOnTxt]}>{v} fps</Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        </View>

        <Text style={styles.section}>Tutti i 6 frame (ordine 01 → 06)</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.strip}>
          {FRAMES.map((src, i) => (
            <View key={i} style={styles.frameBox}>
              <Image source={src} style={styles.smallImg} resizeMode="contain" />
              <Text style={styles.frameLabel}>idle_{String(i + 1).padStart(2, '0')}</Text>
            </View>
          ))}
        </ScrollView>
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
  row: { flexDirection: 'row', gap: 12 },
  card: { flex: 1, backgroundColor: '#151a26', borderRadius: 10, padding: 10, borderWidth: 1, borderColor: '#232a3b' },
  cardTitle: { color: '#bac3d6', marginBottom: 6, fontSize: 12, fontWeight: '600' },
  bigImg: { width: '100%', height: 360, backgroundColor: '#0a0d14', borderRadius: 6 },
  speedRow: { flexDirection: 'row', gap: 6, marginTop: 8, flexWrap: 'wrap' },
  speedBtn: { paddingHorizontal: 10, paddingVertical: 5, borderRadius: 5, backgroundColor: '#232a3b' },
  speedOn: { backgroundColor: '#3b82f6' },
  speedTxt: { color: '#bac3d6', fontSize: 12 },
  speedOnTxt: { color: '#fff', fontWeight: '700' },
  section: { color: '#e8ecf6', fontSize: 14, fontWeight: '700', marginTop: 16, marginBottom: 8 },
  strip: { gap: 10, paddingBottom: 8 },
  frameBox: { backgroundColor: '#151a26', borderRadius: 8, padding: 6, alignItems: 'center', borderWidth: 1, borderColor: '#232a3b' },
  smallImg: { width: 150, height: 225, backgroundColor: '#0a0d14', borderRadius: 4 },
  frameLabel: { color: '#8a95ad', fontSize: 11, marginTop: 4 },
});
