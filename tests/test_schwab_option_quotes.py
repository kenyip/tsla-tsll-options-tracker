import json
import unittest
from datetime import date, datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from trader_platform.research.schwab_option_quotes import (
    credential_status,
    normalize_schwab_option_chain,
    snapshot_schwab_option_quotes,
    write_status_report,
)


class SchwabOptionQuotesTest(unittest.TestCase):
    def test_credentials_fail_closed_without_secrets(self):
        status = credential_status(env={})
        self.assertFalse(status.ready)
        self.assertIn("credentials_missing", status.reason)

    def test_credentials_ready_when_key_secret_and_refresh_present(self):
        status = credential_status(
            env={
                "SCHWAB_APP_KEY": "key",
                "SCHWAB_APP_SECRET": "secret",
                "SCHWAB_REFRESH_TOKEN": "refresh",
            }
        )
        self.assertTrue(status.ready)
        self.assertEqual(status.reason, "ready_for_read_only_market_data")

    def test_normalize_flat_rows(self):
        payload = {
            "rows": [
                {
                    "expiration": "2026-08-21",
                    "option_type": "put",
                    "strike": 50.0,
                    "bid": 0.40,
                    "ask": 0.50,
                    "observed_at": "2026-07-18T20:00:00+00:00",
                    "contract_symbol": "XYZ260821P00050000",
                }
            ]
        }
        rows = normalize_schwab_option_chain(payload, underlying="XYZ")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].symbol, "XYZ")
        self.assertEqual(rows[0].option_type, "put")
        self.assertEqual(rows[0].expiration, date(2026, 8, 21))
        self.assertTrue(rows[0].is_observed)
        self.assertEqual(rows[0].source, "schwab_trader_api")
        self.assertAlmostEqual(rows[0].half_spread, 0.05)

    def test_normalize_exp_date_map_shape(self):
        payload = {
            "callExpDateMap": {},
            "putExpDateMap": {
                "2026-08-21:30": {
                    "50.0": [
                        {
                            "strikePrice": 50.0,
                            "bid": 0.35,
                            "ask": 0.45,
                            "symbol": "XYZ260821P00050000",
                            "volatility": 0.33,
                        }
                    ]
                }
            },
        }
        rows = normalize_schwab_option_chain(
            payload,
            underlying="xyz",
            observed_at=datetime(2026, 7, 18, 16, 0, tzinfo=timezone.utc),
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].option_type, "put")
        self.assertEqual(rows[0].strike, 50.0)
        self.assertAlmostEqual(rows[0].implied_volatility or 0.0, 0.33)

    def test_snapshot_fail_closed_without_credentials(self):
        result = snapshot_schwab_option_quotes("SPY", env={})
        self.assertFalse(result["ok"])
        self.assertEqual(result["n_quotes"], 0)
        self.assertFalse(result["trading_authority"])

    def test_snapshot_with_injectable_transport(self):
        def transport(symbol: str, base: str):
            self.assertEqual(symbol, "ABC")
            self.assertTrue(base.startswith("https://"))
            return {
                "rows": [
                    {
                        "expiration": "2026-09-18",
                        "option_type": "call",
                        "strike": 100,
                        "bid": 1.0,
                        "ask": 1.2,
                        "observed_at": "2026-07-18T15:00:00+00:00",
                    }
                ]
            }

        result = snapshot_schwab_option_quotes(
            "ABC",
            env={
                "SCHWAB_APP_KEY": "k",
                "SCHWAB_APP_SECRET": "s",
                "SCHWAB_REFRESH_TOKEN": "r",
            },
            transport=transport,
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["n_quotes"], 1)
        self.assertFalse(result["trading_authority"])

    def test_status_report_does_not_embed_secrets(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "schwab-status.json"
            report = write_status_report(
                path,
                env={
                    "SCHWAB_APP_KEY": "super-secret-key",
                    "SCHWAB_APP_SECRET": "super-secret-secret",
                    "SCHWAB_REFRESH_TOKEN": "super-secret-refresh",
                },
            )
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("super-secret", text)
            self.assertTrue(report["status"]["ready"])
            loaded = json.loads(text)
            self.assertEqual(loaded["purpose"], "research_option_quotes_only")


if __name__ == "__main__":
    unittest.main()
