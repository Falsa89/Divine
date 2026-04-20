/**
 * AssetSlot — componente di montaggio asset asset-driven.
 *
 * Se il manifest fornisce un asset, lo renderizza come <Image>.
 * Altrimenti, renderizza i `children` come fallback tecnico neutro.
 *
 * Uso tipico:
 *   <AssetSlot asset={HOME_PANELS.profile.frame} style={styles.panel}>
 *     <NeutralPlaceholder label="PROFILE" />
 *   </AssetSlot>
 *
 * Per bottoni con stati:
 *   <ButtonAssetSlot asset={HOME_BUTTONS.wheel} state="default" fallback={<IconEmoji ico="🎯" />} />
 */
import React from 'react';
import { View, Image, StyleProp, ViewStyle, ImageStyle } from 'react-native';
import type { ButtonAsset, PanelAsset } from '../../constants/homeAssetsManifest';

/* ------------------- Panel / Frame asset ------------------- */
type AssetSlotProps = {
  asset?: any;
  style?: StyleProp<ViewStyle>;
  imageStyle?: StyleProp<ImageStyle>;
  resizeMode?: 'cover' | 'contain' | 'stretch';
  children?: React.ReactNode;
};
export function AssetSlot({ asset, style, imageStyle, resizeMode = 'stretch', children }: AssetSlotProps) {
  if (asset) {
    return (
      <View style={style}>
        <Image source={asset} style={[{ width: '100%', height: '100%' }, imageStyle]} resizeMode={resizeMode} />
        {children ? <View style={{ position: 'absolute', inset: 0 as any, left: 0, right: 0, top: 0, bottom: 0 }}>{children}</View> : null}
      </View>
    );
  }
  return <View style={style}>{children}</View>;
}

/* ------------------- Button asset con stati ------------------- */
export type ButtonState = 'default' | 'pressed' | 'selected' | 'disabled';
type ButtonAssetSlotProps = {
  asset?: ButtonAsset;
  state?: ButtonState;
  style?: StyleProp<ViewStyle>;
  imageStyle?: StyleProp<ImageStyle>;
  fallback?: React.ReactNode;
};
export function ButtonAssetSlot({ asset, state = 'default', style, imageStyle, fallback }: ButtonAssetSlotProps) {
  const src = asset ? asset[state] || asset.default : undefined;
  if (src) {
    return (
      <View style={style}>
        <Image source={src} style={[{ width: '100%', height: '100%' }, imageStyle]} resizeMode="contain" />
      </View>
    );
  }
  return <View style={style}>{fallback}</View>;
}

/* ------------------- Export utility per panel ------------------- */
export type { PanelAsset, ButtonAsset };
