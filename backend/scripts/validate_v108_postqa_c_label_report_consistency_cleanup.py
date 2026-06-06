#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(R,'data','design','postqa','v108_postqa_c_label_report_consistency_cleanup_v1.json')))
if d.get('new_inconsistencies_introduced_in_c'): print('FAIL new inconsistencies'); sys.exit(1)
if not d.get('consistency_check_pass',False): print('FAIL consistency'); sys.exit(1)
print('PASS — v108_POSTQA_C label report consistency cleanup'); sys.exit(0)
