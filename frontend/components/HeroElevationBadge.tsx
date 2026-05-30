/**
 * frontend/components/HeroElevationBadge.tsx
 *
 * PROJECT_HERO_ELEVATION_QUALITY_FRAME_RUNTIME_PACK (v22)
 *
 * Badge UI riusabile per visualizzare il tier Hero Elevation di un eroe.
 * Mostra:
 *  - cornice colore basata su tier.color_id
 *  - label IT (Bianco / Verde +1 / Blu +2 / Viola +3 / Oro +2 / Rosso +3 ecc.)
 *  - indicatore quality +1/+2/+3 (se tier.quality > 0)
 *
 * Vincoli:
 *  - read-only props, NESSUNA mutation di gameplay/economy/server
 *  - touch target n/a (display-only)
 *  - safe area n/a (badge inline)
 */
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { resolveHeroElevationTier, type HeroElevationTier } from '../constants/heroElevation';

export type HeroElevationBadgeProps = {
  /** Tier id (es. "E5"). Se omesso o sconosciuto, fallback a E0. */
  tierId?: string | null;
  /** Dimensione del badge. Default 'md'. */
  size?: 'sm' | 'md' | 'lg';
  /** Mostra label testo accanto al frame. Default true. */
  showLabel?: boolean;
};

export default function HeroElevationBadge({ tierId, size = 'md', showLabel = true }: HeroElevationBadgeProps) {
  const tier: HeroElevationTier = resolveHeroElevationTier(tierId);
  const dim = size === 'sm' ? 28 : size === 'lg' ? 56 : 40;
  const fontSize = size === 'sm' ? 11 : size === 'lg' ? 16 : 13;
  return (
    <View style={styles.row} accessibilityLabel={`Tier ${tier.label_it}`}>
      <View
        style={[
          styles.frame,
          {
            width: dim,
            height: dim,
            borderColor: tier.frame_color_hint,
            backgroundColor: tier.color_id === 'white' ? 'rgba(224,224,234,0.15)' : `${tier.frame_color_hint}22`,
          },
        ]}
      >
        <Text style={[styles.tierText, { color: tier.frame_color_hint, fontSize }]}>{tier.tier_id}</Text>
      </View>
      {showLabel ? (
        <View style={styles.labelBlock}>
          <Text style={[styles.labelText, { color: tier.frame_color_hint, fontSize: fontSize + 1 }]}>{tier.label_it}</Text>
          {tier.quality > 0 ? (
            <Text style={styles.qualityText}>{`Quality +${tier.quality}`}</Text>
          ) : null}
        </View>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  frame: {
    borderRadius: 8,
    borderWidth: 2,
    alignItems: 'center',
    justifyContent: 'center',
  },
  tierText: { fontWeight: '800', letterSpacing: 0.5 },
  labelBlock: { flexDirection: 'column' },
  labelText: { fontWeight: '700' },
  qualityText: { color: '#7a7c9a', fontSize: 11, marginTop: 1 },
});
