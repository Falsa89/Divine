/**
 * BattleLoadingScreen
 * ====================
 * Schermata di preload pre-battle con progress bar reale.
 *
 * Riceve:
 *  - `progress`  (0..1): frazione di asset caricati
 *  - `loaded`    (number): asset caricati finora
 *  - `total`     (number): totale asset da caricare
 *  - `label`     (string, opz): ultimo asset caricato / messaggio corrente
 *
 * Design:
 *  - Sfondo gradient coerente con il tema dark del gioco
 *  - Icona centrale con pulse animato
 *  - Titolo "Caricamento Battaglia"
 *  - Sottotitolo con contatore "N / M asset"
 *  - Progress bar orizzontale con fill animato (Reanimated)
 *  - Percentuale grande al centro
 *
 * Il componente è PURO: non esegue nessun preload, riceve solo i valori.
 * Il parent (combat.tsx) orchestra il vero caricamento asset.
 */
import React, { useEffect } from 'react';
import { View, Text, StyleSheet, Dimensions } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import Animated, {
  useSharedValue, useAnimatedStyle, withTiming, withRepeat,
  withSequence, Easing, ZoomIn,
} from 'react-native-reanimated';
import { COLORS } from '../../constants/theme';

const { width: SW } = Dimensions.get('window');

type Props = {
  progress: number;   // 0..1
  loaded: number;
  total: number;
  label?: string;
};

export default function BattleLoadingScreen({ progress, loaded, total, label }: Props) {
  // Animated progress bar fill — si muove smoothly quando `progress` cambia
  const fill = useSharedValue(0);
  useEffect(() => {
    fill.value = withTiming(Math.max(0, Math.min(1, progress)), {
      duration: 220,
      easing: Easing.out(Easing.quad),
    });
  }, [progress]);

  // Icon pulse loop durante il caricamento
  const iconScale = useSharedValue(1);
  useEffect(() => {
    iconScale.value = withRepeat(
      withSequence(
        withTiming(1.15, { duration: 700, easing: Easing.inOut(Easing.quad) }),
        withTiming(1.0, { duration: 700, easing: Easing.inOut(Easing.quad) }),
      ),
      -1,
      false,
    );
  }, []);

  const iconStyle = useAnimatedStyle(() => ({
    transform: [{ scale: iconScale.value }],
  }));

  const fillStyle = useAnimatedStyle(() => ({
    width: `${Math.round(fill.value * 100)}%`,
  }));

  const percentText = Math.round(Math.max(0, Math.min(1, progress)) * 100);
  const barW = Math.min(SW * 0.72, 420);

  return (
    <LinearGradient
      colors={[COLORS.bgPrimary, '#1A0A2E', COLORS.bgPrimary]}
      style={styles.container}
    >
      {/* ───── Icona centrale con pulse ───── */}
      <Animated.View entering={ZoomIn.duration(320)} style={[styles.iconWrap, iconStyle]}>
        <Text style={styles.icon}>⚔️</Text>
      </Animated.View>

      {/* ───── Titolo ───── */}
      <Text style={styles.title}>Caricamento Battaglia</Text>
      <Text style={styles.subtitle}>
        {total > 0 ? `${loaded} / ${total} asset` : 'Preparazione…'}
      </Text>

      {/* ───── Progress bar ───── */}
      <View style={[styles.barTrack, { width: barW }]}>
        <Animated.View style={[styles.barFill, fillStyle]}>
          <LinearGradient
            colors={['#FFD700', '#FF9800', '#FF4444']}
            start={{ x: 0, y: 0.5 }}
            end={{ x: 1, y: 0.5 }}
            style={StyleSheet.absoluteFill}
          />
        </Animated.View>

        {/* glow border */}
        <View pointerEvents="none" style={[StyleSheet.absoluteFill, styles.barGlow]} />
      </View>

      {/* ───── Percentuale ───── */}
      <Text style={styles.percent}>{percentText}%</Text>

      {/* ───── Label corrente (asset/step) ───── */}
      {!!label && (
        <Text style={styles.label} numberOfLines={1} ellipsizeMode="middle">
          {label}
        </Text>
      )}
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 24,
  },
  iconWrap: {
    marginBottom: 20,
  },
  icon: {
    fontSize: 56,
    textAlign: 'center',
  },
  title: {
    color: '#FFFFFF',
    fontSize: 20,
    fontWeight: '800',
    letterSpacing: 1.2,
    marginBottom: 6,
  },
  subtitle: {
    color: '#B8A8D0',
    fontSize: 13,
    fontWeight: '600',
    letterSpacing: 0.5,
    marginBottom: 22,
  },
  barTrack: {
    height: 14,
    backgroundColor: 'rgba(255,255,255,0.08)',
    borderRadius: 7,
    borderWidth: 1,
    borderColor: 'rgba(255,215,0,0.35)',
    overflow: 'hidden',
    position: 'relative',
  },
  barFill: {
    height: '100%',
    borderRadius: 6,
    overflow: 'hidden',
  },
  barGlow: {
    borderRadius: 7,
    borderWidth: 1,
    borderColor: 'rgba(255,215,0,0.18)',
  },
  percent: {
    color: '#FFD700',
    fontSize: 28,
    fontWeight: '900',
    letterSpacing: 2,
    marginTop: 16,
    textShadowColor: 'rgba(255,150,0,0.4)',
    textShadowRadius: 8,
  },
  label: {
    marginTop: 10,
    color: '#6A5A8A',
    fontSize: 11,
    fontFamily: 'monospace',
    maxWidth: '90%',
    textAlign: 'center',
  },
});
