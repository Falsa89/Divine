/**
 * AssetBackedGradient — Drop-in replacement per `<LinearGradient>` che
 * "cade" su un asset immagine quando disponibile nel manifest.
 *
 * IMPORTANTE (fix web): NON usiamo <ImageBackground> perché su react-native-web
 * l'image interna NON eredita le dimensioni del container quando lo style non
 * specifica width/height espliciti → l'image renderizza a dimensione nativa
 * (es. 2244×701 per un frame, occupando tutto lo schermo).
 *
 * Usiamo invece il pattern:
 *   <View style={style}>                              ← wrapper dimensionato
 *     <Image source={...} style={absoluteFillObject} ← fill del wrapper
 *            resizeMode={...} />
 *     {children}
 *   </View>
 *
 * Questo funziona identico su iOS, Android e web.
 *
 * Regole:
 *   - Se `source` è definito → renderizza <View> con <Image absoluteFill> +
 *     optional decor + children sopra.
 *   - Se `source` è undefined → renderizza <LinearGradient fallbackColors>
 *     con gli stessi children e style del caller.
 *
 * In entrambi i casi lo `style` esterno è preservato 1:1, così il layout
 * non cambia mai tra fallback e asset reale.
 */
import React from 'react';
import { View, Image, StyleSheet, StyleProp, ViewStyle, ImageStyle } from 'react-native';
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
  /** Opzionale: overlay decor sopra il frame */
  decorSource?: any;
  /** Style del container esterno */
  style?: StyleProp<ViewStyle>;
  /** Style opzionale per l'immagine interna */
  imageStyle?: StyleProp<ImageStyle>;
  /** resizeMode per l'immagine (default 'stretch') */
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
    return (
      <View style={style}>
        <Image
          source={source}
          // @ts-expect-error — capInsets valida su native, web ignora
          capInsets={capInsets}
          style={[
            {
              position: 'absolute',
              top: 0, left: 0, right: 0, bottom: 0,
              width: '100%', height: '100%',
            },
            imageStyle,
          ]}
          resizeMode={resizeMode}
        />
        {decorSource ? (
          <Image
            source={decorSource}
            style={{
              position: 'absolute',
              top: 0, left: 0, right: 0, bottom: 0,
              width: '100%', height: '100%',
            }}
            resizeMode={resizeMode}
            pointerEvents="none"
          />
        ) : null}
        {children}
      </View>
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
