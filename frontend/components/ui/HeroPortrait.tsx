/**
 * HeroPortrait
 * ------------
 * Rende il portrait di un eroe.
 *
 * Regole:
 * - Per Greek Hoplite → usa l'asset locale corretto in base al parametro `variant`.
 *     - variant='card' (default) → base.png (UI piccolo, homepage, collection)
 *     - variant='detail'         → splash.png (fullscreen grande, santuario, encyclopedia)
 * - Per gli altri eroi → usa l'imageUri remoto.
 * - Se `useRig=true` ed è Greek Hoplite, usa il rig animato (solo per combat / preview).
 */
import React from 'react';
import { View, Image, ImageStyle, StyleProp, ViewStyle } from 'react-native';
import HeroHopliteIdle from './HeroHopliteIdle';
import {
  isGreekHoplite,
  resolveHeroImageSource,
  resolveHeroDetailImageSource,
  GREEK_HOPLITE_CARD,
  GREEK_HOPLITE_DETAIL,
} from './hopliteAssets';

type Props = {
  heroId?: string | null;
  heroName?: string | null;
  imageUri?: string | number | null;
  size: number;
  /** 'card' per UI piccola (default), 'detail' per fullscreen grande */
  variant?: 'card' | 'detail';
  /** se true e è Greek Hoplite → usa il rig animato invece della splash (solo combat/preview) */
  useRig?: boolean;
  animated?: boolean;
  style?: StyleProp<ImageStyle>;
  containerStyle?: StyleProp<ViewStyle>;
  fallback?: React.ReactNode;
};

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

  // Greek Hoplite standard → card (UI) o detail (fullscreen)
  if (isHoplite) {
    const hopliteSource = variant === 'detail' ? GREEK_HOPLITE_DETAIL : GREEK_HOPLITE_CARD;
    return (
      <View style={[{ width: size, height: size }, containerStyle]}>
        <Image
          source={hopliteSource}
          style={[{ width: size, height: size }, style]}
          resizeMode="cover"
        />
      </View>
    );
  }

  // Altri eroi: usa imageUri remoto (resolver varia in base a variant)
  const resolver = variant === 'detail' ? resolveHeroDetailImageSource : resolveHeroImageSource;
  const resolved = resolver(
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
