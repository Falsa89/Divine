"""
Divine Waifus - Sprite Sheet Generator
Uses AI image generation to create unique sprite sheets for each hero
"""
import os
import base64
import asyncio
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from emergentintegrations.llm.openai.image_generation import OpenAIImageGeneration

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
API_KEY = os.getenv("EMERGENT_LLM_KEY")

ELEMENT_THEMES = {
    "fire": "fiery red-orange flames, burning aura, ember particles",
    "water": "aqua blue waves, water droplets, ocean theme",
    "earth": "brown-gold rocky armor, crystal formations, earth tones",
    "wind": "green swirling winds, leaf particles, light fabric flowing",
    "thunder": "electric yellow-blue lightning bolts, sparks, charged energy",
    "light": "golden holy radiance, white wings glow, divine halo",
    "shadow": "dark purple-black shadows, ghostly aura, mysterious mist",
    "dark": "dark purple-black shadows, ghostly aura, mysterious mist",
    "neutral": "balanced grey-silver tones, simple elegant design",
}

CLASS_THEMES = {
    "DPS": "wielding a glowing sword/katana, aggressive combat stance, warrior outfit",
    "Tank": "heavy armor with shield, defensive stance, knight-like protective gear",
    "Support": "magical staff with glowing orb, healing pose, flowing robes and cape",
}


def build_prompt(hero_name: str, element: str, hero_class: str, rarity: int) -> str:
    elem_desc = ELEMENT_THEMES.get(element, ELEMENT_THEMES["neutral"])
    class_desc = CLASS_THEMES.get(hero_class, CLASS_THEMES["DPS"])
    rarity_desc = "legendary divine" if rarity >= 5 else "epic powerful" if rarity >= 4 else "skilled"

    return (
        f"High quality HD anime-style sprite sheet for '{hero_name}', a {rarity_desc} goddess character. "
        f"Beautiful detailed anime art style with cel-shading. "
        f"The character is a stunning anime girl warrior/goddess, {class_desc}. "
        f"Visual theme: {elem_desc}. "
        f"The sprite sheet contains exactly 4 animation frames arranged horizontally in a single row: "
        f"Frame 1: IDLE standing pose facing right, "
        f"Frame 2: ATTACK action pose with weapon slash effect, "
        f"Frame 3: HURT/HIT pose being knocked back, "
        f"Frame 4: SPECIAL SKILL casting pose with magical energy aura. "
        f"Total image is 512x128 pixels (each frame 128x128). "
        f"HD quality, vibrant saturated anime colors, clean black outlines, dark transparent background. "
        f"Consistent character design across all 4 frames. Professional game asset quality."
    )


async def generate_sprite_for_hero(hero: dict) -> bytes | None:
    """Generate a sprite sheet for a single hero using AI"""
    if not API_KEY:
        print("ERROR: No EMERGENT_LLM_KEY found")
        return None

    prompt = build_prompt(
        hero["name"],
        hero.get("element", "neutral"),
        hero.get("hero_class", "DPS"),
        hero.get("rarity", 1),
    )
    print(f"  Generating sprite for: {hero['name']} ({hero.get('element')}/{hero.get('hero_class')})")
    print(f"  Prompt: {prompt[:120]}...")

    try:
        image_gen = OpenAIImageGeneration(api_key=API_KEY)
        images = await image_gen.generate_images(
            prompt=prompt,
            model="gpt-image-1",
            number_of_images=1,
        )
        if images and len(images) > 0:
            print(f"  SUCCESS: Got {len(images[0])} bytes for {hero['name']}")
            return images[0]
        else:
            print(f"  WARN: No image returned for {hero['name']}")
            return None
    except Exception as e:
        print(f"  ERROR generating sprite for {hero['name']}: {e}")
        return None


async def main():
    print("=== Divine Waifus Sprite Sheet Generator ===")
    print(f"API Key: {'SET' if API_KEY else 'MISSING'}")

    client = AsyncIOMotorClient(MONGO_URL)
    db = client.divine_waifus

    heroes = await db.heroes.find({}).to_list(length=100)
    print(f"Found {len(heroes)} heroes")

    # Filter heroes that don't have sprite sheets yet
    heroes_to_generate = [
        h for h in heroes
        if not h.get("sprite_sheet_base64")
    ]
    print(f"Heroes needing sprites: {len(heroes_to_generate)}")

    # Generate 3 at a time to avoid rate limits, max 6 for first batch
    batch = heroes_to_generate[:6]
    generated = 0

    for hero in batch:
        sprite_bytes = await generate_sprite_for_hero(hero)
        if sprite_bytes:
            b64 = base64.b64encode(sprite_bytes).decode("utf-8")
            await db.heroes.update_one(
                {"id": hero["id"]},
                {"$set": {"sprite_sheet_base64": b64}},
            )
            generated += 1
            print(f"  Saved sprite for {hero['name']} ({generated}/{len(batch)})")
        # Small delay between requests
        await asyncio.sleep(2)

    print(f"\n=== Done! Generated {generated}/{len(batch)} sprites ===")
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
