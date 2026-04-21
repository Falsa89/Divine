/**
 * SlotImage — helper minimale per renderizzare un asset PNG/JPG dal manifest
 * solo se presente, con fallback `children` (tipicamente un <Text> emoji o
 * un placeholder View).
 *
 * Versione "leggera" di AssetSlot — senza frame, solo immagine inline su
 * una size controllata dal caller via style.
 *
 * Usage:
 *   <SlotImage
 *     source={HOME_PROFILE_PANEL.lvBadge}
 *     style={s.lvBadge}
 *     fallback={<Text style={s.lvBadgeTxt}>{level}</Text>}
 *   />
 */
import React from 'react';
import { View, Image, StyleProp, ViewStyle, ImageStyle } from 'react-native';

export type SlotImageProps = {
  source?: any;
  style?: StyleProp<ViewStyle>;
  imageStyle?: StyleProp<ImageStyle>;
  resizeMode?: 'cover' | 'contain' | 'stretch' | 'center';
  fallback?: React.ReactNode;
};

export function SlotImage({
  source,
  style,
  imageStyle,
  resizeMode = 'contain',
  fallback,
}: SlotImageProps) {
  if (source) {
    return (
      <View style={style}>
        <Image
          source={source}
          style={[{ width: '100%', height: '100%' }, imageStyle]}
          resizeMode={resizeMode}
        />
      </View>
    );
  }
  return <View style={style}>{fallback}</View>;
}
