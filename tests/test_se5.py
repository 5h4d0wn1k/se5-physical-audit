#!/usr/bin/env python3
"""Offline unit tests for SE5 Physical Audit Lab Kit."""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from physical_audit import (
    LabGuard, GuardError, AuthorizationRecord, AssetInventory,
    TailgatingTestPlan, BadgeCheckMats, AuditReport, WATERMARK,
)


def good_auth(**overrides):
    data = {
        "site": "acme-hq.example",
        "engaging_org": "Acme Lab Security (internal)",
        "authorized_testers": ["Robin Scope"],
        "scope": ["main entrance"],
        "test_window_start": "2026-09-07",
        "test_window_end": "2026-09-09",
        "legal_reviewed_by": "legal (simulated)",
        "consent_on_file": "true",
    }
    data.update(overrides)
    return data


class TestLabGuard(unittest.TestCase):
    def test_requires_lab_root(self):
        with self.assertRaises(GuardError):
            LabGuard(None)

    def test_requires_own(self):
        with self.assertRaises(GuardError):
            LabGuard("/tmp/x", target_org="SomeCorp")


class TestAuthorizationRecord(unittest.TestCase):
    def test_missing_field_rejected(self):
        with self.assertRaises(GuardError):
            AuthorizationRecord({k: v for k, v in good_auth().items()
                                 if k != "scope"})

    def test_real_site_rejected(self):
        with self.assertRaises(GuardError):
            AuthorizationRecord(good_auth(site="acme.com"))

    def test_consent_required(self):
        with self.assertRaises(GuardError):
            AuthorizationRecord(good_auth(consent_on_file="false"))

    def test_bad_dates_rejected(self):
        with self.assertRaises(GuardError):
            AuthorizationRecord(good_auth(test_window_end="2026-09-01"))

    def test_valid_record(self):
        rec = AuthorizationRecord(good_auth())
        self.assertEqual(rec.validated()["watermark"], WATERMARK)


class TestAssetInventory(unittest.TestCase):
    def test_all_synthetic(self):
        for a in AssetInventory().list():
            self.assertTrue(a["location"].endswith(".example"))


class TestTailgatingPlan(unittest.TestCase):
    def test_checklist_is_defensive(self):
        plan = TailgatingTestPlan(AuthorizationRecord(good_auth())).plan(rounds=3)
        self.assertTrue(plan["checklist"])
        self.assertIn("forced entry", plan["prohibited"])
        self.assertIn("lock bypass", plan["prohibited"])

    def test_requires_auth(self):
        with self.assertRaises(GuardError):
            TailgatingTestPlan(AuthorizationRecord({}))


class TestBadgeMats(unittest.TestCase):
    def test_defensive_steps(self):
        m = BadgeCheckMats().build()
        self.assertTrue(any("escort" in s.lower() for s in m["steps"]))
        self.assertEqual(m["watermark"], WATERMARK)


class TestAuditReport(unittest.TestCase):
    def test_authorization_block_present(self):
        a = AuthorizationRecord(good_auth())
        r = AuditReport(a).render(["f"], ["rec"])
        self.assertIn("Authorized testers", r)
        self.assertIn("no forced-entry", r.lower())


class TestCli(unittest.TestCase):
    def test_demo_requires_nothing_else_and_exits_zero(self):
        with tempfile.TemporaryDirectory() as td:
            from physical_audit import main
            code = main(["--lab-root", td, "--demo"])
            self.assertEqual(code, 0)
            self.assertTrue(os.path.exists(
                os.path.join(td, "reports", "physical_audit_report.json")))


if __name__ == "__main__":
    unittest.main()