/**
 * HeroFramedImage — RM1.17-R
 * ------------------------------------------------------------------
 * Componente riutilizzabile che applica il UI portrait framing contract
 * per un dato slot (`home` | `card` | `detailIcon` | `selectedPreview`
 * | `fullscreen`).
 *
 * SINGOLA FONTE DI VERITÀ per portrait rendering fuori dal battle:
 *  - risolve source via heroUiSource(...) (contract-based)
 *  - sceglie resizeMode da framing (contain | cover)
 *  - calcola translate/scale per ancorare il focusY della sorgente
 *    (via computeUiCoverTransform) quando resizeMode='cover'
 *  - applica lo scale extra dichiarato nel framing (>1 zoom-in, <1 out)
 *  - NON tocca BattleSprite / RuntimeSheetSprite: solo UI card/splash.
 *
 * Uso:
 *   <HeroFramedImage
 *     heroId={h.id} heroName={h.name}
 *     imageUrl={h.image}
 *     slot="card"
 *     boxW={48} boxH={48}
 *   />
 */
import React from 'react';
import { View, Image, ImageStyle, StyleProp, ViewStyle } from 'react-native';
import {
  getHeroUiFraming,
  heroUiSource,
  computeUiCoverTransform,
  getHeroSourceAspect,
  type HeroUiSlot,
} from './hopliteAssets';

type Props = {
  heroId?: string | null;
  heroName?: string | null;
  imageUrl?: string | null;
  slot: HeroUiSlot;
  boxW: number;
  boxH: number;
  /** Stile aggiuntivo sull'Image (es. borderRadius). */
  imageStyle?: StyleProp<ImageStyle>;
  /** Stile aggiuntivo sul container wrapper. */
  containerStyle?: StyleProp<ViewStyle>;
  /** Fallback renderizzato se il source non è risolvibile. */
  fallback?: React.ReactNode;
};

export default function HeroFramedImage({
  heroId,
  heroName,
  imageUrl,
  slot,
  boxW,
  boxH,
  imageStyle,
  containerStyle,
  fallback,
}: Props) {
  const framing = getHeroUiFraming(heroId, heroName, slot);
  const source = heroUiSource(heroId, heroName, slot, imageUrl);

  if (!source) {
    return (
      <View style={[{ width: boxW, height: boxH, overflow: 'hidden' }, containerStyle]}>
        {fallback}
      </View>
    );
  }

  // 'contain' → lasciamo che l'Image gestisca il fit nativamente, con
  // eventuale scale extra applicato come transform. Niente crop.
  if (framing.resizeMode === 'contain') {
    const extraScale = framing.scale ?? 1;
    const transform = extraScale !== 1 ? [{ scale: extraScale }] : undefined;
    return (
      <View style={[{ width: boxW, height: boxH, overflow: 'hidden' }, containerStyle]}>
        <Image
          source={source}
          style={[
            { width: boxW, height: boxH },
            transform ? { transform } : null,
            imageStyle,
          ]}
          resizeMode="contain"
        />
      </View>
    );
  }

  // 'cover' → calcolo translateX/Y per ancorare focus e applico scale.
  const sourceAspect = getHeroSourceAspect(heroId, heroName);
  const { transform } = computeUiCoverTransform(boxW, boxH, framing, sourceAspect);

  return (
    <View style={[{ width: boxW, height: boxH, overflow: 'hidden' }, containerStyle]}>
      <Image
        source={source}
        style={[
          { width: boxW, height: boxH },
          transform && transform.length > 0 ? { transform } : null,
          imageStyle,
        ]}
        resizeMode="cover"
      />
    </View>
  );
}
