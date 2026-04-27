import React, { useEffect, useRef, useState, useCallback } from 'react';
import { View, Image, StyleSheet } from 'react-native';

interface AnimatedSpriteProps {
  /** require() or { uri } source of the horizontal sprite sheet */
  source: any;
  /** Width of a single frame in pixels */
  frameWidth: number;
  /** Height of a single frame in pixels */
  frameHeight: number;
  /** Total number of frames in the sheet */
  frames: number;
  /** Frames per second */
  fps?: number;
  /** Loop continuously */
  loop?: boolean;
  /** Display size (scales the frame) */
  size?: number;
  /** Called when a non-looping animation finishes */
  onComplete?: () => void;
}

/**
 * AnimatedSprite - Plays a horizontal sprite sheet animation.
 *
 * Uses overflow:hidden + translateX to show one frame at a time.
 * Lightweight: no external libraries, just setInterval + Image.
 *
 * Render stabilization:
 *  - Safe fallbacks for invalid metadata (frames/frameWidth/frameHeight ≤ 0)
 *    with console.warn logging instead of silent NaN/blank renders.
 *  - Integer-snapped displayW + exact `displayW * frames` image width
 *    prevents sub-pixel rounding bleed-through of neighboring frames.
 */
export default function AnimatedSprite({
  source,
  frameWidth,
  frameHeight,
  frames,
  fps = 10,
  loop = true,
  size,
  onComplete,
}: AnimatedSpriteProps) {
  const [currentFrame, setCurrentFrame] = useState(0);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const frameRef = useRef(0);

  // SAFE METADATA — fall back to safe values + warn so a broken atlas/frameset
  // never produces NaN scale, divide-by-zero, or infinite-frame setInterval.
  const safeFrames = frames > 0 ? frames : 1;
  const safeFW = frameWidth > 0 ? frameWidth : 1;
  const safeFH = frameHeight > 0 ? frameHeight : 1;
  if (typeof __DEV__ !== 'undefined' && __DEV__) {
    if (frames <= 0 || frameWidth <= 0 || frameHeight <= 0) {
      // eslint-disable-next-line no-console
      console.warn(
        '[AnimatedSprite] invalid metadata',
        { frames, frameWidth, frameHeight },
        '→ using safe fallbacks',
      );
    }
  }

  // Geometry — integer-snapped to prevent sub-pixel bleed.
  const displayH = Math.round(size || safeFH);
  const displayW = Math.round(size ? (size * safeFW / safeFH) : safeFW);
  // Image total width is EXACTLY displayW * safeFrames (not derived via scale)
  // → each frame is pixel-perfect aligned; no rounding mismatch with offset.
  const imageWidth = displayW * safeFrames;

  const stop = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  useEffect(() => {
    frameRef.current = 0;
    setCurrentFrame(0);
    stop();

    const ms = Math.round(1000 / Math.max(1, fps));
    intervalRef.current = setInterval(() => {
      const next = frameRef.current + 1;
      if (next >= safeFrames) {
        if (loop) {
          frameRef.current = 0;
          setCurrentFrame(0);
        } else {
          stop();
          onComplete?.();
        }
      } else {
        frameRef.current = next;
        setCurrentFrame(next);
      }
    }, ms);

    return stop;
  }, [source, safeFrames, fps, loop]);

  const offsetX = -(currentFrame * displayW);

  return (
    <View style={[styles.container, { width: displayW, height: displayH, overflow: 'hidden' }]}>
      <Image
        source={source}
        style={{
          width: imageWidth,
          height: displayH,
          transform: [{ translateX: offsetX }],
        }}
        resizeMode="stretch"
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    overflow: 'hidden',
    backgroundColor: 'transparent',
  },
});
