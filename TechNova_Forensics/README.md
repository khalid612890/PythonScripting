# TechNova Solutions – NovaLock Ransomware Investigation (OMC6005UK4 WRIT1)

Deliverables (in `report/`):
- `TechNova_Forensic_Report.docx` / `.pdf` – the forensic report, formatted to the brief (A4, 1" margins, Calibri, 1.5 spacing)
- `TechNova_Presentation.pptx` / `.pdf` – 9-slide, non-technical presentation with speaker notes

Supporting files:
| Folder | Contents |
|---|---|
| `evidence/compressed/` | The evidence set (xz-compressed disk and memory images, PCAP, email logs) with SHA-256 sums. Decompress with `xz -dk` into `evidence/original/`, then run `scripts/00_intake_hash.sh`. |
| `scripts/` | The investigation, run in order 00 to 09. Each output file starts with the exact command that produced it. |
| `outputs/` | Raw tool output: TSK, Autopsy case locker, Volatility 3, TShark/Zeek, YARA/ExifTool, Plaso, email analysis, recovered/exported files, tool versions, Autopsy patch |
| `screenshots/` | Real Autopsy (web UI) and Wireshark (GUI) screenshots, plus renders of the saved terminal output |
| `lab_build/` | Scripts that **generated the simulated evidence**: the brief supplies no evidence files. External IPs are RFC 5737 ranges and all "malware" is inert. |

Tools actually used: The Sleuth Kit 4.12.1, Autopsy 2.24 (patched for Perl taint mode), Volatility 3 2.28.2, Wireshark/TShark 4.2.2,
Zeek 9.0.1, YARA 4.5.0, ExifTool 12.76, Plaso 20261027, Python 3.13. See report section 3.2 and 6.2 for limitations.
