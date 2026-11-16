#!/usr/bin/env python3
"""LAB BUILD SCRIPT - simulated email-gateway log (Postfix format) for 09-15 Nov 2026
plus raw .eml copies of selected messages. Attachments are inert."""
import os, sys, random, datetime as dt, base64, hashlib, zipfile, io
OUT = sys.argv[1]; os.makedirs(os.path.join(OUT, "eml"), exist_ok=True)
random.seed(42)
users = ["jharris", "mpatel", "akhan", "sbaloushi", "rthomas", "itsupport", "lnair", "hsaid"]
legit = [("noreply@microsoft.com", "40.107.22.51", "Your Microsoft 365 invoice"), ("billing@aws.amazon.com", "54.240.8.44", "AWS Billing Statement"),
         ("hr@technova.om", "10.10.10.30", "Staff meeting agenda"), ("support@zoom.us", "170.114.52.2", "Zoom webinar reminder"),
         ("info@omantel.om", "82.178.0.12", "Service notification"), ("projects@dhofar-energy.example", "192.0.2.80", "Re: Project Apollo milestones")]
phish = [  # (when, rcpt, subject, attachment, spf, dkim, verdict)
    ("2026-11-09 07:02:11", "akhan", "Overdue payment notice", "Payment_Notice.html", "softfail", "none", "quarantined"),
    ("2026-11-10 05:47:39", "rthomas", "Shared document: Q4 pricing", None, "fail", "none", "delivered"),
    ("2026-11-11 08:15:03", "sbaloushi", "Invoice INV-20877 overdue", "Invoice_INV-20877.docm", "fail", "none", "quarantined"),
    ("2026-11-12 06:14:27", "jharris", "URGENT: Invoice INV-20931 - payment due today", "Invoice_INV-20931.docm", "softfail", "none", "delivered"),
    ("2026-11-12 06:14:29", "mpatel", "URGENT: Invoice INV-20931 - payment due today", "Invoice_INV-20931.docm", "softfail", "none", "delivered"),
    ("2026-11-12 06:14:31", "lnair", "URGENT: Invoice INV-20931 - payment due today", "Invoice_INV-20931.docm", "softfail", "none", "quarantined"),
    ("2026-11-13 09:40:55", "hsaid", "Mailbox storage full - verify account", None, "fail", "none", "delivered"),
    ("2026-11-14 04:22:18", "itsupport", "Password expiry notice", None, "fail", "none", "delivered"),
]
lines = []; qn = 0x3A1F00
def qid():
    global qn; qn += random.randint(3, 40); return f"{qn:X}"
def log(t, s): lines.append((t, s))
start = dt.datetime(2026, 11, 9, 0, 0, 0)
for day in range(7):
    for _ in range(random.randint(28, 40)):
        t = start + dt.timedelta(days=day, seconds=random.randint(4 * 3600, 15 * 3600))
        frm, ip, subj = random.choice(legit); rc = random.choice(users); q = qid()
        log(t, f"mx01 postfix/smtpd[{random.randint(2000,9000)}]: {q}: client=mail-relay[{ip}]")
        log(t, f"mx01 postfix/cleanup[{random.randint(2000,9000)}]: {q}: message-id=<{hashlib.md5(q.encode()).hexdigest()[:16]}@{frm.split('@')[1]}>")
        log(t, f"mx01 policyd-spf[1201]: {q}: Received-SPF: pass (sender={frm}) client-ip={ip}")
        log(t, f"mx01 postfix/qmgr[1188]: {q}: from=<{frm}>, size={random.randint(4000,90000)}, nrcpt=1 (queue active) subject=\"{subj}\"")
        log(t + dt.timedelta(seconds=1), f"mx01 postfix/smtp[{random.randint(2000,9000)}]: {q}: to=<{rc}@technova.om>, relay=exch01.technova.local[10.10.10.3]:25, status=sent (250 2.0.0 OK)")
for when, rc, subj, att, spf, dkim, verdict in phish:
    t = dt.datetime.strptime(when, "%Y-%m-%d %H:%M:%S"); q = qid()
    frm = "accounts@technova-invoices.com"
    log(t, f"mx01 postfix/smtpd[4471]: {q}: client=vps-2391.hostkey.example[203.0.113.66]")
    log(t, f"mx01 postfix/cleanup[4472]: {q}: message-id=<{hashlib.md5(q.encode()).hexdigest()[:16]}@technova-invoices.com>")
    log(t, f"mx01 policyd-spf[1201]: {q}: Received-SPF: {spf} (technova-invoices.com: 203.0.113.66 is not designated) DKIM={dkim}")
    log(t, f"mx01 postfix/qmgr[1188]: {q}: from=<{frm}>, size={random.randint(40000,60000)}, nrcpt=1 (queue active) subject=\"{subj}\"" + (f" attachment=\"{att}\"" if att else ""))
    if verdict == "delivered":
        log(t + dt.timedelta(seconds=2), f"mx01 postfix/smtp[4480]: {q}: to=<{rc}@technova.om>, relay=exch01.technova.local[10.10.10.3]:25, status=sent (250 2.0.0 OK)")
    else:
        log(t + dt.timedelta(seconds=2), f"mx01 amavis[3301]: ({q}) Blocked BANNED/SPAM-QUARANTINE {{Quarantined}}, <{frm}> -> <{rc}@technova.om>, quarantine: spam-{q}.gz")
lines.sort()
with open(os.path.join(OUT, "mx01_maillog_2026-11-09_to_15.log"), "w") as f:
    for t, s in lines: f.write(t.strftime("%b %d %H:%M:%S ") + s + "\n")

# raw .eml of the message opened by jharris (inert attachment = same docm structure, macro text only)
sys.path.insert(0, os.path.dirname(__file__))
from build_disks import docm  # noqa  (import safe: build_disks only runs build() under __main__ guard below)
att = base64.encodebytes(docm("Administrator", "Invoice INV-20931")).decode()
eml = f"""Return-Path: <bounce-7731@vps-2391.hostkey.example>
Received: from vps-2391.hostkey.example ([203.0.113.66]) by mx01.technova.om with ESMTP id 3A21C4; Thu, 12 Nov 2026 06:14:27 +0000
Received-SPF: softfail (technova-invoices.com: 203.0.113.66 is not designated as permitted sender)
Authentication-Results: mx01.technova.om; spf=softfail smtp.mailfrom=technova-invoices.com; dkim=none; dmarc=none
From: "TechNova Accounts" <accounts@technova-invoices.com>
Reply-To: payments.dept77@protonmail.example
To: jharris@technova.om
Subject: URGENT: Invoice INV-20931 - payment due today
Date: Thu, 12 Nov 2026 10:14:20 +0400
Message-ID: <a7c1e9f04b2d6c33@technova-invoices.com>
X-Mailer: PHPMailer 6.8.1
X-Originating-IP: 203.0.113.66
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="==b0undary=="

--==b0undary==
Content-Type: text/plain; charset=utf-8

Dear Jane,

Please find attached invoice INV-20931 which is now overdue. Payment must be made today to avoid
service suspension. Open the document and click "Enable Content" to view the protected invoice.

Regards,
Accounts Department

--==b0undary==
Content-Type: application/vnd.ms-word.document.macroEnabled.12; name="Invoice_INV-20931.docm"
Content-Disposition: attachment; filename="Invoice_INV-20931.docm"
Content-Transfer-Encoding: base64

{att}
--==b0undary==--
"""
open(os.path.join(OUT, "eml", "msg_3A21C4_jharris_INV-20931.eml"), "w").write(eml)
print("email logs:", len(lines), "lines")
