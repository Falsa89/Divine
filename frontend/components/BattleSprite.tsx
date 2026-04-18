/**
 * BattleSprite — geometria a 3 layer espliciti.
 *
 * Decisioni di design (post-bug "mobile drift/overflow"):
 *
 * 1. Il WRAPPER ESTERNO (in combat.tsx) definisce la home position assoluta
 *    (left/bottom/width/height). BattleSprite NON tocca mai la propria
 *    posizione globale — riempie il wrapper esattamente (width:size, height:frameH).
 *    → Niente più mismatch size+16 vs slotW=size+6 che produceva 10px di
 *      sbordamento orizzontale su mobile.
 *
 * 2. Il ROOT di BattleSprite è un box CONOSCIUTO e STABILE: size × frameH.
 *    Tutti i layer interni sono posizionati in absolute rispetto a questo box,
 *    con left/right/bottom espliciti. Niente più layer absolute "inchiodati a 0,0"
 *    che su native producevano offset orizzontali.
 *
 * 3. TRE GEOMETRIE UNIFICATE: sprite-sheet, hero image e placeholder occupano
 *    tutti ESATTAMENTE size × frameH. Niente più placeholder enormi su mobile
 *    perché erano size*1.25 mentre gli sprite-sheet erano size×size.
 *
 * 4. ANCORAGGIO AL SUOLO COERENTE: il character frame ha
 *    justifyContent:'flex-end' → l'Image con resizeMode:'contain' si ancora
 *    al bordo inferiore del frame, i "piedi" del personaggio sono a bottom=0
 *    del wrapper, che a sua volta è a bottom=home.y dal pavimento del
 *    battlefield. Il terreno è quindi una linea coerente per TUTTE le unità.
 *
 * 5. MOTION LAYER LOCALE: translateX/Y/rotate/scale sono applicati SOLO al
 *    motion container interno (mai al wrapper globale né al root).
 *    Quando torna a (0,0,0,1) lo sprite è nella sua home esatta.
 *    → Non può mai "scorrere fuori" dalla cella.
 */
import React, { useEffect, useState } from 'react';
import { View, Text, Image, StyleSheet } from 'react-native';
import Animated, {
  useSharedValue, useAnimatedStyle, withSequence,
  withTiming, withDelay, withRepeat, Easing, cancelAnimation, withSpring,
} from 'react-native-reanimated';
import { LinearGradient } from 'expo-linear-gradient';
import { ELEMENTS, RARITY } from '../constants/theme';
import { heroBattleImageSource, isGreekHoplite } from './ui/hopliteAssets';
import Constants from 'expo-constants';

type SpriteState = 'idle' | 'attack' | 'hit' | 'skill' | 'ultimate' | 'dead' | 'heal' | 'dodge';

// Frame mapping: 4 frames horizontally → 0=idle, 1=attack, 2=hit, 3=skill
const STATE_TO_FRAME: Record<SpriteState, number> = {
  idle: 0, attack: 1, hit: 2, skill: 3, ultimate: 3, dead: 2, heal: 0, dodge: 0,
};

// =============================================================================
// MOUNT TRACKING — diagnostica remount involontari
// -----------------------------------------------------------------------------
// Registry module-level (sopravvive a re-render di combat.tsx). Ogni unità
// logica (per character.id) incrementa il counter al mount e logga unmount.
// Se durante una battle vedi `m2` o superiore apparire sullo sprite, vuol
// dire che il sistema sta effettivamente RIMONTANDO l'unità — va indagato.
// Invece, se tutti gli sprite restano a `m1` per tutta la battle, la
// identity React è stabile → il bug dev'essere altrove.
// =============================================================================
const MOUNT_REGISTRY: Record<string, number> = {};
function sproutId(c: any): string {
  return String(c?.id ?? c?.hero_id ?? c?.user_hero_id ?? c?.name ?? 'unknown');
}

interface Props {
  character: any;
  state: SpriteState;
  isEnemy?: boolean;
  hpPercent: number;
  showDamage?: number | null;
  showHeal?: number | null;
  isCrit?: boolean;
  size?: number;
  /** Se true, disegna bordo tratteggiato interno + anchor dot sul suolo.
   *  Passato da combat.tsx tramite BATTLE_DEBUG per il debug visivo mirato. */
  debug?: boolean;
}

export default function BattleSprite({
  character, state, isEnemy = false, hpPercent,
  showDamage, showHeal, isCrit, size = 80, debug = false,
}: Props) {
  const elemColor = ELEMENTS.colors[character?.element || character?.hero_element] || '#888';
  const rarColor = RARITY.colors[Math.min(character?.rarity || character?.hero_rarity || 1, 6)] || '#888';
  const heroName = character?.name || character?.hero_name || '?';

  // Geometria locale stabile.
  //   frameW = larghezza cella (== size passato dal wrapper)
  //   frameH = altezza cella (size * 1.25, ratio ritratto).
  // Tutti i layer interni sono dimensionati in funzione di queste due costanti.
  const frameW = size;
  const frameH = Math.round(size * 1.25);

  // Sprite URL (sprite sheet mode, es. bot con atlas PNG)
  const backendUrl = Constants.expoConfig?.extra?.EXPO_BACKEND_URL || '';
  const spriteUrl = character?.sprite_url ? `${backendUrl}${character.sprite_url}` : null;
  const heroImage = character?.hero_image || character?.image;
  const hasSpriteSheet = !!spriteUrl;

  // Current frame based on state (solo per sprite sheet)
  const [currentFrame, setCurrentFrame] = useState(0);
  useEffect(() => { setCurrentFrame(STATE_TO_FRAME[state] || 0); }, [state]);

  // =========================================================================
  // MOUNT TRACKING (deps [] → runs once per REAL mount/unmount)
  // Se questa funzione gira più volte durante la stessa battle per la stessa
  // unità, abbiamo una conferma diretta che il componente viene rimontato.
  // In debug mode mostra anche un badge "mN" sul sprite per ispezione visiva.
  // =========================================================================
  const charKey = sproutId(character);
  const [mountCount] = useState<number>(() => {
    MOUNT_REGISTRY[charKey] = (MOUNT_REGISTRY[charKey] || 0) + 1;
    return MOUNT_REGISTRY[charKey];
  });
  useEffect(() => {
    if (debug) {
      // eslint-disable-next-line no-console
      console.log('[BATTLE_DEBUG][MOUNT]', charKey, 'mount#=', MOUNT_REGISTRY[charKey], 'size=', size, 'enemy=', isEnemy);
    }
    return () => {
      if (debug) {
        // eslint-disable-next-line no-console
        console.log('[BATTLE_DEBUG][UNMOUNT]', charKey, 'prevMount#=', MOUNT_REGISTRY[charKey]);
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // --- Animation shared values ------------------------------------------------
  // idleY/transX/bodyRot/spriteScale/spriteOp sono LOCALI: transform del motion
  // container interno, mai del wrapper globale.
  const idleY = useSharedValue(0);
  const transX = useSharedValue(0);
  const bodyRot = useSharedValue(0);
  const spriteScale = useSharedValue(1);
  const spriteOp = useSharedValue(1);
  const hitFlash = useSharedValue(0);
  const auraOp = useSharedValue(0.15);
  const auraSc = useSharedValue(1);
  const dmgY = useSharedValue(0);
  const dmgOp = useSharedValue(0);
  const dmgScale = useSharedValue(0.5);
  const healFloatY = useSharedValue(0);
  const healFloatOp = useSharedValue(0);

  // --- Idle breathing ---------------------------------------------------------
  useEffect(() => {
    if (state === 'dead') return;
    idleY.value = withRepeat(withSequence(
      withTiming(-3, { duration: 1000, easing: Easing.inOut(Easing.ease) }),
      withTiming(3, { duration: 1000, easing: Easing.inOut(Easing.ease) }),
    ), -1, true);
    auraSc.value = withRepeat(withSequence(
      withTiming(1.12, { duration: 1500 }),
      withTiming(0.95, { duration: 1500 }),
    ), -1, true);
    auraOp.value = withRepeat(withSequence(
      withTiming(0.4, { duration: 1200 }),
      withTiming(0.1, { duration: 1200 }),
    ), -1, true);
  }, [state !== 'dead']);

  // --- State animations -------------------------------------------------------
  useEffect(() => {
    const dir = isEnemy ? -1 : 1;
    // Cancella animazioni pendenti per prevenire accumulo di offset → mai drift.
    cancelAnimation(transX);
    cancelAnimation(bodyRot);
    cancelAnimation(spriteScale);
    // Dash size-aware: proporzionale al size locale, mai oltre ~12%.
    const ATTACK_DASH = Math.round(size * 0.10);
    const ATTACK_LUNGE = Math.round(size * 0.12);
    const SKILL_DASH = Math.round(size * 0.07);
    const HIT_KNOCK = Math.round(size * 0.05);
    const DODGE_STEP = Math.round(size * 0.10);
    switch (state) {
      case 'idle':
        // Re-anchor esplicito alla home locale.
        transX.value = withTiming(0, { duration: 180 });
        bodyRot.value = withTiming(0, { duration: 180 });
        spriteScale.value = withTiming(1, { duration: 180 });
        spriteOp.value = withTiming(1, { duration: 180 });
        break;
      case 'attack':
        transX.value = withSequence(
          withTiming(dir * ATTACK_DASH, { duration: 140 }),
          withTiming(dir * ATTACK_LUNGE, { duration: 60 }),
          withTiming(0, { duration: 260 }),
        );
        spriteScale.value = withSequence(withTiming(1.08, { duration: 120 }), withTiming(1, { duration: 220 }));
        break;
      case 'hit':
        transX.value = withSequence(
          withTiming(-dir * HIT_KNOCK, { duration: 70 }),
          withTiming(0, { duration: 220 }),
        );
        hitFlash.value = withSequence(withTiming(0.6, { duration: 50 }), withTiming(0, { duration: 200 }));
        spriteScale.value = withSequence(withTiming(0.94, { duration: 70 }), withTiming(1, { duration: 180 }));
        bodyRot.value = withSequence(withTiming(-dir * 4, { duration: 70 }), withTiming(0, { duration: 200 }));
        break;
      case 'skill':
      case 'ultimate':
        auraOp.value = withSequence(withTiming(0.8, { duration: 150 }), withDelay(400, withTiming(0.15, { duration: 300 })));
        auraSc.value = withSequence(withTiming(1.5, { duration: 200 }), withTiming(1, { duration: 300 }));
        transX.value = withSequence(
          withTiming(dir * SKILL_DASH, { duration: 160 }),
          withTiming(0, { duration: 280 }),
        );
        spriteScale.value = withSequence(withTiming(1.12, { duration: 160 }), withTiming(1, { duration: 280 }));
        break;
      case 'heal':
        auraOp.value = withSequence(withTiming(0.6, { duration: 300 }), withTiming(0.15, { duration: 500 }));
        idleY.value = withSequence(withTiming(-5, { duration: 250 }), withTiming(0, { duration: 250 }));
        break;
      case 'dodge':
        transX.value = withSequence(
          withTiming(-dir * DODGE_STEP, { duration: 110 }),
          withDelay(180, withTiming(0, { duration: 240 })),
        );
        spriteOp.value = withSequence(withTiming(0.3, { duration: 80 }), withTiming(1, { duration: 200 }));
        break;
      case 'dead':
        cancelAnimation(idleY); cancelAnimation(auraSc); cancelAnimation(auraOp);
        idleY.value = 0;
        bodyRot.value = withTiming(isEnemy ? -20 : 20, { duration: 600 });
        spriteOp.value = withTiming(0.25, { duration: 800 });
        spriteScale.value = withTiming(0.85, { duration: 600 });
        auraOp.value = withTiming(0, { duration: 300 });
        break;
    }
  }, [state, isCrit, size]);

  // --- Damage / Heal float triggers ------------------------------------------
  useEffect(() => {
    if (showDamage && showDamage > 0) {
      dmgY.value = 0; dmgOp.value = 0; dmgScale.value = isCrit ? 0.3 : 0.5;
      dmgOp.value = withSequence(withTiming(1, { duration: 80 }), withDelay(700, withTiming(0, { duration: 300 })));
      dmgY.value = withTiming(-50, { duration: 1000, easing: Easing.out(Easing.quad) });
      dmgScale.value = withSpring(isCrit ? 1.5 : 1.1);
    }
  }, [showDamage]);
  useEffect(() => {
    if (showHeal && showHeal > 0) {
      healFloatY.value = 0; healFloatOp.value = 0;
      healFloatOp.value = withSequence(withTiming(1, { duration: 120 }), withDelay(600, withTiming(0, { duration: 300 })));
      healFloatY.value = withTiming(-45, { duration: 900, easing: Easing.out(Easing.quad) });
    }
  }, [showHeal]);

  // --- Facing --------------------------------------------------------------
  // Ogni asset ha un "native facing" noto. Hoplite combat_base: lancia a sx.
  // Team A (non-enemy) guarda a destra, Team B a sinistra.
  const isHoplite = isGreekHoplite(
    character?.hero_id || character?.id,
    character?.hero_name || character?.name,
  );
  const nativeFacing: 'left' | 'right' = isHoplite ? 'left' : 'right';
  const targetFacing: 'left' | 'right' = isEnemy ? 'left' : 'right';
  const facingScaleX = nativeFacing !== targetFacing ? -1 : 1;

  // --- Animated styles -------------------------------------------------------
  // motionStyle applicato al motion container INTERNO (layer 2). Mai al root.
  const motionStyle = useAnimatedStyle(() => ({
    transform: [
      { translateX: transX.value },
      { translateY: idleY.value },
      { rotate: `${bodyRot.value}deg` },
      { scale: spriteScale.value },
    ],
    opacity: spriteOp.value,
  }));
  const hitStyle = useAnimatedStyle(() => ({ opacity: hitFlash.value }));
  const auraStyle = useAnimatedStyle(() => ({
    opacity: auraOp.value, transform: [{ scale: auraSc.value }],
  }));
  const dmgStyle = useAnimatedStyle(() => ({
    transform: [{ translateY: dmgY.value }, { scale: dmgScale.value }], opacity: dmgOp.value,
  }));
  const healFStyle = useAnimatedStyle(() => ({
    transform: [{ translateY: healFloatY.value }], opacity: healFloatOp.value,
  }));

  // --- Geometria dei layer ---------------------------------------------------
  const auraSize = Math.round(size * 1.15);                   // leggermente più larga del char
  const auraInset = Math.round((frameW - auraSize) / 2);       // centraggio orizzontale
  const shadowW = Math.round(size * 0.7);
  const shadowInset = Math.round((frameW - shadowW) / 2);
  const elemBadgeSize = Math.max(14, Math.min(22, Math.round(size * 0.13)));
  const elemBadgeFont = Math.round(elemBadgeSize * 0.55);

  return (
    // ========================================================================
    //  ROOT: box CONOSCIUTO size × frameH. Riempie esattamente il wrapper
    //  globale (combat.tsx). overflow:'visible' per aura/damage che sborda.
    // ========================================================================
    <View style={[s.root, { width: frameW, height: frameH }, debug && s.debugRoot]}>

      {/* -- LAYER BG-1: Aura glow ---------------------------------------- */}
      {/* Absolute centrato orizzontalmente, ancorato vicino ai piedi       */}
      {/* (bottom:0 = suolo). Mai inchiodato a 0,0.                         */}
      <Animated.View
        pointerEvents="none"
        style={[
          {
            position: 'absolute',
            left: auraInset,
            bottom: 0,
            width: auraSize,
            height: auraSize,
            borderRadius: auraSize / 2,
            backgroundColor: elemColor,
          },
          auraStyle,
        ]}
      />

      {/* -- LAYER BG-2: Shadow ellittica al suolo ----------------------- */}
      {/* NON segue il motion del character → resta al suolo quando attacca. */}
      <View
        pointerEvents="none"
        style={{
          position: 'absolute',
          left: shadowInset,
          bottom: 2,
          width: shadowW,
          height: 6,
          borderRadius: 20,
          backgroundColor: '#000',
          opacity: state === 'dead' ? 0.1 : 0.3,
        }}
      />

      {/* -- LAYER 2: Motion container (fill assoluto, bottom-anchored) -- */}
      {/* Applica qui E SOLO qui translateX/Y/rot/scale locali.            */}
      <Animated.View
        pointerEvents="box-none"
        style={[
          {
            position: 'absolute',
            left: 0, right: 0, top: 0, bottom: 0,
            alignItems: 'center',
            justifyContent: 'flex-end',      // piedi al suolo
          },
          motionStyle,
        ]}
      >
        {/* Character frame — stessa geometria per tutti i render path. */}
        <View
          style={{
            width: frameW,
            height: frameH,
            borderRadius: 8,
            overflow: 'hidden',
            alignItems: 'center',
            justifyContent: 'flex-end',      // il contenuto si ancora al bottom
            backgroundColor: 'transparent',
          }}
        >
          {/* Facing flip container — scaleX applicato solo qui.              */}
          {/* Gli overlay (hit flash, badge, debug) NON devono essere flippati. */}
          <View
            style={{
              width: frameW,
              height: frameH,
              alignItems: 'center',
              justifyContent: 'flex-end',
              transform: [{ scaleX: facingScaleX }],
            }}
          >
            {hasSpriteSheet ? (
              // Sprite sheet mode: atlas 4 frame orizzontali, ogni frame size×frameH.
              <View style={{ width: frameW, height: frameH, overflow: 'hidden' }}>
                <Image
                  source={{ uri: spriteUrl }}
                  style={{
                    width: frameW * 4,
                    height: frameH,
                    marginLeft: -currentFrame * frameW,
                  }}
                  resizeMode="cover"
                />
              </View>
            ) : heroImage ? (
              // Combat pose (es. Hoplite combat_base.png). contain preserva aspect
              // ratio, justifyContent:'flex-end' del parent ancora ai piedi.
              <Image
                source={heroBattleImageSource(heroImage, character?.hero_id || character?.id, character?.hero_name || character?.name)}
                style={{ width: frameW, height: frameH }}
                resizeMode="contain"
              />
            ) : (
              // Placeholder (bot senza asset): stessa geometria size × frameH.
              <LinearGradient
                colors={[elemColor + '40', elemColor + '15']}
                style={{
                  width: frameW,
                  height: frameH,
                  alignItems: 'center',
                  justifyContent: 'center',
                  borderWidth: 1,
                  borderColor: rarColor + '60',
                  borderRadius: 6,
                }}
              >
                <Text style={{ color: elemColor, fontSize: Math.round(frameW * 0.4), fontWeight: '900' }}>
                  {heroName[0]}
                </Text>
              </LinearGradient>
            )}
          </View>

          {/* Hit flash overlay — fuori dal facing flip, copre tutto il frame. */}
          <Animated.View
            pointerEvents="none"
            style={[
              {
                position: 'absolute',
                left: 0, right: 0, top: 0, bottom: 0,
                backgroundColor: '#FF4444',
                borderRadius: 8,
                zIndex: 10,
              },
              hitStyle,
            ]}
          />

          {/* Element badge — bottom-right, fuori dal facing flip. */}
          <View
            style={{
              position: 'absolute',
              bottom: 3,
              right: 3,
              width: elemBadgeSize,
              height: elemBadgeSize,
              borderRadius: elemBadgeSize / 2,
              backgroundColor: elemColor,
              alignItems: 'center',
              justifyContent: 'center',
              borderWidth: 1.5,
              borderColor: 'rgba(0,0,0,0.4)',
              zIndex: 15,
            }}
          >
            <Text style={{ fontSize: elemBadgeFont, color: '#fff' }}>
              {ELEMENTS.icons[character?.element || character?.hero_element] || ''}
            </Text>
          </View>

          {/* DEBUG: bordo tratteggiato interno del character frame (giallo). */}
          {debug && (
            <View
              pointerEvents="none"
              style={{
                position: 'absolute',
                left: 0, right: 0, top: 0, bottom: 0,
                borderWidth: 1,
                borderColor: '#FFFF00',
                borderStyle: 'dashed',
                zIndex: 20,
              }}
            />
          )}
        </View>
      </Animated.View>

      {/* DEBUG: anchor dot sul suolo (bottom-center) — segna home.y reale. */}
      {debug && (
        <View
          pointerEvents="none"
          style={{
            position: 'absolute',
            left: frameW / 2 - 4,
            bottom: -4,
            width: 8,
            height: 8,
            borderRadius: 4,
            backgroundColor: '#FF00FF',
            borderWidth: 1,
            borderColor: '#FFF',
            zIndex: 50,
          }}
        />
      )}

      {/* DEBUG: badge mount count (top-left). Se durante la battaglia vedi
           m2, m3... su una unità, vuol dire che è stata RIMONTATA (bug di
           identity React). Se resta m1 per tutta la battle, la identity è
           stabile → bug di re-entry era nel prop `entering` del wrapper
           (layout animation Reanimated che si ri-triggerava). */}
      {debug && (
        <View
          pointerEvents="none"
          style={{
            position: 'absolute',
            top: 2,
            left: 2,
            paddingHorizontal: 4,
            paddingVertical: 1,
            borderRadius: 3,
            backgroundColor: mountCount > 1 ? '#FF0055' : '#00E5FF',
            zIndex: 60,
            borderWidth: 1,
            borderColor: '#FFF',
          }}
        >
          <Text style={{ color: '#000', fontSize: 8, fontWeight: '900', fontFamily: 'monospace' }}>
            m{mountCount}
          </Text>
        </View>
      )}

      {/* -- LAYER FG-1: Damage float (absolute, centrato) ---------------- */}
      <Animated.View
        pointerEvents="none"
        style={[
          {
            position: 'absolute',
            top: -8,
            left: 0,
            right: 0,
            alignItems: 'center',
            zIndex: 200,
          },
          dmgStyle,
        ]}
      >
        {showDamage && showDamage > 0 ? (
          <Text
            style={[
              s.dmgText,
              isCrit && s.critText,
              { color: isCrit ? '#FFD700' : '#FF4444' },
            ]}
          >
            {isCrit ? 'CRIT! ' : ''}-{showDamage.toLocaleString()}
          </Text>
        ) : null}
      </Animated.View>

      {/* -- LAYER FG-2: Heal float (absolute, centrato) ------------------ */}
      <Animated.View
        pointerEvents="none"
        style={[
          {
            position: 'absolute',
            top: -8,
            left: 0,
            right: 0,
            alignItems: 'center',
            zIndex: 200,
          },
          healFStyle,
        ]}
      >
        {showHeal && showHeal > 0 ? (
          <Text style={s.healFText}>+{showHeal.toLocaleString()}</Text>
        ) : null}
      </Animated.View>
    </View>
  );
}

const s = StyleSheet.create({
  root: {
    // Box conosciuto, immutabile durante la battle. Niente alignItems: il
    // posizionamento di ogni layer è ESPLICITO via left/right/top/bottom.
    overflow: 'visible',
    backgroundColor: 'transparent',
  },
  debugRoot: {
    // Bordo esterno arancione quando debug=true → conferma la cella effettiva.
    borderWidth: 1,
    borderColor: '#FFB347',
  },
  dmgText: {
    fontSize: 14,
    fontWeight: '900',
    textShadowColor: '#000',
    textShadowRadius: 6,
    textShadowOffset: { width: 1, height: 1 },
  },
  critText: { fontSize: 18, letterSpacing: 2 },
  healFText: {
    fontSize: 14,
    fontWeight: '900',
    color: '#44DD88',
    textShadowColor: '#000',
    textShadowRadius: 6,
    textShadowOffset: { width: 1, height: 1 },
  },
});
