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
import { getAnimationProfile } from './battle/heroBattleAnimations';
import HeroHopliteRig from './ui/HeroHopliteRig';
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
  /**
   * actionInstanceId — propagato down a HeroHopliteRig. Identifica in
   * modo univoco OGNI invocazione logica di attack/skill dispatchata
   * dal sistema battle. I frame player partono UNA sola volta per id.
   */
  actionInstanceId?: number;
}

export default function BattleSprite({
  character, state, isEnemy = false, hpPercent,
  showDamage, showHeal, isCrit, size = 80, debug = false,
  actionInstanceId,
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
  // idleY/transX/transY/bodyRot/spriteScale/spriteOp sono LOCALI: transform
  // del motion container interno, mai del wrapper globale.
  //   idleY   = respirazione idle loop (±3px)
  //   transY  = motion verticale COMBAT (es. jump del Terremoto, sink morte).
  //             Additivo a idleY nel transform finale → breath + combat.
  const idleY = useSharedValue(0);
  const transX = useSharedValue(0);
  const transY = useSharedValue(0);
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

  // --- Resolver profilo animazioni per-eroe ----------------------------------
  // Hoplite riceve HOPLITE_PROFILE (spear+shield tank), tutti gli altri
  // eroi usano DEFAULT_PROFILE che preserva il comportamento pre-refactor.
  const animProfile = React.useMemo(() => getAnimationProfile(character), [
    character?.hero_id, character?.id, character?.hero_name, character?.name,
  ]);

  // --- Idle breathing ---------------------------------------------------------
  // ═════════════════════════════════════════════════════════════════════════
  // RIMOSSO IL BREATHING GENERICO GLOBALE.
  // ---------------------------------------------------------------------------
  // Prima c'era un withRepeat su idleY (±3px), auraSc e auraOp applicato a
  // TUTTI gli eroi al mount. Questo creava:
  //   (a) un "bob verticale" generico su ogni personaggio,
  //   (b) un pulse aura costante sotto ogni sprite,
  //   (c) una SOVRAPPOSIZIONE con il breathing specifico del rig Hoplite →
  //       il rig-based idle veniva mascherato e sembrava "il vecchio idle".
  //
  // Regola corretta (dall'utente):
  //   "In battle devono animarsi solo gli stati approvati (idle/attack/skill/
  //    hit/death). Se un eroe non ha un'animazione specifica, resta statico."
  //
  // Quindi qui idleY/auraSc/auraOp vengono solo INIZIALIZZATI a valori neutri
  // e mai messi in loop. Gli eroi che hanno un rig/profilo dedicato (Hoplite)
  // avranno il loro breathing INTERNO al rig. Gli altri restano statici,
  // coerenti con la policy.
  // ═════════════════════════════════════════════════════════════════════════
  useEffect(() => {
    if (state === 'dead') return;
    idleY.value = 0;
    auraSc.value = 1;
    auraOp.value = 0; // nessun glow di base — si attiva solo durante skill
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state !== 'dead']);

  // --- State animations -------------------------------------------------------
  // Delega al profilo dell'eroe. Il profilo conosce la fantasia (spear thrust,
  // Terremoto, kneel death, ecc.) e applica withSequence sui shared values.
  // BattleSprite resta "dumb" rispetto all'identità dell'eroe → pattern
  // pulito e riutilizzabile per i prossimi eroi (basta aggiungere un profilo).
  //
  // ⚠ DEPS FIX (no double-trigger):
  //   Prima le deps erano [state, isCrit, size, animProfile] → qualunque
  //   ri-render del parent che cambiava `isCrit` (es. damage float su
  //   targets) o `size` (layout responsive) faceva ri-scattare questo
  //   effect DURANTE una singola action → Hoplite attack/skill potevano
  //   "ripartire a metà", visivamente sembrava doppio trigger.
  //
  //   Ora le deps sono SOLO [state]. La sequenza parte una volta per
  //   cambio-di-stato, esattamente ciò che ci serve. isCrit è letto al
  //   momento dell'invocazione via closure → il valore al momento del
  //   trigger è quello che conta.
  useEffect(() => {
    const dir = isEnemy ? -1 : 1;
    // Cancella animazioni pendenti per prevenire accumulo offset → no drift.
    cancelAnimation(transX);
    cancelAnimation(transY);
    cancelAnimation(bodyRot);
    cancelAnimation(spriteScale);
    const handles = {
      transX, transY, bodyRot, spriteScale, spriteOp,
      auraOp, auraSc, hitFlash, idleY,
    };
    const ctx = { size, isEnemy, dir };
    switch (state) {
      case 'idle':     animProfile.idleReset(handles, ctx); break;
      case 'attack':   animProfile.attack(handles, ctx); break;
      case 'hit':      animProfile.hit(handles, ctx); break;
      case 'skill':    animProfile.skill(handles, ctx); break;
      case 'ultimate': animProfile.ultimate(handles, ctx); break;
      case 'heal':     animProfile.heal(handles, ctx); break;
      case 'dodge':    animProfile.dodge(handles, ctx); break;
      case 'dead':     animProfile.death(handles, ctx); break;
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state]);

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

  // --- Facing (SINGLE SOURCE OF TRUTH) -----------------------------------
  // Per Hoplite TUTTI i 3 player (idle, affondo, guardia_ferrea) sono stati
  // refactored per NON applicare flip interno: renderizzano i PNG sorgente
  // "as-is" (native-facing LEFT, perché i PNG sono esportati con il
  // personaggio rivolto a sinistra). L'UNICO flip avviene qui, tramite
  // `facingScaleX` applicato al wrapper esterno di BattleSprite. Così:
  //  - Team A (non-enemy, lato sinistro) → targetFacing='right' ≠ native='left'
  //      → scaleX=-1 → character flipped a destra → guarda il nemico ✓
  //  - Team B (enemy, lato destro) → targetFacing='left' == native='left'
  //      → scaleX=+1 → character rimane a sinistra → guarda il nemico ✓
  // Questa regola vale COERENTEMENTE per idle, attack e skill.
  const isHoplite = isGreekHoplite(
    character?.hero_id || character?.id,
    character?.hero_name || character?.name,
  );
  const nativeFacing: 'left' | 'right' = isHoplite ? 'left' : 'right';
  const targetFacing: 'left' | 'right' = isEnemy ? 'left' : 'right';
  const facingScaleX = nativeFacing !== targetFacing ? -1 : 1;

  // --- Animated styles -------------------------------------------------------
  // motionStyle applicato al motion container INTERNO (layer 2). Mai al root.
  // translateY = idleY (breathing loop) + transY (combat motion: jump Terremoto,
  // sink death, ecc.) → breath e combat-motion coesistono senza conflitti.
  const motionStyle = useAnimatedStyle(() => ({
    transform: [
      { translateX: transX.value },
      { translateY: idleY.value + transY.value },
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

      {/* -- HP BAR sul personaggio --------------------------------------- */}
      {/* Barra HP chiara visibile, posizionata SOPRA il character frame.   */}
      {/* NON segue il motion → resta stabile anche durante attack/dodge.   */}
      {/* Accetta hpPercent sia come 0..1 sia come 0..100 (auto-normalize). */}
      {(() => {
        if (state === 'dead') return null;
        const raw = typeof hpPercent === 'number' ? hpPercent : 0;
        const pct = Math.max(0, Math.min(100, raw > 1 ? raw : raw * 100));
        return (
          <View
            pointerEvents="none"
            style={{
              position: 'absolute',
              top: 2,
              left: Math.round(frameW * 0.1),
              width: Math.round(frameW * 0.8),
              height: 5,
              backgroundColor: 'rgba(0,0,0,0.75)',
              borderRadius: 3,
              borderWidth: 1,
              borderColor: 'rgba(255,255,255,0.35)',
              overflow: 'hidden',
            }}
          >
            <View
              style={{
                width: `${pct}%`,
                height: '100%',
                backgroundColor:
                  pct > 50 ? '#4ADE80' :
                  pct > 25 ? '#FBBF24' : '#EF4444',
              }}
            />
          </View>
        );
      })()}

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
            ) : isHoplite ? (
              // HOPLITE — rig a layer (HeroHopliteRig). Invece di renderizzare
              // la combat_base.png intera, montiamo i 7 layer PNG separati
              // (hair/legs/skirt/torso/shield_arm/spear_arm/head_helmet) e
              // animiamo le parti del corpo secondo lo state corrente
              // (idle → respiro; attack → Affondo di Falange con wind-up +
              // thrust + impatto + ritorno in guardia). Le gambe restano
              // sempre fisse → silhouette stabile, disciplina tank.
              // Il rig usa BASE 1024 × 1024 quadrato, lo ancoriamo al bottom
              // del frame portrait (size × size*1.25) via justifyContent.
              <View style={{ width: frameW, height: frameH, alignItems: 'center', justifyContent: 'flex-end' }}>
                <HeroHopliteRig size={frameW} state={state as any} actionInstanceId={actionInstanceId} />
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
