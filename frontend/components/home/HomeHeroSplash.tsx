/**
 * HomeHeroSplash — VERSIONE PULITA (Msg 426)
 * =============================================
 *
 * Solo immagine dell'eroe. NESSUNA cornice, NESSUNA card, NESSUNA label,
 * NESSUN testo sotto, NESSUN box descrittivo, NESSUN halo/bordo artificiale.
 *
 * Le animazioni placeholder precedenti (blink opacity globale, respiro
 * scaleY globale) sono state RIMOSSE. L'eroe resta STATICO e pulito.
 *
 * Il sistema definitivo sarà un motore dedicato che leggerà
 * `heroAnimationConfig.ts` e implementerà:
 *  - blink REALE sugli occhi (regione locale)
 *  - breath LOCALIZZATO sul torace (regione locale)
 *  - extra hair/accessories solo per 5★/6★
 * Quella fase verrà fatta dopo. Qui niente animazioni fake.
 *
 * Unica interazione: tap → onPress (apre il Santuario dell'eroe).
 */
import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Image as RNImage } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import HeroPortrait, { isHopliteHero } from '../ui/HeroPortrait';

type Props = {
  hero: {
    id: string;
    name: string;
    rarity?: number;
    element?: string;
    hero_class?: string;
    image_url?: string | null;
  } | null;
  source?: string;
  inTutorial?: boolean;
  width: number;
  height: number;
  onPress?: () => void;
};

export default function HomeHeroSplash({ hero, width, height, onPress }: Props) {
  if (!hero) {
    // Slot vuoto (nessun testo invasivo; area invisibile)
    return <View style={{ width, height, backgroundColor: 'transparent' }} />;
  }

  const isHop = isHopliteHero(hero.id, hero.name);
  const isBorea = hero.id === 'borea';

  return (
    <TouchableOpacity
      activeOpacity={0.92}
      onPress={onPress}
      style={{ width, height, backgroundColor: 'transparent' }}
    >
      {isHop ? (
        // Hoplite: sempre card art locale (base.png)
        <HeroPortrait
          heroId={hero.id}
          heroName={hero.name}
          size={Math.min(width, height)}
          variant="card"
          containerStyle={{ width, height }}
        />
      ) : hero.image_url ? (
        // Altri eroi con image_url remoto
        <RNImage
          source={{ uri: hero.image_url }}
          style={{ width, height }}
          resizeMode="contain"
        />
      ) : (
        // Fallback sobrio per eroi senza asset (es. Borea tutorial):
        // gradient monotono + iniziale. Nessuna label decorativa.
        <LinearGradient
          colors={isBorea
            ? ['#4A7BFF', '#1B2A4E', '#0A1020']
            : ['#3A3A4E', '#1A1A28', '#0A0612']}
          style={[st.fallback, { width, height }]}
          start={{ x: 0.3, y: 0 }}
          end={{ x: 0.7, y: 1 }}
        >
          <Text style={st.fallbackIcon}>
            {isBorea ? '\uD83C\uDF2C\uFE0F' : (hero.name?.[0] || '?')}
          </Text>
        </LinearGradient>
      )}
    </TouchableOpacity>
  );
}

const st = StyleSheet.create({
  fallback: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  fallbackIcon: {
    fontSize: 110,
    fontWeight: '900',
    color: '#ffffff80',
    textAlign: 'center',
  },
});
