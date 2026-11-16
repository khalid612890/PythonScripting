#!/bin/bash
# FS01 memory analysis with Volatility 3 (Linux symbols: Ubuntu 6.8.0-31-generic ISF)
cd "$(dirname "$0")/.."; M=evidence/working/FS01_memory.raw; O=outputs/memory; mkdir -p $O/dump
vol --version > $O/00_vol_version.txt 2>&1
for pl in banners.Banners linux.pslist linux.pstree linux.psaux linux.bash linux.lsof linux.sockstat linux.envars linux.malfind linux.elfs linux.check_syscall linux.lsmod; do
  echo "\$ vol -f $M $pl" > $O/$pl.txt; vol -q -f $M $pl >> $O/$pl.txt 2>&1; done
PID=$(awk '$4=="kworker_upd"{print $2; exit}' $O/linux.pslist.txt)
vol -q -f $M -o $O/dump linux.pslist --pid $PID --dump > $O/linux.pslist_dump_$PID.txt 2>&1
vol -q -f $M linux.vmayarascan --yara-file scripts/novalock.yar --pid $PID > $O/linux.vmayarascan.txt 2>&1 || true
