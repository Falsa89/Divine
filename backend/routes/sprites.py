"""
Divine Waifus - Sprite Sheet Routes
Serve sprite sheet images for heroes
"""
import base64
from fastapi import HTTPException
from fastapi.responses import Response


def register_sprite_routes(router, db):

    @router.get("/sprites/{hero_id}")
    async def get_hero_sprite(hero_id: str):
        """Get sprite sheet image for a hero"""
        hero = await db.heroes.find_one({"id": hero_id})
        if not hero or not hero.get("sprite_sheet_base64"):
            raise HTTPException(status_code=404, detail="Sprite non trovato")
        
        image_bytes = base64.b64decode(hero["sprite_sheet_base64"])
        return Response(content=image_bytes, media_type="image/png")

    @router.get("/sprites/by-name/{hero_name}")
    async def get_hero_sprite_by_name(hero_name: str):
        """Get sprite sheet image by hero name"""
        hero = await db.heroes.find_one({"name": hero_name})
        if not hero or not hero.get("sprite_sheet_base64"):
            raise HTTPException(status_code=404, detail="Sprite non trovato")
        
        image_bytes = base64.b64decode(hero["sprite_sheet_base64"])
        return Response(content=image_bytes, media_type="image/png")

    @router.get("/sprites")
    async def list_sprites():
        """List all heroes with sprites"""
        heroes = await db.heroes.find(
            {"sprite_sheet_base64": {"$exists": True, "$ne": None}},
            {"id": 1, "name": 1, "element": 1, "hero_class": 1, "rarity": 1, "_id": 0}
        ).to_list(length=100)
        return {"sprites": heroes, "count": len(heroes)}
