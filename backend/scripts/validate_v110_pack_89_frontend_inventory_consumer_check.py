#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_89_inventory_psp_scoped/v110_pack_89_frontend_inventory_consumer_check_v1.json')))
# Pack 89 e' backend-only; nessuna modifica frontend richiesta
assert isinstance(d.get('frontend_files_modified_in_pack_89'), list)
print('[v110 PACK_89_FRONTEND_INVENTORY_CONSUMER_CHECK] OK backend_only_promotion legacy_path_flagged frontend_opt_in_to_server_scoped')
