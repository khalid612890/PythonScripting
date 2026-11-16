#!/bin/bash
# Workstation disk analysis with The Sleuth Kit (TSK). Runs against WORKING copies only.
set -e; cd "$(dirname "$0")/.."; O=outputs/disk; mkdir -p $O/recovered
for img in WS01_jharris WS02_mpatel; do
  I=evidence/working/$img.dd; P=$O/$img; mkdir -p $P
  { echo "\$ img_stat $I"; img_stat $I; } > $P/01_img_stat.txt
  { echo "\$ mmls $I"; mmls $I; } > $P/02_mmls.txt
  { echo "\$ fsstat -o 2048 $I"; fsstat -o 2048 $I; } > $P/03_fsstat.txt
  { echo "\$ fls -o 2048 -r -p -l $I"; fls -o 2048 -r -p -l $I; } > $P/04_fls_all.txt
  { echo "\$ fls -o 2048 -r -d -p $I   (deleted entries)"; fls -o 2048 -r -d -p $I; } > $P/05_fls_deleted.txt
  fls -o 2048 -r -m C: $I > $P/06_bodyfile.txt
  { echo "\$ mactime -b bodyfile -d -y -z UTC 2026-11-01"; mactime -b $P/06_bodyfile.txt -d -y -z UTC 2026-11-01; } > $P/07_mactime.csv
  { echo "\$ tsk_recover -o 2048 $I $O/recovered/$img  (unallocated only)"; tsk_recover -o 2048 $I $O/recovered/$img; } > $P/08_tsk_recover.txt
  # istat for every deleted, named file
  grep -E '^\S+ \* [0-9]+-128' $P/05_fls_deleted.txt | sed -E 's/^\S+ \* ([0-9]+)-128-[0-9]+:\t(.*)$/\1\t\2/' | while IFS=$'\t' read inode name; do
     { echo "\$ istat -o 2048 $I $inode   # $name"; istat -o 2048 $I $inode; echo; } >> $P/09_istat_deleted.txt; done
  { echo "\$ srch_strings -t d $I | grep -iE 'novalock|cdn-update-sync|198.51.100|bc1q'"; srch_strings -t d $I | grep -iE 'novalock|cdn-update-sync|198\.51\.100|bc1q' | sort -u -k2 | head -40; } > $P/10_strings_ioc.txt
done
# targeted icat extraction of key deleted artefacts from WS01
I=evidence/working/WS01_jharris.dd; mkdir -p $O/recovered/icat
for pair in "98:winupd.exe" "100:tn_data.zip"; do icat -o 2048 -r $I ${pair%%:*} > $O/recovered/icat/WS01_${pair#*:}; done
sha256sum $O/recovered/icat/* > $O/recovered/icat/SHA256SUMS.txt
