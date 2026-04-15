import React from 'react';
import { View, StyleSheet } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

interface StarDisplayProps {
  stars: number;
  size?: number;
}

/**
 * StarDisplay - Componente riutilizzabile per visualizzare stelle eroe.
 *
 * Logica ascensione (max 6 slot):
 *   redStars   = Math.floor(stars / 2)
 *   yellowStars = stars - (redStars * 2)
 *   emptySlots  = 6 - redStars - yellowStars
 *
 * Stelle gialle: oro con glow morbido
 * Stelle rosse:  gradient rosso con effetto gemma embossed
 */
export default function StarDisplay({ stars, size = 14 }: StarDisplayProps) {
  if (stars <= 0) return null;

  const capped = Math.min(stars, 12);
  const redCount = Math.floor(capped / 2);
  const yellowCount = capped - redCount * 2;
  const emptyCount = Math.max(0, 6 - redCount - yellowCount);

  const half = size / 2;
  const spike = size * 0.42;
  const inner = size * 0.18;
  const gap = Math.round(size * 0.2);

  return (
    <View style={[styles.row, { gap }]}>
      {/* Red stars first */}
      {Array.from({ length: redCount }).map((_, i) => (
        <View key={`r${i}`} style={[styles.starWrap, { width: size, height: size }]}>
          {/* Outer red glow */}
          <View style={[styles.redGlow, { width: size + 4, height: size + 4, borderRadius: (size + 4) / 2 }]} />
          {/* Red star body */}
          <View style={[styles.starBody, { width: size, height: size }]}>
            <LinearGradient
              colors={['#FF1744', '#D50000', '#B71C1C']}
              start={{ x: 0.2, y: 0 }}
              end={{ x: 0.8, y: 1 }}
              style={[styles.starGradient, { width: size, height: size, borderRadius: size * 0.15 }]}
            >
              {/* Inner star shape via layered Views */}
              <StarShape size={size} spike={spike} inner={inner} half={half} type="red" />
            </LinearGradient>
          </View>
          {/* Top highlight (emboss) */}
          <View style={[styles.redHighlight, { width: size * 0.35, height: size * 0.2, top: size * 0.08, borderRadius: size * 0.2 }]} />
        </View>
      ))}

      {/* Yellow stars */}
      {Array.from({ length: yellowCount }).map((_, i) => (
        <View key={`y${i}`} style={[styles.starWrap, { width: size, height: size }]}>
          <View style={[styles.yellowGlow, { width: size + 2, height: size + 2, borderRadius: (size + 2) / 2 }]} />
          <View style={[styles.starBody, { width: size, height: size }]}>
            <StarShape size={size} spike={spike} inner={inner} half={half} type="yellow" />
          </View>
        </View>
      ))}

      {/* Empty slots */}
      {Array.from({ length: emptyCount }).map((_, i) => (
        <View key={`e${i}`} style={[styles.starWrap, { width: size, height: size }]}>
          <View style={[styles.starBody, { width: size, height: size }]}>
            <StarShape size={size} spike={spike} inner={inner} half={half} type="empty" />
          </View>
        </View>
      ))}
    </View>
  );
}

/**
 * StarShape - Stella a 5 punte costruita con View rotate.
 * Usa 3 layer ruotati per creare la forma stella.
 */
function StarShape({ size, spike, inner, half, type }: {
  size: number; spike: number; inner: number; half: number;
  type: 'red' | 'yellow' | 'empty';
}) {
  const colors = {
    red: {
      arm: ['#FF1744', '#D50000'] as [string, string],
      center: '#FF5252',
      border: '#FF8A80',
    },
    yellow: {
      arm: ['#F59E0B', '#D97706'] as [string, string],
      center: '#FBBF24',
      border: '#FDE68A',
    },
    empty: {
      arm: ['rgba(255,255,255,0.06)', 'rgba(255,255,255,0.03)'] as [string, string],
      center: 'rgba(255,255,255,0.04)',
      border: 'rgba(255,255,255,0.08)',
    },
  };
  const c = colors[type];

  const armW = size * 0.32;
  const armH = size * 0.85;
  const armR = armW * 0.25;

  return (
    <View style={{ width: size, height: size, alignItems: 'center', justifyContent: 'center' }}>
      {/* 3 rotated arms to form star */}
      {[0, 60, -60].map((deg, i) => (
        <LinearGradient
          key={i}
          colors={c.arm}
          start={{ x: 0.5, y: 0 }}
          end={{ x: 0.5, y: 1 }}
          style={{
            position: 'absolute',
            width: armW,
            height: armH,
            borderRadius: armR,
            transform: [{ rotate: `${deg}deg` }],
            borderWidth: type !== 'empty' ? 0.5 : 0.5,
            borderColor: c.border,
          }}
        />
      ))}
      {/* Center gem dot */}
      {type !== 'empty' && (
        <View style={{
          position: 'absolute',
          width: size * 0.3,
          height: size * 0.3,
          borderRadius: size * 0.15,
          backgroundColor: c.center,
          borderWidth: 0.5,
          borderColor: c.border,
        }}>
          {/* Inner shine */}
          <View style={{
            position: 'absolute',
            top: size * 0.03,
            left: size * 0.04,
            width: size * 0.12,
            height: size * 0.08,
            borderRadius: size * 0.06,
            backgroundColor: type === 'red' ? 'rgba(255,255,255,0.45)' : 'rgba(255,255,255,0.5)',
          }} />
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  starWrap: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  starBody: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  starGradient: {
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden',
  },
  // Red star effects
  redGlow: {
    position: 'absolute',
    backgroundColor: 'rgba(255,23,68,0.25)',
  },
  redHighlight: {
    position: 'absolute',
    alignSelf: 'center',
    backgroundColor: 'rgba(255,255,255,0.3)',
  },
  // Yellow star effects
  yellowGlow: {
    position: 'absolute',
    backgroundColor: 'rgba(245,158,11,0.2)',
  },
});
