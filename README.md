# SE5 — Physical Security Audit Kit

Authorized physical-security assessment toolkit for asset inventory, tailgating simulation, and badge-cloning risk analysis.

## Overview

- Builds an inventory of physical assets and access points with clearance levels
- Tracks lock-pick / bypass qualification for authorized testing technicians
- Generates tailgating-simulation checklists with result logging templates
- Analyzes badge-cloning risk from supplied byte samples (EDGE, HID PROX, Awid formats)
- Produces a structured physical-security audit report
- Heavy legal disclaimer — authorized testing only
- Zero dependencies — pure Python standard library

## Features

- **Asset & Access-Point Inventory**: Tag, type, location, owner, classification, lock type, clearance
- **Lock-Out Qualification Tracking**: Per-technician, per-lock-model status
- **Tailgating Simulator Checklist**: 10-step, multi-round simulation plan with grading criteria
- **Badge Risk Engine**: Parses raw byte samples into manufacturer + UID components; risk classification
- **Audit Report Generator**: Structured, sectioned report output
- **Embedded demo** — runs fully offline on sample data

## Installation

No external dependencies required — uses Python standard library only.

```bash
python3 firmware/physical_audit.py
```

## Usage

```python
from firmware.physical_audit import (AssetInventory, TailgatingSimulation,
                                     BadgeRisk, AuditReport)

report = AuditReport(site="ACME HQ", date="2026-09-04")
report.add_section("Findings", "Example finding text")
print(report.render())

risk = BadgeRisk("EDGE")
parsed = risk.parse_raw(base64_bytes)
print(risk.risk_assessment())
```

## Example Output

```
ASSET & ACCESS-POINT INVENTORY — Site
Assets: 2
  [A-01] Server Rack @ Data Center 1 owner=IT Ops (confidential)
  [A-02] Workstation @ Engineering Floor owner=Eng (internal)
Access Points: 1
  [D-01] Main Entrance lock=magnetic clearance=low

BADGE-CLONING RISK ASSESSMENT (EDGE sample)
  [EDGE]      UID=3a4f9b21 risk=HIGH  — Short UID space...
  [HID PROX]  UID=88c1e3a7 risk=HIGH  — Short UID space...
  [Awid]      UID=6d5f0a3c risk=MEDIUM — Moderate UID space...
```

## IMPORTANT: Read before use.

This toolkit is provided **exclusively** for authorized physical-security assessments. Conducting physical-security tests without written authorization is illegal and dangerous.

### Authorization Requirements

You require a signed, scoped testing agreement with the facility owner, plus approval from security leadership and legal counsel, before conducting any physical assessment. The scope must explicitly include which doors, locks, badge systems, and areas may be tested, and featured inspection time windows.

### Legal Framework

Unauthorized entry is governed by **CFAA (18 U.S.C. § 1030)** and **trespass law**, state and local **burglary and criminal trespass statutes**, and the **EU General Data Protection Regulation (GDPR)** where PII is involved. Physical-security incidents can result in arrest, prosecution, and civil liability even if no data is taken.

### Acceptable Use

- Authorized red-team physical engagements with a signed scope
- Internal security audits of facilities you own or operate
- Defensive hardening exercises with informed personnel
- Academic study and laboratory testing on your own equipment

### Prohibited Use

- Entering or testing any facility without written authorization
- Bypassing locks, doors, or badge readers on premises you do not control
- Cloning real, in-use access badges outside an authorized engagement
- Photographing or recording people without consent during exercises
- Any use that violates applicable law or terms of service

### No Warranty

This software is provided "as is" without warranty of any kind. The authors assume no liability for damages, injury, arrest, or loss arising from use or misuse of this tool.

### Responsible Disclosure

Report physical-security gaps to facility owners before public disclosure, and never publish photographs or identifiers that could enable a real attack.

## License

MIT License