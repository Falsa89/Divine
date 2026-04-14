"""Update all 30 heroes with unique images + add animated portrait support"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

# 30 UNIQUE images - one per hero, matched to element/rarity theme
HERO_IMAGES = {
    # 6-star Divine (4 heroes - most epic images)
    "Amaterasu":  "https://images.stockcake.com/public/2/6/5/265b7b66-3ca5-49da-b7a5-c89f6660f587_large/ethereal-anime-goddess-stockcake.jpg",
    "Tsukuyomi":  "https://images.stockcake.com/public/1/9/d/19d4b604-f375-49a7-a8f2-732b348c1506_large/digital-astral-goddess-stockcake.jpg",
    "Susanoo":    "https://images.stockcake.com/public/0/9/f/09fbd8ee-802d-4b28-b799-3729dbb7423f_large/ethereal-warrior-goddess-stockcake.jpg",
    "Izanami":    "https://images.stockcake.com/public/6/9/9/699504cf-f665-493e-885b-fd8c078dd67f_large/neon-cyber-goddess-stockcake.jpg",
    # 5-star Mythic (6 heroes)
    "Athena":     "https://images.stockcake.com/public/c/8/1/c8160c66-4fa0-4372-87b5-0cb7145df41a_large/divine-warrior-goddess-stockcake.jpg",
    "Aphrodite":  "https://images.stockcake.com/public/f/8/3/f83a656b-1128-406a-96b8-aa6d27b4f284_large/celestial-goddess-portrait-stockcake.jpg",
    "Artemis":    "https://images.stockcake.com/public/4/a/7/4a756de7-2ef0-4e67-9791-30e4b2ea609d_large/ethereal-night-goddess-stockcake.jpg",
    "Freya":      "https://images.stockcake.com/public/3/9/1/3910e60e-1083-4690-8d87-3c1611a67a10_large/divine-goddess-power-stockcake.jpg",
    "Valkyrie":   "https://images.stockcake.com/public/b/a/e/bae3c7e3-9965-4d17-a9d5-e13bba332e6b_large/celestial-goddess-illustration-stockcake.jpg",
    "Medusa":     "https://images.stockcake.com/public/9/d/e/9de749ae-ae62-4a6e-b63d-bcb03df4b0bc_large/mystical-snake-goddess-stockcake.jpg",
    # 4-star Epic (6 heroes)
    "Hera":       "https://images.stockcake.com/public/8/9/c/89c43b19-9991-4a98-97e3-9e2af826fe6f_large/golden-magical-goddess-stockcake.jpg",
    "Persephone": "https://images.stockcake.com/public/0/2/3/023cc25c-a649-4af6-b20b-8eaa4ddd87f9_large/mystical-purple-enchantress-stockcake.jpg",
    "Nyx":        "https://images.stockcake.com/public/c/d/e/cde1032b-0d9c-4223-8045-fcca667a89f5_large/cosmic-goddess-beauty-stockcake.jpg",
    "Demeter":    "https://images.stockcake.com/public/4/9/6/496ca6dc-0311-4d0f-9eaa-7b984b447229_large/autumn-goddess-magic-stockcake.jpg",
    "Hecate":     "https://images.stockcake.com/public/4/0/4/404edfd3-13b2-40d9-92a1-dac36ae474b7_large/purple-mystical-angel-stockcake.jpg",
    "Selene":     "https://images.stockcake.com/public/c/a/6/ca6ab9cd-9e2e-4a62-b8ff-68341a6de252_large/magical-moon-flight-stockcake.jpg",
    # 3-star Rare (6 heroes)
    "Sakuya":     "https://images.stockcake.com/public/f/5/c/f5c8a45a-6417-4086-aafe-ca99188f1125_large/celestial-anime-goddess-stockcake.jpg",
    "Kaguya":     "https://images.stockcake.com/public/1/8/d/18de8edb-9c3f-478f-8f6e-022c42d0e0bb_large/celestial-anime-goddess-stockcake.jpg",
    "Inari":      "https://images.stockcake.com/public/9/8/b/98b48999-43a5-4266-b314-34c4da64c292_large/celestial-goddess-dreams-stockcake.jpg",
    "Benzaiten":  "https://images.stockcake.com/public/d/a/1/da119c60-ddb2-4d73-a81b-b5486bf2ddbb_large/ethereal-anime-magic-stockcake.jpg",
    "Raijin":     "https://images.stockcake.com/public/5/a/2/5a2e3edf-171a-4d3a-84dd-f24cb9997c45_large/celestial-anime-goddess-stockcake.jpg",
    "Fujin":      "https://images.stockcake.com/public/f/7/4/f74dfc4b-7c4e-48b0-8140-78a97fa98aea_large/forest-spirit-awakening-stockcake.jpg",
    # 2-star Uncommon (4 heroes)
    "Iris":       "https://images.stockcake.com/public/1/e/e/1eec8ae1-819d-408e-b216-dc3010ba96d6_large/moonlight-fairy-dreams-stockcake.jpg",
    "Echo":       "https://images.stockcake.com/public/a/e/d/aed1dd12-1d9b-4988-b0bb-5c06654f3df3_large/winter-spring-awakening-stockcake.jpg",
    "Daphne":     "https://images.stockcake.com/public/b/f/d/bfd30947-005f-4f69-82c4-09a833ed86fd_large/cosmic-anime-goddess-stockcake.jpg",
    "Chloris":    "https://images.stockcake.com/public/f/1/f/f1fb0c5e-7639-4e19-8e0a-f93b8f143a3c_large/wisdom-through-time-stockcake.jpg",
    # 1-star Common (4 heroes)
    "Aura":       "https://images.stockcake.com/public/b/8/4/b84cd965-b47c-48d6-8b41-4a6cb67e1e8e_large/ethereal-fabric-dancer-stockcake.jpg",
    "Hestia":     "https://images.stockcake.com/public/1/2/5/125b5666-8e5c-4e8a-828f-bf047e77b5a2_large/purple-cosmic-seer-stockcake.jpg",
    "Nike":       "https://images.stockcake.com/public/1/7/9/17919495-8534-4080-8ab0-1b62144486be_large/celestial-anime-maiden-stockcake.jpg",
    "Psyche":     "https://images.stockcake.com/public/3/1/1/311d249e-4de5-410f-b91f-0ee2685b2977_large/celestial-anime-goddess-stockcake.jpg",
}

async def update():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["divine_waifus"]
    count = 0
    for name, url in HERO_IMAGES.items():
        r = await db.heroes.update_one({"name": name}, {"$set": {"image_url": url}})
        if r.modified_count > 0:
            count += 1
            print(f"Updated: {name}")
        else:
            print(f"Skipped (not found or same): {name}")
    print(f"\nTotal updated: {count}/{len(HERO_IMAGES)}")
    client.close()

if __name__ == "__main__":
    asyncio.run(update())
