/**
 * Battle Motion System
 * ====================
 * Architettura a due livelli per eliminare il drift orizzontale su mobile
 * e abilitare in futuro skill con movimento (approach, backstab, center
 * cast, charge, displacement, ecc.).
 *
 * Due concetti chiari e separati:
 *   1. HOME POSITION (anchor, immutabile durante la battle)
 *      - calcolata UNA VOLTA da (team, col, row) + layout del viewport
 *      - ogni sprite è reso in posizione ASSOLUTA alla sua home
 *      - NON dipende dal flex/reflow → nessun drift al re-render
 *
 *   2. ACTION MOTION (offset temporaneo relativo alla home)
 *      - applicato come transform translateX/translateY sul sprite
 *      - sempre seguito da un return-to-home esplicito (offset → 0,0)
 *      - tipi di movimento espliciti (MotionType) → estendibile
 *
 * Il sistema è PROGETTATO per supportare in futuro:
 *   - attaccante che si sposta davanti al target (approach_target)
 *   - assassino che si posiziona dietro (backstab_target)
 *   - ultimate che centra il campo (move_to_center)
 *   - charge orizzontale (charge_line)
 *   - displacement/knockback/pull di bersagli
 *   - forced facing / confuse
 *
 * La home resta la source of truth → knockback/displacement sono temporanei
 * e possono essere implementati come offset sostenuti finché un timer o una
 * skill "cleanse" non li azzera.
 */

// ---- Types ------------------------------------------------------------------

export interface HomePosition {
  /** Centro orizzontale dello sprite (pixel assoluti dentro il battlefield). */
  x: number;
  /** Distanza verticale dal bordo inferiore del battlefield (pixel). Rows back
   *  sono più alte (y maggiore), rows front sono più basse (y minore).       */
  y: number;
}

export interface BattleLayout {
  winW: number;
  winH: number;
  /** Altezza utile del battlefield (dopo topHud/log/padding). */
  fieldH: number;
  tankSize: number;
  dpsSize: number;
  supSize: number;
  /** Step Y tra una row e l'altra (depth stagger). */
  rowStep: number;
}

export type Team = 'A' | 'B';

/**
 * Tipi di movimento supportati. Tutti ritornano alla home position alla fine.
 * I case non ancora implementati nell'UI ricadono su 'none' via default — ma
 * l'interfaccia resta stabile, così aggiungere una skill "approach_target"
 * diventa semplice senza riscrivere il sistema.
 */
export type MotionType =
  | 'none'              // passive / ranged: resta in home
  | 'lunge'             // dash breve avanti + ritorno (default attacco base)
  | 'approach_target'   // si avvicina davanti al target, colpisce, torna
  | 'backstab_target'   // si posiziona dietro al target, colpisce, torna
  | 'move_to_center'    // centro campo per AoE/ultimate, poi torna
  | 'charge_line'       // carica orizzontale fino al target, poi torna
  | 'recoil';           // knockback reattivo (hit subito)

/**
 * Intento di movimento: il TIPO + info opzionali sul target. Progettato
 * per essere passato da combat.tsx (che conosce team/target) a BattleSprite
 * (che esegue la sequenza animata).
 */
export interface MotionIntent {
  type: MotionType;
  /** Posizione del target (per approach/backstab/charge). */
  targetHome?: HomePosition | null;
  /** Centro campo (per move_to_center). */
  centerXY?: HomePosition | null;
}

export interface MotionPlan {
  /** Offset X dalla home durante l'action phase. */
  dx: number;
  /** Offset Y dalla home durante l'action phase. */
  dy: number;
  /** Durata per raggiungere la action position (ms). */
  goDurMs: number;
  /** Tempo di hold alla action position (ms). */
  holdMs: number;
  /** Durata del ritorno alla home (ms). */
  returnDurMs: number;
}

// ---- Layout helpers ---------------------------------------------------------

/**
 * Calcola le metriche del battle layout dal RECT REALE del battlefield
 * (misurato via onLayout). Prima ricevevamo il viewport globale (winW/winH)
 * e sottraevamo paddings stimati — ma su mobile le stime non combaciavano
 * con la safe area reale → unità fuori asse. Ora accetta direttamente il
 * rect del container battlefield: la source of truth è la misura del DOM/UI.
 *
 * Il tankSize è vincolato da DUE criteri contemporaneamente:
 *   1. VERTICALE  — sprite frame (size*1.25) deve entrare nel budget di fieldH
 *                   al netto del row stagger.
 *   2. ORIZZONTALE — 2 team × (support + dps + tank) + VS + margin deve entrare
 *                   nella larghezza reale del battlefield. Altrimenti su
 *                   landscape stretti (mobile) gli sprite vengono tagliati ai
 *                   bordi.
 * Si sceglie il minimo dei due → garantisce che tutte le 12 unità siano
 * visibili dentro il rect reale del container.
 *
 * @param bfW  larghezza reale del battlefield container
 * @param bfH  altezza reale del battlefield container
 */
export function buildBattleLayout(bfW: number, bfH: number): BattleLayout {
  // fieldH = l'altezza utile per gli sprite DENTRO il battlefield.
  const fieldH = Math.max(120, bfH - 8);
  const rowStep = Math.max(14, Math.min(34, Math.round(bfH * 0.10)));

  // Vincolo 1 — verticale: size * 1.25 + stagger rows ≤ fieldH
  const maxByHeight = Math.floor((fieldH - rowStep * 2) / 1.25);

  // Vincolo 2 — orizzontale: spazio per entrambi i team + VS + margini
  // teamWidth = (supSize + dpsSize + tankSize) + 3*slot_pad (6 cad. = 18)
  // con supSize=0.71t, dpsSize=0.86t → teamWidth ≈ 2.57 t + 18
  // totalUsed ≈ 2 * teamWidth + VS(32) + side_margins(32) ≈ 5.15 t + 100
  // → t ≤ (bfW - 100) / 5.15
  const maxByWidth = Math.floor((bfW - 100) / 5.15);

  const tankSize = Math.max(72, Math.min(180, Math.min(maxByHeight, maxByWidth)));
  const dpsSize = Math.round(tankSize * 0.86);
  const supSize = Math.round(tankSize * 0.71);
  return { winW: bfW, winH: bfH, fieldH, tankSize, dpsSize, supSize, rowStep };
}

/**
 * Home position (assoluta) nel battlefield per un'unità data (team, col, row).
 *
 *   Team A (player) occupa la metà SINISTRA:
 *     - col 0 = support (back, più lontano dal centro)
 *     - col 1 = DPS (mid)
 *     - col 2 = tank (front, più vicino al centro/nemico)
 *
 *   Team B (enemy) è il MIRROR: occupa la metà DESTRA, con col 0 = tank
 *   front (vicino al centro), col 2 = support back.
 *
 *   Le row (0=top, 1=mid, 2=bottom nella formation) sono rese come stagger
 *   verticale: row 0 più in alto (più indietro in prospettiva), row 2 più
 *   in basso (più avanti).
 */
export function getHomePosition(
  team: Team,
  col: number,
  row: number,
  L: BattleLayout,
): HomePosition {
  const PAD = 6;
  // Sizes ordered by slot (support, dps, tank)
  const sizesA = [L.supSize, L.dpsSize, L.tankSize];
  const sizesB = [L.tankSize, L.dpsSize, L.supSize]; // mirror: col 0 = tank
  const slotsA = sizesA.map(s => s + PAD);
  const slotsB = sizesB.map(s => s + PAD);
  const totalA = slotsA.reduce((a, b) => a + b, 0);
  const totalB = slotsB.reduce((a, b) => a + b, 0);
  const centerX = L.winW / 2;
  const VS_HALF = 16; // metà larghezza della zona VS

  let x = 0;
  if (team === 'A') {
    // Team A: parte da sinistra del centro (allineato a destra del proprio blocco)
    let cursor = centerX - VS_HALF - totalA;
    // Posizione centrata dentro lo slot
    for (let i = 0; i < col; i++) cursor += slotsA[i];
    x = cursor + slotsA[col] / 2;
  } else {
    // Team B: parte da destra del centro
    let cursor = centerX + VS_HALF;
    for (let i = 0; i < col; i++) cursor += slotsB[i];
    x = cursor + slotsB[col] / 2;
  }

  // Y: coord bottom — row 0 è back (y maggiore, più in alto sullo schermo),
  // row 2 è front (y minore, più in basso vicino al ground).
  const baseBottom = 12;
  const y = baseBottom + (2 - row) * L.rowStep;
  return { x, y };
}

/** Centro campo (usato da move_to_center). */
export function getBattleCenter(L: BattleLayout): HomePosition {
  return { x: L.winW / 2, y: 12 + L.rowStep };
}

// ---- Motion planning --------------------------------------------------------

/**
 * Mappa di default: state backend → MotionType. Quando arriveranno skill
 * custom con movement esplicito, si potrà bypassare questa mappa passando
 * un MotionIntent esplicito al BattleSprite.
 */
export function stateToDefaultMotionType(state: string): MotionType {
  switch (state) {
    case 'attack':
      return 'lunge';
    case 'skill':
      return 'lunge';        // in futuro: potrà diventare 'approach_target'
    case 'ultimate':
      return 'lunge';        // in futuro: 'move_to_center'
    case 'dodge':
      return 'recoil';       // micro step indietro
    case 'hit':
    case 'heal':
    case 'dead':
    case 'idle':
    default:
      return 'none';
  }
}

/**
 * Calcola il MotionPlan concreto dato un intento, la home di partenza e
 * il contesto (size, direzione, eventuale target). Il ritorno è sempre
 * implicito: la sequenza completa è goDurMs → holdMs → returnDurMs.
 */
export function planMotion(
  intent: MotionIntent,
  from: HomePosition,
  size: number,
  isEnemy: boolean,
): MotionPlan {
  const DIR = isEnemy ? -1 : 1;
  const empty: MotionPlan = { dx: 0, dy: 0, goDurMs: 0, holdMs: 0, returnDurMs: 0 };
  switch (intent.type) {
    case 'none':
      return empty;

    case 'lunge': {
      return {
        dx: DIR * size * 0.10,
        dy: 0,
        goDurMs: 140,
        holdMs: 80,
        returnDurMs: 260,
      };
    }

    case 'recoil': {
      return {
        dx: -DIR * size * 0.08,
        dy: 0,
        goDurMs: 110,
        holdMs: 160,
        returnDurMs: 240,
      };
    }

    case 'approach_target': {
      const t = intent.targetHome;
      if (!t) return planMotion({ type: 'lunge' }, from, size, isEnemy);
      // Sta davanti al target, sul proprio lato
      const stopBefore = DIR * (size * 0.55);
      return {
        dx: (t.x - from.x) - stopBefore,
        dy: -(t.y - from.y),
        goDurMs: 320,
        holdMs: 220,
        returnDurMs: 380,
      };
    }

    case 'backstab_target': {
      const t = intent.targetHome;
      if (!t) return planMotion({ type: 'lunge' }, from, size, isEnemy);
      // Sta DIETRO al target (oltre, dal lato opposto)
      const stopBehind = DIR * (size * 0.55);
      return {
        dx: (t.x - from.x) + stopBehind,
        dy: -(t.y - from.y),
        goDurMs: 340,
        holdMs: 240,
        returnDurMs: 400,
      };
    }

    case 'move_to_center': {
      const c = intent.centerXY;
      if (!c) return planMotion({ type: 'lunge' }, from, size, isEnemy);
      return {
        dx: c.x - from.x,
        dy: -(c.y - from.y),
        goDurMs: 360,
        holdMs: 320,
        returnDurMs: 420,
      };
    }

    case 'charge_line': {
      const t = intent.targetHome;
      if (!t) return planMotion({ type: 'lunge' }, from, size, isEnemy);
      // Percorre quasi tutta la distanza rapidamente, fermandosi al target
      const stopBefore = DIR * (size * 0.30);
      return {
        dx: (t.x - from.x) - stopBefore,
        dy: 0,
        goDurMs: 220,
        holdMs: 120,
        returnDurMs: 340,
      };
    }

    default:
      return empty;
  }
}
