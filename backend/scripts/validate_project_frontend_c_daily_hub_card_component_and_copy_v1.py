#!/usr/bin/env python3
import json, sys
from pathlib import Path
M = Path('/app/data/design/frontend/project_frontend_c_daily_hub_card_component_and_copy_v1.json')
ROUTE = Path('/app/frontend/app/daily-hub.tsx')
def main():
    m = json.loads(M.read_text())
    assert m['verdict'] == 'TRACK_C_DAILY_HUB_CARD_COMPONENT_AND_COPY_READY'
    text = ROUTE.read_text()
    assert m['no_fake_availability_claim'] is True
    assert m['no_countdown_timer'] is True
    assert m['copy_clear_about_redirect_to_dedicated_section'] is True
    # Copy keys present in code
    copy = m['copy_italian']
    assert copy['banner_title'] in text, 'banner_title not in route'
    assert 'Nessun claim avviene qui' in text or 'Nessuna ricompensa viene riscattata da qui' in text, 'no clear non-claim disclaimer'
    for cid, csub in copy['entries'].items():
        # at least the first words of each entry copy must appear
        # File .tsx may contain \uXXXX escapes for non-ASCII chars; normalize for comparison.
        norm_text = text.encode('utf-8').decode('unicode_escape', errors='ignore')
        first_8 = csub[:30]
        assert (first_8 in text) or (first_8 in norm_text), f'entry copy {cid} not in route: {first_8}'
    print(f'[PASS] FC Track C card/copy READY — entries_copy={len(copy["entries"])}, no_fake_claim=True, no_countdown=True')
    return 0
if __name__ == '__main__': sys.exit(main())
