#!/usr/bin/env python3
"""
SE5 — Physical Audit Lab Kit (engine)
Authorized assessment scoping, checklist generation, and report building.

Anti-abuse by default:
  * requires explicit --lab-root, --target-org OWN, and a completed
    AuthorizationRecord before any plan/report is produced
  * no force / break-in / bypass logic — only scoping, checklists and reporting
  * all content watermarked and uses synthetic (.example) site names
"""

import argparse
import json
import sys
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional

WATERMARK = "SIMULATION / AUTHORIZED TRAINING ONLY"


class GuardError(Exception):
    pass


class LabGuard:
    def __init__(self, lab_root=None, target_org="OWN"):
        if not lab_root:
            raise GuardError("Explicit --lab-root is required.")
        if target_org != "OWN":
            raise GuardError("Only --target-org OWN is permitted in lab mode.")
        self.lab_root = Path(lab_root)
        self.reports = self.lab_root / "reports"
        self.reports.mkdir(parents=True, exist_ok=True)

    def watermark(self, text):
        return f"[{WATERMARK}]\n{text}"


REQUIRED_AUTH_FIELDS = {
    "site": "synthetic site name (must end in .example)",
    "engaging_org": "organization commissioning the audit",
    "authorized_testers": "list of named, approved testers",
    "scope": "doors/areas explicitly in scope",
    "test_window_start": "YYYY-MM-DD start of test window",
    "test_window_end": "YYYY-MM-DD end of test window",
    "legal_reviewed_by": "person who reviewed authorization",
    "consent_on_file": "true/false",
}


class AuthorizationRecord:
    """Mandatory authorization record; nothing runs without a complete one."""

    def __init__(self, data: Dict):
        missing = [k for k in REQUIRED_AUTH_FIELDS if k not in data]
        if missing:
            raise GuardError(f"Incomplete authorization record, missing: {missing}")
        if not str(data["site"]).lower().endswith(".example"):
            raise GuardError(f"Refusing site '{data['site']}': only synthetic .example names.")
        if str(data.get("consent_on_file", "")).lower() != "true":
            raise GuardError("Authorization record requires consent_on_file = true.")
        try:
            start = date.fromisoformat(data["test_window_start"])
            end = date.fromisoformat(data["test_window_end"])
            if end < start:
                raise GuardError("Test window end precedes start.")
        except ValueError as e:
            raise GuardError(f"Authorization record date problem: {e}")
        self.data = data
        self.data["watermark"] = WATERMARK

    def validated(self) -> Dict:
        return self.data


class AssetInventory:
    """Synthetic asset / access-point inventory for scoping."""

    ASSETS = [
        {"tag": "A-01", "type": "server rack", "location": "data-center-1.example",
         "owner": "IT Ops", "classification": "confidential", "clearance": "restricted"},
        {"tag": "A-02", "type": "workstation", "location": "floor-2.example",
         "owner": "Engineering", "classification": "internal", "clearance": "employee"},
        {"tag": "D-01", "type": "badge reader", "location": "main-entrance.example",
         "owner": "Facilities", "classification": "infrastructure", "clearance": "visitor"},
        {"tag": "D-02", "type": "man-trap", "location": "data-center-1.example",
         "owner": "IT Ops", "classification": "infrastructure", "clearance": "restricted"},
    ]

    def list(self):
        return self.ASSETS


class TailgatingTestPlan:
    """Checklist-based tailgating test plan (escort-badge checks only; no bypass)."""

    CHECKLIST = [
        "1. Confirm the escort procedure is posted at the entry point.",
        "2. Verify a visible badge is required for the tailgating probe.",
        "3. Record whether front-desk staff challenge an untagged individual.",
        "4. Time how long an unchallenged follow-through takes.",
        "5. Note whether the tailgater is asked to badge in when a badge-only lane exists.",
        "6. Do NOT attempt restraint barriers, cage doors, or emergency exits.",
        "7. Do NOT test at any point that could cause injury (automatic doors, lifts).",
        "8. Terminate immediately if security staff instruct you to stop.",
    ]

    def __init__(self, auth: AuthorizationRecord):
        self.auth = auth

    def plan(self, rounds=3):
        site = self.auth.data["site"]
        return {
            "drill_id": f"PHYSC-{self.auth.data['test_window_start'][:4]}",
            "site": site,
            "authorized_testers": self.auth.data["authorized_testers"],
            "test_window": (self.auth.data["test_window_start"],
                            self.auth.data["test_window_end"]),
            "rounds": rounds,
            "checklist": self.CHECKLIST,
            "prohibited": ["forced entry", "lock bypass", "barrier override",
                           "emergency-exit testing", "entry after denial"],
            "watermark": WATERMARK,
        }


class BadgeCheckMats:
    """Defensive badge-verification procedure checklist."""

    STEPS = [
        "Holder presents badge — inspect for validity window.",
        "Verify photo/name against directory listing (if present).",
        "Confirm clearance matches the destination zone.",
        "Spot-check PIITAG: badge id present, issued-in-date, active status.",
        "Escort policy: visitor badges grant escorted access only.",
        "Report anomalies to security desk; log challenge outcome.",
    ]

    def build(self):
        return {"procedure": "defensive badge verification",
                "steps": self.STEPS, "watermark": WATERMARK}


class AuditReport:
    """Structured report builder (authorization block is mandatory)."""

    def __init__(self, auth: AuthorizationRecord):
        self.auth = auth

    def render(self, findings: List[str], recommendations: List[str]) -> str:
        a = self.auth.data
        lines = [
            f"PHYSICAL AUDIT REPORT [{WATERMARK}]",
            "=" * 60,
            f"Site              : {a['site']}",
            f"Engaging org      : {a['engaging_org']}",
            f"Authorized testers: {', '.join(a['authorized_testers'])}",
            f"Test window       : {a['test_window_start']} → {a['test_window_end']}",
            f"Legal review      : {a['legal_reviewed_by']}",
            f"Consent on file   : {a['consent_on_file']}",
            "",
            "FINDINGS",
            "--------",
            *(f"  - {f}" for f in findings),
            "",
            "RECOMMENDATIONS",
            "--------------",
            *(f"  - {r}" for r in recommendations),
            "",
            "No forced-entry, lock-bypass or break-in activity was part of this scope.",
        ]
        return "\n".join(lines)

    def render_json(self, findings, recommendations) -> Dict:
        return {
            "authorization": self.auth.validated(),
            "findings": findings,
            "recommendations": recommendations,
            "generated": datetime.now().isoformat(),
            "watermark": WATERMARK,
        }


def _default_auth() -> Dict:
    return {
        "site": "acme-hq.example",
        "engaging_org": "Acme Lab Security (internal)",
        "authorized_testers": ["Robin Scope, DRILL badge PHY-1"],
        "scope": ["main entrance", "badge-only lane", "front-desk lobby"],
        "test_window_start": "2026-09-07",
        "test_window_end": "2026-09-09",
        "legal_reviewed_by": "internal legal counsel (simulated)",
        "consent_on_file": "true",
    }


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    p = argparse.ArgumentParser(
        prog="se5-physical-audit",
        description="Authorized physical-audit scoping/checklist kit (no break-in logic).")
    p.add_argument("--lab-root", required=True)
    p.add_argument("--target-org", default="OWN")
    p.add_argument("--auth-json", metavar="FILE", default=None,
                   help="Path to a completed authorization-record JSON.")
    p.add_argument("--demo", action="store_true",
                   help="Run offline demo using the bundled synthetic authorization record.")
    p.add_argument("--plan", action="store_true", help="Generate tailgating test plan.")
    p.add_argument("--checklist", action="store_true", help="Print defensive badge-check mat.")
    p.add_argument("--inventory", action="store_true", help="List synthetic asset inventory.")
    args = p.parse_args(argv)

    guard = LabGuard(args.lab_root, args.target_org)

    if args.demo:
        auth_data = _default_auth()
        print(f"SE5 Physical Audit Lab Kit [{WATERMARK}]")
        print("=" * 60)
    elif args.auth_json:
        auth_data = json.loads(Path(args.auth_json).read_text())
    else:
        p.error("Provide --auth-json FILE or use --demo (no unauth plan generation).")
        return 2

    auth = AuthorizationRecord(auth_data)
    print(f"\nAuthorization record validated for {auth.data['site']} "
          f"(consent={auth.data['consent_on_file']}).")

    if args.inventory or args.demo:
        print("\nSynthetic asset / access-point inventory:")
        for a in AssetInventory().list():
            print(f"  [{a['tag']}] {a['type']:<14} {a['location']:<22} "
                  f"clearance={a['clearance']}")

    if args.plan or args.demo:
        plan = TailgatingTestPlan(auth).plan(rounds=3)
        print(f"\nTailgating test plan ({plan['drill_id']}) — {plan['site']}:")
        for item in plan["checklist"]:
            print("  ", item)
        print("\nProhibited techniques (never performed):")
        for x in plan["prohibited"]:
            print("  -", x)
        (guard.reports / "tailgating_plan.json").write_text(
            json.dumps(plan, indent=2))

    if args.checklist or args.demo:
        print("\nDefensive badge-verification checklist:")
        for step in BadgeCheckMats().build()["steps"]:
            print("  *", step)

    if args.demo:
        report = AuditReport(auth)
        md = report.render(["Tailgating into lobby was challenged once by front desk.",
                            "Badge reader at badge-only lane untested (out of window)."],
                           ["Post escort policy at the badge-only lane.",
                            "Increase challenge frequency for vendor badges."])
        print("\n" + md)
        (guard.reports / "physical_audit_report.md").write_text(md)
        (guard.reports / "physical_audit_report.json").write_text(
            json.dumps(report.render_json(
                ["Tailgating into lobby was challenged once; vendor badges unchallenged."],
                ["Post escort policy; run live badge-check drills."]), indent=2))
        print(f"\nReports: {guard.reports / 'physical_audit_report.md'} , "
              f"{guard.reports / 'physical_audit_report.json'}")

    print("\nDemo complete (offline, authorized scope, synthetic data only). Exit 0.")
    return 0


if __name__ == "__main__":
    sys.exit(main())