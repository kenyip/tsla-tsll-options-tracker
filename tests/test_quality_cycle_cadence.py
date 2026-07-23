"""Cadence / sprint helpers for quality_cycle."""
from __future__ import annotations

import os
from pathlib import Path

import scripts.trader_quality_cycle as qc


def test_due_cadence():
    assert qc._due(1, 1) is True
    assert qc._due(1, 7) is True
    assert qc._due(3, 3) is True
    assert qc._due(3, 6) is True
    assert qc._due(3, 1) is False
    assert qc._due(3, 2) is False
    assert qc._due(0, 5) is True  # treated as every 1


def test_paper_book_snapshot_reads_working(tmp_path, monkeypatch):
    ledger = tmp_path / "paper_ledger.json"
    ledger.write_text(
        """
{
  "orders": {
    "a": {"status": "working", "max_loss_usd": 100, "tag": "real"},
    "b": {"status": "working", "max_loss_usd": 200, "tag": "real"},
    "s": {"status": "working", "max_loss_usd": 1, "tag": "m0_stub:smoke_test"}
  }
}
""".strip()
    )
    monkeypatch.setattr(qc, "_LEDGER", ledger)
    snap = qc._paper_book_snapshot()
    assert snap["working"] == 2
    assert snap["book_full"] is True
    assert snap["open_risk_usd"] == 300.0


def test_campaign_skip_when_book_full(monkeypatch):
    # Simulate decision logic used in run_cycle without running evolves
    book = {"working": 2, "book_full": True, "has_book": True, "open_risk_usd": 350.0}
    monkeypatch.setenv("TRADER_QC_CAMPAIGN_EVERY", "3")
    monkeypatch.setenv("TRADER_QC_PAPER_EVERY", "3")
    monkeypatch.setenv("TRADER_QC_FORCE_PAPER", "0")
    force = False
    paper_every = 3
    campaign_every = 3
    for cycle_n, expect_campaign in [(1, False), (2, False), (3, True), (4, False)]:
        run_campaign = force or (not book["book_full"]) or qc._due(campaign_every, cycle_n)
        assert run_campaign is expect_campaign, cycle_n
