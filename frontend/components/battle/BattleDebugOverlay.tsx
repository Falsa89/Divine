/**
 * BattleDebugOverlay
 * ==================
 * Overlay visuale di debug per il battle positioning system.
 *
 * Questa versione è montata come ULTIMO figlio del <View style={st.battlefield}>
 * dentro combat.tsx, quindi lavora nello STESSO sistema di coordinate degli
 * sprite (left = home.x - slotW/2, bottom = home.y) — niente conversioni
 * top/bottom extra.
 *
 * Si attiva via la costante BATTLE_DEBUG in combat.tsx.
 *
 * Cosa mostra:
 *   • Banner rosso molto evidente "BATTLE_DEBUG ON" in alto (marker di versione
 *     del bundle: se NON lo vedi su Expo Go il bundle è cached stantio → Reload).
 *   • Rect info: dimensione reale del battlefield (onLayout) + sizes + #units.
 *   • Outline arancione del battlefield.
 *   • Griglia 3x3 di Team A (ciano) e Team B (magenta) con i bounding box logici.
 *   • Bounding box reale del wrapper assoluto per ogni unità.
 *   • Cross-hair + dot sull'anchor point (piede) di ogni unità.
 *   • Label con team/col/row/zIndex, nome, state, facing, size.
 */
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { BattleLayout, getHomePosition, Team } from './motionSystem';

export interface DebugUnitInfo {
  team: Team;
  col: number;
  row: number;
  id: string;
  name?: string;
  state?: string;
  facing?: 'left' | 'right';
  size: number;
  zIndex: number;
}

interface Props {
  enabled: boolean;
  /** Rect del battlefield misurato via onLayout (w/h). */
  bfRect: { w: number; h: number; x?: number; y?: number } | null;
  layout: BattleLayout;
  units: DebugUnitInfo[];
}

const C = {
  A: '#00E5FF',         // ciano per Team A (player)
  B: '#FF3FB5',         // magenta per Team B (enemy)
  rect: '#FFB347',      // arancione per il battlefield outline
  banner: '#FF0055',    // banner rosso "DEBUG ON"
  grid: 'rgba(255,255,255,0.22)',
};

export default function BattleDebugOverlay({ enabled, bfRect, layout, units }: Props) {
  if (!enabled) return null;

  // Banner SEMPRE visibile (anche prima del layout) — se non lo vedi, il bundle
  // è stantio. Viene reso come primissimo child, con zIndex alto e pointerEvents=none.
  const banner = (
    <View pointerEvents="none" style={s.bannerWrap}>
      <View style={s.banner}>
        <Text style={s.bannerText}>🐞 BATTLE_DEBUG ON · v2</Text>
      </View>
    </View>
  );

  // Rect non ancora noto → mostra solo il banner + info "waiting"
  if (!bfRect) {
    return (
      <View pointerEvents="none" style={StyleSheet.absoluteFillObject}>
        {banner}
        <View style={s.rectInfo}>
          <Text style={s.rectTitle}>BATTLE DEBUG</Text>
          <Text style={s.rectLine}>bf: waiting onLayout…</Text>
          <Text style={s.rectLine}>units: {units.length}</Text>
        </View>
      </View>
    );
  }

  const L = layout;

  // Linee della griglia 3x3 per ogni team (bounding box logico di ogni cella).
  // IMPORTANTE: le dimensioni slotW/slotH qui DEVONO combaciare esattamente col
  // wrapper assoluto in combat.tsx (width: size, height: size * 1.25).
  // Se divergono, il debug overlay mente — le box dell'overlay non coincidono
  // più con le celle reali rese sul schermo.
  const drawGridLines = (team: Team) => {
    const color = team === 'A' ? C.A : C.B;
    const lines: React.ReactNode[] = [];
    for (let col = 0; col < 3; col++) {
      for (let row = 0; row < 3; row++) {
        const home = getHomePosition(team, col, row, L);
        const sizeA = [L.supSize, L.dpsSize, L.tankSize];
        const sizeB = [L.tankSize, L.dpsSize, L.supSize];
        const size = team === 'A' ? sizeA[col] : sizeB[col];
        const slotW = size;
        const slotH = Math.round(size * 1.25);
        lines.push(
          <View
            key={`dbg_cell_${team}_${col}_${row}`}
            pointerEvents="none"
            style={{
              position: 'absolute',
              left: home.x - slotW / 2,
              bottom: home.y,
              width: slotW,
              height: slotH,
              borderWidth: 1,
              borderColor: color + '55',
              borderStyle: 'dashed',
            }}
          />
        );
      }
    }
    return lines;
  };

  // Anchor + bounding box + label per OGNI unità concreta
  const drawUnits = () =>
    units.map(u => {
      const home = getHomePosition(u.team, u.col, u.row, L);
      const color = u.team === 'A' ? C.A : C.B;
      const slotW = u.size;
      const slotH = Math.round(u.size * 1.25);
      return (
        <React.Fragment key={`dbg_u_${u.team}_${u.id}`}>
          {/* Bounding box reale del wrapper assoluto */}
          <View
            pointerEvents="none"
            style={{
              position: 'absolute',
              left: home.x - slotW / 2,
              bottom: home.y,
              width: slotW,
              height: slotH,
              borderWidth: 2,
              borderColor: color,
            }}
          />
          {/* Cross-hair sull'anchor point (piede dello sprite, bottom center) */}
          <View
            pointerEvents="none"
            style={{
              position: 'absolute',
              left: home.x - 7,
              bottom: home.y - 7,
              width: 14,
              height: 14,
            }}
          >
            <View style={[s.crossH, { backgroundColor: color }]} />
            <View style={[s.crossV, { backgroundColor: color }]} />
            <View style={[s.dot, { backgroundColor: color }]} />
          </View>
          {/* Label info sopra il bounding box */}
          <View
            pointerEvents="none"
            style={{
              position: 'absolute',
              left: home.x - slotW / 2,
              bottom: home.y + slotH + 2,
              maxWidth: slotW + 24,
              backgroundColor: 'rgba(0,0,0,0.8)',
              paddingHorizontal: 3,
              paddingVertical: 1,
              borderRadius: 3,
            }}
          >
            <Text style={[s.lbl, { color }]} numberOfLines={1}>
              {u.team}·c{u.col}r{u.row} z{u.zIndex}
            </Text>
            <Text style={[s.lblSmall, { color: '#FFF' }]} numberOfLines={1}>
              {(u.name || u.id).slice(0, 10)} · {u.state || 'idle'}
            </Text>
            <Text style={[s.lblSmall, { color: '#AAA' }]} numberOfLines={1}>
              {u.facing || '—'} · s{u.size}
            </Text>
          </View>
        </React.Fragment>
      );
    });

  return (
    <View pointerEvents="none" style={StyleSheet.absoluteFillObject}>
      {banner}

      {/* Rect info block — top-left (si vede subito su mobile) */}
      <View style={s.rectInfo}>
        <Text style={s.rectTitle}>BATTLE DEBUG</Text>
        <Text style={s.rectLine}>
          bf: {Math.round(bfRect.w)}×{Math.round(bfRect.h)}
        </Text>
        <Text style={s.rectLine}>
          tank:{L.tankSize} dps:{L.dpsSize} sup:{L.supSize} rs:{L.rowStep}
        </Text>
        <Text style={s.rectLine}>units: {units.length}</Text>
      </View>

      {/* Outline arancione che coincide col battlefield (il parent) */}
      <View
        pointerEvents="none"
        style={{
          position: 'absolute',
          left: 0,
          top: 0,
          right: 0,
          bottom: 0,
          borderWidth: 2,
          borderColor: C.rect,
        }}
      />

      {drawGridLines('A')}
      {drawGridLines('B')}
      {drawUnits()}
    </View>
  );
}

const s = StyleSheet.create({
  bannerWrap: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    alignItems: 'center',
    zIndex: 99999,
  },
  banner: {
    backgroundColor: C.banner,
    paddingHorizontal: 12,
    paddingVertical: 3,
    borderBottomLeftRadius: 8,
    borderBottomRightRadius: 8,
    borderWidth: 1.5,
    borderColor: '#FFF',
    shadowColor: '#000',
    shadowOpacity: 0.5,
    shadowRadius: 4,
    shadowOffset: { width: 0, height: 2 },
    elevation: 6,
  },
  bannerText: {
    color: '#FFF',
    fontSize: 11,
    fontWeight: '900',
    letterSpacing: 1.5,
  },
  rectInfo: {
    position: 'absolute',
    top: 26,
    left: 6,
    backgroundColor: 'rgba(0,0,0,0.82)',
    paddingHorizontal: 6,
    paddingVertical: 3,
    borderRadius: 4,
    borderWidth: 1,
    borderColor: C.rect,
    zIndex: 9999,
  },
  rectTitle: {
    color: C.rect,
    fontSize: 10,
    fontWeight: '800',
    letterSpacing: 1,
  },
  rectLine: {
    color: '#FFF',
    fontSize: 9,
    fontFamily: 'monospace',
  },
  lbl: {
    fontSize: 8,
    fontWeight: '700',
    fontFamily: 'monospace',
  },
  lblSmall: {
    fontSize: 8,
    fontFamily: 'monospace',
  },
  crossH: {
    position: 'absolute',
    top: 6,
    left: 0,
    width: 14,
    height: 2,
  },
  crossV: {
    position: 'absolute',
    left: 6,
    top: 0,
    width: 2,
    height: 14,
  },
  dot: {
    position: 'absolute',
    left: 5,
    top: 5,
    width: 4,
    height: 4,
    borderRadius: 2,
  },
});
