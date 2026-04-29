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
};

function hopliteAssetForVariant(variant: HeroImageRole) {
  switch (variant) {
    case 'transparent': return GREEK_HOPLITE_TRANSPARENT;
    case 'detail':      return GREEK_HOPLITE_DETAIL;
    case 'card':
    default:            return GREEK_HOPLITE_PORTRAIT;
  }
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
}: Props) {
  const isHoplite = isGreekHoplite(heroId, heroName);

  // Rig mode: solo se esplicitamente richiesto via useRig
  if (isHoplite && useRig) {
    return (
      <View style={[{ width: size, height: size, overflow: 'hidden' }, containerStyle]}>
        <HeroHopliteIdle size={size} animated={animated} />
      </View>
    );
  }

  // Greek Hoplite standard → asset locale per il variant richiesto
  if (isHoplite) {
    return (
      <View style={[{ width: size, height: size }, containerStyle]}>
        <Image
          source={hopliteAssetForVariant(variant)}
          style={[{ width: size, height: size }, style]}
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
  if (!resolved && typeof imageUri === 'number') {
    // asset require() passato direttamente
    return (
      <View style={[{ width: size, height: size }, containerStyle]}>
        <Image source={imageUri} style={[{ width: size, height: size }, style]} resizeMode="cover" />
      </View>
    );
  }
  if (!resolved) {
    return <View style={[{ width: size, height: size }, containerStyle]}>{fallback}</View>;
  }
  return (
    <View style={[{ width: size, height: size }, containerStyle]}>
      <Image source={resolved} style={[{ width: size, height: size }, style]} resizeMode="cover" />
    </View>
  );
}

// Re-export per compatibilità con import esistenti
export { isGreekHoplite as isHopliteHero } from './hopliteAssets';
