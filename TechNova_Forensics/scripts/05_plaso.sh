#!/bin/bash
# Super-timeline of both workstation images with Plaso (log2timeline + psort)
cd "$(dirname "$0")/.."; O=outputs/timeline; mkdir -p $O
log2timeline --version > $O/00_plaso_version.txt 2>&1
for h in WS01_jharris WS02_mpatel; do
  log2timeline --status_view none --partitions all --storage_file $O/$h.plaso evidence/working/$h.dd > $O/$h.log2timeline.log 2>&1
  pinfo $O/$h.plaso > $O/$h.pinfo.txt 2>&1
  psort --status_view none -o dynamic -w $O/$h.timeline.csv $O/$h.plaso "date > '2026-11-09 00:00:00'" > $O/$h.psort.log 2>&1
done
