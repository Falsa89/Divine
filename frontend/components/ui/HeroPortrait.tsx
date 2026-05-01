/**
 * HeroPortrait
 * ------------
 * Rende il portrait di un eroe con SEMANTICA ROLE-BASED (v16.24+).
 *
 * Variants:
 * - 'transparent' → cutout senza sfondo (Home overlay decorativo).
 * - 'card'  (DEFAULT) → portrait CON SFONDO (list/team-select/post-battle/etc).
 * - 'detail' → fullscreen detail art (sanctuary/hero-viewer).
 *
 * Per Hoplite il file scelto cambia in base al variant:
 *   transparent → base.png (cutout RGBA alpha=0 ai bordi)
 *   card        → splash.png (con background — full art)
 *   detail      → splash.png (stesso file, fullscreen detail)
 *
 * Per gli altri eroi: oggi un solo URL remoto → tutti i variant
 * tornano {uri: imageUrl}. Estendibile in futuro.
 *
 * Se `useRig=true` ed è Greek Hoplite, usa il rig animato (solo combat/preview).
 *
 * BACKWARD COMPAT: i consumer esistenti che NON passano `variant`
 * ricevono il nuovo default 'card' (= con sfondo). Se erano nati per
 * essere trasparenti devono opt-in esplicitamente a `variant='transparent'`.
 * Es: HomeHeroSplash → variant='transparent'.
 */
import React from 'react';
import { View, Image, ImageStyle, StyleProp, ViewStyle } from 'react-native';
import HeroHopliteIdle from './HeroHopliteIdle';
import {
  isGreekHoplite,
  resolveHeroImageByRole,
  getHeroContract,
  GREEK_HOPLITE_TRANSPARENT,
  GREEK_HOPLITE_PORTRAIT,
  GREEK_HOPLITE_DETAIL,
  type HeroImageRole,
} from './hopliteAssets';

type Props = {
  heroId?: string | null;
  heroName?: string | null;
  imageUri?: string | number | null;
  size: number;
  /**
   * Variant del portrait (mapped a HeroImageRole):
   *  - 'transparent' → cutout senza sfondo (Home overlay)
   *  - 'card' (DEFAULT) → portrait con sfondo (list/team-select/post-battle)
   *  - 'detail' → fullscreen art (sanctuary/hero-viewer)
   */
  variant?: HeroImageRole;
  /** se true e è Greek Hoplite → usa il rig animato invece della splash (solo combat/preview) */
  useRig?: boolean;
  animated?: boolean;
  style?: StyleProp<ImageStyle>;
  containerStyle?: StyleProp<ViewStyle>;
  fallback?: React.ReactNode;
  /**
   * Aspect ratio target del container (width/height). Default 1 (quadrato).
   * Se diverso (es. 2 landscape, 0.5 portrait sottile) il crop focusY
   * viene ri-calcolato per preservare il volto.
   */
  aspect?: number;
};

function hopliteAssetForVariant(variant: HeroImageRole) {
  switch (variant) {
    case 'transparent': return GREEK_HOPLITE_TRANSPARENT;
    case 'detail':      return GREEK_HOPLITE_DETAIL;
    case 'card':
    default:            return GREEK_HOPLITE_PORTRAIT;
  }
}

/**
 * RM1.17-F — Calcola lo style per un'Image che usa `cover` ma vuole
 * ancorare il focus Y della sorgente al centro della box.
 *
 * Idea:
 * - La box ha larghezza W, altezza H (aspect = W/H).
 * - La sorgente ha aspect sourceAspectRatio (width/height).
 * - Con resizeMode='cover', la sorgente viene scalata per coprire tutta
 *   la box → una delle due dimensioni deborda.
 * - Di default il cover centra la sorgente (overflow simmetrico).
 * - Noi vogliamo che il focus Y della sorgente (es. 0.28 per Berserker)
 *   vada al centro verticale visibile della box.
 * - Calcoliamo translateY = (overflow verticale) * (0.5 - focusY),
 *   scalato allo spazio della box.
 *
 * Il translate è applicato all'Image che resta `cover`. Il wrapper View
 * ha `overflow:'hidden'` per tagliare l'eccedenza.
 *
 * Per sorgenti landscape in box portrait vale la simmetrica (translateX
 * based on focusX), ma per l'MVP serviamo solo il caso portrait-in-*
 * perché splash.jpg Berserker è 2:3 portrait.
 */
function computeCoverFocusTransform(
  boxW: number,
  boxH: number,
  sourceAspectRatio: number,   // source_width / source_height
  focusY: number,              // 0..1 dal top della sorgente
): { transform?: { translateY: number }[] } {
  const boxAspect = boxW / boxH;
  // Scala cover: la sorgente ri-dimensionata copre completamente la box.
  // scale = max(boxW / src_w_norm, boxH / src_h_norm) con src_h_norm=1.
  // Normalizzando sorgente ad altezza 1 → src_w = sourceAspectRatio.
  // scale_cover = max(boxW / sourceAspectRatio, boxH)
  const srcW = sourceAspectRatio;
  const srcH = 1;
  const scale = Math.max(boxW / srcW, boxH / srcH);
  const scaledH = srcH * scale;
  const overflowY = Math.max(0, scaledH - boxH);
  if (overflowY === 0) return {};
  // translateY = overflowY * (0.5 - focusY).
  //   focusY=0.5 → 0 shift (default cover center)
  //   focusY<0.5 → translateY positivo → Image si sposta giù → visibili i
  //     pixel alti della sorgente (il volto).
  const ty = Math.round(overflowY * (0.5 - focusY));
  // Avoid noop boxAspect dependency, keep for future X focus extension.
  void boxAspect;
  return { transform: [{ translateY: ty }] };
}

export default function HeroPortrait({
  heroId,
  heroName,
  imageUri,
  size,
  variant = 'card',
  useRig = false,
  animated = true,
  style,
  containerStyle,
  fallback,
  aspect = 1,
}: Props) {
  const isHoplite = isGreekHoplite(heroId, heroName);
  const boxW = size;
  const boxH = Math.round(size / aspect);

  // Rig mode: solo se esplicitamente richiesto via useRig
  if (isHoplite && useRig) {
    return (
      <View style={[{ width: boxW, height: boxH, overflow: 'hidden' }, containerStyle]}>
        <HeroHopliteIdle size={Math.min(boxW, boxH)} animated={animated} />
      </View>
    );
  }

  // Greek Hoplite standard → asset locale per il variant richiesto
  if (isHoplite) {
    return (
      <View style={[{ width: boxW, height: boxH, overflow: 'hidden' }, containerStyle]}>
        <Image
          source={hopliteAssetForVariant(variant)}
          style={[{ width: boxW, height: boxH }, style]}
          resizeMode="cover"
        />
      </View>
    );
  }

  // Altri eroi: usa imageUri remoto via resolver role-based
  const resolved = resolveHeroImageByRole(
    variant,
    typeof imageUri === 'string' ? imageUri : null,
    heroId,
    heroName,
  );

  // RM1.17-F — crop focus per eroi registrati con contract.
  // Ricaviamo la focusY in base al variant richiesto.
  const contract = getHeroContract(heroId, heroName);
  const focusY =
    variant === 'detail' ? contract.crop.detailFocusY
    : variant === 'card' ? contract.crop.cardFocusY
    : contract.crop.portraitFocusY;
  // sourceAspectRatio estimate: portrait 2/3=0.667, square 1, landscape 3/2=1.5.
  const srcAspect =
    contract.crop.sourceAspect === 'portrait' ? (2/3)
    : contract.crop.sourceAspect === 'landscape' ? (3/2)
    : 1;
  const focusTransform = computeCoverFocusTransform(boxW, boxH, srcAspect, focusY);

  if (!resolved && typeof imageUri === 'number') {
    // asset require() passato direttamente
    return (
      <View style={[{ width: boxW, height: boxH, overflow: 'hidden' }, containerStyle]}>
        <Image source={imageUri} style={[{ width: boxW, height: boxH }, focusTransform, style]} resizeMode="cover" />
      </View>
    );
  }
  if (!resolved) {
    return <View style={[{ width: boxW, height: boxH }, containerStyle]}>{fallback}</View>;
  }
  return (
    <View style={[{ width: boxW, height: boxH, overflow: 'hidden' }, containerStyle]}>
      <Image source={resolved} style={[{ width: boxW, height: boxH }, focusTransform, style]} resizeMode="cover" />
    </View>
  );
}

// Re-export per compatibilità con import esistenti
export { isGreekHoplite as isHopliteHero } from './hopliteAssets';
