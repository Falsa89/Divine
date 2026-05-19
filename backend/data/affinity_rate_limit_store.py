"""V22 — Affinity rate-limit store abstraction.

Feature-flagged backend selection:
  AFFINITY_RATE_LIMIT_BACKEND=memory (default; in-process sliding window)
  AFFINITY_RATE_LIMIT_BACKEND=redis  (gated; requires REDIS_URL + reachable server)

The `redis` backend is OFF by default and stays in PREP state until all V22
gates pass AND Redis is reachable. If Redis init fails the store FAILS-OPEN
back to memory (canary safety) and logs a single warning.

This module exposes a single public function `rate_limit_check(user_id, ip)`
that returns (allowed: bool, reason: Optional[str], snapshot: dict) — same
contract as the in-route `_rate_limit_check` in `affinity_gift_spend.py`.
The in-route function continues to be authoritative; this module is a
PREP-only abstraction safe to import.
"""
from __future__ import annotations
import os
import time
from typing import Optional, Tuple

_BACKEND_ENV = 'AFFINITY_RATE_LIMIT_BACKEND'
_REDIS_URL_ENV = 'REDIS_URL'
_DEFAULT_BACKEND = 'memory'

_RL_PER_USER_PER_MIN = 30
_RL_PER_USER_PER_HOUR = 240
_RL_PER_IP_PER_MIN = 60
_RL_BURST_WINDOW_S = 10
_RL_BURST_MAX = 6

_MEM_EVENTS: dict = {}
_REDIS_CLIENT = None
_REDIS_INIT_FAILED = False


def current_backend() -> str:
    return os.environ.get(_BACKEND_ENV, _DEFAULT_BACKEND).lower().strip() or _DEFAULT_BACKEND


def _get_redis():
    """Lazy init. Returns client or None. NO permanent fail caching (V23):
    each call retries init so a transient at-startup absence does not
    permanently disable the redis path."""
    global _REDIS_CLIENT
    if _REDIS_CLIENT is not None:
        try:
            _REDIS_CLIENT.ping()
            return _REDIS_CLIENT
        except Exception:
            _REDIS_CLIENT = None
    url = os.environ.get(_REDIS_URL_ENV, '').strip()
    if not url:
        return None
    try:
        import redis  # type: ignore
        c = redis.Redis.from_url(url, socket_timeout=1.0, socket_connect_timeout=1.0)
        c.ping()
        _REDIS_CLIENT = c
        return c
    except Exception:
        return None


def _mem_record(scope: str, key: str) -> None:
    now = time.time()
    ev = _MEM_EVENTS.setdefault((scope, key), [])
    ev.append(now)
    if len(ev) > 1000:
        cutoff = now - 3600
        _MEM_EVENTS[(scope, key)] = [t for t in ev if t >= cutoff]


def _mem_count(scope: str, key: str, window_s: float) -> int:
    now = time.time()
    cutoff = now - window_s
    ev = _MEM_EVENTS.get((scope, key), [])
    return sum(1 for t in ev if t >= cutoff)


def _redis_record_and_count(c, scope: str, key: str, window_s: float) -> int:
    """Record one event and return count in window using sorted set + TTL."""
    rk = f'af2:ratelimit:{scope}:{key}'
    now_ms = int(time.time() * 1000)
    cutoff_ms = now_ms - int(window_s * 1000)
    try:
        pipe = c.pipeline()
        pipe.zadd(rk, {f'{now_ms}': now_ms})
        pipe.zremrangebyscore(rk, 0, cutoff_ms)
        pipe.zcard(rk)
        pipe.expire(rk, int(window_s) + 5)
        results = pipe.execute()
        return int(results[2])
    except Exception:
        return -1


def _redis_count(c, scope: str, key: str, window_s: float) -> int:
    rk = f'af2:ratelimit:{scope}:{key}'
    now_ms = int(time.time() * 1000)
    cutoff_ms = now_ms - int(window_s * 1000)
    try:
        pipe = c.pipeline()
        pipe.zremrangebyscore(rk, 0, cutoff_ms)
        pipe.zcard(rk)
        results = pipe.execute()
        return int(results[1])
    except Exception:
        return -1


def rate_limit_check(user_id: str, client_ip: str) -> Tuple[bool, Optional[str], dict]:
    backend = current_backend()
    uid = (user_id or '<anon>').strip() or '<anon>'
    ip = (client_ip or '<noip>').strip() or '<noip>'
    if backend == 'redis':
        c = _get_redis()
        if c is None:
            # fail-open back to memory
            backend = 'memory_fallback'
        else:
            user_burst = _redis_count(c, 'burst', uid, _RL_BURST_WINDOW_S)
            user_min = _redis_count(c, 'user', uid, 60)
            user_hour = _redis_count(c, 'user', uid, 3600)
            ip_min = _redis_count(c, 'ip', ip, 60)
            snap = {
                'backend': 'redis',
                'user_burst': user_burst, 'burst_max': _RL_BURST_MAX,
                'user_min': user_min, 'user_min_max': _RL_PER_USER_PER_MIN,
                'user_hour': user_hour, 'user_hour_max': _RL_PER_USER_PER_HOUR,
                'ip_min': ip_min, 'ip_min_max': _RL_PER_IP_PER_MIN,
            }
            if user_burst >= _RL_BURST_MAX: return False, 'user_burst_exceeded', snap
            if user_min >= _RL_PER_USER_PER_MIN: return False, 'user_per_minute_exceeded', snap
            if user_hour >= _RL_PER_USER_PER_HOUR: return False, 'user_per_hour_exceeded', snap
            if ip_min >= _RL_PER_IP_PER_MIN: return False, 'ip_per_minute_exceeded', snap
            _redis_record_and_count(c, 'burst', uid, _RL_BURST_WINDOW_S)
            _redis_record_and_count(c, 'user', uid, 3600)
            _redis_record_and_count(c, 'ip', ip, 60)
            return True, None, snap
    # memory / memory_fallback
    user_burst = _mem_count('user', uid, _RL_BURST_WINDOW_S)
    user_min = _mem_count('user', uid, 60)
    user_hour = _mem_count('user', uid, 3600)
    ip_min = _mem_count('ip', ip, 60)
    snap = {
        'backend': backend,
        'user_burst': user_burst, 'burst_max': _RL_BURST_MAX,
        'user_min': user_min, 'user_min_max': _RL_PER_USER_PER_MIN,
        'user_hour': user_hour, 'user_hour_max': _RL_PER_USER_PER_HOUR,
        'ip_min': ip_min, 'ip_min_max': _RL_PER_IP_PER_MIN,
    }
    if user_burst >= _RL_BURST_MAX: return False, 'user_burst_exceeded', snap
    if user_min >= _RL_PER_USER_PER_MIN: return False, 'user_per_minute_exceeded', snap
    if user_hour >= _RL_PER_USER_PER_HOUR: return False, 'user_per_hour_exceeded', snap
    if ip_min >= _RL_PER_IP_PER_MIN: return False, 'ip_per_minute_exceeded', snap
    _mem_record('user', uid)
    _mem_record('ip', ip)
    return True, None, snap


def redis_available() -> bool:
    return _get_redis() is not None


def backend_info() -> dict:
    return {
        'current_backend': current_backend(),
        'redis_url_set': bool(os.environ.get(_REDIS_URL_ENV, '').strip()),
        'redis_alive': redis_available(),
        'feature_flag': _BACKEND_ENV,
        'allowed_values': ['memory', 'redis'],
        'default_value': _DEFAULT_BACKEND,
        'note': 'This module is a PREP abstraction; the authoritative rate-limit guard is still in routes/affinity_gift_spend.py until V23+ migration is approved.',
    }
