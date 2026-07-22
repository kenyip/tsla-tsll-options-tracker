"""Stress-rotation selector: leaders + fresh unstressed multi-leg; ledger excludes re-stress."""
from __future__ import annotations

import json
from pathlib import Path

import scripts.trader_select_stress_hyps as sel


def test_rotation_ledger_excludes_fresh_pick(tmp_path: Path, monkeypatch):
    repo = tmp_path
    shortlist = {
        "shortlist": [
            {
                "hyp_id": "hyp_dna_bac_put_credit_spread_leader",
                "structure": "put_credit_spread",
                "symbol": "BAC",
                "stress_priority": True,
                "full_pnl": 500,
            },
            {
                "hyp_id": "hyp_dna_pltr_put_credit_spread_leader",
                "structure": "put_credit_spread",
                "symbol": "PLTR",
                "stress_priority": True,
                "full_pnl": 400,
            },
        ]
    }
    bootstrap = repo / "reports" / "bootstrap"
    bootstrap.mkdir(parents=True)
    (bootstrap / "QUALITY_SHORTLIST.json").write_text(json.dumps(shortlist), encoding="utf-8")
    # already stressed fresh id
    (bootstrap / "STRESS_ROTATION.json").write_text(
        json.dumps(
            {
                "by_hyp_id": {
                    "hyp_dna_mu_put_credit_spread_done": {
                        "hyp_id": "hyp_dna_mu_put_credit_spread_done",
                        "reject_reason": "B4 fail",
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    # no hyp yaml → registry path empty; evolve logs supply fresh
    log_dir = repo / ".cache" / "platform" / "quality_residual"
    log_dir.mkdir(parents=True)
    (log_dir / "evolve_dr_test.log").write_text(
        "SHIP                 500.00     40  call_credit_spread/NFLX  positive_sim\n"
        "SHIP                 100.00     20  put_credit_spread/MU  positive_sim\n"
        "created: hyp_dna_nflx_call_credit_spread_fresh1, hyp_dna_mu_put_credit_spread_done\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(sel, "_REPO", repo)
    monkeypatch.setattr(sel, "_SHORTLIST", bootstrap / "QUALITY_SHORTLIST.json")
    monkeypatch.setattr(sel, "_HYPS", repo / "missing_hyps.yaml")
    monkeypatch.setattr(sel, "_EVOLVE_LOG_DIR", log_dir)
    monkeypatch.setattr(sel, "_ROTATION", bootstrap / "STRESS_ROTATION.json")

    res = sel.select_stress_hyps(limit=4, n_leaders=2, include_logs=True)
    ids = res["hyp_ids"]
    assert ids[0] == "hyp_dna_bac_put_credit_spread_leader"
    assert ids[1] == "hyp_dna_pltr_put_credit_spread_leader"
    assert "hyp_dna_nflx_call_credit_spread_fresh1" in ids
    assert "hyp_dna_mu_put_credit_spread_done" not in ids


def test_ingest_marks_rejects_and_ranks_leader(tmp_path: Path, monkeypatch):
    import scripts.trader_ingest_stress_rotation as ing

    repo = tmp_path
    bootstrap = repo / "reports" / "bootstrap"
    bootstrap.mkdir(parents=True)
    regime = {
        "results": [
            {
                "hyp_id": "hyp_a_bac",
                "symbol": "BAC",
                "structure": "put_credit_spread",
                "full_history": {"pnl": 500, "n_trades": 40, "verdict": "SHIP", "max_loss_usd": 160},
                "summary": {
                    "regime_hold": True,
                    "n_negative_n_ge_3": 1,
                    "max_dd_across_windows": 100,
                    "worst_window_pnl": -20,
                },
            },
            {
                "hyp_id": "hyp_b_mu",
                "symbol": "MU",
                "structure": "put_credit_spread",
                "full_history": {"pnl": 800, "n_trades": 100, "verdict": "SHIP", "max_loss_usd": 200},
                "summary": {
                    "regime_hold": True,
                    "n_negative_n_ge_3": 5,
                    "max_dd_across_windows": 270,
                    "worst_window_pnl": -180,
                },
            },
        ]
    }
    cost = {
        "summaries": [
            {
                "hyp": "hyp_a_bac",
                "cost_hold": True,
                "slip_5_verdict": "SHIP",
                "slip_5_pnl": 200,
                "note": "survives_5pct_slip",
            },
            {
                "hyp": "hyp_b_mu",
                "cost_hold": False,
                "slip_5_verdict": "REJECT",
                "slip_5_pnl": -600,
                "note": "fragile_at_5pct_slip",
            },
        ]
    }
    rp = tmp_path / "regime.json"
    cp = tmp_path / "cost.json"
    rp.write_text(json.dumps(regime), encoding="utf-8")
    cp.write_text(json.dumps(cost), encoding="utf-8")

    monkeypatch.setattr(ing, "_REPO", repo)
    monkeypatch.setattr(ing, "_LEDGER", bootstrap / "STRESS_ROTATION.json")
    monkeypatch.setattr(ing, "_SHORTLIST", bootstrap / "QUALITY_SHORTLIST.json")
    (bootstrap / "QUALITY_SHORTLIST.json").write_text(json.dumps({"shortlist": []}), encoding="utf-8")

    res = ing.ingest_pair(rp, cp, source="test")
    assert res["n_ledger"] == 2
    sl = ing.refresh_shortlist_from_ledger()
    data = json.loads((bootstrap / "QUALITY_SHORTLIST.json").read_text(encoding="utf-8"))
    ids = [r["hyp_id"] for r in data["shortlist"]]
    assert "hyp_a_bac" in ids
    assert "hyp_b_mu" not in ids
    assert any(r.get("hyp_id") == "hyp_b_mu" for r in data["rejected_tonight"])
    assert data["shortlist"][0]["stress_priority"] is True
