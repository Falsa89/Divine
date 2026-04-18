/**
 * HeroPortrait
 * ------------
 * Wrapper intelligente che mostra il rig animato per eroi specifici,
 * oppure fa fallback a un'Image normale.
 *
 * Mappa nome eroe → rig component. Per ora solo Greek Hoplite (mappato a "Athena").
 */
import React from 'react';
import { View, Image, ImageStyle, StyleProp, ViewStyle } from 'react-native';
import HeroHopliteIdle from './HeroHopliteIdle';

// Nomi eroe che usano il rig Greek Hoplite (case-insensitive)
const HOPLITE_HEROES = ['athena', 'hoplite', 'greek hoplite', 'spartana'];

type Props = {
  heroName?: string;
  imageUri?: string | number | null;
  size: number;
  animated?: boolean;
  /** stile applicato al fallback Image */
  style?: StyleProp<ImageStyle>;
  /** contenitore esterno (es. bordi, background) */
  containerStyle?: StyleProp<ViewStyle>;
  /** fallback quando non c'è immagine */
  fallback?: React.ReactNode;
};

function isHopliteHero(name?: string): boolean {
  if (!name) return false;
  const n = name.toLowerCase().trim();
  return HOPLITE_HEROES.some(k => n.includes(k));
}

export default function HeroPortrait({
  heroName,
  imageUri,
  size,
  animated = true,
  style,
  containerStyle,
  fallback,
}: Props) {
  if (isHopliteHero(heroName)) {
    return (
      <View style={[{ width: size, height: size, overflow: 'hidden' }, containerStyle]}>
        <HeroHopliteIdle size={size} animated={animated} />
      </View>
    );
  }

  if (!imageUri) {
    return <View style={[{ width: size, height: size }, containerStyle]}>{fallback}</View>;
  }

  const source = typeof imageUri === 'string' ? { uri: imageUri } : imageUri;
  return (
    <View style={[{ width: size, height: size }, containerStyle]}>
      <Image source={source} style={[{ width: size, height: size }, style]} resizeMode="cover" />
    </View>
  );
}

export { isHopliteHero };
