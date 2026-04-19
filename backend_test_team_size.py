"""
Test: Verify the 'team size mirror' bug fix in /app/backend/battle_engine.py:695
Expected: enemy team (team_b_final) always has 6 units regardless of player_team size.
"""
import requests
import sys

BASE = "http://localhost:8001"

def log(msg):
    print(msg, flush=True)

def main():
    # 1. Login
    r = requests.post(f"{BASE}/api/login", json={"email": "test@test.com", "password": "password123"}, timeout=15)
    assert r.status_code == 200, f"login failed: {r.status_code} {r.text}"
    token = r.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    log(f"[1] login OK, token acquired")

    # 2. Profile
    r = requests.get(f"{BASE}/api/user/profile", headers=headers, timeout=15)
    assert r.status_code == 200, f"profile failed: {r.status_code} {r.text}"
    profile = r.json()
    user_id = profile.get("id") or profile.get("user", {}).get("id")
    log(f"[2] profile OK user_id={user_id}")

    # 3. User heroes
    r = requests.get(f"{BASE}/api/user/heroes", headers=headers, timeout=15)
    assert r.status_code == 200, f"user heroes failed: {r.status_code} {r.text}"
    user_heroes = r.json()
    if isinstance(user_heroes, dict):
        user_heroes = user_heroes.get("heroes", user_heroes.get("user_heroes", []))
    log(f"[3] user_heroes count={len(user_heroes)}")
    assert len(user_heroes) >= 4, f"need at least 4 heroes, got {len(user_heroes)}"

    # 4. Team current
    r = requests.get(f"{BASE}/api/team", headers=headers, timeout=15)
    assert r.status_code == 200, f"GET /api/team failed: {r.status_code} {r.text}"
    team_now = r.json()
    log(f"[4] current team keys={list(team_now.keys()) if isinstance(team_now, dict) else type(team_now).__name__}")
    cur_formation = team_now.get("formation", []) if isinstance(team_now, dict) else []
    log(f"    current formation entries with hero = {sum(1 for p in cur_formation if p.get('user_hero_id'))}")

    # 5. Build formation with N heroes using POST /api/team/update-formation
    def build_formation(n):
        # 3x3 grid positions: x in 0..2 columns; y rows
        slots = [
            {"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 2, "y": 0},
            {"x": 0, "y": 3}, {"x": 1, "y": 3}, {"x": 2, "y": 3},
        ]
        formation = []
        for i, slot in enumerate(slots):
            entry = {"x": slot["x"], "y": slot["y"]}
            if i < n:
                entry["user_hero_id"] = user_heroes[i]["id"]
            formation.append(entry)
        return formation

    def simulate_and_check(n_heroes):
        formation = build_formation(n_heroes)
        r = requests.post(f"{BASE}/api/team/update-formation", headers=headers,
                          json={"formation": formation}, timeout=15)
        assert r.status_code == 200, f"update-formation failed: {r.status_code} {r.text}"
        log(f"[SET] formation with {n_heroes} heroes OK power={r.json().get('total_power')}")

        r = requests.post(f"{BASE}/api/battle/simulate", headers=headers, timeout=60)
        assert r.status_code == 200, f"battle/simulate failed: {r.status_code} {r.text}"
        result = r.json()
        team_a_final = result.get("team_a_final", [])
        team_b_final = result.get("team_b_final", [])
        log(f"[SIM n={n_heroes}] team_a_final={len(team_a_final)} team_b_final={len(team_b_final)} turns={result.get('turns')} victory={result.get('victory')}")
        return len(team_a_final), len(team_b_final)

    # Test scenarios: 3 heroes, 4 heroes, 6 heroes
    results = []
    for n in (3, 4, 6):
        a, b = simulate_and_check(n)
        results.append((n, a, b))

    # Verify
    log("\n===== RESULTS =====")
    all_ok = True
    for n, a, b in results:
        status = "OK" if b == 6 else "FAIL"
        if b != 6:
            all_ok = False
        log(f"  heroes_set={n}  player_team(team_a_final)={a}  enemy_team(team_b_final)={b}  => {status}")

    if all_ok:
        log("\n✅ bug team-size RISOLTO, enemy team sempre 6 indipendente da player team")
        sys.exit(0)
    else:
        log("\n❌ FAIL: enemy team size still mirrors player team size")
        sys.exit(1)

if __name__ == "__main__":
    main()
