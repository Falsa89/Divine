import React, { useState, useCallback } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import AnimatedSprite from '../components/ui/AnimatedSprite';

// Sprite sheets
const SHEETS = {
  idle: require('../assets/heroes/berserker_sprites/idle.png'),
  attack: require('../assets/heroes/berserker_sprites/attack.png'),
  skill: require('../assets/heroes/berserker_sprites/skill.png'),
  hit: require('../assets/heroes/berserker_sprites/hit.png'),
  death: require('../assets/heroes/berserker_sprites/death.png'),
};

// Metadata - real frame dimensions from actual sheet sizes (1536x1024)
const META: Record<string, { frameWidth: number; frameHeight: number; frames: number; fps: number; loop: boolean }> = {
  idle:   { frameWidth: 256, frameHeight: 1024, frames: 6,  fps: 12, loop: true },
  attack: { frameWidth: 192, frameHeight: 1024, frames: 8,  fps: 10, loop: false },
  skill:  { frameWidth: 153, frameHeight: 1024, frames: 10, fps: 10, loop: false },
  hit:    { frameWidth: 307, frameHeight: 1024, frames: 5,  fps: 10, loop: false },
  death:  { frameWidth: 153, frameHeight: 1024, frames: 10, fps: 8,  loop: false },
};

type AnimKey = keyof typeof SHEETS;

const BUTTONS: { key: AnimKey; label: string; color: string }[] = [
  { key: 'idle',   label: 'IDLE',   color: '#44AA88' },
  { key: 'attack', label: 'ATTACK', color: '#FF5544' },
  { key: 'skill',  label: 'SKILL',  color: '#FF8844' },
  { key: 'hit',    label: 'HIT',    color: '#FFAA22' },
  { key: 'death',  label: 'DEATH',  color: '#8844CC' },
];

export default function SpriteTestScreen() {
  const router = useRouter();
  const [anim, setAnim] = useState<AnimKey>('idle');
  // Key to force remount AnimatedSprite when switching
  const [spriteKey, setSpriteKey] = useState(0);

  const play = useCallback((key: AnimKey) => {
    setAnim(key);
    setSpriteKey(k => k + 1);
  }, []);

  const onAnimComplete = useCallback(() => {
    // Non-looping animation finished -> return to idle
    setAnim('idle');
    setSpriteKey(k => k + 1);
  }, []);

  const meta = META[anim];

  return (
    <LinearGradient colors={['#0A0A1A', '#12102A', '#0A0A1A']} style={s.root}>
      {/* Header */}
      <View style={s.header}>
        <TouchableOpacity onPress={() => router.back()} style={s.backBtn}>
          <Text style={s.backTxt}>←</Text>
        </TouchableOpacity>
        <Text style={s.title}>SPRITE TEST — BERSERKER</Text>
      </View>

      {/* Content */}
      <View style={s.body}>
        {/* Sprite display */}
        <View style={s.spriteArea}>
          <View style={s.spriteBox}>
            <AnimatedSprite
              key={spriteKey}
              source={SHEETS[anim]}
              frameWidth={meta.frameWidth}
              frameHeight={meta.frameHeight}
              frames={meta.frames}
              fps={meta.fps}
              loop={meta.loop}
              size={180}
              onComplete={meta.loop ? undefined : onAnimComplete}
            />
          </View>
          <View style={s.infoRow}>
            <Text style={s.infoLabel}>Animazione:</Text>
            <Text style={[s.infoVal, { color: BUTTONS.find(b => b.key === anim)?.color || '#fff' }]}>{anim.toUpperCase()}</Text>
            <Text style={s.infoDivider}>|</Text>
            <Text style={s.infoLabel}>Frame:</Text>
            <Text style={s.infoVal}>{meta.frames}</Text>
            <Text style={s.infoDivider}>|</Text>
            <Text style={s.infoLabel}>FPS:</Text>
            <Text style={s.infoVal}>{meta.fps}</Text>
            <Text style={s.infoDivider}>|</Text>
            <Text style={s.infoLabel}>Loop:</Text>
            <Text style={s.infoVal}>{meta.loop ? 'Si' : 'No'}</Text>
          </View>
        </View>

        {/* Controls */}
        <View style={s.controls}>
          <Text style={s.controlsTitle}>ANIMAZIONI</Text>
          {BUTTONS.map(b => {
            const isActive = anim === b.key;
            return (
              <TouchableOpacity
                key={b.key}
                style={[s.btn, isActive && { backgroundColor: b.color + '20', borderColor: b.color }]}
                onPress={() => play(b.key)}
                activeOpacity={0.7}
              >
                <View style={[s.btnDot, { backgroundColor: b.color }]} />
                <Text style={[s.btnTxt, isActive && { color: b.color }]}>{b.label}</Text>
                <Text style={s.btnMeta}>{META[b.key].frames}f {META[b.key].fps}fps</Text>
              </TouchableOpacity>
            );
          })}
        </View>
      </View>
    </LinearGradient>
  );
}

const s = StyleSheet.create({
  root: { flex: 1 },
  header: {
    flexDirection: 'row', alignItems: 'center', paddingHorizontal: 12, paddingVertical: 6,
    borderBottomWidth: 1, borderBottomColor: 'rgba(255,107,53,0.15)',
    backgroundColor: 'rgba(7,7,26,0.95)',
  },
  backBtn: { paddingRight: 10 },
  backTxt: { color: '#fff', fontSize: 18, fontWeight: '700' },
  title: { color: '#FF6B35', fontSize: 13, fontWeight: '900', letterSpacing: 1.5 },
  body: { flex: 1, flexDirection: 'row', padding: 12, gap: 12 },
  // Sprite area
  spriteArea: { flex: 1, alignItems: 'center', justifyContent: 'center', gap: 12 },
  spriteBox: {
    width: 220, height: 220, alignItems: 'center', justifyContent: 'center',
    backgroundColor: 'rgba(255,255,255,0.02)', borderRadius: 12,
    borderWidth: 1, borderColor: 'rgba(255,255,255,0.06)',
  },
  infoRow: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  infoLabel: { color: 'rgba(255,255,255,0.35)', fontSize: 9, fontWeight: '600' },
  infoVal: { color: '#fff', fontSize: 10, fontWeight: '800' },
  infoDivider: { color: 'rgba(255,255,255,0.1)', fontSize: 10 },
  // Controls
  controls: { width: 140, gap: 6 },
  controlsTitle: { color: 'rgba(255,255,255,0.3)', fontSize: 8, fontWeight: '800', letterSpacing: 1, marginBottom: 4 },
  btn: {
    flexDirection: 'row', alignItems: 'center', gap: 6,
    paddingHorizontal: 10, paddingVertical: 8, borderRadius: 8,
    borderWidth: 1, borderColor: 'rgba(255,255,255,0.08)',
    backgroundColor: 'rgba(255,255,255,0.02)',
  },
  btnDot: { width: 6, height: 6, borderRadius: 3 },
  btnTxt: { color: 'rgba(255,255,255,0.6)', fontSize: 11, fontWeight: '800', flex: 1 },
  btnMeta: { color: 'rgba(255,255,255,0.2)', fontSize: 8, fontWeight: '600' },
});
