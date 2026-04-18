"""Generate Greek Hoplite sprite frames - one sheet per animation, then split."""
import asyncio, os
from PIL import Image
from emergentintegrations.llm.openai.image_generation import OpenAIImageGeneration

API_KEY = "sk-emergent-f85De8c8b700196Df0"
BASE = "/app/frontend/assets/heroes/greek_hoplite"

CHAR = """Anime-style female Greek hoplite warrior. Long dark brown-black wavy hair flowing past shoulders. Bright green eyes. Warm confident smile. Bronze Corinthian helmet with tall brown horsehair crest. Bronze breastplate (cuirass) over chest. Red-crimson layered battle skirt (pteruges) with bronze plate accents on the belt. Bronze shoulder pauldrons and arm bracers. Bronze shin guards (greaves). Brown leather gladiator sandals with straps up the calves. Carrying a large round bronze shield (aspis) with concentric circle engravings in left hand. Long bronze-tipped spear in right hand. Athletic build. Facing RIGHT. White/empty background. 256x256px per frame. HD anime game quality."""

ANIMS = {
    "idle": {
        "frames": 6,
        "prompt": f"""Horizontal sprite sheet, exactly 6 frames left to right, single row.
{CHAR}
IDLE BREATHING - very subtle, disciplined soldier standing guard.
Frame 1: Standing guard. Shield covers torso, top edge at eye level. Spear vertical in right hand, butt on ground. Feet shoulder-width. Steady gaze forward between helmet and shield edge.
Frame 2: Shoulders rise 1px with breath. Shield rises 1px. Spear unchanged (resting on shoulder). Helmet crest sways 1px right.
Frame 3: Same as 2. Right hand tightens grip on spear shaft. Right foot adjusts 1px outward.
Frame 4: Shoulders lower. Shield descends 1px. Spear sways 1px left from shoulder movement.
Frame 5: Nearly identical to frame 1. Weight shifts slightly to left leg.
Frame 6: Shield rotates 1-2 degrees clockwise (forearm comfort). Spear returns vertical. Loops to frame 1.
VERY minimal movement. Like a statue that breathes.""",
    },
    "attack": {
        "frames": 8,
        "prompt": f"""Horizontal sprite sheet, exactly 8 frames left to right, single row.
{CHAR}
SPEAR THRUST ATTACK - precise, technical, from behind shield.
Frame 1: Right foot steps back 2px. Spear retracts behind right shoulder, shaft horizontal. Shield stays in guard position.
Frame 2: Spear fully retracted behind shoulder. Body slightly rotated right. Weight on back leg. Shield raised, edge covers up to nose.
Frame 3: Right foot pushes forward. Weight transfers to front leg. Arm begins extending. Spear tip still behind body.
Frame 4: Arm 70% extended. Spear tip passes shield line. Feet planted. Body aligned - shoulder, arm, spear in straight line. Shield tilts slightly down.
Frame 5: FULL THRUST. Arm fully extended. Spear tip 15-20px beyond shield. Deep lunge - front knee bent 90 degrees, back leg straight. Thin grey trail on spear tip (2px, 30% opacity).
Frame 6: Arm begins retracting spear. Tip retreats 5px. Body straightens. Shield returns to frontal position.
Frame 7: Spear half-retracted. Weight recenters. Shield in full guard.
Frame 8: Return to idle. Spear vertical. Feet shoulder-width. Shield covers torso.""",
    },
    "skill": {
        "frames": 10,
        "prompt": f"""Horizontal sprite sheet, exactly 10 frames left to right, single row.
{CHAR}
SHIELD WALL SKILL - defensive buff, shield raised, golden reflection.
Frame 1: Left foot advances 2px. Shield begins rising.
Frame 2: Shield fully raised above helmet. Left arm nearly extended up-forward. Spear horizontal behind shield.
Frame 3: Feet plant wide (3px wider). Front knee bends. Body lowers 3-4px. Shield tilts back 5 degrees.
Frame 4: Feet dig in. Tiny dust at feet (2px grey). Tight grip on spear.
Frame 5: Thin golden line appears on shield outer edge, starting from top. 1px wide, 25% opacity, color gold.
Frame 6: Golden line traced halfway around visible shield edge. 40% opacity peak. Shield gleams briefly.
Frame 7: Golden line fades from starting point. 15% opacity. Character immobile.
Frame 8: Glow gone. Full defensive stance held. Micro foot adjustment 1px.
Frame 9: Feet slowly return closer. Shield lowers. Spear returns vertical. Body rises.
Frame 10: Enhanced idle - slightly lower stance, shield 1px more forward. Buff active.""",
    },
    "hit": {
        "frames": 5,
        "prompt": f"""Horizontal sprite sheet, exactly 5 frames left to right, single row.
{CHAR}
SHIELD BLOCK HIT - impact absorbed by shield, minimal body movement.
Frame 1: White flash on SHIELD EDGE (not body). 4-5px, 50% opacity. Shield tilts back 3 degrees from impact force. Left foot slides back 1px.
Frame 2: Left arm bends absorbing recoil. Shield returns to frontal position. Foot replants. No pain expression - only focus.
Frame 3: Shield perfectly repositioned. Weight redistributed. Legs bend 1px lower for stability.
Frame 4: Shield advances 1px forward - pushing back. Spear raises 2px - ready to counter.
Frame 5: Smooth transition to idle. Shield and spear return to position.""",
    },
    "death": {
        "frames": 10,
        "prompt": f"""Horizontal sprite sheet, exactly 10 frames left to right, single row.
{CHAR}
DEATH - slow, dignified fall. Shield is LAST thing to fall.
Frame 1: Right hand opens. Spear begins to slip from grip. Shield still held. Legs tremble (1px shift).
Frame 2: Spear slides out completely, falling right. Tip hits ground (1px dust). Right arm hangs. Shield STILL UP.
Frame 3: Spear flat on ground to the right. Right arm limp. Shield still in guard. Right knee starts buckling.
Frame 4: Right knee touches ground (1px dust). Shield STILL HELD HIGH - left arm uses last strength. Torso tilts forward slightly.
Frame 5: Left arm can no longer hold shield. Shield tilts forward 15 degrees. Bottom edge touches ground.
Frame 6: Both knees on ground. Shield slides sideways, resting on edge. Character kneeling, arms at sides. Head begins to bow.
Frame 7: Torso leans left. Head bows. Shield falls flat with tiny 1px bounce. Minimal dust.
Frame 8: Body collapses onto left side. Shield flat on ground to the left. Spear on ground to the right. Character between weapons.
Frame 9: Lying on left side. Helmet slightly askew. Hair spread.
Frame 10: Still. 10% darkening overall. Dust settled. Silence.""",
    },
}


async def gen_and_split(name, config):
    print(f"\n  Generating {name} ({config['frames']} frames)...")
    gen = OpenAIImageGeneration(api_key=API_KEY)
    try:
        results = await gen.generate_images(
            prompt=config["prompt"], model="gpt-image-1", quality="low"
        )
        if not results:
            print(f"  No results for {name}")
            return False

        # Save full sheet
        sheet_path = os.path.join(BASE, f"{name}_sheet.png")
        with open(sheet_path, "wb") as f:
            f.write(results[0])

        # Split into individual frames
        img = Image.open(sheet_path)
        w, h = img.size
        fw = w // config["frames"]
        out_dir = os.path.join(BASE, name)
        os.makedirs(out_dir, exist_ok=True)

        for i in range(config["frames"]):
            frame = img.crop((i * fw, 0, (i + 1) * fw, h))
            # Resize to 256x256 if needed
            if frame.size != (256, 256):
                # Keep aspect ratio, fit in 256x256
                frame.thumbnail((256, 256), Image.LANCZOS)
                # Paste on transparent 256x256 canvas
                canvas = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
                ox = (256 - frame.size[0]) // 2
                oy = (256 - frame.size[1]) // 2
                canvas.paste(frame, (ox, oy))
                frame = canvas
            frame_path = os.path.join(out_dir, f"{name}_{i+1:02d}.png")
            frame.save(frame_path, "PNG")

        print(f"  OK: {config['frames']} frames saved to {out_dir}/")
        return True
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


async def main():
    print("=== Greek Hoplite Frame Generator ===")
    for name, config in ANIMS.items():
        await gen_and_split(name, config)
    print("\nDone!")

asyncio.run(main())
