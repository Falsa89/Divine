/**
 * AssetBackedGradient — Drop-in replacement per `<LinearGradient>` che
 * "cade" su un asset immagine quando disponibile nel manifest.
 *
 * Regole:
 *   - Se `source` è definito → renderizza <ImageBackground> con capInsets
 *     opzionali (9-slice). Il gradient di fallback NON è renderizzato.
 *   - Se `source` è undefined → renderizza <LinearGradient fallbackColors>
 *     con gli stessi children e style del caller.
 *
 * In entrambi i casi lo `style` esterno è preservato 1:1, così il layout
 * non cambia mai tra fallback e asset reale.
 *
 * Usage:
 *   <AssetBackedGradient
 *     source={HOME_PROFILE_PANEL.frame}
 *     capInsets={HOME_PROFILE_PANEL.capInsets}
 *     fallbackColors={['rgba(11,23,60,0.95)', 'rgba(8,15,40,0.85)']}
 *     style={s.profilePanel}
 *   >
 *     {children}
 *   </AssetBackedGradient>
 */
import React from 'react';
import { ImageBackground, StyleProp, ViewStyle, ImageStyle } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

export type AssetBackedGradientProps = {
  /** Require locale o URL remoto. Se mancante → gradient fallback. */
  source?: any;
  /** capInsets per 9-slice (solo iOS/Android native). Ignorato su web. */
  capInsets?: { top: number; left: number; bottom: number; right: number };
  /** Colori usati SOLO se source è undefined. Mantenere IDENTICI all'originale. */
  fallbackColors: readonly [string, string, ...string[]];
  /** start/end del gradient fallback (opzionale). */
  fallbackStart?: { x: number; y: number };
  fallbackEnd?: { x: number; y: number };
  /** Opzionale: overlay decor sopra il frame (HOME_PROFILE_PANEL.decor etc.) */
  decorSource?: any;
  /** Style del container esterno (identico a LinearGradient) */
  style?: StyleProp<ViewStyle>;
  /** Style opzionale per l'immagine interna quando source è presente */
  imageStyle?: StyleProp<ImageStyle>;
  /** resizeMode per l'immagine (default 'stretch' per 9-slice) */
  resizeMode?: 'cover' | 'contain' | 'stretch';
  children?: React.ReactNode;
};

export function AssetBackedGradient({
  source,
  capInsets,
  fallbackColors,
  fallbackStart,
  fallbackEnd,
  decorSource,
  style,
  imageStyle,
  resizeMode = 'stretch',
  children,
}: AssetBackedGradientProps) {
  if (source) {
    // capInsets è supportato da <ImageBackground> via la prop nativa.
    // Su web viene ignorato ma l'immagine è comunque renderizzata corretta
    // per asset non-9-slice.
    return (
      <ImageBackground
        source={source}
        style={style}
        imageStyle={imageStyle as any}
        resizeMode={resizeMode}
        // @ts-expect-error — capInsets valida su native, web ignora
        capInsets={capInsets}
      >
        {decorSource ? (
          <ImageBackground
            source={decorSource}
            style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0 }}
            resizeMode={resizeMode}
            pointerEvents="none"
          />
        ) : null}
        {children}
      </ImageBackground>
    );
  }

  return (
    <LinearGradient
      colors={fallbackColors as any}
      start={fallbackStart}
      end={fallbackEnd}
      style={style}
    >
      {children}
    </LinearGradient>
  );
}
