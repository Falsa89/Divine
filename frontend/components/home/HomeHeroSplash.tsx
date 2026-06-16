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
import HeroFramedImage from '../ui/HeroFramedImage';
import { isHeroAssetSentinel, hasHeroUiContract } from '../ui/hopliteAssets';

// Pack 125 FIX C — Asset canonico greek_borea tutorial.
// Mappa legacy hero_id `borea` → asset locale `greek_borea/transparent.png`.
// IMPORTANTE: questo e' SOLO un render visuale. Nessun grant di ownership,
// nessuna unlock di Borea, nessuna modifica al roster/Character Bible.
// Tutorial-only: l'eroe NON e' assegnato all'account, NON e' equipaggiabile.
const GREEK_BOREA_TRANSPARENT = require('../../assets/heroes/greek_borea/transparent.png');
const GREEK_BOREA_SPLASH = require('../../assets/heroes/greek_borea/splash.png');

// Pack 125 — Hero id alias canonici per Borea (legacy + canonical).
// Qualsiasi payload server con uno di questi id viene visualizzato con
// l'asset locale greek_borea, NON con il fallback gradient blu/vento.
const BOREA_HERO_ID_ALIASES = new Set<string>(['borea', 'greek_borea']);
function isBoreaLikeId(heroId: string | null | undefined): boolean {
  if (!heroId) return false;
  return BOREA_HERO_ID_ALIASES.has(String(heroId).toLowerCase());
}

type Props = {
  hero: {
    id: string;
    name: string;
    rarity?: number;
    element?: string;
    hero_class?: string;
    image_url?: string | null;
    /** RM1.17-E: sentinel asset:<id>:<variant> quando image_url è remoto-null.
     *  Il resolver in hopliteAssets lo mappa all'asset locale corretto. */
    image?: string | null;
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
  // Pack 125 FIX C — Rilevamento Borea legacy+canonical (no ownership grant).
  const isBorea = isBoreaLikeId(hero.id);
  // RM1.17-E: preferenza ordine — sentinel locale (asset:*) batte image_url
  // remoto null. Se presente, usiamo il resolver che ritorna il cutout
  // trasparente locale (variant transparent/card/detail) mantenendo la
  // semantica storica Home = overlay.
  const imageSentinel = hero.image && isHeroAssetSentinel(hero.image) ? hero.image : null;
  const remoteUrl = hero.image_url && !isHeroAssetSentinel(hero.image_url) ? hero.image_url : null;
  // RM1.17-S — UI contract path FIRST (Hoplite + Berserker + futuri eroi
  // con ui.home configurato). Questo risolve il top-cut su Hoplite perché
  // Hoplite ora ha ui.home = contain transparent.
  const useUiContract = hasHeroUiContract(hero.id, hero.name);

  return (
    <TouchableOpacity
      activeOpacity={0.92}
      onPress={onPress}
      style={{ width, height, backgroundColor: 'transparent' }}
    >
      {isBorea ? (
        // Pack 125 FIX C — Borea (legacy `borea` o canonical `greek_borea`):
        // render asset locale tutorial. NESSUN grant ownership, NESSUNA unlock,
        // NESSUNA modifica roster/Character Bible. Tutorial-only.
        <RNImage
          accessibilityLabel="Borea (tutorial)"
          source={GREEK_BOREA_TRANSPARENT}
          style={{ width, height }}
          resizeMode="contain"
        />
      ) : useUiContract ? (
        // RM1.17-S — Eroi con UI contract (Hoplite, Berserker, future):
        // framing home contract-driven (contain, no crop testa).
        <HeroFramedImage
          heroId={hero.id}
          heroName={hero.name}
          imageUrl={imageSentinel || remoteUrl || undefined}
          slot="home"
          boxW={width}
          boxH={height}
        />
      ) : isHop ? (
        // Fallback legacy: non dovrebbe più attivarsi (Hoplite ha ui contract),
        // ma preservato per safety.
        <HeroPortrait
          heroId={hero.id}
          heroName={hero.name}
          size={Math.min(width, height)}
          variant="transparent"
          containerStyle={{ width, height }}
        />
      ) : imageSentinel ? (
        // RM1.17-E — Eroi con sentinel ma senza UI contract (fallback legacy).
        <HeroPortrait
          heroId={hero.id}
          heroName={hero.name}
          imageUri={imageSentinel}
          size={Math.min(width, height)}
          variant="transparent"
          containerStyle={{ width, height }}
        />
      ) : remoteUrl ? (
        // Altri eroi con image_url remoto (URL HTTP/HTTPS).
        <RNImage
          source={{ uri: remoteUrl }}
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
