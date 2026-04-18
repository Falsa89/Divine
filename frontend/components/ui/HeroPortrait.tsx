/**
 * HeroPortrait
 * ------------
 * Rende il portrait di un eroe.
 *
 * Regole:
 * - Per Greek Hoplite → usa SEMPRE la splash art (non il rig).
 * - Per gli altri eroi → usa l'imageUri remoto.
 * - Se `useRig=true` ed è Greek Hoplite, usa il rig animato (solo per combat / preview).
 */
import React from 'react';
import { View, Image, ImageStyle, StyleProp, ViewStyle } from 'react-native';
import HeroHopliteIdle from './HeroHopliteIdle';
import {
  isGreekHoplite,
  resolveHeroImageSource,
  GREEK_HOPLITE_SPLASH,
} from './hopliteAssets';

type Props = {
  heroId?: string | null;
  heroName?: string | null;
  imageUri?: string | number | null;
  size: number;
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

  // Greek Hoplite standard → splash art
  if (isHoplite) {
    return (
      <View style={[{ width: size, height: size }, containerStyle]}>
        <Image
          source={GREEK_HOPLITE_SPLASH}
          style={[{ width: size, height: size }, style]}
          resizeMode="cover"
        />
      </View>
    );
  }

  // Altri eroi: usa imageUri remoto
  const resolved = resolveHeroImageSource(
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
