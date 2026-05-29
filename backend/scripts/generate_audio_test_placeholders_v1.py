#!/usr/bin/env python3
"""
PROJECT_AUDIO_PLACEHOLDER_FOUNDATION - Track C generator.

Genera 12 file WAV TEST placeholder mono 16-bit a 16kHz procedurali
usando SOLO Python stdlib (wave + struct + math). Nessuna libreria esterna.
Nessun audio finale, nessun copyright issue, nessun voice acting.

Ogni file e' ~10-100KB. Tutti chiaramente "placeholder" all'udito
(toni puri / sweep / chirp). Devono essere sostituiti prima del release.
"""
import math
import struct
import wave
from pathlib import Path

OUT_DIR = Path('/app/frontend/assets/audio/test_placeholders')
OUT_DIR.mkdir(parents=True, exist_ok=True)

SR = 16000  # 16kHz sample rate, mono, 16-bit
MAX_AMP = 0.4  # global safety amplitude (avoid hearing damage on default volume)


def write_wav(name: str, samples: list[float]) -> Path:
    """Save samples (-1..1 floats) as 16-bit PCM mono WAV."""
    p = OUT_DIR / name
    with wave.open(str(p), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        frames = b''.join(
            struct.pack('<h', max(-32767, min(32767, int(s * 32767))))
            for s in samples
        )
        w.writeframes(frames)
    return p


def envelope(t: float, dur: float, attack=0.005, release=0.05) -> float:
    """Simple AR envelope to avoid clicks."""
    if t < attack:
        return t / attack
    if t > dur - release:
        return max(0.0, (dur - t) / release)
    return 1.0


def tone(freq: float, dur_ms: int, amp: float = MAX_AMP) -> list[float]:
    n = int(SR * dur_ms / 1000)
    return [
        amp * envelope(i / SR, dur_ms / 1000) * math.sin(2 * math.pi * freq * i / SR)
        for i in range(n)
    ]


def chirp(f0: float, f1: float, dur_ms: int, amp: float = MAX_AMP) -> list[float]:
    n = int(SR * dur_ms / 1000)
    out = []
    for i in range(n):
        t = i / SR
        dur = dur_ms / 1000
        f = f0 + (f1 - f0) * (t / dur)
        out.append(amp * envelope(t, dur) * math.sin(2 * math.pi * f * t))
    return out


def click(dur_ms: int, freq: float = 1200, amp: float = MAX_AMP) -> list[float]:
    n = int(SR * dur_ms / 1000)
    out = []
    for i in range(n):
        t = i / SR
        # exponential decay click
        decay = math.exp(-25 * t)
        out.append(amp * decay * math.sin(2 * math.pi * freq * i / SR))
    return out


def noise_pulse(dur_ms: int, amp: float = MAX_AMP) -> list[float]:
    """Simple deterministic pseudo-noise based on bit manipulation."""
    n = int(SR * dur_ms / 1000)
    out = []
    state = 0xACE1
    for i in range(n):
        # LFSR for deterministic pseudo-noise
        bit = ((state >> 0) ^ (state >> 2) ^ (state >> 3) ^ (state >> 5)) & 1
        state = ((state >> 1) | (bit << 15)) & 0xFFFF
        sample = (state / 32768.0 - 1.0)
        t = i / SR
        dur = dur_ms / 1000
        out.append(amp * envelope(t, dur) * sample * 0.5)
    return out


def mix(*tracks):
    """Mix multiple sample lists to same length (max length)."""
    n = max(len(t) for t in tracks)
    out = [0.0] * n
    for t in tracks:
        for i, s in enumerate(t):
            out[i] += s
    # normalize if needed
    peak = max(abs(s) for s in out) or 1.0
    if peak > 0.95:
        out = [s * (0.85 / peak) for s in out]
    return out


def fanfare(dur_ms: int) -> list[float]:
    # 3-note ascending arpeggio (C4-E4-G4)
    third = dur_ms // 3
    return tone(261.63, third) + tone(329.63, third) + tone(392.00, dur_ms - 2 * third)


def victory_stinger(dur_ms: int) -> list[float]:
    quarter = dur_ms // 4
    return tone(523.25, quarter) + tone(659.25, quarter) + tone(783.99, quarter) + tone(1046.50, dur_ms - 3 * quarter)


def defeat_stinger(dur_ms: int) -> list[float]:
    half = dur_ms // 2
    return tone(440.00, half) + tone(220.00, dur_ms - half)


def ambient_loop(dur_ms: int) -> list[float]:
    # Soft drone: low sine + slight beat with detuned partner
    n = int(SR * dur_ms / 1000)
    out = []
    for i in range(n):
        t = i / SR
        s = 0.18 * math.sin(2 * math.pi * 110.0 * t) + 0.12 * math.sin(2 * math.pi * 110.7 * t)
        # cross-fade for loopability
        loop_env = 1.0
        fade = 0.1
        if t < fade:
            loop_env = t / fade
        elif t > (dur_ms / 1000 - fade):
            loop_env = (dur_ms / 1000 - t) / fade
        out.append(loop_env * s)
    return out


SPECS = [
    ('test_ui_click.wav',                click(50, 1500)),
    ('test_ui_confirm.wav',              tone(880, 120)),
    ('test_ui_back_cancel.wav',          chirp(660, 330, 100)),
    ('test_ui_error_locked.wav',         mix(tone(220, 300), tone(233, 300))),  # dissonant 2nd
    ('test_reward_basic.wav',            chirp(440, 880, 500)),
    ('test_notification_basic.wav',      mix(tone(987.77, 250), tone(1318.51, 250))),  # B5 + E6
    ('test_mode_enter.wav',              chirp(220, 880, 400)),
    ('test_battle_start.wav',            fanfare(700)),
    ('test_battle_hit_soft.wav',         noise_pulse(80)),
    ('test_battle_victory_stinger.wav',  victory_stinger(1500)),
    ('test_battle_defeat_stinger.wav',   defeat_stinger(1500)),
    ('test_ambient_placeholder_loop.wav', ambient_loop(4000)),
]


def main():
    print(f'Generating {len(SPECS)} placeholder WAV files in {OUT_DIR}')
    total_size = 0
    for name, samples in SPECS:
        p = write_wav(name, samples)
        size = p.stat().st_size
        total_size += size
        print(f'  - {name}: {size} bytes ({len(samples)} samples)')
    print(f'Total: {total_size} bytes ({total_size/1024:.1f} KiB)')


if __name__ == '__main__':
    main()
