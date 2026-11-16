#!/bin/bash
# Evidence intake: hash originals, make read-only, create verified working copies (ACPO Principle 1 & 3)
set -e; cd "$(dirname "$0")/.."
O=evidence/original; Wk=evidence/working; mkdir -p $Wk outputs/intake
chmod -R a-w $O
( echo "# Evidence intake hashes - $(date -u '+%F %T UTC') - analyst workstation $(hostname)"
  find $O -type f | sort | while read f; do echo "$(md5sum "$f" | cut -d' ' -f1)  $(sha256sum "$f" | cut -d' ' -f1)  $(stat -c %s "$f")  $f"; done ) | tee outputs/intake/evidence_hashes_original.txt
rm -rf $Wk; cp -a $O/. $Wk/; chmod -R u+w $Wk
( cd $O && find . -type f -exec sha256sum {} + | sort -k2 ) > /tmp/claude-0/o.sha
( cd $Wk && find . -type f -exec sha256sum {} + | sort -k2 ) > /tmp/claude-0/w.sha
diff /tmp/claude-0/o.sha /tmp/claude-0/w.sha && echo "VERIFIED: working copies identical to originals" | tee -a outputs/intake/evidence_hashes_original.txt
