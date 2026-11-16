#!/usr/bin/env python3
"""Builds the 5-10 minute non-technical presentation (PPTX)."""
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
os.chdir(os.path.join(os.path.dirname(__file__), '..'))
NAVY, RED, GREY, WHITE = RGBColor(0x14, 0x2B, 0x4C), RGBColor(0xC0, 0x39, 0x2B), RGBColor(0x55, 0x5F, 0x6B), RGBColor(255, 255, 255)
pr = Presentation(); pr.slide_width, pr.slide_height = Inches(13.333), Inches(7.5)
blank = pr.slide_layouts[6]
def box(s, x, y, w, h, text, size=18, color=GREY, bold=False, fill=None, fc=None):
    sh = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h)) if fill else s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    if fill: sh.fill.solid(); sh.fill.fore_color.rgb = fill; sh.line.fill.background()
    tf = sh.text_frame; tf.word_wrap = True
    for i, line in enumerate(text.split('\n')):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        r = p.add_run(); r.text = line; r.font.size = Pt(size); r.font.bold = bold; r.font.name = 'Calibri'; r.font.color.rgb = fc or color
    return sh
def slide(title, notes=''):
    s = pr.slides.add_slide(blank)
    box(s, 0, 0, 13.333, 1.0, '', fill=NAVY); box(s, 0.5, 0.18, 12, 0.7, title, 30, bold=True, fc=WHITE)
    s.notes_slide.notes_text_frame.text = notes; return s
def bullets(s, items, x=0.6, y=1.4, w=12, size=22):
    box(s, x, y, w, 5.5, '\n'.join('•  ' + i for i in items), size)
def pic(s, f, x, y, w): s.shapes.add_picture('screenshots/' + f, Inches(x), Inches(y), width=Inches(w))

s = pr.slides.add_slide(blank); box(s, 0, 0, 13.333, 7.5, '', fill=NAVY)
box(s, 0.8, 2.2, 11.5, 1.2, 'TechNova Solutions – Ransomware Investigation', 40, bold=True, fc=WHITE)
box(s, 0.8, 3.5, 11.5, 1.5, 'What happened, what was taken, and what to do next\nCase TechNova_IR_2026_014  ·  16 November 2026  ·  [Student name]', 20, fc=WHITE)
s.notes_slide.notes_text_frame.text = 'Introduce yourself as the external analyst. 30 seconds. This is for managers, so the technical detail is in the report.'

s = slide('What happened – in one minute', 'Keep it simple: one email led to three encrypted systems and stolen data.')
for i, (t, d) in enumerate([('Thu 12 Nov', 'Fake invoice email opened on Jane\'s PC'), ('12–15 Nov', 'Hidden remote control; attackers explore'),
                            ('Sun 15 Nov', 'Confidential files stolen (1.8 MB)'), ('Mon 16 Nov', 'Files encrypted on 3 systems; ransom note')]):
    box(s, 0.6 + i * 3.15, 1.6, 2.9, 0.8, t, 22, bold=True, fill=RED if i in (2, 3) else NAVY, fc=WHITE)
    box(s, 0.6 + i * 3.15, 2.5, 2.9, 1.6, d, 20)
box(s, 0.6, 4.6, 12, 2, 'The attackers were inside for 4 days before anyone noticed.\nThis was a data breach as well as a ransomware attack ("double extortion").', 24, color=NAVY, bold=True)

s = slide('How we investigated', 'Stress evidence integrity: everything was fingerprinted before and after, and we only worked on copies.')
bullets(s, ['Fingerprinted (hashed) every piece of evidence and worked only on verified copies – ACPO & NIST standards',
            'Workstation disks: Autopsy & The Sleuth Kit – recovered deleted files',
            'File-server memory: Volatility 3 – found the hidden ransomware process',
            'Network traffic: Wireshark, TShark & Zeek – traced the stolen data leaving',
            'Email logs, malware & timeline: Python, YARA, ExifTool, Plaso',
            'All tools are open-source, free and accepted in court'], size=21)

s = slide('How they got in', 'Show the email. The warning signs were there: the sender failed the email checks but was delivered anyway.')
bullets(s, ['Email from "technova-invoices.com" – a look-alike of our name', 'It failed the email security checks but was still delivered',
            '"Enable content" ran a hidden program', '8 such emails in one week; 5 reached inboxes'], w=5.6, size=20)
pic(s, 'term_12_email_summary.png', 6.3, 1.4, 6.8)

s = slide('What was stolen', 'Be clear: payroll and HR data belong to real people, so we must notify the authorities and affected parties.')
for i, f in enumerate(['Payroll (Nov 2026)', 'HR employee records', 'Client contracts', 'Q3 financial report', 'Project Apollo design']):
    box(s, 0.6, 1.5 + i * 0.85, 4.6, 0.7, f, 20, bold=True, fill=RED, fc=WHITE)
pic(s, 'wireshark_03_exfil.png', 5.6, 1.5, 7.3)
box(s, 5.6, 6.3, 7.3, 0.8, 'Sent to an outside server on Sun 15 Nov, 01:20 UTC – the network recording proves it', 16)

s = slide('How it spread', 'One shared IT account opened every door.')
bullets(s, ['A shared "itsupport" password let the attacker into the file server and a second PC',
            'The same ransomware file (identical fingerprint) was found on WS01, WS02 and in the network traffic',
            'On the file server it hid under a fake system name ("kworker_upd")'], w=6, size=20)
pic(s, 'term_05_vol_psaux.png', 6.8, 1.5, 6.2)

s = slide('Impact', 'Summarise the damage honestly, including what we could and could not recover.')
bullets(s, ['3 systems compromised: WS01, WS02 and the FS01 file server',
            'Documents encrypted; some originals recovered from deleted space, one file lost',
            'Personal data stolen → reportable under Oman\'s Personal Data Protection Law',
            'Paying 0.85 BTC would not guarantee recovery or stop the leak'])

s = slide('What we recommend', 'Spend most of the time here. Link each action to what we found.')
for i, (h, t) in enumerate([('Now', 'Isolate & rebuild the 3 systems · block attacker addresses · reset all passwords · do not pay'),
                            ('This month', 'Block emails that fail checks · switch off Office macros · offline backups · MFA'),
                            ('This quarter', 'Separate the network · monitor traffic for beacons · staff phishing training')]):
    box(s, 0.6, 1.5 + i * 1.8, 2.6, 1.4, h, 26, bold=True, fill=[RED, NAVY, GREY][i], fc=WHITE)
    box(s, 3.4, 1.6 + i * 1.8, 9.4, 1.4, t, 21)

s = slide('Questions', 'Invite questions. Full technical evidence is in the report appendices.')
box(s, 0.6, 2.2, 12, 2, 'Key message: one email, one shared password, four unnoticed days.\nSimple controls would have stopped this attack at several points.', 28, color=NAVY, bold=True)
pr.save('report/TechNova_Presentation.pptx'); print('saved slides')
