#!/usr/bin/env python3
"""Builds the forensic report (DOCX) to the brief's format: A4, 1" margins, 1.5 spacing, Calibri
14/12/11 bold/bold/regular, 9pt italic figure captions. All numbers quoted come from saved tool outputs."""
import os, csv
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
os.chdir(os.path.join(os.path.dirname(__file__), '..'))
SS = 'screenshots/'
d = Document()
for s in d.sections:
    s.page_height, s.page_width = Inches(11.69), Inches(8.27)
    s.left_margin = s.right_margin = s.top_margin = s.bottom_margin = Inches(1)
st = d.styles['Normal']; st.font.name = 'Calibri'; st.font.size = Pt(11)
st.element.rPr.rFonts.set(qn('w:eastAsia'), 'Calibri'); st.paragraph_format.line_spacing = 1.5
for name, size in (('Heading 1', 14), ('Heading 2', 12), ('Title', 20)):
    h = d.styles[name]; h.font.name = 'Calibri'; h.font.size = Pt(size); h.font.bold = True; h.font.color.rgb = RGBColor(0, 0, 0)
    h.element.rPr.rFonts.set(qn('w:asciiTheme'), 'Calibri') if False else None
    rf = h.element.rPr.find(qn('w:rFonts'))
    if rf is not None:
        for a in ('w:asciiTheme', 'w:hAnsiTheme', 'w:eastAsiaTheme', 'w:cstheme'): rf.attrib.pop(qn(a), None)
    h.element.rPr.rFonts.set(qn('w:ascii'), 'Calibri'); h.element.rPr.rFonts.set(qn('w:hAnsi'), 'Calibri')
fig = [0]; tab = [0]
def H1(t): d.add_heading(t, level=1)
def H2(t): d.add_heading(t, level=2)
def P(t, bold_lead=None):
    p = d.add_paragraph()
    if bold_lead: p.add_run(bold_lead).bold = True
    p.add_run(t); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; return p
def B(items):
    for i in items:
        p = d.add_paragraph(style='List Bullet')
        if isinstance(i, tuple): p.add_run(i[0]).bold = True; p.add_run(i[1])
        else: p.add_run(i)
def cap(t, kind='Figure'):
    c = fig if kind == 'Figure' else tab; c[0] += 1
    p = d.add_paragraph(); r = p.add_run(f'{kind} {c[0]}: {t}'); r.italic = True; r.font.size = Pt(9)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.line_spacing = 1.0
def IMG(f, t, w=6.2):
    d.add_picture(SS + f, width=Inches(w)); d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER; cap(t)
def T(rows, t, widths=None, size=9):
    cap(t, 'Table')
    tb = d.add_table(rows=len(rows), cols=len(rows[0])); tb.style = 'Table Grid'
    for i, r in enumerate(rows):
        for j, v in enumerate(r):
            c = tb.cell(i, j); c.text = ''; run = c.paragraphs[0].add_run(str(v)); run.font.size = Pt(size); run.bold = (i == 0)
            c.paragraphs[0].paragraph_format.line_spacing = 1.0
            if widths: c.width = Inches(widths[j])
    d.add_paragraph()
def txt(f, n=None):
    L = [l for l in open(f, errors='replace').read().splitlines() if not l.startswith('Running as')]
    return L[:n] if n else L
def CODE(lines):
    p = d.add_paragraph(); p.paragraph_format.line_spacing = 1.0
    r = p.add_run('\n'.join(lines)); r.font.name = 'Consolas'; r.font.size = Pt(8)

hashes = [l.split() for l in txt('outputs/intake/evidence_hashes_original.txt') if l[:1].isalnum() and not l.startswith('VERIFIED')]

# ---------------- Title page ----------------
d.add_paragraph('Digital Forensic Investigation Report', style='Title')
P('Ransomware incident ("NovaLock") at TechNova Solutions')
P('Module: OMC6005UK4 Introduction to Forensic Tools & Techniques (WRIT1)\nCase reference: TechNova_IR_2026_014\n'
  'Report date: 16 November 2026\nAnalyst: [Student name / ID]\nClassification: CONFIDENTIAL. Prepared for TechNova Solutions management')
P('Note on the evidence. The assessment brief describes the evidence but does not supply the files. The analyst therefore built a '
  'reproducible lab copy of the scenario (scripts in lab_build/): two NTFS workstation disk images, a real RAM capture of a '
  'Linux file-server VM, 48 hours of genuine packet capture produced by isolated network namespaces, and email-gateway logs. '
  'The investigation then treated these files as received evidence. Every output, hash and screenshot in this report was '
  'produced by the named tool running against those files. External IP addresses use RFC 5737 documentation ranges, '
  'and the "malware" is inert.', 'Scope statement. ')
d.add_page_break()

# ---------------- I Executive summary ----------------
H1('1. Executive Summary')
P('Over the weekend of 14–16 November 2026, TechNova Solutions was hit by ransomware that the attackers call "NovaLock". '
  'Our investigation shows that the attack began four days earlier, on Thursday 12 November, when finance employee Jane Harris '
  'opened a fake invoice attached to an email. The email came from a look-alike address (technova-invoices.com) and failed the '
  'company email system\'s sender checks, but it was still delivered. Opening the document installed hidden remote-control '
  'software on her computer (WS01). That software then contacted the attackers\' server about every ten minutes.')
P('Using the login of the shared "itsupport" account, the attackers read five confidential files from the main file server '
  '(FS01), including payroll, HR records and client contracts. On Sunday 15 November at 01:20 UTC they uploaded a 1.8 MB '
  'archive of these files to an external server. Our ransomware investigation therefore also involves a data breach. '
  'The attackers then copied the ransomware to a second PC (WS02), opened a hidden back door on FS01, and on Monday between '
  '02:03 and 02:10 UTC encrypted documents on all three machines and left ransom notes demanding 0.85 Bitcoin.')
P('Some original documents could be recovered from deleted disk space, and the attackers\' tools, addresses and wallet were '
  'identified. We recommend that TechNova: does not pay the ransom; rebuilds the three affected systems; resets all passwords, '
  'starting with "itsupport"; reports the data breach to the Ministry of Transport, Communications and IT and to affected clients, as Oman\'s data-protection law requires; blocks '
  'macro-enabled Office files from email; and deploys multi-factor authentication, offline backups and network monitoring. '
  'The attack would most likely have been stopped at several points by these controls.')
# ---------------- II Introduction ----------------
H1('2. Introduction')
P('TechNova Solutions is a small IT-consulting firm. On Monday 16 November 2026 staff found their files on the shared drive '
  'and desktops replaced with encrypted copies and ransom notes. The IT manager reported overnight outbound traffic, '
  'antivirus alerts that a user dismissed, and a recent wave of suspicious emails. The analyst was engaged as an external examiner to:')
B(['identify the initial point of compromise and attack vector;', 'reconstruct the timeline and how the ransomware spread;',
   'assess which systems and data were affected or exfiltrated;', 'recover evidence of the attacker\'s identity and methods; and',
   'report findings and recommendations to professional standards.'])
P('All times are UTC (Oman local time is UTC+4). Hosts: WS01 (jharris, 10.10.10.21), WS02 (mpatel, 10.10.10.22), FS01 file server (10.10.10.5), DC01/DNS (10.10.10.2).')

# ---------------- III Methodology ----------------
H1('3. Methodology')
H2('3.1 Standards and process')
P('The work followed the four ACPO Good Practice Guide principles (ACPO, 2012) and the NIST SP 800-86 collection, examination, '
  'analysis and reporting stages (Kent et al., 2006). Incident handling followed the SANS PICERL model. In practice this meant:')
B([('ACPO 1 – no change to evidence: ', 'originals were hashed (MD5 + SHA-256), made read-only (chmod a-w), and all work was done on '
    'verified working copies (scripts/00_intake_hash.sh).'),
   ('ACPO 2 – competence: ', 'only established, peer-reviewed tools were used, and versions were recorded (outputs/install/tool_versions.txt).'),
   ('ACPO 3 – audit trail: ', 'every step is a script whose command line is written at the top of each output file, so a third party can repeat it.'),
   ('ACPO 4 – responsibility: ', 'the examiner kept the case log and chain-of-custody record (Appendix A).')])
H2('3.2 Tool selection and justification')
P('Open-source tools were preferred because their source can be inspected, which supports the reliability that Daubert/ISO 27037 '
  'expect, and because they cost nothing for a small firm. Each type of evidence was matched to a dedicated tool. Python was used only '
  'to automate, hash, merge and report. It did not replace any forensic tool. Table 1 lists what was actually run.')
T([['Tool (version)', 'Status', 'Evidence', 'Purpose / justification'],
   ['The Sleuth Kit 4.12.1', 'Used', 'WS01, WS02', 'mmls/fsstat/fls/istat/icat/tsk_recover/mactime/srch_strings/hfind: partition and NTFS MFT analysis, deleted-file recovery; court-accepted CLI, scriptable'],
   ['Autopsy 2.24 (TSK web GUI)', 'Used (after patch)', 'WS01, WS02', 'Case management, image MD5 verification, browsing, keyword search, hash-alert DB; visual corroboration of TSK'],
   ['Volatility 3 v2.28.2', 'Used', 'FS01 RAM', 'linux.pslist/pstree/psaux/sockstat/lsof/envars/malfind/proc.Maps/vmayarascan: processes, sockets, injected code'],
   ['Wireshark / TShark 4.2.2', 'Used', 'PCAP', 'Protocol hierarchy, conversations, DNS/HTTP/SMB2/NTLMSSP fields, TCP stream reassembly, object export'],
   ['Zeek 9.0.1', 'Used', 'PCAP', 'conn/dns/http/files/smb_files/ntlm logs for fast, high-level traffic triage'],
   ['YARA 4.5.0', 'Used', 'Files + RAM', 'Custom rules (scripts/novalock.yar) for the ransomware and macro downloader; also used inside Volatility'],
   ['ExifTool 12.76', 'Used', 'Attachment, payload', 'Document metadata (author, company, creation time) linking attacker tooling'],
   ['Plaso 20261027', 'Used (partial)', 'WS01, WS02', 'log2timeline/psort super-timeline of file-system events; Chrome parser failed (see 6.2)'],
   ['Python 3.13', 'Used (supporting)', 'Email, all', 'Mail-log parsing, header analysis, timeline merge, screenshot rendering, report build'],
   ['Autopsy 4.x, FTK Imager, EnCase, Magnet AXIOM', 'Discussed only', '–', 'Autopsy 4 is a Java desktop GUI not packaged for this headless Linux host; FTK Imager/EnCase/AXIOM are commercial/Windows (comparison only)'],
   ['Eric Zimmerman tools (MFTECmd, PECmd, EvtxECmd)', 'Discussed only', '–', 'Not used: the lab images contain no Prefetch, registry hives or EVTX logs to parse; TSK istat/Plaso covered the MFT']],
  'Forensic tools – used, partly successful, and discussed only', [1.4, 0.9, 0.8, 3.1], 8)
H2('3.3 Acquisition and working environment')
P('Analysis ran on an isolated Ubuntu 24.04 forensic VM. Tools came from the official Ubuntu repositories (sleuthkit, autopsy, '
  'tshark/wireshark, yara, exiftool), the Zeek OBS repository (zeek-lts), and PyPI (volatility3, plaso). Disk images were '
  'treated as raw (dd) physical acquisitions, and the memory image as a raw physical capture (QEMU pmemsave, comparable to '
  'LiME/AVML on a live server). Volatility 3 needs a symbol table for the exact Linux kernel. The banners plugin identified '
  'Ubuntu 6.8.0-31-generic, and the matching ISF file was installed into the volatility3 symbols directory.')

# ---------------- IV Evidence overview ----------------
H1('4. Evidence Overview')
T([['Item', 'Description', 'Size (bytes)', 'MD5', 'SHA-256 (first 32 hex)']] +
  [[os.path.basename(h[3]), {'FS01_memory.raw': 'FS01 physical RAM, raw', 'TechNova_perimeter_48h.pcap': 'Core-switch capture 14–16 Nov (48 h)',
    'WS01_jharris.dd': 'WS01 disk, MBR + NTFS', 'WS02_mpatel.dd': 'WS02 disk, MBR + NTFS',
    'mx01_maillog_2026-11-09_to_15.log': 'Mail-gateway log, 9–15 Nov', 'msg_3A21C4_jharris_INV-20931.eml': 'Raw phishing email (export)'}.get(os.path.basename(h[3]), ''),
    h[2], h[0], h[1][:32]] for h in hashes],
  'Evidence register with intake hashes (full values: outputs/intake/evidence_hashes_original.txt)', [1.5, 1.6, 0.8, 1.2, 1.3], 7)
P('After the working copies were made, they were re-hashed and found identical to the originals ("VERIFIED" line, Figure 1). '
  'Autopsy\'s own MD5 for WS02 on import (A9638FAD…EB035C) independently matched the intake value. Originals are stored in '
  'evidence/original (read-only). In a live case they would sit on write-protected media in a sealed bag, logged in Appendix A.')
IMG('term_01_intake_hashes.png', 'Intake hashing and working-copy verification (scripts/00_intake_hash.sh)')

# ---------------- V Analysis and findings ----------------
H1('5. Analysis and Findings')
H2('5.1 Initial point of compromise and attack vector')
P('Email log (Python). The parser read 246 messages for 9–15 November. Eight came from the look-alike domain technova-invoices.com '
  'through 203.0.113.66, and all failed SPF (4 fail, 4 softfail). Five of them were delivered despite failing (Figure 2), '
  'including "URGENT: Invoice INV-20931" to jharris and mpatel at 06:14 on 12 November. The raw headers show a Reply-To '
  'address on a different domain, X-Mailer PHPMailer, and DKIM/DMARC "none". These are classic indicators of spoofing.')
IMG('term_12_email_summary.png', 'Mail-gateway analysis: SPF failures delivered to users (scripts/06_email_analysis.py)')
P('Attachment (YARA, ExifTool). The extracted Invoice_INV-20931.docm matched the Office_Macro_Downloader YARA rule '
  '(AutoOpen, WScript.Shell, powershell, DownloadString). ExifTool shows Creator "Administrator", Company "Invoice Services Ltd" '
  'and last-modified-by "DESKTOP-K4R8P1Q", created 10 Nov 21:03Z. This attacker build-machine name is a useful attribution pivot.')
P('Workstation WS01 (TSK, Plaso, icat+SQLite). The file-system timeline shows the attachment written to the Outlook cache at '
  '06:39:52 and saved to Downloads at 06:41:07. Chrome History, carved with icat, records a visit to '
  'http://cdn-update-sync.net/invoice/view.php?id=20931 at 06:42:15 (Figure 3). This is the same URL embedded in the macro. '
  'winupd.exe was created at 06:42:58, followed at 06:43:05 by a scheduled task "MicrosoftEdgeUpdateTaskCoreUA" that runs it at logon '
  '(persistence, MITRE T1053.005). The PowerShell PSReadLine history records the attacker\'s later commands. Conclusion: the initial access '
  'vector was spear-phishing with a macro-enabled attachment (T1566.001) opened on WS01. WS02 also held the attachment in cache, '
  'but there is no evidence it was opened there.')
IMG('term_15_chrome_history.png', 'Chrome History extracted with icat (MFT 89) and queried with SQLite: macro-initiated visit to C2')
H2('5.2 Command-and-control and attacker activity on the network')
P('Zeek dns.log and TShark show WS01 resolving cdn-update-sync.net 288 times, followed each time by HTTP POST /gate.php to '
  '203.0.113.66 with a PowerShell User-Agent (Figure 4). That is one beacon every ~10 minutes for the full 48 hours. '
  'The regular interval with small jitter is characteristic of automated C2, not human browsing. NTLMSSP fields show the account '
  '"itsupport" authenticating from WS01 to FS01 (14 Nov 22:10:31) and to WS02 (15 Nov 23:05:43). An "itsupport" account '
  'logging in from a finance PC at night is anomalous. A phishing email titled "Password expiry notice" had been delivered to '
  'itsupport 18 hours earlier, which is the likely, but unproven, source of the credential.')
IMG('wireshark_01_c2_beacons.png', 'Wireshark: repeated DNS lookups and POST /gate.php beacons from WS01 to 203.0.113.66')
IMG('wireshark_02_smb_lateral.png', 'Wireshark: SMB2 NTLM logon as itsupport, Shared-folder file reads on FS01 and winupd.exe written to WS02 ADMIN$')
H2('5.3 Affected data and exfiltration')
P('SMB2 Create requests (TShark, Zeek smb_files.log) show five files read from \\\\FS01\\Shared: Q3_Financial_Report.xlsx, '
  'Client_Contracts_2026.docx, Payroll_Nov2026.csv, Project_Apollo_Design.pdf and HR_Employee_Records.xlsx. On WS01, '
  'fls -d revealed a deleted %TEMP%\\tn_data.zip (MFT 100, created 15 Nov 01:18:22). icat recovered it, and its listing contains '
  'exactly these five file names (Figures 6–7). Two minutes later, at 01:20:15, WS01 sent HTTP POST /upload?f=tn_data.zip, '
  '1,801,366 bytes, to 198.51.100.23 (Figure 8). Exporting the object with tshark --export-objects produced an archive with the same '
  'SHA-256 as the copy the lab server received (4d19d74a…0318). This confirms the upload was complete. Exfiltration is therefore '
  'confirmed for payroll, HR and client data (MITRE T1560.001 archive, T1048 exfiltration over HTTP). Each is personal or '
  'commercially sensitive information.')
IMG('term_03_fls_deleted.png', 'TSK fls -d on WS01: deleted payload, staging archive and original documents')
IMG('term_04_istat_winupd.png', 'TSK istat on deleted MFT entries 100 (tn_data.zip) and 98 (winupd.exe)')
IMG('wireshark_03_exfil.png', 'Wireshark: HTTP POST of tn_data.zip (1.8 MB) to 198.51.100.23 on 15 Nov 01:20 UTC')
H2('5.4 Spread and mechanism of the ransomware')
P('Lateral movement to WS02. The SMB capture shows winupd.exe written to \\\\WS02\\ADMIN$ at 23:05:43. TSK found '
  'C:\\Windows\\winupd.exe on WS02 created four seconds later. The PowerShell history on WS01 contains the matching '
  '"wmic /node:WS02 … process call create" command (T1021.002, T1047). The deleted WS01 payload (recovered from MFT 98), the '
  'SMB-transferred copy (Wireshark object export) and the WS02 file share one SHA-256: 3ef7b9c9…5a13. This proves that a single sample '
  'spread from WS01. Its MD5 was loaded into Autopsy as an alert hash set for both hosts.')
P('File server FS01 (Volatility 3). linux.pstree/psaux (Figure 9) show a start-up script (PID 1/86) that launches '
  '"nc -l -p 4444" as a bind shell. An attacker shell (sh, PID 85) is the parent of kworker_upd (PID 92), run as '
  '"./kworker_upd /srv/samba/shared" from the hidden directory /tmp/.X11-unix/.cache. The name imitates a kernel worker thread '
  '(T1036.004 masquerading), but a real kworker has PPID 2 and no command line. linux.sockstat (Figure 10) ties PID 92 to the '
  'tcp/4444 socket and to a connection to 203.0.113.66:443. TShark\'s reassembly of the tcp/4444 stream (Figure 11) shows the exact '
  'commands sent from WS01 at 01:55:22, and at 02:09:37 FS01 sent "st=done" to the C2 with User-Agent NovaLock/2.1. '
  'linux.vmayarascan with the NovaLock rule matched the ransom-note text, the .novalock extension, the C2 domain and the Bitcoin '
  'wallet inside PID 92\'s memory (Figure 12). Process memory dumped with linux.proc.Maps also matched in a file-level YARA scan.')
IMG('term_05_vol_psaux.png', 'Volatility 3 linux.psaux: bind-shell listener and masquerading kworker_upd')
IMG('term_06_vol_sockstat.png', 'Volatility 3 linux.sockstat: kworker_upd holds the tcp/4444 shell and a socket to 203.0.113.66:443')
IMG('term_09_tshark_4444.png', 'TShark follow tcp.stream: attacker commands to FS01 on port 4444')
IMG('term_07_vol_yarascan.png', 'Volatility 3 linux.vmayarascan with scripts/novalock.yar: indicators in PID 92 memory')
H2('5.5 Affected systems and recovery')
P('Encryption on WS01 happened at 02:03:11 and on WS02 at 02:06:54 (Plaso, Figure 13). Each affected folder holds '
  '*.novalock files plus README_RESTORE_FILES.txt. The ransomware creates an encrypted copy and then deletes the original, so '
  'TSK tsk_recover restored Client_List_2026.docx and Budget_Plan_2027.xlsx on both workstations from unallocated MFT entries. '
  'Q3_Financial_Summary.xlsx could not be recovered because its MFT record had been reused. Analysis of the sample\'s strings '
  'also shows "vssadmin delete shadows /all /quiet" (T1490 inhibit recovery), which the PowerShell history confirms, so '
  'Windows shadow copies should not be relied on for recovery. Autopsy views of the encrypted Documents folder and a keyword search are in Appendix C.')
IMG('term_13_plaso_timeline.png', 'Plaso psort output (filtered): delivery, persistence and encryption events on WS01')
H2('5.6 Attack timeline')
rows = list(csv.reader(open('outputs/timeline/super_timeline_key_events.csv')))
T([['UTC', 'Source', 'Host', 'Event']] + [[r[0][5:16], r[1], r[2], r[3]] for r in rows[1:]],
  'Correlated super-timeline (outputs/timeline/super_timeline_key_events.csv)', [0.95, 0.65, 1.0, 3.6], 7.5)
H2('5.7 Indicators of compromise and attacker profile')
T([['Type', 'Indicator'],
   ['Domain / IP (C2)', 'cdn-update-sync.net, technova-invoices.com → 203.0.113.66'],
   ['IP (exfiltration)', '198.51.100.23  (POST /upload)'],
   ['Email', 'accounts@technova-invoices.com; Reply-To payments.dept77@protonmail.example; X-Mailer PHPMailer 6.8.1'],
   ['File SHA-256', 'winupd.exe 3ef7b9c90d21ec95c1971bf83154db0e4971a8a57007ac95b68027c1e9a95a13'],
   ['File names / paths', '%APPDATA%\\Microsoft\\Update\\winupd.exe; /tmp/.X11-unix/.cache/kworker_upd; *.novalock; README_RESTORE_FILES.txt'],
   ['Persistence', 'Task MicrosoftEdgeUpdateTaskCoreUA; FS01 start-up script with nc bind shell on tcp/4444'],
   ['Network signature', 'HTTP POST /gate.php, UA "NovaLock/2.1" or PowerShell 5.1; ~600 s interval'],
   ['Ransom', 'BTC bc1qnv7l0ck9x2t4h5m8r3e6w0q1z7y4u2p9s5d3f; Victim ID TN-7F3A91C2; novalock_support@onionmail.example'],
   ['Attacker host artefact', 'Document last-modified-by DESKTOP-K4R8P1Q']], 'Indicators of compromise', [1.5, 4.7], 8)
P('Identity. No real-world identity can be attributed from this evidence. The infrastructure (VPS hosting, a Proton-style reply '
  'address, an onion-mail contact) is anonymised. The wallet, the "DESKTOP-K4R8P1Q" build name and the C2 domain are the best '
  'leads for law-enforcement requests and threat-intelligence matching. The behaviour (phishing, credential reuse, double '
  'extortion: exfiltration before encryption) matches commodity ransomware-as-a-service affiliates.')

# ---------------- VI Conclusion ----------------
H1('6. Conclusion')
P('The root cause was a macro-enabled phishing attachment opened on WS01 on 12 November 2026. This was made possible by email '
  'filtering that delivered messages failing SPF and by Office macros being allowed. The attacker used a shared, over-privileged '
  '"itsupport" credential to reach FS01 and WS02, stole five confidential files on 15 November, and encrypted WS01, WS02 and '
  'the FS01 share on 16 November. All three systems are compromised, and personal data (payroll, HR) was exfiltrated, so this is '
  'a reportable data breach under Oman\'s Personal Data Protection Law (Royal Decree 6/2022). Business impact includes downtime, '
  'loss of the Q3 summary file, regulatory exposure and reputational harm with clients.')
H2('6.1 Critical evaluation of tools')
P('TSK gave the most precise disk results. It reads the MFT directly, so it showed both $STANDARD_INFORMATION and $FILE_NAME '
  'times and recovered deleted files, but it needs expert interpretation. Autopsy 2.24 made the same data easier to browse and '
  'verified image hashes, but it is old and needed patching. Volatility 3 was decisive for FS01: the masquerading process and '
  'its sockets never appear on disk. Its Linux analysis depends on an exact kernel symbol file. TShark/Wireshark gave packet-level '
  'proof (stream content, file export), while Zeek summarised 6,700 packets into readable logs within seconds. The two are '
  'complementary. YARA linked artefacts across disk, network and memory. Its rules are only as good as the analyst\'s knowledge of the sample.')
H2('6.2 Problems encountered and limitations')
B([('Autopsy 2.24 would not start ', '("Insecure directory in $ENV{PATH}") because newer Perl versions reject the empty PATH it sets in taint mode. '
    'A patched copy setting PATH=/usr/bin was used (diff in outputs/install/autopsy_patch.diff). Scripted clicking of "All Deleted Files" did not render, so TSK fls -d was used instead.'),
   ('Plaso chrome_27_history parser ', 'raised "no such table: visit_source", and no browser events were produced. The History database was extracted with icat and queried with SQLite.'),
   ('Volatility 3 linux.pslist --dump ', 'returned "Error outputting file". linux.proc.Maps --dump worked. linux.bash returned nothing because the server shell was BusyBox ash, not bash.'),
   ('Lab evidence. ', 'The evidence is a faithful but synthetic reconstruction. NTFS "MFT Modified" times show the image build time (16 Nov 11:40), the remote-shell reply shows the lab host kernel, '
    'the capture contains ICMP "port unreachable" packets from the lab DNS client, and no Windows Prefetch, registry or event logs exist. In a live case these would be examined with Eric Zimmerman\'s tools. '
    'The initial infection (12 Nov) is outside the 48-hour capture window, so it is supported by disk, browser and email evidence only.'),
   ('Encryption is simulated ', '(XOR); real NovaLock-style samples would need sandbox reverse engineering before any decryption claim.')])

# ---------------- VII Recommendations ----------------
H1('7. Recommendations')
T([['#', 'Recommendation', 'Justification (finding)', 'Priority'],
   ['1', 'Isolate and rebuild WS01, WS02 and FS01 from known-good media; remove the scheduled task and FS01 start-up backdoor', 'Persistence found (5.1, 5.4)', 'Immediate'],
   ['2', 'Block 203.0.113.66, 198.51.100.23 and the two domains at the firewall/DNS; hunt for the IOCs on all hosts', 'Active C2 (5.2)', 'Immediate'],
   ['3', 'Reset all credentials, disable the shared "itsupport" account, and use named admin accounts with MFA', 'Credential reuse (5.2)', 'Immediate'],
   ['4', 'Do not pay; restore from backups and from files recovered in this report; notify the regulator, affected staff and clients', 'Exfiltration confirmed (5.3)', 'Within 72 h'],
   ['5', 'Reject email that fails SPF/DMARC; publish DMARC p=reject; quarantine .docm/.html attachments', 'Five failing emails delivered (5.1)', 'Short term'],
   ['6', 'Disable Office macros from the internet (Group Policy); deploy EDR and stop users dismissing AV alerts', 'Macro execution; dismissed AV', 'Short term'],
   ['7', 'Keep immutable/offline 3-2-1 backups; test restores quarterly', 'Shadow copies deleted (5.5)', 'Short term'],
   ['8', 'Segment the network: block workstation-to-workstation SMB/ADMIN$ and restrict FS01 management ports', 'Lateral SMB and tcp/4444 (5.4)', 'Medium'],
   ['9', 'Deploy Zeek/IDS with egress alerting for periodic beacons and large uploads; centralise logs for 90 days', 'Beaconing undetected for 4 days', 'Medium'],
   ['10', 'Run phishing-awareness training and an incident-response plan exercise', 'User opened attachment; AV ignored', 'Ongoing']],
  'Prioritised, evidence-linked recommendations', [0.3, 2.6, 2.0, 0.9], 8)

# ---------------- References ----------------
H1('References')
for r in ['ACPO (2012) Good Practice Guide for Digital Evidence, v5. Association of Chief Police Officers.',
          'Carrier, B. (2005) File System Forensic Analysis. Boston: Addison-Wesley.',
          'ISO/IEC 27037:2012 Guidelines for identification, collection, acquisition and preservation of digital evidence.',
          'Kent, K., Chevalier, S., Grance, T. and Dang, H. (2006) NIST SP 800-86 Guide to Integrating Forensic Techniques into Incident Response.',
          'Ligh, M.H., Case, A., Levy, J. and Walters, A. (2014) The Art of Memory Forensics. Indianapolis: Wiley.',
          'MITRE (2026) ATT&CK Enterprise Matrix. Available at: https://attack.mitre.org.',
          'SANS Institute (2023) Incident Handler\'s Handbook. SANS Reading Room.',
          'Volatility Foundation (2026) Volatility 3 documentation. Available at: https://volatility3.readthedocs.io.',
          'Zeek Project (2026) Zeek documentation. Available at: https://docs.zeek.org.']:
    P(r)

# ---------------- Appendices ----------------
d.add_page_break(); H1('Appendix A – Chain of Custody and Case Log')
T([['Date/time (UTC)', 'Item', 'Action', 'By', 'Integrity check'],
   ['16-11-2026 11:40', 'All six items', 'Received into evidence store; hashed; set read-only', 'Analyst', 'MD5+SHA-256 recorded'],
   ['16-11-2026 11:40', 'All six items', 'Working copies created in evidence/working', 'Analyst', 'SHA-256 identical (VERIFIED)'],
   ['16-11-2026 11:41', 'WS01/WS02 images', 'Registered in Autopsy case TechNova_IR_2026_014 (symlink, no copy)', 'Analyst', 'Autopsy MD5 = intake MD5 (WS02)'],
   ['16-11-2026 11:41–12:00', 'Working copies', 'Examined with TSK, Volatility 3, TShark, Zeek, YARA, ExifTool, Plaso', 'Analyst', 'Originals untouched (read-only)'],
   ['16-11-2026 12:00', 'Recovered artefacts', 'Exported to outputs/ and hashed (SHA256SUMS, 04_ioc_hashes.txt)', 'Analyst', 'Hashes in Appendix B']],
  'Chain-of-custody record', [1.1, 1.1, 2.2, 0.6, 1.2], 8)
H1('Appendix B – Evidence and Artefact Hashes')
CODE(txt('outputs/intake/evidence_hashes_original.txt'))
CODE(txt('outputs/malware/04_ioc_hashes.txt'))
H1('Appendix C – Additional Screenshots')
for f, t in [('autopsy_01_new_case.png', 'Autopsy 2.24: creating case TechNova_IR_2026_014'),
             ('autopsy_02_add_host_WS01.png', 'Autopsy: host WS01 with NovaLock alert hash database'),
             ('autopsy_04_image_details_WS02.png', 'Autopsy: image import – partition detection'),
             ('autopsy_05_image_added_WS02.png', 'Autopsy: WS02 image added, MD5 calculated on import'),
             ('autopsy_WS01_10_fs_details.png', 'Autopsy Image Details (NTFS file-system statistics), WS01'),
             ('autopsy_WS01_11_documents_encrypted.png', 'Autopsy File Analysis: encrypted Documents folder on WS01'),
             ('autopsy_WS01_13_meta_winupd_deleted.png', 'Autopsy Meta Data view of deleted MFT entry 98 (winupd.exe)'),
             ('autopsy_WS01_15_keyword_search.png', 'Autopsy keyword search: 5 hits for "cdn-update-sync" in WS01'),
             ('autopsy_WS02_15_keyword_search.png', 'Autopsy keyword search for "NOVALOCK" in WS02'),
             ('term_02_mmls.png', 'TSK mmls partition layout of WS01'),
             ('term_08_tshark_http.png', 'TShark HTTP request extraction (excerpt)'),
             ('term_10_yara_files.png', 'YARA rule matches on recovered, exported and dumped artefacts'),
             ('term_11_exiftool.png', 'ExifTool metadata for the phishing attachment and recovered files'),
             ('term_14_zeek_smb.png', 'Zeek smb_files.log'),
             ('wireshark_04_fs01_shell.png', 'Wireshark: tcp/4444 shell and FS01 "st=done" check-in')]:
    if os.path.exists(SS + f): IMG(f, t, 5.8)
H1('Appendix D – Tool Outputs and Scripts')
P('Supporting files are provided with this report: scripts/ (00_intake_hash.sh, 01_disk_tsk.sh, 02_memory_vol3.sh, 03_network.sh, '
  '04_malware_yara_exif.sh, 05_plaso.sh, 06_email_analysis.py, 07_super_timeline.py, novalock.yar, autopsy_drive.js), '
  'outputs/ (raw output of every command, Zeek logs, Plaso storage files and CSV timelines, recovered and exported files), and '
  'lab_build/ (the scripts that generated the simulated evidence). Tool versions: outputs/install/tool_versions.txt.')
CODE(open('scripts/novalock.yar').read().splitlines())
H1('Appendix E – Glossary')
T([['Term', 'Meaning'], ['C2', 'Command-and-control server the malware reports to'], ['Exfiltration', 'Unauthorised copying of data out of the organisation'],
   ['MFT', 'Master File Table – NTFS index of every file, kept after deletion until reused'], ['Hash (SHA-256/MD5)', 'Digital fingerprint proving a file is unchanged'],
   ['IOC', 'Indicator of compromise – an observable sign of the attack'], ['Lateral movement', 'Attacker moving from one internal system to another'],
   ['SPF/DKIM/DMARC', 'Email sender-authentication checks'], ['YARA', 'Pattern-matching language for identifying malware']], 'Glossary', [1.6, 4.6], 9)
os.makedirs('report', exist_ok=True)
d.save('report/TechNova_Forensic_Report.docx'); print('saved report')
