#!/usr/bin/env python3
"""Email gateway log + header analysis (Python). Supplements, does not replace, the forensic tools."""
import re, sys, email, collections, csv, os
os.chdir(os.path.join(os.path.dirname(__file__), '..')); O = 'outputs/email'; os.makedirs(O, exist_ok=True)
log = open('evidence/working/email/mx01_maillog_2026-11-09_to_15.log').read().splitlines()
msgs = collections.defaultdict(dict)
for l in log:
    m = re.match(r'(\w+ \d+ [\d:]+) mx01 \S+: \(?([0-9A-F]+)\)?:? (.*)', l)
    if not m: continue
    t, q, rest = m.groups(); d = msgs[q]; d.setdefault('time', t)
    if 'from=<' in rest: d['from'] = re.search(r'from=<([^>]*)>', rest).group(1); d['subject'] = (re.search(r'subject="([^"]*)"', rest) or [None, ''])[1]; a = re.search(r'attachment="([^"]*)"', rest); d['attachment'] = a.group(1) if a else ''
    if 'client=' in rest: d['client'] = re.search(r'client=(\S+)', rest).group(1)
    if 'Received-SPF' in rest: d['spf'] = re.search(r'Received-SPF: (\w+)', rest).group(1)
    if 'status=sent' in rest: d['to'] = re.search(r'to=<([^>]*)>', rest).group(1); d['verdict'] = 'delivered'
    if 'Quarantined' in rest: d['to'] = re.search(r'-> <([^>]*)>', rest).group(1); d['verdict'] = 'quarantined'
sus = [dict(qid=q, **d) for q, d in msgs.items() if d.get('spf') in ('fail', 'softfail') or 'technova-invoices' in d.get('from', '')]
with open(f'{O}/suspicious_messages.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['qid', 'time', 'from', 'to', 'subject', 'attachment', 'client', 'spf', 'verdict']); w.writeheader(); [w.writerow({k: s.get(k, '') for k in w.fieldnames}) for s in sus]
summ = collections.Counter(d.get('spf') for d in msgs.values())
m = email.message_from_file(open('evidence/working/email/eml/msg_3A21C4_jharris_INV-20931.eml'))
with open(f'{O}/summary.txt', 'w') as f:
    f.write(f'Total messages: {len(msgs)}\nSPF results: {dict(summ)}\nSuspicious (SPF fail/softfail or lookalike domain): {len(sus)}\n')
    f.write(f"Delivered suspicious: {sum(1 for s in sus if s.get('verdict')=='delivered')}\n\n")
    for s in sus: f.write(f"{s['time']}  {s.get('from')} -> {s.get('to')}  [{s.get('verdict')}] SPF={s.get('spf')} \"{s.get('subject')}\" {s.get('attachment','')}\n")
    f.write('\n--- Header analysis: msg_3A21C4_jharris_INV-20931.eml ---\n')
    for h in ['Return-Path', 'From', 'Reply-To', 'To', 'Subject', 'Date', 'X-Mailer', 'X-Originating-IP', 'Authentication-Results']: f.write(f'{h}: {m[h]}\n')
    for r in m.get_all('Received'): f.write(f'Received: {r}\n')
    for p in m.walk():
        if p.get_filename(): f.write(f'Attachment: {p.get_filename()} ({p.get_content_type()})\n')
print(open(f'{O}/summary.txt').read())
