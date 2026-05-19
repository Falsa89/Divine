"""V24 — Affinity gift-spend abuse metrics (in-memory, gated).

Light-weight metrics collector with no external dependency. Gated behind
AFFINITY_METRICS_ENABLED=true_explicit_affinity_metrics_on. When OFF the
record_* functions become no-ops; when ON they update process-local counters
and histograms.

A snapshot is exposed via /api/affinity/gift-spend/_admin/metrics-snapshot
(read-only, gated by same flag). Endpoint stays disabled by default; abuse
instrumentation runs as PREP/STAGE4 internal only.
"""
from __future__ import annotations
import os, threading, time
from collections import defaultdict

_ENV = 'AFFINITY_METRICS_ENABLED'
_ON_VALUE = 'true_explicit_affinity_metrics_on'

_LOCK = threading.Lock()
_started_at = time.time()

# counters: key -> int
_counters: dict = defaultdict(int)
# latency buckets in ms (histogram)
_HIST_BUCKETS_MS = (5, 10, 25, 50, 100, 250, 500, 1000, 2000)
_hist: dict = defaultdict(lambda: {b: 0 for b in (*_HIST_BUCKETS_MS, '+Inf')})
_hist_sum: dict = defaultdict(float)
_hist_count: dict = defaultdict(int)
# gauges
_gauges: dict = {}


def enabled() -> bool:
    return os.environ.get(_ENV, '') == _ON_VALUE


def inc(name: str, labels: dict | None = None, n: int = 1) -> None:
    if not enabled():
        return
    key = _key(name, labels)
    with _LOCK:
        _counters[key] += n


def observe_latency_ms(name: str, latency_ms: float, labels: dict | None = None) -> None:
    if not enabled():
        return
    key = _key(name, labels)
    with _LOCK:
        _hist_sum[key] += latency_ms
        _hist_count[key] += 1
        for b in _HIST_BUCKETS_MS:
            if latency_ms <= b:
                _hist[key][b] += 1
        _hist[key]['+Inf'] += 1


def set_gauge(name: str, value, labels: dict | None = None) -> None:
    if not enabled():
        return
    key = _key(name, labels)
    with _LOCK:
        _gauges[key] = value


def snapshot() -> dict:
    if not enabled():
        return {'enabled': False, 'reason': 'AFFINITY_METRICS_ENABLED not set'}
    with _LOCK:
        return {
            'enabled': True,
            'started_at_epoch': _started_at,
            'uptime_seconds': time.time() - _started_at,
            'counters': dict(_counters),
            'histograms': {k: dict(v) for k, v in _hist.items()},
            'histogram_sums_ms': dict(_hist_sum),
            'histogram_counts': dict(_hist_count),
            'gauges': dict(_gauges),
            'buckets_ms': list(_HIST_BUCKETS_MS),
            'safety': {
                'flag': _ENV,
                'design': 'in_memory_process_local',
                'not_for_production_dashboards': True,
                'no_borea_data': True,
                'no_user_pii': True,
            },
        }


def _key(name: str, labels: dict | None) -> str:
    if not labels:
        return name
    parts = ','.join(f'{k}={labels[k]}' for k in sorted(labels))
    return f'{name}{{{parts}}}'
