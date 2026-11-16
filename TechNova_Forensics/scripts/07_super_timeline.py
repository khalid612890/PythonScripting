#!/usr/bin/env python3
"""Correlated super-timeline of key events. Each row cites the tool output it came from.
Python here only merges and sorts the findings; the events themselves came from the forensic tools."""
import csv, os
os.chdir(os.path.join(os.path.dirname(__file__), '..'))
E = [
 ("2026-11-09 07:02:11", "Email", "MX01", "First lookalike-domain phish (technova-invoices.com) to akhan - quarantined", "outputs/email/summary.txt"),
 ("2026-11-12 06:14:27", "Email", "MX01", "INV-20931 .docm phish delivered to jharris and mpatel (SPF softfail, origin 203.0.113.66)", "outputs/email/summary.txt"),
 ("2026-11-12 06:39:52", "Disk", "WS01", "Attachment written to Outlook cache Content.Outlook\\7XK2LQ9P", "outputs/timeline/WS01_jharris.timeline.csv"),
 ("2026-11-12 06:41:07", "Disk", "WS01", "Invoice_INV-20931.docm saved to Downloads (opened by user)", "outputs/timeline/WS01_jharris.timeline.csv"),
 ("2026-11-12 06:42:15", "Disk", "WS01", "Chrome visits http://cdn-update-sync.net/invoice/view.php?id=20931", "outputs/disk/WS01_jharris/12_chrome_history.txt"),
 ("2026-11-12 06:42:58", "Disk", "WS01", "Payload winupd.exe created in %APPDATA%\\Microsoft\\Update (later deleted)", "outputs/disk/WS01_jharris/09_istat_deleted.txt"),
 ("2026-11-12 06:43:05", "Disk", "WS01", "Persistence: scheduled task MicrosoftEdgeUpdateTaskCoreUA -> winupd.exe", "outputs/timeline/WS01_jharris.timeline.csv"),
 ("2026-11-12 06:52:31", "Disk", "WS02", "Same attachment cached on WS02 (no evidence it was opened)", "outputs/timeline/WS02_mpatel.timeline.csv"),
 ("2026-11-14 03:00:00", "Network", "WS01", "C2 beaconing to cdn-update-sync.net (203.0.113.66) every ~10 min - 288 POST /gate.php in 48 h", "outputs/network/08_beacon_count.txt"),
 ("2026-11-14 04:22:18", "Email", "MX01", "'Password expiry notice' phish delivered to itsupport (possible credential theft)", "outputs/email/summary.txt"),
 ("2026-11-14 22:10:31", "Network", "WS01->FS01", "SMB2 logon as itsupport; \\\\FS01\\Shared - 5 sensitive files read", "outputs/network/05_smb2_files.txt"),
 ("2026-11-15 01:18:22", "Disk", "WS01", "Staging archive %TEMP%\\tn_data.zip created (later deleted, recovered)", "outputs/disk/WS01_jharris/09_istat_deleted.txt"),
 ("2026-11-15 01:20:15", "Network", "WS01->198.51.100.23", "EXFILTRATION: HTTP POST /upload?f=tn_data.zip, 1,801,366 bytes", "outputs/network/04_http_requests.txt"),
 ("2026-11-15 23:05:43", "Network", "WS01->WS02", "Lateral movement: winupd.exe written to \\\\WS02\\ADMIN$ as itsupport", "outputs/network/zeek/smb_files.log"),
 ("2026-11-15 23:05:47", "Disk", "WS02", "C:\\Windows\\winupd.exe created (same SHA-256 as WS01 payload)", "outputs/disk/WS02_mpatel/11_winupd_hash.txt"),
 ("2026-11-16 01:55:13", "Memory", "FS01", "FS01 boots; start-up script launches nc listener on tcp/4444 (backdoor)", "outputs/memory/linux.pstree.txt"),
 ("2026-11-16 01:55:22", "Network", "WS01->FS01", "Shell on tcp/4444: id; uname; ls /srv/samba/shared; ./kworker_upd", "outputs/network/07_tcp4444_stream.txt"),
 ("2026-11-16 01:55:18", "Memory", "FS01", "kworker_upd (PID 92, parent sh PID 85) running from /tmp/.X11-unix/.cache", "outputs/memory/linux.psaux.txt"),
 ("2026-11-16 02:03:11", "Disk", "WS01", "Documents encrypted (*.novalock) + README_RESTORE_FILES.txt", "outputs/timeline/WS01_jharris.timeline.csv"),
 ("2026-11-16 02:06:54", "Disk", "WS02", "Documents encrypted (*.novalock) + ransom note", "outputs/timeline/WS02_mpatel.timeline.csv"),
 ("2026-11-16 02:09:37", "Network", "FS01->203.0.113.66", "FS01 reports 'st=done' to C2 (User-Agent NovaLock/2.1)", "outputs/network/04_http_requests.txt"),
]
E.sort()
with open('outputs/timeline/super_timeline_key_events.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['utc', 'source', 'host', 'event', 'evidence_file']); w.writerows(E)
print(len(E), 'events')
