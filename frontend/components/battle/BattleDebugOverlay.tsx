/**
 * BattleDebugOverlay
 * ==================
 * Overlay visuale di debug per il battle positioning system. Si attiva
 * tramite la costante BATTLE_DEBUG in combat.tsx. Nativo + web: funziona
 * su Expo Go senza dipendere dal DOM.
 *
 * IMPORTANTE: l'overlay viene montato come ULTIMO figlio del root della
 * battle view (top-level, SOPRA HUD e log) in modo che:
 *   - sia sempre visibile anche su Expo Go (non clipped da overflow:hidden
 *     del BattleWrapper né da altri parent)
 *   - mostri un banner rosso "DEBUG ON" inconfutabile → se NON vedi questo
 *     banner su Expo Go, il bundle è cached su una versione vecchia
 *     (ricarica l'app: scuoti → Reload, oppure kill-and-reopen).
 *
 * Mostra:
 *   - Banner rosso "[BATTLE_DEBUG ON]" top-center (marker di versione)
 *   - Rect reale del battlefield (w/h/x/y)
 *   - Griglia logica 3x3 di Team A e Team B (linee sottili)
 *   - Anchor/home position di ogni unità (cerchio pieno + cross-hair)
 *   - Bounding box del wrapper assoluto di ogni unità
 *   - Label con id/nome, col/row, team, zIndex, state, facing
 *
 * Convenzioni cromatiche:
 *   - Team A (player)   → ciano (#00E5FF)
 *   - Team B (enemy)    → magenta (#FF3FB5)
 *   - battlefield rect  → arancione (#FFB347)
 *   - banner marker     → rosso vivido (#FF0055)
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
  /** Rect del battlefield in coordinate del PARENT dell'overlay (cioè la
   *  battle view root). Ci serve x/y per poter disegnare gli anchor/box
   *  delle unità alla posizione GLOBALE corretta. */
  bfRect: { w: number; h: number; x?: number; y?: number } | null;
  layout: BattleLayout;
  units: DebugUnitInfo[];
}

const COLORS = {
  A: '#00E5FF',
  B: '#FF3FB5',
  rect: '#FFB347',
  grid: 'rgba(255,255,255,0.22)',
  banner: '#FF0055',
};

export default function BattleDebugOverlay({ enabled, bfRect, layout, units }: Props) {
  if (!enabled) return null;

  // Banner marker SEMPRE visibile — conferma che il bundle aggiornato è carico.
  // Se su Expo Go NON vedi questo banner, il cache è stantio → reload app.
  const banner = (
    <View pointerEvents="none" style={s.bannerWrap}>
      <View style={s.banner}>
        <Text style={s.bannerText}>🐞 BATTLE_DEBUG ON</Text>
      </View>
    </View>
  );

  // Finché il rect non è noto, mostriamo solo il banner + rect info a zero
  if (!bfRect) {
    return (
      <View pointerEvents="none" style={StyleSheet.absoluteFillObject}>
        {banner}
        <View style={s.rectInfo}>
          <Text style={s.rectTitle}>BATTLE DEBUG</Text>
          <Text style={s.rectLine}>bf: waiting onLayout…</Text>
        </View>
      </View>
    );
  }

  const L = layout;
  const bfX = bfRect.x ?? 0;
  const bfY = bfRect.y ?? 0;
  const bfH = bfRect.h;

  // Converte (home.x, home.y=bottom) nelle coordinate dell'overlay top-level.
  //   top  = bfY + bfH - home.y - slotH
  //   left = bfX + home.x - slotW/2
  const toScreen = (homeX: number, homeY: number, slotW: number, slotH: number) => ({
    left: bfX + homeX - slotW / 2,
    top: bfY + bfH - homeY - slotH,
  });

  const drawGridLines = (team: Team) => {
    const color = team === 'A' ? COLORS.A : COLORS.B;
    const lines: React.ReactNode[] = [];
    for (let col = 0; col < 3; col++) {
      for (let row = 0; row < 3; row++) {
        const home = getHomePosition(team, col, row, L);
        const sizeA = [L.supSize, L.dpsSize, L.tankSize];
        const sizeB = [L.tankSize, L.dpsSize, L.supSize];
        const size = team === 'A' ? sizeA[col] : sizeB[col];
        const slotW = size + 6;
        const slotH = size * 1.25;
        const scr = toScreen(home.x, home.y, slotW, slotH);
        lines.push(
          <View
            key={`dbg_cell_${team}_${col}_${row}`}
            pointerEvents="none"
            style={{
              position: 'absolute',
              left: scr.left,
              top: scr.top,
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

  const drawUnits = () =>
    units.map(u => {
      const home = getHomePosition(u.team, u.col, u.row, L);
      const color = u.team === 'A' ? COLORS.A : COLORS.B;
      const slotW = u.size + 6;
      const slotH = u.size * 1.25;
      const scr = toScreen(home.x, home.y, slotW, slotH);
      // Anchor cross-hair → posizione "piede" dello sprite (bottom center).
      const anchorLeft = bfX + home.x - 7;
      const anchorTop = bfY + bfH - home.y - 7;
      return (
        <React.Fragment key={`dbg_u_${u.team}_${u.id}`}>
          {/* Bounding box del wrapper assoluto */}
          <View
            pointerEvents="none"
            style={{
              position: 'absolute',
              left: scr.left,
              top: scr.top,
              width: slotW,
              height: slotH,
              borderWidth: 2,
              borderColor: color,
            }}
          />
          {/* Cross-hair anchor point */}
          <View
            pointerEvents="none"
            style={{ position: 'absolute', left: anchorLeft, top: anchorTop, width: 14, height: 14 }}
          >
            <View style={[s.crossH, { backgroundColor: color }]} />
            <View style={[s.crossV, { backgroundColor: color }]} />
            <View style={[s.dot, { backgroundColor: color }]} />
          </View>
          {/* Label info */}
          <View
            pointerEvents="none"
            style={{
              position: 'absolute',
              left: scr.left,
              top: scr.top - 26,
              maxWidth: slotW + 20,
              backgroundColor: 'rgba(0,0,0,0.78)',
              paddingHorizontal: 3,
              paddingVertical: 1,
              borderRadius: 3,
            }}
          >
            <Text style={[s.lbl, { color }]} numberOfLines={1}>
              {u.team}·c{u.col}r{u.row} z{u.zIndex}
            </Text>
            <Text style={[s.lblSmall, { color: '#FFF' }]} numberOfLines={1}>
              {(u.name || u.id).slice(0, 10)} • {u.state || 'idle'}
            </Text>
            <Text style={[s.lblSmall, { color: '#AAA' }]} numberOfLines={1}>
              {u.facing || '—'} • s{u.size}
            </Text>
          </View>
        </React.Fragment>
      );
    });

  return (
    <View pointerEvents="none" style={StyleSheet.absoluteFillObject}>
      {banner}
      {/* Rect info block — top-left */}
      <View style={s.rectInfo}>
        <Text style={s.rectTitle}>BATTLE DEBUG</Text>
        <Text style={s.rectLine}>
          bf: {Math.round(bfRect.w)}×{Math.round(bfRect.h)} @ ({Math.round(bfX)},{Math.round(bfY)})
        </Text>
        <Text style={s.rectLine}>
          tank:{L.tankSize} dps:{L.dpsSize} sup:{L.supSize} rs:{L.rowStep}
        </Text>
        <Text style={s.rectLine}>units: {units.length}</Text>
      </View>

      {/* Battlefield edge outline (nella posizione reale misurata) */}
      <View
        pointerEvents="none"
        style={{
          position: 'absolute',
          left: bfX,
          top: bfY,
          width: bfRect.w,
          height: bfRect.h,
          borderWidth: 2,
          borderColor: COLORS.rect,
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
    backgroundColor: COLORS.banner,
    paddingHorizontal: 10,
    paddingVertical: 2,
    borderBottomLeftRadius: 6,
    borderBottomRightRadius: 6,
    borderWidth: 1,
    borderColor: '#FFF',
  },
  bannerText: { color: '#FFF', fontSize: 10, fontWeight: '900', letterSpacing: 1 },
  rectInfo: {
    position: 'absolute',
    top: 22,
    left: 6,
    backgroundColor: 'rgba(0,0,0,0.8)',
    paddingHorizontal: 6,
    paddingVertical: 3,
    borderRadius: 4,
    borderWidth: 1,
    borderColor: COLORS.rect,
    zIndex: 9999,
  },
  rectTitle: { color: COLORS.rect, fontSize: 10, fontWeight: '800', letterSpacing: 1 },
  rectLine: { color: '#FFF', fontSize: 9, fontFamily: 'monospace' },
  lbl: { fontSize: 8, fontWeight: '700', fontFamily: 'monospace' },
  lblSmall: { fontSize: 8, fontFamily: 'monospace' },
  crossH: { position: 'absolute', top: 6, left: 0, width: 14, height: 2 },
  crossV: { position: 'absolute', left: 6, top: 0, width: 2, height: 14 },
  dot: { position: 'absolute', left: 5, top: 5, width: 4, height: 4, borderRadius: 2 },
});

export default function BattleDebugOverlay({ enabled, bfRect, layout, units }: Props) {
  if (!enabled || !bfRect) return null;

  const L = layout;

  // Grid lines (logiche 3x3 per lato). Usa bounding X di ogni slot.
  const drawGridLines = (team: Team) => {
    const color = team === 'A' ? COLORS.A : COLORS.B;
    const lines: React.ReactNode[] = [];
    for (let col = 0; col < 3; col++) {
      for (let row = 0; row < 3; row++) {
        const home = getHomePosition(team, col, row, L);
        const sizeA = [L.supSize, L.dpsSize, L.tankSize];
        const sizeB = [L.tankSize, L.dpsSize, L.supSize];
        const size = team === 'A' ? sizeA[col] : sizeB[col];
        const slotW = size + 6;
        const slotH = size * 1.25;
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

  // Anchor marker + label per ogni unità presente
  const drawUnits = () =>
    units.map(u => {
      const home = getHomePosition(u.team, u.col, u.row, L);
      const color = u.team === 'A' ? COLORS.A : COLORS.B;
      const slotW = u.size + 6;
      const slotH = u.size * 1.25;
      return (
        <React.Fragment key={`dbg_u_${u.team}_${u.id}`}>
          {/* Bounding box del wrapper assoluto */}
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
          {/* Cross-hair anchor point (base centrale dello sprite) */}
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
          {/* Label info */}
          <View
            pointerEvents="none"
            style={{
              position: 'absolute',
              left: home.x - slotW / 2,
              bottom: home.y + slotH + 2,
              maxWidth: slotW + 20,
              backgroundColor: 'rgba(0,0,0,0.78)',
              paddingHorizontal: 3,
              paddingVertical: 1,
              borderRadius: 3,
            }}
          >
            <Text style={[s.lbl, { color }]} numberOfLines={1}>
              {u.team}·c{u.col}r{u.row} z{u.zIndex}
            </Text>
            <Text style={[s.lblSmall, { color: '#FFF' }]} numberOfLines={1}>
              {(u.name || u.id).slice(0, 10)} • {u.state || 'idle'}
            </Text>
            <Text style={[s.lblSmall, { color: '#AAA' }]} numberOfLines={1}>
              {u.facing || '—'} • s{u.size}
            </Text>
          </View>
        </React.Fragment>
      );
    });

  return (
    <View pointerEvents="none" style={StyleSheet.absoluteFillObject}>
      {/* Rect info block — top-left */}
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

      {/* Battlefield edge outline */}
      <View
        pointerEvents="none"
        style={{
          position: 'absolute',
          left: 0,
          top: 0,
          right: 0,
          bottom: 0,
          borderWidth: 1,
          borderColor: COLORS.rect,
        }}
      />

      {/* Grid lines logica 3x3 per team */}
      {drawGridLines('A')}
      {drawGridLines('B')}

      {/* Anchor + bounding box + label per ogni unità */}
      {drawUnits()}
    </View>
  );
}

const s = StyleSheet.create({
  rectInfo: {
    position: 'absolute',
    top: 2,
    left: 2,
    backgroundColor: 'rgba(0,0,0,0.8)',
    paddingHorizontal: 6,
    paddingVertical: 3,
    borderRadius: 4,
    borderWidth: 1,
    borderColor: COLORS.rect,
    zIndex: 9999,
  },
  rectTitle: { color: COLORS.rect, fontSize: 10, fontWeight: '800', letterSpacing: 1 },
  rectLine: { color: '#FFF', fontSize: 9, fontFamily: 'monospace' },
  lbl: { fontSize: 8, fontWeight: '700', fontFamily: 'monospace' },
  lblSmall: { fontSize: 8, fontFamily: 'monospace' },
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
