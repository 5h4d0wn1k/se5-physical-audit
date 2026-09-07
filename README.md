# SE5 — Physical Audit Lab Kit

Authorized physical-security assessment **scoping / checklist / reporting** tool.
Plan tailgating-test rounds, print defensive badge-check materials, and build audit
reports — all locked behind a mandatory authorization record. No forced-entry, lock
bypass, or break-in logic exists in this kit.

## Features

- **AuthorizationRecord (mandatory)** — site (`.example` only), engaging org,
  named testers, in-scope doors/areas, test window, legal review, consent flag.
  Nothing is generated without a complete record.
- **Synthetic asset inventory** — assets and access points with clearance levels.
- **TailgatingTestPlan** — checklist rounds with explicit prohibited techniques.
- **BadgeCheckMats** — defensive badge-verification steps (escort policy, validation).
- **AuditReport** — Markdown + JSON reports with a mandatory authorization block.

## IMPORTANT: Read before use.

Provided **exclusively** for authorized physical-security assessments. Testing
without written authorization is illegal and dangerous.

### Authorization Requirements
- Signed, scoped testing agreement with the facility owner, security leadership,
  and legal counsel, covering which doors/locks/areas and time windows may be tested.
- `--target-org` is locked to `OWN`; site names must be synthetic (`.example`).
- `consent_on_file` must be `true` in the authorization record.
- Requests to remove these safeguards (or add bypass/break-in logic) will be refused.

### Legal Framework
- **CFAA (18 U.S.C. § 1030)**, trespass law, state/local burglary and criminal
  trespass statutes, and **GDPR** where PII is involved.

### Prohibited Use
- Testing any facility without written authorization.
- Bypassing locks, doors, or badge readers on premises you do not control.
- Cloning real, in-use badges.
- Photographing/recording people without consent during exercises.

### No Warranty
Provided "AS IS". Author accepts no liability for damages, injury, or arrest
arising from misuse.

### Responsible Disclosure
Report gaps to facility owners privately; never publish identifiers/ photographs
that could enable a real attack.

## Live Lab Test Plan

1. `python3 physical_audit.py --lab-root ./lab --demo` → exit 0; validates the
   bundled synthetic authorization record; writes MD + JSON reports.
2. `python3 physical_audit.py --lab-root ./lab --plan --auth-json auth.json` →
   generates a tailgating plan from a completed record.
3. `python3 physical_audit.py --lab-root ./lab --inventory` → lists synthetic inventory.
4. Negative: `--lab-root ./lab --target-org SomeCorp` exits non-zero; an incomplete
   `--auth-json` is also rejected.
5. `python -m unittest discover -s tests` → 13 offline tests pass.

## Metrics

- Authorization fields required: 8 (all mandatory).
- Inventory: 4 synthetic assets/access points.
- Tailgating checklist: 8 steps + 5 prohibited techniques.
- Badge-check steps: 6 defensive procedures.
- Test count: 13.

## Usage

```bash
python3 physical_audit.py --lab-root ./lab --demo
python3 physical_audit.py --lab-root ./lab --auth-json auth.json --plan
python3 physical_audit.py --lab-root ./lab --checklist
```

## License

MIT