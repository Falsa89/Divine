import React, { useEffect, useMemo } from 'react';
import { View, StyleSheet } from 'react-native';
import Svg, { Circle, Rect, Ellipse, Path, G, Defs, RadialGradient, Stop } from 'react-native-svg';
import Animated, {
  useSharedValue, useAnimatedStyle, withRepeat, withSequence,
  withTiming, withDelay, Easing, cancelAnimation,
} from 'react-native-reanimated';

type SpriteState = 'idle' | 'attack' | 'hit' | 'skill' | 'ultimate' | 'dead' | 'heal' | 'dodge';

interface Props {
  name?: string;
  element?: string;
  heroClass?: string;
  rarity?: number;
  isEnemy?: boolean;
  state: SpriteState;
  scale?: number;
}

// Generate unique visual traits from hero name using simple hash
function hashStr(s: string): number {
  let h = 0;
  for (let i = 0; i < s.length; i++) { h = ((h << 5) - h + s.charCodeAt(i)) | 0; }
  return Math.abs(h);
}

// Skin tone palette
const SKIN_TONES = ['#FFEEDD', '#F5D5B8', '#DEB896', '#C4956A', '#A67B5B', '#8D6346'];

// Hair style generators - return SVG path data relative to head center
const HAIR_GENERATORS = [
  // 0: Spiky short
  (cx: number, r: number, col: string) => `M${cx-r} ${16} L${cx-r+2} ${8} L${cx-r+5} ${12} L${cx-r+7} ${6} L${cx} ${10} L${cx+r-7} ${5} L${cx+r-5} ${11} L${cx+r-2} ${7} L${cx+r} ${16} Z`,
  // 1: Long flowing
  (cx: number, r: number, col: string) => `M${cx-r} ${16} Q${cx-r-3} ${10} ${cx-r+2} ${6} L${cx} ${4} L${cx+r-2} ${6} Q${cx+r+3} ${10} ${cx+r} ${16} L${cx+r+2} ${30} Q${cx+r} ${35} ${cx+r-3} ${32} L${cx+r} ${16} Z`,
  // 2: Twin tails
  (cx: number, r: number, col: string) => `M${cx-r} ${16} L${cx-r+3} ${8} L${cx} ${10} L${cx+r-3} ${8} L${cx+r} ${16} Z M${cx-r-1} ${17} L${cx-r-4} ${35} L${cx-r+1} ${33} Z M${cx+r+1} ${17} L${cx+r+4} ${35} L${cx+r-1} ${33} Z`,
  // 3: Ponytail
  (cx: number, r: number, col: string) => `M${cx-r} ${16} L${cx-r+4} ${9} L${cx} ${7} L${cx+r-4} ${9} L${cx+r} ${16} Z M${cx+r-2} ${14} Q${cx+r+5} ${16} ${cx+r+3} ${34} L${cx+r} ${30} Z`,
  // 4: Short bob
  (cx: number, r: number, col: string) => `M${cx-r-1} ${16} Q${cx-r} ${7} ${cx} ${6} Q${cx+r} ${7} ${cx+r+1} ${16} L${cx+r+1} ${22} Q${cx+r} ${24} ${cx+r-2} ${23} L${cx+r} ${16} L${cx-r} ${16} L${cx-r-2} ${23} Q${cx-r} ${24} ${cx-r-1} ${22} Z`,
  // 5: Mohawk/punk
  (cx: number, r: number, col: string) => `M${cx-r} ${16} L${cx-3} ${12} L${cx-2} ${2} L${cx} ${0} L${cx+2} ${2} L${cx+3} ${12} L${cx+r} ${16} Z`,
  // 6: Curly
  (cx: number, r: number, col: string) => `M${cx-r} ${16} Q${cx-r-2} ${12} ${cx-r+1} ${9} Q${cx-r+3} ${5} ${cx-2} ${7} Q${cx} ${3} ${cx+2} ${7} Q${cx+r-3} ${5} ${cx+r-1} ${9} Q${cx+r+2} ${12} ${cx+r} ${16} Z`,
  // 7: Samurai topknot
  (cx: number, r: number, col: string) => `M${cx-r} ${16} L${cx-r+3} ${10} L${cx} ${8} L${cx+r-3} ${10} L${cx+r} ${16} Z M${cx-2} ${8} L${cx-1} ${1} Q${cx} ${-1} ${cx+1} ${1} L${cx+2} ${8} Z`,
];

// Element colors with light/dark variants
const ELEM_COLORS: Record<string, { main: string; light: string; dark: string }> = {
  fire:    { main: '#FF5544', light: '#FF8866', dark: '#CC3322' },
  water:   { main: '#4499FF', light: '#66BBFF', dark: '#2266CC' },
  earth:   { main: '#CC9944', light: '#DDBB66', dark: '#AA7722' },
  wind:    { main: '#44DD99', light: '#66FFBB', dark: '#22AA66' },
  thunder: { main: '#FFCC33', light: '#FFDD66', dark: '#CCAA00' },
  light:   { main: '#FFDD88', light: '#FFEEAA', dark: '#CCAA55' },
  shadow:  { main: '#AA55FF', light: '#CC88FF', dark: '#7733CC' },
  dark:    { main: '#AA55FF', light: '#CC88FF', dark: '#7733CC' },
  neutral: { main: '#8899AA', light: '#AABBCC', dark: '#667788' },
};

// Accessory types
const ACCESSORIES = [
  'none', 'headband', 'horns', 'halo', 'crown', 'earring', 'scarf', 'mask',
];

export default function ChibiSprite({ name = '?', element = 'neutral', heroClass = 'DPS', rarity = 1, isEnemy = false, state, scale = 1 }: Props) {
  const hash = useMemo(() => hashStr(name), [name]);
  const ec = ELEM_COLORS[element] || ELEM_COLORS.neutral;

  // Derive unique traits from hash
  const skinIdx = hash % SKIN_TONES.length;
  const hairStyleIdx = (hash >> 3) % HAIR_GENERATORS.length;
  const hairHue = (hash >> 6) % 3; // 0=element color, 1=lighter, 2=darker variant
  const accessoryIdx = (hash >> 9) % ACCESSORIES.length;
  const bodyBuild = (hash >> 12) % 3; // 0=slim, 1=normal, 2=bulky
  const eyeStyle = (hash >> 15) % 4; // different eye shapes

  const skinColor = SKIN_TONES[skinIdx];
  const skinShadow = SKIN_TONES[Math.min(skinIdx + 1, SKIN_TONES.length - 1)];
  const hairColor = hairHue === 0 ? ec.main : hairHue === 1 ? ec.light : ec.dark;
  const accessory = ACCESSORIES[accessoryIdx];

  // Class-based armor
  const armorMain = heroClass === 'Tank' ? '#3355AA' : heroClass === 'Support' ? '#33AA55' : '#AA3344';
  const armorLight = heroClass === 'Tank' ? '#4477CC' : heroClass === 'Support' ? '#44CC66' : '#CC5566';
  const armorDark = heroClass === 'Tank' ? '#224488' : heroClass === 'Support' ? '#228844' : '#882233';

  // Body dimensions based on build
  const bodyW = bodyBuild === 0 ? 14 : bodyBuild === 1 ? 16 : 18;
  const bodyH = bodyBuild === 0 ? 18 : bodyBuild === 1 ? 20 : 22;
  const headR = bodyBuild === 2 ? 11 : 12;

  // Animation values
  const bodyY = useSharedValue(0);
  const bodyRot = useSharedValue(0);
  const transX = useSharedValue(0);
  const spriteOp = useSharedValue(1);
  const flashOp = useSharedValue(0);
  const auraOp = useSharedValue(rarity >= 5 ? 0.3 : 0.15);
  const auraSc = useSharedValue(1);

  // Idle
  useEffect(() => {
    if (state === 'dead') return;
    bodyY.value = withRepeat(withSequence(
      withTiming(-2.5, { duration: 900, easing: Easing.inOut(Easing.ease) }),
      withTiming(2.5, { duration: 900, easing: Easing.inOut(Easing.ease) }),
    ), -1, true);
    auraSc.value = withRepeat(withSequence(
      withTiming(1.15, { duration: 1500 }),
      withTiming(1, { duration: 1500 }),
    ), -1, true);
    auraOp.value = withRepeat(withSequence(
      withTiming(rarity >= 5 ? 0.5 : 0.25, { duration: 1200 }),
      withTiming(rarity >= 5 ? 0.15 : 0.05, { duration: 1200 }),
    ), -1, true);
  }, [state !== 'dead', rarity]);

  // State animations
  useEffect(() => {
    const dir = isEnemy ? -1 : 1;
    switch (state) {
      case 'attack':
        transX.value = withSequence(
          withTiming(dir * 18, { duration: 120 }),
          withTiming(dir * 22, { duration: 50 }),
          withTiming(0, { duration: 200 }),
        );
        bodyRot.value = withSequence(
          withTiming(dir * -8, { duration: 100 }),
          withTiming(dir * 4, { duration: 80 }),
          withTiming(0, { duration: 150 }),
        );
        break;
      case 'hit':
        transX.value = withSequence(
          withTiming(-dir * 10, { duration: 60 }),
          withTiming(-dir * 6, { duration: 40 }),
          withTiming(0, { duration: 200 }),
        );
        flashOp.value = withSequence(
          withTiming(0.7, { duration: 50 }),
          withTiming(0, { duration: 200 }),
        );
        bodyRot.value = withSequence(
          withTiming(-dir * 10, { duration: 60 }),
          withTiming(0, { duration: 200 }),
        );
        break;
      case 'skill':
      case 'ultimate':
        auraOp.value = withSequence(
          withTiming(0.8, { duration: 150 }),
          withDelay(400, withTiming(rarity >= 5 ? 0.3 : 0.15, { duration: 300 })),
        );
        auraSc.value = withSequence(
          withTiming(1.5, { duration: 200 }),
          withTiming(1, { duration: 300 }),
        );
        transX.value = withSequence(
          withTiming(dir * 14, { duration: 150 }),
          withTiming(0, { duration: 250 }),
        );
        bodyY.value = withSequence(
          withTiming(-6, { duration: 150 }),
          withTiming(0, { duration: 250 }),
        );
        break;
      case 'heal':
        auraOp.value = withSequence(
          withTiming(0.6, { duration: 300 }),
          withTiming(rarity >= 5 ? 0.3 : 0.15, { duration: 500 }),
        );
        bodyY.value = withSequence(
          withTiming(-4, { duration: 300 }),
          withTiming(0, { duration: 300 }),
        );
        break;
      case 'dodge':
        transX.value = withSequence(
          withTiming(-dir * 22, { duration: 100 }),
          withDelay(150, withTiming(0, { duration: 200 })),
        );
        break;
      case 'dead':
        cancelAnimation(bodyY);
        cancelAnimation(auraSc);
        cancelAnimation(auraOp);
        bodyRot.value = withTiming(isEnemy ? -75 : 75, { duration: 500 });
        spriteOp.value = withTiming(0.3, { duration: 600 });
        bodyY.value = withTiming(12, { duration: 500 });
        auraOp.value = withTiming(0, { duration: 300 });
        break;
    }
  }, [state]);

  const wrapStyle = useAnimatedStyle(() => ({
    transform: [
      { translateX: transX.value },
      { translateY: bodyY.value },
      { rotate: `${bodyRot.value}deg` },
    ],
    opacity: spriteOp.value,
  }));
  const auraStyle = useAnimatedStyle(() => ({
    opacity: auraOp.value,
    transform: [{ scale: auraSc.value }],
  }));
  const flashStyle = useAnimatedStyle(() => ({ opacity: flashOp.value }));

  const W = 56;
  const H = 72;
  const cx = W / 2;
  const flip = isEnemy ? -1 : 1;
  const headCy = 18;
  const bodyCy = headCy + headR + bodyH / 2 - 2;
  const legTop = bodyCy + bodyH / 2 - 2;

  // Generate hair path
  const hairGen = HAIR_GENERATORS[hairStyleIdx];
  const hairPath = hairGen(cx, headR, hairColor);

  // Eye sizes based on style
  const eyeRx = eyeStyle === 0 ? 2.2 : eyeStyle === 1 ? 2.5 : eyeStyle === 2 ? 1.8 : 2;
  const eyeRy = eyeStyle === 0 ? 2.5 : eyeStyle === 1 ? 2 : eyeStyle === 2 ? 2.8 : 2.2;

  return (
    <View style={[styles.wrap, { transform: [{ scaleX: flip }, { scale }] }]}>
      {/* Aura */}
      <Animated.View style={[styles.aura, { backgroundColor: ec.main }, auraStyle]} />
      {/* Hit flash */}
      <Animated.View style={[styles.flash, flashStyle]} />

      <Animated.View style={wrapStyle}>
        <Svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
          <Defs>
            <RadialGradient id={`skin_${hash}`} cx="50%" cy="35%" r="65%">
              <Stop offset="0%" stopColor={skinColor} />
              <Stop offset="100%" stopColor={skinShadow} />
            </RadialGradient>
            <RadialGradient id={`armor_${hash}`} cx="50%" cy="25%" r="75%">
              <Stop offset="0%" stopColor={armorLight} />
              <Stop offset="100%" stopColor={armorMain} />
            </RadialGradient>
          </Defs>

          {/* === LEGS === */}
          <Rect x={cx - 5} y={legTop} width={4} height={11} rx={2} fill={armorDark} />
          <Rect x={cx + 1} y={legTop} width={4} height={11} rx={2} fill={armorDark} />
          {/* Boots */}
          <Rect x={cx - 6} y={legTop + 8} width={6} height={5} rx={2} fill="#443322" />
          <Rect x={cx} y={legTop + 8} width={6} height={5} rx={2} fill="#443322" />
          {/* Boot accents */}
          <Rect x={cx - 5} y={legTop + 8} width={4} height={1.5} rx={0.5} fill={ec.dark} opacity={0.5} />
          <Rect x={cx + 1} y={legTop + 8} width={4} height={1.5} rx={0.5} fill={ec.dark} opacity={0.5} />

          {/* === BODY === */}
          <Rect x={cx - bodyW / 2} y={bodyCy - bodyH / 2} width={bodyW} height={bodyH} rx={4} fill={`url(#armor_${hash})`} />
          {/* Chest plate detail */}
          <Path d={`M${cx - 3} ${bodyCy - bodyH / 2 + 3} L${cx} ${bodyCy - bodyH / 2 + 7} L${cx + 3} ${bodyCy - bodyH / 2 + 3}`} fill="none" stroke={armorLight} strokeWidth={1} opacity={0.6} />
          {/* Belt */}
          <Rect x={cx - bodyW / 2 + 1} y={bodyCy + bodyH / 2 - 5} width={bodyW - 2} height={3} rx={1} fill="#554433" />
          <Circle cx={cx} cy={bodyCy + bodyH / 2 - 3.5} r={1.8} fill={ec.main} />

          {/* Cape for 4+ star */}
          {rarity >= 4 && (
            <Path d={`M${cx - bodyW / 2 + 1} ${bodyCy - bodyH / 2 + 2} L${cx - bodyW / 2 - 3} ${bodyCy + bodyH / 2 + 8} Q${cx} ${bodyCy + bodyH / 2 + 12} ${cx + bodyW / 2 + 3} ${bodyCy + bodyH / 2 + 8} L${cx + bodyW / 2 - 1} ${bodyCy - bodyH / 2 + 2}`} fill={ec.dark} opacity={0.4} />
          )}

          {/* === LEFT ARM === */}
          <Rect x={cx - bodyW / 2 - 6} y={bodyCy - bodyH / 2 + 2} width={7} height={5} rx={2.5} fill={armorLight} />
          <Circle cx={cx - bodyW / 2 - 6} cy={bodyCy - bodyH / 2 + 4.5} r={2.5} fill={skinColor} />

          {/* === RIGHT ARM + WEAPON === */}
          <Rect x={cx + bodyW / 2 - 1} y={bodyCy - bodyH / 2 + 2} width={7} height={5} rx={2.5} fill={armorLight} />
          <Circle cx={cx + bodyW / 2 + 6} cy={bodyCy - bodyH / 2 + 4.5} r={2.5} fill={skinColor} />

          {/* Weapon */}
          {heroClass === 'DPS' && (
            <G>
              <Rect x={cx + bodyW / 2 + 5} y={bodyCy - bodyH / 2 - 8} width={2.5} height={16} rx={1} fill="#BBCCDD" />
              <Rect x={cx + bodyW / 2 + 3} y={bodyCy - bodyH / 2 + 7} width={7} height={2.5} rx={1} fill="#887766" />
              <Path d={`M${cx + bodyW / 2 + 5} ${bodyCy - bodyH / 2 - 8} L${cx + bodyW / 2 + 6.25} ${bodyCy - bodyH / 2 - 14} L${cx + bodyW / 2 + 7.5} ${bodyCy - bodyH / 2 - 8} Z`} fill="#DDEEFF" />
              <Circle cx={cx + bodyW / 2 + 6.25} cy={bodyCy - bodyH / 2 - 9} r={1} fill={ec.main} opacity={0.7} />
            </G>
          )}
          {heroClass === 'Tank' && (
            <G>
              <Rect x={cx + bodyW / 2 + 3} y={bodyCy - bodyH / 2 - 2} width={12} height={14} rx={3.5} fill="#4466AA" stroke="#6688CC" strokeWidth={1} />
              <Circle cx={cx + bodyW / 2 + 9} cy={bodyCy - bodyH / 2 + 5} r={3} fill={ec.main} opacity={0.5} />
              <Circle cx={cx + bodyW / 2 + 9} cy={bodyCy - bodyH / 2 + 5} r={1.5} fill={ec.light} opacity={0.7} />
            </G>
          )}
          {heroClass === 'Support' && (
            <G>
              <Rect x={cx + bodyW / 2 + 5.5} y={bodyCy - bodyH / 2 - 12} width={2} height={24} rx={1} fill="#886644" />
              <Circle cx={cx + bodyW / 2 + 6.5} cy={bodyCy - bodyH / 2 - 12} r={4} fill={ec.main} opacity={0.6} />
              <Circle cx={cx + bodyW / 2 + 6.5} cy={bodyCy - bodyH / 2 - 12} r={2} fill="#fff" opacity={0.5} />
              <Circle cx={cx + bodyW / 2 + 6.5} cy={bodyCy - bodyH / 2 - 12} r={1} fill={ec.light} />
            </G>
          )}

          {/* === HEAD === */}
          <Circle cx={cx} cy={headCy} r={headR} fill={`url(#skin_${hash})`} />

          {/* Hair */}
          <Path d={hairPath} fill={hairColor} />

          {/* Eyes */}
          <Ellipse cx={cx - 4} cy={headCy + 1} rx={eyeRx} ry={eyeRy} fill="#fff" />
          <Circle cx={cx - 3.5} cy={headCy + 1.5} r={1.5} fill="#222" />
          <Circle cx={cx - 3} cy={headCy + 0.5} r={0.6} fill="#fff" />
          <Ellipse cx={cx + 4} cy={headCy + 1} rx={eyeRx} ry={eyeRy} fill="#fff" />
          <Circle cx={cx + 4.5} cy={headCy + 1.5} r={1.5} fill="#222" />
          <Circle cx={cx + 5} cy={headCy + 0.5} r={0.6} fill="#fff" />

          {/* Eyebrows */}
          <Path d={`M${cx - 6} ${headCy - 2.5} L${cx - 2} ${headCy - 3}`} fill="none" stroke={hairColor} strokeWidth={1.2} opacity={0.7} />
          <Path d={`M${cx + 2} ${headCy - 3} L${cx + 6} ${headCy - 2.5}`} fill="none" stroke={hairColor} strokeWidth={1.2} opacity={0.7} />

          {/* Mouth */}
          <Path d={`M${cx - 2} ${headCy + 5} Q${cx} ${headCy + 7} ${cx + 2} ${headCy + 5}`} fill="none" stroke={skinShadow} strokeWidth={0.8} />

          {/* Blush */}
          <Ellipse cx={cx - 7} cy={headCy + 3} rx={2} ry={1} fill="#FF8888" opacity={0.25} />
          <Ellipse cx={cx + 7} cy={headCy + 3} rx={2} ry={1} fill="#FF8888" opacity={0.25} />

          {/* === ACCESSORIES === */}
          {accessory === 'headband' && (
            <Rect x={cx - headR} y={headCy - 3} width={headR * 2} height={3} rx={1} fill={ec.main} opacity={0.8} />
          )}
          {accessory === 'horns' && (
            <>
              <Path d={`M${cx - 8} ${headCy - 8} L${cx - 6} ${headCy - 14} L${cx - 4} ${headCy - 8}`} fill={ec.dark} />
              <Path d={`M${cx + 4} ${headCy - 8} L${cx + 6} ${headCy - 14} L${cx + 8} ${headCy - 8}`} fill={ec.dark} />
            </>
          )}
          {accessory === 'halo' && (
            <Ellipse cx={cx} cy={headCy - headR - 3} rx={8} ry={2.5} fill="none" stroke="#FFD700" strokeWidth={1.5} opacity={0.7} />
          )}
          {accessory === 'crown' && (
            <Path d={`M${cx - 7} ${headCy - headR + 1} L${cx - 5} ${headCy - headR - 5} L${cx - 2} ${headCy - headR - 1} L${cx} ${headCy - headR - 7} L${cx + 2} ${headCy - headR - 1} L${cx + 5} ${headCy - headR - 5} L${cx + 7} ${headCy - headR + 1} Z`} fill="#FFD700" />
          )}
          {accessory === 'earring' && (
            <Circle cx={cx - headR + 1} cy={headCy + 4} r={1.5} fill="#FFD700" />
          )}
          {accessory === 'scarf' && (
            <Path d={`M${cx - bodyW / 2 - 1} ${headCy + headR - 2} Q${cx} ${headCy + headR + 3} ${cx + bodyW / 2 + 1} ${headCy + headR - 2} L${cx + bodyW / 2 + 4} ${headCy + headR + 8} Q${cx + bodyW / 2 + 2} ${headCy + headR + 10} ${cx + bodyW / 2} ${headCy + headR + 6}`} fill={ec.main} opacity={0.7} />
          )}
          {accessory === 'mask' && (
            <Rect x={cx - 6} y={headCy - 2} width={12} height={5} rx={2} fill="#222" opacity={0.6} />
          )}

          {/* Rarity sparkles */}
          {rarity >= 5 && (
            <>
              <Circle cx={cx - 12} cy={6} r={1.2} fill={ec.light} opacity={0.7} />
              <Circle cx={cx + 12} cy={8} r={1} fill="#FFD700" opacity={0.6} />
              <Circle cx={cx + 9} cy={3} r={1.3} fill={ec.main} opacity={0.5} />
            </>
          )}
          {rarity >= 6 && (
            <>
              <Circle cx={cx - 9} cy={3} r={1.2} fill="#FFD700" opacity={0.8} />
              <Circle cx={cx} cy={1} r={1.5} fill="#FFD700" opacity={0.6} />
              <Circle cx={cx + 5} cy={-1} r={1} fill={ec.light} opacity={0.7} />
            </>
          )}

          {/* Shoulder element badge */}
          <Circle cx={cx - bodyW / 2 - 1} cy={bodyCy - bodyH / 2 + 4} r={3} fill={ec.main} opacity={0.5} />
        </Svg>
      </Animated.View>

      {/* Ground shadow */}
      <View style={[styles.shadow, { opacity: state === 'dead' ? 0.1 : 0.35 }]} />
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    width: 60,
    height: 86,
    alignItems: 'center',
    justifyContent: 'flex-end',
  },
  aura: {
    position: 'absolute',
    width: 48,
    height: 48,
    borderRadius: 24,
    top: 2,
  },
  flash: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: '#FF4444',
    borderRadius: 8,
  },
  shadow: {
    width: 32,
    height: 6,
    borderRadius: 16,
    backgroundColor: '#000',
    marginTop: -3,
  },
});
