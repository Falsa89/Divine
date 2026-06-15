"""Pre-QA Stabilization 117B — Hero Upgrade Readiness route (READ-ONLY).

Requires auth + server_id. No silent s1 fallback. No DB writes.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from utils.hero_upgrade_readiness import (
    HERO_UPGRADE_READINESS_SOURCE_VERSION,
    build_metadata,
    build_per_hero_readiness,
    build_envelope_no_psp,
)


def create_hero_upgrade_readiness_router(db, get_current_user):
    router = APIRouter(prefix='/api/hero-upgrade', tags=['hero_upgrade_readiness'])

    @router.get('/metadata')
    async def metadata():
        return build_metadata()

    @router.get('/readiness')
    async def readiness(
        server_id: Optional[str] = Query(None),
        current_user: dict = Depends(get_current_user),
    ):
        if not server_id:
            payload = build_metadata()
            payload.update({
                'code': 'SERVER_ID_REQUIRED',
                'message': (
                    'Hero upgrade readiness e\' server-scoped. '
                    'Fornire server_id esplicito; nessun silent s1 fallback.'
                ),
                'no_silent_s1_fallback': True,
            })
            raise HTTPException(status_code=400, detail=payload)

        uid = current_user.get('id')
        psp = await db.player_server_profiles.find_one({
            'user_id': uid, 'server_id': server_id
        })
        if not psp:
            return build_envelope_no_psp(server_id)

        # find_one solo → nessuna mutation. Limito a 500 record (uguale al cap
        # esistente in /api/user/heroes).
        cursor = db.user_heroes.find({'user_id': uid, 'server_id': server_id})
        user_heroes = await cursor.to_list(500)
        heroes = [build_per_hero_readiness(uh) for uh in user_heroes]
        return {
            'status': 'ok',
            'server_id': server_id,
            'source_version': HERO_UPGRADE_READINESS_SOURCE_VERSION,
            'safe_read_only': True,
            'no_db_writes': True,
            'no_upgrade_activation': True,
            'no_material_consume': True,
            'no_claim_activation': True,
            'no_reward_activation': True,
            'server_scoped': True,
            'heroes': heroes,
            'heroes_count': len(heroes),
            'any_red_dot_candidate': False,
            'global_blocker': 'ECONOMY_SOURCE_NOT_SAFE_FOR_READINESS',
        }

    return router
