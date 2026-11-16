#!/bin/bash
# Network analysis: TShark (Wireshark CLI) + Zeek
cd "$(dirname "$0")/.."; P=evidence/working/TechNova_perimeter_48h.pcap; O=outputs/network; mkdir -p $O/zeek $O/export_http
t(){ n=$1; shift; { echo "\$ tshark -r $P $*"; tshark -r $P "$@"; } > $O/$n.txt 2>&1; }
capinfos $P > $O/00_capinfos.txt
t 01_protocol_hierarchy -q -z io,phs
t 02_ip_conversations -q -z conv,ip
t 03_dns_queries -Y "dns.flags.response==0" -T fields -e frame.time -e ip.src -e dns.qry.name
t 04_http_requests -Y http.request -T fields -e frame.time -e ip.src -e ip.dst -e http.host -e http.request.method -e http.request.uri -e http.user_agent -e http.content_length
t 05_smb2_files -Y "smb2.cmd==5 && smb2.filename" -T fields -e frame.time -e ip.src -e ip.dst -e smb2.tree -e smb2.filename
t 06_smb2_sessions -Y "ntlmssp.auth.username" -T fields -e frame.time -e ip.src -e ip.dst -e ntlmssp.auth.domain -e ntlmssp.auth.username
t 07_tcp4444_stream -q -z follow,tcp,ascii,"$(tshark -r $P -Y 'tcp.port==4444' -T fields -e tcp.stream -c1)"
t 08_beacon_count -Y 'http.request.uri=="/gate.php"' -T fields -e ip.src | sort | uniq -c
tshark -r $P --export-objects http,$O/export_http > /dev/null 2>&1
tshark -r $P --export-objects smb,$O/export_smb > /dev/null 2>&1
sha256sum $O/export_http/* $O/export_smb/* > $O/09_exported_objects_sha256.txt 2>/dev/null
( cd $O/zeek && /opt/zeek/bin/zeek -C -r ../../../$P LogAscii::use_json=F >/dev/null 2>&1 )
/opt/zeek/bin/zeek --version > $O/zeek/zeek_version.txt
