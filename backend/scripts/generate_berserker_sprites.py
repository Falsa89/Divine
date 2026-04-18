"""
Generate Berserker sprite sheets using OpenAI image generation.
One sprite sheet per animation.
"""
import os
import base64
import asyncio
from emergentintegrations.llm.openai.image_generation import OpenAIImageGeneration

API_KEY = "sk-emergent-f85De8c8b700196Df0"
OUTPUT_DIR = "/app/frontend/assets/heroes/berserker_sprites"

os.makedirs(OUTPUT_DIR, exist_ok=True)

CHARACTER_DESC = """
Anime-style female berserker warrior from Norse mythology.
Silver-white hair with red highlights, fierce determined expression.
Red crimson bodysuit with silver-grey partial plate armor (shoulder pauldrons, bracers, shin guards).
Wielding a heavy one-handed battle axe.
Athletic muscular build, medium height.
Style: HD anime game character, clean lines, vibrant colors.
Direction: facing RIGHT.
Background: TRANSPARENT (plain white/empty background).
Frame size: 256x256 pixels per frame.
IMPORTANT: Keep proportions, colors, and design IDENTICAL across ALL frames.
"""

ANIMATIONS = {
    "idle": {
        "frames": 6,
        "prompt": f"""Create a horizontal sprite sheet with exactly 6 frames arranged left to right in a single row.
{CHARACTER_DESC}
Animation: IDLE breathing cycle.
Frame 1: Standing relaxed, axe held at right side pointing down, weight on left foot.
Frame 2: Shoulders rise slightly (1-2px up), chest expands with breath.
Frame 3: Same as 2 but left hand clenches into fist, slight forward lean.
Frame 4: Shoulders lower back, chest contracts, axe sways back slightly.
Frame 5: Returns to frame 1 position, left hand relaxes.
Frame 6: Grip on axe adjusts slightly (micro rotation), then back to frame 1.
Movement is VERY subtle. Character barely moves. Just breathing and grip adjustment.
All 6 frames must be side by side in one horizontal row. Each frame 256x256px.""",
    },
    "attack": {
        "frames": 8,
        "prompt": f"""Create a horizontal sprite sheet with exactly 8 frames arranged left to right in a single row.
{CHARACTER_DESC}
Animation: DIAGONAL AXE SLASH from upper-right to lower-left.
Frame 1: Right foot steps back, axe begins to rise, torso rotates right.
Frame 2: Axe fully raised above right shoulder, body wound up to right, left shoulder forward. Maximum tension.
Frame 3: Torso begins counter-rotation, axe at 1 o'clock position, left foot plants forward.
Frame 4: Axe mid-swing at 10 o'clock, arm fully extended, maximum speed - add subtle motion blur on blade (3-4px steel trail).
Frame 5: IMPACT point, axe at 8 o'clock, front foot planted firmly, small dust cloud at feet (2-3 grey pixels).
Frame 6: Follow-through, axe continues to 7 o'clock by inertia, body leaning forward, knees bent.
Frame 7: Arm pulls axe up to stop momentum, torso straightens, slight weight bounce.
Frame 8: Transition back to idle pose, axe returns to side.
The WEIGHT of the heavy axe must be visible in the slow wind-up and dragged follow-through.
All 8 frames side by side in one row. Each frame 256x256px.""",
    },
    "skill": {
        "frames": 10,
        "prompt": f"""Create a horizontal sprite sheet with exactly 10 frames arranged left to right in a single row.
{CHARACTER_DESC}
Animation: BERSERKER FURY activation.
Frame 1: From idle, right arm raises axe.
Frame 2: Axe is PLANTED into the ground in front. Small debris/dust at impact point.
Frame 3: Both hands release axe. Arms spread to sides. Torso straightens.
Frame 4: Fists clench. Arms bend bringing fists to chest level. Posture lowers slightly.
Frame 5: Mouth opens in a war cry. Head tilts back slightly. Hair begins to lift (wind from below, 2-3px rise). Arm muscles tense visibly.
Frame 6: PEAK fury - hair fully lifted. Very subtle heat haze distortion lines around torso (1px wavy semi-transparent lines, 20% opacity). Tiny screen-shake feel.
Frame 7: Cry ends. Hair begins to fall. Heat haze persists. Hands lower toward axe.
Frame 8: Right hand GRABS axe handle with a yank. Small dust cloud from ground where axe was planted.
Frame 9: Axe extracted forcefully. Body crouches lower - more aggressive stance, legs wider.
Frame 10: POWERED-UP idle: leaning forward, axe held higher (ready to strike, not dangling). More intense gaze. Heat haze dissolves.
NO flames on shoulders. NO magic aura. Only heat haze distortion and body language show the power.
All 10 frames side by side in one row. Each frame 256x256px.""",
    },
    "hit": {
        "frames": 5,
        "prompt": f"""Create a horizontal sprite sheet with exactly 5 frames arranged left to right in a single row.
{CHARACTER_DESC}
Animation: TAKING A HIT (struck on left shoulder/chest).
Frame 1: IMPACT - body jerks backward 3-4px. Head snaps right. White flash circle on impact point (4-5px, 60% opacity). This is the hit frame.
Frame 2: Right foot slides back 2px to stabilize. Left arm raises instinctively for protection. Axe in right hand points downward.
Frame 3: Weight recenters. Eyes lock back on enemy. Teeth visibly clench. Grip tightens on axe.
Frame 4: Aggressive forward snap - torso leans forward as if to say 'is that all?' Right foot returns to position.
Frame 5: Smooth transition back toward idle. Grip on axe is firmer than before.
The reaction is NOT pain - it is IRRITATION and ANGER. She looks more dangerous after being hit.
All 5 frames side by side in one row. Each frame 256x256px.""",
    },
    "death": {
        "frames": 10,
        "prompt": f"""Create a horizontal sprite sheet with exactly 10 frames arranged left to right in a single row.
{CHARACTER_DESC}
Animation: DEATH sequence - warrior falls.
Frame 1: Body sways left. Knees bend slightly. Axe still held but arm trembles (1px alternating shift).
Frame 2: Right arm tries to raise axe for one last strike. The effort is visible - arm rises SLOWLY, not with attack speed.
Frame 3: Arm fails to complete the swing. Axe reaches only 2 o'clock and stops. Fingers begin to open.
Frame 4: Fingers fully open. Axe SLIPS from hand and begins to fall. Arm drops to side.
Frame 5: Axe hits ground with small 1px bounce. Tiny dust cloud. Body still standing but staggering.
Frame 6: Knees buckle. Torso tilts forward. Arms hang limp at sides.
Frame 7: Character falls to knees. Small dust at knee impact point (2px).
Frame 8: Torso leans sideways to the left. Hair falls heavily over face.
Frame 9: Body collapses fully onto left side. Axe visible on ground 10-15px away.
Frame 10: Completely still. Lying on side. Overall sprite slightly darkened (10-15% darker). No movement.
Death is SILENT and HEAVY. No screaming, no dramatic effects. Just a warrior who fought until the very end.
All 10 frames side by side in one row. Each frame 256x256px.""",
    },
}


async def generate_sprite(name: str, config: dict):
    print(f"\n  Generating {name} ({config['frames']} frames)...")
    gen = OpenAIImageGeneration(api_key=API_KEY)
    try:
        results = await gen.generate_images(
            prompt=config["prompt"],
            model="gpt-image-1",
            number_of_images=1,
            quality="high",
        )
        if results and len(results) > 0:
            img_data = results[0]
        else:
            print(f"  No results returned for {name}")
            return False

        output_path = os.path.join(OUTPUT_DIR, f"{name}.png")
        with open(output_path, "wb") as f:
            f.write(img_data)
        size_kb = len(img_data) / 1024
        print(f"  Saved: {output_path} ({size_kb:.1f} KB)")
        return True
    except Exception as e:
        print(f"  ERROR generating {name}: {e}")
        return False


async def main():
    print("=== Berserker Sprite Sheet Generator ===")
    print(f"Output: {OUTPUT_DIR}")
    results = {}
    for name, config in ANIMATIONS.items():
        ok = await generate_sprite(name, config)
        results[name] = ok

    print("\n=== Results ===")
    for name, ok in results.items():
        status = "OK" if ok else "FAILED"
        frames = ANIMATIONS[name]["frames"]
        print(f"  {name}: {status} ({frames} frames)")

    # Write metadata
    import json
    metadata = {}
    for name, config in ANIMATIONS.items():
        metadata[name] = {
            "file": f"{name}.png",
            "frameWidth": 256,
            "frameHeight": 256,
            "frames": config["frames"],
            "fps": 12 if name == "idle" else 10 if name in ("attack", "skill", "hit") else 8,
            "loop": name == "idle",
        }
    meta_path = os.path.join(OUTPUT_DIR, "metadata.json")
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"\n  Metadata: {meta_path}")


if __name__ == "__main__":
    asyncio.run(main())
