"""
Generate ANIMATION-SAFE helper layers for Greek Hoplite rig.

L'idea: creare "underpaint/fill" layers che stanno DIETRO ai limb rotanti
(spear_arm, shield_arm, head_helmet, skirt) e coprono le aree che verrebbero
esposte quando il limb ruota via dal corpo.

I fill NON ruotano (restano ancorati al corpo), quindi quando un braccio
ruota di 5-15°, il disco di fill resta sotto e copre il vuoto.

Colori scelti dal sampling dell'audit:
  - spear shoulder area: RGB(135,110,68)  brass armor
  - shield shoulder:     RGB(123,89,55)   dark brass
  - neck:                RGB(99,73,55)    skin shadow
  - hip/waist:           RGB(78,45,38)    underskirt red-brown
"""
import os
import numpy as np
from PIL import Image, ImageFilter, ImageDraw

SRC = '/app/frontend/assets/heroes/greek_hoplite/rig'
OUT = '/app/frontend/assets/heroes/greek_hoplite/rig_safe'
os.makedirs(OUT, exist_ok=True)

BASE = 1024


def soft_disc(size, cx, cy, rx, ry, color_rgb, peak_alpha=220, feather=0.6):
    """Crea un disco ellittico a bordi sfumati (RGBA 1024x1024).

    feather = 0.6 significa che il 60% del raggio è feathered (alpha → 0),
    il 40% centrale resta al peak_alpha.
    """
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    arr = np.zeros((size, size, 4), dtype=np.uint8)
    y, x = np.ogrid[:size, :size]
    # normalized radial distance (1.0 = on the edge)
    nd = np.sqrt(((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2)
    # feather: alpha 1.0 inside (1-feather) band, linear fade to 0 at nd=1.0
    inner = 1.0 - feather
    mask = np.clip(1.0 - (nd - inner) / feather, 0.0, 1.0)
    mask[nd < inner] = 1.0
    mask[nd > 1.0] = 0.0

    arr[..., 0] = color_rgb[0]
    arr[..., 1] = color_rgb[1]
    arr[..., 2] = color_rgb[2]
    arr[..., 3] = (mask * peak_alpha).astype(np.uint8)
    return Image.fromarray(arr, 'RGBA')


def generate_all():
    artifacts = []

    # FILOSOFIA v2:
    # Ridimensionati e ridotti in opacità. Colore quasi-nero → appaiono come
    # ombre/shading del corpo in idle (completamente blend-in nel torso),
    # ma riempiono il vuoto dietro la spalla quando il limb ruota.
    # Posizioni vincolate alle aree DI FATTO coperte dai limb (vedi audit).

    # 1. SHOULDER SPEAR FILL — pivot spear_arm (570, 390)
    # Arm opaque nella row y=390: x=81..609. Fill deve restare < x=609.
    # Piccolo disco verticale sotto la spalla, low opacity.
    spear_fill = soft_disc(
        BASE, cx=560, cy=415, rx=38, ry=62,
        color_rgb=(55, 38, 22), peak_alpha=140, feather=0.75,
    )
    out1 = os.path.join(OUT, 'shoulder_spear_fill.png')
    spear_fill.save(out1, optimize=True)
    artifacts.append(('shoulder_spear_fill.png', out1))

    # 2. SHOULDER SHIELD FILL — pivot shield_arm (700, 440)
    # Shield opaque row y=440: x=686..992. Fill deve stare sopra x=686.
    shield_fill = soft_disc(
        BASE, cx=720, cy=450, rx=42, ry=65,
        color_rgb=(50, 32, 18), peak_alpha=140, feather=0.75,
    )
    out2 = os.path.join(OUT, 'shoulder_shield_fill.png')
    shield_fill.save(out2, optimize=True)
    artifacts.append(('shoulder_shield_fill.png', out2))

    # 3. NECK FILL — piccolo disco scuro sotto la testa (pivot head 610, 245).
    # Testa opaca y=130-309. Collo tra y=260 e y=340 (tra helmet e torso).
    neck_fill = soft_disc(
        BASE, cx=625, cy=300, rx=28, ry=38,
        color_rgb=(45, 30, 22), peak_alpha=155, feather=0.7,
    )
    out3 = os.path.join(OUT, 'neck_fill.png')
    neck_fill.save(out3, optimize=True)
    artifacts.append(('neck_fill.png', out3))

    # 4. HIP / WAIST BRIDGE — piccola striscia a cavallo di torso(end 544)+skirt(start 512)
    # Molto bassa opacità, colore scuro di sotto-gonna. Larga ma sottile.
    hip_fill = soft_disc(
        BASE, cx=650, cy=540, rx=70, ry=22,
        color_rgb=(45, 22, 18), peak_alpha=150, feather=0.7,
    )
    out4 = os.path.join(OUT, 'hip_fill.png')
    hip_fill.save(out4, optimize=True)
    artifacts.append(('hip_fill.png', out4))

    # 5. UNDER-ARM FILL SPEAR — chiude il gap ascella tra torso e spear arm.
    # Torso bbox x 593-764, spear arm termina a x=609 verso dx. Overlap 593-609.
    # Disco minuscolo posto in quel tight overlap.
    under_arm_spear = soft_disc(
        BASE, cx=595, cy=440, rx=30, ry=42,
        color_rgb=(48, 30, 18), peak_alpha=130, feather=0.8,
    )
    out5 = os.path.join(OUT, 'under_arm_spear.png')
    under_arm_spear.save(out5, optimize=True)
    artifacts.append(('under_arm_spear.png', out5))

    return artifacts


if __name__ == '__main__':
    arts = generate_all()
    print(f"Generated {len(arts)} animation-safe helpers:")
    for name, path in arts:
        sz = os.path.getsize(path)
        print(f"  {name:<28s} {sz:>6d} bytes  → {path}")
