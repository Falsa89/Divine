"""
Server Time endpoint.
Restituisce l'orario ufficiale del server (UTC).
Il client usa questo valore per:
  - calcolare l'offset client↔server
  - determinare la fase temporale (dawn/day/sunset/night) della homepage
  - resettare task giornalieri etc.

Configurazione:
  - `SERVER_TIMEZONE_OFFSET_HOURS`: offset manuale (default 0 = UTC).
    In futuro può essere spostato in env o in un documento config DB.
"""
from datetime import datetime, timezone
from fastapi import APIRouter

SERVER_TIMEZONE_OFFSET_HOURS = 0  # UTC ufficiale del server


def register_server_time_routes(router: APIRouter):
    @router.get("/server-time")
    async def get_server_time():
        now = datetime.now(timezone.utc)
        return {
            "iso": now.isoformat(),
            "epoch_ms": int(now.timestamp() * 1000),
            "utc_offset_hours": SERVER_TIMEZONE_OFFSET_HOURS,
            "hour": now.hour,
            "minute": now.minute,
            "second": now.second,
        }
