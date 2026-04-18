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

  const displayH = size || frameHeight;
  const displayW = size ? (size * frameWidth / frameHeight) : frameWidth;
  const scale = displayH / frameHeight;
  const sheetWidth = frameWidth * frames;

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

    const ms = Math.round(1000 / fps);
    intervalRef.current = setInterval(() => {
      const next = frameRef.current + 1;
      if (next >= frames) {
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
  }, [source, frames, fps, loop]);

  const offsetX = -(currentFrame * displayW);

  return (
    <View style={[styles.container, { width: displayW, height: displayH, overflow: 'hidden' }]}>
      <Image
        source={source}
        style={{
          width: sheetWidth * scale,
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
