"""
Download hero images and store URLs in database
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

HERO_IMAGES = {
    # 6-star Divine heroes get the most dramatic images
    "Amaterasu": "https://images.stockcake.com/public/5/6/3/56302345-c0b1-4da4-8795-0297c928d97d_large/elegant-anime-girl-stockcake.jpg",
    "Tsukuyomi": "https://images.stockcake.com/public/4/a/a/4aaf1f46-18bf-41b0-9b4d-e50d1341324c_large/clockwork-anime-maiden-stockcake.jpg",
    "Susanoo": "https://images.stockcake.com/public/e/7/1/e717e846-fd42-41b5-bd0d-aabcf606769b_large/confident-anime-girl-stockcake.jpg",
    "Izanami": "https://images.stockcake.com/public/a/6/1/a619a837-e7c2-4e79-b918-5310f7ed6043_large/shy-anime-girl-stockcake.jpg",
    # 5-star Mythic
    "Athena": "https://images.stockcake.com/public/f/7/8/f7846949-02f7-4a79-8a13-8efdd9f372a7_large/stylish-anime-girl-stockcake.jpg",
    "Aphrodite": "https://images.stockcake.com/public/8/7/f/87fdff59-ac65-4ab7-8e0a-3e0bb26af8bd_large/cheerful-blue-haired-girl-stockcake.jpg",
    "Artemis": "https://images.stockcake.com/public/a/4/9/a4954f9e-69c6-4735-b097-c62211eb7896_large/cherry-blossom-girl-stockcake.jpg",
    "Freya": "https://images.stockcake.com/public/3/b/1/3b1955ce-41f5-4a63-acfb-a6fa4f1ec2c7_large/chibi-lightning-girl-stockcake.jpg",
    "Valkyrie": "https://images.stockcake.com/public/e/7/1/e717e846-fd42-41b5-bd0d-aabcf606769b_large/confident-anime-girl-stockcake.jpg",
    "Medusa": "https://images.stockcake.com/public/5/6/3/56302345-c0b1-4da4-8795-0297c928d97d_large/elegant-anime-girl-stockcake.jpg",
    # 4-star Epic
    "Hera": "https://images.stockcake.com/public/f/7/8/f7846949-02f7-4a79-8a13-8efdd9f372a7_large/stylish-anime-girl-stockcake.jpg",
    "Persephone": "https://images.stockcake.com/public/4/a/a/4aaf1f46-18bf-41b0-9b4d-e50d1341324c_large/clockwork-anime-maiden-stockcake.jpg",
    "Nyx": "https://images.stockcake.com/public/a/6/1/a619a837-e7c2-4e79-b918-5310f7ed6043_large/shy-anime-girl-stockcake.jpg",
    "Demeter": "https://images.stockcake.com/public/a/4/9/a4954f9e-69c6-4735-b097-c62211eb7896_large/cherry-blossom-girl-stockcake.jpg",
    "Hecate": "https://images.stockcake.com/public/3/b/1/3b1955ce-41f5-4a63-acfb-a6fa4f1ec2c7_large/chibi-lightning-girl-stockcake.jpg",
    "Selene": "https://images.stockcake.com/public/8/7/f/87fdff59-ac65-4ab7-8e0a-3e0bb26af8bd_large/cheerful-blue-haired-girl-stockcake.jpg",
    # 3-star Rare
    "Sakuya": "https://images.stockcake.com/public/8/7/f/87fdff59-ac65-4ab7-8e0a-3e0bb26af8bd_large/cheerful-blue-haired-girl-stockcake.jpg",
    "Kaguya": "https://images.stockcake.com/public/5/6/3/56302345-c0b1-4da4-8795-0297c928d97d_large/elegant-anime-girl-stockcake.jpg",
    "Inari": "https://images.stockcake.com/public/a/4/9/a4954f9e-69c6-4735-b097-c62211eb7896_large/cherry-blossom-girl-stockcake.jpg",
    "Benzaiten": "https://images.stockcake.com/public/a/6/1/a619a837-e7c2-4e79-b918-5310f7ed6043_large/shy-anime-girl-stockcake.jpg",
    "Raijin": "https://images.stockcake.com/public/3/b/1/3b1955ce-41f5-4a63-acfb-a6fa4f1ec2c7_large/chibi-lightning-girl-stockcake.jpg",
    "Fujin": "https://images.stockcake.com/public/e/7/1/e717e846-fd42-41b5-bd0d-aabcf606769b_large/confident-anime-girl-stockcake.jpg",
    # 2-star
    "Iris": "https://images.stockcake.com/public/f/7/8/f7846949-02f7-4a79-8a13-8efdd9f372a7_large/stylish-anime-girl-stockcake.jpg",
    "Echo": "https://images.stockcake.com/public/a/4/9/a4954f9e-69c6-4735-b097-c62211eb7896_large/cherry-blossom-girl-stockcake.jpg",
    "Daphne": "https://images.stockcake.com/public/8/7/f/87fdff59-ac65-4ab7-8e0a-3e0bb26af8bd_large/cheerful-blue-haired-girl-stockcake.jpg",
    "Chloris": "https://images.stockcake.com/public/a/6/1/a619a837-e7c2-4e79-b918-5310f7ed6043_large/shy-anime-girl-stockcake.jpg",
    # 1-star
    "Aura": "https://images.stockcake.com/public/3/b/1/3b1955ce-41f5-4a63-acfb-a6fa4f1ec2c7_large/chibi-lightning-girl-stockcake.jpg",
    "Hestia": "https://images.stockcake.com/public/a/4/9/a4954f9e-69c6-4735-b097-c62211eb7896_large/cherry-blossom-girl-stockcake.jpg",
    "Nike": "https://images.stockcake.com/public/e/7/1/e717e846-fd42-41b5-bd0d-aabcf606769b_large/confident-anime-girl-stockcake.jpg",
    "Psyche": "https://images.stockcake.com/public/5/6/3/56302345-c0b1-4da4-8795-0297c928d97d_large/elegant-anime-girl-stockcake.jpg",
}

async def update_hero_images():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["divine_waifus"]
    
    count = 0
    for name, url in HERO_IMAGES.items():
        result = await db.heroes.update_one(
            {"name": name},
            {"$set": {"image_url": url}}
        )
        if result.modified_count > 0:
            count += 1
            print(f"Updated: {name}")
    
    print(f"\nTotal updated: {count}/{len(HERO_IMAGES)}")
    client.close()

if __name__ == "__main__":
    asyncio.run(update_hero_images())
