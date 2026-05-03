/**
 * RM1.23-C2 — SynergyHeroMiniCard
 * ─────────────────────────────────────────────────────────────────────────
 * Mini-card grafica per i membri di una sinergia. Sostituisce le pill
 * testuali nel Synergy Codex e nella tab Sinergie del Hero Detail.
 *
 *  Varianti:
 *   • variant='tile'    → verticale ~80×88 (Codex)
 *      avatar 48 + nome + badge stato
 *   • variant='compact' → orizzontale ~h54 (Hero Detail)
 *      avatar 38 + nome/stelle + badge stato
 *
 *  Stati colorati:
 *   • in_team           → verde (#44DD88)  badge "In team"
 *   • owned             → azzurro (#44AAFF) badge "Posseduto"
 *   • not_owned         → grigio (#666)    badge "Manca"
 *
 *  Read-only: niente onPress di default (deep-link instabile).
 *
 *  Risoluzione immagine:
 *   • Se hero_id è registrato in HERO_ASSET_REGISTRY (Hoplite, Berserker,
 *     placeholder set) → asset locale via heroPortraitSource.
 *   • Altrimenti fallback iniziali volto + sfondo gradient elemento/fazione.
 */
import React, { useMemo, useState } from 'react';
import { View, Text, StyleSheet, Image, ImageSourcePropType } from 'react-native';
import { getHeroVariant, heroPortraitSource } from './hopliteAssets';

export type SynergyHeroMember = {
  canonical_id: string;
  display_name: string;
  owned: boolean;
  in_team: boolean;
  best_stars: number;
  max_stars: number;
  hero_id?: string | null;
  image_url?: string | null;
  /** RM1.23-C3: opzionale per future API che mandano l'image inline */
  image?: string | null;
  hero_image?: string | null;
  rarity?: number | null;
  element?: string | null;
  faction?: string | null;
  asset_status?: string | null;
};

type Variant = 'tile' | 'compact';

type Props = {
  member: SynergyHeroMember;
  variant?: Variant;
  /** Se true, riduce ulteriormente la card (es. liste molto dense). */
  dense?: boolean;
};

const STATUS = {
  IN_TEAM: { color: '#44DD88', bg: '#44DD8822', label: 'In team' },
  OWNED:   { color: '#44AAFF', bg: '#44AAFF22', label: 'Posseduto' },
  MISSING: { color: '#7A6C8E', bg: '#7A6C8E22', label: 'Manca' },
};

const ELEMENT_TINT: Record<string, string> = {
  fire: '#FF6B5544',
  water: '#3FA9F544',
  earth: '#A37A4444',
  wind: '#7BD3FA44',
  air: '#7BD3FA44',
  lightning: '#FFD93D44',
  thunder: '#FFD93D44',
  light: '#FFE9A044',
  dark: '#7B5BC044',
  shadow: '#7B5BC044',
  ice: '#9FE6FF44',
  nature: '#7CD68A44',
  arcane: '#C285FF44',
};

const RARITY_BORDER: Record<number, string> = {
  1: '#88CC88',
  2: '#44AAFF',
  3: '#9966FF',
  4: '#FFB347',
  5: '#FF44CC',
  6: '#FFD700',
};

function getStatus(member: SynergyHeroMember) {
  if (member.in_team) return STATUS.IN_TEAM;
  if (member.owned) return STATUS.OWNED;
  return STATUS.MISSING;
}

function initials(name: string): string {
  const parts = (name || '').trim().split(/\s+/);
  if (!parts.length) return '?';
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[1][0]).toUpperCase();
}

/**
 * RM1.23-C3 — Risolutore immagine prioritizzato per mini-card.
 * Priority order:
 *   1) getHeroVariant(canonical_id, name, 'portrait') — restituisce splash.jpg
 *      (vera arte hero) tramite HERO_CONTRACTS placeholder/canonical.
 *      Fallback chain interna: portrait → splash → card → detail.
 *   2) getHeroVariant(canonical_id, name, 'splash') — esplicito su splash
 *      se il contratto non ha portrait registrata.
 *   3) heroPortraitSource(image_url, id, name) — sentinel/URL remoto +
 *      fallback HERO_ASSET_REGISTRY ('card' role, ultima spiaggia).
 *   4) {uri: image | image_url | hero_image} — campo backend remoto.
 *   5) null → fallback iniziali.
 *
 * Usa display_name come alias-recovery (Hoplite/Berserker name aliases).
 */
function resolveMiniCardImage(
  member: SynergyHeroMember,
): ImageSourcePropType | null {
  const resolvedId =
    (member.hero_id && String(member.hero_id)) ||
    (member.canonical_id && String(member.canonical_id)) ||
    null;
  const name = member.display_name || null;

  // 1) portrait variant via contract (splash.jpg per placeholder, art canonica per Hoplite/Berserker)
  const portraitSrc = getHeroVariant(resolvedId, name, 'portrait');
  if (portraitSrc) return portraitSrc;

  // 2) esplicito splash variant (alcune contratti potrebbero avere solo splash)
  const splashSrc = getHeroVariant(resolvedId, name, 'splash');
  if (splashSrc) return splashSrc;

  // 3) sentinel-based / legacy registry resolver
  const legacy = heroPortraitSource(
    member.image_url || member.image || member.hero_image,
    resolvedId,
    name,
  );
  if (legacy && (typeof legacy === 'number' ||
      (typeof legacy === 'object' && (legacy as any).uri && (legacy as any).uri !== ''))) {
    return legacy;
  }

  // 4) URL remoto raw (image / image_url / hero_image)
  const remote = member.image || member.image_url || member.hero_image;
  if (remote && typeof remote === 'string' && remote.length > 0 && !remote.startsWith('asset:')) {
    return { uri: remote };
  }

  return null;
}

/**
 * Avatar con immagine resolver + fallback iniziali.
 *
 * Image rendering: resizeMode='cover' con focusY ~0.30 implicito tramite
 * objectPosition simulato via translateY (volto leggibile per portrait
 * 2:3 splash). RN non supporta nativo objectPosition: usiamo crop overflow
 * con immagine extra-tall per preservare il volto centrato sopra il busto.
 */
function MiniAvatar({
  member,
  size,
  borderColor,
}: {
  member: SynergyHeroMember;
  size: number;
  borderColor: string;
}) {
  const [errored, setErrored] = useState(false);
  const src: ImageSourcePropType | null = useMemo(
    () => resolveMiniCardImage(member),
    [member.image_url, member.image, member.hero_image, member.hero_id, member.canonical_id, member.display_name],
  );
  const elemTint = (member.element && ELEMENT_TINT[String(member.element).toLowerCase()]) || '#3A2A5C44';

  // Determina se il source è valido (require number o uri non-vuoto).
  const hasValidSource =
    !errored && src != null &&
    (typeof src === 'number' || (typeof src === 'object' && (src as any).uri && (src as any).uri !== ''));

  const radius = size / 2;
  // Per preservare il volto in portrait 2:3 (splash.jpg) dentro un cerchio:
  // - srcAspect ≈ 0.667 (W/H), quindi se renderizziamo come square cover lo
  //   scaledHeight = size, scaledWidth = size * 0.667 ⇒ overflow orizzontale
  //   negativo (no, height domina). Il volto è tipicamente nel quadrante
  //   superiore (y ≈ 0.25-0.35 della splash). resizeMode='cover' su un
  //   container quadrato croppa il body inferiore (mostra busto/spalle
  //   senza volto). Soluzione: rendiamo l'immagine PIÙ ALTA del container e
  //   la spostiamo in alto con translateY negativo per portare il volto
  //   al centro del cerchio.
  const overheight = Math.round(size * 0.45); // 45% extra height
  const imgH = size + overheight;
  const imgW = size; // forza width = container per evitare crop laterale
  const imgTranslateY = -Math.round(overheight * 0.55); // sposta in su per centrare faccia (focusY ~0.30)

  return (
    <View
      style={[
        styles.avatarWrap,
        {
          width: size,
          height: size,
          borderRadius: radius,
          borderColor,
          backgroundColor: elemTint,
        },
      ]}
    >
      {hasValidSource ? (
        <Image
          source={src as ImageSourcePropType}
          style={{
            width: imgW,
            height: imgH,
            transform: [{ translateY: imgTranslateY }],
          }}
          resizeMode="cover"
          onError={() => setErrored(true)}
        />
      ) : (
        <Text style={[styles.avatarInitials, { fontSize: Math.round(size * 0.36) }]}>
          {initials(member.display_name)}
        </Text>
      )}
    </View>
  );
}

function StarsRow({ best, max, dense }: { best: number; max: number; dense?: boolean }) {
  if (max <= 0) return null;
  const fontSize = dense ? 8 : 9;
  return (
    <Text style={[styles.starsText, { fontSize }]}>
      {best > 0 ? `${best}/${max}★` : `—/${max}★`}
    </Text>
  );
}

export default function SynergyHeroMiniCard({ member, variant = 'tile', dense = false }: Props) {
  const status = getStatus(member);
  const rarityBorder = (member.rarity && RARITY_BORDER[member.rarity]) || '#3A2A5C';

  if (variant === 'compact') {
    // Orizzontale per Hero Detail (avatar 38 + info a destra)
    const avatarSize = dense ? 34 : 38;
    return (
      <View
        style={[
          styles.compactWrap,
          { borderColor: status.color + '88', backgroundColor: status.bg },
        ]}
      >
        <MiniAvatar member={member} size={avatarSize} borderColor={rarityBorder} />
        <View style={styles.compactBody}>
          <Text style={styles.compactName} numberOfLines={1}>
            {member.display_name}
          </Text>
          <View style={styles.compactSubRow}>
            <View style={[styles.statusDot, { backgroundColor: status.color }]} />
            <Text style={[styles.compactStatus, { color: status.color }]} numberOfLines={1}>
              {status.label}
            </Text>
            <View style={styles.compactStarsSpacer} />
            <StarsRow best={member.best_stars} max={member.max_stars} dense />
          </View>
        </View>
      </View>
    );
  }

  // Tile verticale per Codex
  const avatarSize = dense ? 44 : 48;
  return (
    <View
      style={[
        styles.tileWrap,
        { borderColor: status.color + '88', backgroundColor: status.bg },
      ]}
    >
      <MiniAvatar member={member} size={avatarSize} borderColor={rarityBorder} />
      <Text style={styles.tileName} numberOfLines={1} ellipsizeMode="tail">
        {member.display_name}
      </Text>
      <StarsRow best={member.best_stars} max={member.max_stars} />
      <View style={[styles.tileBadge, { backgroundColor: status.color + '33', borderColor: status.color }]}>
        <Text style={[styles.tileBadgeText, { color: status.color }]} numberOfLines={1}>
          {status.label}
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  // ── Avatar shared ───────────────────────────────────────────────────
  avatarWrap: {
    overflow: 'hidden',
    borderWidth: 1.5,
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarInitials: {
    color: '#F0E6FF',
    fontWeight: '900',
    letterSpacing: 0.5,
  },

  // ── Tile (vertical) — Codex ─────────────────────────────────────────
  tileWrap: {
    width: 80,
    minHeight: 92,
    borderWidth: 1,
    borderRadius: 10,
    paddingHorizontal: 4,
    paddingVertical: 5,
    alignItems: 'center',
    justifyContent: 'flex-start',
    gap: 3,
  },
  tileName: {
    color: '#F0E6FF',
    fontSize: 10,
    fontWeight: '700',
    textAlign: 'center',
    width: '100%',
    lineHeight: 12,
  },
  tileBadge: {
    paddingHorizontal: 5,
    paddingVertical: 1,
    borderRadius: 6,
    borderWidth: 0.5,
    alignSelf: 'stretch',
    alignItems: 'center',
    marginTop: 1,
  },
  tileBadgeText: {
    fontSize: 8,
    fontWeight: '900',
    letterSpacing: 0.3,
  },

  // ── Compact (horizontal) — Hero Detail ──────────────────────────────
  compactWrap: {
    flexDirection: 'row',
    alignItems: 'center',
    minHeight: 50,
    paddingHorizontal: 6,
    paddingVertical: 5,
    borderWidth: 1,
    borderRadius: 8,
    gap: 8,
    flexBasis: '48%',
    flexGrow: 1,
    maxWidth: '100%',
  },
  compactBody: {
    flex: 1,
    minWidth: 0,
  },
  compactName: {
    color: '#F0E6FF',
    fontSize: 11,
    fontWeight: '800',
  },
  compactSubRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 2,
    gap: 4,
  },
  statusDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
  },
  compactStatus: {
    fontSize: 9,
    fontWeight: '700',
  },
  compactStarsSpacer: { flex: 1 },

  // ── Stars shared ────────────────────────────────────────────────────
  starsText: {
    color: '#FFB347',
    fontWeight: '700',
  },
});
