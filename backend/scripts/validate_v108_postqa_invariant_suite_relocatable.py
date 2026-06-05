#!/usr/bin/env python3
# v108_POSTQA_A — Runtime invariant: master suite runner deve essere RELOCATABLE.
import os,sys,re
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'backend','scripts','run_hero_skill_kit_validator_suite.py')
c=open(p,encoding='utf-8').read()
# Must use Path(__file__).resolve().parent as default for SCRIPTS_DIR.
if not re.search(r'_DEFAULT_SCRIPTS_DIR\s*=\s*Path\(__file__\)\.resolve\(\)\.parent', c):
    print('FAIL default SCRIPTS_DIR is not Path(__file__).resolve().parent'); sys.exit(1)
if 'DIVINE_VALIDATOR_SCRIPTS_DIR' not in c: print('FAIL env override DIVINE_VALIDATOR_SCRIPTS_DIR not present'); sys.exit(1)
if 'v108_POSTQA_A_RELOCATABLE_DEFAULT_RELATIVE' not in c: print('FAIL sentinel token missing'); sys.exit(1)
# Must NOT have a bare hardcoded SCRIPTS_DIR=Path('/app/backend/scripts') line.
if re.search(r"^SCRIPTS_DIR\s*=\s*Path\(\s*['\"]/app/backend/scripts['\"]\s*\)", c, re.MULTILINE):
    print('FAIL hardcoded SCRIPTS_DIR=Path("/app/backend/scripts") still present as default'); sys.exit(1)
print('PASS — v108_POSTQA_A invariant: master suite runner is relocatable (default relative)'); sys.exit(0)
